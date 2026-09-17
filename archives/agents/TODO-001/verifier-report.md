# TODO-001 verifier 報告

実装者の報告を鵜呑みにせず、playwright-core（headless Chromium、ローカルにキャッシュ済み
`~/.cache/ms-playwright/chromium-1234`）で独自に確認した。スクリプトはリポジトリ外の
scratchpad に置いた（コミットしていない）。

## 確認項目ごとの結果

### 1. 幅 360 / 390 / 430px の縦画面、全 17 スライド — ○

`#viewport-frame` の実測比率はすべて 1.7778（=16/9）と一致。
全 17 スライド × 3 幅（計 51 通り）で `#next-btn` をクリックしながら計測し、
`document.documentElement.scrollWidth > innerWidth`（横スクロール発生）は
すべて `false`。`#slide-canvas` の `scrollWidth > clientWidth` も全て `false`。

スクリーンショットでも目視確認（`portrait_390.png` 通常表示、
`portrait_430_slide8.png` 表がある重めのスライド8）。枠が幅いっぱいで
中身のはみ出しは無い。

### 2. 幅 1280px で変更前と見た目が同じこと — ○

`git stash` で変更前に戻し、幅 1280x800 のフルページスクリーンショットを撮影
（`before_1280.png`）。変更を戻して（`git stash pop`）同条件で再撮影
（`after_1280.png`）。

- `#viewport-frame` の bounding box は前後で完全一致
  （`{"width":918,"height":516.375,"top":89,"bottom":605.375}`）。
- 画像は MD5 では不一致だったが、差分の bbox は `(49,126)-(59,136)` の
  10x10px のみ。切り出して見比べると、ヘッダーの緑色の点
  （`animate-pulse` のアニメーション中のドット、`bg-lime-400 animate-pulse`）
  の明滅タイミングの違いで、レイアウトの差ではない
  （`before_crop.png` / `after_crop.png` を目視、色の濃淡がわずかに違うだけで
  位置・大きさは同一）。

結論: PC 幅での見た目に変化は無い。

### 3. 縦画面（390x844）での操作 — ○

- 再生: `#play-btn` クリックで `#play-icon` のクラスが `fa-play` →
  `fa-pause` に変化。動作している。
- 次/前スライド: `#slide-num` が `01 → 02（次）→ 01（前）` と変化。
- 字幕表示切替: `#toggle-caption-btn` クリックで `#subtitle-banner` の
  `hidden` クラスが `true → false` に変化。
- 擬似フルスクリーン: `#fullscreen-btn` クリックで `#player-viewport` に
  `pseudo-fullscreen` クラスが付与され、`#viewport-frame` が画面中央に
  16:9 のレターボックス（`width:390 height:219.375` ≒ 比率1.778）で表示。
  スクリーンショット `portrait_390_fs.png` でも、枠外が暗く落ちて
  レターボックス表示になっているのを確認。
- Esc で閉じる: `Escape` キー押下後、`pseudo-fullscreen` クラスが外れることを確認。

### 4. 横向き（740x360）で破綻しないこと — △（既存の挙動、今回の変更とは無関係）

このサイズは `max-width: 640px` のメディアクエリに掛からないため、今回変更した
モバイル用 CSS は一切効かない（素の PC 用 `.video-viewport { aspect-ratio: 16/9 }`
がそのまま使われる）。実測では枠が `708x398px` になり、ビューポート高 360px を
超えて上にはみ出す（`top: -268px`）。

**これは今回の変更による regression ではない。** `git stash` で変更前の
コードに戻し、同じ 740x360 で計測したところ、枠のサイズ・位置は
`{"width":708,"height":398.25,"top":-268,"bottom":130.25}` と変更後と完全に
同一だった。横スクロール（`docScrollW > innerWidth`）も前後とも発生していない。
縦にはみ出して要スクロールになるのは、640px を超える横長で低い画面という
特殊なケースの既存の挙動であり、今回の指示（「16:9 の枠が横幅いっぱいに
収まること」「破綻しないこと」）の範囲では、少なくとも横方向の破綻・
regression は無い。縦方向にスクロールが必要になる点を「破綻」と見るかどうかは
判断が要る（既存の挙動なので今回の項目の対象外と考えるのが妥当だとは思うが、
明示の合意はない）。

### 5. コンソールエラー — ○

1280x800 / 390x844 / 360x800 / 430x932、および縦画面 51 通りの操作、
横画面 740x360、フルスクリーン操作を含め、`console.error` / `pageerror` は
すべて `(none)`。

## 変更されたファイル

`git status` / `git diff --stat`: `claude_memo.html` のみ変更（71 insertions,
27 deletions）。指示の対象範囲と一致している。未追跡の `archives/` は
今回の作業記録なので対象外。

## 確かめられなかったこと・判断が要る点

- 項目4（740x360 横向き）は「破綻しない」の意味次第で判定が変わる。
  横方向の破綻・regression は無いが、縦にコンテンツがはみ出しスクロールが
  必要になる点は変更前から存在する挙動。これを今回の項目の対象とするかは
  管理者の判断が要る。
- 音声・読み上げ関連は範囲外のため未確認（TODO-002 の担当）。
- `:has()` セレクタへの依存など、実装者報告にある古いブラウザでの非対応は
  未検証（今回の確認環境は最新 Chromium のみ）。
