# TODO-010 の分担

挙動が変わり、既存のタップ（TODO-005）と同じ要素に載る項目なので、
実装（main）とは別に確認とレビューを分けた。

- **verifier**（Sonnet 5 / effort medium）: 実装が指示どおり動くかを実測で
  確かめる。ブラウザ自動化が使えるかの調査から任せた → `verifier-report.md`
- **reviewer**（Sonnet 5 / effort high）: しきい値の妥当性、既存ハンドラとの
  干渉、フラグの落とし方を規約と設計に照らして見る → `reviewer-report.md`

どちらもコードは直させず、報告だけさせた。時間のしきい値を外す判断は
利用者が選び、main が反映してから verifier に再検証させた。

2 つの表と振り返りは
`archives/todo/TODO-010. スマホのスワイプでスライドを切り替える.md` にある。
