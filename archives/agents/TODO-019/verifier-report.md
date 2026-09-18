# TODO-019 verifier 報告

## 検証方法

ヘッドレス Chromium（Playwright 1.63.0）で `claude_memo.html` を実際に開き、
`page.route()` で `translate.google.com` への通信を止める／差し替えることで
5 つの完了条件をそれぞれ実測した。`window.onSlideAudioFinished` を
ラップして呼び出しタイミング・回数を計測している。スライド 1 は
`duration: 18`（秒）、デフォルトの再生速度（playbackRate）は 1 倍。

スクリプトは
`/tmp/claude-649/.../scratchpad/verify_hang.js`
`/tmp/claude-649/.../scratchpad/verify_normal2.js`
`/tmp/claude-649/.../scratchpad/verify_pause.js`
`/tmp/claude-649/.../scratchpad/verify_playreject.js`
（セッション専用の一時ディレクトリなので、報告に主要部分を貼る）

## 完了条件ごとの結果

1. **`onended` が来なくても、音声の実長 + 3 秒で進む**
   → OK（実測）。`translate.google.com` へのリクエストを **応答させずに
   ハングさせ**（onerror も onended も発火しない状況）、実測 **21.00 秒**
   で `onSlideAudioFinished()` が呼ばれた。18 秒（スライドの想定秒数）+ 3
   秒と一致。

   ```
   [HANG, no onerror/onended] slide1 duration=18s -> onSlideAudioFinished after 21.00 s (expect ~21s: 18+3)
   ```

2. **実長が取れない（NaN・0）ときは、スライドの想定秒数 + 3 秒**
   → OK。上の 1 のケースがそのまま該当する（通信がハングして
   `onloadedmetadata` が一度も発火しないため、実長が取れないまま
   スライドの想定秒数 + 3 秒の初期タイマーで進んだ）。21.00 秒で一致。
   `loadedmetadata` が実際に発火して実長で張り直すケース自体は、
   3 の検証（2 秒の実音声）で間接的に確認済み（後述）。

3. **`onended` が正常に来たときは、安全タイマーで二重に進まない**
   → OK（実測）。ffmpeg で 2 秒の実音声ファイルを作り、
   `translate.google.com` へのリクエストをその音声で応答するよう差し替え。
   1 回目の `onSlideAudioFinished()` が呼ばれた直後に `pausePresentation()`
   でスライド進行を止め、そのまま 23 秒待った（安全タイマーがクリアされて
   いなければ 18+3=21 秒付近で 2 回目が呼ばれるはず）。結果は **1 回のまま**。

   ```
   [REAL 2s AUDIO, paused right after 1st onended] total calls in 23s: 1 (expect exactly 1; if safety timer not cleared, would become 2 around t=21s)
   ```

   （最初に「8 秒待って回数を数える」だけの雑なテストをしたところ 2 回に
   なったが、これは次のスライドへ自動で進んだ分の正当な 2 回目だったため、
   上記のとおり 1 回目の直後に一時停止する形に作り直して確認し直した。）

4. **一時停止・スライド移動（`stopSpeech()`）の後にタイマーが残って
   勝手に進むことがない**
   → OK（実測）。通信をハングさせた状態で再生開始 1 秒後に一時停止
   （`stopSpeech()` 経由）し、その後 24 秒（本来の安全タイマー 21 秒を
   超える時間）待っても `onSlideAudioFinished()` は一度も呼ばれなかった。

   ```
   [PAUSE after stopSpeech, network hung] stray onSlideAudioFinished within 24s after pause: false (expect false)
   ```

5. **`onerror` / `play()` 拒否の待ち時間が従来と同じ**
   → OK（実測）。
   - `onerror`（通信を abort）: 実測 **17.99 秒** ≒ 18 秒（+3 秒なし）
   - `play()` 拒否（`HTMLMediaElement.prototype.play` を差し替えて強制的に
     reject させた）: 実測 **18.05 秒** ≒ 18 秒（+3 秒なし）

   ```
   [BLOCKED] slide1 duration=18s -> onSlideAudioFinished after 17.99 s (expect ~21s: 18+3)
   [play() forced reject] slide1 duration=18s -> onSlideAudioFinished after 18.05 s (expect ~18s, no +3s, same as before)
   ```

   どちらも `slideData[currentIndex].duration / playbackRate` のみで、
   3 秒の余裕は付いていないことを確認した（差分どおり、これらのパスは
   `setEndTimeout(... )` の呼び方自体を変えていない）。

## 変更ファイルと範囲

`git diff` は `claude_memo.html` の `stopSpeech()` と `speakOnlineTTS()`
のみを変更しており、依頼の対象範囲と一致していた。ほかのファイルは
`archives/agents/TODO-019/`（未追跡ディレクトリ、この報告用）以外に
変更なし。

## 確かめられなかったこと・判断が要る点

- 条件 2 のうち「`loadedmetadata` が実際に発火して実長 + 3 秒に張り直す」
  単独のケースは、独立した実測はしていない（3 の 2 秒音声テストで
  `onended` が先に来るため、`onloadedmetadata` のタイマー張り替え自体が
  効いているかは間接確認にとどまる）。コードは
  `fallbackAudioElement.onloadedmetadata` で `audioSec` が有限かつ正の
  ときだけ `setEndTimeout((audioSec / playbackRate)*1000 + 3000)` を
  張り直しており、ロジック上は条件を満たしているが、実測での直接確認は
  していない。必要なら、意図的に音声の長さとスライドの `duration` を
  大きくずらした音声ファイルで別途測れる。
- ヘッドレス Chromium での計測であり、実際のブラウザ UI での手動確認は
  行っていない（`play-btn` のクリックはユーザー操作として扱われ、通常は
  自動再生ブロックを受けないため、5 の `play()` 拒否は `play()` を
  強制的に reject させる形での擬似的な検証）。
- コードの品質面（分岐の意味が正しいか等）のレビューはしていない
  （verifier の担当外）。
