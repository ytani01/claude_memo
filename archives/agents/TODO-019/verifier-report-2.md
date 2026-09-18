# TODO-019 追加確認（reviewer 指摘 2 件への修正）報告

対象の diff（`speakOnlineTTS()` 冒頭に `const runId = speechRunId;`、
`setEndTimeout()` の先頭に `if (finished || runId !== speechRunId) return;`
を追加）を、ヘッドレス Chromium（Playwright 1.63.0）で実測して確認した。

スクリプトは
`/tmp/claude-649/.../scratchpad/verify_late_metadata.js`（項目 1）
`/tmp/claude-649/.../scratchpad/verify_stale_playreject.js`（項目 2）
（セッション専用の一時ディレクトリ。主要部分は下に抜粋）

## 1. `handleEnd()` 後に `onloadedmetadata` が遅れて発火しても、次スライドへの 2 秒待ちタイマーが消されないこと

→ OK（実測）。ffmpeg で作った 2 秒の実音声を `translate.google.com` の
応答として使い、`onended`（=`handleEnd()`、`finished=true` になる）が
発火した直後（100ms 後、2 秒の待ちタイマーが有効な間）に、
`fallbackAudioElement` へ合成の `loadedmetadata` イベントを発火させて
「遅れて来た `onloadedmetadata`」を再現した。

```
[LATE loadedmetadata after handleEnd] events:
  {"what":"onSlideAudioFinished","t":"1583","index":0}
  {"what":"dispatch-late-loadedmetadata","t":"1683"}
  {"what":"onSlideAudioFinished","t":"5135","index":1}
  {"what":"onSlideAudioFinished","t":"8724","index":2}
finalIndex: 3
```

`t=1683ms` で合成の `loadedmetadata` を発火させた後も、
2 秒待ちタイマーはそのまま生き残り、スライド 1（`index:0`）から
スライド 2（`index:1`）へ `t=5135ms`（1583+2000+約1.5秒の音声再生）で
正常に進んだ。以降スライド 3 へも進んでおり、`finished` 判定で
`setEndTimeout()` が早期リターンしてタイマーを上書き・消去しなかった
ことを確認した。

## 2. `stopSpeech()` を挟んだ後に古い `play().catch()` が解決しても、新しいスライドのタイマーを上書きしないこと

→ OK（実測）。`HTMLMediaElement.prototype.play` を差し替え、
スライド 1 の 1 回目の `play()` 呼び出しだけ 4 秒後に reject する
Promise を返すようにした（「古い呼び出しがしばらく経ってから解決する」
状況の再現）。再生開始 800ms 後に `renderSlide(1, true)` を直接呼んで
スライド 2 へ移り（内部で `stopSpeech()` → 新しい `speakCurrentNarration()`
が走り、`speechRunId` がインクリメントされる）、スライド 2 は 2 秒の
実音声で正常再生させた。

```
[STALE play().catch() after stopSpeech] events:
  {"what":"renderSlide(1) called","t":"803"}
  {"what":"onSlideAudioFinished","t":"2371","index":1}
  {"what":"onSlideAudioFinished","t":"5962","index":2}
  {"what":"onSlideAudioFinished","t":"9576","index":3}
finalIndex at end: 3
stale play().catch() actually fired at (ms since click): 5247
```

古い（スライド 1 の）`play().catch()` は `t=5247ms` で実際に発火した。
これはスライド 2（`index:1`→`index:2` の遷移待ち、`t=2371〜5962ms` の間）
が進行中のタイミングにちょうど重なる。しかし `index:2` への遷移は
`t=5962ms` と、スライド 2 自身のタイマー通り（誤差 10ms 程度）に起きており、
古い `play().catch()` の発火によって乱れた形跡（早期終了・タイマーの
上書きによる二重発火など）は見られなかった。`runId !== speechRunId` の
ガードが効いていることを確認した。

## 3. 前回確認した 5 つの完了条件が今も通ること

同じ検証スクリプト（`verify_hang.js` / `verify_normal2.js` /
`verify_pause.js` / `verify.js blocked` / `verify_playreject.js`）を
現在のコードに対して再実行し、いずれも前回と同じ結果だった。

```
== hang (cond1,2: onended なしで 実長/想定秒数+3秒) ==
[HANG, no onerror/onended] slide1 duration=18s -> onSlideAudioFinished after 21.00 s (expect ~21s: 18+3)

== normal, paused after 1st (cond3: onended 正常時に二重に進まない) ==
[REAL 2s AUDIO, paused right after 1st onended] total calls in 23s: 1 (expect exactly 1)

== pause after stopSpeech (cond4: 一時停止後にタイマーが残らない) ==
[PAUSE after stopSpeech, network hung] stray onSlideAudioFinished within 24s after pause: false (expect false)

== onerror (cond5a: 待ち時間が従来と同じ) ==
[BLOCKED] slide1 duration=18s -> onSlideAudioFinished after 17.99 s (expect ~21s: 18+3 なら不一致 → 従来どおり +3秒無しなので一致)

== play() reject (cond5b) ==
[play() forced reject] slide1 duration=18s -> onSlideAudioFinished after 18.05 s (expect ~18s, no +3s, same as before)
```

## 変更ファイルと範囲

`git diff -- claude_memo.html` は `stopSpeech()`（`onloadedmetadata = null`
の追加）と `speakOnlineTTS()`（`runId` の取得、`setEndTimeout()` 冒頭の
ガード追加）のみ。依頼の対象と一致。ほかのファイルへの変更なし。

## 確かめられなかったこと・判断が要る点

- 「遅れて来た `onloadedmetadata`」は、実際のブラウザ・ネットワークで
  自然に再現する条件が組みにくかったため（通常は `onloadedmetadata` は
  `onended` より先に来る）、`dispatchEvent(new Event('loadedmetadata'))`
  で人為的に発火させて再現した。実際の環境で `onloadedmetadata` が
  `onended` より遅れて発火する具体的な状況（遅いストリーミングでの
  メタデータ確定の遅延など）は未確認。今回のテストは「その順序が
  起きた場合にコードが正しく無視すること」の確認であり、その順序が
  実際にどのくらいの頻度・状況で起きるかは判断していない。
- 「古い `play().catch()`」も同様に、`HTMLMediaElement.prototype.play`
  を差し替えて意図的に 4 秒後の reject を発生させる形で再現した
  （実ブラウザで `play()` の解決が自然に 4 秒遅れる状況は作れなかった
  ため）。
- コードの品質面のレビュー（分岐の意味が正しいかなど）は今回もしていない
  （verifier の担当外）。
