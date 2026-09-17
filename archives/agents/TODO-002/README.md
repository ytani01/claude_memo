# TODO-002 の分担

`claude_memo.html` 1 ファイルの変更だが、挙動が変わり、分岐が増えるので、
実装・確認・レビューを分けた（`~/.claude/CLAUDE.md` の規則どおり）。
原因の見立てを外して **2 巡した**ので、各担当の報告も 2 組ある。

| 担当 | モデル | 役割 |
|---|---|---|
| main | Opus 5 | 調査、原因の特定、依頼書、追加修正、決着 |
| implementer | Opus 5（定義は sonnet） | 依頼書どおりの実装 |
| verifier | Sonnet 5 | 依頼どおりか、構文、範囲の確認 |
| reviewer | Opus 5（定義は sonnet） | 分岐と条件式のレビュー |

implementer と reviewer を Opus に上げたのは、原因の切り分けと、
分割読みの分岐が増えることによる競合の見落としを防ぐため。

## ファイル

- `main-investigation.md` — 最初の調査。**結論は 2 つとも外れている**
- `implementer-request.md` / `implementer-report.md` — 1 巡目
- `verifier-request.md` / `verifier-report.md` — 1 巡目（末尾に追加確認）
- `reviewer-request.md` / `reviewer-report.md` — 1 巡目
- `implementer-request-2.md` / `implementer-report-2.md` — 2 巡目
- `verifier-request-2.md` / `verifier-report-2.md` — 2 巡目（末尾に追加確認）
- `reviewer-request-2.md` / `reviewer-report-2.md` — 2 巡目

振り返りは `archives/todo/TODO-002. Android Chrome での読み上げを直す.md`。
