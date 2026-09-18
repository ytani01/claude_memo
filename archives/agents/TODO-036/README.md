# TODO-036 の分担

| 担当 | 定義 | 役割 |
|------|------|------|
| main | — | 実装（`claude_memo.html` の SVG 6 箇所） |
| verifier | `~/.claude/agents/verifier.md`（Sonnet 5 / effort medium） | 段差の実測とスクリーンショットでの確認 |

実装を分けなかったのは、変更が属性 2 つの置き換え（6 行）で、該当箇所を
読んだ時点で diff が確定していたため。確認は「実装した本人は動くはずで
済ませる」ので、規模によらず分けた。

- [verifier の報告](verifier-report.md)
