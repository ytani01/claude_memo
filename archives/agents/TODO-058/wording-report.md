# wording 報告（TODO-058）

## 変更ファイル

- `README.md`
- `CLAUDE.md`
- `docs/User.md`
- `docs/Developer.md`
- `player.html`（コメント）
- `slides/_rules.js`（コメント）
- `slides/readme.js`（コメント + ナレーション + table）
- `slides/user.js`（コメント）
- `slides/developer.js`（コメント）
- `slides/claude-memo.js`（コメント）
- `tools/measure-duration.py`（docstring + help text）
- `tools/test_measure_duration.py`（コメント）

## ナレーション変更

### `slides/readme.js`

**スライド 9**（「入っているスライド」）
- 前: `'このリポジトリには、紹介用のreadme、作り方を説明するuser、内部の作りを説明するdeveloper、実例のclaude-memoの4つのデッキが入っています。'`
- 後: `'このリポジトリには、紹介用のreadme、作り方を説明するuser、内部の作りを説明するdeveloper、実例のclaude-memoの4つのスライド一式が入っています。'`

## 機械的な一括置換にしなかった箇所

### `README.md:55` 表見出し
- 「デッキ」→「名前」
- 理由: 表が列挙する `readme`・`user`・`developer`・`claude-memo` は識別子であり、「名前」の方が見出しとして自然

### `docs/User.md:120` 置換表の対比表
- 「デッキ」→「スライド一式」（表の行見出し）
- 理由: 「共通」との対比を明確にするため。「スライド一式だけの語」と「共通で用いる語」の二項対立が読み取れるように

### `docs/Developer.md` の各所
- 「デッキ側が先」→「スライド一式側が先」
- 「デッキだけの語」→「スライド一式だけの語」
- 理由: 処理順序の対比で「スライド一式」「共通」の関係が読み取れるように。特に日本語として「側」を伴うことで、両者の関係がより明確になる

### `tools/measure-duration.py` docstring
- `slides/<デッキ名>.js` → `slides/<スライド一式名>.js`
- 理由: ファイル名のプレースホルダとしては "スライド一式名" の方が正確。実際のファイルはこの部分に `readme`・`user` などが入る

### `tools/test_measure_duration.py`
- 「4 デッキすべてが実際に読めること（デッキだけの語があるものは 1 つ以上）」
- → 「4 つのスライド一式すべてが実際に読めること（スライド一式だけの語があるものは 1 つ以上）」
- 理由: コメントの「4 つ」という数えに合わせて表現を統一

## 検証

- ✓ grep で「デッキ」が 0 件（archives/ と TODO.md を除く）
- ✓ `node --check` で `slides/*.js` 4 本の構文 OK
- ✓ `python3 tools/test_measure_duration.py` 合格

## duration の測り直し対象

以下のスライド 1 ファイルのナレーションが変わったため、duration の測り直しが必要：

- `slides/readme.js` スライド 9
