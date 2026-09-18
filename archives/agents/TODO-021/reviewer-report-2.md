# TODO-021 レビュー報告（追加修正分）

対象: `git diff -- claude_memo.html`（未コミット）。先の
`reviewer-report.md` の指摘 1（SELECT の除外）・3（padding）への対応と、
指摘 2 に対する `schedulePauseTransition()` の新設を見た。

## 実測

Playwright（Chromium、`npx playwright install chromium` 後に実行）で
以下を確認した。スクリプトは
`/tmp/claude-649/.../scratchpad/verify.js`, `verify2.js`（セッション内の
一時ファイル。永続しない）。

1. **指摘 1 の修正確認**: `#pause-select` にフォーカスした状態で Space を
   押しても `play-icon` のクラスは変化しない
   （`fa-solid fa-play ml-0.5` のまま）。除外は効いている
2. **待ちを縮めたとき**: `pauseSeconds=3` で `onSlideAudioFinished()` を
   起こし、500ms 後に `1` へ変更 → 実測 1065ms でスライドが進んだ
   （期待値 1000ms 付近。誤差はポーリング間隔 20ms 分）
3. **待ちを伸ばしたとき**: 同様に `2→3` へ 500ms 後に変更 → 実測 3059ms で
   スライドが進んだ（期待値 3000ms 付近）
4. **待ちの最中に一時停止**: 1 秒待ちの 500ms 時点で `togglePlay()` →
   `pauseStartedAt` と `slideTransitionTimeout` はどちらも `null` に戻り、
   元のタイマーが指していたはずの時刻を過ぎてもスライドは進まなかった
   （取りこぼし・ゴーストタイマーは無い）

いずれも指摘なし。想定どおり動く。

## 要修正

なし。

## 検討

### 1. `TODO.md:31-50` — 指摘 2 の決定（即時反映）が `TODO.md` に未記載

利用者判断で「その回から即時反映」に決まったとのことだが、`TODO.md` の
TODO-021 節の「決めたこと（2026-09-18）」には、選んだ値を覚えない旨のみで、
待ちの最中に変更したときの反映タイミングについての記述が無い。

根拠: `/home/ytani/.claude/CLAUDE.md`「判断が要ることは、いま答えられるなら
項目を立てる前に聞く。決まったことは背景として書き」。今回は着手後に決まった
点だが、同じ考え方で「決めたこと」欄に追記しておくと、後で読み返したときに
なぜ `schedulePauseTransition()` が要るのかが `TODO.md` だけで追える。
コードのコメント（1305-1306 行）には経緯が書かれているので実害は無いが、
`TODO.md` 側にも一言あるとよい。

コードの問題ではないため、直すかどうかは管理者の判断で良い。

## 問題なし・確認できた点

- **`pauseStartedAt !== null` ⇔ `isPlaying === true` の不変条件が保たれている。**
  `isPlaying` を立てるのは `playPresentation()`、倒すのは `pausePresentation()`
  のみで、後者は必ず `stopSpeech()`（`pauseStartedAt = null` を含む）を通る
  （`claude_memo.html:1573`, `1584`, `1593`）。競合の心当たりは無かった
- **`slideTransitionTimeout` の共用先**（読了後の待ち・消音時の待ち・
  Web Speech の安全タイマー・Online TTS の `setEndTimeout`）はどれも
  `onSlideAudioFinished()` を経由してから `pauseStartedAt` を触るので、
  `schedulePauseTransition()` 導入で新たに衝突する経路は見当たらなかった
- **一時停止・シーク・手動送り（前後ボタン・再生リスト・シークバー）・
  最終スライドのどの経路も `renderSlide()` → `speakCurrentNarration()` →
  `stopSpeech()` か、`pausePresentation()` → `stopSpeech()` を通るため、
  `pauseStartedAt` の取りこぼしは実測でも見つからなかった**
- **`performance.now()` の差分計算は、待ちを伸ばした場合も縮めた場合も
  正しい。** `remainMs = max(0, pauseSeconds*1000 - 経過)` は基準点
  （`pauseStartedAt`）を固定したまま何度呼んでも累積誤差が出ない作り
- **コメントの調子は既存箇所と揃っている。** 1305-1306 行の 2 行コメントは
  1459-1461 行あたりの既存の「なぜ」コメントと同じ密度で、過剰な説明は
  無かった
- **指摘 1（SELECT 除外）・指摘 3（padding）はどちらも報告どおりに直っている。**
  除外リストに `'SELECT'` が入り、`pause-select` の padding は `speed-btn`
  と同じ `px-3 py-2` になっている
- 他に `<select>` は無いので、除外リストの変更が他要素に影響することは無い
