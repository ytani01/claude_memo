# TODO-010 verifier-report

## 検証方法

- Node に globally インストール済みの Playwright (`chromium@1.63.0`, `/home/ytani/.local/share/mise/installs/node/26.9.0/lib/node_modules/playwright`) が使えたので、これを使った。
- `claude_memo.html`（未コミットの差分入り）を作業用の一時ディレクトリへ
  `\cp` でコピーし（`/tmp/claude-649/.../scratchpad/claude_memo.html`）、
  リポジトリのファイルには一切手を入れていない。
- Playwright で `hasTouch: true` のコンテキストを作り、`#player-viewport` に対して
  `Touch` / `TouchEvent` を合成した `touchstart` / `touchend` を発火させ、
  実機のスワイプ・タップを再現した。
- 判定には DOM の実測値を使った（`isPlaying` や `currentIndex` はスクリプトの
  クロージャ内変数で `window` に出ていないため直接は読めない）。
  - スライド切り替え: `#slide-num` のテキスト（`01`, `02`, ...）
  - 再生／一時停止の状態: `#play-btn` 内の `<i>` が `fa-pause` クラスを
    持つかどうか（`playPresentation()` / `pausePresentation()` が
    直接書き換えている要素）
- スクリプト本体: `/tmp/claude-649/.../scratchpad/test.js`
  （実行環境が終わると消える一時ファイルなので、必要なら再現手順ごと
  このまま貼る。以下に主要部分を残す）

実行結果（終了コード 0、`PAGE ERROR` ログなし）:

```
INITIAL: {"slideNum":"01","title":"1. 私の Claude Code の使い方","playing":false}
LEFT SWIPE slideNum 01 -> 02 (expect +1)
POST-SWIPE CLICK playing false -> false (expect unchanged) slideNum 02 -> 02 (expect unchanged)
RIGHT SWIPE slideNum 02 -> 01 (expect -1)
VERTICAL SWIPE+CLICK slideNum 01 -> 01 (expect unchanged) playing false -> true (expect toggled)
SLOW SWIPE+CLICK slideNum 01 -> 01 (expect unchanged) playing true -> false (expect toggled)
SHORT SWIPE+CLICK slideNum 01 -> 01 (expect unchanged) playing false -> true (expect toggled)
TAP slideNum 01 -> 01 (expect unchanged) playing true -> false (expect toggled)
TAP AFTER SWIPE playing false -> true (expect toggled = flag did not carry over) slideNum stayed at 02 then tap slideNum 02 (expect unchanged by the tap)
BOUNDARY: at first slide 01 , after prev-swipe: 01 (expect unchanged, no crash)
TOTAL SLIDES: 17
BOUNDARY: at last slide 17 / 17 , after next-swipe: 17 (expect unchanged, no crash)
EXIT: 0
```

## 完了条件との対応

1. 横スワイプ（左→次、右→前）で `renderSlide()` が呼ばれる経路か
   → **確認済み**。速い左スワイプ（300px, 100ms）で `01`→`02`、
   続く速い右スワイプで `02`→`01` に戻った。ソース上も
   `(dx < 0 ? nextBtn : prevBtn).click()` で `next-btn` / `prev-btn` の
   click ハンドラ（`renderSlide(currentIndex ± 1, true)`）に投げている。

2. スワイプ後に `#player-viewport` の click（再生／一時停止）が
   発火しないか → **確認済み**。スワイプ直後に実機さながらの
   合成 `click` イベントを追加で発火させたが、`playing` は
   `false → false` のまま変化しなかった。`swiped` フラグで
   click ハンドラの先頭で `return` している分岐がそのとおり効いている。

3. 縦方向のスワイプ・ゆっくりした動き・短い動きでは切り替わらないか
   → **確認済み**（3 パターンとも）。
   - 縦スワイプ（dy=400px, dx=0）: `slideNum` 不変
   - 遅いスワイプ（700ms、`SWIPE_MAX_MS=600` 超過）: `slideNum` 不変
   - 短いスワイプ（20px、`SWIPE_MIN_PX=50` 未満）: `slideNum` 不変
   - いずれも直後の click では再生／一時停止がきちんとトグルしており、
     `swiped` フラグが誤って立っていないことも合わせて確認した。

4. 単純なタップでは従来どおり再生／一時停止が切り替わり、フラグが
   次のタップに持ち越されないか → **確認済み**。
   - 単発タップで `playing` がトグルした。
   - 「スワイプ → 別のタップ」の順に発火させても、後続タップで
     `playing` は正しくトグルした（前段のスワイプで立てた `swiped` を
     後続タップの `touchstart` が `swiped = false` にリセットしている
     ことに対応）。

5. 先頭・末尾のスライドでスワイプしても壊れないか → **確認済み**。
   - 先頭（`01`）で右スワイプ（=prev）: `slideNum` は `01` のまま、
     `PAGE ERROR` なし。
   - 末尾（`17`/`17`）で左スワイプ（=next）: `slideNum` は `17` のまま、
     `PAGE ERROR` なし。
   - ソース上も `prevBtn` / `nextBtn` の click ハンドラに
     `currentIndex > 0` / `currentIndex < slideData.length - 1` の
     ガードがあり、`renderSlide()` 自体にも
     `if (index < 0 || index >= slideData.length) return;` があるため、
     二重にガードされている。

## 変更ファイルと指示の範囲

- `git diff` で変わっているのは `claude_memo.html` のみ、かつ差分は
  1756〜1800 行あたり（`player-viewport` のタッチ／クリックまわり）の
  1 箇所にまとまっている。`TODO.md` の TODO-010 の要件（横スワイプで
  `prev-btn` / `next-btn` と同じ `renderSlide()` へ、タップの再生／
  一時停止と競合させない）と範囲は一致している。指示に無いファイルの
  変更は無い。

## 確かめられなかったこと・判断が要る点

- **実機（実際のスマホのブラウザ）での確認はタスク上 verifier の担当外**
  （依頼文の指示どおり）。今回の検証は Playwright の合成タッチイベントに
  よるもので、実デバイスの `touch-action` の扱いやブラウザごとの
  click 抑制タイミングの細部までは再現できていない。
- `TODO.md` のチェックリストの 2 項目目「タップでの再生／一時停止が
  誤爆しないことを実機で確かめる」は、文字どおり実機確認が必要なため
  このレポートでは未消化（利用者が実機で確認する前提）。
- `SWIPE_MIN_PX=50` / `SWIPE_MAX_MS=600` のしきい値そのものが実際の
  スマホの操作感として妥当かどうかは、動作ロジックの正しさとは別の
  「使い勝手」の話であり、verifier の判断範囲外と考える。

## 再検証（時間条件を外した後）

管理者からの指示: スワイプ判定から時間の条件（`SWIPE_MAX_MS`）を外し、
距離（横 50px 以上）と方向（横 > 縦）だけで判定するよう変更。
`touchStartAt`（時刻）は `touchStarted`（真偽値）に置き換え。

`git diff` で該当箇所を確認したところ、上記のとおりになっていた
（`SWIPE_MAX_MS` の定義と `dt > SWIPE_MAX_MS` の分岐が消え、
`touchStarted` という真偽値フラグに置き換わっている）。

### 検証方法

前回と同じ手順・同じ Playwright 環境。`claude_memo.html` を
一時ディレクトリへ再度 `\cp` でコピーし直し（前回のコピーを上書き）、
リポジトリのファイルは変更していない。テストスクリプト
（`/tmp/claude-649/.../scratchpad/test.js`）のうち、以前の「遅いスワイプ」
のシナリオ（4番）だけを次のとおり書き換えて再実行した（他のシナリオは
そのまま）。

- 旧: 700ms・横100pxのスワイプ → スライドが**変わらない**ことを期待
- 新: 1000ms・横80pxのスワイプ → スライドが**変わる**ことを期待し、
  さらにそのスワイプ直後に合成 `click` を発火させて、再生／一時停止が
  **トグルしない**（click が抑制される）ことも確認

### 実行結果（終了コード 0、`PAGE ERROR` ログなし）

```
INITIAL: {"slideNum":"01","title":"1. 私の Claude Code の使い方","playing":false}
LEFT SWIPE slideNum 01 -> 02 (expect +1)
POST-SWIPE CLICK playing false -> false (expect unchanged) slideNum 02 -> 02 (expect unchanged)
RIGHT SWIPE slideNum 02 -> 01 (expect -1)
VERTICAL SWIPE+CLICK slideNum 01 -> 01 (expect unchanged) playing false -> true (expect toggled)
SLOW SWIPE(1000ms,80px) slideNum 01 -> 02 (expect +1, i.e. slide DID change)
SLOW SWIPE POST-CLICK playing true -> true (expect unchanged, i.e. click suppressed) slideNum 02 -> 02 (expect unchanged)
SHORT SWIPE+CLICK slideNum 02 -> 02 (expect unchanged) playing true -> false (expect toggled)
TAP slideNum 02 -> 02 (expect unchanged) playing false -> true (expect toggled)
TAP AFTER SWIPE playing true -> false (expect toggled = flag did not carry over) slideNum stayed at 03 then tap slideNum 03 (expect unchanged by the tap)
BOUNDARY: at first slide 01 , after prev-swipe: 01 (expect unchanged, no crash)
TOTAL SLIDES: 17
BOUNDARY: at last slide 17 / 17 , after next-swipe: 17 (expect unchanged, no crash)
EXIT: 0
```

### 新規に確かめた点

- **ゆっくりした横スワイプ（1000ms・80px）でスライドが送られる**:
  `slideNum` が `01` → `02` に変わった（`expect +1` どおり）。
- **同時に、再生／一時停止が誤爆しない**: スワイプ直後の合成 `click`
  （実機で touchend 後に飛んでくる click を模したもの）で `playing` は
  `true → true` のまま変化しなかった（`SLOW SWIPE POST-CLICK` の行）。

### 前回通っていた 9 パターンの再確認

- 速い左右スワイプでの切り替え: 通った（`LEFT SWIPE`, `RIGHT SWIPE`）
- スワイプ直後の click 抑制: 通った（`POST-SWIPE CLICK`）
- 縦スワイプでの非反応: 通った（`VERTICAL SWIPE+CLICK` で `slideNum` 不変、
  かつ click は抑制されず `playing` がトグル）
- 短い横移動（20px）での非反応: 通った（`SHORT SWIPE+CLICK` で `slideNum`
  不変、`playing` はトグル）
- 単純タップでの再生／一時停止のトグル: 通った（`TAP`）
- フラグの持ち越し無し（スワイプの直後の別タップでも正しくトグル）:
  通った（`TAP AFTER SWIPE`）
- 先頭・末尾での境界（クラッシュ無し、スライド不変）: 通った
  （`BOUNDARY` の 2 行とも）

「遅いスワイプで切り替わらない」という旧シナリオ自体は、今回の変更で
仕様が変わった（時間を見なくなった）ため、期待値を「切り替わる」に
更新して置き換えた。

### 確かめられなかったこと・判断が要る点（再検証分）

- 前回と同様、実機での確認は対象外。1000ms・80px という具体的な数値は
  今回の依頼文で指定されたものをそのまま使っており、これより極端に
  遅い（数秒かける）操作や、指を止めてから動かす操作までは試していない。
  ソースを読む限り時間を一切見ない実装（`touchStarted` は真偽値のみで
  時刻を持たない）なので、理屈の上ではどれだけ時間をかけても距離条件
  さえ満たせば切り替わるはずだが、この点は数値では確認していない
  （読みによる推定）。
