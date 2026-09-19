# TODO-051 の分担

`README.md` を書き直し、その内容と `docs/` の 2 つをスライドにした項目。

| 担当 | 見たもの | 報告 |
|------|----------|------|
| main | `measure-duration.py` の `--deck` 対応、`README.md` の書き直し、`duration` の実測、既定デッキの切り替え、文書の追随 | — |
| implementer（readme） | `slides/readme.js` | `implementer-readme-report.md` |
| implementer（usage） | `slides/usage.js` | `implementer-usage-report.md` |
| implementer（developer） | `slides/developer.js` | `implementer-developer-report.md` |
| verifier | 3 デッキの再生、`duration` の突き合わせ、見た目 | `verifier-report.md` |
| reviewer | 素材との食い違い、既定変更の取りこぼし | `reviewer-report.md` |

## この分担にした理由

- デッキ 3 つは互いに独立していて、素材（`README.md` と `docs/` の 2 つ）も
  別々なので、**3 人に並列で書かせた**。同じファイルを触らないので衝突しない
- `README.md` の書き直しは**アピールの方針を決める作業**なので main が書き、
  それを素材として implementer に渡した
- `duration` の実測はネットワーク越しで時間がかかるうえ、3 デッキまとめて
  やるほうが速いので main が引き取った
- 既定のデッキを変える（挙動が変わる）ので、確認とは別にレビューも入れた
