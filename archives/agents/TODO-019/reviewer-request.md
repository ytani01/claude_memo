# TODO-019 レビュー依頼（reviewer）

## 目的

`speakOnlineTTS()` に足した安全タイマーを、設計と規約に照らしてレビューする。
コードは直さないこと。問題と根拠を報告するだけ。

## 対象範囲

`git diff` の差分（`claude_memo.html` の `stopSpeech()` と
`speakOnlineTTS()`）。周辺として `speakCurrentNarration()` の Web Speech 側の
安全タイマー、`onSlideAudioFinished()`、`slideTransitionTimeout` の扱いを読む。

## 見てほしい点

- `slideTransitionTimeout` を安全タイマーと次スライドへの待ちで共有している。
  取り違えや二重起動が起きないか
- `speechRunId` を見ていないが、`stopSpeech()` の後始末だけで足りているか
- 余裕 3 秒（Web Speech 側と同じ値）が妥当か。再生速度を変えたときの挙動
- `onloadedmetadata` が `src` 差し替え前に消されているか、使い回しの要素で
  前のスライドのイベントが残らないか
- TODO-018 で合わせた進行バー・時間表示への影響

## 完了条件

上記それぞれについて、問題なしか、問題ありなら行番号と根拠を書く。

目安 20 分。

## 報告先

`archives/agents/TODO-019/reviewer-report.md`
返事は 5 行以内。
