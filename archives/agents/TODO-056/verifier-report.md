## やったこと

1. スクラッチディレクトリ（リポジトリ外）に `player.html`・`slides/_rules.js`・
   `slides/user.js` の 3 つだけを、同じ位置関係でコピーした
   （`\cp` を使用。`archives/`・`docs/`・`tools/`・`README.md`・`TODO.md` は
   コピーしていない）。
2. そこで `python3 -m http.server 8917` を起動し、以下を `curl` で確認した。

   ```
   player.html?deck=user -> 200
   slides/_rules.js       -> 200
   slides/user.js         -> 200
   slides/readme.js       -> 404  （既定デッキ用ファイルは渡していないので想定どおり）
   ```

   終了後 `kill` でサーバーを停止した。
3. `player.html` 全文（1000 行弱）を `grep -noE '(src|href)="[^"]*"'` と
   `fetch(|import(|document.write|XMLHttpRequest|\.src ?=|createElement` で
   網羅的に検索した。ローカル（相対パス）を指す参照は次の 2 箇所のみ:
   - `<script src="slides/_rules.js"></script>`（464 行目）
   - `document.write(`<script src="slides/${deckName}.js"><\/script>`)`（471 行目）
   他の `src=`/`href=` はすべて `https://` の CDN（Tailwind・Google Fonts・
   FontAwesome）。`fetch`・`XMLHttpRequest`・`createElement` の使用箇所も
   確認したが、いずれもローカルファイルの取得には関わらない
   （`createElement('button')` は DOM 操作用）。
4. `docs/User.md` の記述を 1 つずつ照合した。
   - 「渡すのは 3 つだけ」→ 上記の実測で確認。過不足なし
     （`_rules.js` を除くと 404 になり、`readme.js` を足さなくても
     `deck=user` は 200 で返ることも確認した）
   - 「`tools/`・`docs/`・`archives/`・`README.md`・`TODO.md` は要らない」→
     3 で見た通り `player.html` にはこれらへのローカル参照は無い。実際に
     コピーせずに動作したことでも裏付けられる
   - リンク `[Developer.md の「場所を選ばない」](Developer.md#場所を選ばない)`
     → `docs/Developer.md` 27 行目に `### 場所を選ばない` の見出しが実在する
     ことを確認した
   - `docs/Developer.md`・`README.md` の既存記述との整合 → 両ファイルとも
     「ネット接続が必要」「`file://` は試していない」「`public_html/` に
     置くだけで公開できる」という記述で一致している

## 結果

- 検証コマンドはすべて成功（終了コード等の失敗は無し。上記の `curl` は
  すべて期待どおりの HTTP コードを返した）
- `docs/User.md` の新規節に書かれた内容は、実際に再現して確認した範囲で
  すべて正しかった

## 見つけた問題

無し。ただし気づいた点を 1 つ書いておく（`docs/User.md` の diff の範囲外、
既存の `docs/Developer.md` 側の記述）。

- `docs/Developer.md` の「場所を選ばない」節（29 行目）は
  「`player.html` がローカルを指すのは `slides/<名前>.js` だけ」と書いており、
  `slides/_rules.js` への言及が無い。実際には `_rules.js` もローカル参照
  （464 行目）なので、この一文だけを読むと不正確に見える。今回追加された
  `docs/User.md` 側は `_rules.js` と `<名前>.js` の 2 種類ときちんと書いており
  矛盾は無いが、リンク先の Developer.md の表現がやや古い可能性がある。
  これは今回の TODO-056 の対象範囲外なので、直すかどうかの判断は管理者に
  委ねる。
