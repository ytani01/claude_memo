# TODO-053 verifier 報告

## 走らせた検証

1. `node --check slides/user.js slides/developer.js slides/readme.js`
   → 成功（終了コード 0、出力なし）
2. `python3 -m http.server 8791` を立てて `curl` で存在確認
   - `/player.html` 200、`/slides/user.js` 200、`/docs/User.md` 200
   - `/slides/usage.js` 404、`/docs/Usage.md` 404（旧ファイルは実在しないので想定どおり）
3. Playwright（`/tmp/verify064b/node_modules/playwright`、このリポジトリに
   node_modules が無いため借用）で 3 デッキを開いた
   - `?deck=` 無し（readme）: `01 / 10`、コンソールエラー無し
   - `?deck=user`: `01 / 11`、コンソールエラー無し
   - `?deck=developer`: `01 / 11`、コンソールエラー無し
   - `console` の `error` と `pageerror` の両方を拾ったが 3 デッキとも空配列
4. `tools/measure-duration.py --write` 無しで 3 枚を実測し、ファイルの
   `duration` と突き合わせ（全て一致）
   - `user` 8 枚目: 実測 `duration: 9` / ファイル `9` 一致
   - `user` 11 枚目: 実測 `duration: 10` / ファイル `10` 一致
   - `developer` 1 枚目: 実測 `duration: 11` / ファイル `11` 一致
5. `python3 tools/test_measure_duration.py` → `OK`（終了コード 0）

すべて成功。落ちた検証は無い。

## 変更されたファイルと範囲

`git status` は次のとおり:

- リネーム: `docs/Usage.md` → `docs/User.md`、`slides/usage.js` → `slides/user.js`
- 変更: `CLAUDE.md`、`README.md`、`docs/Developer.md`、`docs/User.md`、
  `slides/developer.js`、`slides/readme.js`、`slides/user.js`

TODO-053 の指示（`README.md`・`docs/Developer.md`・`CLAUDE.md`・`slides/*.js`
の中の `Usage.md` と `?deck=usage` を直す）と範囲は一致している。指示に
無いファイルの変更は無い。

`git diff` で `docs/Usage.md` 由来の `slides/user.js` との差分を取ったところ、
リネーム以外に想定どおりの変更のみ:

- ヘッダーコメントの `deck=usage`→`deck=user`、`docs/Usage.md`→`docs/User.md`
- 8 枚目のナレーション中の `Usage.md`→`User.md`（文字数が 1 減ったため
  `duration` も `10`→`9` に変わっている。上記 4 で実測と一致を確認済み）
- 8 枚目の見出しカード内の `docs/Usage.md`→`docs/User.md`
- 11 枚目のナレーション・本文中の `Usage.md`→`User.md`（`duration` は
  `10` のまま変わっていない。実測でも `10` と出て一致）

`developer.js` の 1 枚目はナレーション中の `Usage.mdで足ります` を
`User.mdで足ります` に直しており、文字数が 1 減って `duration` が
`12`→`11` に変わっている（実測と一致）。

`slides/readme.js` は `usage` デッキの節にあった `--deck usage` コマンド例と
出力例の `usage.js` を `--deck user` / `user.js` に直しているのみ。
ナレーションや `duration` は変わっていない。

## `?deck=user` の再生確認

上記 3 の Playwright 確認どおり、1 枚目が表示され、コンソールエラーも
`pageerror` も無く、総枚数 `11` を確認した。`?deck=` 無し（`readme`）と
`?deck=developer` も壊れていない。

## 古い名前の残存（判断が要る点）

`archives/` と `TODO.md` 以外で、`Usage.md`・`?deck=usage`・`usage.js` という
**固有名詞としての残存は無い**（`grep -rn "deck=usage"` などで確認）。

ただし、**単語としての `usage`（デッキ名としての言及）が 4 箇所残っている**。
TODO-053 の指示は「`Usage.md` と `?deck=usage` を直す」であり、この単語
そのものへの言及は明示的な対象になっていないため、指示違反とまでは
言い切れないが、放置するとデッキ一覧の表記と実際のデッキ名がずれる。
見つけた箇所:

1. `README.md:59` — 「入っているスライド」表の行
   `| \`usage\` | スライドの作り方 |`
2. `CLAUDE.md:8` — 「`readme`・`usage`・`developer`・`claude-memo` の
   4 デッキ」という構成の説明
3. `docs/Developer.md:14` — リポジトリ構成表の
   `| \`slides/<名前>.js\` | スライドのデータ。\`readme\`・\`usage\`・
   \`developer\`・\`claude-memo\` |`
4. `slides/readme.js:223, 237` — 9 枚目のナレーション（「作り方を説明する
   usage」）と、デッキ一覧テーブルの行
   `<tr><td ...>usage</td><td ...>スライドの作り方</td></tr>`

これらは `docs/User.md` へのリンクではなく、デッキ名の記述そのものが
`usage` のまま残っている。デッキ名を `user` に揃える方針（TODO-053 で
決めた「デッキ名も `user` に揃える」）に照らすと、この 4 箇所も直すべきか
どうかは管理者の判断が要る。

## 確かめられなかったこと

- リンクの実在確認は `curl` によるファイル存在確認と Playwright の目視
  相当（コンソールエラー無し）で行った。相対リンクを 1 つずつ機械的に
  抽出して全数チェックする、までは行っていない
  （`docs/User.md`・`README.md`・`CLAUDE.md`・`docs/Developer.md` を
  読んで `.md` へのリンクは目視でも確認した）
- Playwright はこのリポジトリに `node_modules` が無かったため、
  `/tmp/verify064b/node_modules/playwright` を借用して実行した
