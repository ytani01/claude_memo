# TODO-018 確認報告

## 1. `git diff` の範囲

`git diff` を全文読んだ。変更は指示どおり次の 4 点だけに収まっている。

- `claude_memo.html` 1513行付近: `playbackLoop` の経過を
  `currentSlideElapsedTime += deltaTime * getEffectiveSpeed();` から
  `currentSlideElapsedTime += deltaTime * playbackRate;` に変更。
  コメントも実時間軸である旨に書き換わっている
- `duration` を待ち時間に使う 3 箇所が `duration / getEffectiveSpeed()` から
  `duration / playbackRate` に変わっている（1316行 消音中、1441行
  `fallbackAudioElement.onerror`、1447行 `play().catch`）
- 384行 `total-time-display` の直書きが `3:15` → `--:--`
- `CLAUDE.md` の再生ロジックの説明が、`duration` は 1.4 倍速で読み切る実時間
  であることと、バーは `deltaTime * playbackRate` で進める旨に書き換わっている

他のファイルの変更なし（`git status` でも `CLAUDE.md` と `claude_memo.html`
のみ）。

## 2. `getEffectiveSpeed()` が残るべき箇所

```
$ grep -n "getEffectiveSpeed" claude_memo.html
1143:        const getEffectiveSpeed = () => playbackRate * baseSpeedMultiplier;
1364:                        utterance.rate = Math.min(2.0, getEffectiveSpeed() * 0.95);
1396:                    const safetyTime = Math.max(6000, (textToSpeak.length / 4.5 / getEffectiveSpeed()) * 1000 + 3000);
1426:            fallbackAudioElement.playbackRate = Math.min(2.0, getEffectiveSpeed());
```

指示どおり 3 箇所（`utterance.rate`、Web Speech の安全タイマー、
`fallbackAudioElement.playbackRate`）に残っている。読み上げの待ち時間に
`duration` を使う 3 箇所（消音中・onerror・play() 拒否）は `playbackRate` に
変わっており、読み上げ速度そのものを扱う箇所とは区別されている。

## 3. `node` での数値検証

`slideData` を html（473〜1130行）から切り出し、`module.exports` を足して
`require` で読み込み、`playbackLoop` の式を deltaTime=0.05s 刻みで再現した。

```
$ node -e "..."
slides: 17
total duration(s): 214
formatTime(total): 3:34
slide0 duration: 12
rate=0.75 OLD real時間で埋まるまで= 11.45  NEW= 16.05  期待 duration/rate= 16.00
rate=1    OLD= 8.60   NEW= 12.00  期待= 12.00
rate=1.25 OLD= 6.90   NEW= 9.60   期待= 9.60
rate=1.4  OLD= 6.15   NEW= 8.60   期待= 8.57
rate=2    OLD= 4.30   NEW= 6.05   期待= 6.00
```

- 変更前の式（`playbackRate * 1.4`）では `rate=1.0` のとき実時間 8.60s で
  バーが埋まる。これは `duration / 1.4 = 12/1.4 = 8.57` とほぼ一致し、
  指示にあった「変更前は `duration/1.4`」を裏付ける
- 変更後の式（`playbackRate` のみ）では、各 rate で実時間が
  `duration / rate` とほぼ一致する（0.05s 刻みの離散化誤差のみ）
- 全 17 スライドの `duration` 合計は 214 秒で、`formatTime(214)` は `3:34`。
  html の `total-time-display` の初期表示は `--:--` に変わっており、
  実行時に `totalTimeDisplay.textContent = formatTime(totalDurationSeconds);`
  （1575行）で上書きされる。表示は `3:34` になるはずで、直書きの
  `3:15` は誤りだった（または `1.0` 系速度前提と食い違っていた）ことが
  裏付けられる

## 4. 構文チェック

script タグの中身（473〜1899行）を切り出し `node --check` を実行し、
`SYNTAX OK` を確認した。エラーなし。

## 5. `playbackRate` 切り替え時の挙動（1678行あたり）

`speedBtn` のクリックハンドラは `playbackRate = speedOptions[nextIdx];` の
代入のみを行い、`currentSlideElapsedTime` には触れない（差分の前後で
同じ）。再生中なら `speakCurrentNarration()` を呼ぶが、この関数も
`currentSlideElapsedTime` を初期化しない（初期化は `renderSlide` の
`resetOffset` 時のみ、1456行）。

- **変更前**: `playbackLoop` は常に `getEffectiveSpeed() = playbackRate * 1.4`
  で経過を進めていたので、速度変更後は新しい `playbackRate` に応じて
  バーの進みが変わっていた（挙動としては変更後と同じ「速度変更が即座に
  バーへ反映される」形）
- **変更後**: `playbackLoop` は `deltaTime * playbackRate` で進むので、
  速度変更後は新しい `playbackRate` そのものの速さでバーが進む。
  仕組みは変わったが、「速度ボタンを押すと即座にバーの進み方が変わる」
  という見た目の挙動自体は変更前後で同じ

一方、`speakCurrentNarration()` は `stopSpeech()` で読み上げを止めてから
**スライドの先頭の文章を読み直す**（読み上げ中の位置を維持しない）。
これに対し `currentSlideElapsedTime` はリセットされない。つまり
「読み上げは頭から再生されるのに、進行バーは変更前の位置から続く」という
食い違いが起き得る。ただしこれは今回の diff が持ち込んだものではなく、
変更前から existed していた挙動（`getEffectiveSpeed()` を使っていたときも
同様にリセットしていなかった）。**今回の指示（4点の変更が意図通りかの
確認）の範囲外の既存の挙動なので、これが問題かどうかの判断はしていない。**
気づいた点として報告するのみ。

## 確かめられなかったこと・判断できないこと

- 実際のブラウザでの動作確認（音声再生・進行バーの見た目）はしていない。
  Node での数式再現のみ
- 上記 5. の「読み上げは頭から、バーは続きから」という食い違いが、
  今回の修正で悪化したか、そもそも許容されている挙動かは判断していない
  （diff には含まれておらず、指示の確認範囲の外と判断した）
