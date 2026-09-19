# TODO-054 verifier 報告

## 1. 検証コマンド

```
python3 tools/test_measure_duration.py
```
→ `OK`、終了コード 0。

## 2. 読みの結果が変更前と一字一句同じか（独立に確認）

implementer の突き合わせとは別に、自分でスクリプトを組んで確かめた
（`/tmp/.../scratchpad/verify_narration.js`、`py_extract.py`、
`py_js_compare.js`）。

- **旧 JS vs 新 JS**: `git show 97d62e5:player.html` から `prepareSpeechText()`
  の関数本体を正規表現で機械抽出し（手で書き写さない）、Node の `vm` で
  実行。新側も現在の `player.html` の `prepareSpeechText()` 本体をそのまま
  抽出し、`slides/_rules.js` と各デッキの `deckConfig.rules` を読み込んで
  実行。4 デッキ・**49 個**のナレーション全てで入力（旧デッキファイルの
  `narration` 文字列）が変わっていないことを確認したうえで、出力が
  **全て一致**（`ALL MATCH`）。
- **新 JS vs 新 Python**: `tools/measure-duration.py` の `prepare()` を
  4 デッキ・49 個のナレーションに対して実行し、上記の新 JS の出力と
  比較。**全て一致**（`compared 49, mismatches 0`）。
- **突き合わせの自己点検**: 検証スクリプトが実際に差分を検出できることを
  確かめるため、`slides/_rules.js` の置換文字列を 1 つだけ意図的に壊した
  コピーで再実行し、`DIFF DETECTED` になることを確認した
  （壊していない元のファイルは変更していない）。これで「常に一致と出る
  壊れた検証」ではないことを確かめた。

以上より、読みの結果は変更前と一字一句同じと判断してよい。

## 3. 振り分け（数・並び順）

- `slides/_rules.js`（共通 20 語）: 依頼書の並び順（TODO / Claude / 考え方 /
  使い方 / measure-duration.py / player.html / User.md / slideData / slides /
  deckConfig / deck / duration / clamp / cqw / px / rem / Tailwind / HTML /
  Python / user）とファイルの中身を目視で突き合わせ、**完全一致**。
- 各デッキの `deckConfig.rules`:
  - `slides/readme.js`: claude-memo / yt_slide / JavaScript / \bURL\b /
    \breadme\b / \bdeveloper\b（6 個、順序一致）
  - `slides/user.js`: \.js\b / \bwrite\b（2 個、順序一致）
  - `slides/developer.js`: archives/todo 〜 \btools\b（12 個、順序一致）
  - `slides/claude-memo.js`: TODO\.md 〜 \bimplementer\b（18 個、順序一致）
  - 合計 20 + 6 + 2 + 12 + 18 = **58**。旧 `prepareSpeechText()` の
    `.replace()` の連なりも 58 個で、個数が一致する。
  - `tools/test_measure_duration.py` も `common_rules` が 20 個であることを
    アサートしている（`OK` で通過済み）。

## 4. `tools/measure-duration.py` に写しが残っていないか

- `RULES` の写しは無い。`load_rules()` / `load_deck_rules()` /
  `load_common_rules()` が `slides/_rules.js` とデッキファイルを都度読む
  実装になっている。
- 冒頭 docstring は「読みの置換表は `slides/_rules.js`（共通）と
  `slides/<デッキ名>.js` の `deckConfig.rules`（デッキだけの語）から読む」
  「表そのものはここには持たない」と、今の作りに合った説明になっている。
- コード中に残る「player.html の写し」というコメントは `TTS_MAX_CHARS` と
  `BASE_SPEED_MULTIPLIER` の 2 定数だけを指しており、置換表とは無関係。
  この 2 つは今回の依頼の範囲外（読みの置換表の話ではない）で、
  実際に写しとして残っている。指摘のみで、直すかは管理者判断。

## 5. `player.html` の読み込み方

`slides/_rules.js` を `<script src="slides/_rules.js"></script>` で読んでおり、
`fetch` は使っていない。デッキを読む `document.write` より前に置かれている
（`player.html:462` あたり）。`file://` で開ける形のまま。

## 6. ネットワーク

`curl` や `ffprobe` を伴う `--text` 実行、`--write` は行っていない。
`python3 tools/test_measure_duration.py` と、Node/Python でのローカルな
文字列比較だけを行った。

## 変更ファイルの一覧と範囲の確認

```
 player.html                    |  71 +++++----------------------
 slides/claude-memo.js          |  21 ++++++++
 slides/developer.js            |  15 ++++++
 slides/readme.js               |   9 ++++
 slides/user.js                 |   5 ++
 tools/measure-duration.py      | 108 +++++++++++++++--------------------------
 tools/test_measure_duration.py |  39 +++++++++------
 (新規) slides/_rules.js
```

依頼書の分担（implementer: `slides/_rules.js` の新設、`player.html`、
4 デッキ、`tools/measure-duration.py`、`tools/test_measure_duration.py`）と
一致。`docs/`、`TODO.md`、コミットには手を付けていない（範囲外、main の担当）。

## 確かめられなかったこと・判断が要ること

- **置換の当たる順番（デッキ側が先か、共通表の並びが崩れていないか）の
  パーサとしての壊れやすさ**は、この報告の対象外（reviewer の担当）。
  今回は「結果が変わっていないこと」だけを確かめた。
- `tools/measure-duration.py` の docstring 中の「player.html の写し」という
  表記が `TTS_MAX_CHARS` / `BASE_SPEED_MULTIPLIER` の 2 定数を指している点は
  今回の依頼（読みの置換表の外出し）の範囲外なので、直すべきかどうかは
  判断していない。管理者の判断を仰ぎたい。

---

## 再確認（reviewer 指摘 5 点の対応後）

対象: implementer が reviewer 報告の 5 点を直した後の状態
（`archives/agents/TODO-054/implementer-report.md` の追記分）。

### 1. 4 デッキの読みが 97d62e5 と一字一句同じか（独立確認）

前回と同じ手口（`verify_narration.js`）を、今の `slides/_rules.js` /
各デッキの `deckConfig.rules` に対して再実行した。

```
Compared 49 narrations across 4 decks.
ALL MATCH
```

`slides/_rules.js` を確認したところ、`TODO\.md` / `TODO-([0-9]+)` / `TODO` /
`CLAUDE\.md` / `Claude Code` / `Claude` の順で共通表の先頭に並んでおり、
**共通 24 語**になっている。`slides/claude-memo.js` からはこの 4 行が
消えて **14 語**になっている（`python3` で `load_common_rules()` /
`load_deck_rules('claude-memo')` の長さを実測し、24 / 14 を確認）。

claude-memo デッキの narration に `TODO.md` や `CLAUDE.md` 等の語を含む
ものがあるかを grep で確かめたところ複数あり（例: `TODO.md`、
`TODO-054` のような TODO-番号、`CLAUDE.md`）、それらを含む narration も
`ALL MATCH` に含まれている。つまり、当たる語が実際に使われている
narration でも読みが変わっていないことを確認した。

Python 側（`prepare()`）との突き合わせも再実行し、4 デッキ・49 個全てで
JS と Python の出力が一致することを確認した（`compared 49, mismatches 0`）。

### 2. `python3 tools/test_measure_duration.py`

`OK`、終了コード 0。

### 3. 足したテストが、実際に壊れたときに落ちるか（3 ケース）

`tools/measure-duration.py` をバックアップ（`/tmp/.../scratchpad/
measure-duration.py.bak`）してから、1 ケースずつわざと壊して
`python3 tools/test_measure_duration.py` を実行し、そのたびにバックアップへ
戻した（最終状態は `git status`／`git diff --stat` で元と同じであることを
確認済み）。

- **ケース 1（コメントアウト行の読み飛ばし）**: `load_rules()` の
  「`//` で始まる行を除く」処理を削除して実行 →
  `AssertionError`（`COMMENTED_SAMPLE` の期待値と食い違う）で**落ちた**。
  テストは意図どおり効いている。
- **ケース 2（`rules:` の無いデッキ）**: `deck_rules_from_text()` の
  `if m else []` を外し、`m` が `None` のとき `.group(1)` を呼ぶように壊して
  実行 → `AttributeError: 'NoneType' object has no attribute 'group'` で
  **落ちた**。テストは意図どおり効いている。
- **ケース 3（`\'` を含む置換文）**: **落ちなかった。** `JS_RULE_RE` を
  直す前の `r"\[/(.+?)/([gi]*), '(.*?)'\]"`（`\'` を特別扱いしない版）に
  戻して実行しても、`python3 tools/test_measure_duration.py` は `OK` の
  まま通った。

  原因を調べた。`load_rules()` には正規表現の修正とは別に
  `replacement.replace(r"\'", "'")` という後処理があり、`QUOTE_SAMPLE`
  （`'イッツ\'です'`、`\'` が 1 箇所だけ）では、非貪欲な `(.*?)'\]` が
  「次に `']` という並びが現れる位置」を探す性質のおかげで、たまたま
  正しい終端（末尾の本当の閉じクォート）まで一致してしまい、修正前の
  正規表現でも結果が変わらない。

  実際に壊れる例で確認した。置換文の中に `\']` という並び
  （エスケープされた引用符の直後に `]`）が来ると、修正前の正規表現は
  そこで誤って打ち切る。

  ```
  sample: [/foo/gi, 'abc\']def'],
  修正前: [('foo', 'abc\\', re.IGNORECASE)]   # 'def' 以降を取りこぼす
  修正後: [('foo', "abc']def", re.IGNORECASE)]  # 正しく全体を取れる
  ```

  つまり **修正 2 自体は正しく効いている**（上のケースで実際に違いが出る）
  が、**`tools/test_measure_duration.py` の `QUOTE_SAMPLE` はこの修正の
  有無を区別できていない**。「通るだけのテスト」になっている 1 件が
  見つかった。

### 4. コメントアウト行の読み飛ばし（直接確認）

```python
sample = "const X = [\n    // [/foo/gi, 'コメントアウト'],\n    [/TODO/gi, 'トゥードゥー'],\n];\n"
md.load_rules(sample)
# => [('TODO', 'トゥードゥー', re.IGNORECASE)]
```

コメントアウト行の `foo` ルールは拾われず、有効な行だけが読まれることを
確認した。

### 変更ファイルの確認（再確認時点）

```
 player.html                    |  71 ++++--------------------
 slides/claude-memo.js          |  17 ++++++
 slides/developer.js            |  15 +++++
 slides/readme.js               |   9 +++
 slides/user.js                 |   5 ++
 tools/measure-duration.py      | 121 +++++++++++++++++------------------------
 tools/test_measure_duration.py |  68 ++++++++++++++++++-----
 (新規) slides/_rules.js
```

範囲外のファイルへの手出しはない。ミューテーションテスト後の
`tools/measure-duration.py` は元の内容と一致していることを確認済み
（バックアップと突き合わせ、`test_measure_duration.py` が `OK` を出すことでも
裏付け）。

### まとめ・判断が要る点

- 4 デッキの読みは 97d62e5 時点と一字一句同じ（claude-memo デッキを含む）。
  共通 24 語 / claude-memo 14 語も指示どおり。
- `python3 tools/test_measure_duration.py` は通る。
- **`QUOTE_SAMPLE` のテストは、reviewer 指摘 2（置換文の `\'` 対応）を
  リグレッションとして検知できない。** 実装（`JS_RULE_RE` の修正）自体は
  正しく効いているが、テストのサンプルが弱い。`abc\']def` のような
  「エスケープされた引用符のすぐ後に `]` が続く」ケースをテストに足すと
  検知できるようになる。直すかどうかは管理者判断。
- コメント行の読み飛ばしと、`rules:` が無いデッキのケースは、それぞれ
  対応する実装を壊すとテストが実際に落ちることを確認した。

---

## 再々確認（QUOTE_SAMPLE の差し替え後）

`tools/test_measure_duration.py` の `QUOTE_SAMPLE` が
`[/it's/gi, 'イッツ\']'],`（エスケープした引用符の直後が `]`）に、期待値も
`("it's", "イッツ']", md.re.I)` に差し替わっていることを確認した。

- `python3 tools/test_measure_duration.py` → `OK`、終了コード 0。
- `tools/measure-duration.py` をバックアップしたうえで、`JS_RULE_RE` を
  旧い `r"\[/(.+?)/([gi]*), '(.*?)'\]"` に戻して実行 →

  ```
  AssertionError: [("it's", 'イッツ\\', re.IGNORECASE)]
  ```

  で**落ちた**。前回見つけた「`QUOTE_SAMPLE` が修正 2 のリグレッションを
  検知できない」という穴はふさがっている。確認後、バックアップから
  `tools/measure-duration.py` を元に戻し、`python3 tools/test_measure_duration.py`
  が再び `OK` になること、`git diff --stat` が元の内容（変更 121 行）と
  一致することを確認した。

他の 2 件（コメントアウト行の読み飛ばし、`rules:` の無いデッキ）は前回確認
済みのためやり直していない。

---

## docs/README.md の記述が実装と合っているか

対象: `docs/User.md`「読みを直す」節（新設）、`docs/Developer.md`、
`README.md` の未コミットの変更（`git diff` で見える範囲）。文章の書きぶりは
見ていない。事実と違う箇所だけを確かめた。

### 1. `docs/User.md` の例のとおり `deckConfig.rules` を足すと読みが変わるか

`slides/readme.js` を一時的に変更し（`/tmp/.../scratchpad/readme.js.bak` に
バックアップ）、`docs/User.md` の例そのままの行
`[/requestAnimationFrame/gi, 'リクエスト アニメーション フレーム'],` を
`rules:` に追加してから、Python の `prepare()` で確認した。

```
prepare('requestAnimationFrame を使う', deck='readme')
=> 'リクエスト アニメーション フレーム を使う'
```

期待どおり変わった。確認後 `slides/readme.js` をバックアップから戻し、
`git diff --stat slides/readme.js` が元の `9 insertions` のままであることを
確認した。

### 2. `rules` を省いたデッキでも動くか

`deckConfig.rules` を含まないダミーの `deckConfig` テキストを
`md.deck_rules_from_text()` に渡すと `[]` が返ることを確認した
（Python 側）。JS 側は `player.html` の `prepareSpeechText()` が
`(deckConfig.rules || []).concat(SPEECH_RULES)` と書かれており（前回確認済
み）、`rules` が無いデッキでも空配列にフォールバックする。
記述どおり。

### 3. 「デッキが先、共通が後」「同じ語はデッキ側が勝つ」

- 順番: JS は `(deckConfig.rules || []).concat(SPEECH_RULES)` を `reduce`、
  Python は `load_deck_rules(deck) + load_common_rules()` の順で
  `for` ループを回しており、どちらもデッキ側を先に当てる実装になっている
  （前回・今回の突き合わせで裏付け済み）。
- 「デッキ側が勝つ」の実測: 共通・デッキ双方に `\buser\b` を当てる
  ルールを用意し（デッキ側 `'ゆーざーデッキ版'`、共通側 `'ユーザー'`）、
  `'user がログインする'` を通したところ `'ゆーざーデッキ版 がログインする'`
  になった。デッキ側が先に当たって文字列を書き換えるため、共通側の
  同じパターンはもう一致しない。記述どおり。

### 4. `--text` に `--deck` を合わせないと既定の表（readme）で測る

`measure()` は実行せず（ネットワーク不使用）、コードを追って確認した。

- `tools/measure-duration.py:37`: `DEFAULT_DECK = 'readme'`
- `tools/measure-duration.py:158-159`: `--deck` の `argparse` の既定値は
  `DEFAULT_DECK`
- `tools/measure-duration.py:181`: `--text` のジョブも
  `measure(text, args.deck)` を呼んでおり、`--deck` を省くと
  `args.deck == 'readme'` になる
- `measure()` は `prepare(text, deck)` → `load_deck_rules(deck)` と
  デッキ名で表を選ぶので、`--deck` を付け忘れると `readme` の表で測る。
  記述どおり。

### 5. `docs/Developer.md` / `README.md` のファイル説明・順番・`<script>` タグ

- `slides/_rules.js` をファイル一覧に「全デッキ共通の読みの置換表」として
  追加している → 実在し、説明も一致（`slides/_rules.js` の中身は
  `SPEECH_RULES`、共通表）。
- 「デッキの `deckConfig.rules` が先、`slides/_rules.js` の `SPEECH_RULES`
  が後」→ 3. で確認済み、実装と一致。
- 「`_rules.js` はデッキより先に読む必要があるので、`document.write` の前の
  `<script>` タグで読んでいる（`fetch` にすると `file://` で開けなくなる）」
  → `player.html` を確認したところ、`<script src="slides/_rules.js">` が
  デッキを読む `document.write` のブロックより前（`player.html:462` 付近）
  にあり、`fetch` は使っていない。記述どおり。
- `tools/test_measure_duration.py` の説明を「書き戻しの置換を確かめる
  自己テスト」→「書き戻しの置換と、置換表の読み取りを確かめる自己テスト」
  に変更している。実際のファイルには `apply_durations()` の検査（書き戻し）
  と `load_rules()`/`load_deck_rules()`/`load_common_rules()` の検査
  （置換表の読み取り）の両方があり、一致している。
- 「このスクリプトは... 写しではない（TODO-054）。ただし `TTS_MAX_CHARS` と
  `BASE_SPEED_MULTIPLIER` の 2 つは `player.html` の写し」という記述 →
  `player.html` は `BASE_SPEED_MULTIPLIER = 1.4`（498 行）、
  `TTS_MAX_CHARS = 180`（525 行）、`tools/measure-duration.py` も
  同じ値（40-41 行）を持ち、置換表（`RULES`）自体の写しはコード上に
  無いことは既に確認済み。記述どおり。

### まとめ

上記 5 点について、事実と違う箇所は見つからなかった。
