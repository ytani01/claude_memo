# TODO-009 の分担

| 担当 | 役割 | 報告 |
|------|------|------|
| main | 原因の特定、方針の相談、実装（メディアクエリ 1 行とコメント、`CLAUDE.md`） | — |
| verifier | Playwright で 3 条件 × 17 スライドの実測 | [verifier-report.md](verifier-report.md) |
| reviewer | 差分が及ぶ範囲のレビュー（挙動が変わる変更のため） | [reviewer-report.md](reviewer-report.md) |

分担の理由: 差分は 1 行だが、メディアクエリの条件を広げる変更なので挙動が変わる。
`CLAUDE.md` の決まりどおり、確認（verifier）とレビュー（reviewer）を分けた。
実装は差分が小さい見込みだったので main が直接行い、implementer は立てていない。

実測の生データとスクリプトは `measure-output.json` / `measure.js.txt`。
