# TODO-058 verifier-report

## 1. `?slides=` / 旧 `?deck=` / 両方無いときの既定 / 両方あるとき

`player.html:466-473` のパラメータ解決ロジックを node で切り出して確認した。

```js
const slidesName = (params.get('slides') || params.get('deck') || 'readme')
    .replace(/[^\w-]/g, '');
```

結果:

```
slides only: user
deck only:   user
both:        readme   (?slides=readme&deck=user)
neither:     readme
```

`slides` が優先され、無ければ `deck`、両方無ければ `readme`。問題なし。

## 2. `slides/_rules.js` 置換表の順序と実際の置換

```
[/slidesConfig/gi, 'スライズ コンフィグ'],   // 18行目
[/\bslides\b/gi, 'スライズ'],                // 19行目
```

`slidesConfig` が先。node で `SPEECH_RULES` を実際に読み込み、
`"slidesConfig.rules と slides の話"` に順に当てた結果:

```
スライズ コンフィグ.rules と スライズ の話
```

`slidesConfig` が壊れず一括で置換され、`slides` 単体も正しく置換された。問題なし。

## 3. `deck`・「デッキ」の残存

```
grep -rln "deck\|デッキ" --include="*.html" --include="*.js" --include="*.py" --include="*.md" . \
  | grep -v archives/ | grep -v 'TODO\.md$'
```

`player.html` のみヒット。該当は以下の後方互換 2 行だけ（想定どおり）。

```
468:         旧 ?deck= も受ける（TODO-058。公開済みのリンクが切れるため）。 -->
471:        const slidesName = (params.get('slides') || params.get('deck')
```

`docs/`・`README.md`・`slides/*.js`・`tools/*.py`・`CLAUDE.md` に `deck`/`デッキ` の
残存なし。

## 4. `docs/User.md` / `README.md` に「旧 `?deck=` も動く」の記載が無いこと

`grep -n "deck\|デッキ" docs/User.md README.md docs/Developer.md CLAUDE.md` → ヒット無し。
指示どおり文書には出していない。

## 5. `tools/measure-duration.py` の動作

- `--help`: `--slides SLIDES_NAME`（既定 `readme`）、`--text`、番号指定、`--all`、`--write` が
  そろっている。
- `--slides readme/user/developer/claude-memo --all` を実行、いずれも exit 0 で各スライドの
  `duration:` が出力された。
- `--text "テスト文章です"` → exit 0（`--slides` 省略でも既定 `readme` の置換表で動く）。
- 番号指定（`--slides` を付けず `1`）→ exit 0、`readme` のスライド1が測定された
  （コード上 `DEFAULT_SLIDES = 'readme'`、`--slides` の既定値も同じ）。

いずれも問題なし。

## 6. `python3 tools/test_measure_duration.py`

- 現状: `OK`、exit 0。
- わざと壊す: `slides/_rules.js` から `slidesConfig` の置換行を一時的に削除し、再実行したところ
  以下で落ちた（想定どおり検知できた）。

  ```
  AssertionError: [('TODO\\.md', ...), ... ('\\bslides\\b', 'スライズ', re.IGNORECASE), ...]
  assert len(common_rules) == 23, common_rules
  ```

- 直後に `\cp /tmp/_rules.js.bak slides/_rules.js` で復元し、再度 `OK`（exit 0）を確認。
  `git diff --stat slides/_rules.js` の差分行数（9 行）も壊す前後で変わらないことを確認した。

## 7. 構文チェック（`node --check`）

- `slides/readme.js` / `slides/user.js` / `slides/developer.js` / `slides/claude-memo.js`:
  いずれも OK。
- `player.html` は拡張子の都合で直接は不可のため、`<script>...</script>` 3 個を
  抜き出して `node --check` を個別に実行し、3 つとも OK。

## 8. `duration` の測り直しの整合性

`--all`（`--write` 無し）で出力された `duration: N` の並びと、各 `slides/<名前>.js` 内の
`duration: N,`（フィールドとしての行）の並びを突き合わせた。4 ファイルとも完全一致。

（`slides/readme.js` と `slides/user.js` の grep には、コード例として画面に表示している
`duration: 10` や `duration: 2` という文字列がノイズとして混ざったが、これは `render()` 内の
説明用 HTML 文字列であり、実際の `duration:` フィールドではない。フィールドとしての行
（末尾にカンマがあるもの）だけを比べると 4 ファイルとも一致した。）

## 9. 日本語の言い換えの自然さ

`docs/User.md` の「読みを直す」節、`slides/_rules.js` のコメント、
`tools/measure-duration.py` の docstring、`docs/Developer.md`、`CLAUDE.md`、
`slides/*.js` の該当箇所を読んだ。「共通」と「スライド一式だけ」の対比は
崩れておらず、機械的な単純置換で不自然になっている箇所は見当たらなかった
（例: `slides/readme.js:232` の紹介ナレーションも読める文になっている）。

ただし自然さの判断は主観に依るところがあり、完全に網羅したわけではない
（全ファイルの全箇所を読んだわけではなく、置換対象の周辺を中心に確認した）。

## 変更ファイルと指示の範囲

`git status --short`:

```
M CLAUDE.md
M README.md
M docs/Developer.md
M docs/User.md
M player.html
M slides/_rules.js
M slides/claude-memo.js
M slides/developer.js
M slides/readme.js
M slides/user.js
M tools/measure-duration.py
M tools/test_measure_duration.py
?? archives/agents/TODO-058/
```

TODO-058 の「変えるもの」表・依頼文の対象範囲（`player.html`、`slides/*.js` 4 本、
`tools/` 2 本、`docs/`、`README.md`、`CLAUDE.md`）と一致しており、範囲外のファイルの
変更は見当たらなかった。`docs/Developer.md:109` の `deckConfig.rules` 直しと
`slides/developer.js`・`slides/readme.js` のナレーション各 1 箇所の直しも `git diff` で
確認できた。

## 確かめられなかったこと・判断が要ること

- ブラウザでの実際の読み上げ（TTS）確認はしていない（node でのロジック抽出確認のみ）。
- 日本語の言い換えの自然さは主観判断であり、全ファイル・全箇所を機械的に突き合わせては
  いない。不自然だと明確に言える箇所は見つからなかったが、「完全に問題無し」を保証する
  ものではない。
