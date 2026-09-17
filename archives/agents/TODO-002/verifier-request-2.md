# TODO-002 確認依頼 その 2（verifier）

## 目的

2 回目の修正（`git diff`。`claude_memo.html` と `CLAUDE.md`）が
依頼どおりか確かめる。**コードは直さない。**

## 読むもの

- `archives/agents/TODO-002/implementer-request-2.md`（依頼内容と原因）
- `archives/agents/TODO-002/implementer-report-2.md`
- `git diff`

## 確かめること

1. 依頼書の「直し方」2 つ（`<meta name="referrer">`、読み上げの分割）が
   両方入っているか。`chromeResumeTimer` と `isAndroid` が残っていないか
2. `splitForSpeech()` が 17 枚すべての `narration` で
   **文字を落とさない・重複させない**か（`prepareSpeechText()` を通した後で）
3. `speechRunId` による打ち切りが効くか。一時停止・スライド送り・
   音声エンジンの切替・ミュートの各操作で、前のスライドの残りが
   読み始められないこと
4. safety timeout が分割後も足りるか。分割すると発話の間に隙間が入るので、
   合計時間が `safetyTime`（`文字数/4.5/速度*1000 + 3000`）を超えないか、
   実測して確かめる。超えるなら報告する（直さない）
5. `<script>` に構文エラーが無いか
6. `CLAUDE.md` の記述がコードと合っているか
7. **ブラウザで実際に再生して確かめる**（PC の Chrome）。
   Web Speech で最後まで読むか、Online TTS が鳴るか

## Playwright を使うときの注意

`node_modules` は `/tmp/claude-649/.../scratchpad` にある（前回入れたもの）。
**スクリプトの最後に必ず `await browser.close()` を書くこと。**
前回、閉じ忘れたプロセスが 30 分以上残って固まった。

## 報告

`archives/agents/TODO-002/verifier-report-2.md`。返事は 5 行以内。目安 20 分。
