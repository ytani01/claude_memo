# TODO-009 verifier-report

## 対象・方法

対象: `claude_memo.html`（未コミットの作業ツリー、`git diff` で見える差分のみ）。
Playwright（グローバル `npm -g` の `playwright@1.63.0`、chromium 同梱版）で
`file://` のローカル HTML を開いて実測した。スクリプトは
`archives/agents/TODO-009/measure.js.txt`、生の実測値（JSON）は
`archives/agents/TODO-009/measure-output.json` に置いた。

計測方法:
- `#slide-category` を含む上段の行の `getBoundingClientRect().bottom`
- `#slide-canvas` の `top` / `bottom`
- `#player-viewport` の content-box（padding 内側）の top / bottom を
  `getComputedStyle` の border/padding を引いて算出
- 併せて `#player-viewport` の border-box（見た目の枠の外周）の bottom も
  参考値として取った
- 17 スライド全てを `#next-btn` を JS で `click()` して送りながら測定
  （フルスクリーン中は暗幕の裏に隠れて実際のポインタークリックが通らない
  ため、`page.evaluate` 経由の `click()` に切り替えた。これは送り操作の
  代替であって、ボタンの実クリック可否を検証したものではない）
- 自動再生は `#play-btn` のアイコンが `fa-pause` なら止めてから測定

## 1. 844x390・タッチあり・フルスクリーン

`matchMedia('(pointer: coarse)')` = true、`(max-width: 767.98px)` = false
（想定どおり、幅ではなく pointer:coarse 側で縮小経路に入っている）。

17 スライド全件で:
- 上段 bottom と canvas top の差（`canvasTop - headerBottom`）: 最小 **2.89px** 〜 最大 6.15px（全スライドで正、重なり無し）
- canvas bottom と content-box bottom の差（`contentBoxBottom - canvasBottom`）: **-6.94px 〜 -3.68px**（content-box の下端から 3.7〜6.9px はみ出している）
- canvas bottom と border-box bottom（枠の見た目の外周）の差: 18.06px 〜 21.32px（枠自体からは十分内側で、見た目上の欠けは無い）

判定: **上段との重なりは 17 スライド全てで解消**（`canvasTop >= headerBottom` を満たす）。
一方、下側は content-box（padding の内側）をわずかに超えており、bottom padding
（p-6 相当 ×`--vp-scale` ≒ 25px）の余白を 4〜7px 食い込んでいる。ただし枠の
見た目の外周（border-box）までは 18px 以上余裕があり、コントロールボタン類は
`#player-viewport` の外にあるため、目視での欠けや操作要素との重なりは
起きていない。この点は「重なりが無い」の解釈次第で見解が分かれるので、
判断が要る点として下に書く。

## 2. 844x390・タッチあり・通常表示（フルスクリーンでない）

`pointer: coarse` = true、`max-width: 767.98px` = false（同上）。

17 スライド全件で:
- 上段との差: 最小 **5.23px** 〜 最大 5.96px（重なり無し）
- content-box 下端との差: **-2.35px 〜 -1.63px**（1.6〜2.4px の食い込み、フルスクリーン時より小さい）
- border-box 下端との差: 22.65px 〜 23.37px（余裕あり）

判定: 上段との重なりは無し。下側の食い込みはフルスクリーン時よりわずかに小さい。

## 3. 1280x800・タッチ無し（PC、回帰確認）

`pointer: coarse` = false、`max-width: 767.98px` = false →
縮小経路の `@media` ブロックが**適用されていない**ことを `matchMedia` で確認済み。

17 スライド全件で:
- 上段との差: 5.94px 〜 6.73px
- content-box 下端との差: **+1.94px 〜 +2.73px**（正、食い込み無し）
- border-box 下端との差: 26.94px 〜 27.73px

判定: 回帰無し。従来どおり縮小経路に入らず、上下とも余裕がある。

備考: `--vp-scale` のカスタムプロパティ自体は PC でも JS
（`setupViewportScale`／ResizeObserver）が値（0.956 程度）を設定しているが、
`transform: scale(var(--vp-scale,1))` の CSS ルールは `@media` の中にしか
無いため、`matchMedia` が false の PC では効いていない。実測（canvas が
960x540 相当のまま計算されている）とも整合している。

## TODO-003（フルスクリーン中のタップで抜ける）の回帰確認

844x390・タッチありでフルスクリーンに入った後、レターボックスの暗幕
（左上角 (5,5) のクリック、`#viewport-stage` 自身がターゲット）をクリックした。

- クリック前: `#player-viewport.classList.contains('pseudo-fullscreen')` = `true`
- クリック後: 同 = `false`

判定: 壊れていない。タップでフルスクリーンから抜けられる。

## 変更ファイルの範囲

`git diff` で変わっているのは `claude_memo.html` のみ。差分は
- コメント文の書き換え（PC/縮小経路の説明）
- 縮小経路のメディアクエリに `, screen and (pointer: coarse)` を追加
- 対応するコメント（JS 側の `--vp-scale` の説明）の書き換え

の 3 箇所で、TODO-009 の記述（縮小経路をタッチ画面にも広げる）と一致している。
指示に無いファイル・箇所の変更は無い。

## 判断が要る点

- **下側の 4〜7px の食い込みをどう扱うか。** 上段との重なり（TODO-009 が
  問題にしていた症状）は解消しているが、`#slide-canvas` の下端は
  `#player-viewport` の content-box（bottom padding の内側）をわずかに
  超えている。枠の見た目の外周やコントロールボタンとは重ならないため、
  実害は無いと見えるが、「重なりが無い」の完了条件をどこまで厳密に取るかは
  管理者の判断だと思う。数値は上記の実測値を参照
- TODO-009 のチェック項目「横持ちスマホの実機（または同じ大きさの画面）で、
  上段と本文が重ならないことを確かめる」は、実機ではなく Playwright の
  エミュレーション（`hasTouch`/`isMobile` context）での確認である点は
  明記しておく。実機での確認は行っていない
