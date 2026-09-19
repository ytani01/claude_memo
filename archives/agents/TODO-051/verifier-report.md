# TODO-051 verifier-report

## 走らせた検証

1. **3 デッキの再生確認**（`python3 -m http.server 8791` + Playwright/chromium、viewport 1280x800 と 1440x900）
   - `player.html`（`?deck=` 無し）→ readme が出た。`SLIDE 01 / 10`、コンソールエラー無し
   - `?deck=usage` → `SLIDE 01 / 11`、コンソールエラー無し
   - `?deck=developer` → `SLIDE 01 / 11`、コンソールエラー無し
   - `?deck=claude-memo` → `SLIDE 01 / 17`、コンソールエラー無し（既存デッキも壊れていないことを確認）
   - 4 デッキとも `page.on('console'|'pageerror')` で拾ったエラーは空配列
   - **終了コード**: 該当なし（ブラウザ確認）。すべて成功

2. **`node --check slides/readme.js slides/usage.js slides/developer.js`**
   → `NODE_CHECK_OK`（終了コード 0）

3. **`duration` の実測突き合わせ**（`tools/measure-duration.py --deck <名前> --all`、`--write` は付けていない）
   - `readme`: 実測 `12,11,11,8,10,9,8,8,12,10` / ファイル中の `duration` `12,11,11,8,10,9,8,8,12,10` → **完全一致**
   - `usage`: 実測 `7,10,10,10,10,9,12,10,10,9,10` / ファイル `7,10,10,10,10,9,12,10,10,9,10` → **完全一致**
   - `developer`: 実測 `12,15,15,16,12,12,12,13,14,9,14` / ファイル `12,15,15,16,12,12,12,13,14,9,14` → **完全一致**
   - 3 デッキとも枚数（10・11・11）と `--all` で測った実測秒数のずれ無し

4. **`tools/test_measure_duration.py`**
   → 標準出力 `OK`、終了コード 0（`apply_durations` の assert がすべて通った）

## 変更されたファイルと指示の範囲

`git status --short`:
```
 M CLAUDE.md
 M README.md
 M docs/Developer.md
 M docs/Usage.md
 M player.html
 M tools/measure-duration.py
?? archives/agents/TODO-051/
?? slides/developer.js
?? slides/readme.js
?? slides/usage.js
```
TODO-051 の指示範囲（`README.md`・`docs/`・3 デッキ新規・`player.html` の既定変更・
`tools/measure-duration.py` の `--deck`）と一致。指示に無いファイルの変更は無い。

`git diff` の中身も確認:
- `player.html`: 既定デッキを `claude-memo` → `readme` に変更した 1 行のみ
- `CLAUDE.md`: 構成の節でデッキ一覧・既定・確認コマンドを更新
- `tools/measure-duration.py`: `SRC` 固定を `SLIDES`/`DEFAULT_DECK` + `--deck` 引数化。
  `narrations()` を引数必須にし、`write_durations()` に `src` を渡す形に変更。ロジックの
  破壊的変更は無く、既存の `apply_durations()` は無変更

## 見た目（スクリーンショット）

PC 幅（1440x900）で 1 枚目と中ほどの 1 枚を撮影。枠からのはみ出し・重なりは無し。

- `/home/ytani/tmp/playwright-mcp/TODO-051-readme-1.png`（1 枚目）
- `/home/ytani/tmp/playwright-mcp/TODO-051-readme-5.png`（5 枚目 `deckConfig と slideData`。コード例あり、崩れ無し）
- `/home/ytani/tmp/playwright-mcp/TODO-051-usage-1.png`（1 枚目）
- `/home/ytani/tmp/playwright-mcp/TODO-051-usage-6.png`（6 枚目 `番号と枚数は自動`）
- `/home/ytani/tmp/playwright-mcp/TODO-051-developer-1.png`（1 枚目）
- `/home/ytani/tmp/playwright-mcp/TODO-051-developer-6.png`（6 枚目 `duration は実測値`）

## 文書と実態の一致

- `README.md`・`docs/Usage.md`・`docs/Developer.md`・`CLAUDE.md` の
  `?deck=`・コマンド例・デッキ一覧・既定のデッキ（`readme`）の記述は、
  実際の動きと一致していた
- `claude-memo` を既定として書き残している箇所は無かった
  （`grep -n "既定" docs/*.md CLAUDE.md README.md` で確認。`claude-memo` は
  「実例」「17 枚が入っている」のような中立の言及のみ）
- `python3 tools/measure-duration.py --help` の出力と `docs/Developer.md`・
  `docs/Usage.md` の説明文は一致（`--deck DECK` の既定値も `readme` と表示された）

## 見つけたこと（判断が要る、または報告のみ）

1. **`tools/measure-duration.py` のモジュール docstring に軽微な誤記がある。**
   17 行目「`--deck` はどのデッキを読むかで、既定は `slides/DEFAULT_DECK.js`。」
   の `DEFAULT_DECK` は f-string ではなく生の文字列なので、実際に `--help` や
   実行結果に `DEFAULT_DECK` という文字は出ない（`--deck` の `help=` の方は
   f-string で正しく `readme` と表示される）。**動作には影響しないが、
   docstring の文言としては `slices/readme.js` と書くべきところが
   `slides/DEFAULT_DECK.js` という不完全なテンプレート文字列のまま残っている。**
   該当箇所: `tools/measure-duration.py:17`

2. **`CLAUDE.md` の「構成」節に、既定デッキが変わったことと整合しない
   説明文が残っている。**
   ```
   「Claude Code の使い方」を紹介する日本語スライドを、動画プレイヤー風の UI で
   自動再生するページ。`player.html` は `?deck=<名前>` で `slides/<名前>.js` を
   読む（既定は `readme`）。
   ```
   （`CLAUDE.md:14-16`）
   この段落の前半「『Claude Code の使い方』を紹介する…ページ」は
   `claude-memo` デッキ 1 本だった頃の説明で、いまは `readme`・`usage`・
   `developer`・`claude-memo` の 4 デッキがあり、既定は「Claude Code の
   使い方」ではなく「yt_slide 自体の紹介」になっている。「既定は `readme`」
   に直した一方で、直前の文はそのまま残っており、内容が食い違っている。
   直すかどうかは管理者の判断。

## 確かめられなかったこと・判断できないこと

- TTS の実測は Google Translate TTS 経由のため、実行するたびにわずかな
  ばらつきが出る可能性がある（今回は 3 デッキとも 1 回の実測でぴったり
  一致した。複数回測って再現性まで確かめてはいない）
- `README.md` のサンプルコード（`slideData` の書き方）が実際の
  `slides/readme.js` の書き方と細部まで一致しているかは、目視での
  比較のみ（文字単位の突き合わせはしていない。指示に「文字単位で
  突き合わせる」とあったのは表示例の再現についてで、この README の
  コード例はスライド内の対応する例のスクリーンショットと見比べ、
  内容は一致していた）
- 上記「見つけたこと」の 2 点は報告のみで、修正はしていない
