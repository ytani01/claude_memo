# TODO-051 reviewer report

対象: `git diff`（CLAUDE.md・README.md・docs/Developer.md・docs/Usage.md・
player.html・tools/measure-duration.py）と、未追跡の
`slides/readme.js`・`slides/usage.js`・`slides/developer.js`。

## 要修正

1. **`slides/usage.js:104`／古い前提が残っている。**
   スライド4「手順2と3 書いて開く」の画面表示が
   「`?deck=` を省くと `slides/claude-memo.js` が読まれる」のまま。
   既定は `player.html:466` で `readme` に変わっており、`README.md:29-30`・
   `docs/Usage.md:17`・`CLAUDE.md:8` はすでに `readme` に直っている。
   `slides/readme.js` に直すべき。

2. **`slides/readme.js:198-213`（Slide 8「duration の測り方」）／
   README.md と食い違う。**
   コマンド例が `tools/measure-duration.py --all --write` のままで、
   出力例も `スライド 15: duration 17 -> 16` / `claude-memo.js: 1 枚を
   書き換えた` という旧版そのもの。TODO-051 で決めた「`slides/readme.js`
   は書き直した `README.md` と同じ内容にする」に反する。`README.md:51`
   は既に `--deck <名前> --all --write` に直っている。

3. **`slides/usage.js:262-271`（Slide 10「まとめて書き戻す」）／
   `--deck` が抜けている。**
   コマンド例が `tools/measure-duration.py --all --write` のまま。
   `docs/Usage.md` の対応する実行例は `--deck usage --all --write` に
   直っている（Usage.md 差分参照）。既定が `readme` に変わった今、この
   スライドの手順どおりに `usage` デッキのつもりで打つと、実際には
   `readme.js` が書き換わる（`tools/measure-duration.py` の
   `args.deck` の既定が `DEFAULT_DECK = 'readme'` であるため。コードを
   読んで確認、実行はしていない）。

4. **`tools/measure-duration.py:17`／docstring の変数名がそのまま出力される。**
   モジュール docstring の「既定は `slides/DEFAULT_DECK.js`。」が
   f-string ではない通常の文字列なので、変数名 `DEFAULT_DECK` が
   埋め込まれずそのまま残っている。148 行の `--deck` の `help=` は
   f-string で `readme` と正しく埋め込まれている（`--help` で実測済み）
   のと対照的。`--help` には出ないが、ソースを読む開発者には誤情報。

## 検討

5. **`slides/developer.js` の 1 枚目だけ出典行が付いている。**
   `docs/Developer.md より` という行（Slide 1 末尾）が developer.js には
   あるが、readme.js・usage.js の 1 枚目には無い。3 デッキ間の体裁を
   揃えるという観点で不揃い。

6. **1 枚目のバッジ文言の付け方が統一されていない。**
   readme.js は「yt_slide」、usage.js は「USAGE GUIDE」、developer.js は
   「DEVELOPER GUIDE」。usage/developer は `<種別> GUIDE` の型だが readme
   だけ違う型。意図的なら問題ないが、揃える方針なら直す余地がある。

7. **`README.md`「入っているスライド」表にデッキへのリンクが無い。**
   デッキ名を列挙するだけで `player.html?deck=<名前>` への直接リンクは
   無い。TODO-051 の「README.md と docs/ からリンクする」に対し、
   docs/Usage.md・docs/Developer.md は該当デッキへの誘導文を追加した
   のに対し、README.md 自体は「すぐ試す」節の一般形の説明にとどまる。

## 好みの範囲

8. `slides/readme.js` の複数箇所（Slide 1・6 見出しなど）は「HTML1枚」
   「1枚のスライド」と数字にスペースを詰めて書くが、`README.md` 本文は
   「HTML 1 枚」とスペースを入れる。表記が揺れている。

## 確認して問題無かった点（参考）

- `docs/Developer.md` の「触ると鳴らなくなるもの」3 点（Audio 要素の
  使い回し・Web Speech の分割・no-referrer）は `slides/developer.js`
  Slide 8 に漏れなく入っている
- `tools/measure-duration.py` の `--deck` は `--text` だけのときは
  デッキの存在を確認しない（`(args.slides or args.all) and not
  src.exists()` のガード）。`--text` のみの用途を壊していない
- `slides/*.js` の新しい 3 デッキとも、スライドデータの書き方を見せる
  コード例は 1 行のオブジェクトリテラルで書かれており、`duration: N,`
  の次行に `narration: '` が来る `--write` の危険な形にはなっていない
  （実測でパターンを確認）
- `player.html`・`CLAUDE.md`・`README.md`・`docs/` に、既定が
  `claude-memo` のままだと読める記述は他に残っていない
  （`grep -rn claude-memo` で確認、`archives/` 以外）
