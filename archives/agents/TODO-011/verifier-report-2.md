# TODO-011 検証報告（第2版: JS 実測への切り替え後）

## 検証方法

`claude_memo.html`（変更後、作業ツリー）と `git show HEAD:claude_memo.html`
を `/tmp/before.html` に出したもの（変更前）を playwright（chromium,
headless, `NODE_PATH=$(npm root -g) node ...`）で開き、指示された 7 項目を
実測した。スクリプトはスクラッチパッド
（`/tmp/claude-649/.../scratchpad/measure.js`。report には残していない）。

全実行で終了コードは 0。コンソールエラー・pageerror は全条件で 0 件
（各測定結果の `errors` 配列は常に空）。

## 1. 6 サイズ・通常表示で下端が innerHeight 以下

| サイズ | frame.bottom | innerHeight | 判定 |
|---|---|---|---|
| 844x390 | 390 | 390 | OK（ちょうど一致） |
| 667x375 | 375 | 375 | OK |
| 640x420 | 420 | 420 | OK |
| 700x420 | 420 | 420 | OK |
| 720x420 | 420 | 420 | OK |
| 767x420 | 420 | 420 | OK |

はみ出し 0（すべて `bottom - innerHeight <= 0`）。640〜767px 帯（ヘッダー折り返し
帯を含む）でも収まっている。

## 2. フルスクリーンが変更前と一致

| サイズ | 変更後 frame | 変更前 frame |
|---|---|---|
| 844x390 | {width:693, height:390} | 同一 |
| 667x375 | {width:667, height:375} | 同一 |
| 640x420 | {width:640, height:360} | 同一 |
| 700x420 | {width:700, height:394} | 同一 |
| 720x420 | {width:720, height:405} | 同一 |
| 767x420 | {width:747, height:420} | 同一 |

6 サイズすべて left/top/width/height が変更前後で完全一致。
（scrollY は前後で異なるが、フルスクリーン化で自動スクロールされた位置の違いで、
frame の矩形自体には影響していない。）

## 3. 縦持ち・PC が変更前と一致

| 条件 | 変更後 frame | 変更前 frame |
|---|---|---|
| portrait normal (390x844) | {left:16,top:65,width:358,height:201} | 同一 |
| portrait fullscreen | {left:0,top:312,width:390,height:219} | 同一 |
| PC (1280x800) | {left:24,top:89,width:918,height:516} | 同一 |

すべて完全一致。

## 4. --vp-scale が frame.width / 960 と一致

`getBoundingClientRect().width`（丸め前の実数）で再計算して比較。

| サイズ | rawWidth | --vp-scale | width/960 | 差 |
|---|---|---|---|---|
| 640x420 | 531.546875 | 0.5536946614583333 | 0.5536946614583333 | 0 |
| 720x420 | 602.65625 | 0.6277669270833334 | 0.6277669270833334 | 0 |
| 767x420 | 602.65625 | 0.6277669270833334 | 0.6277669270833334 | 0 |
| 844x390 | ~535.111 | 0.5574055989583333 | (同値) | 0 |
| 667x375 | 480 | 0.5 | 0.5 | 0 |
| 700x420 | 560 | 0.5833333333333334 | 0.5833333333333334 | 0 |

丸め前の実数で比較すると全サイズで差 0（第1版の報告にあった 0.0001 程度の
「丸め差」は、報告時に整数へ丸めた width で割ったための見かけ上の差であり、
実測（丸め前）では完全一致することを確認した）。

## 5. スクロール後に resize しても frame の大きさが変わらない

844x390、`window.scrollTo(0, 300)` 後に `resize` イベントを発火。

| | width | height |
|---|---|---|
| スクロール前 | 535 | 301 |
| スクロール後（scrollY=300 で resize 発火後） | 535 | 301 |

変化なし。コメントにある「scrollY を足して補正する」実装が効いている。

## 6. 回転相当（844x390 → 390x844 → 844x390）

| | width | height | bottom | innerHeight |
|---|---|---|---|---|
| s1 (844x390) | 535 | 301 | 390 | 390 |
| s2 (390x844) | 358 | 201 | 266 | 844 |
| s3 (844x390) | 535 | 301 | 390 | 390 |

s1 と s3 が完全一致（往復して元に戻る）。s2 は単独の 390x844 測定結果
（1. 3. 節と同値）とも一致。いずれも `bottom <= innerHeight`。

## 7. ResizeObserver が無い環境

844x390、`window.ResizeObserver` を `delete` してから読み込み。

| | frame | vp | --vp-scale | エラー |
|---|---|---|---|---|
| 変更後 | {width:796,height:448,bottom:537} | {width:960,height:540} | "" (空) | 0件 |
| 変更前 | 同一 | 同一 | "" (空) | 0件 |

変更前後で完全に同じ挙動（max-width が入らず `overflow:hidden` の保険だけが
効く旧来の見え方）。JS エラーは発生していない。`setupViewportScale()` は
`if (!frame || !('ResizeObserver' in window)) return;` で早期 return する
実装で、それが effective に確認できた。

## 変更範囲の確認

`git status --short` は `claude_memo.html` のみ変更（他は
`archives/agents/TODO-011/` の新規ファイルのみ、これは報告用）。
`git diff --stat` は 38 追加 / 2 削除で、指示にある「CSS の固定値をやめて
JS 実測にする」範囲（`#viewport-frame` の CSS から `max-width` 系を削って
`margin-inline: auto` を残す／`setupViewportScale()` の書き換え）と一致。
他ファイルの変更なし。

## 判断できなかったこと・確認できなかったこと

- 実装の「良さ」（レビュー観点、コメントの正確さなど）は確認していない。
- 6 サイズ以外の端末解像度、実機での dvh/ツールバー表示変化に伴う動的挙動は
  対象外（playwright はビューポート固定のため再現できない）。
- MutationObserver によるフルスクリーン切替時の追随は、フルスクリーンの
  値が変更前と一致していることから間接的に確認できているが、
  「切り替えの瞬間に一度不整合な値が出ないか」のような過渡的な状態までは
  見ていない。
