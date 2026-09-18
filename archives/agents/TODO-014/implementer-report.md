# TODO-014 実装担当の報告

対象: `claude_memo.html`（1972 行 → 1939 行、`git diff --stat` は 58 挿入 91 削除）。
チェックリストの 9 項目をすべて実施した。`TODO.md` は触っていない。

## 項目ごとの結果

1. **`.video-viewport.pseudo-fullscreen` の重複（L157-172 / L253-266）— 実施**
   メディアクエリ側（現 L253-259）を差分 5 行だけにした
   （`right` / `bottom` / `width` / `height` / `z-index`）。
   削ったのは基底の定義と同じ値の宣言のみ（`position` / `top` / `left` /
   `max-width` / `max-height` / `margin` / `padding`）。基底の規則が先に
   書かれていて両方 `!important`・同じ詳細度なので、共通の値は基底から、
   差分はメディアクエリから適用され、計算値は変更前と一致する。
   `border-radius` / `box-shadow` は元からメディアクエリ側に無く、基底から
   効いていたので変化なし。**−11 行**
2. **`play()` の非 Promise 分岐（`unlockFallbackAudio`）— 実施**
   `const p` を消して `fallbackAudioElement.play().then(...).catch(...)` に。
   `try` の中なので、万一 `play()` が `undefined` を返す環境では
   `TypeError` が `catch(e)` に落ちる（後述の懸念）。**−6 行**
3. **`formatTime()` — 実施**
   `${secs < 10 ? '0' : ''}${secs}` を `String(secs).padStart(2, '0')` に。
   `secs` は `Math.floor(seconds % 60)` で 0〜59 なので出力は同一。
   1 行にはしていない（`mins` / `secs` の 2 行は残した。分ける方が読みやすく、
   項目の狙いは重複の除去）。**±0 行**
4. **`updateWaveState()` — 実施**
   `waveContainer.classList.toggle('paused', !active)` にし、`className` は
   共通部分 + 色のクラスの連結 1 本にした。付くクラスの集合は変更前と同一
   （active: `text-lime-400 font-bold`、非 active: `text-slate-400`）。
   バッジは HTML の初期クラス（`text-xs px-2`）を JS が上書きする作りなので、
   `classList.toggle` だけにせず `className` の代入は残した。**−5 行**
5. **プレイリスト項目のクラス文字列 4 本 — 実施**
   `PLAYLIST_ITEM_CLASS`（共通）、`PLAYLIST_ITEM_ACTIVE_CLASSES`、
   `PLAYLIST_ITEM_IDLE_CLASSES` と `setPlaylistItemState(item, active)` を
   `initPlaylist()` の手前に置き、init と `updatePlaylistSelection()` の
   両方から呼ぶ。`<i>` のクラスもこの関数が持つので、`innerHTML` 側は
   `<i></i>` にして直後に設定している（DOM へ入れる前なので描画は挟まらない）。
   番号の `<span>` の色（`text-lime-400` / `text-slate-500`）は元から
   `updatePlaylistSelection()` が触っておらず、初期描画のままになる。
   **その挙動もそのまま残した**（変えると動作の変更になる）。
6. **`getElementById('playlist-item-N')` の引き直し — 実施**
   `initPlaylist()` で `playlistItems` 配列にボタンを貯め、
   `updatePlaylistSelection()` はその配列を回す。`initPlaylist()` の頭で
   `playlistItems.length = 0` にして作り直しに備えた。
   `btn.id` の付与は残してある。5・6 合わせて **−9 行**
7. **`playerViewport` 定数の利用（3 か所）— 実施**
   `setFullscreen()`、フルスクリーンボタンの click、Escape の分岐から
   `document.getElementById('player-viewport')` を消し、L1750 の
   `playerViewport` を使う。**−3 行**
8. **シークバーの対象スライド探索 — 実施**
   ```js
   const targetIndex = Math.max(0, slideStartTimes.findLastIndex(t => t < targetSec));
   currentSlideElapsedTime = targetSec - slideStartTimes[targetIndex];
   ```
   **境界の一致（コードを追った根拠）**
   - `slideStartTimes[i]` は元のループの `accumulated` と**同じ順序の同じ
     加算**で作られている（L1207-1212）ので、浮動小数の誤差まで一致する
   - 元のループの条件は `accumulated + duration[i] >= targetSec`、すなわち
     `slideStartTimes[i+1] >= targetSec` を満たす**最初の** `i`。
     これは `slideStartTimes[i] < targetSec` を満たす**最後の** `i` と
     同値（累積は単調増加なので）。だから比較は `<=` ではなく **`<`**
   - **スライドの開始時刻ちょうど**（`targetSec === slideStartTimes[k]`、
     `k > 0`）: 元のループは `i = k-1` で成立して**手前のスライドの末尾**
     （offset = その duration）を選ぶ。`<` の `findLastIndex` も `k-1` を
     返し offset も同じ。`<=` にすると `k` の 0 秒になり**挙動が変わる**
   - **0 秒**: `findLastIndex` が `-1` を返すので `Math.max(0, …)` で 0 に寄せる。
     offset は `0 - 0 = 0` で、元のループ（`i=0` で成立、offset 0）と一致
   - **末尾**（ratio = 1、`targetSec === total`）: どちらも最終スライド、
     offset はその duration
   - 実測: 全 17 枚の実際の `duration` で、0〜total を 1000 分割した点、
     各スライドの開始時刻ちょうどとその ±1e-9、0 と total の計 1055 ケースを
     新旧の関数で突き合わせ、**差 0 件**
   **−9 行**
9. **同一ファイル内の静的要素への null ガード 4 つ — 実施**
   `if (stage)`（`setFullscreen` 内）、`if (stage) { … }`（暗幕の click）、
   `if (fsIcon)`、`if (toggleVoiceEngineBtn)`、`if (!tapFeedbackIcon) return`
   を削除。対象の `id` はすべて同じファイルの HTML にある
   （`viewport-stage` L330、`tap-feedback-icon` L358、
   `toggle-voice-engine-btn` L312、`fsIcon` は `#fullscreen-btn` の `<i>`）。
   **−8 行**

## 検証

- **構文**: `<script>`（`src` 無し 2 つ）の中身をスクラッチパッドへ取り出し
  `node --check`。**両方とも成功（終了コード 0）**。一時ファイルは削除済み
- **シークバーの等価性**: 上記 1055 ケースで新旧の
  `(targetIndex, offset)` を比較 → `cases 1055 diffs 0 total 214`（成功）
- **参照漏れの grep**: 消した識別子 `accumulated` / `slideOffset` の残存なし。
  `playlist-item-` の参照は `btn.id` の代入 1 か所だけ（読む側は無し）。
  追加した `PLAYLIST_ITEM_*` / `playlistItems` / `setPlaylistItemState` は
  定義と使用が対応している。`document.getElementById('player-viewport')` は
  0 件（`playerViewport` に統一）
- **ブラウザでの見た目・動作の確認はしていない**（確認担当の範囲）

## 判断が要る点・残る懸念

- **項目 2 と `CLAUDE.md` の但し書き**: 「この項目に入れないもの」に
  「`unlockFallbackAudio()` の解錠」とあるが、項目 2 の行番号
  （L1186-1195）はまさにその関数の中。**解錠の手順（1 個を使い回す、
  クリックの中で呼ぶ、無音 WAV を volume 0 で鳴らす）は変えていない**と
  判断して実施した。ただし `play()` が Promise を返さない環境では、
  変更前は同期で `pause()` + `volume = 1` していたのが、変更後は
  `TypeError` が `catch` に落ちて **`volume` が 0 のまま残る**
  （Online TTS が無音になる）。対象ブラウザはすべて Promise を返す前提での
  実施。戻す方が良いと判断されるなら 8 行で元に戻せる
- **項目 7 の周辺で 1 つ消したガード**: Escape の分岐にあった
  `if (viewport && …)` の `viewport &&` は、項目 9 が名指しした 4 つに
  含まれていない。実際には `playerViewport` は同じファイルの静的要素で
  項目 9 と同じ性質なので**消した**。名指しの範囲を 1 つ超えているので、
  戻すかどうかは管理者の判断で
- **範囲外だが気づいたこと**（直していない）:
  - `btn.id = playlist-item-${idx}` は、項目 6 の後は誰も読んでいない
  - `updatePlaylistSelection()` は番号の `<span>` の色を更新しないので、
    選択が移っても最初に選ばれていた項目の番号が `text-lime-400` のまま。
    元からの挙動で、直すと**見た目が変わる**ため触っていない
