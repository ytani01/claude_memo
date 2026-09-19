# TODO-046 レビュー報告

対象: `git diff HEAD` と `git status` に出る未コミットの変更すべて
（`slides-claude-memo.js` → `slides/claude-memo.js` の `git mv`、`player.html`、
`tools/measure-duration.py`、`README.md`、`CLAUDE.md`、`docs/Usage.md`、
`docs/Developer.md`、`archives/agents/TODO-046/README.md`）。

**要修正は 0 件。** 検討 2 件、好みの範囲 2 件。

---

## 検討

### 1. `claude_memo.html:5` — 旧ファイル名がコメントに残っている

```html
<!-- 旧 URL。中身は player.html と slides-claude-memo.js に分けた（TODO-041）。
```

`archives/` を除いたリポジトリ全体を `grep -rn "slides-"` で見たところ、
**旧名が残っているのはここと `TODO.md`（項目の説明なので当然）だけ**で、
実質これが唯一の直し漏れ。

ただし次の TODO-047 で `claude_memo.html` ごと削除する予定なので、
放置しても消える。今直すか、TODO-047 に任せるかは管理者の判断。
TODO-046 のチェックリストにこのファイルは入っていない。

### 2. `docs/Usage.md:10-12` — 手順 1 で括弧が 2 つ続く

```
1. `slides/<名前>.js` を作る（`slides/` は `player.html` と同じ
   ディレクトリに置く）
   （`<名前>` に使えるのは英数字・`_`・`-` だけ。それ以外は捨てられる）
```

変更前は `1. slides-<名前>.js を player.html と同じディレクトリに作る` の
1 文で、括弧は 1 つだった。今回、置き場所の説明を括弧に入れたため、
閉じ括弧の直後にまた開き括弧が来る。`~/.claude/CLAUDE.md` の
「自然な日本語で書く」に照らして読みにくい。

置き場所を本文に戻せば括弧は 1 つに戻る。たとえば
`player.html と同じディレクトリの slides/ に <名前>.js を作る` のように、
1 文で書ける内容。

**「`slides/` が無ければ作る」が書かれていない点については、指摘しない。**
リポジトリには `slides/claude-memo.js` が入っているので、チェックアウト
した人の手元には必ず `slides/` がある。player.html だけを他所へ持ち出す
場合は `docs/Developer.md` の「置き場所は選ばない」が
「`player.html` と `slides/` を同じディレクトリに置けば」と書いていて、
そちらでカバーできている。

---

## 好みの範囲

### 3. `tools/measure-duration.py:28` — 78 字から 82 字に伸びた

```python
SRC = pathlib.Path(__file__).resolve().parent.parent / 'slides' / 'claude-memo.js'
```

変更前は 78 字で、今回 82 字になった。`pathlib` はスラッシュを含む
文字列を 1 つの引数として受けるので、`/ 'slides/claude-memo.js'` と
書けば 78 字のまま。

このリポジトリに行長の規約は無く（`CLAUDE.md` にも `docs/` にも記述が
無い）、同じファイルの 89 行目が既に 80 字あるので、**直さなくてよい。**

### 4. `slides/` のディレクトリ一覧が見えるようになった（実測）

`python3 -m http.server` で配って実測したところ、`slides/` が 200 を返し、
ディレクトリ一覧としてデッキ名が並ぶ。

ただし `public_html/` の下なので元から全部公開されており、
変更前もルートの一覧に `slides-*.js` が並んでいた。**見えるものは
実質変わらないので、対応は要らない。** 隠したいなら `slides/index.html`
を置けばよいが、TODO-046 の範囲外。

---

## 確かめて問題が無かったこと

### `deckName` のサニタイズにパストラバーサルの余地は無い（実測）

```js
const deckName = (new URLSearchParams(location.search).get('deck')
    || 'claude-memo').replace(/[^\w-]/g, '');
document.write(`<script src="slides/${deckName}.js"><\/script>`);
```

`\w` は `u` フラグが無いので ASCII の `[A-Za-z0-9_]`。許可集合に
`.` も `/` も入っていないため、**ディレクトリが 1 段増えても上へは
登れない。** node で実際に通した結果:

| 入力 `?deck=` | 結果の `src` |
|---------------|--------------|
| `../../etc/passwd` | `slides/etcpasswd.js` |
| `..%2F..%2Fsecret` | `slides/2F2Fsecret.js` |
| `%2e%2e%2fx` | `slides/2e2e2fx.js` |
| `a/b` | `slides/ab.js` |
| `a.js` | `slides/ajs.js` |
| `...` | `slides/.js` |
| `` (空) | `slides/claude-memo.js` |
| `deck` 無し | `slides/claude-memo.js` |

`%2F` は `URLSearchParams` が `/` に復号したうえで `replace` が落とすので、
二重エンコードでも抜けられない。

`...` のように全部落ちると `slides/.js` というドットファイルを要求する形に
なるが、HTTP で実測して 404 が返り、エラーメッセージの経路に入ることを
確認した（変更前も `slides-.js` で 404 だったので、挙動は変わらない）。
なお Apache などドットファイルを 403 で拒むサーバーでは 403 になり得るが、
どちらにせよ読み込み失敗として同じ経路に入る（403 の側は未確認）。

### 参照の直し漏れ

`archives/` を除いて `slides-` を全文検索した結果、上の項目 1 以外に
残っているものは無い。TODO-046 が挙げた 3 か所
（`player.html` の `src=` とエラーメッセージ、`measure-duration.py` の `SRC`）は
すべて直っており、余計な変更は入っていない（指示範囲どおり）。

`tools/measure-duration.py` は実際に読み込ませて確認した。
`SRC` が `slides/claude-memo.js` に解決され、`narrations()` が 17 件を
返す（移動前と同じ枚数）。

### `docs/Developer.md` の「置き場所は選ばない」

```
`player.html` がローカルを指しているのは `slides/<名前>.js` の 1 か所だけで、
しかも相対パス。残りは全部 CDN の https。**`player.html` と `slides/` を
同じディレクトリに置けば、`public_html/` の外でもそのまま動く**
```

`player.html` を読んで確認したが、ローカルを指しているのは 467 行目の
`document.write` 1 か所だけで、他は CDN の https か `claude_memo.html` の
相対リンク。`slides/` は相対パスなので、`player.html` と並べて置けば
動く。**記述は実装と合っている。**
「`slides-*.js` を」→「`slides/` を」の書き換えも、ディレクトリを
指すようになったので正しい。

### プロジェクトの `CLAUDE.md` の規約

- **「`docs/` に TODO 番号を書かない」** — `grep -rn "TODO-" docs/ README.md`
  で 0 件。違反なし
- **「`CLAUDE.md` に `docs/` の写しを置かない」** — 今回の変更は
  `slides-claude-memo.js` → `slides/claude-memo.js` と
  `slides-<名前>.js` → `slides/<名前>.js` の置換だけで、節も行も増えていない。
  違反なし
- `CLAUDE.md:20` の `TODO-043` は「このファイルと `archives/` では番号で
  参照してよい」に当たるので問題なし

### テスト

このリポジトリにはテストが無い（`CLAUDE.md`「ビルド、依存関係の
インストール、テストは無い」）。今回の変更はパス文字列 3 か所で、
分岐も条件式も増えていないので、**テストを足す必要は無い。**
動作確認は verifier の担当で足りる。

### コメント

コード側に新しいコメントは追加されていない。既存のコメント
（`player.html` の `document.write` まわり、`measure-duration.py` の
「`player.html` の写し」）はどれも「なぜ」を書いており、
今回の変更で意味が古くなったものは無い。

### `archives/agents/TODO-046/README.md` の書式

表・見出し・分担の理由が揃っていて、他の `archives/agents/` と同じ形。
書いてある内容も実態と合っている。

- `verifier` の定義（`~/.claude/agents/verifier.md`）は `model: sonnet` なので
  「定義どおり Sonnet 5」は正しい
- `reviewer` の定義も `model: sonnet` なので「Opus 5 に上書きした」も正しい
- 「実装は 3 か所のパス文字列と文書だけで小さいため、`implementer` は
  立てず main が行った」も、差分の実態と一致している
