# TODO-030 検証依頼

## 目的

`duration` の測定スクリプトをリポジトリに入れた。**写し元とずれていないか**と、
**`CLAUDE.md` に書いたコマンドが書いたとおりに動くか**を確かめる。

## 対象

- `tools/measure-duration.py`（新規）
- `CLAUDE.md`（差分は `git diff HEAD`）

## 完了条件

**1. 写しがずれていないこと。** これが一番大事。スクリプトの `RULES` と
定数は `claude_memo.html` の写しで、ずれると測った秒数が実際とずれる。
**1 行ずつ突き合わせて確かめること。**

- `RULES` の 20 件が `prepareSpeechText()` の `.replace()` と、
  **順番・パターン・置換後の文字列・大文字小文字の扱い（`gi` か `g` か）**
  まで一致している
- `TTS_MAX_CHARS = 180` が `claude_memo.html` の `TTS_MAX_CHARS` と一致
- `BASE_SPEED_MULTIPLIER = 1.4` が `claude_memo.html` の
  `BASE_SPEED_MULTIPLIER` と一致
- 180 字の切り詰めが `speakOnlineTTS()` の
  `text.substring(0, TTS_MAX_CHARS)` と同じ扱い（置換の**後**に切ること）

**2. コマンドが書いたとおりに動くこと。** `CLAUDE.md` に書いた形を
そのまま打って確かめる。

- `tools/measure-duration.py 2 17`
- `tools/measure-duration.py --text 'テストです。'`
- `tools/measure-duration.py --all`
- 引数を何も渡さないとき、エラーメッセージが出て落ちないこと
- **プロジェクトのトップ以外から実行しても動くこと**（`SRC` を
  `__file__` からの相対で解いているはず）

**3. 測った値が今の `duration` と合っていること。** `--all` の出力と
`slideData` の `duration` を突き合わせる。**ずれている枚があれば、
枚数と値を報告する**（直さない）。

**4. `CLAUDE.md` の記述が実装と合っていること。**

- `slideData` の要素の形から `category` が消えている（TODO-029 の消し残しを
  この項目で直した）
- 合計 316 秒が `duration` の合計と一致
- 「構成」の節が `tools/` に触れている

## やらないこと

**コードは直さない。** 見つけたことを報告するだけ。

## 報告

`archives/agents/TODO-030/verifier-report.md` に書く。
**返事は 5 行以内**。**写しの突き合わせは「一致した」で済ませず、
何件を照合したかを数字で書くこと。**

## 目安

10〜20 分。`--all` は 17 回 `curl` を叩くので少し時間がかかる。
