# TODO-029 の分担

| 担当 | 何を頼んだか |
|------|--------------|
| main | 実装（フッターと `category` の削除） |
| verifier | 削除で表示と動作が壊れていないかの確認 |

削除だけで分岐も条件式も変わらないため、**実装は main が直接書き、
レビューは立てなかった**。ただし `CLAUDE.md` の「実装した本人は
『動くはず』で済ませてしまう」に従い、**確認は必ず分けた**。

- [verifier-request.md](verifier-request.md) — 依頼
- [verifier-report.md](verifier-report.md) — 報告（15/15 通過）
- [layout-check.mjs](layout-check.mjs) — verifier が組んだ Playwright の
  前後比較スクリプト。変更前（`git show HEAD:claude_memo.html`）と
  作業ツリーをそれぞれローカル HTTP サーバーに載せ、4 条件
  （PC 1280x800 / 横持ち 844x390 の通常とフルスクリーン /
  縦持ち 390x844 フルスクリーン）のはみ出しを測って比べる。
  **同じ前後比較をする項目では、これを渡して使い回させる**
  （毎回組ませると cache_creation が同じだけかかる）
