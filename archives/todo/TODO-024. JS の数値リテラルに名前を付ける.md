# TODO-024. JS の数値リテラルに名前を付ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 7,303 | 21,760 | 76% |
| verifier | Sonnet 5 | medium | 8,738 | 42,700 | 24% |
| 合計 |  |  | 16,041 | 64,460 | 概算 $1.1 |

- verifier は定義（`.claude/agents/verifier.md`）のとおり Sonnet 5 / medium。
  上書きはしていない

## きっかけ

`claude_memo.html` の JS 部分に、意味の分からない数値がそのまま書かれていた。
`1.4`（UI の 1.0x に対する実際の速さの倍率）が代表例で、ほかにも
`2.0`（rate の上限）、`0.95`（rate の係数）、`0.85`（pitch）、
`6000` / `4.5` / `3000`（Web Speech の安全タイマー）、
`3000`（Online TTS の終了タイマーの余裕）、`180`（TTS へ渡す最大文字数）、
`50`（発話開始前の遅延）が散らばっていた。

利用者と相談し、進行バーの `100` やミリ秒換算の `1000` のような自明なものも
含めて、JS 全体の数値を対象にすると決めた。

## やったこと

`claude_memo.html` の 1 ファイルだけを変更した。定義部（`getEffectiveSpeed` の
近く）に定数をまとめて置き、使用箇所を置き換えた。**挙動は変えていない。**

- `baseSpeedMultiplier` → `BASE_SPEED_MULTIPLIER`（他の定数と命名をそろえた。
  コメント 2 箇所の参照も直した）
- 単位・換算: `MS_PER_SECOND`、`SECONDS_PER_MINUTE`、`PROGRESS_MAX_PERCENT`
- 表示: `SLIDE_BASE_WIDTH_PX`（960）、`SLIDE_ASPECT_RATIO`（16 / 9）
- 読み上げ: `MAX_SPEECH_RATE`、`WEB_SPEECH_RATE_FACTOR`、`WEB_SPEECH_PITCH`、
  `SPEECH_START_DELAY_MS`、`SPEECH_SAFETY_MIN_MS`、`SPEECH_CHARS_PER_SECOND`、
  `SPEECH_SAFETY_MARGIN_MS`、`TTS_END_MARGIN_MS`、`TTS_MAX_CHARS`

行末に付いていた説明のコメント（「ほんの少しゆったりとしたテンポ感」
「ピッチを 0.85 に下げ…」）は、定数の定義側へ移した。

触らなかったもの:

- `slideData` の `id` と `duration`（原稿そのもの）
- `splitForSpeech(text, maxLen = 40, minLen = 20)` の `40` / `20`。
  デフォルト引数として既に名前が付いており、定数にしても読みやすさは変わらない
- `volume = 0` / `1`、`padStart(2, '0')`、配列の添字の `0` / `1` のような、
  名前を付けても増えるだけのもの

## 確かめたこと

verifier（Sonnet 5 / medium）が確認した。報告は
`../agents/TODO-024/verifier-report.md`。

- `git diff` の全 hunk で、置換前後の値が一致し、演算子の並びと括弧も
  変わっていない（複数行に折り返した箇所も優先順位は同じ）
- 定数名と使われ方が一致している。`MS_PER_SECOND` は秒→ミリ秒換算の
  8 箇所だけに使われている
- 旧名 `baseSpeedMultiplier` はコメントを含めて残っていない
- JS 部分を切り出した `node --check` が通る

## 分担の振り返り

- verifier は、差分の値の一致・`node --check`・旧名の残存を一通り確かめ、
  そのうえで `splitForSpeech` の `40` / `20` が残っていることを挙げてきた。
  値の取り違えは見つからなかった
- 見込みと食い違わなかった。1 ファイル内の置換なので実装は main が持ち、
  確認だけ分ける形で足りた
- 次に同じ規模（1 ファイル内の機械的な置換、挙動は変えない）をやるなら、
  同じく main が実装して verifier だけ立てる。reviewer は要らない。
  ただし確認の依頼には**「残っている数値を、定数にすべきものと残してよいものに
  分けて挙げる」**まで書くこと。今回それを書いたので判断が要る点が上がってきた
