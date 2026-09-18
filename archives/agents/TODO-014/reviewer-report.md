# TODO-014 レビュー担当の報告

対象: `claude_memo.html` の未コミットの差分（`git diff`、58 挿入 91 削除）。
観点は「描画結果と動作が変わらないこと」。

## 結論

**動作が変わる指摘は無い。** 9 項目の範囲外の変更も無い。
重大度を付けた指摘は 3 件で、いずれも「動作が変わらない」側。

- 到達し得る入力の範囲では、シークバー・クラス操作・CSS・null ガードの
  どれも変更前と同じ結果になることを、実測か原文の突き合わせで確かめた
- 1 件だけ、**到達しない入力**（総時間を超える `targetSec`）で結果が
  変わる。クランプがあるので現状では起き得ない（下記 A）

## 指摘

### A. シークバー: 総時間を超える値だけ結果が変わる（検討 / 動作は変わらない）

`claude_memo.html:1871`

```js
const targetIndex = Math.max(0, slideStartTimes.findLastIndex(t => t < targetSec));
```

- **何が違うか**: `targetSec > totalDurationSeconds` のとき、旧ループは
  break せずに `targetIndex = 0` / `slideOffset = 0`（先頭へ戻る）、
  新実装は最後のスライドの末尾になる
- **どの条件で現れるか**: 現れない。直前の
  `const ratio = Math.max(0, Math.min(1, clickX / rect.width))`（L1865）で
  `ratio ≤ 1` にクランプされ、`targetSec = ratio * totalDurationSeconds`
  が総時間を超えないため
- **実測**: 実データの `duration`（12,13,10,14,12,12,12,14,14,12,14,14,11,
  11,12,12,15 / 合計 214 秒）で、旧ループと新実装を 100,056 通り
  （0〜214 を 10 万分割＋各スライドの開始時刻ちょうど・±1e-9・0・214・
  −1・219）に与えて比較した。**差が出たのは 219（= 総時間 +5）の 1 件のみ**
- **判断**: クランプ済みなので直す必要は無い。むしろ新実装の方が
  範囲外での挙動は妥当（先頭へ飛ばない）

境界の一致も上の実測に含まれている。補足すると:

- `slideStartTimes` は L1194-1199 で `slideData` を先頭から同じ順に足して
  作られており、旧ループの `accumulated` と加算の順序・基準が同一
- 旧条件「`accumulated + duration[i] >= targetSec` を満たす最初の i」は
  「`slideStartTimes[i] < targetSec` を満たす最後の i」と同値
- 0 秒 → 旧 `[0, 0]` / 新 `findLastIndex` が −1 → `Math.max(0, -1)` で
  `[0, 0]`。末尾（214 秒）→ 両方 `[16, 15]`。境界ちょうど（例 12 秒）→
  両方「手前のスライドの末尾」。コメント（L1868-1870）の説明と一致する
- 長さ 0 のスライドは `slideData` に無い（全 17 枚が 10〜15）。仮にあっても
  旧新とも、そのスライドは選ばれない（開始時刻が次と同値になるため
  `findLastIndex` は後ろを取るが、旧ループもその手前を取る）

### B. `unlockFallbackAudio`: `play()` が Promise を返さない環境で音量が 0 のまま（検討 / 動作は変わらない）

`claude_memo.html:1178`

- **何が違うか**: 旧コードの `else` 分岐は `pause()` と `volume = 1` を
  行っていた。新コードで `play()` が `undefined` を返すと
  `undefined.then` で `TypeError` になり、`catch(e)`（L1184）の
  `console.warn` に落ちる。このとき `fallbackAudioElement.volume` は
  直前に入れた **0 のまま**になり、以後 Online TTS が無音で再生される
- **どの条件で現れるか**: `HTMLMediaElement.play()` が Promise を返さない
  ブラウザのみ。Chrome 50 / Safari 10 以降は返すので、このページが既に
  必須にしている機能（container query = Chrome 105 / Safari 16、
  `100dvh`、`aspect-ratio`）より要求が低く、実質到達しない
- **判断**: TODO-014 が「対象ブラウザはすべて Promise を返す」と決めた
  とおりの結果で、項目の想定内。直すなら `catch` の中で
  `fallbackAudioElement.volume = 1` を補うだけで済む（1 行）

### C. 残った null ガードとの不揃い（好みの範囲 / 動作は変わらない）

`claude_memo.html:1907`

`setupViewportScale()` の中に `stage && stage.classList.contains(...)` が
残っている。同じ `#viewport-stage` を、L1806・L1820 では無ガードで触る形に
変わったので、読んだときに「どちらが正しいのか」が分かりにくい。

- 元から L1924 の `new MutationObserver(update).observe(stage, ...)` は
  無ガードで、`stage` が無ければそこで例外になる。つまりこのガードは
  今回の差分の前から実質意味を持っていない
- TODO-014 のチェックリストに含まれていない箇所なので、**この項目で直す
  必要は無い**。気になるなら別項目

## 「なぜ大丈夫か」の根拠（重点項目ごと）

### CSS の重複解消（L157-171 の基底 / L253-259 のメディアクエリ）

メディアクエリ側から消えた 7 宣言
（`position: absolute` / `top: 0` / `left: 0` / `max-width: none` /
`max-height: none` / `margin: 0` / `padding: 1.5rem`）は、**すべて基底の
`.video-viewport.pseudo-fullscreen`（L157-171）に同じ値・同じ `!important`
で存在する**（両ブロックを読んで 1 宣言ずつ突き合わせた）。

- 詳細度はどちらも `.video-viewport.pseudo-fullscreen` = (0,2,0) で同じ。
  メディアクエリは詳細度を上げない
- 基底（L157）が先、メディアクエリ（L253）が後なので、両方 `!important` の
  同値争いは後者が勝つ。残した 5 宣言（`right: auto` / `bottom: auto` /
  `width: 960px` / `height: 540px` / `z-index: 1`）は基底と値が異なるため
  必要で、消えていない
- 同じメディアクエリ内の `#player-viewport`（ID = 詳細度 (1,0,0)）は
  `!important` 無しなので、基底の `!important` に負ける。ただし
  `position` / `top` / `left` / `max-width` / `padding` は値が同じで、
  `transform` は競合しない。**計算値は変更前と一致する**
- 基底だけが持つ `border-radius: 0` / `box-shadow` は元からメディアクエリ側に
  無く、今回も触っていない

### `classList.toggle` への置き換え 2 か所

`updateWaveState()`（L1517-1523）は **`className` の全文代入のままで、
`classList.toggle` にしていない**（`waveContainer` の `paused` だけが
toggle）。つまり「代入時に消えていたクラスが残る」という筋の差は起きない。
クラスの集合は、旧 2 本と新 1 本を集合として比較して一致を確認した
（active / 非 active とも `true`）。`audioStatusBadge` は HTML の初期クラス
（`text-xs` / `px-2`、L379）を JS が上書きする作りで、これも変更前と同じ。

プレイリスト項目（`setPlaylistItemState()`、L1589-1593）は全文代入から
toggle に変わっているので、「他所で付いたクラスが残る」経路を確かめた。

- `claude_memo.html` 全体の `classList` 呼び出しを列挙したところ、
  プレイリスト項目のクラスを触るのは `setPlaylistItemState()` だけ。
  `scrollPlaylistIntoView()`（L1624-1637）は `scrollTo` のみでクラスを
  触らない。Tailwind の CDN も実行時にクラスを足さない
- したがって toggle 後に残り得るクラスは
  `PLAYLIST_ITEM_CLASS`（共通）＋ active / idle のどちらか一方だけ。
  旧 4 本の全文文字列と集合比較して 4 本とも一致を確認した
- 番号 `<span>` の色（`text-lime-400` / `text-slate-500`）は、旧実装でも
  `updatePlaylistSelection()` が触っておらず初期描画のまま残る。
  新実装も `innerHTML` 側に残しており、**この既存の挙動を変えていない**
  （直すと動作の変更になるので、この項目では正しい判断）
- `<i></i>` を空で書いてから `setPlaylistItemState()` で入れているが、
  `appendChild` の前の同期処理なので描画は挟まらない

### プレイリスト項目の配列保持

- `initPlaylist()` の呼び出しは `startApp()`（L1928）の **1 か所だけ**で、
  `startApp()` も `DOMContentLoaded` か即時実行の **1 回だけ**（L1933-1937）。
  再実行の経路は無い
- それでも `initPlaylist()` の先頭で `playlistItems.length = 0`（L1597）を
  しており、再実行しても古い DOM を掴み続けない
- `updatePlaylistSelection()` は `renderSlide()`（L1499）から呼ばれるが、
  `startApp()` は `initPlaylist()` → `renderSlide(0, true)` の順なので、
  配列が空のまま回ることは無い。仮に空でも forEach が何もしないだけで、
  旧実装の `if (!item) return` と同じ結果
- `const playlistItems`（L1587）はトップレベルで、使う関数が呼ばれるのは
  すべてスクリプト末尾の `startApp()` 以降。TDZ に当たらない

### null ガードの削除

消した 4 つの対象は、いずれも `claude_memo.html` 内の静的な要素で、
`<script>` は `</body>` の直前にあるため参照時点で必ず存在する。
DOM から取り除く経路も無い（`innerHTML` への代入は
`slide-canvas`(L1487) と `playlist-items`(L1596) の 2 か所だけで、
どれもこれらの要素を含まない）。

| 消したガード | 対象 | 定義 |
|---|---|---|
| `if (toggleVoiceEngineBtn)` | `#toggle-voice-engine-btn` | L312（静的） |
| `if (!tapFeedbackIcon) return` | `#tap-feedback-icon` | L358（静的。`#slide-canvas` の外の兄弟） |
| `if (stage)` 2 か所 | `#viewport-stage` | L330（静的） |
| `if (fsIcon)` | `#fullscreen-btn > i` | L456（静的） |

### 範囲

差分のハンクを 1 つずつ TODO-014 のチェックリストに対応付けた。
CSS 1 項・`play()` 1 項・`formatTime` 1 項・`updateWaveState` 1 項・
プレイリスト 2 項・`playerViewport` 1 項・シークバー 1 項・
null ガード 1 項で、**9 項目に対応しないハンクは無い**。
`slideData` や読み上げまわり（`splitForSpeech()`、`prepareSpeechText()`、
音声の絞り込み、`referrer` の meta）には一切触れていない。
`TODO.md` とスライド枚数の直書き（L420 の `playlist-count`）も変更なし。

### コメント

新しく入ったコメントは 2 か所とも「なぜ」を書いている。

- L1583「共通のクラスと、選択中かどうかで変わるクラスを分ける」
- L1868-1870 シークバーの境界の扱い（旧実装と同じになる理由）

### テスト

このプロジェクトにはビルドもテストも無く（`CLAUDE.md`「構成」）、
確認はブラウザで開いて行う方針なので、テストの追加不足は指摘しない。
なお、シークバーの境界比較に使った検証スクリプトは
`/tmp/seekcmp.js`（一時ファイル）に置いた。再現したい場合は
`duration` の配列を書き写して `node` で走らせるだけで足りる。
