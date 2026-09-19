# TODO-044 verifier report

対象: `docs/Developer.md` の「置き場所は選ばない」節（`git diff HEAD` の差分 1 か所）。
根拠: `player.html`（1339 行）、`claude_memo.html`（16 行）。

## 1. 手順の再現

`player.html` と `slides-claude-memo.js` を scratchpad 配下の別ディレクトリへコピーし、
`python3 -m http.server 18234` を起動して確認。

- `curl` で `player.html` → 200
- `curl` で `slides-claude-memo.js` → 200

確認後、`pgrep` で PID を確認してから `kill`、コピーしたディレクトリは `\rm -rf` で削除済み。
（削除直後の `pgrep -f "http.server 18234"` は誤検出で、実体は無し。`ps -ef` で
プロセスが存在しないことを確認済み）。

手順どおりに動く。一致。

## 2. 主張の照合

- **「ローカルを指しているのは `slides-<名前>.js` の 1 か所だけ」**
  `player.html` 全体を `src=` / `href=` / `fetch(` / `import(` / `url(` /
  `new Audio` / `new Image` / `.src =` / `document.write` などで洗い出した。
  ローカル参照は 467 行目の `document.write(\`<script src="slides-${deckName}.js"><\/script>\`)`
  の 1 か所のみ。一致。
- **「残りは全部 CDN の https」**
  `player.html` 中の `https://` は次の 6 件のみ。すべて外部 CDN / API:
  - `https://cdn.tailwindcss.com`（Tailwind）
  - `https://fonts.googleapis.com`（Google Fonts, preconnect）
  - `https://fonts.gstatic.com`（Google Fonts, preconnect）
  - `https://fonts.googleapis.com/css2?family=Noto+Sans+JP...&family=JetBrains+Mono...`（Google Fonts 本体）
  - `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css`（FontAwesome）
  - `https://translate.google.com/translate_tts?...`（読み上げ音声のフォールバック、821 行目 `ttsUrl`）
  一致。
- **`claude_memo.html` のリダイレクト先も相対パス**
  `location.replace('player.html?deck=claude-memo')` および
  `<meta http-equiv="refresh" content="0; url=player.html?deck=claude-memo">`、
  本文中の `<a href="player.html?deck=claude-memo">` の 3 か所とも相対パス。一致。
- **外部から取っているものの列挙（Tailwind・Google Fonts・FontAwesome・読み上げの音声）**
  上記の https 一覧と過不足なく一致。

## 3. 「試していない」の書き方について

`file://` を試していない、という書き方（断定せず「試していない」と明記し、
`document.write` による相対 `<script>` 読み込みと外部音声要求がブラウザ制限に
当たる「可能性がある」とだけ書いている点）は、確認できていない事実として
適切な書き方になっている。実際に試して確定させる必要は無い、という指示どおり
今回は試していない。

## 確かめられなかったこと・判断できないこと

- `file://` で実際に開いたときにどう壊れるか（あるいは壊れないか）は、
  ブラウザが使える環境が無いため未検証。文書もその前提で書かれている。
- 「公開 URL を変えたくないなら、元の場所にリダイレクトかシンボリックリンクを
  残す」という提案の妥当性は、運用方針そのものの判断であり、今回の検証範囲
  （事実確認）の外と考え、立ち入っていない。

## 結論

節の主張はすべて `player.html` / `claude_memo.html` の中身と一致し、
手順（`python3 -m http.server` での配布）もそのとおりに動く。食い違いは無かった。
