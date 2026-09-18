# TODO-022 reviewer-report

対象: `git diff -- claude_memo.html`（速度選択を `speed-btn` から `select` へ）

## 要修正

なし。

## 検討

なし。

## 好みの範囲

なし。

## 確認した内容

- **0.9 / 1.75 に戻る経路が残っていないか**: `grep -n "playbackRate" claude_memo.html`
  で全出現を確認。代入は初期値 `let playbackRate = 1.0;`（1146 行）と、今回の
  `speedSelect` の `change` ハンドラ（1734 行）の 2 か所だけ。キーボード
  ショートカット（1848〜1876 行、Space / ArrowRight / ArrowLeft / f / m /
  Escape）や他の UI に速度を操作する経路は無い。`select` の `<option>` も
  `0.75 / 1 / 1.25 / 1.5 / 2` の 5 個のみで、TODO-022 の「決めたこと」
  （0.9 と 1.75 は落とす）と一致。playwright で実際に `#speed-select` を
  `1.25` に変更し、`playbackRate`（グローバル変数として読める）が `1.25`、
  `getEffectiveSpeed()` が `1.75`（`1.25 * baseSpeedMultiplier(1.4)`）に
  なることを実測済み
- **`playbackRate` を読む各箇所**（`getEffectiveSpeed()` 1156 行、消音時の
  待ち 1350 行、Online TTS の安全タイマー 1489/1494/1498/1503 行、
  `playbackLoop()` 1571 行）は今回の diff で変更されておらず、変数の型・
  意味（数値の倍率）も変わっていないので辻褄は合っている
- **TODO-021 の `#pause-select` との揃え**: `class` 属性の文字列は
  `pause-select` と完全に同一（`bg-slate-800 hover:bg-slate-700
  border border-slate-700 text-xs text-sky-400 font-mono font-bold
  px-3 py-2 rounded-lg transition cursor-pointer`）。`selected` 属性の
  付け方、ラベルの書式（「速度 1.0x」「待ち 2秒」）、配置順（速度が
  左、待ちが右。TODO-022 の「決めたこと」どおり）も一致していて過剰な
  差分は無い
- **初期値の整合**: HTML の `<option value="1" selected>` と JS の
  `let playbackRate = 1.0;`（1146 行）が一致することを確認。playwright で
  ページ読み込み直後の `#speed-select` の `value` が `"1"` であることも
  実測
- **`speed-btn` / `speedBtn` / `speedOptions` の残骸**: コード側に残っていない
  ことを grep で確認（`TODO.md` のチェックリスト文言に `speed-btn` の
  記述が残っているのみで、これは未チェック項目の説明文なので問題無い）
- **選択された値がイベントで拾えているか**: playwright の
  `page.select_option("#speed-select", "1.25")` で `change` イベントが発火し、
  `playbackRate` が実際に書き換わることを実測（`select_option` は `change`
  を発火させる標準動作）

## 残る懸念（未確認）

- `speakCurrentNarration()` 内で `isPlaying` のときに再度読み上げを
  やり直す挙動（変更前の `speedBtn` のクリック時と同じ処理）について、
  実際に音声を再生させての確認はしていない（ネットワーク接続が要る
  Online TTS のため、今回は速度変更後の `playbackRate` の値と
  `getEffectiveSpeed()` の計算のみ実測し、音声の実再生は見ていない）
