# TODO-021 レビュー報告

対象: `git diff -- claude_memo.html`（未コミット）

## 要修正

### 1. `claude_memo.html:1827` — 新しい `<select>` がグローバルショートカットの除外対象に入っていない

問題: グローバルの `keydown` ハンドラ（`document.addEventListener('keydown', ...)`,
1825 行〜）は、`['INPUT', 'TEXTAREA'].includes(e.target.tagName)` のときだけ
ショートカットを無効にしている。今回追加した `#pause-select`（`<select>`）は
この除外リストに入っていない。

根拠（実測）: Playwright（Chromium）で `#pause-select` にフォーカスした状態で
Space キーを押すと、`e.preventDefault()` が効いて select のドロップダウンは
開かず、代わりに `togglePlay()` が発火して再生状態が切り替わった
（`play-icon` のクラスが `fa-play` → `fa-pause` に変化。select の `value` は
`2` のまま変化なし＝ドロップダウンは開いていない）。

なぜ問題か: キーボードで `#pause-select` を操作しようとした利用者が、
意図せず再生/一時停止を切り替えてしまう。既存の `speed-btn` は `<button>`
なのでこの経路の対象にならなかったが、今回初めて `<select>` を追加した
ことで、既存の除外リストの穴が実際に踏まれるようになった。

どう直すべきか（提案）: 1827 行の除外リストに `'SELECT'` を加える
（`['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)`）。

## 検討

### 2. `claude_memo.html:1295-1313` — 待ちの最中にプルダウンを変えても、その回の待ちには反映されない

`onSlideAudioFinished()` は `setTimeout(..., pauseSeconds * 1000)` で
呼び出し時点の `pauseSeconds` を遅延時間として固定する。待ちが始まった
「後」に `#pause-select` を変更しても、`setTimeout` の遅延はすでに
評価済みなので今回のスライドには反映されず、次のスライド以降から効く。

比較: `speed-btn` は変更のたびに `if (isPlaying) speakCurrentNarration();`
を呼び、その場で読み上げをやり直して新しい速度を即座に反映させている
（1711-1721 行）。待ち秒数側には同等の再スケジュールが無い。

これがバグかどうかは仕様次第（TODO-021 の決定事項には「変更した回から
即座に反映する」とは書かれていない）。待ちは 1〜3 秒と短く、実害は
小さいので重大度は「検討」にとどめる。反映タイミングをどうするかは
管理者の判断が要る。

### 3. `claude_memo.html:427-431` の見た目 — `speed-btn` との差

`padding` が `speed-btn` は `px-3 py-2`、`pause-select` は `px-2 py-2` と
微妙に異なる（クラス自体はほぼ流用できている）。実害は無く、横幅が
違って見える程度。直すなら `px-3` に揃える案があるが、好みの範囲。

## 問題なし・確認できた点

- **待ち秒数の参照箇所は 1 箇所に集約されている。** `pauseSeconds`
  （1144 行で宣言）は `onSlideAudioFinished()` の `setTimeout` 1 箇所
  （1313 行）でしか使われておらず、`change` イベント（1723-1725 行）で
  更新される。直書きの `2000` は削除されている。TODO-020 が「待ち秒数を
  1 箇所から参照する」ために必要としていた形になっている
- **覚えない仕様どおり。** `localStorage` などの保存処理は無く、
  `pauseSeconds` は変数のまま（過剰な作り込みは無い）
- **チェックリストの 2 項目は両方満たされている**（プルダウンを置く、
  直書きの 2000ms を値から引く）
- 日本語ラベル「待ち 1秒」「待ち 2秒」「待ち 3秒」、`title` の
  「ナレーション終了後の待ち時間」は自然で、既存の `title="字幕の表示/非表示"`
  などと調子が揃っている
- 配置は「Right Options」（`toggle-caption-btn` の次、`speed-btn` の前）で、
  再生操作の並びに置くという決定事項どおり
