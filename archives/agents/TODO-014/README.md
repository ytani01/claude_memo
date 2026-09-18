# TODO-014 の分担

|| 担当 | モデル | 役割 |
|---|---|---|---|
| implementer | Opus 5 | `claude_memo.html` の重複整理 9 件を実装する |
| verifier | Sonnet | 9 件がすべて実施され、構文と参照が壊れていないかを確かめる |
| reviewer | Opus 5 | 描画結果・動作が変わっていないかを差分で見る |

## 理由

- 1 ファイル内の整理だが、CSS の上書き順・`classList.toggle` の切り替え・
  シークバーの境界判定と、分岐の意味が変わり得る箇所を含むので、
  実装・確認・レビューを分けた
- ブラウザでの実機確認は利用者が行う。担当は静的な確認までとする

## 報告

- [implementer-report.md](implementer-report.md) — 9 項目それぞれの実施内容と減った行数
- [verifier-report.md](verifier-report.md) — 項目ごとの実施確認、CSS 計算値の突き合わせ、`node --check`
- [reviewer-report.md](reviewer-report.md) — 動作が変わらないことの根拠、境界の実測
