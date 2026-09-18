# TODO-005 の分担

| 担当 | 役割 | 依頼した理由 |
|------|------|--------------|
| main（Opus 5 / effort high） | 設計と実装 | 1 ファイルの 3 か所なので、実装を分ける規模ではない |
| verifier（Sonnet 5 / effort medium） | 差分と干渉の実測 | コードを変える項目なので、確認は必ず別の目に回す |
| reviewer（Sonnet 5 / effort high） | 設計とコードのレビュー | 挙動が変わる項目なので、確認とは別にレビューも入れる |

verifier には headless chromium での実測まで指示した（TODO-004 で、環境が
あるのに手計算で済まされたため）。

- [verifier の報告](verifier-report.md)
- [reviewer の報告](reviewer-report.md)
- [TODO-005 のまとめ](../../todo/TODO-005.%20スライドのタップで再生と一時停止を切り替える.md)
