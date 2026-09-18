# reviewer の報告（TODO-016）

対象: `git diff claude_memo.html`（未コミット。32 挿入 / 73 削除）。
実装の報告を鵜呑みにせず、変更前（`git show HEAD:`）と変更後の 2 版を
headless Chromium で並べて計測し直した。

**動作が変わるもの: 0 件。** 規約との食い違いも無い。
以下は「検討」以下の指摘のみ。

## 実測でやったこと（結論の根拠）

変更前後の両方に同じ計測スクリプトを差し込み、
`#viewport-stage` / `#viewport-frame` / `#player-viewport` /
`#subtitle-banner` / `#slide-canvas` の `getBoundingClientRect()` と
`getComputedStyle()`（width, max-width, margin-left/right, position,
display, transform, overflow）を、**通常 / 字幕オン / 擬似フルスクリーン**の
3 状態で記録した。あわせて字幕トグル 3 回・速度 9 回・音声エンジン 3 回を
押して、class 集合・文言・`slideStartTimes`・プレイリストの中身も記録した。

画面は 6 通り。実装者が試していない**タッチ画面（`pointer: coarse`）**を
`--blink-settings=primaryPointerType=2,availablePointerTypes=2` で
再現した（`matchMedia('(pointer: coarse)').matches === true` を確認済み）。

| 条件 | 経路 | 結果 |
| --- | --- | --- |
| 1280x900 | PC | 矩形すべて一致 |
| 780x900 | PC（境界のすぐ上） | 一致 |
| 760x900 | 縮小経路（幅 < 768） | 一致 |
| 760x480 | 縮小経路＋JS の `max-width` あり | 一致 |
| 900x600 + coarse | 縮小経路（幅 ≥ 768、TODO-009 の経路） | 一致 |
| 844x520 + coarse | 同上・横持ち相当 | 一致 |

差が出たのは次の 2 種類だけで、どちらも描画に影響しない。

- `#player-viewport` の `max-width` の計算値が `100%` → `none`。
  **使用値の幅は全条件で同一**（例: 918px / 732px / 753.77px）。
  縮小経路では元から `max-width: none` が掛かっており、擬似フルスクリーン中は
  `.video-viewport.pseudo-fullscreen` が `max-width: none !important` を
  持つので、この宣言はどの経路でも効いていなかった
- `#playlist-items` の `childNodes` が 17 → 20（後述の指摘 2）。
  `childElementCount` は 17 のまま

JS 側は 6 条件すべてで完全一致。
`speed=1.25x,1.5x,1.75x,2.0x,0.75x,0.9x,1.0x,1.25x,1.5x`、
`voice=Web Speech API/... ; Online Voice/... ; Web Speech API/...`、
`starts=[0,12,25,35,49,61,73,85,99,113,125,139,153,164,175,187,199]`、
字幕トグル 1 回目・2 回目の class 集合（ボタン・アイコン・バナー）も一致。

**計測のノイズについて。** `#slide-canvas` の `transform` が
`matrix(1,…)` と `matrix(0.98,…)` の間で揺れる行があるが、
**同じ版を 2 回走らせても揺れる**（`new` 対 `new` で差が出た）ので、
スライド入場アニメーションの取得タイミングによるもので、この差分とは関係ない。
アニメーションを外した比較では `#slide-canvas` も一致した。

静的な確認: `<script>` 2 ブロックとも `node --check` 成功、
`<style>` の `{` `}` は 38/38、`@media` はコメントを除いて 1 か所、
`brand` / `heading` / `Urbanist` / `speechActive` / `playlist-item` の
grep はいずれも 0 件、`startApp()` の呼び出しは 1 か所のみ。

## 設計・規約の確認（問題なし）

- **`width: 100%` を消してよい根拠**（依頼 3, 4）。`#viewport-frame` の親は
  `#viewport-stage`（`position: relative` の素の div）、`#viewport-stage` の親は
  `class="lg:col-span-3 flex flex-col gap-3"` の**縦 flex**。
  つまり flex アイテムなのは `#viewport-stage` の方で、これは変えていない。
  `#viewport-frame` と `.video-viewport` はどちらもブロック整形の子なので
  `width: auto` が `width: 100%` と同じ使用値になる（border-box のため
  ボーダー 1px の分もずれない）。上の実測と合っている
- **`@media` の統合で順序は変わっていない。** 元の 2 ブロックの間には
  コメントしか無く（`git show HEAD:claude_memo.html` で確認）、統合後も
  `#viewport-frame` → `#subtitle-banner` → `…is-fullscreen > #subtitle-banner`
  → `#player-viewport` → `.video-viewport.pseudo-fullscreen` → `body.fs-lock`
  → `…is-fullscreen::before` の順のまま。セレクタの衝突も無い
- **JS が入れるインライン `max-width` との噛み合わせ。** 900x600 + coarse で
  `max-width: 753.778px` がインラインで入った状態を実測。`width: auto` +
  `max-width` + `margin-inline: auto` で枠は変更前と同じ位置に中央寄せされ
  （x=73.11、フルスクリーン中は左右マージン 73.11/73.125）、変更前と一致した
- 速度の巡回は `indexOf` が -1 でも `(-1 + 1) % 7 === 0` で先頭（0.75）に戻り、
  元の `nextIdx < 0` の分岐と同じ。UI からは到達しない防御的な枝で、
  付いたコメントもその旨を正しく書いている
- `speechActive` は読み出しが 0 箇所で、落ちた副作用は無い
- 「手を付けないもの」（`playlist-count` の `17 Slides`、`updateWaveState()` の
  クラス、音声選択の正規表現、Web Speech 経路、`speakOnlineTTS()` の
  `finished` / `handleEnd`、スライド定義）に差分は無い。範囲外の変更も無い
- `CLAUDE.md`（プロジェクト）の記述に、今回消した宣言に触れている箇所は無い
  （`brand` / `Urbanist` / `width: 100%` の言及なし）。`#viewport-frame` と
  `setupViewportScale()` の説明は今も実態と合っており、更新は要らない
- `setupViewportScale()` 上のコメントの「@media 2 か所」→「@media」の直しは
  実態と合っている（「片方を変えたら両方直す」は JS 側と CSS 側の 2 つを
  指しており、意味が通る）

## 検討

### 1. `claude_memo.html:182-183` — PC の説明がモバイル用コメントの末尾に入った

追記された 2 行:

```
   16:9 の外枠（#viewport-frame）はマウスの PC では素通しで、
   ブロック要素のまま幅いっぱいに広がるので指定は要らない。 */
```

この直前までは「Mobile: 中身は PC と同じ 960x540 のまま描き…」で始まる
**縮小経路の説明**が続いており、その末尾に PC 側の話が足されている。
内容は実測と合っている（上記）が、読む側は直後の `@media` ブロックの
説明だと取りやすい。`#viewport-stage` のコメント（L160-161）の側か、
独立した 1 行コメントに置く方が素直だと考える。

根拠: 実際のファイル L175-186 を読んだ結果。重大度は表示に影響しないので検討。

### 2. `claude_memo.html:1570` — `initPlaylist()` が冪等でなくなり、プレースホルダのコメントが残る

`innerHTML = ''` を消したことで、HTML 側に書いてある
`<!-- Dynamic playlist item buttons injected via JS -->`（L457）が
DOM に残り続ける。実測で `#playlist-items` の `childNodes` が 17 → 20
（コメント 1 + 前後のテキストノード 2）。

**描画は変わらない**（コメント／空白テキストは要素ではないので、Tailwind の
`space-y-2` が使う `> :not([hidden]) ~ :not([hidden])` にも当たらない。
上の実測でも矩形は一致）。`startApp()` からの 1 回しか呼ばれないことも
確認済み（`grep startApp` で定義 1・登録 1・呼び出し 1）。

ただし、この 2 行は「2 回呼ばれても壊れない」保険でもあった。消すと、将来
`initPlaylist()` を再実行する変更が入った時点で項目が二重に積まれる
（`playlistItems` 配列も同時に消してあるので、配列と DOM がずれることは無い）。
節約できるのは 2 行なので、残す判断もあると考える。

根拠: 実測（`childNodes` 17→20、矩形は一致）と L457・L1570-1591 の読み。

### 3. `claude_memo.html:243-251` — 統合後にコメントが 2 つ続いて重複気味

```
/* 暗幕と裏のスクロール止めも同じ条件。
   …（TODO-003 の経緯）… */
/* 擬似フルスクリーン中は裏のページをスクロールさせない。 */
body.fs-lock {
```

1 つ目の冒頭「暗幕と裏のスクロール止めも」と 2 つ目「裏のページを
スクロールさせない」が同じことを言っている。実装者も報告の「残る懸念」で
読みにくさに触れている。整理するなら文面だけの変更になるので、この項目で
やるか別にするかは管理者の判断で。

根拠: 実際のファイル L243-254 を読んだ結果。

## 好みの範囲

### 4. `claude_memo.html:1173-1177` — `map()` の外側で `accumTime` を書き換えている

```js
let accumTime = 0;
const slideStartTimes = slideData.map(slide => {
    const start = accumTime;
    accumTime += slide.duration;
    return start;
});
```

値は実測で変更前と同一。ただし `accumTime` は初期化のためだけの `let` として
トップレベルに残り続ける（他に参照は無いことを grep で確認）。
「未使用の定義を減らす」という項目の趣旨からすると、
`reduce` などで外の変数を残さない形もある。5 行が 5 行なので効果は小さい。

## 確かめられなかったこと

- **実機のタッチ端末では試していない。** `pointer: coarse` は headless Chromium
  の `--blink-settings` で再現したもので、実際のスマホ・タブレットでの
  確認は未実施。ただし縮小経路（`#player-viewport` が
  `position: absolute; width: 960px; max-width: none`）に入った状態で
  計測できており、この項目で消した宣言はその経路では元から効いていない
- Web Speech / Online TTS の**実際の音**は鳴らしていない。触ったのは
  `speechActive`（読み出し 0）と音声エンジン切替の表示だけで、
  再生経路そのものには差分が無い
