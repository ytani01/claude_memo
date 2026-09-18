# TODO-026 検証依頼

## 目的

まとめ（スライド 17）に「その他の便利な使い方」の行を足したことで、
表示と秒数が壊れていないかを確かめる。**行が 4 本から 5 本に増えたので、
16:9 の枠と `#slide-canvas` の内側に収まっているかが一番の確認点。**

## 対象

`claude_memo.html` と `CLAUDE.md`（`git diff HEAD` で差分を見る）。

1. スライド 17 のカードを 4 行から 5 行にした（`fa-toolbox` の行を末尾に追加）。
   行が増える分、`space-y` を 1.1cqw → 0.8cqw、`mb` を 1.4cqw → 1.1cqw、
   各行の `padding` を 1.1cqw → 0.95cqw に詰めた
2. ナレーションを書き直し、`duration` を 22 → 23 にした
3. `CLAUDE.md` の合計秒数を 316 → 317 に直した

## 完了条件

- **スライド 17 のナレーションの実測が `duration: 23` と合っている**
  （測り方は下記）。**読み上げ用の文字列が 180 字を超えていないこと**。
  超えると Online TTS で末尾が切れる。実測で 174 字のはずだが、確かめること
- `duration` の合計が 317 秒で、`CLAUDE.md` の記述と一致している
  （`formatTime(317)` は `5:17`）
- JS エラーが出ない。送りと再生が動く（17 枚）
- **レイアウトのはみ出しが変更前から増えていない。**
  **スライド 17 を表示した状態**で 4 条件を測ること:
  PC 1280x800 / 横持ち 844x390 の通常とフルスクリーン /
  縦持ち 390x844 のフルスクリーン
- **`#slide-canvas` の内側でカードが見切れていないこと**（5 行すべて）。
  `#slide-canvas` は `overflow-hidden` なので、ページ全体のはみ出しが
  0 でも中で切れることがある

## 使い回せるもの

**ゼロから組み直さないこと。**

- `archives/agents/TODO-029/layout-check.mjs` — 前後比較の本体
- `archives/agents/TODO-025/internal-overflow-check.mjs` — `#slide-canvas` の
  内部見切れを測るもの

どちらも「スライド 17 を表示してから測る」ように直して使う。

## 測り方（`duration`）

`/tmp/claude-649/-net-fs-vol0-home-localhost-1-ytani-ytani-public-html-claude-memo/0c76b96c-b599-4dcd-becf-a00170c1141d/scratchpad/measure.py`
に測定スクリプトがある。`python3 measure.py 17` でスライド 17 を測れる。
読み上げ用の文字数と、180 字で切れたかどうかも出る。

## やらないこと

**コードは直さない。** 見つけたことを報告するだけ。

## 報告

`archives/agents/TODO-026/verifier-report.md` に書く。
**返事は 5 行以内**。はみ出しの px と実測秒数は数字で書くこと。

## 目安

15〜25 分。
