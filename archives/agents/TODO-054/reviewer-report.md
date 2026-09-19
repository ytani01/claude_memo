# TODO-054 レビュー報告（reviewer）

対象: `git diff`（97d62e5 以降、未コミット）の
`player.html` / `slides/_rules.js`（新設） / `slides/{readme,user,developer,claude-memo}.js` /
`tools/measure-duration.py` / `tools/test_measure_duration.py`。

「今と同じ読みになるか」は verifier の担当。ここでは設計の良し悪しのみを見た。

## 要修正

### 1. `tools/measure-duration.py:39` の `JS_RULE_RE` がコメントアウト行を拾ってしまう

`JS_RULE_RE = re.compile(r"\[/(.+?)/([gi]*), '(.*?)'\]")` は `//` の有無を
見ていない。実測すると、コメントアウトした行もそのままルールとして拾われる。

```python
>>> JS_RULE_RE.findall("    // [/foo/gi, 'コメントアウト'],\n")
[('foo', 'gi', 'コメントアウト')]
```

JS 側では `//` の行はもちろん無効（コメント）だが、Python 側は有効なルールとして
`prepare()` に混ぜてしまう。**ルールを一時的に無効化したいとき、`//` を付けて
コメントアウトする」という自然な操作をすると、JS と Python の挙動が食い違う。**
落ちるのではなく、静かに違う秒数を出す（依頼文が名指しした「コメントアウトされた
行」の罠がそのまま実在する）。現状のファイル群に既存のコメントアウト行は無いので
今の 4 デッキでは症状が出ないが、パーサ自体の欠陥であり、将来誰かがルールを
一時的に外そうとした瞬間に踏む。

## 検討

### 2. TODO.md・TODO-NNN・CLAUDE.md・Claude Code の読みが `claude-memo` デッキ専用になっている

`_rules.js`（共通）にあるのは素の `TODO` と `Claude` の 2 語だけで、
`TODO\.md` / `TODO-([0-9]+)` / `CLAUDE\.md` / `Claude Code` は
`slides/claude-memo.js` の `rules:` にしかない（README の指示どおりの配置で、
implementer の落ち度ではない）。

以前は `prepareSpeechText()` が全デッキ共通の 1 本のチェーンだったので、
どのデッキのナレーションに `TODO.md` や `CLAUDE.md` が出てきても正しく読めた。
今回の分割後は、**「今その語を使っているデッキ」にしかルールが無い**ため、
例えば `developer.js` に今後「CLAUDE.md を読んでから直す」のようなナレーションを
足すと、`CLAUDE\.md` 用の専用ルールが無いデッキなので、共通の素の `Claude` だけが
当たり、`.md` の部分は素通りして変な読みになる（`\.md` 用の共通ルールも無い）。
実測はしていないが、今の各デッキの narration に該当語が無いことは grep で確認済みで、
現状の回帰は無い。

TODO.md・CLAUDE.md はこのリポジトリ全体で頻出する語（`CLAUDE.md` 自体が
このプロジェクトの規約ファイル）なので、他のデッキが将来これらの語を使う可能性は
低くない。**「今どのデッキに書かれているか」ではなく「複数デッキで使われ得る語か」で
共通/デッキ振り分けを決めた方が、将来語を足したときの罠が減る**（少なくとも
`TODO\.md` / `TODO-([0-9]+)` / `CLAUDE\.md` は共通行きの候補）。今回は「表を
外に出すだけ」が目的なので、振り分けの直しは別項目でよいと思う。

### 3. `tools/measure-duration.py` の `--text` が `--deck` の指定を忘れると違う結果になる

`main()` の `--text` ジョブは `measure(text, args.deck)` を呼ぶが、
`args.deck` は指定しなければ `DEFAULT_DECK`（`readme`）になる
（`tools/measure-duration.py:38`,`174`）。改修前は `measure(text)` が
デッキに関係ない単一のグローバル置換表を使っていたので `--deck` は無関係だった。
改修後は、`claude-memo` デッキ向けの下書きを `--text` で測るときに
`--deck claude-memo` を付け忘れると、`readme` デッキの語彙表で測ってしまい、
実際に読ませたときと違う秒数が出る（静かに間違う）。`README.md`（依頼文）にも
明記が無く、テストも `--text` 経路を確認していない。

### 4. 新しいテストが「非空であること」しか見ていない

`tools/test_measure_duration.py` の新しい検査は
`assert deck_rules, f'{deck}: ...'`（空でないか）と
`assert len(common_rules) == 20`（個数だけ）しか見ていない。
`load_rules()` 自体のテスト（`JS_SAMPLE`）も、素の `TODO`・`\/`・`$1`・
無フラグの 4 パターンしか含まず、コメント行・置換文中の `'`・`u` などの
未対応フラグは検査していない。

つまり、次のような壊れ方はどれもテストを通り抜ける。

- あるデッキの `rules:` の一部だけが原因不明で読み落とされる（要素数が減っても
  1 件以上残っていれば `assert deck_rules` は通る）
- `_rules.js` の共通表の中身が入れ替わる・誤字がある（個数が 20 のままなら通る）
- 上の「要修正 1」のコメント行拾いのような、パーサの誤検出

「壊れたら落ちる」ではなく「今は空でも 20 個でもない、という極端な壊れ方だけ
落ちる」テストになっている。少なくとも `load_rules()` 側にコメント行・
クォート入り置換文のケースを 1 つずつ足すことと、`load_deck_rules`/
`load_common_rules` の結果を実際の中身（既知のパターン・置換文のリスト）と
突き合わせる検査を検討してよい。

### 5. `deckConfig.rules` が無いデッキの経路が未検証

JS 側 (`deckConfig.rules || []`) も Python 側
(`re.search(...) ` が `None` なら `[]`) も、`rules:` が無いデッキで動くように
書かれている（実測: `rules:` を含まないダミーの `deckConfig` テキストを渡すと
`None` が返り、`load_deck_rules` は空配列を返すことを確認した）。ただし今の
4 デッキは全部 `rules:` を持つため、この経路はテストで一度も通っていない。
依頼文の完了条件にも無い。壊しても気づけない状態なので、気にするなら
`rules:` を持たないダミー文字列を `load_deck_rules` 相当の関数に渡すテストを
足すとよい。

## 良かった点（参考）

- 当たる順番（デッキ側 → 共通）は JS・Python とも一貫しており、README が挙げた
  `public_html`/`HTML`、`Claude Code`/`Claude`、`TODO.md`/`TODO` の組は、
  いずれも先に当たる語が別のデッキ配列 or 同じ配列内の早い行にあるため壊れて
  いない（実際に規則の並びを 1 行ずつ突き合わせて確認した）。
- 共通表・各デッキの `rules:` の並び順は、依頼文が指定した並びと完全に一致
  している（grep で突き合わせ済み）。
- `<script src="slides/_rules.js">` を `document.write` より前に置く配置、
  `fetch` を避けて `file://` 対応を保つ判断は指示どおりで問題ない。
- 実装の範囲は `README.md` が implementer に許した範囲ぴったりで、
  `docs/`・`TODO.md` への手出しは無い（範囲外の変更なし）。
- `python3 tools/test_measure_duration.py` は現状 `OK` で通る（実行して確認済み）。
