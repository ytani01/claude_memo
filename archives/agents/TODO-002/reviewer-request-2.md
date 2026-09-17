# TODO-002 レビュー依頼 その 2（reviewer）

## 目的

2 回目の修正（`git diff`）をレビューする。**コードは直さない。**

## 背景

1 回目の修正は原因を外していた（実機で直らなかった）。
真の原因は 2 つで、`archives/agents/TODO-002/implementer-request-2.md` に
実測付きで書いてある。

## 読むもの

- `archives/agents/TODO-002/implementer-request-2.md`
- `archives/agents/TODO-002/implementer-report-2.md`
- `git diff`（`claude_memo.html`、`CLAUDE.md`）

## 見てほしいところ

- `splitForSpeech()` の切り方。`maxLen = 40` / `minLen = 20` の妥当性、
  40 文字の途中で切れたときの読み上げの不自然さ、
  括弧や記号をまたいで切ってしまう場合
- `speechRunId` で打ち切る作り。漏れている経路が無いか
  （`utterance.onend` の連鎖、`onerror` からの Online TTS への落ち、
  safety timeout、`setTimeout` の 50ms）
- `onerror` を「1 回だけ」にした判定（`finished = true` にしてから
  `speakOnlineTTS()`）で、Online TTS 側の `handleEnd` と競合しないか
- safety timeout を分割後も同じ式のままにしたことの是非
- `<meta name="referrer" content="no-referrer">` をページ全体に効かせた
  ことの副作用（CDN 3 つ以外に影響が無いか）
- 過剰な作り込みが無いか

## 報告

`archives/agents/TODO-002/reviewer-report-2.md` に、指摘を重要な順に。
直す/直さないの判断は管理者がする。返事は 5 行以内。目安 20 分。
