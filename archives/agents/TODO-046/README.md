# TODO-046 の分担

スライドのデータを `slides-<名前>.js` からサブディレクトリ `slides/<名前>.js` へ
移した項目。実装は main が行い、確認とレビューを分けた。

| 担当 | 見たもの | 報告 |
|------|----------|------|
| verifier | 実際に HTTP で配って動くか、`measure-duration.py` が動くか | [verifier-report.md](verifier-report.md) |
| reviewer | 参照の直し漏れ、文書と実装の食い違い、規約との整合 | [reviewer-report.md](reviewer-report.md) |

## この分担にした理由

読み込み先が変わる（挙動の変更）ので、`CLAUDE.md` の「挙動が変わる項目には
確認の担当とは別にレビューの担当も入れる」に従った。実装は 3 か所の
パス文字列と文書だけで小さいため、`implementer` は立てず main が行った。

- verifier は手順が決まった確認（HTTP で 200/404、エラーメッセージ、
  スクリプトの実行）なので定義どおり Sonnet 5
- reviewer は「直し漏れが無いか」の判断が要るので Opus 5 に上書きした
