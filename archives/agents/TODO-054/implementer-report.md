# TODO-054 implementer 報告

## 変更したファイル

- `slides/_rules.js`（新規） — 共通の読みの置換表 `SPEECH_RULES`。20 個、
  `player.html` にあった順のまま。
- `slides/readme.js:4-14` — `deckConfig.rules` を追加（claude-memo / yt_slide /
  JavaScript / \bURL\b / \breadme\b / \bdeveloper\b の 6 個）。
- `slides/user.js:5-12` — `deckConfig.rules` を追加（\.js\b / \bwrite\b の 2 個）。
- `slides/developer.js:5-21` — `deckConfig.rules` を追加（archives/todo 〜
  \btools\b の 12 個）。
- `slides/claude-memo.js:4-25` — `deckConfig.rules` を追加（TODO\.md 〜
  \bimplementer\b の 18 個）。
- `player.html:462-471` — `<script src="slides/_rules.js"></script>` を
  デッキ読み込みの `document.write` の前に追加。
- `player.html:600-607`（旧 601-662） — `prepareSpeechText()` の 58 個の
  `.replace()` の連なりを、`(deckConfig.rules || []).concat(SPEECH_RULES)` を
  `reduce` で回す形に置き換え。
- `tools/measure-duration.py` — 冒頭の docstring、`RULES` の写しを削除し、
  `load_rules()` / `load_deck_rules()` / `load_common_rules()` を新設。
  `[/pattern/flags, 'replacement']` の行から `\/`→`/`、`$1`→`\1`、`i`→`re.I`
  へ変換する。`prepare()` と `measure()` に `deck` 引数を足し、デッキ側を先、
  共通を後に当てる。`main()` の呼び出しへ `args.deck` を渡すよう変更。
- `tools/test_measure_duration.py` — 「`player.html` と `RULES` がそろって
  いるか」の検査を削除。代わりに `load_rules()` を小さな JS 文字列で検査し、
  4 デッキすべてで `load_deck_rules()` が読めること、`load_common_rules()` が
  20 個になることを確認。`apply_durations()` の既存の検査はそのまま。

## 検証

- `python3 tools/test_measure_duration.py` → `OK`（終了コード 0）
- 読みの結果の突き合わせ（Node で `player.html` の旧
  `prepareSpeechText()` と、新しい `slides/_rules.js` +
  `deckConfig.rules` を実際に `vm` で読み込んで動かしたもの、双方を比較）:
  4 デッキ・49 個のナレーション全てで一字一句一致（`ALL MATCH`）。
- 同じ 49 個について、Python 側の `prepare()` の出力と JS 側の出力も突き合わせ、
  完全一致を確認（`PY/JS ALL MATCH`）。
- `tools/measure-duration.py --text 'TODO を確認' --deck readme` を実際に実行し、
  ネットワーク越しに動くことも確認（この実行自体は完了条件には含まれない）。

## 判断が要る点・気づいたこと

特になし。範囲外の直したい点も見つからなかった。

## 追記: レビュー指摘 5 点への対応

reviewer の報告（`archives/agents/TODO-054/reviewer-report.md`）を受け、
管理者から指示のあった 5 点を直した。

1. `tools/measure-duration.py:42-56` — `JS_RULE_RE` がコメントアウト行
   （行頭の空白の後が `//`）を拾ってしまう件。`load_rules()` の先頭で、
   `strip()` して `//` で始まる行を除いてから正規表現を掛けるように変更。
2. `tools/measure-duration.py:44` — 置換文に `'` が入ると途中で切れる件。
   `JS_RULE_RE` の置換文の部分を `'((?:\\.|[^'\\])*)'` に変え、`\'` を含む
   文字列も 1 つの引用符として読めるようにした。読み取った後
   `load_rules()` で `\'` → `'` に戻す。
3. `slides/_rules.js:6-12` — `TODO\.md` / `TODO-([0-9]+)` / `CLAUDE\.md` /
   `Claude Code` の 4 つを `slides/claude-memo.js` から共通表へ移動。
   指示どおりの並び（`TODO\.md` → `TODO-([0-9]+)` → `TODO` → `CLAUDE\.md` →
   `Claude Code` → `Claude` → `考え方` → 以降今のまま）にした。共通は
   20 → 24 語。`slides/claude-memo.js:8-22` から該当 4 行を削除し、
   18 → 14 語になった。
4. `tools/measure-duration.py:59-65` — テストで「rules: を持たないデッキ」を
   検査できるよう、`load_deck_rules()` からファイルを読まない部分を
   `deck_rules_from_text()` として切り出した（ファイル読み込みの
   `load_deck_rules()` はこれを呼ぶだけに変更）。
   `tools/test_measure_duration.py` に、コメントアウト行が読み飛ばされる
   こと、置換文に `\'` を含むルールが正しく取れること、
   `deck_rules_from_text()` に `rules:` の無いテキストを渡すと空になる
   ことの 3 つを追加。`common_rules` の個数の検査も 20 → 24 に更新。
5. `tools/measure-duration.py:14-17`（docstring） — `--text` は測りたい
   デッキと `--deck` を揃えないと違う秒数が出る旨を 1 行足した。

### 検証（追記分）

- `python3 tools/test_measure_duration.py` → `OK`（終了コード 0）。
- 読みの結果の突き合わせをやり直した。Node で 97d62e5（= 現在の HEAD）の
  `player.html` の旧 `prepareSpeechText()` と、直した後の
  `slides/_rules.js` + `deckConfig.rules` を `vm` で実際に読み込んで動かした
  ものを比較 → 4 デッキ・49 個のナレーション全てで一字一句一致
  （`ALL MATCH`）。
- 同じ 49 個について、Python 側の新しい `prepare()` の出力と JS 側の出力も
  突き合わせ、完全一致を確認（`PY/JS ALL MATCH`）。
- 範囲外（`docs/`、`TODO.md`、他の指摘 2・3 の残り）には手を付けていない。
