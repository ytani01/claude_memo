# TODO-002 実装報告（implementer）

依頼書どおり `claude_memo.html` のみを変更した。差分は 42 行追加 6 行削除。

## 変更したファイルと箇所

### 1. `claude_memo.html:1118-1145` — フラグと unlock 用の関数を追加

- `isAndroid`（`/Android/.test(navigator.userAgent)`）
- `SILENT_WAV`: 8 サンプル分の無音 WAV の data URI（unlock 専用）
- `unlockFallbackAudio()`: `fallbackAudioElement` がまだ無いときだけ
  `new Audio(SILENT_WAV)` を作り、`volume = 0` で `play()` → 解決したら
  `pause()` して `volume` を 1 に戻す。2 回目以降は即 return する

### 2. `claude_memo.html:1598` — 再生ボタンのハンドラで unlock を呼ぶ

`togglePlay()` の直前に `unlockFallbackAudio();` を 1 行足した。
Web Speech の unlock（既存のダミー utterance）はそのまま。

### 3. `claude_memo.html:1379-1388` — `speakOnlineTTS()` が要素を使い回す

`new Audio(ttsUrl)` をやめ、既存の要素の `src` を差し替えて `load()` する。
使い回しで前のハンドラが残らないよう、`src` を入れる前に
`onended` / `onerror` を `null` にしてから（後段で改めて代入される）。
要素がまだ無い場合（再生ボタンを押さずに読み上げに来た経路）は、
従来どおり `new Audio()` を作る。

### 4. `claude_memo.html:1233-1236` — `stopSpeech()` は pause だけ

`fallbackAudioElement = null;` を消した。unlock を捨てないため。

### 5. `claude_memo.html:1355-1357` — `chromeResumeTimer` を Android では起動しない

`chromeResumeTimer = setInterval(...)` を `if (!isAndroid)` で囲んだ
（`clearInterval` は従来どおり無条件）。

## 検証

- `<script>`（src 無し、2 ブロック）を抜き出して連結し `node --check`
  → 成功（終了コード 0）。
- ビルド・テストはこのプロジェクトに無い（`CLAUDE.md`）。実機での確認は
  依頼書のとおり利用者が行う。

## 残る懸念

- unlock の無音再生が解決する前に `src` を差し替えると、その `play()`
  の Promise は AbortError で reject する。`.catch()` で握りつぶしている
  ので実害は無いはずだが、`.then()` 側の `pause()` が本番の再生を止める
  ことは無い（reject した側に流れるため）と判断した。
- `isAndroid` の判定は User-Agent 文字列のみ。Android 上の Firefox など、
  pause/resume が要る環境でも回避策が無効になるが、依頼書の方針どおり。
- 範囲外だが気づいたこと: `speakOnlineTTS()` の `onerror` と
  `play().catch()` はどちらも `slideTransitionTimeout` を張る。両方
  走ると後勝ちで上書きされるだけなので害は無いが、経路が重なっている。
