# TODO-001 verifier 報告（2 巡目・スクロール修正の最終確認）

playwright-core（headless Chromium、`~/.cache/ms-playwright/chromium-1234`）で
実際にブラウザを動かして確認した。スクリプトはリポジトリ外の scratchpad
（`/tmp/claude-649/.../scratchpad/rv2/`）に置いた。コミットしていない。

## 確認項目ごとの結果

### A1. スライド切替でページがスクロールしない — ○

`#next-btn` を 5 回クリック（390x844 / 1280x800 の両方）した間、
`window.scrollY` は常に `0` のまま。

**注意点（検証方法の落とし穴）**: 最初 `page.click()`（Playwright の実クリック、
要素が画面外だと自動でスクロールさせる）でチャプター一覧の最後の項目
（17 番目）をクリックしたところ `window.scrollY` が `217` に変化したため、
一瞬「退行では」と疑った。しかし `element.click()` をページ内 JS から直接
呼ぶ（Playwright の actionability による自動スクロールを介さない）方式で
同じ操作をやり直すと `window.scrollY` は常に `0` のままだった。
つまり先の `217` は Playwright 自身の「クリック前に要素を画面内へスクロールする」
挙動によるもので、アプリのコードが原因ではない。この区別を付けた上での
結論として、アプリの `scrollPlaylistIntoView()` はページをスクロールさせて
いないと判断した。

自動再生（`playbackLoop`）は `updatePlaylistSelection()` を経由して
`next-btn` と同じコードパスを通るため、別途の検証は行っていない
（コードの経路が同一であることは `claude_memo.html:1530-1543` を読んで確認）。

### A2. チャプター一覧内で再生中の項目が見える位置までスクロールする — ○

390x844 で `#playlist-items` の内部 `scrollTop` を実測。

| クリックした項目 | 内部 scrollTop |
|---|---|
| 0（1 番目） | 0 |
| 5 | 0 |
| 10（11 番目） | 57 |
| 16（17 番目・最後） | 333 |
| 0 に戻す | 0 |

box の `scrollHeight=774` / `clientHeight=441` で、17 項目が全部は
収まらない高さ。クリックした項目は毎回 box の可視範囲内
（`itemTop >= boxTop` かつ `itemBottom <= boxBottom`、誤差 1px 以内）に
入ることを確認した。

### A3. PC（1280x800）でも 1・2 が成り立ち、退行していない — ○

1280x800 でも `window.scrollY` は次スライド 5 回・項目 0/10/16 クリックの
全パターンで `0` のまま。PC では一覧が画面内に収まる（`boxTop=151,
boxBottom=592`）ため内部スクロールもほぼ起きないが、退行は無い。

### A4. 一覧の一番上（1 番目）・一番下（17 番目）で破綻しない — ○

上記 A2 の表のとおり、0 番目・16 番目とも例外やエラー無く動作し、
`console.error` / `pageerror` は 0 件。

## B. 3 巡目の修正の再確認

### 5. 幅 360/390/430/767/768/1280px × 全 17 スライドではみ出し無し — ○

各幅で `#next-btn` を 17 回押し、`#slide-canvas` の `scrollWidth/Height`
が `clientWidth/Height` を超えるケースと、`document.documentElement.scrollWidth
> innerWidth`（横スクロール）を全 102 通り（6 幅 × 17 スライド）で確認。
問題 0 件、console エラー 0 件。

### 6. PC が HEAD と見た目が同じ（スクロールバー表示、フルスクリーン出入りで横ずれ無し） — ○

`ignoreDefaultArgs: ['--hide-scrollbars']` で起動し、`git show HEAD:claude_memo.html`
と現在のファイルを同条件（1280x800）で比較。フルスクリーンに入る前・
入った後・Esc で出た後の 3 時点で `#player-viewport` の矩形、`header` の幅、
`document.documentElement.clientWidth` を測定した。

HEAD と今回とで、3 時点すべて完全一致（例: 入る前 `pv={x:24,y:89,width:918,
height:516.375}`、入った後 `pv={x:0,y:40,width:1280,height:720}`、
`clientWidth` は前後とも常に 1280）。横ずれは無い。

### 7. スマホ縦のフルスクリーンで字幕が枠の下に出て重ならないこと。暗幕タップで閉じ、スライド・字幕タップでは閉じないこと — ○

390x844、字幕表示 ON でフルスクリーンに入り、`#viewport-frame`
（`top:312.3, bottom:531.7`）と `#subtitle-banner`
（`top:543.7, bottom:641.2`）の矩形を実測。重なり判定（区間の交差）は
`false`。間隔は約 12px（`margin-top: 0.75rem` どおり）。

タップの区別は `page.touchscreen.tap(x, y)` で実際の画面座標を叩いて確認
（要素への合成イベントではなく、実座標でのタップ）。

- 枠の中央（195, 400）をタップ → `is-fullscreen` は `true` のまま（閉じない）
- 暗幕の帯（195, 10。枠の上、`top:312` より上の暗い領域）をタップ →
  `is-fullscreen` が `false` に変わる（閉じる）

### 8. コンソールにエラーが出ないこと — ○

上記すべての検証（6 幅 × 17 スライド、PC/HEAD 比較、モバイルフルスクリーン、
タップ操作）を通じて `console.error` / `pageerror` は一貫して 0 件。

## 変更されたファイルと指示との対応

`git diff --stat`:
- `claude_memo.html`（269 行変更）— 指示の対象。差分の中身を通読し、
  実装者報告（`implementer-report-3.md`）の記述と実際の diff が一致することを
  確認した（`#viewport-stage` の新設、レターボックスの移設、暗幕タップの
  ハンドラ、`scrollPlaylistIntoView()` の追加など）
- `CLAUDE.md`（27 行変更）— `slideData` 439 行目・`playbackLoop` 手前
  1098 行目・`playlist-count` 420 行目と、実測の行番号が一致することを
  `grep -n` で確認した。追記内容も diff の実装と食い違わない
- `TODO.md`（8 行追加）— 実機で見つかった別件（スクロールの件、
  音声が途中で切れる件）の追記。コードの変更ではないので今回の確認範囲外だが、
  記述内容自体に矛盾は無い

指示の範囲外のファイルは変更されていない。

## 確かめられなかったこと・判断が要る点

- 実機（iOS Safari / Android Chrome）は未検証（デスクトップ Chromium のみ）。
  TODO.md に追記された「Android Chrome で見つかった」件（ページスクロール、
  音声の途切れ）のうち、スクロールの件は今回の修正で解消していることを
  ヘッドレス環境で確認したが、実機での再現確認はできていない
- 自動再生（`playbackLoop`）経由でのスライド送りは、コードパスが
  `next-btn` と同一であることの確認に留め、実際に自動再生を走らせての
  実測はしていない（`speechSynthesis` の `end` イベント待ちなどが絡み、
  ヘッドレス環境では安定して再現しない可能性があるため）
- 横向き（landscape）は指示どおり範囲外として未確認
