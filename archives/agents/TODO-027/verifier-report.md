# TODO-027 検証報告

## 結論

**問題無し。** 完了条件はすべて満たしている。

## 変更ファイルの範囲

`git diff HEAD` で確認。`claude_memo.html`（スライド 1 の `<p>`・情報ボックス・
`narration`・`duration`）と `CLAUDE.md`（合計秒数）のみ変更。依頼書に書かれた
4 点以外の変更は無い。

## 検証したこと

使ったスクリプトはすべて TODO-026 で作った `/tmp/verify064/` 内のものを
「表示するスライドを 1 に変える」だけ直して使い回した（作り直していない）。
`layout-check-17.mjs` と `internal-overflow-check-17.mjs` は
`for (let i = 0; i < 16; i++)` を `< 0` に変更（スライド 1 は送り不要）。

### 1. ナレーションの実測

`measure.py 1` を実行。

```
slide 1: 原文 110字 / 読み 107字 / 実測 22.344s / 1.4倍速 15.96s -> duration: 16
```

- 実測 `duration: 16` は `claude_memo.html` の `duration: 16` と一致
- 読み上げ文字列は **107字**（180字以内。依頼書の想定どおり）

### 2. `duration` 合計

```
grep -oP "duration:\s*\K[0-9]+" claude_memo.html | awk '{s+=$1} END {print s, NR}'
→ 315 17
```

17 枚の合計は **315 秒**。`CLAUDE.md` の記述（315）と一致。
`formatTime(315)` を Node で確認 → `5:15`（一致）。

### 3. JS エラー・送り/再生（Playwright, PC 1280x800）

```
total-slides= 17
slide-num after 16 next= 17
total-time-display= 5:49
CONSOLE_ERRORS: []
```

コンソールエラー無し。17 枚への送り、play/pause も問題無し。

### 4. ページ全体のはみ出し（スライド 1 表示、4 条件、TODO-026 コミット後 vs 今回）

`before` = `git show HEAD:claude_memo.html`（TODO-026 コミット後）、
`after` = 作業ツリー。`layout-check-17.mjs` を実行。

```
PC 1280x800        : before X=0px Y=0px    after X=0px Y=0px    dX=0 dY=0
横持ち 844x390 通常  : before X=0px Y=885px  after X=0px Y=885px  dX=0 dY=0
横持ち フルスクリーン: before X=0px Y=425px  after X=0px Y=425px  dX=0 dY=0
縦持ち フルスクリーン: before X=0px Y=0px    after X=0px Y=0px    dX=0 dY=0
```

4 条件すべて **差分 0px**。ページ全体のはみ出しは変更前から増えていない
（横持ち通常・フルスクリーンの Y はページ自体の下に続くコンテンツによる
既存のスクロール分で、スライド 1 固有の変化ではない）。

### 5. `#slide-canvas` 内側の見切れ（`<br>` で 2 行になった本文と見出しの
`whitespace-nowrap`）

依頼書にあった「とくに横持ち 844x390 フルスクリーンは、TODO-026 で 9px の
見切れが出た条件」に注意して測定。`internal-overflow-check-17.mjs`
（スライド 1 用に送り回数を 0 にしたもの）と、見出し・本文に絞った
専用チェック（`/tmp/verify064/slide1-final-check.mjs`）の 2 本で測った。

```
--- PC 1280x800 ---
  p.bottom - canvas.bottom = -151.8px（canvas 内側に収まる）
  h1 右はみ出し = -281.3px  左はみ出し = -34.7px  h1.scrollWidth - clientWidth = 0.0px
  canvas internalOverflow X=0px Y=0px
--- 横持ち 844x390 通常 ---
  p.bottom - canvas.bottom = -126.4px
  h1 右はみ出し = -240.2px  左はみ出し = -29.8px  scrollW-clientW = 0.0px
  canvas internalOverflow X=0px Y=0px
--- 横持ち 844x390 フルスクリーン（前回 9px が出た条件） ---
  p.bottom - canvas.bottom = -104.3px
  h1 右はみ出し = -211.6px  左はみ出し = -25.7px  scrollW-clientW = 0.0px
  canvas internalOverflow X=0px Y=0px
--- 縦持ち 390x844 フルスクリーン ---
  p.bottom - canvas.bottom = -66.0px
  h1 右はみ出し = -118.5px  左はみ出し = -14.8px  scrollW-clientW = 0.0px
  canvas internalOverflow X=0px Y=0px
```

**4 条件とも `internalOverflow` は X/Y ともに 0px。** `p.bottom - canvas.bottom`
と `h1` の左右はみ出しもすべて負の値（＝枠の内側に収まっている）。
`h1.scrollWidth - clientWidth` も全条件 0px なので、`whitespace-nowrap` に
よる横方向のはみ出しは無い。

`<p>` が実際に 2 行で描画されていることは、`getBoundingClientRect().height`
と `getComputedStyle().lineHeight` の比（PC で 78.9px / 39.5px ≈ 2.0）で
別途確認済み。縦持ちフルスクリーンだけこの比が transform スケールの影響で
崩れる（`lineHeight` は変形前の CSS 値、`getBoundingClientRect` は変形後の
実測値のため単純な比では測れない）ので、この条件は `pBottomOverflow` の
値（-66.0px、収まっている）で判断した。

## やらなかったこと・判断できないこと

- `p` の行数を transform スケール下で厳密に「2 行」と数値だけで確認する
  方法は今回作れなかった（上記のとおり `lineHeight` 比は縦持ち
  フルスクリーンでは参考にならない）。目視でのスクリーンショット確認は
  していない。ただし `p.bottom - canvas.bottom` が全条件で負であることから、
  2 行になっても内側に収まっていると判断した
- コードは直していない
