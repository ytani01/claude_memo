# TODO-052 verifier report

## 1. git diff の範囲
`git diff` は `slides/developer.js`（1 箇所）、`slides/readme.js`（3 箇所）、
`slides/user.js`（1 箇所）のみ。すべて `duration:` の数値の変更で、
ナレーション本文や他の箇所には手が入っていない。確認済み。

## 2. ASCII 英字の残り
`tools/measure-duration.py` を import し、4 デッキ全ナレーションに
`prepare()` を当てて英字（`[A-Za-z]+`）の残りを数えた。

- readme（10 枚）: 残り 0
- user（11 枚）: 残り 0
- developer（11 枚）: 残り 0
- claude-memo（17 枚）: 残りあり（`Raspberry` `Pi` `PC` `SSH` `AI` `Opus`
  `Sonnet` `Haiku` `ID` `MCP` `Ctrl` `G` `OpenAI` `Codex` `Obsidian` など）。
  指示どおり、claude-memo に固有名詞・略語が残るのは元からの仕様として
  問題無しと判断。

readme / user / developer に残りは無い。目標達成。

## 3. 当てる順序
- `player.html` の `prepareSpeechText()`（607〜609 行付近）:
  `const rules = (deckConfig.rules || []).concat(SPEECH_RULES);` で
  デッキ側が先、共通表（`slides/_rules.js` の `SPEECH_RULES`）が後。
- `tools/measure-duration.py` の `prepare()`（87 行付近）:
  `for pattern, replacement, flags in load_deck_rules(deck) + load_common_rules():`
  でも同じくデッキ側が先、共通が後。

両者は順序・対象ファイルとも一致している。

## 4. 置換表の広く当たりすぎるパターン
`slides/_rules.js` を読んだ。`px\b` と `rem\b` は前側に `\b` が無い
（`px\b`）ため、理屈上は語の末尾が偶然 "px" になる単語（例:
英単語の一部）にも当たり得る。ただし実際のナレーションで `px` を含む
箇所（`developer.js` の「768px」、`user.js` の「px や rem」）に対して
`prepare()` を実際に当てて確認したところ、いずれも意図通り
「ピクセル」に変換され、日本語側の誤爆も無かった。**実害は確認できな
かったが、パターン自体は本来 `\bpx\b` にしたほうが安全**（現状でも
問題は起きていないので、直すかどうかは管理者の判断）。

そのほかの置換（`\bslides\b`、`\bdeck\b`、`\buser\b` など）は
`deckConfig` や `User.md` などの複合語のルールが先に来ているため、
実際の当たり方を試した範囲では問題は見つからなかった。

## 5. duration の実測確認
変わった 5 枚を `tools/measure-duration.py --deck <名前> <番号>` で
測り直し、ファイルの値と比較した。

| デッキ | スライド | 測定結果 | ファイルの値 | 一致 |
|---|---|---|---|---|
| readme | 1 | duration: 11 | 11 | ○ |
| readme | 4 | duration: 9 | 9 | ○ |
| readme | 10 | duration: 9 | 9 | ○ |
| user | 3 | duration: 11 | 11 | ○ |
| developer | 1 | duration: 12 | 12 | ○ |

5 枚とも一致。

## 確かめられなかったこと・判断が要る点
- 「4. 実際に再生して読みを聴き、直すものがあれば直す」は
  `TODO.md` 上まだ未チェックの項目であり、本タスクの依頼範囲外なので
  聴取確認は行っていない（音声再生は本タスクの指示に含まれていない）。
- `px\b` / `rem\b` の先頭 `\b` が無い点は、今回のナレーションでは実害が
  無いことを確認したが、将来ナレーションに "px" で終わる英単語が
  混ざった場合に誤爆する可能性は残る。直すかどうかは管理者の判断。
