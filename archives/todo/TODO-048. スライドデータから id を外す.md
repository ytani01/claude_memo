# TODO-048. スライドデータから `id` を外す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 31,484 | 58,195 | 84% |
| verifier ×2 | Sonnet 5 | medium | 14,045 | 71,309 | 16% |
| 合計 |  |  | 45,529 | 129,504 | 概算 $3.3 |

- **この数字は TODO-049 と合わせたもの。** 2 件まとめて着手したので、
  集計の範囲（TODO-048 を立てたコミットから）に TODO-049 の作業も入っている。
  TODO-049 側には表を置いていない
- verifier は TODO-048 用と TODO-049 用の 2 つを並列で動かした。集計は
  担当名でまとまるので、2 つ分の合算になっている
- main のモデルは切り替えずに Opus 5 のまま着手した。見込みの Sonnet 5 との
  差は、切り替えの手間のほうが大きいと判断したため

## きっかけ

スライド番号は `slideData` の並び順で決まるのに、データにも `id` として
持っていた。二重に持っているので、スライドを差し替えたり間に足したりすると
（TODO-025 で実際に並びを変えた）`id` を振り直す手間が出て、ずれも起きうる。

利用者からの「配列の順番で番号が分かるので、データには `id` は不要では」
という指摘で立てた。

## やったこと

`id` を読んでいたのは `player.html` の 3 箇所だけで、どれも表示用だった。

- `player.html` … `String(slide.id).padStart(2, '0')` を `currentIndex + 1`
  から出すように、`${slide.id}. ${slide.title}` も同様に変えた。プレイリストの
  番号（`slideData.forEach((slide, idx) => ...)` の中）は既に `idx` があったので
  `idx + 1` にした
- `slides/claude-memo.js` … `id:` の 17 行を削除
- `docs/Usage.md` … 記述例 2 箇所とキーの表から `id` を外した。「スライドの
  枚数はどこにも書かない」の段落を「番号も枚数もどこにも書かない」に直した
- `docs/Developer.md` … `slideData` の 1 要素の説明から `id` を外した

`tools/measure-duration.py` は `id` を見ていないので触っていない。

## 確かめたこと

verifier に確認させた（報告は
[archives/agents/TODO-048/](../agents/TODO-048/verifier-report.md)）。

- `slide.id` の参照と `id:` の行が残っていないこと
- 差し替えた 3 箇所が元と同じ番号を出すこと。`currentIndex` と `idx` が
  その時点で正しい値になっていることをコードを追って確認
- `slides/claude-memo.js` が構文として壊れていないこと（`node --check`）と、
  `narration` が 17 件そのまま取れること
- 文書に `id` の説明が残っていないこと

## 振り返り

**分担**: 実装は main、確認は verifier（Sonnet 5 / medium）に分けた。
verifier は指示した確認をすべて通し、加えて「TODO-049 の差分が同じ作業ツリーに
混ざっているのでコミットの分け方を決める必要がある」と報告してきた。
これは想定どおりの働きで、判断そのものは管理者に返している。

**見込みとの差**: 担当の見立ては合っていた。main のモデルだけが見込み
（Sonnet 5 / medium）と違い、Opus 5 / high のまま進めた。やったことは
3 箇所の置き換えと 17 行の削除で、判断が要ったのは `docs/Usage.md` の
段落をどう書き直すかだけだったので、**Sonnet 5 / medium で足りた**。

**次に同じ規模なら**: 実装は main、確認は verifier の 1 人で変えなくてよい。
ただし main のモデルは見込みどおりに落としてから着手する。この項目の料金は
main が 84% を占めており、下げる余地はそこにしかない。
