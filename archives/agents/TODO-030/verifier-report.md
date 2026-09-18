# TODO-030 検証報告

## 結論

**1 件、要確認あり。** `tools/measure-duration.py` の写しは 20 件すべて
一致し、コマンドも書いたとおりに動く。ただし **`--all` の実測が
スライド 15 だけ `duration` の値とずれている**（実測 16、実装 17）。
コードは直していない。

## 1. 写しの突き合わせ（1 行ずつ）

`tools/measure-duration.py` の `RULES`（20 件）と、`claude_memo.html`
`prepareSpeechText()` の `.replace()`（20 件）を、**順番・パターン・
置換後の文字列・大文字小文字の扱い**の 4 項目で 1 行ずつ突き合わせた。

| # | パターン | 置換後 | JS のフラグ | Python のフラグ | 一致 |
|---|---|---|---|---|---|
| 1 | `TODO\.md` | トゥードゥー ドット エムディー | `gi` | `re.I` | OK |
| 2 | `TODO-([0-9]+)` → `\1`/`$1` | トゥードゥー \1 | `gi` | `re.I` | OK |
| 3 | `TODO` | トゥードゥー | `gi` | `re.I` | OK |
| 4 | `ccstatusline` | シーシー ステータス ライン | `gi` | `re.I` | OK |
| 5 | `/clear` | スラッシュ クリア | `gi` | `re.I` | OK |
| 6 | `/goal` | スラッシュ ゴール | `gi` | `re.I` | OK |
| 7 | `/doctor` | スラッシュ ドクター | `gi` | `re.I` | OK |
| 8 | `/rc` | スラッシュ アールシー | `gi` | `re.I` | OK |
| 9 | `/login` | スラッシュ ログイン | `gi` | `re.I` | OK |
| 10 | `Claude Code` | クロード コード | `gi` | `re.I` | OK |
| 11 | `Claude` | クロード | `gi` | `re.I` | OK |
| 12 | `tmux` | ティーマックス | `gi` | `re.I` | OK |
| 13 | `pyright-lsp` | パイライト エルエスピー | `gi` | `re.I` | OK |
| 14 | `ponytail` | ポニーテール | `gi` | `re.I` | OK |
| 15 | `codegraph` | コードグラフ | `gi` | `re.I` | OK |
| 16 | `git worktree` | ギット ワークツリー | `gi` | `re.I` | OK |
| 17 | `auto-mode` | オートモード | `gi` | `re.I` | OK |
| 18 | `考え方` | かんがえかた | `g`（大小区別あり） | `0`（フラグ無し＝大小区別あり） | OK |
| 19 | `\bmain\b` | メイン | `gi` | `re.I` | OK |
| 20 | `\bimplementer\b` | インプリメンター | `gi` | `re.I` | OK |

**20 件中 20 件、順番・パターン・置換後の文字列・大小文字の扱いとも一致。**
18 番目だけ他と違って `g`（大小区別あり）で、Python 側もそこだけ
フラグ 0（`re.I` を付けない）になっており、ここも揃っている。

バックリファレンスの書き方は JS が `$1`、Python が `\1` で表記こそ違うが、
`re.sub` と `String.replace` それぞれの正しい書き方であり、意味は同じ
（`tools/measure-duration.py 2 17` の実測で `TODO-17` を含むナレーションが
無かったため、この 1 件は展開結果の実地確認はできていない。パターン上の
突き合わせのみ）。

定数も確認した。

- `TTS_MAX_CHARS`: Python `180` / JS（1168 行）`180` → 一致
- `BASE_SPEED_MULTIPLIER`: Python `1.4` / JS（1141 行）`1.4` → 一致

切り詰めの順序も確認した。Python は `prepare(text)` してから
`spoken[:TTS_MAX_CHARS]`（置換の**後**に切る）。JS は
`textToSpeak = prepareSpeechText(slide.narration)` を
`speakOnlineTTS(textToSpeak)` に渡し、その中で
`text.substring(0, TTS_MAX_CHARS)`（1460〜1465 行）としており、
**置換してから渡す**ので順序は同じ。一致。

## 2. コマンドの動作確認

`CLAUDE.md` に書かれた形をそのまま実行した。

```
$ tools/measure-duration.py 2 17
スライド 2: 原文 114 字 / 読み 126 字 / 実測 27.240s / 1.4 倍速 19.46s -> duration: 19
スライド 17: 原文 162 字 / 読み 174 字 / 実測 32.664s / 1.4 倍速 23.33s -> duration: 23

$ tools/measure-duration.py --text 'テストです。'
下書き: 原文 6 字 / 読み 6 字 / 実測 1.200s / 1.4 倍速 0.86s -> duration: 1

$ tools/measure-duration.py
usage: measure-duration.py [-h] [--text TEXT] [--all] [slides ...]
measure-duration.py: error: スライド番号か --text か --all を渡す
（exit code 2、クラッシュせずエラーメッセージで終了）

$ cd /tmp && .../tools/measure-duration.py 1
スライド 1: 原文 110 字 / 読み 107 字 / 実測 22.344s / 1.4 倍速 15.96s -> duration: 16
（exit code 0。プロジェクトのトップ以外から実行しても `SRC` が
`__file__` からの相対で正しく解決され、動く）
```

4 点とも問題無し。

## 3. `--all` の実測と `duration` の突き合わせ

```
$ tools/measure-duration.py --all
スライド 1: ... -> duration: 16
スライド 2: ... -> duration: 19
スライド 3: ... -> duration: 19
スライド 4: ... -> duration: 19
スライド 5: ... -> duration: 21
スライド 6: ... -> duration: 19
スライド 7: ... -> duration: 19
スライド 8: ... -> duration: 19
スライド 9: ... -> duration: 18
スライド 10: ... -> duration: 21
スライド 11: ... -> duration: 19
スライド 12: ... -> duration: 15
スライド 13: ... -> duration: 17
スライド 14: ... -> duration: 17
スライド 15: ... -> duration: 16
スライド 16: ... -> duration: 18
スライド 17: ... -> duration: 23
```

`grep -oP "duration:\s*\K[0-9]+" claude_memo.html` で拾った実装側の値
（順に 16, 19, 19, 19, 21, 19, 19, 19, 18, 21, 19, 15, 17, 17, **17**,
18, 23）と突き合わせた。

**スライド 15 だけずれている。** `--all` の実測は `duration: 16`、
`claude_memo.html` の実装は `duration: 17`。他の 16 枚は一致。

（この 1 件のずれは `duration` の値と実測の話で、
`measure-duration.py` 自体の写し違いではない。TTS の実測は
ネットワーク経由の音声を毎回取得するため 1 秒未満の揺れが出ることは
これまでの計測でも見えているが、今回は 1 秒の差なので誤差の範囲か、
それとも直し忘れかは判断できない）

## 4. `CLAUDE.md` の記述確認

- `slideData` の要素の形から `category` が消えている:
  `{ id, title, duration, narration, render() }` になっており、
  `claude_memo.html` 本体にも `category:` は 1 件も無い（`grep` で確認）→ 一致
- 合計 316 秒: `duration` の合計を `grep` + `awk` で計算 → **316**、
  `CLAUDE.md` の記述と一致
- 「構成」の節: `tools/` に触れている（`claude_memo.html` 1 ファイルと、
  `tools/` の補助スクリプトだけ、という記述に直っている）→ 一致

## やらなかったこと・判断できないこと

- スライド 15 の `duration: 16`（実測） vs `17`（実装）のずれが、誤差か
  直し忘れかは判断できない。1 秒の差であり、他の 16 枚は完全一致している
  ことから、このスライドだけ実装側の値が古い可能性がある。**直すかどうかは
  管理者の判断**
- `\bTODO-([0-9]+)\b` のバックリファレンス（`\1`/`$1`）の実地動作は、
  今回のナレーションに `TODO-数字` を含む文が無かったため、パターンの
  文字列比較のみで確認した（実行結果での確認はしていない）
