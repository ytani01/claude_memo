# TODO-045 verifier report

対象: `README.md`（新規、未コミット）

## 1. ファイル構成の表

`git ls-files`（archives 以外）と突き合わせた。

```
.gitignore
CLAUDE.md
TODO.md
claude_memo.html
docs/Developer.md
docs/Usage.md
player.html
slides-claude-memo.js
tools/measure-duration.py
```

README の表に載っているもの: `player.html`・`slides-<名前>.js`・
`slides-claude-memo.js`・`claude_memo.html`・`docs/`・
`tools/measure-duration.py`・`archives/`・`TODO.md`・`CLAUDE.md`。
実在するファイルと一致し、主なものの漏れも無い。`.gitignore` は
「主な」とは言えず、載っていなくても問題ないと判断した（これは判断）。

## 2. 手元で動かす手順

空きポート 8931 で `python3 -m http.server` を実際に起動し、curl で確認した。

```
player.html: 200
slides-claude-memo.js: 200
player.html?deck=claude-memo: 200
```

サーバは確認後に `kill` で停止し、`pgrep -f "http.server 8931"` で
プロセスが残っていないことを確認済み（`pkill` は使っていない）。

## 3. リンク

`docs/Usage.md`、`docs/Developer.md` とも実在する（`ls docs/` で確認）。
相対パスの書き方も問題なし。

## 4. `?deck=` を省くと `slides-claude-memo.js` を読む

`player.html` 465-466 行目を確認した。

```js
const deckName = (new URLSearchParams(location.search).get('deck')
    || 'claude-memo').replace(/[^\w-]/g, '');
document.write(`<script src="slides-${deckName}.js"><\/script>`);
```

`deck` パラメータが無ければ `'claude-memo'` にフォールバックし、
`slides-claude-memo.js` を読み込む。README の記述と一致する。
実機テストでも `player.html`（`?deck=` 無し）が 200 を返し、
`deck=claude-memo` を明示した場合と同じスライド構成であることを
確認した。

## 5. 事実の整合性

- 字幕・再生速度・フルスクリーンの切り替え: `player.html` に
  `toggle-caption-btn`・`speed-select`・フルスクリーン関連のコードが
  実在する（確認済み）
- CDN 依存（Tailwind・Google Fonts・FontAwesome）: `player.html`
  11-17 行目、および `docs/Developer.md` 17-25 行目の記述と一致
- ビルド無し: `docs/Developer.md` の記述と矛盾しない。リポジトリに
  `package.json` 等のビルド設定は無く、事実と合っている
- 実例 17 枚: `slides-claude-memo.js` 内のスライドオブジェクト数
  （`{` の出現数・`id:` の出現数）がいずれも 17 で一致。冒頭のタイトルも
  「私の Claude Code の使い方」で README の記述と一致
- `claude_memo.html` が旧 URL から `player.html?deck=claude-memo` への
  リダイレクトであること: ファイルの中身（`location.replace` と
  `<meta http-equiv="refresh">`）で確認済み

## 6. 「含めない」と決めたものが入っていないか

- 公開 URL: 記載なし
- `TODO.md` の運用への言及: 表の 1 行としての説明のみ
  （「進行中の項目と、完了済みの目次」）で、TODO-045 が
  「構成表の 1 行としての説明は可」としている範囲に収まる
- プレイヤーの機能一覧（操作の説明）:
  冒頭の概要文に「字幕・再生速度・フルスクリーンを切り替えられる」と
  ある。これは機能名の列挙であり、ボタンの押し方などの「操作の説明」
  ではないが、TODO-045 が「何のリポジトリか」の説明として求めている
  範囲（`player.html` はナレーション付きスライドの再生プレイヤー、
  実例は 17 枚）を超えて機能名を並べている。**「含めない」とした
  機能一覧に当たるかどうかは境界線上で、判断できない。管理者の判断が
  要る点として報告する。**

## 確かめられなかったこと

- ブラウザでの実際の表示・字幕表示・フルスクリーン動作そのものは
  今回の確認範囲外（README の記述内容の裏取りとしては player.html の
  コードと docs の記述の突き合わせに留めた）
