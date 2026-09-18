# TODO-011 検証報告

## 検証方法

`claude_memo.html`（変更後、作業ツリー）と `git show HEAD:claude_memo.html`
で出した変更前のファイルの両方を playwright（chromium, headless）で開き、
5 条件（横持ち通常・横持ちフルスクリーン・縦持ち通常・縦持ちフルスクリーン・
PC）× スライド3枚で `#viewport-frame` / `#player-viewport` / `#slide-canvas`
の矩形と `--vp-scale` を計測した。スクリプトは
`/tmp/.../scratchpad/verify.js`（このセッションのスクラッチパッド。
report には残していない）。measure.js.txt をベースに、複数スライド送りと
`#slide-canvas` が `#player-viewport` 内に収まっているかの判定を追加した。

終了コードは全条件で 0（例外なく実行完了）。

## 完了条件ごとの実測値

### 1. 844x390（タッチ）通常表示で下端が innerHeight 以下

- 変更前: `frame.bottom = 537`, `innerHeight = 390` → **収まっていない**（537 > 390、`fits:false`）
- 変更後: `frame.bottom = 390`, `innerHeight = 390` → **収まる**（`fits:true`、ちょうど下端一致）

3スライドとも同じ結果（slide1/2/3 で frame の矩形は同一、canvas は文字量で若干変動するが `canvasInsideVp:true`）。

### 2. 844x390 フルスクリーンが変更前と同じ大きさ（693x390）

- 変更前: `frame = {width:693, height:390}`
- 変更後: `frame = {width:693, height:390}`

一致。3スライドとも同じ。

### 3. 390x844 通常・フルスクリーン、1280x800 PC が変更前と変わらない

| 条件 | 変更前 frame | 変更後 frame |
|---|---|---|
| portrait normal | {left:16,top:65,width:358,height:201} | 同一 |
| portrait fullscreen | {left:0,top:312,width:390,height:219} | 同一 |
| PC | {left:24,top:89,width:918,height:516} | 同一 |

すべて変更前後で数値が完全一致。canvas の矩形は文字レンダリングの揺れで
1px 前後ずれるスライドがあるが、frame/vp の矩形と scale は完全一致。

### 4. --vp-scale が frame.width / 960 に追随している

全条件・全スライドで `scale` と `expectedScale`（`frame.width / 960`）が
一致（横持ち通常のみ僅かな丸め差: `0.5574055989583333` vs
`0.5572916666666666`。差は 0.0001 程度で、getComputedStyle の丸めと
実測 width の丸め誤差によるもので、追随自体はできている）。

代表値（変更後）:
- landscape normal: frame.width=535, scale=0.55741, expected=0.55729
- landscape fullscreen: frame.width=693, scale=0.72222, expected=0.72188
- portrait normal: frame.width=358, scale=0.37292, expected=0.37292（完全一致）
- portrait fullscreen: frame.width=390, scale=0.40625, expected=0.40625（完全一致）
- PC: frame.width=918, scale=0.95625, expected=0.95625（完全一致）

## 複数スライドでの本文はみ出し確認

5条件 × 3スライド、すべて `canvasInsideVp:true`（`#slide-canvas` の矩形が
`#player-viewport` の内側）。はみ出しは検出されなかった。

## 変更範囲の確認

`git status` / `git diff --stat` で `claude_memo.html` のみ変更（15行追加）。
diff の内容は `#viewport-frame` への `max-width`（vh/dvh 版の2行）と
`margin-inline: auto`、`#viewport-stage.is-fullscreen > #viewport-frame` への
`max-width: none` の追加のみで、指示された範囲と一致。他ファイルの変更なし。

## 判断できなかったこと・確認できなかったこと

- `dvh` 単位に実際に対応したブラウザでの挙動は、chromium のヘッドレス実行
  でも `dvh` は解釈されるはずだが、実機のツールバー表示/非表示に伴う
  動的な高さ変化までは再現していない（playwright はビューポート固定）。
  コメントにある「dvh 非対応ブラウザ向けの保険」という意図の検証は
  そもそも対象外と判断した。
- 843x390 以外の端末サイズ（他機種の横持ち解像度）は指示に無いため検証していない。
- 実装が正しいかの「良さ」の判断（レビュー観点）はここでは行っていない。
