# TODO-026 検証報告

## 結論

**要修正あり。** 横持ち 844x390 フルスクリーンで `#slide-canvas` の内側に
9px の見切れが新たに発生している。他の完了条件はすべて満たしている。

## 検証したこと

### 1. ナレーションの実測（`archives/agents/TODO-026/.../measure.py 17` 相当）

`measure.py` に測定スクリプトがあったのでそのまま使用（作り直していない）。

```
slide 17: 原文 162字 / 読み 174字 / 実測 32.640s / 1.4倍速 23.31s -> duration: 23
```

- 実測 `duration: 23` は `claude_memo.html` の `duration: 23` と一致
- 読み上げ文字列は **174字**（180字以内。TTS で切れない）

### 2. `duration` 合計

```
grep -oP "duration:\s*\K[0-9]+" claude_memo.html | awk '{s+=$1} END {print s, NR}'
→ 317 17
```

17 枚の合計は **317 秒**。`CLAUDE.md` の記述（317）と一致。
`formatTime(317)` を Node で確認 → `5:17`（一致）。

（別途 `#total-time-display` を実測すると `5:51` になるが、これは
`slideSpan = duration + pauseSeconds` で 1 スライドごとにポーズ秒数
（既定 2 秒 × 17 枚 = 34 秒）を足した表示用の合計で、`duration` の単純合計
とは別物。TODO-026 の変更前後で計算式は変わっておらず、今回の不具合では
ない）

### 3. JS エラー・送り/再生（Playwright, PC 1280x800）

```
total-slides= 17
slide-num after 16 next= 17
total-time-display= 5:51
CONSOLE_ERRORS: []
```

コンソールエラー無し。17 枚への送り、play/pause ボタンの操作も問題無し。

### 4. ページ全体のはみ出し（スライド 17 表示、4 条件、前後比較）

`archives/agents/TODO-029/layout-check.mjs` の測定部分を、
「スライド 17 まで送ってから測る」ように直して使用
（`/tmp/verify064/layout-check-17.mjs`。関数確認部分は今回の主眼で
ないため省き、はみ出し測定のみ残した）。

before は `git show HEAD:claude_memo.html`、after は作業ツリーを
それぞれ別ポート（18900 / 18899）でローカル配信して比較。

```
--- PC 1280x800 ---            before: X=0px Y=0px   after: X=0px Y=0px
--- 横持ち 844x390 通常 ---      before: X=0px Y=841px after: X=0px Y=841px
--- 横持ち 844x390 フルスクリーン ---
                                before: X=0px Y=381px after: X=0px Y=381px
--- 縦持ち 390x844 フルスクリーン ---
                                before: X=0px Y=0px   after: X=0px Y=0px
```

4 条件すべて **差分 0px**。ページ全体のはみ出しは変更前から増えていない。

### 5. `#slide-canvas` 内側の見切れ（5 行すべて、4 条件、前後比較）

`archives/agents/TODO-025/internal-overflow-check.mjs` を、
「スライド 17 まで送ってから測る」ように直し、カードの検出セレクタを
`.grid` から `[class*="space-y-"] > div`（このスライドはグリッドでなく
縦積みのため）に直して使用（`/tmp/verify064/internal-overflow-check-17.mjs`
と `-before.mjs`）。

**before（4 行、HEAD）**

```
PC 1280x800        : cardCount=4  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-101.5px
横持ち 844x390 通常  : cardCount=4  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-93.1px
横持ち フルスクリーン: cardCount=4  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-72.1px
縦持ち フルスクリーン: cardCount=4  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-45.4px
```

**after（5 行、作業ツリー）**

```
PC 1280x800        : cardCount=5  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-83.2px
横持ち 844x390 通常  : cardCount=5  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-77.0px
横持ち フルスクリーン: cardCount=5  internalOverflow X=0px Y=9px  lastCard.bottom-canvas.bottom=-56.1px
縦持ち フルスクリーン: cardCount=5  internalOverflow X=0px Y=0px  lastCard.bottom-canvas.bottom=-37.5px
```

**横持ち 844x390 フルスクリーンだけ、before の 0px から after で
`internalOverflow Y=9px` に増えている。** 5 枚目のカード自体は
`canvas.bottom` より 56px 上（見た目には見切れていない）だが、
`#slide-canvas` は `overflow-hidden` なので `canvas.scrollHeight` が
`clientHeight` を 9px 超えている＝カード群のどこかが枠の内側で 9px
はみ出し、隠れて見えていない状態。他の 3 条件は差分 0px。

## 変更ファイルの範囲

`git diff HEAD` で確認。`claude_memo.html` と `CLAUDE.md` のみ変更。
依頼書に書かれた 3 点（カード追加とスペーシング調整、ナレーションと
`duration`、`CLAUDE.md` の合計秒数）以外の変更は無い。

## やらなかったこと・判断できないこと

- 9px のずれの原因箇所（どのカード/どの余白が枠の内側で膨らんでいるか）
  は特定していない。原因調査は確認担当の範囲外と判断し、実測結果だけを
  報告する
- Web Speech 側のナレーション（`toggle-voice-engine-btn` で切替）は
  今回測っていない。依頼が Online TTS の 180 字制限だったため対象外とした
- コードは直していない

## 再測定

前回指摘した 9px の内側見切れの修正（注記ボックスの文言短縮・padding
1cqw→0.8cqw・font-size 下限 0.9rem→0.8rem）を確認した。使ったスクリプトは
前回作成した `/tmp/verify064/internal-overflow-check-17.mjs`・
`layout-check-17.mjs` をそのまま再実行（作り直していない）。サーバは
`before`=`git show HEAD:claude_memo.html`（変更前は今回未変更なので前回と
同じ）、`after`=修正後の作業ツリーを 18900/18899 で再度立て直した。

### 1. `#slide-canvas` 内側の見切れ（4 条件）

```
PC 1280x800        : internalOverflow X=0px Y=0px
横持ち 844x390 通常  : internalOverflow X=0px Y=0px
横持ち フルスクリーン: internalOverflow X=0px Y=0px   ← 前回 9px から 0px に
縦持ち フルスクリーン: internalOverflow X=0px Y=0px
```

**4 条件とも 0px。** 前回 9px だった横持ちフルスクリーンも解消された。

### 2. ページ全体のはみ出し（4 条件、before/after 差分）

```
PC 1280x800        : dX=0 dY=0
横持ち 844x390 通常  : dX=0 dY=0
横持ち フルスクリーン: dX=0 dY=0
縦持ち フルスクリーン: dX=0 dY=0
```

前回測定時から**変わらず全条件で差分 0px**。

### 3. 注記ボックスの実測（文字サイズ・枠内への収まり）

`canvas.querySelector('.bg-sky-950\/60')` で注記ボックスの
`getComputedStyle().fontSize` と、`#slide-canvas` の内側にどれだけ
余裕があるか（`canvas.bottom - note.bottom` など）を測った。

```
PC 1280x800        : font-size=15.6px  bottom余裕=33.4px right余裕=25.6px left余裕=25.6px
横持ち 844x390 通常  : font-size=13.4px  bottom余裕=22.5px right余裕=22.0px left余裕=22.0px
横持ち フルスクリーン: font-size=12.8px  bottom余裕=4.3px  right余裕=19.3px left余裕=19.3px
縦持ち フルスクリーン: font-size=16.4px  bottom余裕=16.0px right余裕=11.1px left余裕=11.1px
```

4 条件とも余裕は正の値（枠内に収まっている）。文字サイズは 12.8〜16.4px で、
他のクローム要素（TODO-001 に記録がある 4.5〜5.2px の縮小経路）より
明らかに大きく、読める大きさ。横持ちフルスクリーンの下端余裕が 4.3px と
最も狭いが、はみ出してはいない。

### 再測定のまとめ

3 点とも問題無し。`#slide-canvas` 内側の見切れは解消され、ページ全体の
はみ出しも前回から変化なし、注記も読める大きさで枠内に収まっている。
