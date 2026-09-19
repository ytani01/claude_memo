# TODO-044. `public_html/` 以外へ移しても動くことを `docs/Developer.md` に書く

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 1,974 | 5,539 | 60% |
| verifier | Sonnet 5 | medium | 5,071 | 20,597 | 40% |
| 合計 |  |  | 7,045 | 26,136 | 概算 $0.5 |

- verifier は定義（`~/.claude/agents/verifier.md`）のまま（sonnet /
  `effort: medium`）

## きっかけ

「`~/public_html` 以外へ移しても動くか」と聞かれた。調べると、`player.html`
がローカルを指しているのは `slides-<名前>.js` の 1 か所だけで、しかも相対
パス。残りは全部 CDN の https なので、どこに置いても動く。**そのことが
どこにも書いていなかった。**

## やったこと

`docs/Developer.md` の「リポジトリの構成」の下に「置き場所は選ばない」の節を
足した。

- `player.html` と `slides-*.js` を同じディレクトリに置けば `public_html/` の
  外でも動くこと
- 手元で試す手順（`python3 -m http.server 8000`）
- **`file://` で直接開くのは試していない**こと（`document.write` で足した
  相対の `<script>` と外部への音声要求がブラウザの制限に当たる可能性がある）
- ネット接続が要ること
- 公開 URL を変えたくないなら元の場所にリダイレクトかシンボリックリンクを
  残すこと

## 確かめたこと

verifier（Sonnet 5 / effort medium）に再現と照合を任せた。報告は
`archives/agents/TODO-044/verifier-report.md`。

- 別ディレクトリへ `player.html` と `slides-claude-memo.js` だけをコピーし、
  `python3 -m http.server` で両方 200 で取れることを再現
- **ローカルのファイルを指す参照は `player.html:467` の
  `slides-${deckName}.js` の 1 か所だけ**であることを、`src=`・`href=`・
  `url()`・`fetch()` などを洗い出して確認。残りは https が 6 件
  （Tailwind、Google Fonts 2、FontAwesome、翻訳 TTS）
- `claude_memo.html` のリダイレクト先も相対
- 食い違いは無し

`file://` はブラウザが無いので検証していない（文書にもそう書いてある）。

## 分担の振り返り

- verifier は食い違いを 1 件も見つけなかった。ただし**「ローカル参照が
  1 か所だけ」という主張の洗い出し**は、文書の正しさがそこ 1 点に懸かって
  いたので、別の目で数えさせる価値があった。見落としがあれば文書の主張が
  丸ごと崩れる種類の記述
- 見込みとの食い違いは無し
- 次に**数行の追記**をやるなら、今回と同じで verifier 1 人でよい。ただし
  main の消費が少ない（$0.3）ぶん verifier の割合が 40% に上がる。
  この規模では確認担当のほうが高くつくが、主張の裏取りが要る記述なので
  省かない。裏取りの要らない書式だけの追記なら main だけでよい
