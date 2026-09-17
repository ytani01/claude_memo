# TODO-002 実装報告 その 2（implementer）

対象は `claude_memo.html` のみ。1 回目のコミット（5a171bd）の上に足した。

## 変更点

- `claude_memo.html:6-7` — `<head>` に
  `<meta name="referrer" content="no-referrer">` を追加（コメント 1 行付き）。
  Google Translate TTS が Referer 付きだと 404 を返す件の対処
- `claude_memo.html:1119-1120` — `chromeResumeTimer` と `isAndroid` を削除し、
  `speechRunId`（読み上げの世代番号）に置き換え
- `claude_memo.html:1214-1228` — `splitForSpeech(text, maxLen = 40, minLen = 20)`
  を追加。20 文字以上たまったところで `。、！？` の後ろで切り、
  40 文字に達したら強制的に切る。分割は無損失（連結すると元に戻る）
- `claude_memo.html:1240` — `stopSpeech()` の `chromeResumeTimer` 停止を
  `speechRunId++` に置き換え。停止・一時停止・スライド移動が入ると、
  走っているチャンクのキューが次を `speak()` しなくなる
- `claude_memo.html:1279` — `speakCurrentNarration()` の冒頭（`stopSpeech()` の
  直後）で `runId` を捕まえる
- `claude_memo.html:1303-1378` — Web Speech の分岐を書き換え。
  音声の選択は 1 回だけ行い、`speakChunk(i)` が 1 チャンクずつ `speak()` して
  `onend` で次を呼ぶ。**最後のチャンクの `onend` だけ** `handleEnd()`
  （＝`onSlideAudioFinished()`）を呼ぶ。`onerror` は `finished` フラグで
  1 回だけ `speakOnlineTTS(textToSpeak)` に落ちる。safety timeout は元の式
  （全文の文字数）のまま、`runId` の一致も条件に加えた

`unlockFallbackAudio()` と `fallbackAudioElement` の使い回し、180 文字の
切り詰め、`duration` の扱いは触っていない。

## 検証

| 内容 | コマンド | 結果 |
|---|---|---|
| `<script>` の構文 | 本体の `<script>` を抜き出して `node --check` | OK（終了コード 0） |
| 分割の動作 | `splitForSpeech` を抜き出し、実際の `narration` 17 本に適用 | 無損失。チャンク長 13〜40 文字、最大 6 チャンク |
| Referer の影響 | `curl` で Google Translate TTS を Referer 有無で比較 | 無し 200 `audio/mpeg` / 有り 404 `text/html`（依頼書の実測と一致） |

ブラウザでの実再生（PC Chrome で Web Speech / Online TTS が最後まで鳴るか）は
こちらでは確認できていない。確認の担当・利用者の実機確認が要る。

## 残る懸念・範囲外

- **`CLAUDE.md` の「Android では `chromeResumeTimer` を動かさない」の行
  （71-73 行）が実体と合わなくなった。** 依頼書には直すよう書かれていたが、
  実装担当は文書を触らない決まりなので**直していない**。管理者側で更新が要る
- 40 文字での強制分割は文の途中で切れることがあり、そこにわずかな間が入る
  （例: 「…Claude Code の」／「具体的な使い方や…」）。読み上げは続くが、
  気になるなら区切り文字に `・` や空白を足すなどの調整が要る
- `no-referrer` はページ全体に効く。CDN（Tailwind・Google Fonts・
  FontAwesome）は Referer 無しでも配信されるが、今後アクセス解析や
  Referer を見る外部サービスを足すときは影響する
- 分割により 1 スライドの発話が複数回に分かれるので、`onstart` の
  「朗読中 (Web Speech)」表示はチャンクごとに走る（表示は同じなので実害なし）
