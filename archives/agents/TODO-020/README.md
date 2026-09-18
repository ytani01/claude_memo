# TODO-020 の分担

| 担当 | モデル | 役割 |
|------|--------|------|
| main | Opus 5 / high | 実装 |
| verifier | Sonnet 5 / medium | チェックリストどおりかの実測確認 |
| reviewer | Sonnet 5 / high | 規約・設計に照らしたレビュー |

分担の理由: 進行バーと時間の計算という挙動が変わる項目なので、確認と
レビューを分けた（`CLAUDE.md`）。実装は 1 ファイルの数十行で main が持った。

- `verifier-report.md`
- `reviewer-report.md`
