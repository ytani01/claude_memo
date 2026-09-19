# TODO-058 の分担

「デッキ」をやめ、識別子の `deck` も `slides` に変える。

## 誰にどこを担当させたか

| 担当 | 範囲 |
|------|------|
| implementer | 識別子のリネーム（`?slides=`、`slidesConfig`、`--slides`、`slides-heading`、`slidesName`、`tools/` の関数名）、旧 `?deck=` の後方互換、`slides/_rules.js` の置換表の入れ替え |
| wording | 日本語の文章の「デッキ」を「スライド一式」に言い換える（`README.md`、`CLAUDE.md`、`docs/*.md`、`player.html` のコメント、`slides/*.js` のコメント・本文・ナレーション） |
| main | 言い換え後の `duration` の測り直し（`tools/measure-duration.py --all --write`） |
| verifier | 指示どおりに直っているか、テストと実行が通るかの確認 |
| reviewer | 規約と設計に照らしたレビュー |

## その分担にした理由

- **識別子と日本語の文章を分けた。** 同じファイルを触るので同時には動かせないが、
  片方は機械的な置換、もう片方は言い回しの判断で、必要な注意が違う。
  混ぜると「置換し忘れ」と「言い回しが変」が同じ差分に混ざって切り分けにくい
- **reviewer を入れた。** 分岐が 1 つ増える（`slides` が無ければ `deck` を見る）。
  テストが通ることを見ても、分岐の意味が正しいかは捕まえられない
- **`duration` の測り直しは main がやった。** `--all --write` を流すだけで
  判断が要らない

## 報告

- [implementer](implementer-report.md)
- [wording](wording-report.md)
- [verifier](verifier-report.md)
- [reviewer](reviewer-report.md)
