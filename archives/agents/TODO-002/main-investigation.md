# TODO-002 調査メモ（main）

Android Chrome で「音声が途中で途切れる」件。コードを読んで原因の候補を絞った。
**実機での確認は未実施**（利用者にお願いする）。

## 先に潰した候補

### 180 文字の切り詰めは起きていない
`speakOnlineTTS()` は `text.substring(0, 180)` で切るが、`prepareSpeechText()` で
読みを展開した後の文字数を 17 枚すべてで測ったところ、**最長 164 文字**
（スライド 17）で 180 に届かない。切り捨ては 0 枚。

### safety timeout の早発火も考えにくい
`safetyTime = max(6000, 文字数 / 4.5 / 速度 * 1000 + 3000)`。既定速度
（`playbackRate` 1.0 × `baseSpeedMultiplier` 1.4）で 21〜29 秒。
実際の読み上げに要る時間は 13〜19 秒程度なので、6〜10 秒の余裕がある。

### duration で先に進むわけでもない
`playbackLoop()` は `duration` を超えた分を頭打ちにするだけで、次のスライドへは
進めない。進むのは読み終わりのイベントか safety timeout のときだけ。

## 最有力の原因: `chromeResumeTimer` の pause/resume

`claude_memo.html:1322-1330`

```js
chromeResumeTimer = setInterval(() => {
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
    } else {
        clearInterval(chromeResumeTimer);
    }
}, 5000);
```

これは**デスクトップ Chrome** の「長い発話が 15 秒ほどで勝手に止まる」既知の
問題への回避策。ところが **Android Chrome では `pause()` が発話を止めたまま
`resume()` で戻らない**ことが知られており、回避策がそのまま原因になる。

- 5 秒間隔なので、**読み始めて約 5 秒で止まる**
- 1 枚あたりの読み上げは 13〜19 秒なので、「途中で途切れる」症状と合う
- 止まった後は `speaking` が false になり、`onend` も来ないので、
  safety timeout（21〜29 秒）が来るまで無音のまま待つことになる

## もう 1 つの候補: Google Translate TTS

スクリーンショットでは音声エンジンが `online`（Google Translate TTS）に
切り替わっていた。`translate.google.com/translate_tts` は Google 側が
Referer や User-Agent で弾くことがあり、途中で切れるというより鳴らない
・`onerror` に落ちる形になる。こちらが起きているなら症状は
「そもそも鳴らない」に近いはず。

## 利用者にお願いしたい切り分け

1. 画面右上の **音声エンジンの切替ボタン**で `Web Speech API` と
   `Online TTS` を入れ替え、**どちらでも途切れるか**を見る
2. 途切れるのが **Web Speech のときだけ**なら、原因は `chromeResumeTimer`。
   直し方は「Android では pause/resume を呼ばない」
3. **両方で途切れる**なら、画面を消したときやタブを切り替えたときに
   起きていないかも見る（バックグラウンドでの制限）
4. 途切れるのが**毎回同じあたり（5 秒くらい）**か、**スライドによって違う**かも
   分かると絞れる

---

# 追記（2026-09-18）: 実機の症状が分かれた

利用者の実機確認:
- **Web Speech API**: 途中で途切れる
- **Online TTS**: **そもそも音が出ない**

症状が 2 系統で違うので、原因も別々。

## Online TTS が鳴らない原因: 自動再生のブロック

Google 側のブロックではない。手元から同じ URL を叩くと
**HTTP 200 / `audio/mpeg` / 89KB** が返る（Referer 無し、Android の
User-Agent どちらでも）。

原因は `Audio.play()` の**自動再生ポリシー**。

`claude_memo.html:1546-1556` の再生ボタンのハンドラは、
**Web Speech API だけ**を「ユーザー操作の文脈」で unlock している。

```js
playBtn.addEventListener('click', () => {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.resume();
        const dummyUtterance = new SpeechSynthesisUtterance('');
        dummyUtterance.volume = 0;
        window.speechSynthesis.speak(dummyUtterance);   // ← Web Speech の unlock
    }
    togglePlay();
});
```

一方 `speakOnlineTTS()`（`claude_memo.html:1349`）は**毎回 `new Audio(url)` を
作って `play()` する**。しかも呼ばれるのは `setTimeout` や読み終わりの
イベントの中で、ユーザー操作の文脈から外れている。
Android Chrome はデスクトップより自動再生に厳しいので、
`play()` が reject され、`.catch()` の

```js
console.warn("Audio play blocked by browser interaction policy:", e);
```

に落ちて、無音のまま `duration` 分だけ待つ。**「音が出ない」に一致する。**

**直し方**: 再生ボタンを押した瞬間に `Audio` 要素を 1 つ作って無音で
`play()` → `pause()` して unlock し、以後はその 1 つを `src` の差し替えで
使い回す（毎回 `new Audio()` しない）。

## Web Speech が途切れる原因: 変わらず `chromeResumeTimer`

上の本文のとおり。5 秒ごとの `pause()` / `resume()` が Android Chrome で
戻ってこない。**直し方**: Android では pause/resume を呼ばない。

## 残る確認

どちらも実機でしか確かめられない。直したものを実機で見てもらう必要がある。
