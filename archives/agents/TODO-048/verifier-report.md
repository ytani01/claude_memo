# TODO-048 verifier report

## 確かめたこと

### 1. `id` を読む箇所が残っていないか
`grep -n "\.id\b\|id:" player.html docs/Usage.md docs/Developer.md tools/measure-duration.py slides/claude-memo.js`
の結果、該当なし（全ファイルでヒット 0 件）。
`slides/claude-memo.js` の `id:` 行は旧版で 17 行あったが、
`git diff slides/claude-memo.js | grep -c '^-.*id:'` の結果も 17 で、
全行が削除されている（新版に `id:` は残っていない）。

### 2. 差し替えた 3 箇所が元と同じ番号を出すか
- `player.html:895` `slideNum.textContent = String(currentIndex + 1).padStart(2, '0');`
- `player.html:896` `controlTitlePreview.textContent = \`${currentIndex + 1}. ${slide.title}\`;`
- `player.html:1013` `${String(idx + 1).padStart(2, '0')}`（`slideData.forEach((slide, idx) => ...)` の `idx`）

`renderSlide(index, ...)` の冒頭（880〜882行）で `currentIndex = index;` と
先に代入してから 895・896 行を使っているので、その時点の `currentIndex` は
呼び出し時に渡された添字と一致する。`idx` は `Array.forEach` のコールバック
引数で 0 始まりの添字そのもの。どちらも `+ 1` しているので 1 始まりになる。

旧版の `slides/claude-memo.js`（`git show HEAD:slides/claude-memo.js`）を
確認したところ、`id: 1` 〜 `id: 17` が配列の並び順（1 番目の要素が
`id: 1`、17 番目が `id: 17`）とちょうど一致していた（TODO-025 の並び替え後
の状態で既にずれが無かった）。よって `currentIndex + 1` / `idx + 1` は
旧 `slide.id` と全スライドで一致し、表示は変わらない。

### 3. 構文チェックと `narration` 件数
`slides/claude-memo.js` は ES モジュールではない（`window.deckConfig = ...`
形式）ため `node --check slides/claude-memo.js` がそのまま使え、
`SYNTAX OK` を確認した。

`tools/measure-duration.py` の `narrations()` と同じ正規表現
（`r"narration: '(.*?)',\n"`）で抽出したところ 17 件取得できた（想定どおり）。

### 4. 文書に `id` の説明が残っていないか
`docs/Usage.md` の記述例 2 箇所（本編・サンプル）から `id: 1,` の行が
両方削除済み。キーの表からも `id` の行が外れている。
「**スライドの番号も枚数もどこにも書かない。**」という一文に更新されており、
実データ（`id` を持たない配列）と整合している。
`docs/Developer.md` も `{ id, title, duration, narration, render() }` から
`{ title, duration, narration, render() }` に直り、「スライド番号は持たせず、
並び順から出す（TODO-048）」の一文が足されている。

### 5. `tools/measure-duration.py` が `id` に依存していないか
`grep -n "\.id\b\|id:" tools/measure-duration.py` はヒット無し。
`narrations()` は正規表現でナレーション文字列を並び順に取るだけで、
`id` を参照していない。

## 見つけたこと（判断が要る点）

TODO-048 の対象は `player.html` の 3 箇所・`slides/claude-memo.js` の
`id:` 17 行・`docs/Usage.md` の記述例 2 箇所とキーの表、と TODO.md に
書かれている。しかし実際の未コミット差分には、これに加えて
**`docs/Developer.md` の定数名置き換え**（`1.4` → `BASE_SPEED_MULTIPLIER`、
`180 文字` → `TTS_MAX_CHARS`、`4.5` → `SPEECH_CHARS_PER_SECOND`、
`3 秒` → `TTS_END_MARGIN_MS`、`40 文字程度` → `maxLen` の既定値、など）と、
**`docs/Usage.md` の同種の定数名置き換え**（`1.4 倍速` → `BASE_SPEED_MULTIPLIER`、
`180 字で切れる` → `TTS_MAX_CHARS` など）、さらに**`tools/measure-duration.py`
全体**（docstring・help・結果表示の定数名置き換え）が混ざっている。

これらは TODO.md の `## TODO-049. ドキュメントとスクリプトの数値を定数名に
置き換える` の内容と一致する（`TODO-049` のチェックボックスは全て未チェック
`[ ]` のまま）。つまり、**TODO-048 と TODO-049 の変更が同じ作業ツリーの
差分に混在した状態でコミット待ちになっている**。

依頼の対象範囲は 4 ファイル（`tools/measure-duration.py` を含まない）
だったため、この 5 番目のファイルの変更は指示の範囲外だが、
`docs/Developer.md` と `docs/Usage.md` の diff 自体にも TODO-048 と
無関係な TODO-049 分の変更が同居している。TODO-048 の内容自体
（`id` を外す）は正しく反映されているが、**TODO-048 として確認・コミット
すべき範囲と、TODO-049 として別にすべき範囲が今の作業ツリーでは分かれて
いない**。これをどう扱うか（TODO-048 と TODO-049 をまとめて 1 コミットに
するか、`git add -p` などで分けてコミットするか）は管理者の判断が必要。

## 確かめられなかったこと
- ブラウザでの実際の表示確認（DOM を実際にレンダリングしての目視）はして
  いない。コードを読んで `currentIndex` / `idx` の値を追う静的な確認と、
  旧 `id` の値との突き合わせで代用した。
