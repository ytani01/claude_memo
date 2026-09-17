# TODO-002 レビュー依頼（reviewer）

## 目的

implementer の変更（`git diff`、`claude_memo.html` のみ）を、
設計と規約に照らしてレビューする。**コードは直さない。** 報告するだけ。

## 読むもの

- `archives/agents/TODO-002/main-investigation.md`（原因の調査）
- `archives/agents/TODO-002/implementer-request.md`
- `archives/agents/TODO-002/implementer-report.md`
- `git diff`

## 見てほしいところ

- **分岐と条件式の意味が変わったところ**。特に:
  - `if (!isAndroid) chromeResumeTimer = setInterval(...)` にしたことで、
    Android では `chromeResumeTimer` が null のまま残る。
    これを前提にしている他の箇所が壊れていないか
  - `stopSpeech()` で `fallbackAudioElement = null` をやめたことの影響
  - `speakOnlineTTS()` の中で要素が無いときに `new Audio()` する分岐が、
    unlock 済みの要素を取り違える形になっていないか
- `onended` / `onerror` を使い回す作りで、前のスライドのハンドラが
  効いてしまう競合が起きないか（連打、シーク、スライド送り）
- User-Agent 判定（`/Android/`）の是非。Android 上の Firefox や
  Chrome 以外も巻き込むが、それで困るか
- 無音 WAV の data URI を新しく埋め込んだことの是非。
  もっと簡単な unlock の手が無いか
- 過剰な作り込みが無いか（この項目は「最小の差分で直す」方針）

## 報告

`archives/agents/TODO-002/reviewer-report.md` に、指摘を重要な順に書く。
直す/直さないの判断は管理者がするので、**判断まで踏み込まなくてよい**。
返事は 5 行以内。目安 15 分。
