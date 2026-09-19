# TODO-051. `README.md` と `docs/` の内容をスライドにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer × 3 + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer × 3 + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 32,367 | 69,869 | 61% |
| implementer × 3 | Sonnet 5 | medium | 44,090 | 187,057 | 18% |
| reviewer | Sonnet 5 | high | 15,944 | 93,102 | 11% |
| verifier | Sonnet 5 | medium | 10,867 | 67,464 | 10% |
| 合計 |  |  | 103,268 | 417,492 | 概算 $6.6 |

- implementer は定義（`.claude/agents/implementer.md`）が sonnet。上書きせず
  そのまま使った。集計は 3 人分をまとめた 1 行（個別には割れない）
- verifier と reviewer も定義のまま

## きっかけ

`player.html` の使い方と作りは `docs/` の文章でしか読めなかった。
このリポジトリ自身がプレゼンプレイヤーなので、同じ内容をスライドでも
見られるようにする。**リポジトリの紹介そのものをスライドで見せられるのが、
このプレイヤーの一番分かりやすい実例になる。**

## 決めたこと

- **デッキは 3 つ。** `slides/readme.js`、`slides/usage.js`、
  `slides/developer.js`。読み手が違うので、ドキュメントの分かれ方に揃える
- **`README.md` の本体も書き直す。** アピールする相手は**プレゼンを作りたい
  人**で、道具としての魅力を前に出す
- **要点だけを載せる**（各 8〜12 枚）
- **`?deck=` が無いときは `readme` を出す。** `claude-memo` は数あるデッキの
  1 つという扱いにして、既定から外す

## やったこと

**1. `tools/measure-duration.py` に `--deck <名前>` を足した。**
それまで `slides/claude-memo.js` 固定だった読み込みと書き戻しが、
どのデッキでもできるようになった（既定は `readme`）。

**2. `README.md` を書き直した。** 「HTML 1 枚で、ナレーション付きのプレゼンが
動き出す」を冒頭に置き、できること・すぐ試す・自分のスライドを作る・
入っているスライドの順にした。ファイル構成の表は後ろへ下げた。

**3. 3 デッキを作った**（implementer 3 人が並列）。

| デッキ | 枚数 | 素材 |
|--------|------|------|
| `readme` | 10 | 書き直した `README.md` |
| `usage` | 11 | `docs/Usage.md` |
| `developer` | 11 | `docs/Developer.md` |

**4. `duration` を実測して入れた。** implementer には仮の値を入れさせ、
main が `--deck <名前> --all --write` で 3 デッキ分を測り直した
（readme 6 枚、usage 11 枚、developer 8 枚が仮の値から動いた）。

**5. 既定のデッキを `readme` にした**（`player.html` の 1 か所）。
`CLAUDE.md`・`README.md`・`docs/` の「既定は `claude-memo`」も直し、
`docs/Usage.md` と `docs/Developer.md` の冒頭にスライド版への案内を足した。

## 確かめたこと

verifier が確認した（報告は `archives/agents/TODO-051/verifier-report.md`）。

- **3 デッキとも再生できる。** `?deck=` 無しで readme が出る。
  `usage`・`developer`・`claude-memo` もそれぞれ出る。コンソールにエラー無し
- `node --check` が 3 ファイルとも通る
- **`duration` が全枚とも実測と一致**（3 デッキ 32 枚）
- 見た目を PC 幅で 6 枚撮り、枠からのはみ出しも重なりも無し
  （`~/tmp/playwright-mcp/TODO-051-*.png`）

reviewer が差分を見た（報告は `archives/agents/TODO-051/reviewer-report.md`）。
要修正 4 件はすべて直した。

- **スライドの中に古い前提が残っていた。**「`?deck=` を省くと
  `claude-memo.js` が読まれる」、`--deck` の付かない `--write` の例が 2 か所。
  **元にした文書は直したのに、そこから起こしたスライドが追随していなかった**
- `measure-duration.py` の docstring に、変数名 `DEFAULT_DECK` がそのまま
  出ていた（f-string ではなかった）
- verifier も `CLAUDE.md` の「『Claude Code の使い方』を紹介するページ」が
  デッキ 1 本だった頃のままだと見つけた。直した
- 「触ると鳴らなくなるもの」3 点が `developer` デッキに漏れなく入っていること、
  3 デッキとも `--write` の正規表現に引っかかる書き方をしていないことは、
  問題無しと確認された

## 残ること

- **ナレーションの英単語の読みが崩れる。** 置換表に無い語が多い
  （`player.html` 12 回、`duration` 8 回など）。**TODO-052 として立てた**
- reviewer の「検討」3 件は見送った。1 枚目のバッジ文言の型が揃っていない
  こと、`developer` の 1 枚目だけ出典行があること、`README.md` の表に
  デッキへのリンクが無いこと。**どれも読む妨げにならない**ので、
  次にスライドを触るときについでに直せばよい

## 分担の振り返り

- **implementer 3 人の並列は効いた。** 3 デッキで料金の 18% に収まった。
  素材（`README.md` と `docs/` の 2 つ）が初めから分かれていて、
  依頼文の共通部分をそのまま流用できたのが大きい
- **implementer は「元の文書の最新版」を見ていたのに、スライドに古い前提を
  書いた。** 3 件とも `claude-memo` が既定だった頃の話。依頼文に
  「既定は `readme` に変わる」と書かなかったのが原因。**作業の途中で変わる
  前提は、依頼文に明記する**（今回は main が既定を変えるのが implementer の
  作業と同時だった）
- **reviewer がその 3 件を全部拾った。** verifier は「動くか」を見たので、
  スライドに書いてある文字と元の文書の食い違いは拾えていない。
  **文書から起こす作業では、レビューの担当が要る**
- **見込み（implementer × 3 + verifier + reviewer）と食い違わなかった。**
- **次に同じ規模（文書からデッキを起こす）をやるなら、同じ組み方でよい。**
  そのうえで**「元の文書のどこが今まさに変わっているか」を依頼文に書く**。
  今回の要修正 4 件のうち 3 件はそれで防げた
