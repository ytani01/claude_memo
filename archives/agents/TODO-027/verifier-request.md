# TODO-027 検証依頼

## 目的

スライド 1（表紙）を掴みに書き直したことで、表示と秒数が壊れていないかを
確かめる。**本文が 1 行から 2 行（`<br>` で改行）に増えたので、
枠と `#slide-canvas` の内側に収まっているかが確認点。**

## 対象

`claude_memo.html` と `CLAUDE.md`（`git diff HEAD` で差分を見る）。

1. 本文の `<p>` を「ネット上の情報をもとに、自分なりにアレンジして
   試行錯誤中です。」から「常時起動の Raspberry Pi に、出先のスマホから
   一言。`<br>`それだけでタスクが最後まで進みます。」に差し替えた（2 行）
2. 下の情報ボックスを「使い方の一例としてご紹介させていただきます | 2026-09」
   から「ネット上の情報をもとにした自己流の一例です | 2026-09」に
3. ナレーションを書き直し、`duration` を 18 → 16 にした
4. `CLAUDE.md` の合計秒数を 317 → 315 に直した

## 完了条件

- **スライド 1 のナレーションの実測が `duration: 16` と合っている**。
  読み上げ用の文字列が 180 字以内であること（実測 107 字のはず）
- `duration` の合計が 315 秒で、`CLAUDE.md` の記述と一致
  （`formatTime(315)` は `5:15`）
- JS エラーが出ない。送りと再生が動く（17 枚）
- **レイアウトのはみ出しが変更前から増えていない。スライド 1 を表示した
  状態**で 4 条件: PC 1280x800 / 横持ち 844x390 の通常とフルスクリーン /
  縦持ち 390x844 のフルスクリーン
- **`#slide-canvas` の内側で見切れていないこと。**
  `<br>` で 2 行になった本文と、見出し（`whitespace-nowrap` が掛かっている）に
  注意。とくに横持ち 844x390 フルスクリーンは、TODO-026 で 9px の
  見切れが出た条件

## 使い回せるもの

**ゼロから組み直さないこと。** TODO-026 で「スライド 17 を表示してから測る」
形に直したスクリプトが `/tmp/verify064/` に残っているはず
（`layout-check-17.mjs`、`internal-overflow-check-17.mjs`）。
**表示するスライドを 1 に変えるだけ**で使える。
元は `archives/agents/TODO-029/layout-check.mjs` と
`archives/agents/TODO-025/internal-overflow-check.mjs`。

## 測り方（`duration`）

`/tmp/claude-649/-net-fs-vol0-home-localhost-1-ytani-ytani-public-html-claude-memo/0c76b96c-b599-4dcd-becf-a00170c1141d/scratchpad/measure.py`
に測定スクリプトがある。`python3 measure.py 1` でスライド 1 を測れる。

## やらないこと

**コードは直さない。** 見つけたことを報告するだけ。

## 報告

`archives/agents/TODO-027/verifier-report.md` に書く。
**返事は 5 行以内**。はみ出しの px と実測秒数は数字で書くこと。

## 目安

10〜20 分（スクリプトが残っているので短いはず）。
