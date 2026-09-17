# TODO-002 確認報告（verifier）

対象: `claude_memo.html` の `git diff`（implementer 実装分）。コードは直していない。

## 1. 依頼書の「やること」が入っているか

- 1（Online TTS unlock）: 入っている。`unlockFallbackAudio()`（1118〜1145 行付近）を
  再生ボタンのクリックハンドラ内（1598 行）で呼び、無音 WAV で
  `play()` → `pause()` している。2 回目以降は `fallbackAudioElement` が
  既にあるので即 return（1127 行）。`speakOnlineTTS()`（1372〜1412 行）は
  `new Audio()` をやめ、既存要素の `src` を差し替えて `load()` している。
- 2（Android で `chromeResumeTimer` を止める）: 入っている。`isAndroid`
  （`/Android/.test(navigator.userAgent)`、1118 行）で判定し、
  `if (!isAndroid) chromeResumeTimer = setInterval(...)`（1354 行）で
  Android 時は起動しない。`clearInterval` 側は従来どおり無条件。

両方とも実際に動かして確認済み（後述）。

## 2. 「やらないこと」に手が入っていないか

- 180 文字の切り詰め: `cleanText = text.substring(0, 180)`（1376 行）は
  変更なし。
- safety timeout: diff に該当箇所の変更なし（`safetyTime` 周りは触られていない）。
- `duration` の扱い: `slide.duration` を使う箇所（`muteWaitMs` 計算など）は
  変更なし。
- 無関係なリファクタリング: 見当たらない。差分は依頼の 5 箇所に対応する
  最小限の追加・削除のみ。

## 3. `<script>` の構文エラー

自分で確かめ直した。`<script src=...>` を除く 2 ブロックを抜き出して連結し
`node --check` → 終了コード 0（構文エラー無し）。実装の報告を鵜呑みにせず
独自に実行した結果も同じ。

## 4. `fallbackAudioElement` を触る全箇所をたどった結果

`grep -n "fallbackAudioElement" claude_memo.html` で洗い出し、以下を確認。

- 宣言（1116 行）: `null` で初期化。以後、コード中で `null` に戻す箇所は
  他に無い（`git grep` で確認）。依頼どおり `stopSpeech()` は
  `fallbackAudioElement = null` を削除済み（1233〜1236 行、`pause()` のみ）。
- `unlockFallbackAudio()`（1127〜1141 行）: 既にあれば即 return。無ければ
  `new Audio(SILENT_WAV)` を作って unlock。
- `speakOnlineTTS()`（1379〜1388 行）: 要素が無ければ `new Audio()`
  （再生ボタンを経ずに読み上げに来た経路のフォールバック）。ある場合は
  `pause()` → `onended`/`onerror` を `null` にしてから `src` 差し替え →
  `load()`。その直後（1397・1401 行）で `onended`/`onerror` を
  改めて代入しており、前のハンドラが残ることは無い。
- ミュート切替（`muteBtn`、1671〜1681 行）、音声エンジン切替
  （`toggleVoiceEngineBtn`、1621〜1636 行）、スライド移動
  （`prevBtn`/`nextBtn`/`restartBtn`、いずれも内部で `stopSpeech()` →
  `speakCurrentNarration()` を経由）はすべて `stopSpeech()` の
  `pause()` のみを通るので `fallbackAudioElement` を作り直さない。
  最後まで再生したとき（`onSlideAudioFinished()` → `pausePresentation()`）
  も `fallbackAudioElement` を触る箇所は無い。

## 5. PC Chrome での動作確認（実機は不要、Playwright で実際に動かした）

`npx playwright`（chromium、既にインストール済み）でヘッドレス実行し、
`file://.../claude_memo.html` を開いて実際にクリックして確認した
（静的な読みだけで済ませていない）。

- 再生ボタンをクリック → `fallbackAudioElement` が生成され、
  `chromeResumeTimer` が起動（デスクトップ UA）。ページエラー・
  console エラー無し。
- ヘッドレス環境には日本語音声が無く `speechSynthesis` がエラーになるため、
  既存のフォールバック経路で自動的に `speakOnlineTTS()` に落ちることを
  確認（これは今回の変更の対象外の既存挙動）。この際 `fallbackAudioElement`
  の `src` が正しく Google Translate TTS の URL に差し替わった。
- 音声エンジン切替ボタン（Web Speech ⇔ Online）をクリック →
  `src` が Online TTS の URL に差し替わることを確認。
- 一時停止（再生ボタン再クリック）→ `fallbackAudioElement` は
  破棄されず `paused: true` のまま残ることを確認（`stopSpeech()` が
  `null` にしていないことの実地確認）。
- 次のスライドへ移動、ミュート→ミュート解除、それぞれの前後で
  `fallbackAudioElement` のオブジェクト参照（`===`）が同一であることを
  確認（作り直されていない）。
- Android UA（`chromium.newContext({ userAgent: ... })`）で開いて
  再生ボタンをクリック → `isAndroid: true`、`chromeResumeTimer: false`
  （起動していない）を確認。ページエラー無し。

いずれの操作でも console エラー・pageerror は 0 件だった。

## 確かめられなかったこと

- 実機 Android Chrome でのユーザー操作起点の自動再生解除（unlock）が
  実際に効くかどうかは、Playwright のヘッドレス環境では検証できない
  （依頼書のとおり実機確認は利用者が行う）。
- `speakOnlineTTS()` の `onerror`/`play().catch()` の両方が
  `slideTransitionTimeout` を張る点（実装報告に書かれている「範囲外の
  気づき」）は、今回の変更前から存在する経路の重なりであり、今回の
  変更で悪化していないことは diff 上確認したが、動作面まで深追いは
  していない。

## 追加確認（レビューの検討 1・4 を受けた修正）

対象 diff:

- `claude_memo.html` の `stopSpeech()` に `fallbackAudioElement.onended = null;`
  `fallbackAudioElement.onerror = null;` を追加（1231〜1238 行付近）。
- `CLAUDE.md` の「触るときの注意」に 2 行追加。

### `<script>` の構文チェックのやり直し

`<script src=...>` を除く 2 ブロックを再度抜き出して `node --check` を
実行し直した → 終了コード 0（構文エラー無し）。

### 1. `stopSpeech()` でのハンドラ nulling

- `speakOnlineTTS()`（1379〜1412 行付近）は `src` 差し替えの直前で
  `onended`/`onerror` を一旦 `null` にしたあと、`play()` を呼ぶ前に
  `onended`/`onerror` を必ず改めて代入している（1397・1401 行付近）。
  そのため `stopSpeech()` 側で先に `null` にしても、次に鳴らすときは
  必ず新しいハンドラが張られる。**必要なハンドラを消してしまう問題は無い。**
- Playwright（chromium、file:// で実行）で実際に確認した。
  - 再生を開始し Online TTS にフォールバックした直後、
    `fallbackAudioElement.onended` / `onerror` が関数であることを確認。
  - 次のスライドへ移動（`stopSpeech()` → `speakCurrentNarration()` を
    経由）した直後は一旦 `null` になり、新しい発話が始まると
    再び関数として張り直されることを確認（`page.evaluate` で
    `typeof` を見た。`JSON.stringify` は関数を落とすため、null のときは
    キーごと消える形で観測された）。
  - ミュートにして `stopSpeech()` だけが走り、その後新しい発話が
    始まらない状態では、`onended`/`onerror` は `null` のまま残ることを
    確認（＝前のナレーションのハンドラが残ることは無い）。
  - この一連の操作で console エラー・pageerror は 0 件。
- 結論: 前のハンドラが残る問題も、必要なハンドラを消してしまう問題も
  無いことを実地で確認した。

### 2. `CLAUDE.md` の追記内容とコードの整合

- 「`fallbackAudioElement` は 1 個を使い回す。再生ボタンのクリックの中で
  unlock している…」: `unlockFallbackAudio()` が再生ボタンの
  クリックハンドラ内（1598 行付近）で呼ばれ、`fallbackAudioElement` が
  既にあれば即 return する作りと一致。`stopSpeech()` はもう
  `fallbackAudioElement = null` をしない（既存の確認どおり）。
- 「Android では `chromeResumeTimer` の `pause()`/`resume()` を動かさない…
  読み上げが 5 秒ほどで止まる」: `chromeResumeTimer` の間隔は
  `setInterval(..., 5000)`（1366 行）で 5 秒ごと。Android では
  `resume()` が効かない前提のもとでは、このタイマーが最初に
  `pause()` を呼ぶ 5 秒後の時点で読み上げが止まったままになる、
  という記述はコードの間隔（5000ms）と整合している。
- 2 点とも、コードの実際の値・挙動との食い違いは見つからなかった。

## 追加確認の結論

2 点とも問題は見つからなかった。判断が要る点は無い。
