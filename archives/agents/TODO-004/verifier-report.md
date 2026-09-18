# TODO-004 verifier report

このプロジェクトにビルド・テストは無い（1 ファイルの静的 HTML）。実行した検証は
`git diff` による差分確認、CSS の静的な読み込み、代表的な画面サイズでの手計算のみ。
ブラウザ実測（chromium/playwright 等）は環境が無かったため行っていない。

## 1. 変更が TODO-004 の記述どおりか

`git diff` の全体:

```diff
diff --git a/claude_memo.html b/claude_memo.html
index d1e327b..1cf41d5 100644
--- a/claude_memo.html
+++ b/claude_memo.html
@@ -112,8 +112,11 @@
 
         /* Pseudo Fullscreen Overlay Fallback - Fixed 16:9 Ratio Centered */
         /* 画面中央の 16:9 レターボックスはこのラッパーが担う。中身も字幕も
-           この箱を基準に置けるので、100vh からレターボックスの位置を
-           計算する必要が無い（TODO-001）。 */
+           この箱を基準に置けるので、100dvh からレターボックスの位置を
+           計算する必要が無い（TODO-001）。
+           高さは dvh で取る。スマホの 100vh は URL バーを含んだ高さなので、
+           横持ち（幅 768 以上で PC 側の経路に入る）で 16:9 の箱が画面の下へ
+           はみ出す（TODO-004）。dvh 非対応のブラウザ用に vh の行を先に置く。 */
         #viewport-stage.is-fullscreen {
             position: fixed;
             top: 0;
@@ -122,7 +125,9 @@
             bottom: 0;
             width: 100vw;
             height: 100vh;
+            height: 100dvh;
             max-width: calc(100vh * (16 / 9));
+            max-width: calc(100dvh * (16 / 9));
             max-height: calc(100vw * (9 / 16));
             margin: auto;
             z-index: 9999;
```

変更されたファイルは `claude_memo.html` のみ。変更箇所も
`#viewport-stage.is-fullscreen` のコメントと `height` / `max-width` の 2 行の
追加だけで、TODO-004 に書かれた範囲どおり。余計な変更は見当たらない。

`git status` は `claude_memo.html` の modified のみ。

## 2. CSS の書き方

- `height: 100vh;` の直後に `height: 100dvh;` を置く形は、CSS の「後勝ち」の
  カスケードと「無効な宣言は無視される」という挙動を利用した標準的なフォール
  バックの書き方で、正しい。`dvh` 未対応のブラウザは 2 行目の宣言を無効な値として
  無視するので、1 行目の `vh` の値がそのまま有効に残る。`max-width` の 2 行も同様。
- `max-height: calc(100vw * (9 / 16))` は幅基準の計算なので `vh`/`dvh` のどちらでも
  値は変わらない。触らなくてよい、という TODO の判断は妥当。

## 3. 他の規則への影響

`#viewport-stage.is-fullscreen` に連動する規則を確認した（`claude_memo.html`
100〜260 行付近）。

- `.video-viewport.pseudo-fullscreen`: `position: absolute` + `top/left/right/bottom: 0`
  で親要素（`#viewport-stage.is-fullscreen`）に対する相対配置。親の高さが
  `vh` から `dvh` に変わっても、子は `100%` で追随するだけなので影響なし。
- `#subtitle-banner`（768px 未満の `@media` 内、`top: 100%` で親の下端を基準に
  している）も同様に親のサイズに対する相対値なので影響なし。
- 768px 未満の `@media screen and (max-width: 767.98px)` 内の各規則
  （`#viewport-frame`、`#player-viewport`、`.video-viewport.pseudo-fullscreen` の
  縦持ち用上書き）は `960x540` の固定 px と `transform: scale()` で組んでおり、
  `vh`/`dvh` を直接使っていない。今回の変更の影響を受けない。
- 暗幕 `#viewport-stage.is-fullscreen::before`（`@media (max-width: 767.98px),
  (pointer: coarse)`）は `position: fixed` + `inset: 0` でビューポート全体を
  覆う独立した要素であり、`#viewport-stage` 自身の高さ（`vh`/`dvh`）を参照して
  いない。暗幕の帯の見え方は「レターボックスの外側」がどれだけ空くかで決まり、
  今回の変更でレターボックスの高さが縮む（dvh<vh のとき）方向にしか動かないため、
  暗幕が消える方向の心配はない。むしろ帯がわずかに広がる。

これらの規則が壊れる要素は見当たらない。

## 4. 代表的な画面サイズでの手計算

計算の前提: `dvh` は実際に見えている高さ（URL バー等の分だけ `vh` より小さい
場合がある）とする。ブラウザ実測はしていないので、URL バーの高さは仮定の値。

### 844x390 横持ちスマホ（幅768以上、PC 側の経路）

想定: `vh = 390`（URL バー込みの CSS 100vh 基準）、`dvh = 350`（URL バー分 40px
差し引いた見えている高さ、仮定）。

- 旧（`vh` 基準）: `width: 100vw = 844`。
  `max-width: calc(100vh*16/9) = calc(390*16/9) ≈ 693.3`。
  `height: 100vh = 390`。
  `max-height: calc(100vw*9/16) = calc(844*9/16) ≈ 474.75`。
  → `width = min(844, 693.3) = 693.3`、`height = min(390, 474.75) = 390`。
  箱は 693.3×390。**見えている高さ 350 に対して 390 は 40px はみ出す**
  （TODO の記述どおりの不具合を再現）。
- 新（`dvh` 基準）: `max-width: calc(100dvh*16/9) = calc(350*16/9) ≈ 622.2`。
  `height: 100dvh = 350`。
  → `width = min(844, 622.2) = 622.2`、`height = min(350, 474.75) = 350`。
  箱は 622.2×350、アスペクト比 622.2/350 ≈ 1.778 = 16/9 で正しく、
  見えている高さ 350 ちょうどに収まりはみ出さない。

### 390x844 縦持ちスマホ（幅768未満）

`vw = 390`、`dvh` を仮に 800（URL バー込みなら 844）とする。
このケースは `max-height: calc(100vw*9/16) = calc(390*9/16) ≈ 219.4` が
`height`（100dvh、800前後）より小さく効くため、`vh`→`dvh` の変更に関わらず
`height` は常に `max-height` 側（幅基準）で決まる。
→ `width = min(390, calc(dvh*16/9)) = 390`（`dvh*16/9` は 1300 超で `100vw` より
大きいので `width` は制約されない）、`height = 219.4`。
**縦持ちでは今回の変更による見た目の違いは無い**（もともと幅基準で決まっていた
経路のため）。

### 1280x800 PC（URL バーの影響なし = `vh = dvh`）

`vh = dvh = 800`、`vw = 1280`。
`max-height: calc(100vw*9/16) = 1280*9/16 = 720`。
`height: 100dvh = 800` → `max-height` 720 で頭打ち → `height = 720`。
`max-width: calc(100dvh*16/9) = 800*16/9 ≈ 1422.2`（`vw=1280` より大きいので
`width = 100vw = 1280` のまま制約されない）。
箱は 1280×720、アスペクト比ちょうど 16/9。
**PC では `vh = dvh` なので今回の変更で見た目は変わらない。**

以上より、TODO-004 が意図した「横持ちスマホでだけ挙動が変わり、縦持ちスマホと
PC では変わらない」という設計は、手計算のうえでは成立している。

## 5. 他に `100vh` を使っている箇所が残っていないか

```
grep -n "100vh" claude_memo.html
```
の結果、`#viewport-stage.is-fullscreen` のコメントとフォールバック用の
`height: 100vh;` / `max-width: calc(100vh * (16/9));`（意図して残した行）以外に
`100vh` の使用は無い。ファイル全体で他に `vh` 単位を使っている箇所も無かった
（`grep -n "vh\b"` で確認、ヒットはすべて上記の意図した行）。

## 確かめられなかったこと・判断できないこと

- **実際のブラウザでの実測はしていない。** URL バーの高さ（`vh` と `dvh` の
  差分）は仮定の値であり、実機・実ブラウザでの検証はできていない。手計算上の
  ロジックが正しいことは確認したが、「実際に画面の下にはみ出さなくなったか」の
  最終確認は目視／実機テストが必要（TODO.md のチェック項目 2 番目「横持ちの
  スマホ、縦持ちのスマホ、PC の 3 つで、はみ出しとレターボックスを確かめる」は
  実機でないと完了とは言えない）。
- `dvh` 未対応ブラウザでの実際のレンダリング（無効宣言が本当に無視されるか）も
  静的な仕様上の判断であり、実ブラウザでは確認していない。
