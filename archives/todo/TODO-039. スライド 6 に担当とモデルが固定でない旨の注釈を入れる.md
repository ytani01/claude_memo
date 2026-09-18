# TODO-039. スライド 6 に担当とモデルが固定でない旨の注釈を入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 8,575 | 26,060 | 73% |
| verifier | Sonnet 5 | medium | 8,612 | 54,180 | 27% |
| 合計 |  |  | 17,187 | 80,240 | 概算 $1.8 |

- verifier は定義（`~/.claude/agents/verifier.md`）のまま Sonnet 5 / effort
  medium。表示確認と秒数の測定だけなので上書きしていない
- main の effort は利用者の設定が high だったため、見込みの medium と違う

## きっかけ

スライド 6「マルチエージェントで役割分担」の表は、担当ごとにモデルが
固定で決まっているように読める。実際はタスクの内容に応じて main が
選んでいるので、その旨を注釈で補うことにした。

## やったこと

`claude_memo.html` のスライド 6（`id: 6`）だけを変えた。

- 4 項目の表の下に注釈を 1 行足した。最初は小さい灰色の文字にしたが、
  利用者から「もっと目立たせて」と言われ、lime の枠付き・太字・中央寄せ、
  文字サイズ `clamp(1.0rem, 2.0cqw, 1.4rem)` に直した
- ナレーション末尾を「直接ファイルを編集できるのは main と implementer
  だけに制限しています。ただし、担当とモデルは固定ではなく、タスクの
  内容に応じて main が判断します。」に差し替えた
- `duration` を 19 から 23 に直した

## 確かめたこと

verifier が確認した（`archives/agents/TODO-039/verifier-report.md`）。

- `tools/measure-duration.py 6` — 読み 171 字（`TTS_MAX_CHARS` の 180 未満で
  切れない）、実測 32.472s、1.4 倍速で 23.19s → `duration` は 23
- 1280x720（PC）と 844x390（横持ちスマホ、Playwright の `hasTouch` /
  `isMobile` で `pointer: coarse` を模擬）の両方で、注釈まで枠内に収まり、
  本文の切れもはみ出しも無い

## 分担の振り返り

- verifier は `duration` が 19 のままずれていることを見つけた。秒数を測る
  手順があるので、ここは main が省きやすいところだった。844x390 で
  `hasTouch` を付けないと `pointer: coarse` のメディアクエリが効かず
  誤ってはみ出して見える、という条件も押さえていた
- 見込みと食い違わなかった。文言とスタイルの変更だけなので implementer は
  立てず、挙動や分岐が変わらないので reviewer も立てていない
- 次に同じ規模（1 スライドの文言と見た目の変更）をやるなら、同じく
  main + verifier で足りる。verifier への依頼に、測る画面サイズと
  `pointer: coarse` を模す必要があることを最初から書いておくと、
  撮り直しの 1 往復を減らせる
