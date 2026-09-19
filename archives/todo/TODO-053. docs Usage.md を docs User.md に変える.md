# TODO-053. `docs/Usage.md` を `docs/User.md` に変える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 9,574 | 32,633 | 80% |
| verifier | Sonnet 5 | medium | 7,725 | 50,158 | 16% |
| 合計 |  |  | 17,299 | 82,791 | 概算 $2.4 |

- verifier は定義のまま
- 集計した範囲には、利用者からの別の質問（ターミナルに出る差分表示を
  抑えられるか）で動かした `claude-code-guide` の分も入っている。
  この項目とは関係が無いので表から外した（Haiku 4.5 / output 913 /
  cache_creation 28,299 / 概算 $0.0）

## きっかけ

「使い方」よりも「この文書は誰向けか」が分かる名前にする。
`Developer.md`（`player.html` を直す人）と並べたとき、`User.md`
（スライドを作る人）のほうが対になる。

## 決めたこと

- **デッキ名も `user` に揃える。** `slides/usage.js` は `slides/user.js` に、
  URL は `player.html?deck=user` になる
- 旧 URL（`?deck=usage`）のリダイレクトは用意しない。公開して間もなく、
  外から参照されていないため

## やったこと

- `git mv docs/Usage.md docs/User.md`、`git mv slides/usage.js slides/user.js`
- `README.md`・`CLAUDE.md`・`docs/Developer.md`・`docs/User.md`・
  `slides/readme.js`・`slides/developer.js`・`tools/measure-duration.py` の
  中の `Usage.md`・`?deck=usage`・`usage.js` と、**デッキ名としての `usage`** を直した
- **ナレーションが変わった 4 枚の `duration` を測り直した。**
  `user` の 8 枚目（10 → 9）、`developer` の 1 枚目（12 → 11）。
  `user` の 11 枚目と `readme` の 9 枚目は測り直しても値が変わらなかった

## 確かめたこと

verifier が確認した（報告は `archives/agents/TODO-053/verifier-report.md`）。

- 相対リンクがすべて実在するファイルを指している
- `?deck=user` が再生でき（11 枚）、`readme` と `developer` も壊れていない。
  コンソールにエラー無し
- `node --check` が 3 ファイルとも通る。自己テストも通る
- 測り直した 3 枚の `duration` が実測と一致

**verifier が「デッキ名としての `usage`」の残りを 4 か所見つけた。**
`README.md` のデッキ一覧、`CLAUDE.md` の構成、`docs/Developer.md` の表、
`slides/readme.js`（ナレーションと一覧の表）。main は `Usage.md` と
`?deck=usage` という**固有名詞の形でしか探していなかった**。指摘を受けて直し、
`slides/readme.js` の 9 枚目を測り直した（値は変わらず）。

## 分担の振り返り

- **verifier が拾ったのは「指示の字面の外」だった。** 依頼書には
  「`Usage.md`・`?deck=usage`・`usage.js` が残っていないか」と書いたが、
  verifier はそれらが無いことを確かめたうえで、**デッキ名としての `usage`**
  が残っていることを別立てで報告した。判断は管理者に返している（指示どおり）
- **改名の項目では、探す文字列を「固有名詞の形」で書くと取りこぼす。**
  次は「旧名が単語として出てくる箇所も挙げる」と依頼書に書く
- **見込み（verifier 1 人）と食い違わなかった。**
- **次に同じ規模（改名と参照の追随）をやるなら、同じく verifier 1 人でよい。**
  レビューは要らなかった（挙動が変わらないため）
