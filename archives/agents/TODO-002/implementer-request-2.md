# TODO-002 実装依頼 その 2（implementer）

実機確認で、1 回目の修正では直っていないことが分かった。原因は **調査し直して
特定済み**（下記）。再調査はしなくてよい。対象は `claude_memo.html` のみ。

## 実機の症状（利用者・Android Chrome）

1. Web Speech: **約 15 秒で切れる**（5 秒ではない）
2. Online TTS: **全く鳴らない**
3. **PC でも Online TTS が鳴らなくなった**（以前は鳴っていた）

## 原因 1: Google Translate TTS は Referer を見て 404 を返す

1 回目の修正（`Audio` の unlock）は無関係だった。実測:

| 送るヘッダ | 応答 |
|---|---|
| Referer 無し | 200 `audio/mpeg` |
| `Referer: https://www.tanibayashi.jp/` | **404** `text/html` |
| `Referer: https://www.tanibayashi.jp/claude_memo.html` | **404** |
| User-Agent だけ / Sec-Fetch-* だけ | 200 |

ブラウザは既定の referrer policy（`strict-origin-when-cross-origin`）で
origin だけの Referer を必ず送るので、**PC でも Android でも 404 になる**。
`<audio>` 要素には `referrerpolicy` 属性が無いので、要素側では抑えられない。

**直し方**: `<head>` に `<meta name="referrer" content="no-referrer">` を足す。
ページ全体の Referer が止まるが、他は CDN（Tailwind・Google Fonts・
FontAwesome）への読み込みだけなので影響しない。

## 原因 2: Android Chrome にも「長い発話が 15 秒ほどで止まる」制限がある

1 回目で Android の `pause()`/`resume()` を止めたら、制限がそのまま出た。
**回避策を戻しても直らない**（Android では `resume()` で戻らない）。

**直し方**: 読み上げる文を**短く分けて順に読ませる**。
`speakCurrentNarration()` の Web Speech の分岐で、`prepareSpeechText()` の
結果を 1 つの `SpeechSynthesisUtterance` にせず、分割して順に `speak()` する。

- 区切りは `。` `、` `！` `？` の後ろ。1 つが長すぎるときはさらに切る。
  **1 つあたり 40 文字程度を上限**にする（既定速度で 10 秒弱に収まる）
- **最後の 1 つが読み終わったときだけ** `handleEnd()` を呼ぶ。
  途中のものは次を `speak()` するだけ
- 途中で `stopSpeech()` / 一時停止 / スライド移動が入ったら、
  **残りを読み始めない**（`window.speechSynthesis.cancel()` だけでは
  こちらのキューが動き続ける）
- `onerror` で Online TTS に落ちる既存の動きは残す。ただし
  **落ちるのは 1 回だけ**にすること（分割した数だけ落ちないように）
- safety timeout は分割後の全体の長さで計算し直す。
  文字数の合計は変わらないので、今の式のままでよい
- **`chromeResumeTimer` は要らなくなるので消す。** 分割すれば
  デスクトップ Chrome の 15 秒問題も起きない。`isAndroid` も使い道が
  無くなるなら消す。関連する `CLAUDE.md` の記述も直す
  （「Android では `chromeResumeTimer` を動かさない」の行）

## そのままにすること

- 1 回目で入れた `Audio` の unlock（`unlockFallbackAudio()`、要素の使い回し）は
  **残す**。Android の自動再生ポリシー対策として要る
- 180 文字の切り詰め、`duration` の扱い、他の機能は触らない

## 完了条件

- PC の Chrome で Web Speech / Online TTS の両方が鳴り、最後まで読む
- `<script>` に構文エラーが無い
- 差分は最小限。整形やリファクタリングを混ぜない

## 報告

`archives/agents/TODO-002/implementer-report-2.md` に、変更点・確認したこと・
残る懸念を書く。返事は 5 行以内。目安 20 分。
