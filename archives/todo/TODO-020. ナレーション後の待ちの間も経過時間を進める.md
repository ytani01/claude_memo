# TODO-020. ナレーション後の待ちの間も経過時間を進める

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + reviewer |
| 実施 | Opus 5 / effort high | verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 7,252 | 11,962 | 43% |
| reviewer | Sonnet 5 | high | 31,308 | 77,484 | 43% |
| verifier | Sonnet 5 | medium | 7,605 | 29,638 | 13% |
| 合計 |  |  | 46,165 | 119,084 | 概算 $1.8 |

- 担当は 2 つとも定義のまま（`~/.claude/agents/`）

## きっかけ

ナレーションが終わってからスライドを切り替えるまでの間、進行バーと時間表示が
止まって見えていた。`playbackLoop()` が `currentSlideElapsedTime` をそのスライドの
`duration` で頭打ちにしており、`totalDurationSeconds` にも待ちの分が入って
いなかったため。

待ちも各スライドの尺に含める方針にした。待ち秒数は TODO-021 で選べるように
したので、その値を参照する（決め打ちにしない）。

## やったこと

`claude_memo.html` のみ。

- `slideSpan(index)` を足した（`duration` ＋ `pauseSeconds`）
- `totalDurationSeconds` と `slideStartTimes` を `const` から `let` に変え、
  `recalcTimeline()` で組み直せるようにした
- `playbackLoop()` の頭打ちを `duration` から `slideSpan()` に変えた
- 待ち秒数のプルダウンの `change` で `recalcTimeline()` を呼び、合計時間の
  表示と進行バーを張り直す。待ちを縮めたときに経過が新しい尺を超えたままに
  ならないよう、そこで頭打ちも掛け直す

## 確かめたこと

verifier が Playwright（Chromium, headless）で `file://` を開いて実測した。

- `slideSpan()` が各スライドで `duration + 2` になっている
- 全 17 枚。`duration` の合計 317 秒に対し `totalDurationSeconds` は 351 秒
  （差 34 秒 ＝ 2 秒 × 17 枚）。3 秒に変えると 368 秒（差 51 秒 ＝ 3 秒 × 17 枚）
- 合計時間の表示が 5:51 → 6:08 にその場で変わる
- 待ちの間も時間表示が増え続け、止まらない

reviewer の指摘は要修正 0 件。

## 分担の振り返り

分担は `archives/agents/TODO-020/README.md`。

- **reviewer だけが見つけたもの**: 待ちが尺に入ったことで、シークバーで
  「ナレーションの無い区間」を指せるようになった。そこを指すとナレーションが
  最初から鳴り直し、バーは実際の終了より早く頭打ちに見える。チェックリストに
  シークの記述が無かったので verifier は触れていない
- **見込みとの差**: 顔ぶれは見込みどおりで 1 巡で済んだ。TODO-021 で
  「Playwright で実測できる」と依頼文に書く形にしたのがそのまま効き、
  verifier が最初から実測して返した（TODO-021 は 1 巡目が静的確認だけだった）
- reviewer が料金の 43% を占めた。シークの経路を実測で追ったぶんで、
  実際にそこから唯一の指摘が出ているので削りどころではない
- **次に同じ規模なら**: この 3 者・1 巡で足りる。依頼文に「実測の手段はある」と
  「チェックリストの外で気づいた挙動も挙げてよい」を書いておくこと

## 残ること

シークバーで待ちの区間を指したときの振る舞いは、今回は対応しないと決めた
（2026-09-18）。TODO-020 のチェックリストは満たしており、待ちの区間は全体の
2 割弱で、指してもそのスライドの頭から読み直すだけのため。
