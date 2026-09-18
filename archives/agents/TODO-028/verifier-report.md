# TODO-028 検証報告

## 結論

**問題無し。** 完了条件はすべて満たしている。

## 変更ファイルの範囲

`git diff HEAD` で確認。`claude_memo.html`（スライド 16 の 1 枚目カードの
`<p>`・`narration`・`duration`）と `CLAUDE.md`（合計秒数）のみ変更。
依頼書に書かれた 3 点以外の変更は無い。カードの枚数（2 枚のまま）、
行数も増えていない。

## 検証したこと

使ったスクリプトは `/tmp/verify064/` の `layout-check-17.mjs` と
`internal-overflow-check-17.mjs`（TODO-026・027 で使い回してきたもの）。
表示するスライドを 16 に変えるため、送り回数を `for (let i = 0; i < 15; i++)`
に直しただけ（作り直していない）。カード検出セレクタは、スライド 16 が
`space-y-` ではなく `.grid` の 2 枚カード構成なので `.grid > div` に直した
（スライド 17 用の `space-y-` セレクタのままでは 0 件になるため）。

### 1. ナレーションの実測

`measure.py 16` を実行。

```
slide 16: 原文 130字 / 読み 127字 / 実測 24.528s / 1.4倍速 17.52s -> duration: 18
```

- 実測 `duration: 18` は `claude_memo.html` の `duration: 18` と一致
- 読み上げ文字列は **127字**（180字以内。依頼書の想定どおり）

### 2. `duration` 合計

```
grep -oP "duration:\s*\K[0-9]+" claude_memo.html | awk '{s+=$1} END {print s, NR}'
→ 316 17
```

17 枚の合計は **316 秒**。`CLAUDE.md` の記述（316）と一致。
`formatTime(316)` を Node で確認 → `5:16`（一致）。

### 3. JS エラー・送り/再生（Playwright, PC 1280x800）

```
total-slides= 17
slide-num after 16 next= 17
total-time-display= 5:50
CONSOLE_ERRORS: []
```

コンソールエラー無し。17 枚への送り、play/pause も問題無し。

### 4. ページ全体のはみ出し（スライド 16 表示、4 条件、前コミット vs 今回）

`before` = `git show HEAD:claude_memo.html`（TODO-027 コミット後）、
`after` = 作業ツリー。

```
PC 1280x800        : before X=0px Y=0px    after X=0px Y=0px    dX=0 dY=0
横持ち 844x390 通常  : before X=0px Y=841px  after X=0px Y=841px  dX=0 dY=0
横持ち フルスクリーン: before X=0px Y=381px  after X=0px Y=381px  dX=0 dY=0
縦持ち フルスクリーン: before X=0px Y=0px    after X=0px Y=0px    dX=0 dY=0
```

4 条件すべて **差分 0px**。ページ全体のはみ出しは変更前から増えていない。

### 5. `#slide-canvas` 内側の見切れ（4 条件）

```
PC 1280x800        : cardCount=2  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-83.3px
横持ち 844x390 通常  : cardCount=2  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-66.6px
横持ち フルスクリーン: cardCount=2  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-31.9px
縦持ち フルスクリーン: cardCount=2  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-37.4px
```

4 条件とも `internalOverflow` は X/Y ともに 0px。カードは 2 枚のまま検出
され、`lastCard.bottom - canvas.bottom` もすべて負（枠の内側に収まっている）。
依頼書のとおり、本文が 2 字短くなっただけで、見切れは発生していない。

## やらなかったこと・判断できないこと

特になし。コードは直していない。
