# TODO-002. Android Chrome での読み上げを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | 調査 = main（済） / 実装 = implementer / 確認 = verifier / レビュー = reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer（実装・確認・レビューを 2 巡） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 36,492 | 105,121 | 50% |
| reviewer | Opus 5 | high | 41,567 | 106,053 | 25% |
| verifier | Sonnet 5 | medium | 34,296 | 153,546 | 13% |
| implementer | Opus 5 | medium | 15,406 | 65,899 | 12% |
| 合計 |  |  | 127,761 | 430,619 | 概算 $9.3 |

- implementer と reviewer は定義のモデルが sonnet。原因の切り分けと分岐の
  レビューが要るので Opus 5 に上書きした
- 集計の範囲は `--since '2026-09-18 04:32:22'`（TODO-001 の決着コミット）から。
  **調査の分は入っていない。** 調査は TODO-001 の作業と重なる時間帯に
  main がやったので、TODO-001 側の集計に含まれている

## きっかけ

スマホ（Android, Chrome）での音声再生が未検証だった。利用者の実機確認で、
2 系統とも壊れていることが分かった。

- Web Speech API: 途中で途切れる
- Online TTS: そもそも音が出ない

## やったこと

**原因の見立てを 2 回外し、3 巡目で直した。**

### 1 巡目（コミット `5a171bd`）— 外れ

調査メモ（`archives/agents/TODO-002/main-investigation.md`）の見立てに沿って
直したが、実機では何も変わらなかった。

- `chromeResumeTimer` の 5 秒ごとの `pause()`/`resume()` を Android で
  止めた → 実際に切れるのは 15 秒だった
- 再生ボタンで `Audio` 要素を 1 つ unlock し、使い回すようにした →
  自動再生のブロックではなかった

実機の結果は「Web Speech は約 15 秒で切れる」「Online TTS は鳴らない」、
さらに **PC でも Online TTS が鳴らなくなった**（回帰ではなく、
もともと鳴らなくなっていたものに気づいた）。

### 2 巡目（コミット `acf6ad1`）— 当たり

実測で原因を 2 つ特定した。

**Online TTS**: Google Translate TTS は **Referer が付いた要求に 404 を返す**。

| 送るヘッダ | 応答 |
|---|---|
| Referer 無し | 200 `audio/mpeg` |
| `Referer: https://www.tanibayashi.jp/`（origin だけ） | 404 `text/html` |
| User-Agent だけ / Sec-Fetch-* だけ | 200 |

ブラウザは既定の referrer policy（`strict-origin-when-cross-origin`）で
origin の Referer を必ず送るので、PC でも Android でも鳴らない。
`<audio>` 要素には `referrerpolicy` 属性が無いので、`<head>` に
`<meta name="referrer" content="no-referrer">` を置いてページ全体で止めた。

**Web Speech**: Chrome は **PC も Android も**、長い発話を 15 秒ほどで
打ち切る。`splitForSpeech()` で 40 文字程度に分け、順に読ませる。

- 区切りは `。、！？` の後ろ。20 文字たまってから切る
- 40 文字で強制的に切るが、**英単語の途中と句読点の直前では切らない**
  （`codegraph` が `codegr` / `aph` に割れていた）
- `stopSpeech()` で `speechRunId` を進め、古い run のキューが動き続けないようにした
- Android だけ `pause()`/`resume()` を止める回避策（`chromeResumeTimer`）は
  不要になったので削除した

1 巡目で入れた `Audio` の unlock は、原因ではなかったが残してある。

## 確かめたこと

- **利用者の実機確認**（決め手）。Android Chrome で Web Speech が最後まで
  読み切り、Online TTS も鳴ること、PC でも両方鳴ることを確認した
- `splitForSpeech()` を 17 枚の `narration`（`prepareSpeechText()` を通した後）に
  かけて、文字の欠落・重複が 0、英単語が割れる箇所が 0、チャンクが
  句読点で始まる箇所が 0 であることを確認した。チャンクの最大長は 41 文字
- `curl` で Referer の有無による 404 / 200 を再現した
- Playwright で、`no-referrer` を入れたページから `translate_tts` が
  200 `audio/mpeg` を返すことを確認した
- `<script>` の中身を抜き出して `node --check`（終了コード 0）

**ヘッドレスのブラウザでは読み上げそのものを確かめられなかった。**
日本語の音声エンジンが無く（`voices` が 0 件）、外部の音声も読み込めない。
この環境には `espeak` / `spd-say` も入っていない。読み上げの確認は
実機だけが判定できる。

## 見送ったこと

`archives/agents/TODO-002/reviewer-report-2.md` の検討 3・好みの範囲。

- **safety timeout の余裕をチャンク間の間（ま）が食う。** 最大 6 分割で、
  間 1 つあたりの余裕は 600ms。実機で切れなかったのでそのままにした
- **`speechActive` がどこからも読まれない。** 変更前からで、今回の差分の
  責任ではない

## 分担の振り返り

**各担当が何を見つけたか**

- **reviewer** が一番効いた。2 巡目で要修正 2 件を出し、どちらも実データで
  裏を取っていた（`codegraph` が割れる箇所を実際に分割して見つけた、
  最後のチャンクの `onend` だけ `runId` の判定が漏れている経路を
  コードを追って特定した）。1 巡目でも「実装担当が懸念に挙げた競合は
  起きない」ことを chromium で実測して潰している
- **verifier** は「依頼どおりか」は確実に見たが、**症状が直ったかは
  一度も見られなかった**。1 巡目で「すべて確認済み・問題なし」と報告した
  ものが実機では直っていない。音を鳴らす手段が無い以上、この項目では
  構造的にそうなる
- **implementer** は依頼書どおりに実装した。原因が合っていれば速い
- **main が 1 巡目の原因を外した。** 調査メモの見立てをそのまま依頼書に
  写し、確かめ直さなかった。誤りの根は、調査のときに `curl` を
  **Referer 無しで**叩いて「Google 側のブロックではない」と結論したこと

**見込みと食い違った理由**

分担そのものは見込みどおりで、食い違ったのは**巡数**。1 巡で終わる
つもりが 2 巡かかり、料金は $9.3 になった。原因は分担ではなく、
**原因の見立てを確かめる工程が誰にも割り当てられていなかった**こと。
実装・確認・レビューはすべて「依頼書の原因が正しい」前提で動く。

**次に同じ規模の項目をやるなら**

- **外部サービスを叩く確認は、ブラウザと同じヘッダで試す。** 今回の
  無駄（1 巡目まるごと、$4 前後）はこの 1 点から出た
- **実機でしか判定できない項目は、直す前に症状を数値で聞く。**
  「途中で切れる」ではなく「何秒で切れるか」。今回、5 秒と 15 秒の
  取り違えが 1 巡分の差になった
- **確認の担当が症状を再現できない項目では、そのことを依頼書に明記して、
  確認の範囲を「依頼どおりか」に限る。** 今回の verifier の
  「問題なし」は、範囲を誤解させる報告になった
- reviewer に Opus を充てたのは正解。この項目で唯一、実装の中身に
  踏み込んだ指摘を出した担当だった
