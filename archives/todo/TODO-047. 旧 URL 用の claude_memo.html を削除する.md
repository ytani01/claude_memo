# TODO-047. 旧 URL 用の `claude_memo.html` を削除する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main のみ |
| 実施 | Opus 5 / effort high | main のみ |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 1,363 | 3,611 | 100% |
| 合計 |  |  | 1,363 | 3,611 | 概算 $0.3 |

- **この数字は実際より小さい。** 削除そのものは TODO-046 のコミットより前に
  やっていたので、集計の範囲（`--since` で TODO-046 のコミット時刻から）には
  決着の作業しか入っていない。実作業の分は TODO-046 の集計に混じっている
- モデルと effort は過剰だった（下記）

## きっかけ

TODO-041 で `claude_memo.html` を `player.html` と `slides-claude-memo.js` に
分けたとき、`claude_memo.html` は `player.html?deck=claude-memo` へ飛ばす
だけの 3 行の HTML として残した。TODO-046 でスライドのデータを `slides/` へ
移すのに合わせて、これも消すことにした。旧 URL のリンクは切れる。

## やったこと

- `git rm claude_memo.html`
- 参照を 5 か所消した。**チェックリストには `README.md` しか書いていなかったが、
  実際には `CLAUDE.md`・`docs/Usage.md`・`docs/Developer.md` にもあった**
  - `README.md` … ファイル構成の表の 1 行
  - `CLAUDE.md` … 「構成」の段落（折り返しもやり直した）
  - `docs/Developer.md` … リポジトリの構成の表の 1 行と、「置き場所は
    選ばない」の「（`claude_memo.html` のリダイレクトも相対）」
  - `docs/Usage.md` … 「公開」の節の「これを真似た 3 行の HTML を置けばよい」
    の段落。手本のファイルが無くなるので、段落ごと削った

## 確かめたこと

- `README.md`・`CLAUDE.md`・`docs/` に `claude_memo.html` への参照が
  残っていないこと（`grep`）
- `README.md`・`TODO.md`・`CLAUDE.md`・`docs/Usage.md`・`docs/Developer.md` の
  相対リンクがすべて実在するファイルを指すこと（リンク切れ 0）
- `archives/` には旧ファイル名への言及が多く残るが、現行仕様ではないので
  触っていない

## 残ること

旧 URL（`claude_memo.html`）を開くと 404 になる。公開先に古いリンクが
残っていて困るようなら、サーバー側でリダイレクトを設定する。

## 振り返り

サブエージェントは立てなかった。文書の削除だけで、確かめる中身が
「参照が残っていないか」と「リンクが切れていないか」しか無く、どちらも
`grep` とスクリプトで機械的に確かめられたため。この判断は妥当だった。

ただし **main のモデルと effort は過剰**だった。やったのは 1 ファイルの
削除と 5 か所の参照の除去で、判断が要ったのは `docs/Usage.md` の
「短い URL を付けたいときは、これを真似た 3 行の HTML を置けばよい」を
どうするか（手本が消えるので段落ごと削る）の 1 点だけ。次に同じ規模なら
effort medium で足りる。

この項目の途中で、**モデルと effort は「多分大丈夫」の水準まで低めに設定し、
問題が出てから上げる**方針が決まった。以後はそれに従う。
