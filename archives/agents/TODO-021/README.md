# TODO-021 の分担

| 担当 | モデル | 役割 |
|------|--------|------|
| main | Opus 5 / high | 実装 |
| verifier | Sonnet 5 / medium | 指示どおりかの確認 |
| reviewer | Sonnet 5 / high | 規約・設計に照らしたレビュー |

分担の理由: 挙動が変わる項目なので、確認とレビューを分けた（`CLAUDE.md`）。
実装は 1 ファイルの数十行で、main が持った。

- `verifier-report.md` / `verifier-report-2.md`
- `reviewer-report.md` / `reviewer-report-2.md`

2 巡目は、1 巡目の reviewer の指摘（SELECT のショートカット除外漏れ、
待ち中の即時反映）へ対応した差分が対象。
