# TODO-002 確認報告 その 2（verifier）

対象: `claude_memo.html` と `CLAUDE.md` の 2 回目の修正（`git diff`）。
コードは変更していない。

## 1. 依頼書の直し方 2 つが入っているか

- `<meta name="referrer" content="no-referrer">` — `claude_memo.html:6-7` に
  `<head>` 内で確認した。コメント付き
- 読み上げの分割（`splitForSpeech()`）— `claude_memo.html:1212-1225` に実装、
  `speakCurrentNarration()`（1303〜）で `speakChunk(i)` として使われている
- `chromeResumeTimer` と `isAndroid` は `grep` で 0 件。残っていない

**結果: 両方入っている。**

## 2. `splitForSpeech()` の無損失性（17 枚全部）

`prepareSpeechText()` を通した後の 17 本の `narration` に実際の
`splitForSpeech()` をそのまま適用し、`chunks.join('') === text` を確認する
スクリプトを実行した。

```
#1 len=123 chunks=4 lossless=true
...(17 本すべて)...
#17 len=164 chunks=5 lossless=true
ALL LOSSLESS: true maxChunkLen: 40 maxChunks: 6
```

**結果: 17 枚すべてで文字を落とさず・重複させない。** 実装報告の数値
（チャンク長 13〜40 文字、最大 6 チャンク）とも一致。

## 3. `speechRunId` による打ち切り

コードを読んだ範囲では:

- 一時停止（`pausePresentation()` → `stopSpeech()` → `speechRunId++`）
- スライド送り（`renderSlide()` は `isPlaying` のときだけ
  `speakCurrentNarration()` を呼び、その内部で `stopSpeech()` が先に走る。
  `isPlaying` が false のとき＝そもそも読み上げていないので問題にならない）
- 音声エンジン切替（`toggleVoiceEngineBtn` のクリックで
  `speakCurrentNarration()` を直接呼ぶ＝内部で `stopSpeech()`）
- ミュート（`muteBtn` のクリックで明示的に `stopSpeech()`）

のいずれも `speechRunId` を更新する経路を通る。`speakChunk()` 内で
`runId !== speechRunId` を見て次のチャンクを話さない実装も確認した。

Playwright で実際にクリック（8 秒後にミュート on/off、8 秒後に次スライド、
8 秒後に音声エンジン切替）を連続して走らせたが、`pageerror` は 0 件、
コンソールの "falling back to Online TTS" も各操作につき 1 回ずつで、
多重フォールバックや例外は出なかった。

**ただし、この環境には TTS 音声エンジン（espeak 等）が入っておらず、
Chromium の `speechSynthesis.getVoices()` は 0 件だった。** そのため
Web Speech は毎回即座に `onerror` になり Online TTS へ落ちる。
「前のスライドの残りが Web Speech で読み始められないか」は
**この環境では実際の音声チャンクの継続で確かめられていない**（コードの
読み取りと、例外が出ないことの確認どまり）。判断は管理者かブラウザに
音声合成が入った環境での実機確認に委ねる。

## 4. safety timeout が分割後も足りるか

式は変更されておらず、全文の文字数ベースのまま
（`Math.max(6000, (textToSpeak.length / 4.5 / getEffectiveSpeed()) * 1000 + 3000)`）。
分割によってチャンク間に実際の発話の隙間（ブラウザの実装依存）が入るが、
**この環境では音声エンジンが無く実測できない**（3 と同じ理由）。
実装報告も「ブラウザでの実再生は確認できていない」としており、ここは
**未確認のまま**。実機（音声の鳴る環境）での実測が必要。

## 5. `<script>` の構文エラー

2 つの `<script>` のうち大きい方（87,467 文字）を抜き出して
`node --check` を実行し、終了コード 0 を確認した。

## 6. `CLAUDE.md` の記述がコードと合っているか

`git diff CLAUDE.md` は `chromeResumeTimer` の記述を、
`splitForSpeech()` と `no-referrer` の 2 項目に置き換えている。
コードの実態（`chromeResumeTimer`/`isAndroid` の削除、`splitForSpeech()`
の追加、`no-referrer` の追加）と一致する。
（実装報告では「文書は実装担当の対象外なので直していない」とあったが、
この diff には反映済み。誰が直したかは分からないが内容は合っている）

## 7. ブラウザで実際に再生して確かめる

Playwright（Chromium, headed, X 転送先 `DISPLAY=localhost:10.0`）で
`http://localhost:8791/claude_memo.html` を開き、再生ボタンをクリックした。

- **Online TTS: 鳴る経路を確認した。** `translate_tts` への要求はすべて
  `200 audio/mpeg` で返った（4 件、Referer 無しで成功。`no-referrer` の
  効果を実地で確認）。この環境はヘッドレス音声デバイスが無いため
  「実際に音が聞こえるか」までは確認できないが、404 は一件も出ていない
- **Web Speech: 最後まで読むかは確認できていない。** 上記のとおり
  この環境に TTS 音声が無く（`getVoices()` が 0 件）、`speak()` を呼ぶと
  即座に `onerror` になり Online TTS に自動で落ちるため、Web Speech の
  実際の発話・チャンク送りは試せなかった
- `pageerror` は一連の操作（再生→ミュート on/off→次スライド→音声エンジン
  切替）を通じて 0 件

## 変更ファイルの範囲

`git status` / `git diff --stat`:

```
 CLAUDE.md        |   9 +++--
 claude_memo.html | 106 ++++++++++++++++++++++++++++++-------------------------
```

依頼書（`claude_memo.html` のみを対象とし、文書は「関連する `CLAUDE.md`
の記述も直す」と明示）の範囲と合っている。範囲外のファイルの変更は無い。

## 確かめられなかったこと・判断できないこと

- **音声エンジン（espeak 等）が無い作業環境のため、Web Speech の実際の
  発話・15 秒制限の回避・安全タイムアウトの妥当性は実測できていない。**
  実装報告も同様に「ブラウザでの実再生は確認できていない」としている。
  ここは**利用者の実機（PC Chrome、できれば Android Chrome も）での
  確認が必須**。特に「safety timeout が分割後の実際の間隔を含めて足りるか」
  は数値でしか裏付けが無い
- 40 文字での強制分割が文の途中で切れる件（実装報告に記載）は、
  読み上げの自然さの問題であり、依頼の完了条件には入っていないため
  ここでは確認していない

## 追加確認（レビューの要修正 2 件）

### 1. `splitForSpeech()` の強制切りの見直し

17 本の `narration` を `prepareSpeechText()` に通してから、実際の
`splitForSpeech()`（英単語の途中・句読点の直前では切らない版）をそのまま
適用して確認した。

- **(a) 文字の欠落・重複**: 17 本すべて `chunks.join('') === text` で一致。
  欠落・重複なし
- **(b) 英単語が割れる箇所**: 0 件。チャンクの末尾が英数字で、次のチャンクの
  先頭も英数字になる箇所（＝単語の途中で切れた箇所）を全 17 本・全チャンク
  境界で調べたが 0 件だった
- **(c) `、`/`。` で始まるチャンク**: 0 件。全チャンクの先頭 1 文字が
  `、。！？` のいずれかになる箇所は無かった
- **(d) チャンクの最大長**: 全体で **41 文字**（#2, #9, #11 の 3 本で
  1 チャンクが 41 文字になった）。他は 40 文字以下（32〜40 文字）。
  40 文字ちょうどで単語・句読点の条件に触れず切れたケースが大半で、
  条件に触れて 1 文字だけ延びたケースが 3 件、というところまでは伸びたが
  それ以上（42 文字以上）には伸びていない

### 2. `handleEnd()` への `runId !== speechRunId` 判定

`handleEnd` の呼び出し元は Web Speech の分岐内で 2 か所のみ
（`claude_memo.html:1360` 最後のチャンクの `onend`、`1382` の safety
timeout）。どちらも既存のガード（`isPlaying`、`finished`）と併存する形で
`runId` チェックが足されており、矛盾は見当たらない。`stopSpeech()` が
`speechRunId` を進める経路（一時停止・スライド送り・エンジン切替・
ミュート）はすべて確認済みで、`handleEnd` 側の追加チェックは「`cancel()`
後に古い `onend`/timeout が遅れて発火した場合の二重発火防止」として
働く形になっており、他の経路と競合しない

### 3. `CLAUDE.md` の文言

`git diff CLAUDE.md` で「最大 40 文字」になっていることを確認した
（`splitForSpeech()` の既定 `maxLen = 40` と一致。上記(d)のとおり実際には
条件により 41 文字まで伸びる場合があるが、「最大」という言い方自体は
「目安の上限」として妥当な範囲と判断する。1 文字単位の精度を求めるなら
「約 40 文字」の方がより正確、という程度の指摘に留まる）

### `<script>` 構文チェックのやり直し

大きい方の `<script>`（更新後）を抜き出して `node --check` を再実行し、
終了コード 0 を確認した。

### この追加確認で新たに分かった限界

- (d) で判明したとおり、`maxLen=40` としていても実際のチャンク長は
  条件によって 41 文字まで伸びることがある。実害（読み上げの不自然さや
  15 秒制限への抵触）は無いと考えられるが、「最大 40 文字」という文言と
  1 文字ずれる点は報告しておく
