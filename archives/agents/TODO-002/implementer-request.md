# TODO-002 実装依頼（implementer）

## 目的

Android Chrome で音声が壊れている 2 件を直す。原因は調査済み
（`archives/agents/TODO-002/main-investigation.md`）。原因の再調査はしない。

## 対象

`claude_memo.html` のみ。

## やること

### 1. Online TTS が鳴らない（自動再生のブロック）

- `fallbackAudioElement` を**毎回 `new Audio()` しない**。再生ボタンの
  クリックハンドラ（`setupEventListeners()` 内、1552 行付近）で、
  ユーザー操作の文脈のうちに `Audio` 要素を 1 つだけ作って
  無音で `play()` → `pause()` して unlock する（2 回目以降は作り直さない）。
- `speakOnlineTTS()`（1341 行付近）は、その 1 つの要素の `src` を
  差し替えて `load()` → `play()` する。
- `stopSpeech()`（1190 行付近）は `pause()` するだけにして、
  **`fallbackAudioElement = null` にしない**（unlock が無駄になる）。
- `onended` / `onerror` を毎回上書きする作りのままで構わないが、
  使い回しで前のハンドラが残らないようにすること。

### 2. Web Speech が途中で途切れる（`chromeResumeTimer`）

- 1325〜1333 行の 5 秒ごとの `pause()`/`resume()` は、デスクトップ Chrome
  向けの回避策。**Android では起動しない**ようにする。
- 判定は `navigator.userAgent` に `Android` が含まれるかで十分。

## やらないこと

- 180 文字の切り詰め、safety timeout、`duration` の扱いは触らない
  （調査で潰した候補）。
- リファクタリング、整形、他の機能の変更はしない。差分は最小限に。

## 完了条件

- PC の Chrome で今までどおり読み上げが動く（Web Speech / Online TTS 両方）。
- 上の 2 点が直っている。実機での確認は利用者が行うので、こちらでは不要。
- ブラウザの JS 構文エラーが無いこと（`node --check` は HTML なので使えない。
  `<script>` の中身を切り出して確認するなど、方法は任せる）。

## 報告

`archives/agents/TODO-002/implementer-report.md` に、変更点・確認したこと・
残る懸念を書く。返事は 5 行以内（終わったか / 報告のパス / 判断が要る点）。

目安 15 分。
