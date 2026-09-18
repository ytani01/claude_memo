# TODO-023 の分担

| 担当 | 役割 |
|------|------|
| main | スライド 2 の差し替え、読みの置換の追加、`duration` の修正 |
| verifier | 差分の範囲、`duration` と実測の一致、レイアウトのはみ出しの確認 |

実装は `claude_memo.html` 1 ファイルの `slideData[1]` と
`prepareSpeechText()` に閉じるので、実装の担当は分けず main がやった。
分岐や条件式は変わらないので reviewer は入れていない。

確認は verifier に分けた。`duration` は Google Translate TTS の音声を
`ffprobe` で測らないと確かめられず（TODO-018）、実装した本人は
「19 のままでよいはず」で済ませてしまう。実際、読みの置換を足したあとの
測り直しでスライド 10 のずれ（20 → 19）が見つかった。

- `verifier-request.md` — 1 回目の依頼
- `verifier-report.md` — 1 回目（スライド 2 の差し替え）
- `verifier-report-2.md` — 2 回目（読みの置換を足したあとの測り直し）
- `verifier-report-3.md` — 3 回目（`duration` 修正後の仕上がり）

2 回目・3 回目の依頼は `SendMessage` で同じ verifier に送ったので、
依頼のファイルは残っていない。内容は各報告の冒頭にある。
