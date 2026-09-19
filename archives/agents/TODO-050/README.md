# TODO-050 の分担

`tools/measure-duration.py` に `--write` を足し、測った値を
`slides/claude-memo.js` の `duration` へ書き戻せるようにした項目。

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | 実装（`--write`、`apply_durations()` の切り出し、docs の更新） | — |
| verifier | 書いたとおりに動くか、既存 17 枚の値が実測と合っているか | `verifier-report.md` |
| reviewer | 差分の設計と規約（写しのずれ、書き戻しの安全さ） | `reviewer-report.md` |

## この分担にした理由

- 1 ファイルの小さな変更だが、**ファイルを書き換える**機能なので
  確認は main から分けた（`CLAUDE.md` の規則）
- 新しいオプションが増えて挙動が変わるので、確認とは別にレビューも入れた
- 実装は 1 ファイルに閉じるので implementer は立てず、main が書いた
