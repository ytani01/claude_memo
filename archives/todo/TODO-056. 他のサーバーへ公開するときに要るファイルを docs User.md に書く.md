# TODO-056. 他のサーバーへ公開するときに要るファイルを `docs/User.md` に書く

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 5,822 | 16,713 | 80% |
| verifier | Sonnet 5 | medium | 4,250 | 29,312 | 20% |
| 合計 |  |  | 10,072 | 46,025 | 概算 $0.8 |

- verifier は `~/.claude/agents/verifier.md` の定義どおり（model: sonnet /
  effort: medium）。上書きしていない

## きっかけ

`docs/User.md` の「公開」の節は「`public_html/` 下なので置くだけ」で止まって
いて、他のサーバーへ持っていくときに何を渡せばよいかが書いていなかった。
同じ趣旨は `docs/Developer.md` の「場所を選ばない」と `README.md` にあるが、
スライドを作るだけの人は `User.md` しか読まない。

## やったこと

- `docs/User.md` の「公開」に「他のサーバーへ持っていくとき」を足した。
  渡すのは `player.html`・`slides/_rules.js`・公開したいデッキの
  `slides/<名前>.js` の 3 つだけ、`tools/`・`docs/`・`archives/`・
  `README.md`・`TODO.md` は要らない、ネット接続（CDN）と HTTP 配信が前提、
  の 3 点。詳しくは Developer.md の「場所を選ばない」へリンクで送り、
  写しは置かない
- `docs/Developer.md` の「場所を選ばない」の一文を直した。
  「ローカルを指すのは `slides/<名前>.js` だけ」は `slides/_rules.js` が
  抜けていて不正確だった（`player.html` は 464 行目で読んでいる）。
  検証の過程で verifier が見つけた

## 確かめたこと

verifier が実際に再現した。

- リポジトリ外の一時ディレクトリに挙げた 3 ファイルだけを同じ位置関係で
  コピーし、`python3 -m http.server` で配信。`player.html?deck=user` と
  ローカル参照の 2 ファイルがいずれも 200 で返った。`slides/readme.js` は
  404（渡していないので想定どおり）。`_rules.js` を外すと 404 になることも
  確かめ、3 つで過不足が無いことを両側から押さえた
- `player.html` 全文から `src=`・`href=`・`document.write`・`fetch`・
  `XMLHttpRequest`・`createElement` を洗い、ローカル（相対パス）を指す参照が
  `slides/_rules.js` と `slides/${deckName}.js` の 2 箇所だけであることを確認
- リンク先の `### 場所を選ばない` が `docs/Developer.md` に実在することと、
  `README.md`・`Developer.md` の既存の記述と食い違わないことを確認

報告は [archives/agents/TODO-056/verifier-report.md](../agents/TODO-056/verifier-report.md)。

## 分担の振り返り

- **verifier が見つけたもの。** `docs/User.md` に書いた内容そのものは
  すべて正しく、問題は出なかった。一方で、範囲外の `docs/Developer.md` の
  一文が `slides/_rules.js` を落としていることを見つけた。これは
  `player.html` を grep で洗った副産物で、User.md だけを読んでいたら
  出てこない。**「書いたとおりに試す」を別の担当にやらせた分の元は取れた**
- **見込みとの差。** 見込みどおり main が書いて verifier が確かめる形で
  収まった。料金も $0.8 で、文書 1 節の項目として想定の範囲
- **次に同じ規模をやるなら。** 文書だけの項目でも、
  **「書いたとおりに試せる手順」が含まれるなら verifier は分ける**。
  逆に、試せるものが無い書き換え（言い回しの調整など）まで分ける必要は無い。
  今回 main は verifier の起動後に何も叩かず待ったので、main の
  cache_read は 85 万で収まった
