# TODO-010 reviewer 報告

対象: `git diff` の 1 ハンクのみ（`claude_memo.html` 1759〜1810 行あたり、
横スワイプでスライドを送る処理を `#player-viewport` の click ハンドラの前に追加）。

読んだもの: `CLAUDE.md`、`TODO.md` の TODO-010 節、
`archives/todo/TODO-005. スライドのタップで再生と一時停止を切り替える.md`、
`archives/todo/TODO-003. 横持ちのスマホでフルスクリーンから抜けられないのを直す.md`、
実装本体（1690〜1930 行、DOM 構造 330〜430 行）。実測は Playwright
（システムの chromium、`has_touch`/`is_mobile` で 390x844 をエミュレート）で行った。

要修正は無かった。検討 3 件、好みの範囲 1 件。

## 検討

1. **`claude_memo.html:1793`／スワイプが遅いと click に落ちて再生／一時停止が誤爆する。**
   `dt > SWIPE_MAX_MS` で早期 return したとき、`swiped` は立てないまま
   touchend を抜ける。距離（`dx >= 50px`）は満たしていても時間切れなら
   スワイプ扱いにならず、直後の click がそのまま `playBtn.click()` に届く。
   ゆっくりした意図的なドラッグ（手が震える、指の動きが遅い、など）でも
   移動量が十分なら「スワイプのつもりが再生／一時停止に化ける」ことになる。
   根拠: コード自体（1793〜1810 行）。実機での体感は未確認。
   対応案（直すかは管理者判断）: 時間の判定と click 抑止の判定を分け、
   `Math.abs(dx) >= SWIPE_MIN_PX` を満たした時点で（時間切れでスライドは
   送らなくても）click は抑止する、など

2. **`claude_memo.html:1023` ほか／`#slide-canvas` 内の `overflow-x-auto` との
   干渉は、現状のコンテンツでは実害が無いことを実測で確認した。**
   `overflow-x-auto` が付いた要素が 2 枚のスライドにある
   （750 行の表、1023 行のターミナル風ブロック）。`playerViewport` の
   touchstart/touchend は `preventDefault` していないので、理屈の上では
   その内側でユーザーが横スクロールしようとした指の動きが、同時に
   スワイプ判定（`dx >= 50px` かつ `|dx| > |dy|`）にも掛かり、意図しない
   スライド送りが起きる懸念があった。
   実測（390x844、`--vp-scale` 0.373 の縮小経路）で `scrollWidth ===
   clientWidth`（853 === 853）を両方の要素で確認し、**現状のコンテンツ量では
   そもそも横スクロールが発生しない**（`#player-viewport` の実レイアウト幅は
   `transform: scale()` の影響を受けず常に 960px 基準なので、画面の物理幅に
   よらず同じ結果になる）ことを確かめた。今は問題無いが、将来これらの
   スライドの列や文言を増やして実際に横スクロールが要るようになったときは、
   この干渉が顕在化する。`render()` を触るときに気に留める程度でよい

3. **`claude_memo.html:1775`〜`1797`／`touchcancel` は listen していないが、
   実害は無いことを確認した。** `touchstart` が毎回 `swiped = false` と
   `touchStartAt`/`X`/`Y` の再設定を条件なしに行う（1775〜1784 行）ため、
   途中で `touchcancel` になって状態が残っても、次の `touchstart` で
   必ず上書きされる。`touchcancel` 後に `click` が飛んでくる経路は
   仕様上ほぼ無いので、フラグの取りこぼしは見当たらない。指摘ではなく
   確認結果として記録する

## 好みの範囲

- `claude_memo.html:1768-1769` の `SWIPE_MIN_PX` / `SWIPE_MAX_MS` は
  ファイル内で 2 例目の `UPPER_SNAKE_CASE` 定数（もう 1 例は
  `SILENT_WAV`、1168 行）で、既存の書き方と揃っている。変更不要

## 確認して問題無しとした点（指示にあった 4 項目）

- **しきい値と `clientX` の当たり外れ**: `#player-viewport` は
  `transform: scale(var(--vp-scale))` で縮小されるが、レイアウト自体は
  常に 960x540 のままで、`clientX`/`clientY` はブラウザが実画面座標
  （transform 適用後の見た目の位置）で渡す。したがって `--vp-scale` が
  0.34〜0.77 のどこであっても、50px は「指が実際に動いた画面上の距離」として
  一定の意味を持つ。実測（`--vp-scale` 0.373、`#player-viewport` の実画面幅
  358px の状態で 80px の横移動）でスライドが 1 つ進むことを確認した。
  縮小経路で `clientX` を使うのは理にかなっている
- **既存ハンドラとの干渉**: タップ（TODO-005、同じ `click` ハンドラ内で
  `swiped` フラグにより抑止）、暗幕のタップ（TODO-003、`#viewport-stage`
  自身への click かつ `e.target === stage` でしか反応しないので、
  `#player-viewport` からバブリングした click は当たらない）、
  シークバー（`#seekbar-container` は `#viewport-stage` の外、別の
  コントロールパネル内にあり `#player-viewport` の子孫ではない）、
  フルスクリーン（`fullscreenBtn`/`Escape` のハンドラは別要素・別イベント）の
  いずれとも DOM 上・イベント上の重なりは無い
- **`passive: true`**: `preventDefault` を呼んでいないので `passive: true`
  のままで問題無い。縦スクロールを妨げない設計はコードの通り機能する
  （横方向優勢のときだけ反応し、縦優勢または同値は無視する）
- **フラグの落とし方**: マルチタッチ（`touches.length !== 1` で
  `touchStartAt = 0` にして無効化。2 本目の指が触れた時点で新しい
  `touchstart` が発火しここを通るので、ピンチ操作をスワイプと誤認しない）、
  `touchcancel`（検討 3 の通り実害無し）、click が来ない場合・二重に来る
  場合（次の `touchstart` で必ず `swiped = false` に戻すコメント通りの
  設計）のいずれも、コードを読む限り抜けは無い

## コメント・命名

- コメントは「なぜ」（`preventDefault` しない理由、フラグを touchstart で
  落とす理由）を書いており、既存箇所の書き方と揃っている
- 変数名（`touchStartX/Y/At`, `swiped`）、定数名は妥当で、TODO-005 の
  コメント資産（`tap-feedback-icon` まわり）を壊していない

## 範囲

差分はこのハンクのみで、指示に無い変更は混ざっていない。
