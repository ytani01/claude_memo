# TODO-001 implementer 報告（3 巡目）

2 巡目のレビュー（`reviewer-report-2.md`）の指摘を、指示された方針どおりに直した。
コミットはしていない。

## 方針（指摘 2〜7 をまとめて解く形）

レターボックスを **`#viewport-stage`（ラッパー）自身**に持たせた。
これまでは PC が `.video-viewport.pseudo-fullscreen`、768px 未満が
`#viewport-frame.is-fullscreen`、字幕が `min()` の計算、と 3 か所が
それぞれ別にレターボックスを算出していた。ラッパーが画面中央の 16:9 の箱に
なると、中身も字幕もその箱を基準に置けるので、`100vh` からの逆算が要らなくなる。

- PC: ラッパーがレターボックス、`.video-viewport.pseudo-fullscreen` は
  その中で `absolute; inset: 0`。字幕は Tailwind の
  `absolute bottom-3 left-4 right-4` のまま＝枠に重なる（HEAD と同じ位置）
- 768px 未満: ラッパーがレターボックス、`#viewport-frame` はその中で
  `width:100%; aspect-ratio:16/9`＝ラッパーと同じ大きさ。中身は
  `--vp-scale` で縮む既存の仕組みのまま。字幕は `top: 100%` で枠の下

`is-fullscreen` を付ける先も枠からラッパーへ移したので、
`#viewport-frame` の `overflow: hidden` は 768px 未満で常に効いたままにでき、
`overflow: visible` の例外（暗幕を切らないための戻し）が要らなくなった。

## 変更したファイルと箇所

### claude_memo.html

- `claude_memo.html:111-142` — `#viewport-stage.is-fullscreen` を新設
  （`position:fixed` + `max-width/max-height` のレターボックス、`z-index:9999`）。
  `.video-viewport.pseudo-fullscreen` は `absolute; inset:0; width/height:100%`
  に変更（`z-index` と `aspect-ratio` は不要になったので削除）
- 旧 `body.fs-lock`（全幅） — ここから削除し、下のメディアクエリへ移した（指摘 2）
- 旧 `#viewport-frame.is-fullscreen ~ #subtitle-banner`（`min()` で
  `100vh` からレターボックスを計算していた 9 行） — **削除**（指摘 3・4・7）
- `claude_memo.html:184-195` — `#viewport-stage.is-fullscreen > #subtitle-banner`
  を新設。`top:100%` で枠の直下、`margin-top:0.75rem`。
  `bottom: auto` は Tailwind の `bottom-3` が残ると `top` と挟まれて
  高さが潰れるため（実測で 26px になった。入れて 97.5px）
- `claude_memo.html:203-207` — `body.fs-lock` をメディアクエリの中へ。
  理由（PC でスクロールバーが消えると `100vw` 基準の箱がずれる）をコメントに
- `claude_memo.html:208-226` — 暗幕を `#viewport-frame.is-fullscreen::before` から
  `#viewport-stage.is-fullscreen::before` へ。旧 `#viewport-frame.is-fullscreen`
  ブロック（レターボックスと `overflow: visible`）は削除
- `claude_memo.html:281-331` — `#viewport-stage` / `#viewport-frame` /
  `#player-viewport` のネストを 4 空白ずつに揃えた（指摘 9）。
  字幕バナーのコメントも `#viewport-stage` の子の深さに合わせた
- `claude_memo.html:1626-1655` — `setFullscreen()` が `is-fullscreen` を付ける先を
  `#viewport-frame` から `#viewport-stage` へ。あわせて暗幕タップのハンドラを追加。
  `#viewport-stage` の `click` で `e.target === stage` のときだけ
  `setFullscreen(false)`（疑似要素のヒットは元の要素が受けるので、
  枠の中身や字幕のタップとはこれで区別できる）（指摘 5）

### CLAUDE.md

- `CLAUDE.md:19` — `slideData` 353 → **439 行**（`grep -n` 実測）
- `CLAUDE.md:23` — 再生ロジック 1012 → **1098 行**
- `CLAUDE.md:59` — `playlist-count` 334 → **420 行**
- `CLAUDE.md:43-57` — 字幕の節を書き直し。`margin: 1px` が
  `#player-viewport` の 1px ボーダーを打ち消す値であること（指摘 8）、
  レターボックスは `#viewport-stage.is-fullscreen` の 1 か所であること（指摘 7）、
  `fs-lock` と暗幕が 768px 未満だけであることと暗幕タップの条件（指摘 2・5）を追記

## 検証

Chromium `/home/ytani/.cache/ms-playwright/chromium-1234/chrome-linux/chrome` +
`playwright-core`（`/home/ytani/work/ytBackgammon/node_modules`）、`file://` 読み込み。
スクリプトは scratchpad の `rv3/t1.js`〜`t4.js`。いずれも終了コード 0。

### t1: 全幅 × 全 17 スライド（通常時とフルスクリーン時の両方）

360 / 390 / 430 / 641 / 767 / 768 / 1280px の 7 サイズ × 2 状態 = 14 通り。
各サイズで `ArrowRight` を 17 回送り、`#slide-num` で 17 種すべてを確認。

結果は全 14 通りで **`slide-canvas` のはみ出し 0 / 横スクロール 0 /
console エラー・pageerror 0 件**。

### t2: PC が HEAD と同じか（スクロールバーを表示した状態）

`ignoreDefaultArgs: ['--hide-scrollbars']` で起動。`git show HEAD:claude_memo.html`
を別ファイルに出して同条件で比較。1280x800 と 1280x500 で、
フルスクリーンに入る前・入った後・Esc で出た後の 3 時点を測った。

`#player-viewport` と `#subtitle-banner` の矩形、`header` の幅、
`documentElement.clientWidth` が **6 時点すべてで HEAD と完全一致**
（差分は `#viewport-frame` が HEAD に存在しないことだけ）。

| | HEAD | 今回 |
|---|---|---|
| 1280x800 入る前 `clientWidth` | 1280 | 1280 |
| 1280x800 入った後 `clientWidth` | 1280 | 1280 |
| 1280x500 入る前 `clientWidth` | 1274 | 1274 |
| **1280x500 入った後 `clientWidth`** | **1274** | **1274**（2 巡目は 1280 に広がっていた） |
| 1280x500 入った後の箱 x | 192.56 | 192.56（2 巡目は 195.56） |
| 1280x800 フルスクリーン中の字幕 | 17, 647, 1246, 100 | 同じ |

指摘 2 の横ずれは消えた。

### t3: スマホ縦のフルスクリーン（`isMobile` + `hasTouch`）

360x800 / 390x844 / 430x932 / 767x900 の 4 通り。

| 幅 | 枠（y, 高さ） | 字幕（y, 高さ） | 枠の下端との間隔 | 重なり |
|---|---|---|---|---|
| 360 | 298.8, 202.5 | 513.3, 97.5 | 12px | 無し |
| 390 | 312.3, 219.4 | 543.7, 97.5 | 12px | 無し |
| 430 | 345.1, 241.9 | 598.9, 97.5 | 12px | 無し |
| 767 | 234.3, 431.4 | 677.7, 97.5 | 12px | 無し |

2 巡目は字幕が枠の高さの 34% を覆っていたが、今回は **0%**（枠の外）。
間隔 12px は `margin-top: 0.75rem` どおり。字幕の下端も画面内に収まっている
（390x844 なら 641 < 844）。

タップの区別（`touchscreen.tap()` で実測、4 サイズすべて同じ結果）:

- 枠の中身（スライド中央）をタップ → フルスクリーンのまま
- 字幕をタップ → フルスクリーンのまま
- 暗幕（画面上端）をタップ → **抜ける**。`is-fullscreen` /
  `pseudo-fullscreen` / `fs-lock` の 3 つが揃って外れ、アイコンも
  `fa-expand` に戻る

`window.scrollY` はフルスクリーン中 0 のまま（裏は止まっている）。
`pageerror` 0 件。

### t4: フルスクリーン中に幅が変わったとき

390x844 でフルスクリーンに入り、そのまま 1280x800 → 390x844 と往復。

| 状態 | `body` の `overflow` | 字幕の `position` | 字幕（y, 高さ） |
|---|---|---|---|
| 390 フルスクリーン | `hidden` | absolute | 544, 98（枠の下） |
| → 1280 に拡大 | **`hidden auto`**（＝解除） | absolute | 647, 100（枠に重なる） |
| → 390 に戻す | `hidden` | absolute | 544, 98（枠の下） |
| Esc 後 | `hidden auto` | static | 枠の下に流れる |

スクロール止めも字幕の置き方もメディアクエリで切り替わるので、
回転や幅の変化に自動で追従する（JS 側で幅を見る処理は入れていない）。

## 判断が要る点・残る懸念

- **`#viewport-frame` は PC ではほぼ空の入れ物になった。** PC の
  フルスクリーン中は中身が `absolute` で抜けるため高さ 0 になる（実測
  `[0, 40, 1280, 0]`）。見た目に影響は無いが、768px 未満の縮小専用の要素に
  近づいたので、将来この 2 段のラッパーを 1 つに畳める可能性はある。
  今回は範囲外と判断して触っていない
- **`aspect-ratio: 16 / 9` を `.video-viewport.pseudo-fullscreen` から外した。**
  `width: 100%` と `height: 100%` の両方が決まっている以上 `aspect-ratio` は
  無視される（ラッパー自身が 16:9 なので結果も同じ）。実測でも HEAD と
  矩形が一致している
- **暗幕タップの範囲。** 横持ちなどでレターボックスが画面を埋め尽くすと
  暗幕の面積が 0 になり、タップで抜けられなくなる。横持ちは範囲外（TODO-001 の
  対象外）なので手当てしていないが、`f` キーと Esc しか出口が無い状態は残る
- **`min()` は消えたが `100vh` は 1 か所残っている**
  （`#viewport-stage.is-fullscreen` の `height: 100vh` と
  `max-width: calc(100vh * (16 / 9))`）。これは箱そのものの定義で、
  アドレスバーが伸縮しても箱と字幕は一緒に動くため、指摘 3 のずれ
  （箱と字幕が別々の基準で決まること）は起きない
- 実機（iOS Safari / Android Chrome）でのアドレスバー伸縮は、
  デスクトップ Chromium では再現できないので**未確認**のまま
