# TODO-050. 測った `duration` をスライドデータへ自動で書き戻す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + reviewer |
| 実施 | Opus 5 / effort high | verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 25,408 | 44,193 | 68% |
| reviewer | Sonnet 5 | high | 25,093 | 68,427 | 24% |
| verifier | Sonnet 5 | medium | 6,200 | 34,308 | 9% |
| 合計 |  |  | 56,701 | 146,928 | 概算 $3.0 |

- verifier と reviewer は定義（`~/.claude/agents/`）のまま。モデルの上書きはしていない

## きっかけ

`duration` は「Online TTS の音声を `BASE_SPEED_MULTIPLIER` 倍で再生した
実測秒数」なので、ナレーションを変えるたびに測り直しが要る（TODO-018）。
測る道具は TODO-030 で `tools/measure-duration.py` として入れたが、
出た値を `slides/claude-memo.js` へ手で書き写す必要があった。
TODO-032 は、その書き写し忘れで 1 枚ずれていた件。

利用者から「全部測って自動的に入れるツールが欲しい」と依頼があった。

## 決めたこと

- **新しいスクリプトは作らず、`tools/measure-duration.py` に `--write` を
  足す。** 置換表と定数の写しが 1 か所のままで済む
- **`--dry-run` は作らない。** 変わった枚だけ `17 -> 16` と出して、
  そのまま書き換える。戻すのは git の差分で足りる
- **複数回測って中央値は採らない。** ぶれが問題になってから考える

## やったこと

**1. `tools/measure-duration.py` に `--write` を足した。**

```bash
tools/measure-duration.py --all --write   # 全部測って書き戻す
tools/measure-duration.py 15 --write      # 1 枚だけ
```

- 置換は `apply_durations(text, updates)`（ファイルに触らない）と、
  読み書きをする `write_durations(updates)` に分けた
- `duration: N,` の次の行に `narration: '` が来る並びで拾う。
  `render()` が返す HTML の中の `duration:` を巻き込まないため
- 拾えた数が `narration` の数と合わなければ、書かずに終わる
- 測定が途中で失敗するとその場で終わり、書き込みまで進まない
  （`write_text()` は全部測り終えたあと 1 回だけ呼ぶ）
- `--write` を `--text` だけと組み合わせたときは、測る前にエラーで止める

**2. `tools/test_measure_duration.py` を置いた。**
`apply_durations()` の置換だけを見る。ネットワークも `pytest` も要らず、
`python3` だけで走る。`render()` の中の `duration: 99,` を巻き込まないことも
ここで見ている。

**3. 文書を直した。** `README.md`、`docs/Usage.md`、`docs/Developer.md` に
`--write` の使い方と出力例を足した。`CLAUDE.md` と `docs/Developer.md` の
「テストは無い」も、テストが 1 本できたので直した。

## 確かめたこと

verifier が確認した（報告は `archives/agents/TODO-050/verifier-report.md`）。

- 自己テストが通る。文書に書いたコマンド例が書いたとおりに動く
- **1 枚わざとずらしてから書き戻すと元に戻り、`git diff` が空になる**
- **既存 17 枚の点検。`--all` の実測値と `duration` が 17 枚とも一致**
  （TODO-032 で直したスライド 15 も 16 のまま）

reviewer が差分を見た（報告は `archives/agents/TODO-050/reviewer-report.md`）。
要修正 1 件は直した。

- **`CLAUDE.md` の「テストは無い」が取り残されていた。**
  `docs/Developer.md` 側だけ直して、同じことを書いている `CLAUDE.md` を
  見落としていた。直した
- 長すぎた表の行と、同じファイルを 3 回読んでいた箇所も直した
- 書き戻しの安全さ、`--text` との組み合わせ、関数を 2 つに分けたことは
  問題なしと確認された

## 残ること

- **`--write` は `slides/claude-memo.js` 固定。** 他のデッキでは使えない。
  TODO-051 で直す
- **`render()` の中にスライドデータの書き方をそのまま載せると、
  正規表現が誤爆しうる。** 今のデッキには無いが、`player.html` の使い方を
  説明するデッキ（TODO-051）を作るときは、`duration: 20,` の次の行に
  `narration: '` が来る書き方を避けるか、`found` の食い違いで止まるのを
  当てにすること

## 分担の振り返り

- **reviewer が `CLAUDE.md` の追随漏れを見つけた。** verifier は「書いた
  ものが動くか」を見るので、**書き換えていないファイルとの食い違いは
  拾えない**。同じ主張が 2 か所にある文書では、レビューの担当が要る
- **verifier は既存 17 枚の点検で「全部一致」を出した。** TODO-030 の
  振り返りで決めた「入れた道具で既存のデータを一通り点検させる」を
  依頼書に書いた。今回はバグが出なかったが、`--write` が既存の値を
  壊さないことの確かめにもなった
- **見込み（verifier + reviewer）と食い違わなかった。** 実装は 1 ファイルに
  閉じたので implementer は立てず、main が書いた
- **verifier の `--all --write` が権限で止まった**（ファイルを壊しうる操作と
  判定された）。verifier は単発の書き戻しで代替し、通しの実行は main が
  済ませていた。**ファイルを書き換える道具を確認させるときは、
  「通しの実行は管理者が済ませた」と依頼書に書いておくと迷わせずに済む**
- **次に同じ規模（道具に機能を 1 つ足す）をやるなら、同じく
  verifier + reviewer の 2 人でよい。** reviewer の分が料金の 24% で、
  拾ったのは 1 件だが、それは verifier には拾えない種類だった
