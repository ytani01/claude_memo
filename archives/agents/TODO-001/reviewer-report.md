# TODO-001 reviewer 報告

対象: `claude_memo.html` の未コミット差分（レビュー開始時に `git diff` で取得したもの）。
コードは直していない。コミットもしていない。

## 先に: 作業ツリーが途中で HEAD に戻された

レビュー中の 2026-09-18 03:09:05 に `claude_memo.html` が書き換えられ、
現在 `git diff` は空、`git status` は `archives/` のみ。ファイルは HEAD と同一
（1635 行、`viewport-frame` の出現数 0）。

下のレビューは**レビュー開始時に取得した差分**に対するもの。実測もその差分が
入っていた状態（03:05〜03:08）で行ったので、測定値は差分適用後の値として有効。
誰が戻したかは分からない。差分を復元してから判断してほしい。

## 実測の環境

Chromium `~/.cache/ms-playwright/chromium-1234/chrome-linux/chrome`、
`playwright-core`（`/home/ytani/work/ytBackgammon/node_modules`）、`file://` 読み込み。
CDN は到達する状態。

---

## 要修正

### 1. 字幕バナーとスライド上部の情報が 5px 前後になり、読めない

**場所**: 削除された旧 `#subtitle-banner { position: static; margin-top: 0.75rem }` と、
新 CSS 144-151 行 `#player-viewport { ... transform: scale(var(--vp-scale, 1)) }`。

**何が問題か**: 390x844 で実測。

| 要素 | computed font-size | 実効（× `--vp-scale` 0.3729） |
|------|--------------------|-------------------------------|
| `#caption-text`（ナレーション字幕） | 14px | **5.2px** |
| `#slide-category` | 12px | **4.5px** |
| スライド本文 `h1`（参考） | 45.5px | 17.0px |

本文が読めて字幕が読めないのは、本文が `cqw` + `clamp()` で 960px 基準の相対
指定なのに対し、`#player-viewport` 直下のクローム（233 行 `text-sm md:text-base`、
240 行 `text-xs md:text-sm`、257 行 `h-6 md:h-7`、269 行 `text-sm md:text-base`）が
Tailwind の固定 px で、しかも `md:` は**ビューポート幅**で判定されるため
≤640px では小さい方が選ばれるから。

**どうなると困るか**: 変更前は `#subtitle-banner` が `position: static` で縮小枠の
外に流れていたので 14px のまま読めた。今回、枠の中に戻したうえで全体を 0.37 倍
するので、「ナレーション字幕」という機能がスマホで事実上使えなくなる。

実装者は `p-4 md:p-6` だけを `padding: 1.5rem` と明示して PC 側に揃えた（報告の
判断 2）が、同じ理由で問題になる他の `md:` ユーティリティは手当てされていない。
つまり新 CSS 135-137 行のコメント「cqw も clamp() も常に 960px 基準で解決される
ので、PC の見た目がそのまま小さくなる」は、この 4 要素については成立していない。

### 2. 擬似フルスクリーンの暗幕がタップを素通しする

**場所**: 新 CSS 174 行 `box-shadow: 0 0 0 100vmax rgba(2, 6, 23, 0.92);`

**何が問題か**: `box-shadow` はヒットテストの対象外。390x844 でフルスクリーンに
した状態で実測すると、

- `#viewport-frame` の実体は `y=312, 390x219` の帯だけ
- `elementFromPoint(5, 5)` → ヘッダー（`border-b ... bg-slate-900/80 backdrop-blur ...`）
- `elementFromPoint(195, 804)` → フッター（`border-t ... bg-slate-950 ...`）

**どうなると困るか**: 画面の上下あわせて約 625px は「暗くなっているだけの、
生きた UI」。暗幕をタップするとヘッダーやチャプター一覧に当たり、スクロールも
する。見た目はモーダルを約束しているのに動作が伴わない。変更前のモバイル上書き
（`max-width:100vw; max-height:100vh; overflow-y:auto`）は画面をほぼ埋めていたので、
この食い違いは無かった。

---

## 検討

### 3. `:has()` 非対応ブラウザでフルスクリーンが完全な無反応になる

**場所**: 新 CSS 162 行 `#viewport-frame:has(> .pseudo-fullscreen)` と
178 行 `.video-viewport.pseudo-fullscreen`（`@media` 内）。

**何が問題か**: セレクタを解釈できない環境ではルール全体が落ちる。一方 178 行の
上書きは `:has()` を含まないので生き残り、`!important` 付きで position / top / left /
right / bottom / width / height / max-width / max-height / margin / z-index / padding を
すべて再指定し、基底の 112 行のフルスクリーン指定を打ち消す。

**どうなると困るか**: 該当ブラウザでフルスクリーンボタンを押しても**見た目が
1px も変わらない**（アイコンだけ変わる）。変更前は旧モバイル上書きが効いて
フルスクリーンになっていたので、機能の退行にあたる。対象は Firefox <121、
iOS Safari <15.4。**未実測**（CSS の仕様からの判断）。切り捨ててよいかは判断が要る。

### 4. JS が動かないと 960px の箱がはみ出したまま残る（CSS だけの逃げ道が無い）

**場所**: 新 CSS 148 行のフォールバック値 `var(--vp-scale, 1)`、
新 JS 1651-1665 行 `setupViewportScale()`。

**何が問題か**: 390x844 で `--vp-scale` を外して実測すると、
`#player-viewport` は 960x540 のまま、`#viewport-frame` は 358px、
`document.documentElement.scrollWidth` が 976（`window.innerWidth` は 390）。
`#viewport-frame` に `overflow: hidden` が無い。

**どうなると困るか**: `body { overflow-x: hidden }` があるので横スクロールバーは
出ないが、スライドの右 6 割は見えず届かない。`setupViewportScale()` は
`startApp()` の先頭なので実際に落ちる確率は低いが、`#viewport-frame` に
`overflow: hidden` を 1 行足せば最悪でも枠内に収まる。

### 5. 640px の境界に段差が残り、641〜767px は元の不具合のまま

**場所**: 新 CSS 138 行 `@media screen and (max-width: 640px)`。

**何が問題か**: 高さ 900、スライド 1 で実測。

| 幅 | `transform` | 字幕の実効サイズ |
|----|-------------|------------------|
| 640 | あり（scale 0.633） | 8.9px |
| 641 | なし | 14px |
| 700 | なし | 14px |
| 768 | なし | 16px |

641px 以上では container が実幅に戻るので `clamp()` の下限が効き、はみ出しが復活する
（実装者の報告どおりスライド 4 / 13 / 17 で +14px / +14px / +3px）。

**どうなると困るか**: 今回直した不具合が 640px の 1px 上で戻ってくる。
スマホ横持ち（844x390、932x430）も 640px 超なので縮小の対象外。境界を `md:`
（768px）に合わせるか、640px 据え置きにするかは判断が要る。

### 6. `CLAUDE.md` の「触るときの注意」が実態と合わなくなる

**場所**: `CLAUDE.md`「スライドの拡大縮小は container query に頼っている」の節。

**何が問題か**: この記述だけを読むと、≤640px では container が常に 960px 固定になり
`--vp-scale` の縮小が別系統で効いていることが分からない。また、指摘 1 のとおり
`#player-viewport` 直下の `md:` ユーティリティが縮小の対象になる点も書かれていない。

**どうなると困るか**: 次にスライドや字幕まわりを触るときに同じ罠を踏む。
`#viewport-frame` と `setupViewportScale()` の存在、`md:` が縮小対象になることを
1〜2 行足しておきたい（ユーザー全体の `CLAUDE.md` の「なぜそうしたかは
（TODO-NNN）で参照」に沿う形で）。

### 7. `ResizeObserver` が無い環境向けのフォールバックは動くことのない経路

**場所**: 新 JS 1660-1664 行の `else { window.addEventListener('resize', update); }`。

**何が問題か**: `ResizeObserver` を持たないブラウザ（Chrome <64 / Safari <13.1）は
`aspect-ratio`（Chrome 88 / Safari 15）も `:has()` も無いので、この分岐に落ちた時点で
縮小方式そのものが成立しない。**未実測**（各機能の対応バージョンからの判断）。

**どうなると困るか**: 困りはしないが、動かない経路を保守することになる。3 行減らせる。

**なお、指示で挙がっていた次の 2 点は問題無しと判断した。**
`ResizeObserver` を外す手立てが無い件は、ページ寿命と同じで SPA のような付け外しが
無いのでリークにならない。無限ループも起きない（frame にカスタムプロパティを
書くだけで frame 自身のサイズは変わらないので、`ResizeObserver` は再発火しない）。
`clientWidth` が 0 のときは scale 0 で不可視になるが、`#viewport-frame` が
`display: none` になる経路が無く、初期値がずれても `ResizeObserver` の初回発火で
直るので実害は無い（Tailwind CDN が実行時にスタイルを注入する件もこれで吸収される）。

---

## 好みの範囲

### 8. `clientWidth` は整数に丸められる

新 JS 1657 行。frame の幅は `%` 由来なので小数になり得る（実測は 358 ちょうど
だったが保証は無い）。`getBoundingClientRect().width` にすれば右端に髪の毛ほどの
隙間が出る余地を消せる。

### 9. `#slide-canvas .overflow-x-auto .inline-flex { flex-shrink: 0 }` は用済み

新 CSS 153-155 行。≤640px でも中身は PC と同じ 960px で組まれるので、PC で要らない
この上書きはモバイルでも要らない。残すと「モバイルだけ PC と違う」点を 1 つ作る。
指示で残すよう言われたとのことなので、判断は管理者に。

---

## 範囲について

差分は `claude_memo.html` のみ。音声やスライドの中身には触れていない。指示に無い
追加は指摘 2 の暗幕（`box-shadow`）1 点だけで、実装者が報告の判断 4 で開示済み。
テストの無いリポジトリ（`CLAUDE.md`「ビルド、依存関係のインストール、テストは無い」）
なので、テストの追加は求めない。新しいコメントはいずれも「なぜ」を書いており問題無い。

## PC 側の確認

実装者の「PC は変わらない」という主張は妥当と読めた。`#viewport-frame` は
PC では `width: 100%` だけの静的ブロックで、親（`.lg:col-span-3.flex.flex-col`）の
column flex では既に幅いっぱいになる。`.video-viewport` は通常フローの
`aspect-ratio: 16/9` のままで、PC の `pseudo-fullscreen`（112 行）も
祖先に `transform` / `filter` を持つ要素が無いので `position: fixed` が
ビューポート基準で正しく効く。実装者の MD5 比較（4 サイズ IDENTICAL）と矛盾しない。
