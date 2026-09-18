# TODO-004 の分担

| 担当 | 役割 | 依頼した理由 |
|------|------|--------------|
| main（Opus 5 / effort high） | 原因の特定と実装 | 変更が CSS 1 か所なので、実装を分ける規模ではない |
| verifier（Sonnet 5 / effort medium） | 差分と周辺の規則の確認 | コードを変える項目なので、確認は必ず別の目に回す |

reviewer は入れていない。分岐や条件式は変わらず、`#viewport-stage.is-fullscreen` の
高さの基準を替えるだけだったため。

- [verifier の報告](verifier-report.md)
- [TODO-004 のまとめ](../../todo/TODO-004.%20横持ちのスマホでフルスクリーンの高さを画面に合わせる.md)
