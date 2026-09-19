# TODO-042 の分担

文書 1 つ（`docs/Usage.md`）を新規に書く項目。本文は main が書き、
**再現と事実の照合だけを verifier に分けた。**

文書だけの項目は main が確認してよいことになっているが、例外として
「書いたとおりに試せる手順やコマンド例があるなら、その再現は必ず分ける」
（`~/.claude/CLAUDE.md`、TODO-017）。`docs/Usage.md` には
`player.html?deck=sample` で開く手順と `tools/measure-duration.py --text` の
実行例があるので、分けた。

挙動を変える項目ではないので、レビューの担当は立てていない。

| 担当 | モデル | 依頼した内容 | 報告 |
|------|--------|--------------|------|
| verifier | Sonnet 5 / effort medium（定義のまま） | 最小の例を実際に置いて読めるか、コマンド例の出力が合うか、文書中の主張が実装と合うか | [verifier-report.md](verifier-report.md) |

verifier はモデルを上書きしていない。手順が決まった再現確認で判断が要らず、
定義の sonnet で足りたため。
