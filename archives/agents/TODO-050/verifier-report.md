# TODO-050 verifier 報告

## 走らせた検証

1. `python3 tools/test_measure_duration.py`
   - `OK` を出して終了コード 0。`apply_durations()` の置換（1 枚だけ変える、
     何も変えない、`render` 関数内の `duration: 99,` を巻き込まない）を確認。

2. `tools/measure-duration.py --text 'テスト'`
   - `下書き: 原文 3 字 / 読み 3 字 / 実測 0.888s / BASE_SPEED_MULTIPLIER=1.4 倍速 0.63s -> duration: 1`
   - 終了コード 0。docs/Usage.md の出力例（`--text 'ここに読み上げる文章'`）と
     書式が一致。

3. `--write` を単独で渡す（スライド番号・`--all` 無し）
   ```
   usage: measure-duration.py [-h] [--text TEXT] [--all] [--write] [slides ...]
   measure-duration.py: error: スライド番号か --text か --all を渡す
   ```
   終了コード 2。

   `--write --text 'x'`（`--text` はあるがスライド番号・`--all` 無し）
   ```
   usage: measure-duration.py [-h] [--text TEXT] [--all] [--write] [slides ...]
   measure-duration.py: error: --write はスライド番号か --all と一緒に渡す
   ```
   終了コード 2。指示どおり、`--write` はスライド番号か `--all` と一緒でないと
   エラーになる。

4. `tools/measure-duration.py --all`（書き戻し無し）
   - 17 枚すべて実行できた（終了コード 0）。出力は下記「既存 17 枚の点検」参照。

5. **書き戻しが実際に効くか。**
   `slides/claude-memo.js` の 13 行目 `duration: 10,` を `duration: 999,` に
   書き換えたあと `tools/measure-duration.py 1 --write` を実行。

   ```
   スライド 1: 原文 65 字 / 読み 64 字 / 実測 13.584s / BASE_SPEED_MULTIPLIER=1.4 倍速 9.70s -> duration: 10
   スライド 1: duration 999 -> 10
   claude-memo.js: 1 枚を書き換えた
   ```
   実行後 13 行目は `duration: 10,` に戻り、`git diff --quiet slides/claude-memo.js`
   は差分なし（終了コード 0）で、元の状態に一致することを確認した。
   （※ この時点で `git checkout` は不要だった。ファイルは既に元の値に戻っている）

6. **既存 17 枚の点検。**
   `tools/measure-duration.py --all` の実測結果（`-> duration: N`）と
   `slides/claude-memo.js` の現在の `duration` を突き合わせた。

   | スライド | 現在の duration | 実測結果 |
   |---|---|---|
   | 1 | 10 | 10 |
   | 2 | 21 | 21 |
   | 3 | 19 | 19 |
   | 4 | 23 | 23 |
   | 5 | 18 | 18 |
   | 6 | 23 | 23 |
   | 7 | 25 | 25 |
   | 8 | 19 | 19 |
   | 9 | 19 | 19 |
   | 10 | 21 | 21 |
   | 11 | 19 | 19 |
   | 12 | 15 | 15 |
   | 13 | 17 | 17 |
   | 14 | 17 | 17 |
   | 15 | 16 | 16 |
   | 16 | 18 | 18 |
   | 17 | 24 | 24 |

   **17 枚すべて一致。ずれは無い。**

   ※ `--all --write` の実行は、Claude Code の auto mode の分類器に
   「Irreversible Local Destruction」として拒否され、こちらの環境からは
   実行できなかった（許可を得れば再実行できる）。ただし上記の突き合わせで
   17 枚とも現在値と実測値が一致しているため、`--all --write` を実行しても
   `変更なし` になるはずだと判断できる。項目 5 で単発の書き戻しは確認済み。

7. docs の記述と実際の動きの突き合わせ
   - README.md・docs/Developer.md・docs/Usage.md の説明文どおりに `--write` が
     動くことを 1〜6 で確認した。
   - docs/Usage.md の `--all --write` の出力例
     ```
     スライド 15: duration 17 -> 16
     claude-memo.js: 1 枚を書き換えた
     ```
     は「変わった枚だけ出る」ことの説明用の例であり、現在の
     `slides/claude-memo.js` の実測値と一致させる意図の例ではないと読める
     （現状ではスライド 15 は 16 のままでずれていないので、この例をそのまま
     再現することはできない。単発の書き換えでは、項目 5 で「999 -> 10」と
     いう形で同じ仕組みが働くことは確認した）。

## 変更されたファイル

- `README.md`、`docs/Developer.md`、`docs/Usage.md`、`tools/measure-duration.py`
  （追跡済み・変更）
- `tools/test_measure_duration.py`（新規）
- `archives/agents/TODO-050/`（新規。分担の README のみ、着手前に main が置いたもの）

TODO-050 の対象（`--write` の追加、docs の更新、テストの追加）と一致しており、
指示の範囲外のファイルは変わっていない。

## 確かめられなかったこと・判断が要る点

- **`--all --write` そのものの実行は auto mode の許可拒否で行えなかった。**
  代わりに `--all`（書き戻し無し）で 17 枚の実測値を取り、現在の
  `slides/claude-memo.js` と手で突き合わせて一致を確認し、書き戻しの仕組み自体は
  項目 5 の単発テスト（999 -> 10 に戻ることと `git diff` が空になること）で
  確認した。`--all --write` を通しで走らせたい場合は、Bash の許可設定を
  変えるか、管理者側で実行してもらう必要がある。
- TODO.md のチェックボックス「`--all --write` で 17 枚を測り、
  `slides/claude-memo.js` の `duration` を書き換える」は、現状すでに 17 枚とも
  実測値と一致しているため、この項目が指す「実際に書き換える作業」が
  過去に済んでいるのか、それとも最初から一致していて書き換える必要が
  無かったのかは、このログからは判断できない。管理者の確認を勧める。
