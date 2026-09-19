# TODO-054 の分担

| 担当 | 範囲 |
|------|------|
| implementer | `slides/_rules.js` の新設、`player.html`、4 つのデッキ、`tools/measure-duration.py`、`tools/test_measure_duration.py` |
| verifier | 読みの結果が変更前と一字一句同じか、検査が通るか |
| reviewer | 置換の当たる順番と、パーサの壊れやすさ |
| main | `docs/User.md`、`docs/Developer.md`、`TODO.md`、コミット |

複数のファイルにまたがり、実装・テストがまとまって要るので実装を分けた。
`prepareSpeechText()` の挙動が変わるので、確認とは別にレビューも立てる。

## 依頼（implementer 向け）

### 目的

読みの置換表を `player.html` の中から外へ出し、デッキごとに語を足せるように
する。`tools/measure-duration.py` が持っている写しも消す。

### 1. `slides/_rules.js` を新しく作る

全デッキ共通の表。書き方は次のとおり（`tools/measure-duration.py` が
この形を正規表現で読むので、**1 行 1 ルール、この書式を崩さない**）。

```js
// 全デッキ共通の読みの置換表（TODO-054）。
// デッキだけの語は slides/<名前>.js の deckConfig.rules に書く。
// 当てる順はデッキ側が先、ここが後（デッキ側で読みを上書きできる）。
// tools/measure-duration.py もこのファイルを読む。
const SPEECH_RULES = [
    [/TODO/gi, 'トゥードゥー'],
    [/Claude/gi, 'クロード'],
];
```

共通に入れるのは、**今の `player.html` の `prepareSpeechText()` にある順番の
まま**、次の 20 個だけ。

```
TODO / Claude / 考え方 / 使い方 / measure-duration\.py / player\.html /
User\.md / slideData / \bslides\b / deckConfig / \bdeck\b / \bduration\b /
\bclamp\b / \bcqw\b / px\b / \brem\b / Tailwind / HTML / \bPython\b / \buser\b
```

### 2. 残りをデッキへ移す

各デッキの `deckConfig` に `rules:` を足す。**共通と同じく、今の並び順を保つ。**

- `slides/readme.js` — `claude-memo` / `yt_slide` / `JavaScript` / `\bURL\b` / `\breadme\b` / `\bdeveloper\b`
- `slides/user.js` — `\.js\b` / `\bwrite\b`
- `slides/developer.js` — `archives/todo` / `public_html` / `Online TTS` / `Web Speech` / `requestAnimationFrame` / `container query` / `no-referrer` / `\bmeta\b` / `\bAudio\b` / `\btransform\b` / `\bCDN\b` / `\btools\b`
- `slides/claude-memo.js` — `TODO\.md` / `TODO-([0-9]+)` / `ccstatusline` / `/clear` / `/goal` / `/doctor` / `/rc` / `/login` / `CLAUDE\.md` / `Claude Code` / `tmux` / `pyright-lsp` / `ponytail` / `codegraph` / `git worktree` / `auto-mode` / `\bmain\b` / `\bimplementer\b`

**当たる順番が結果を決める。** `public_html` は `HTML` より、`Claude Code` は
`Claude` より、`TODO.md` は `TODO` より先に当たらなければならない。いずれも
デッキ側が先に当たるので成り立つ。ここが崩れると読みが変わる。

### 3. `player.html`

- デッキを読む `document.write` の**前**に
  `<script src="slides/_rules.js"></script>` を置く（`fetch` は使わない。
  `file://` で開けなくなるため）
- `prepareSpeechText()` の `.replace()` の連なりを消し、
  `deckConfig.rules`（無ければ空）→ `SPEECH_RULES` の順に回す形にする

### 4. `tools/measure-duration.py`

- `RULES` の写しを消し、`slides/_rules.js` とデッキのファイルから読む
- JS と Python で書き方が違うところを吸収する:
  パターンの `\/` は `/`、置換文の `$1` は `\1`、フラグの `i` は `re.I`。
  `re.A` は今までどおり付ける（Python の `\b` は日本語を語の一部と見なす）
- `prepare()` はデッキのルールを先、共通を後に当てる
- 冒頭の docstring の「この下の定数と RULES は player.html の写し」を、
  今の作りに合わせて書き直す

### 5. `tools/test_measure_duration.py`

- 今ある「`player.html` と `RULES` がそろっているか」の検査は、写しが
  無くなるので消す
- 代わりに、**JS から読む関数の検査**を足す。小さな JS の文字列を渡して
  期待どおりのルールが取れること、4 つのデッキが実際に読めること
- `apply_durations()` の既存の検査はそのまま残す

### 完了条件

- `python3 tools/test_measure_duration.py` が `OK` を出す
- **4 デッキすべてのナレーションについて、読みの結果が変更前と一字一句同じ。**
  変更前の結果は `git stash` や `git show HEAD:...` で取れる。自分で
  確かめてから報告すること（ここがずれると `duration` を測り直す羽目になる）
- ネットワークは使わない（実測は要らない）

### 範囲外

`docs/`、`TODO.md`、コミットは管理者がやる。`duration` の測り直しもしない。
