# TODO-016 の分担

項目: [TODO-016. 未使用の定義と冗長な記述を削る](../../../TODO.md)
（決着後は `archives/todo/TODO-016. ….md`）

見込みと実施、消費トークンの表は TODO のファイル側にある（ここには写さない）。

| 担当 | 役割 | モデル |
|------|------|--------|
| implementer | `claude_memo.html` の 9 か所を直す | Opus 5（定義は sonnet） |
| verifier | 指示どおり直っているか、参照漏れが無いかを確かめる | Sonnet 5（定義のまま） |
| reviewer | 描画結果と動作が変わっていないかを見る | Opus 5（定義は sonnet） |

## この分担にした理由

- TODO-014 と同型（見た目と動作を変えない整理）なので、同じ 3 担当にした
- implementer を上げたのは、CSS の上書き順（`@media` の統合、
  `width: 100%` の削除）が計算値に効くため
- reviewer を上げたのは、この項目の合否が「動作が変わらないこと」の
  判定そのものだから。整形に見えて分岐の意味が変わっていないかを見る
- verifier は手順の決まった確認（`node --check`、削除した識別子の grep）
  なので定義のまま

## 報告

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
- [reviewer-report.md](reviewer-report.md)
