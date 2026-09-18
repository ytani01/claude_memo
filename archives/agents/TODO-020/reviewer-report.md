# TODO-020 reviewer 報告

対象: `git diff -- claude_memo.html`（未コミット、41 行）。`TODO.md` の
TODO-020 の節と、参照している TODO-021 の決定事項と照らして読んだ。
verifier の報告（3 項目の完了条件はすべて実測で成立）は読んだ上で、
コードとして良いかを見た。

## 実測方法

Playwright（Chromium、`npx playwright`、node 版）で `file://` を開き、
`page.evaluate` でトップレベルの `let`/`const`（`slideData` や
`pauseSeconds` など。IIFE に包まれていないのでスクリプトスコープの
束縛がそのまま読み書きできる）を直接読み書きして実測した。
スクリプトは `/tmp/claude-649/.../scratchpad/verify-todo020*.js`
（セッション内の一時ファイル、リポジトリには残していない）。

## 要修正

なし。

## 検討

### 1. シークバーで「待ちの区間」をクリックすると、ナレーションが最初から
再生し直され、進行バーは実際の終了より何秒も早く頭打ちになって止まって見える

`claude_memo.html:1886-1899` のシークバーの click ハンドラは、TODO-020 で
`totalDurationSeconds` / `slideStartTimes` に待ち秒数が入るようになったことで、
「そのスライドの待ちの区間」もクリック対象に含まれるようになった。ここを
クリックすると `renderSlide(targetIndex, false)`（`resetOffset=false`）が
呼ばれ、`currentSlideElapsedTime` は待ちの区間の値のまま、
`speakCurrentNarration()` がナレーションを最初から再生し直す。

実測（`pauseSeconds=3`、スライド 0 の `duration=18` で、待ちの区間
＝ 18〜21 秒の中の 19 秒を狙ってクリック）:

```
クリック直後: currentSlideElapsedTime=18.94  badge="朗読中 (Online Voice)"
+1.2s: elapsed=20.16 (span=21 未満)
+3.9s: elapsed=21.00 (span で頭打ち)  badge="朗読中 (Online Voice)"
+6.0s: elapsed=21.00                  badge="朗読中 (Online Voice)"（変化なし）
```

頭打ち後も `badge` が「朗読中」のまま何秒も変わらない＝進行バーは
そのスライドの 100% で止まって見えるが、裏では最初からのナレーションが
まだ鳴っている（`onended` が来るまで `onSlideAudioFinished()` は呼ばれず、
本当の待ちにも入らない）。TODO-020 の目的は「待ちの間も進行バーを
止めない」ことなので、この経路は逆に「実際にはまだ話し終わっていないのに
バーだけ止まって見える」形になっている。

待ちの区間は 1〜3 秒しかなく、350 秒超のバー全体の 0.3〜0.9% 程度の幅
（かなり狭い標的）なので、意図せず踏む頻度は低いと見ている
（未確認: 実機でのタップ精度）。TODO-020 のチェックリストにはシーク時の
挙動は書かれておらず、対応するかどうかは範囲の判断が要る。

### 2. `pauseSeconds` を縮めた瞬間、`currentSlideElapsedTime` が過去の値より
小さくなり得る（表示が巻き戻る）

`claude_memo.html:1746` の
`currentSlideElapsedTime = Math.min(currentSlideElapsedTime, slideSpan(currentIndex))`
は、待ちを縮めたときに `currentSlideElapsedTime` が旧い上限（縮める前の
`span`）に張り付いていると、新しい（小さい）`span` へ切り下げられる。

実測（`currentSlideElapsedTime` を直接、縮める前の `span`（=21）へ
セットしてから `pauseSeconds` を 3→1 に変更）:

```
変更前: currentSlideElapsedTime=21  表示 0:21
変更後: currentSlideElapsedTime=19  表示 0:19
```

表示が 2 秒巻き戻る。ただし、これが自然な操作で実際に踏めるかは別で、
実際の待ち中は `currentSlideElapsedTime`（`playbackLoop` の実時間加算）と
`schedulePauseTransition()` の残り時間計算（`performance.now()` 基準）が
同じ壁時計を基準にしているため、通常は両者がほぼ同期したまま
（`slideSpan` の上限に張り付く瞬間＝ちょうど実際の遷移が起きる瞬間）で、
巻き戻りが目に見える窓は基本的に無いはずだと見ている。実際に自然な
再生（`setTimeout` の遅延・タブのバックグラウンド化などで遷移がわずかに
遅れる場合）で再現できるかは**未確認**（今回は `currentSlideElapsedTime`
を直接書き換えて上限に張り付いた状態を人工的に作った）。

## 問題なし・確認できた点

- **`totalDurationSeconds` / `slideStartTimes` を `let` にした影響は、
  読んでいる箇所（`updateProgressDisplay()`、`initPlaylist()`、シークバーの
  click、`pauseSelect` の change）のどれも古い値を掴んだままになる経路が
  無い。** すべてトップレベルの `let` を素の変数名で参照するクロージャで、
  `recalcTimeline()` の代入がそのまま全読者に伝わる（コピーして保持している
  箇所は無い）。`initPlaylist()` は `recalcTimeline()`（1199 行、モジュール
  読み込み時に 1 回実行）より後の `startApp()` から呼ばれる順序で、
  初回表示も正しい値を読む（実測: 初期表示 `5:51` = 351 秒 = `317 + 2×17`
  と一致）
- **待ち秒数の変更を実測。** 2→3 秒で合計時間表示が `5:51`→`6:08`
  （351→368 秒、`317 + 3×17` と一致）。verifier の実測と同じ結果
- **過剰な作りではない。** `slideSpan` は 1 行の arrow function、
  `recalcTimeline()` も既存の `accumTime` ループをそのまま関数に
  切り出しただけで、新しい抽象化や設定項目を足していない
- **コメントの調子は既存箇所と揃っている。** 新しいコメントはどれも
  「なぜ」（待ちも尺に含める、待ちを縮めたときに超えたままにしない、など）
  を短く書いており、削られた英語コメント（`Total calculated presentation
  duration` 等）も TODO-021 以降の日本語コメントへの置き換えの流れに沿っている
- **範囲は `claude_memo.html` のみ、かつ TODO-020 のチェックリスト 3 項目に
  対応する差分だけ。** 無関係な変更は見当たらない
- ミュート時の待ち（`speakCurrentNarration()` の `isMuted` 分岐）は
  `slide.duration` のみで待ち、`onSlideAudioFinished()` 経由で
  `schedulePauseTransition()` に入る経路は変わっていないので、TODO-020 で
  壊れていない
