# TODO-002 レビュー報告（reviewer）

対象: `git diff`（`claude_memo.html` のみ、+42/-6）。
読んだもの: `main-investigation.md`、`implementer-request.md`、
`implementer-report.md`、`claude_memo.html:1110-1440, 1490-1700`、
プロジェクトの `CLAUDE.md`。

**要修正は 0 件。** 依頼書の 2 点は原因のとおりに直っており、範囲外の変更も無い。
以下は検討 4 件・好みの範囲 2 件。

---

## 先に、実測で確かめたこと（問題なし）

- **無音 WAV は正しい WAV。** base64 を decode して検証:
  60 バイト、RIFF サイズ 52（＝実サイズと一致）、PCM 16bit / 8kHz / mono、
  data 16 バイト＝8 サンプル（約 1ms）。壊れた data URI なら unlock が
  黙って失敗するところだった。
- **implementer が「懸念」に挙げた unlock の競合は起きない（実測）。**
  chromium（headless、`--autoplay-policy=no-user-gesture-required`）で
  「`play()` → 同じタスクで `pause()`/`src=`/`load()` → 本番 `play()`」を
  再現したところ、unlock 側の promise は **AbortError で reject** し、
  `.then()` の `pause()` は走らない。本番の再生は `paused=false` のまま、
  `volume` は `.catch()` 側で 1 に戻る。結果:
  `unlock play REJECTED:AbortError | real play resolved, paused=false || final volume=1`。
  自動再生がブロックされる既定の設定でも `NotAllowedError` → `volume=1` で、
  どちらの経路でも音量 0 のまま取り残されることは無かった。
- **無音 WAV による unlock は無駄ではない。** 「再生ボタンの click の中で
  そのまま本番 `play()` するから要らないのでは」と一度は思ったが、
  `claude_memo.html:1332-1340` に **Web Speech の `onerror` から
  `speakOnlineTTS()` へ落ちる経路**があり、ここはユーザー操作の文脈の外。
  この経路のために、要素を先に unlock しておく意味がある。
  「もっと簡単な手」は、この経路を捨てない限り無い。
- **範囲。** 差分は依頼した 5 か所だけ。整形・リファクタリングの混入は無い。

---

## 検討 1: `stopSpeech()` が `onended` / `onerror` を付けたまま残す

`claude_memo.html:1233-1236`

要素を `null` にしなくなったことで、**一時停止・消音・スライド送りの後も
前のナレーションのハンドラが要素に付いたまま**になる（変更前は要素ごと
捨てていたので必ず消えた）。`finished` は false のままなので、この後に
古い `error` イベントが 1 発来ると、古い `handleEnd` が
`slideTransitionTimeout` を張り直す。

- 実害が出る窓は狭い。`ended` は pause 中に飛ばないし、online 経路では
  `stopSpeech()` の直後に同じタスクで `speakOnlineTTS()` が
  `onended`/`onerror` を `null` にするので、間に何も挟まらない。
  危ないのは「一時停止したまま、読み込み中だった src が error に落ちる」形だけ。
- 根拠は上記の行のコードと `speakCurrentNarration()`
  （`claude_memo.html:1262-1285`、online 分岐は同期呼び出し）。
  **実測はしていない（未確認）。**
- `stopSpeech()` でも `onended = null; onerror = null;` を足せば閉じる。

## 検討 2: 要素を共有したことで、古い `play()` の `catch` が新スライドのタイマーを上書きする

`claude_memo.html:1407-1411`

`play()` の promise が pending のうちに `pause()` されると
**AbortError で reject する**（chromium で実測。`OLD play catch fired: AbortError`）。
その `.catch()` は

```js
const muteWaitMs = (slideData[currentIndex].duration / getEffectiveSpeed()) * 1000;
slideTransitionTimeout = setTimeout(handleEnd, muteWaitMs);
```

を実行するが、`currentIndex` は**もう次のスライドに進んでいる**一方、
`handleEnd` は**前のスライドのクロージャ**（`finished === false`）。
連打・シーク・スライド送りで再生開始前に切り替えると、
グローバルの `slideTransitionTimeout` が古いハンドラのタイマーで上書きされる。

- **これは変更前からある**（変更前も `stopSpeech()` の `pause()` が同じ
  reject を起こしていた）。今回の差分が悪くしたわけではない。
- 実際には `onSlideAudioFinished()` が先頭で `slideTransitionTimeout` を
  clear するので、多くの場合は自然に消える。残るのは
  「古いタイマーの方が先に発火して、再生中のスライドを飛ばす」形。
- 直すなら `.catch()` の中で `if (finished) return;` ではなく、
  AbortError を除外するのが素直。今回の項目でやるかは管理者の判断。

## 検討 3: 一度ブロックされると `unlockFallbackAudio()` が二度と効かない

`claude_memo.html:1126-1127` と `claude_memo.html:1379-1382`

`unlockFallbackAudio()` の門は `if (fallbackAudioElement) return;`、つまり
**「要素があるか」を「unlock 済みか」の代わりに使っている**。
`speakOnlineTTS()` 側の `new Audio()` でも要素は埋まるので、

1. 既定の Web Speech で再生開始（unlock は呼ばれるが、この時点では問題なし）
2. ※ もしくは Space キーで再生開始（`claude_memo.html:1719-1724`。
   こちらは `unlockFallbackAudio()` を呼んでいない）
3. Web Speech の `onerror` → 文脈外で `speakOnlineTTS()` → `new Audio()` が
   ブロックされる
4. **以後、再生ボタンを何度押しても unlock は走らない**（要素があるので即 return）

という流れが作れる。`audioUnlocked` のようなフラグで門を分ければ閉じる。

- 根拠は上記 2 か所のコードと、`playBtn` 以外の再生経路
  （Space: `claude_memo.html:1719-1724`、engine 切替:
  `claude_memo.html:1632-1634`）。**実機での再現はしていない（未確認）。**
- 頻度は低い（3 の分岐に入らない限り起きない）。

## 検討 4: `CLAUDE.md` に、対で残すべき注意が書かれていない

プロジェクトの `CLAUDE.md`「触るときの注意」は、TODO-001 で足した
container query / `--vp-scale` の注意を残している。今回の変更で、
同じ性質の「知らずに触ると戻ってしまう」前提が 2 つ増えた。

- `fallbackAudioElement` は**再生ボタンで unlock した 1 個を使い回す。
  `null` にしてはいけない**（`stopSpeech()` の中のコメントだけが根拠になっている）
- **Android では `pause()`/`resume()` の回避策を動かさない**（動かすと止まる）

`CLAUDE.md` の「読み上げ」の節に 2 行足し、詳細は `（TODO-002）` で参照する形が
既存の書き方に揃う。差分に `CLAUDE.md` が含まれていないのが唯一の
「片方だけ変わっている」箇所。

---

## 好みの範囲

1. **コメントが英語。** 追加した 5 か所のコメントはすべて英語。この
   ファイルは元の実装が英語コメントなので不整合とまでは言えないが、
   TODO-001 で足した注意書き（`claude_memo.html:1700-1703` など）は日本語。
   新しく足す説明は日本語に寄せた方が揃う。
2. **`claude_memo.html:1357` のブレース無し `if`。**
   `if (!isAndroid) chromeResumeTimer = setInterval(() => {` は、
   波括弧無しの `if` に 8 行の本体がぶら下がる形で読みにくい。
   周りのコードは 1 行で収まるときだけブレースを省いている。

---

## 判断が要る点（管理者へ）

- 検討 1・2・3 は、いずれも「今回の症状とは別の、狭い条件でのずれ」。
  TODO-002 の方針（最小の差分）を優先してこのまま出すか、
  検討 1（2 行）だけ足すか。
- 検討 4（`CLAUDE.md` への追記）は、この項目で一緒にやるのが自然に見える。
