# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 構成

`player.html`（外枠と再生エンジン）、`slides-claude-memo.js`（スライドの
データ）、`claude_memo.html`（旧 URL からのリダイレクト）と、`tools/` の
補助スクリプトだけ。ビルド、依存関係のインストール、テストは無い。
Tailwind・Google Fonts・FontAwesome は CDN から読む（オフラインでは崩れる）。

配置場所が `public_html/` なので、これらのファイルがそのまま公開される。
確認はブラウザで `player.html?deck=claude-memo` を開くだけでよい。

## 中身

「Claude Code の使い方」を紹介する日本語スライドを、動画プレイヤー風の UI で
自動再生するページ。HTML → `slideData` → 再生ロジック の 3 段構成で、
データだけが別ファイルに分かれている（TODO-041）。

- **`slides-claude-memo.js`**: スライド 17 枚の配列 `slideData`。1 要素が
  `{ id, title, duration, narration, render() }`。`render()` は
  Tailwind クラス付きの HTML 文字列を返す関数で、`slide-canvas` に差し込まれる。
  スライドの追加・修正はこのファイルだけを触る。先頭の `deckConfig` は
  ページの `<title>` とヘッダーの見出し
- **`player.html`**: 外枠の HTML・CSS と再生ロジック。`?deck=<名前>` の
  `<名前>` から `slides-<名前>.js` を読む（既定は `claude-memo`）。
  読み込みは `</main>` の直後の `document.write` で、再生ロジックの
  `<script>` より先に走らせている
- **再生ロジック**: `requestAnimationFrame` の
  `playbackLoop` が `duration` を進め、尽きたら次のスライドへ。
  **`duration` には、Online TTS の音声を 1.4 倍速で再生した実測秒数が
  入っている**（TODO-018 で 17 枚すべて `ffprobe` で測って入れ替えた。
  合計 324 秒）。**`prepareSpeechText()` の置換表を変えると読み上げの長さも
  変わるので、当たるスライドの `duration` を測り直す**（TODO-023）。
  **測るには `tools/measure-duration.py` を使う**（`tools/measure-duration.py 2 17`、
  案の下見は `--text`）。**このスクリプトは `prepareSpeechText()` の置換表と
  `TTS_MAX_CHARS`・`BASE_SPEED_MULTIPLIER` を写しているので、
  そちらを直したら一緒に直す**（TODO-030）。
  進行バーと時間表示は実時間（`deltaTime * playbackRate`）で進め、
  **読み上げの速度だけが `playbackRate * baseSpeedMultiplier`（1.4）**。
  時間軸に 1.4 を掛けるとバーだけが先走り、`duration` で頭打ちになって
  読み終わりまで止まる。**スライドの送りは読み上げの終了イベントで起きる**ので、
  音声が `duration` より長ければバーは 100% で待つ。`duration` を待ち時間に
  使うのは消音中と、音声が鳴らせなかったとき（`onerror`・`play()` の拒否）だけ。
  **Web Speech に切り替えると音声の長さが変わるので、バーとはずれる**
- **読み上げ**: 2 系統を `toggle-voice-engine-btn` で切り替える。
  `speech` = Web Speech API（`SpeechSynthesisUtterance`）、
  `online` = Google Translate TTS の URL を `Audio` で再生（180 文字で切る）。
  既定は `online`。
  Web Speech は読み終わりのイベントが来ないことがあるので、**文字数**から
  計算した安全タイマー（`textToSpeak.length / 4.5 / getEffectiveSpeed()`）で
  次へ進める。Online TTS 側にも安全タイマーがあり、**音声の実長**
  （`loadedmetadata` で取れなければスライドの `duration`）に 3 秒足した
  時点で次へ進める（TODO-019）

## 触るときの注意

- **スライドの拡大縮小は container query に頼っている。** `.video-viewport` が
  `container-type: inline-size` で、`render()` の中は `cqw` と
  `clamp()` で書く。`px` や `rem` 直書きは 16:9 を縮めたときに崩れる
- **幅 768px 未満とタッチ画面は、container query とは別系統で縮小している。**
  条件は `@media screen and (max-width: 767.98px), screen and (pointer: coarse)`。
  タッチ画面を加えたのは、横持ちのスマホ（844x390 など）が幅 768 以上で PC 扱いに
  なり、レターボックスの中では `clamp()` の下限 px が効いて本文が縮まず、
  枠内上段に重なるため（TODO-009）。**フルスクリーン中に限らず、タッチ画面なら
  通常表示でも縮小経路に入る**（タブレットやタッチ対応 PC も同じ）。
  `#viewport-frame` が 16:9 の外枠になり、`setupViewportScale()` が
  `--vp-scale` を入れて `#player-viewport`（中身は 960x540 のまま）を
  `transform: scale()` で縮める（TODO-001）。**縮むのは枠の中身すべてで、
  `cqw` や `clamp()` で書いていない固定 px のものも例外ではない。**
  幅 768px 未満では `md:` は効かない（`md:` は `min-width: 768px`）ので、
  枠の中のクロームは `text-xs` などの小さい方が選ばれ、それがさらに
  `--vp-scale`（0.34〜0.77）倍される。実際、枠の上の
  `#slide-category` と `SLIDE nn / 17` は 390px 幅で 4.5〜5.2px になる
  （補助的な情報なので、読めなくてよいものとして残している。TODO-001）
- **字幕バナー（`#subtitle-banner`）だけは枠の外**（`#viewport-stage` 直下）に
  あり、縮小されない。マウスの PC では絶対配置で枠に重ね、縮小経路（幅 768px 未満
  またはタッチ画面）では枠の下に流す。
  `margin: 1px` は `#player-viewport` の 1px ボーダーを打ち消す値で、
  通常時とフルスクリーン中の両方に効く。ボーダーの太さを変えたら一緒に直す
- **擬似フルスクリーンのレターボックスは `#viewport-stage.is-fullscreen` だけが
  持つ。高さの基準は `100dvh`**（`vh` の行は dvh 非対応ブラウザ用に残してある）。
  スマホの `100vh` は URL バーを含んだ高さなので、`vh` のままだと横持ちで
  箱が画面の下へはみ出す（TODO-004）。 中身（`.video-viewport.pseudo-fullscreen`、縮小経路では
  `#viewport-frame`）も字幕も、このラッパーを基準に置いているので、
  比率やサイズを変えるのはここ 1 か所でよい（TODO-001）。
  字幕はフルスクリーン中、マウスの PC では枠に重なり、縮小経路では `top: 100%` で
  枠のすぐ下（暗幕の上）に出る
- **`body.fs-lock`（裏のスクロール止め）と暗幕（`::before`）は、幅 768px 未満
  または `(pointer: coarse)` のときだけ。** マウスの PC で裏をスクロール禁止に
  するとスクロールバーが消え、裏のページ全体がスクロールバー幅ぶん、
  `100vw` 基準のレターボックスがその半分だけ横に動く（TODO-003 で実測。
  ずれは 3px 程度で、比率によっては fs-lock を掛けた方が正しい位置になる）。
  タッチ画面を条件に加えたのは、横持ちのスマホが幅 768 以上で PC 扱いになり、
  フルスクリーンから抜けられなくなるため（TODO-003）。
  **暗幕の帯は画面の比率で決まる。** 16:9 ちょうどの画面では帯が 0px になり、
  タップで抜ける出口が無くなる（対応しないと決めた。TODO-003）暗幕のタップでフルスクリーンを抜ける
  （ハンドラは `#viewport-stage` の click で、`e.target` がラッパー自身の
  ときだけ反応する＝枠の中身や字幕のタップでは閉じない）
- **スライド枚数は書かない。** `total-slides` も `playlist-count` も
  `initPlaylist()` が `slideData.length` で埋める（TODO-041）
- `total-time-display` の初期値は `--:--`。`initPlaylist()` が
  `duration` の合計で上書きするので、値を直書きしない（TODO-018）
- `narration` は `prepareSpeechText()` を通してから読み上げられる。
  記号や英単語の読みがおかしいときはここを見る
- **Online TTS の `Audio` 要素（`fallbackAudioElement`）は 1 個を使い回す。**
  再生ボタンのクリックの中で unlock しているので、`null` にして作り直すと
  Android Chrome で自動再生がブロックされて鳴らなくなる（TODO-002）
- **Web Speech は `splitForSpeech()` で 40 文字程度に分けて順に読ませる。**
  Chrome は PC も Android も、長い発話を 15 秒ほどで打ち切る。
  1 つにまとめると途中で切れる（TODO-002）
- **`<meta name="referrer" content="no-referrer">` を外さない。**
  Google Translate TTS は Referer が付いた要求に 404 を返すので、
  外すと Online TTS が鳴らなくなる（TODO-002）
