# TODO-053 の分担

`docs/Usage.md` を `docs/User.md` に、`slides/usage.js` を `slides/user.js` に
改名した項目。

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | `git mv` と、参照の追随、変わったナレーションの `duration` 測り直し | — |
| verifier | リンク切れ、`?deck=user` の再生、古い名前の残り、`duration` | `verifier-report.md` |

## この分担にした理由

- 改名と参照の直しだけで、判断の要る設計は無い。実装は main が済ませた
- **ファイル名が変わる項目は、リンク切れと取りこぼしが起きやすい**ので、
  確認は別の担当に分けた（`CLAUDE.md` の規則）
- 挙動そのものは変わらない（URL の名前が変わるだけ）ので、レビューは入れなかった
