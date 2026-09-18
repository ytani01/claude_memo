# TODO-039 の分担

| 担当 | モデル | 役割 |
|------|--------|------|
| main | Opus 5 / effort high | スライド 6 の文言・注釈・`duration` の修正 |
| verifier | Sonnet 5 / effort medium | 秒数の実測と、2 つの画面サイズでの表示確認 |

1 スライドの文言と見た目だけの変更なので implementer は立てていない。
挙動や分岐が変わらないので reviewer も立てていない。`duration` の実測と
レイアウトの確認は、実装した本人が省きやすいので verifier に分けた。

- [verifier への依頼](verifier-request.md)
- [verifier の報告](verifier-report.md)
