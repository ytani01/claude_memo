# TODO-041 の分担

- **verifier**（Sonnet 5 / effort medium）… 分割前後で表示と再生が
  変わっていないかをブラウザで確認。分割は行が移るだけに見えても、
  移し漏れや初期化の順番のずれは静的に読んでも出ないため
- **reviewer**（Sonnet 5 / effort high）… 差分のレビュー。
  `?deck=` という分岐が新しく入るので、確認とは別に入れた

実装は main（Opus 5 / effort high）。行を移す作業が中心で、
判断が要るのは分割の境界と `?deck=` の設計だけだったため、
implementer には分けなかった。

- [verifier の報告](verifier-report.md)
- [reviewer の報告](reviewer-report.md)
