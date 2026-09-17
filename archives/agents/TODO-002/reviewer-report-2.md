# TODO-002 レビュー報告 その 2（reviewer）

対象: `git diff`（`claude_memo.html`、`CLAUDE.md`）。コードは直していない。

## 要修正

### 1. `claude_memo.html:1220`（`splitForSpeech` の 40 文字強制切り）が英単語を割る

実測（`narration` 17 本に `splitForSpeech` を適用）:

```
slide 8: 「…検索する codegr」／「aph などが活躍し…」
```

`codegraph` が `codegr` と `aph` に割れ、読み上げが別々の無意味な語になる。
強制切り（末尾が `。、！？` でない 40 文字ちょうどのチャンク）は全体で
13 か所あり、うち ASCII 語をまたぐのはこの 1 か所。
根拠: `node` で実際に分割した結果。

方向としては、40 に達したときに直前の「切ってよい位置」（空白・
`・` `）` `」`、ASCII と非 ASCII の境目など）まで戻る手がある。判断は管理者に。

### 2. `claude_memo.html:1348-1354` — `utterance.onend` に `runId` の判定が無い

```js
utterance.onend = () => {
    if (i + 1 < chunks.length) {
        speakChunk(i + 1);   // ← speakChunk 側で runId を見ている
    } else {
        handleEnd();          // ← ここは finished しか見ていない
    }
};
```

`speechRunId` で塞いだ経路のうち、**最後のチャンクの `onend` だけが漏れている**。
`stopSpeech()` は `speechRunId++` のあと `speechSynthesis.cancel()` を呼ぶが、
Chrome が中断されたものに `end` を配ると、古い run のクロージャの
`finished` はまだ `false` なので `handleEnd()` → `onSlideAudioFinished()` が
通る。起きること:

- `onSlideAudioFinished()` が `slideTransitionTimeout` を `clearTimeout` する
  ので、**いま走っている run の safety timeout が消える**
- 1 秒後に `renderSlide(currentIndex + 1)` が走り、**スライドが 1 枚余分に進む**

発火条件は「最後のチャンクの再生中に `stopSpeech()` が入る」こと。
`isPlaying` が false になるポーズは `onSlideAudioFinished()` の先頭で
弾かれるので無事だが、**消音ボタン・速度変更・矢印キー/プレイリストでの
スライド移動**は `isPlaying` が true のまま通る（1684-1691 行、1595-1600 行、
1734-1745 行を読んで確認）。

**未確認**: Chrome が `cancel()` 時に `end` を出すか `error`（`canceled`）を
出すかは、この環境（ヘッドレス Chromium に日本語音声が無い）では確かめられ
なかった。`error` しか出さないなら 1359 行の判定で塞がっていて実害は無い。
実機の DevTools コンソールで、`speak()` 中に `cancel()` して `end` が出るかを
見れば決着する。なお変更前のコードも同じ穴を持っていた（1 発話まるごとが
対象だったので、当たる時間幅は今より広かった）。

## 検討

### 3. safety timeout をチャンク間の間（ま）が食う

`claude_memo.html:1370` の式は全文の文字数のままで、余裕は固定の 3000ms。
分割で発話が最大 6 個に分かれるので、**間 1 つあたりの余裕は 600ms**
（4 チャンクなら 1000ms）。実測した内訳:

| チャンク数 | 該当スライド | safety | 間 1 つあたりの余裕 |
|---|---|---|---|
| 6 | 11, 12 | 約 26.2〜26.7 秒 | 600ms |
| 5 | 2,4,5,6,7,8,9,17 | 約 23.9〜27.1 秒 | 750ms |
| 4 | 1,3,10,13,14,15,16 | 約 20.8〜23.6 秒 | 1000ms |

式の想定速度（`len / 4.5 / 1.4` = 6.3 文字/秒）より実際の読み上げは速いと
思われるので、たいていは余る見込み。ただし**未確認**（実機で測っていない）。
併せて、safety timeout が先に鳴っても**残りのチャンクは止まらない**
（`handleEnd()` は `cancel()` を呼ばない）ので、次のスライドが出るまでの
約 1 秒は前のスライドの音が続く。

### 4. 強制切りでチャンクが `、` で始まる箇所が 2 つ

slide 2 の `「、そしてアカウント切替用…」`、slide 11 の
`「、コストと精度の最適化を…」`。読み上げ自体は続くが、句の途中で間が入る。
1 と同じ直し方（切ってよい位置まで戻る）で一緒に消える。

### 5. `CLAUDE.md:71` の書き方が実装とずれている

「`splitForSpeech()` で 40 文字ずつに分けて」とあるが、実際は
**20 文字以上たまったところで `。、！？` の後ろ、40 文字で強制**。
実測のチャンク長は 13〜40 文字。「最大 40 文字で」の方が実体に合う。
他の 2 件（`meta referrer`、`Audio` 要素の使い回し）の記述は実装と一致。

## 問題なしと判断したところ（依頼で挙がっていたもの）

- **`onerror` → Online TTS の競合**: Web Speech 側と Online TTS 側の
  `finished` / `handleEnd` は別のクロージャで、Web Speech 側は
  `finished = true` にラッチしてから落ちるので二重には進まない。
  合流先の `onSlideAudioFinished()` も 1 秒タイマーを貼り直すだけ。
  落ち残る Web Speech の safety timeout は `!finished` で no-op になる
  （`clearTimeout` されないが害は無い）
- **`onerror` の 1 回だけ判定**: `finished || runId !== speechRunId` で、
  古い run のキャンセルエラーからの誤フォールバックも塞がっている
  （変更前は塞がっていなかった。改善）
- **50ms の `setTimeout`**: 1305 行で `runId !== speechRunId` を見ている
- **`<meta name="referrer" content="no-referrer">` の副作用**:
  このページの外部参照は CDN 3 つと Google TTS だけで、`<a href>` は 0 件
  （`grep`）。CDN 3 つは Referer 無しで到達を確認（`curl`: Tailwind 302、
  Google Fonts 200、FontAwesome 200）。`<head>` の 7 行目にあり、10 行目の
  最初の CDN 読み込みより前なので効く。現状で副作用は見当たらない
- **範囲**: 差分は依頼の範囲内。`chromeResumeTimer` / `isAndroid` の残骸は
  `grep` で 0 件。整形やリファクタリングの混入も無い
- **テスト**: このプロジェクトにテストの枠は無い（`CLAUDE.md`「構成」）。
  実装担当が 17 本の `narration` で分割を確かめており、これで足りる

## 好みの範囲

- `claude_memo.html:1224` の `if (buf.trim())` は、末尾が空白だけのときに
  それを捨てる。実装報告の「無損失」は厳密には成り立たない
  （実データでは発生しないことを確認済み）
- `speechActive`（1110, 1252, 1257, 1344, 1358 行）はどこからも読まれない
  死んだ変数。変更前からそうなので今回の差分の責任ではない。
  1358 行の代入が `runId` の判定より前にあるのも、読まれない以上は実害なし
