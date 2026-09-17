# TODO-001 implementer 報告

対象は `claude_memo.html` のみ。他のファイルは触っていない。コミットもしていない。

## 変更したファイルと箇所

`claude_memo.html`（変更後の行番号）

- **130-133** `#viewport-frame` を新設。PC では `width: 100%` だけの素通しの箱。
- **135-192** `@media screen and (max-width: 640px)` を書き換え
  - 136-139 `#viewport-frame`: `position: relative; aspect-ratio: 16 / 9;`
  - 141-151 `#player-viewport`: `position: absolute; top/left: 0; width: 960px;
    height: 540px; max-width: none; padding: 1.5rem;
    transform: scale(var(--vp-scale, 1)); transform-origin: top left;`
  - 153-155 `#slide-canvas .overflow-x-auto .inline-flex { flex-shrink: 0 }` は指示どおり残した
  - 159-175 `#viewport-frame:has(> .pseudo-fullscreen)`: 擬似フルスクリーンは
    外枠の方を `position: fixed` の 16:9 レターボックスにする
  - 177-190 `.video-viewport.pseudo-fullscreen` のモバイル上書き: 中身は
    `position: absolute` の 960x540 のまま据え置く（`transform` は生かす）
  - 削除したもの（指示どおり）: `.video-viewport { aspect-ratio: auto; min-height: 60vh }`、
    `#slide-canvas` の `.grid-cols-2/3/4` 段数変更、`h1.whitespace-nowrap` の折り返し、
    `#subtitle-banner { position: static }`、旧モバイル用 `pseudo-fullscreen` 上書き
- **231-232, 276** `#player-viewport` を `<div id="viewport-frame">` で包んだ
- **1651-1665** `setupViewportScale()` を追加。`ResizeObserver` で外枠の幅を見て
  `--vp-scale = clientWidth / 960` を外枠に設定する（`ResizeObserver` が無い環境は
  `resize` イベントにフォールバック）
- **1668** `startApp()` の先頭で `setupViewportScale()` を呼ぶ

## 判断した点（指示に無かったもの）

1. **セレクタを `.video-viewport` ではなく `#player-viewport` にした。**
   この div には Tailwind の `relative` と `p-4` が付いている。Tailwind CDN は
   実行時に `<style>` を head へ追加するので、クラス同士（詳細度が同じ）では
   Tailwind が勝ち、`position: absolute` が効かない。id セレクタで確実に上書きした。
2. **モバイルで `padding: 1.5rem` を明示した。** Tailwind の `p-4 md:p-6` は
   ビューポート幅で切り替わるため、縮小表示では PC（`md:p-6` = 1.5rem）と
   余白が変わってしまう。PC の見た目をそのまま縮小する方針に合わせた。
3. **擬似フルスクリーンは「外枠を fixed にする」方式にした。**
   `.video-viewport` 自身を fixed にすると論理幅が実機の幅（360px 等）に戻り、
   container query の基準が縮んで clamp() の下限があふれる（元の問題の再発）。
   外枠を画面いっぱいの 16:9 レターボックスにすれば、中身は 960x540 のまま
   `--vp-scale` で縮小され、`ResizeObserver` が外枠を見ているので縮小率も自動で
   追随する。`:has()` を使用（Chrome 105+ / Safari 15.4+ / iOS 15.4+）。
4. **フルスクリーン時に外枠へ `box-shadow: 0 0 0 100vmax rgba(2,6,23,.92)` を足した。**
   縦画面では 16:9 の上下が余り、背後のチャプター一覧が透けて見えて壊れて見えるため。
   1 行で済む範囲の追加。
5. **包んだ div の中身は再インデントしていない。** 70 行の差分を避けるため、
   インデントは元のまま。整えたい場合は別途。

## 検証

`playwright-core` + キャッシュ済み Chromium（`~/.cache/ms-playwright/chromium-1234`）で
ヘッドレス実行。スクリプトは scratchpad に置いた（リポジトリには入れていない）。

| 検証 | 結果 |
|------|------|
| 360x800 / 390x844 / 430x932 縦画面: 外枠が 16:9 で幅いっぱい、`--vp-scale` は 0.342 / 0.373 / 0.415 | 成功（終了コード 0） |
| 全 17 スライドで `#slide-canvas` の `scrollHeight == clientHeight`（縦のはみ出し無し）、`document.scrollWidth == innerWidth`（横スクロール無し）@390px | 成功 |
| PC 1280x800 / 1440x900 / 1024x768 / 768x900 のフルページ画像を変更前後で MD5 比較（アニメーションは停止して撮影） | **4 件すべて IDENTICAL**（終了コード 0） |
| 擬似フルスクリーン: 390x844・360x800 で外枠が幅いっぱいの 16:9、中身のはみ出し無し。740x360・1280x800 は従来どおり viewport が fixed | 成功 |
| Escape で解除、再生（0:00→0:02）、次/前スライド（01→02→01）、字幕表示切替 を 4 サイズで実行 | 成功 |
| 390x844 →（回転）844x390 → 360x800 のリサイズで `--vp-scale` が 0.373 → 0.829 → 0.342 と追随 | 成功 |

画像は `~/tmp/playwright-mcp/todo001-*.png` に保存した
（`todo001-390x844.png`、`todo001-fs-390x844.png`、`todo001-360-slide7.png` など）。

注: `#player-viewport` 自体は `scrollHeight > clientHeight` になるが、これは背景の
装飾（`-top-24 -right-24` のぼかし円）が枠外に出ているためで、変更前も同じ
（`overflow: hidden` で隠れている）。中身のはみ出しではない。

## 範囲外だが気づいたこと

- **幅 641〜660px あたりでスライド 4・13・17 の中身が数 px はみ出す。**
  変更前後で同じ数値（4:+14px、13:+14px、17:+3px）なので既存の問題。
  縮小表示のブレークポイントを 640px から 768px に上げれば一緒に直るが、
  今回の指示の範囲外なので触っていない。
- ヘッダーが `sticky top-0 z-50` なので、スクロールするとスライド上端に
  かぶる。これも変更前と同じ挙動（枠が低くなった分、かぶる機会は減る）。
- 縦画面では通常表示もすでに幅いっぱいの 16:9 なので、擬似フルスクリーンに
  しても見える大きさはほとんど変わらない（周りが暗くなるだけ）。仕様として
  問題なければそのままでよい。
