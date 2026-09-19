# TODO-049 の分担

| 担当 | モデル | effort | 役割 |
|------|--------|--------|------|
| main | Opus 5 | high | 実装（`docs/Developer.md`・`docs/Usage.md`・`tools/measure-duration.py`） |
| verifier | Sonnet 5 | medium | 実装の確認（[報告](verifier-report.md)） |

## この分担にした理由

文書とスクリプトだけを変える項目だが、確かめる中身が「書式が揃っているか」
ではなく「書いた定数名が `player.html` に実在し、値が合っているか」なので、
`CLAUDE.md` の例外（main が確認してよい場合）には当たらない。確認を
verifier に分けた。

`docs/Usage.md` にスクリプトの実行例を貼り直したので、**その再現を必ず
別の担当にやらせる**という方針（TODO-017）に従い、verifier に実際に
`tools/measure-duration.py` を動かさせて出力との一致を確かめさせた。

TODO-048 と同時に着手したので、verifier は 2 つ並列で動かした。
