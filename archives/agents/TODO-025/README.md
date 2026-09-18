# TODO-025 の分担

| 担当 | 何を頼んだか |
|------|--------------|
| main | 実装（並べ替えとスライド 2 の書き直し） |
| verifier | 並び・`id`・`duration`・レイアウトの確認 |

並べ替えは配列要素の入れ替えと `id` の振り直しだけ、スライド 2 は 1 枚の
差し替えなので、**実装は main が直接書いた**（`TODO.md` の見込みでは
implementer も立てる予定だったが、着手してみて分ける規模ではなかった）。
分岐も条件式も変わらないためレビューは立てず、**確認だけ分けた**。

- [verifier-request.md](verifier-request.md) — 依頼
- [verifier-report.md](verifier-report.md) — 報告（15/15 通過）
- [internal-overflow-check.mjs](internal-overflow-check.mjs) — verifier が
  足した Playwright スクリプト。`#slide-canvas` は `overflow-hidden` なので、
  **ページ全体がはみ出さなくてもカード内部で見切れることがある**。
  `scrollHeight`/`clientHeight` と各カードの矩形を測って、それを捕まえる。
  **カードや行を増やす変更では、これも合わせて走らせる**

前後比較の本体は [TODO-029/layout-check.mjs](../TODO-029/layout-check.mjs) を
直して使い回させた（組み直させていない）。
