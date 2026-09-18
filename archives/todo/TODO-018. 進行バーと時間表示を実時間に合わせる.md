# TODO-018. 進行バーと時間表示を実時間に合わせる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + reviewer |
| 実施 | Opus 5 / effort high | verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 23,168 | 39,141 | 57% |
| reviewer | Opus 5 | high | 21,116 | 59,213 | 31% |
| verifier | Sonnet 5 | medium | 14,979 | 67,603 | 12% |
| 合計 |  |  | 59,263 | 165,957 | 概算 $4.2 |

- reviewer は定義（`~/.claude/agents/reviewer.md`）のモデルが opus、
  `effort: high`。前提そのものを疑わせる担当なので上書きしなかった
- verifier は定義のまま（sonnet / medium）。2 回動かした分を合算している

## きっかけ

TODO-017 の確認中に、`total-time-display` の直書き `3:15` が実際の表示と
合っていないことが見つかった。調べると直書きは読み込み直後の一瞬しか見えず、
`initPlaylist()` が `duration` の合計で上書きしていた。

さらに `playbackLoop` が経過を `deltaTime * getEffectiveSpeed()`（1.4 倍）で
進めていた。`duration` は 1.4 倍速での読了時間に近いと**見立てた**ので、
1.4 を外せばバーが読み終わりにぴったり届くはず、と考えて着手した。

## やったこと

**この見立ては間違っていた。** reviewer が 17 枚のナレーションを
`prepareSpeechText()` にかけ、コードと同じ URL で Google Translate TTS から
実際に音声を取得して `ffprobe` で測ったところ、1.4 倍速での実再生は合計
316.2 秒で、`duration` の合計 214 秒の 1.48 倍あった（17 枚すべてで超過、
比 1.33〜1.73）。見立ての根拠にした「文字数から 7.5 文字/秒」は当てずっぽうで、
実測は 1.0 倍で 5.15 文字/秒だった。`duration` は手で振った尺の目安で、
読み上げの長さとは対応していなかった。

そこで次の 2 つを入れた。

1. **時間軸から 1.4 を外した。** `playbackLoop` の経過を
   `deltaTime * playbackRate` に変え、`duration` を待ち時間に使う 3 箇所
   （消音中・音声の `onerror`・`play()` の拒否）も `duration / playbackRate` に
   揃えた。読み上げの実速度（`utterance.rate`、
   `fallbackAudioElement.playbackRate`、Web Speech の安全タイマー）は
   `getEffectiveSpeed()` のまま
2. **`duration` を実測値に振り直した。** 17 枚を reviewer の実測（1.4 倍速での
   実再生秒数）の四捨五入に入れ替えた。合計 214 秒 → 317 秒（5:17）

`total-time-display` の直書きは `--:--` にした（`initPlaylist()` が
`duration` の合計で上書きするので、値を直書きしない）。
`CLAUDE.md` の再生ロジックの説明も実測に合わせ、併せて reviewer が見つけた
記述の誤り（安全タイマーは `duration` ではなく文字数から計算している、
Online TTS には安全タイマーが無い）と古い行番号も直した。

## 確かめたこと

verifier が 2 回確認した（報告は `archives/agents/TODO-018/`）。

- 1 回目: 差分が意図した 4 箇所に収まっていること、`getEffectiveSpeed()` が
  読み上げ側の 3 箇所に残っていること、`node` で経過が
  `duration / playbackRate` に一致すること、`node --check` の通過
- 2 回目: `duration` 17 件が reviewer の実測の四捨五入と 1 件ずつ一致し、
  合計 317 秒・`formatTime(317)` = `5:17` になること。`duration` 以外
  （`id` / `category` / `title` / `narration` / `render`）に差分が無いこと。
  `CLAUDE.md` の書き換え 4 点が実装と合っていること

## 残ること

- **Web Speech に切り替えるとバーとずれる。** `duration` は Online TTS の
  実測値なので、OS の音声で読むとスライドごとの長さが変わる。
  実測はこの環境からはできない
- **`playbackRate` が 1.5 以上のとき、音声の速度が上限 2.0 で頭打ちになる**
  （`Math.min(2.0, getEffectiveSpeed())`）。1.5x / 1.75x / 2.0x は耳で同じ
  速さなのに、時間軸だけがそれぞれの倍率で進む。変更前からある
- **再生中の速度切り替えとシークで、音声が頭から鳴り直すのにバーは据え置き**
  （`currentSlideElapsedTime` をリセットするのは `renderSlide(i, true)` だけ）。
  変更前からある
- **Online TTS に安全タイマーが無い**件は TODO-019 として別に立てた

## 分担の振り返り

- **reviewer が前提を覆した。** 「`duration` は 1.4 倍速での読了時間」という
  main の見立てを、実際に TTS の音声を取得して `ffprobe` で測ることで否定した。
  文字数からの見積もりでは一致して見えたので、実測しない限り気付けなかった。
  指摘は要修正 4 件・検討 4 件で、`CLAUDE.md` の既存の誤記（安全タイマーの
  説明）まで拾っている
- verifier は 2 回とも指示した数字を実測で返した。ただし**前提を疑う動きは
  していない**。1 回目は「経過が `duration / playbackRate` に一致する」ことを
  確かめており、それは指示どおりだが、その `duration` 自体が実態と合って
  いるかは見ていない。確認とレビューを分けた意味がそのまま出た
- 見込み（verifier + reviewer）と食い違わなかった。ただし**巡り直しが 1 回
  増えた**。前提の実測を、実装のあとではなく着手前に済ませていれば、
  1 回目の実装・確認・レビューは要らなかった
- **次に同じ規模をやるなら、実測で確かめられる前提は着手前に測らせる。**
  「`duration` は読了時間らしい」と見立てた時点で、実装の前に reviewer か
  verifier へ実測だけを頼むべきだった。今回の料金 $4.2 のうち、1 回目の
  実装とその確認（main の一部と verifier の 1 回目）は前提が違った分の
  やり直しになっている
