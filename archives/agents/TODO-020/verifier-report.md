# TODO-020 verifier 報告

## 対象
`claude_memo.html` の未コミット差分（`git diff` 41 行、1 ファイルのみ）。
指示範囲どおり、変更ファイルはこの 1 つだけ。他のファイルへの変更なし
（`git status` で確認済み）。

## 検証方法
python の `playwright`（Chromium, headless）で `file://` から実ページを開き、
ブラウザ内の JS 変数・DOM を直接 `page.evaluate` で読み書きして実測した。
Node 版 playwright は未インストールだったため python 版（1.63.0、
インストール済み）を使用。スクリプトは
`/tmp/claude-649/.../scratchpad/verify_todo020.py` と
`verify_todo020_pause.py`（作業ディレクトリ外の scratchpad に保存、
リポジトリには残していない）。

## 完了条件ごとの確認結果

### 1. slideSpan() = duration + pauseSeconds、頭打ちが slideSpan() になっている
コード上、`playbackLoop()` の頭打ちが
`const span = slideSpan(currentIndex); if (currentSlideElapsedTime > span) ...`
に変わっている（`claude_memo.html` 1571 行付近）。実測でも確認:

```
slide 0: duration=18 span=20 span-dur=2
slide 1: duration=19 span=21 span-dur=2
```

`pauseSeconds`（既定値 2）が正しく加算されている。

### 2. 合計時間に 待ち秒数 × 枚数 が足されている
実測（実際のスライド枚数は 14 ではなく 17 枚だった）:

```
n_slides: 17
pauseSeconds: 2
totalDurationSeconds: 351
raw duration sum (durationのみの合計): 317
351 - 317 = 34 = 2 × 17  … 一致
```

プルダウンを 3 秒に変えたときも:

```
after change to 3s -> totalDurationSeconds: 368
368 - 317 = 51 = 3 × 17  … 一致
```

枚数は指示文の「14 枚なら」という想定と異なるが、式（待ち秒数 × 枚数）は
両方の待ち秒数で計算どおりに成立している。

### 3. 待ち秒数のプルダウンを変えると合計時間表示と進行バーがその場で更新される
`pauseSelect` の `change` イベントに `recalcTimeline()` の呼び出しと
`totalTimeDisplay.textContent = formatTime(totalDurationSeconds)` および
`updateProgressDisplay()` が追加されている。実測:

```
total-time-display text (before change, pause=2s): 5:51
total-time-display text (after change to 3s):      6:08
```

5:51 → 351 秒、6:08 → 368 秒で、上の 2. の計算と一致。`change` の場で
即座に更新されることを確認した。

### 4. 読み終わりから次のスライドへ移るまでの間、進行バーと時間表示が止まらない
`playbackLoop()` は `isPlaying` の間ずっと `requestAnimationFrame` で回り
続けており、待ち中（`pauseStartedAt !== null` の間）も止める分岐が無い。
実際に `isPlaying=true` にして `onSlideAudioFinished()`（＝ナレーション終了の
本物のハンドラ）を呼び、150ms おきに `current-time-display` の文字列と
`progress-bar` の width をサンプリングした（スライド 0: duration=18,
pauseSeconds=2, span=20）。

```
elapsed=18.03 display=0:18 width=5.13769% pauseStartedAt=None      (待ち開始直前)
elapsed=18.18 display=0:18 width=5.18043% pauseStartedAt=1334.7    (待ち中)
elapsed=18.33 display=0:18 width=5.22316% pauseStartedAt=1334.7
elapsed=18.48 display=0:18 width=5.26590% pauseStartedAt=1334.7
elapsed=18.63 display=0:18 width=5.30863% pauseStartedAt=1334.7
elapsed=18.78 display=0:18 width=5.35134% pauseStartedAt=1334.7
elapsed=18.93 display=0:18 width=5.39410% pauseStartedAt=1334.7
elapsed=19.08 display=0:19 width=5.43681% pauseStartedAt=1334.7
elapsed=19.23 display=0:19 width=5.47957% pauseStartedAt=1334.7
elapsed=19.38 display=0:19 width=5.52231% pauseStartedAt=1334.7
elapsed=19.53 display=0:19 width=5.56501% pauseStartedAt=1334.7
elapsed=19.68 display=0:19 width=5.60775% pauseStartedAt=1334.7
elapsed=19.83 display=0:19 width=5.65048% pauseStartedAt=1334.7
elapsed=19.98 display=0:19 width=5.69322% pauseStartedAt=1334.7    (待ち終わり直前、20 で頭打ち)
elapsed=0.10  display=0:20 width=5.72650% pauseStartedAt=None      (次スライドへ遷移後)
elapsed=0.25  display=0:20 width=5.76923% pauseStartedAt=None
elapsed=0.40  display=0:20 width=5.81197% pauseStartedAt=None
elapsed=0.55  display=0:20 width=5.85470% pauseStartedAt=None
```

`pauseStartedAt` が非 null（待ち中）の間も `elapsed` と `width` が単調に
増え続けており、止まっていない。20 秒（span）で頭打ちになった直後に
次のスライドへ切り替わる（`slideTransitionTimeout` の遷移）ことも確認できた。

## 判断できなかったこと・確かめられなかったこと
- 実際のナレーション音声（Online TTS / Web Speech）を鳴らした状態での
  エンドツーエンドの再生は試していない（環境に音声出力が無いため）。
  今回は `onSlideAudioFinished()` を直接呼ぶ形で「ナレーションが終わった
  直後」の状態を作って確認した。音声再生自体の正しさは今回の確認対象
  （TODO-020）ではないため対象外とした。
- モバイル実機・タッチ操作での見え方は確認していない（今回の指示にも
  含まれていない）。
- 品質面（コードの良し悪し、設計判断の妥当性）は reviewer の担当なので
  踏み込んでいない。

## 変更ファイルの範囲
`git status` / `git diff` ともに `claude_memo.html` のみが変更対象。
指示された対象範囲と一致している。
