# TODO-022 の分担

| 担当 | モデル | 役割 |
|------|--------|------|
| main | Opus 5 / high | 実装 |
| verifier | Sonnet 5 / medium | 完了条件どおりかの実測確認 |
| reviewer | Sonnet 5 / high | 規約・設計に照らしたレビュー |

分担の理由: UI と再生速度の挙動が変わる項目なので、確認とレビューを分けた
（`CLAUDE.md`）。実装は 1 ファイルの十数行で main が持った。

- `verifier-report.md`
- `reviewer-report.md`
