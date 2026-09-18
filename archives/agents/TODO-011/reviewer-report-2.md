# TODO-011 reviewer-report-2

対象: `git diff -- claude_memo.html`（89px の固定値をやめ、`setupViewportScale()`
の JS 実測で枠の高さ上限を出す版）。前回レビュー
（`archives/agents/TODO-011/reviewer-report.md`）の要修正 1・2・検討 3 が
どう解消されたかを中心に見た。

確認方法: `playwright`（headless Chromium）で `claude_memo.html` を
`file://` で開き、幅・高さを変えて `#viewport-frame` の
`getBoundingClientRect()` と `style.maxWidth` を実測。スクリプトは
`/tmp/.../scratchpad/measure2.js`, `measure3.js`（セッション限りの
スクラッチパスなので実行結果をここに転記する）。

## 要修正

なし。

## 検討

### 1. `matchMedia` の文字列が CSS と JS の 2 か所（実質 3 か所）で二重管理になった

`claude_memo.html:203, 277, 1935-1936`

```js
const mobile = window.matchMedia(
    'screen and (max-width: 767.98px), screen and (pointer: coarse)');
```

CSS 側の `@media screen and (max-width: 767.98px), screen and (pointer: coarse)`
はこの diff 以前から 2 か所（203 行, 277 行）にあり、対応関係は
コメントで示されているだけで、コード上つながっていない。今回 JS にも同じ
文字列を持ったことで 3 か所目の複製になった。CSS 側の境界（`767.98px` や
`pointer: coarse` の条件）を変えても JS 側は気付かず、ヘッダーの高さの帯と
無関係に、枠だけ縮小経路に入る／入らないというずれが起きうる。

実測では今回の変更が壊れているわけではない（幅 640〜900px, 767/768 境界を
含めて `mobile.matches` は CSS のブレークポイントと一致して切り替わった）。
CSS 側の 2 か所の複製は前回レビュー時点で既にあった構造で、今回はその
パターンを踏襲したものなので「新たに規約を破った」とは言えないが、
複製が 1 つ増えたことで気付かれにくさは増している。避け方の一案として、
CSS 側の `@media` ブロックに `:root { --is-mobile: 1 }` のような
目印を置き、JS はその CSS カスタムプロパティを `getComputedStyle` で読む
（文字列としての条件式を JS に持たない）方法があるが、今の 2 か所の
複製も未解決のままなので、この diff だけの問題ではなく、`CLAUDE.md` の
「触るときの注意」に「この条件式を変えたら 3 か所（203, 277, 1936 行）を
直す」という注記を足す価値がある。

## 問題なし（確認した点）

- **要修正 1（89px が帯によってずれる）は解消。** `frame.getBoundingClientRect().top`
  を毎回測る方式に変えたことで、ヘッダーが折り返す 640〜712px の帯を含め、
  幅 640/641/660/700/710/712/720/750/767/768/800/900px の全域で
  `frame.bottom` が `window.innerHeight` に一致した（実測、高さ 420px 固定・
  タッチ画面エミュレーション）。前回報告の「iPhone SE 横持ち 667x375 で
  +16px」もこの版では解消（`frame.top=105` → `bottom=375`、`innerHeight=375`
  と一致）
- **要修正 2（コメントの数値が全域で成立しない）も解消。** 65px/24px/89px の
  固定値はコード上に残っていない（`grep` で確認）。コメントは「JS が実測する」
  という記述に変わっており、特定の帯だけで成立する数値を書いていない
- **検討 3（定数の由来が紐付いていない）は解消。** 高さの上限がヘッダーと
  本文上余白の実際の高さ（DOM 実測）から出るようになり、Tailwind の
  `py-2 sm:py-3` や `p-4 md:p-6` を変えても、コメントを直し忘れても、
  計算自体はそのときの実際の高さに追従する
- **`update()` の発火経路（ResizeObserver / resize / MutationObserver）は
  過不足なく走り、暴れない。** 実測で確認:
  - 幅を 640↔700↔690↔667px と往復させても、各幅で正しい `maxWidth` に
    収束し、`ResizeObserver loop limit exceeded` 系の console 警告は
    出なかった
  - `max-width` を書き込むこと自体が `frame` の幅を変え、`ResizeObserver`
    がもう一度 `update()` を呼ぶが、2 回目の計算は 1 回目と同じ値になり
    そこで止まる（`top` は横幅ではなく縦位置なので、`max-width` を変えても
    変化しない）。実測でも 2 回目以降の再計算による値のブレは見られなかった
  - フルスクリーンの class を付け外すと `MutationObserver` が発火し、
    付けた直後に `maxWidth` が空になり、外した直後に復元された
  - PC（マウス、1280x800）では最初から `maxWidth` は空のまま
- **`frame.getBoundingClientRect().top + window.scrollY` の妥当性は確認できた。**
  ページを 300px スクロールしても、`top`（-195）+`scrollY`（300）は
  スクロール前の値（105）と一致し、`update()` はスクロールでは再実行され
  ない設計（スクロールリスナーが無い）が、その設計どおりで矛盾は無い。
  sticky ヘッダーはスクロール後も自身の見た目の位置を画面に固定するだけで、
  レイアウト上の高さ（フローに残す分）は変えないため、`frame` の
  ページ内位置の計算式自体には影響しない（実測で裏取り済み）。
  **ピンチズーム中の挙動は未確認**（headless Chromium のビューポート変更で
  代用できる範囲を超えるため）。レイアウトビューポート基準の値
  （`innerHeight` 等）はピンチズームでは変わらない設計上、壊れないと
  推測されるが、実機での確認はしていない
- **CSS に残した `margin-inline: auto` と、その上のコメントは実装と食い違って
  いない。** CSS 側は `max-width` を持たず、コメントも「JS が入れる」と
  書いてあるとおり実装されている
- **`#viewport-stage.is-fullscreen > #viewport-frame { max-width: none }` は
  削除され、JS 側の `stage.classList.contains('is-fullscreen')` チェックに
  置き換わった。** `:has()` は使っておらず、TODO-001 の方針（クラスの
  付け外しで見る）と整合している。実測でもフルスクリーン中に `maxWidth` が
  空になることを確認した
- 差分の範囲は依頼どおりで、無関係な変更は混ざっていない。コメントの
  書き方（「なぜ」の説明、TODO 番号の参照）も既存のスタイルと揃っている
