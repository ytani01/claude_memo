# TODO-045 の分担

| 担当 | モデル | 役割 |
|------|--------|------|
| main | Opus 5 / effort high | 利用者と内容を決め、`README.md` を書く |
| verifier | Sonnet 5 / effort medium | 構成表・手順・リンク・事実の確認 |

文書だけの項目だが、ファイル構成の表と `python3 -m http.server` の手順は
**書いたとおりに試せる**ので、再現を main から分けた（`~/.claude/CLAUDE.md`
の「README の手順やコマンド例のように、書いたとおりに試せるものがあるなら、
その再現は必ず分ける」）。挙動は変わらないので reviewer は立てていない。

- [verifier-report.md](verifier-report.md) — 確認の報告
