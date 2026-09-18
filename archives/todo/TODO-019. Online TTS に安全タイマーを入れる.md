# TODO-019. Online TTS に安全タイマーを入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | verifier |
| 実施 | Opus 5 / effort high | verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 20,919 | 74,411 | 62% |
| verifier | Sonnet 5 | medium | 30,219 | 66,524 | 23% |
| reviewer | Sonnet 5 | high | 29,687 | 63,682 | 15% |
| 合計 |  |  | 80,825 | 204,617 | 概算 $3.7 |

- 見込みは verifier だけだったが、挙動が変わる項目なので着手時に reviewer を
  足した（利用者に確認して決めた）
- verifier は定義のモデルが sonnet。同じ Sonnet 5 のまま使った。
  reviewer も定義のまま（effort は定義の `high`）
- 集計の範囲（17:14〜17:35）には、TODO-020 と TODO-021 を立てたやり取りも
  入っている。TODO-019 だけの分はこれより少ない

## きっかけ

TODO-018 のレビューで reviewer が見つけた。`speakOnlineTTS()` が持つのは
`onended`・`onerror`・`play()` の拒否の 3 つだけで、通信が途中で止まって
`onended` が来ない場合の受け皿が無かった。既定の読み上げは Online TTS なので、
その状態になるとバーが `duration` で頭打ちのまま止まり続ける。
Web Speech 側には文字数から計算した安全タイマーがあった。

## やったこと

`claude_memo.html` の `speakOnlineTTS()` と `stopSpeech()`。

- 待ち時間の張り直しを `setEndTimeout()` にまとめ、`onerror` と
  `play()` 拒否の経路もそこを通るようにした
- 安全タイマーを追加。まずスライドの `duration / playbackRate` + 3 秒で張り、
  `loadedmetadata` で音声の実長が取れたら
  実長 / 再生速度 + 3 秒に張り直す
- 使い回す `<audio>` 要素なので、`onloadedmetadata` も `stopSpeech()` と
  `src` 差し替えのときに `null` にする
- reviewer の指摘 2 件に対し、`setEndTimeout()` の先頭に
  `if (finished || runId !== speechRunId) return;` を足した。
  `slideTransitionTimeout` は「次のスライドへの待ち」と共用なので、
  読了後や古い呼び出しから張り直すと、そちらを消してしまう
- `CLAUDE.md` の読み上げの説明を、実装に合わせて書き直した

待ち時間の基準は「音声の実長 + 3 秒、取れなければスライドの `duration`」に
決めた（2026-09-18、利用者と相談）。`onerror` と `play()` 拒否の待ち時間は
従来どおり変えていない。

## 確かめたこと

verifier がヘッドレス Chromium + Playwright で実測した
（`archives/agents/TODO-019/verifier-report.md`、`verifier-report-2.md`）。

- `onended` が来なくても、音声の実長 + 3 秒で次へ進む
- 実長が取れないときは、スライドの想定秒数 + 3 秒で進む
- `onended` が正常に来たときに二重に進まない
- `stopSpeech()` の後にタイマーが残って勝手に進むことがない
- `onerror` / `play()` 拒否の待ち時間が従来と同じ
- 修正後: 遅れて来た `onloadedmetadata` も、古い `play().catch()` も、
  次のスライドへの待ちタイマーを壊さない

後ろ 2 つは自然には再現できず、合成イベントと `play()` の差し替えで
再現している。

## 分担の振り返り

- **reviewer が見つけたもの**: 共用している `slideTransitionTimeout` を、
  遅れて来た `onloadedmetadata` と古い `play().catch()` が上書きして
  「次のスライドへ進む」を握り潰す経路 2 件。どちらもコード読解で、
  テストでは出ない種類の指摘だった。`CLAUDE.md` の説明が実装と食い違う
  ことにも気づいた
- **verifier が見つけたもの**: 完了条件はすべて実測で通した。
  指摘としての発見は無い。ただし修正後の再確認で、合成イベントを使ってでも
  再現する形に持ち込んだのは verifier の仕事
- **見込みとの食い違い**: 見込みは verifier だけだった。実際には
  reviewer の 2 件が無ければ、テストが全部通ったまま握り潰しの経路が残った。
  10 行程度の差分でも、分岐が増えるなら reviewer を外さないこと
- **次に同じ規模なら**: 同じ組み方でよい。ただし reviewer を先に走らせ、
  指摘を反映してから verifier を 1 回だけ回すほうが安い。今回は並行させた
  ため verifier を 2 回走らせている（$0.8 のうち後半が再確認分）
