# TODO-033 の分担

| 担当 | 役割 |
|------|------|
| main（Opus 5 / high） | 並べ替えと文言の実装、`duration` の測定、`CLAUDE.md` の更新 |
| verifier（Sonnet 5 / medium） | 並び・実測・表示の確認。コードは直さない |

**実装と確認を分けた理由**（`~/.claude/CLAUDE.md`）。文言と並びだけの項目で
分岐は変わらないので、reviewer は立てなかった。

利用者の文言の指示が 6 回に分かれたため、**同じ verifier に追加の依頼を
送り続けて使い回した**（立て直すと Playwright の組み直しから始まる）。

- `verifier-request.md` — 最初の依頼
- `verifier-report.md` — 6 回分の報告（追記式）
