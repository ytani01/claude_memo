# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 構成

`claude_memo.html` 1 ファイルだけ。ビルド、依存関係のインストール、テストは無い。
Tailwind・Google Fonts・FontAwesome は CDN から読む（オフラインでは崩れる）。

配置場所が `public_html/` なので、このファイルがそのまま公開される。
確認はブラウザでファイルを開くだけでよい。

## 中身

「Claude Code の使い方」を紹介する日本語スライドを、動画プレイヤー風の UI で
自動再生するページ。HTML → `slideData` → 再生ロジック の 3 段構成で、すべて
`claude_memo.html` の中にある。

- **`slideData`**（439 行あたり〜）: スライド 17 枚の配列。1 要素が
  `{ id, category, title, duration, narration, render() }`。`render()` は
  Tailwind クラス付きの HTML 文字列を返す関数で、`slide-canvas` に差し込まれる。
  スライドの追加・修正はここだけを触る
- **再生ロジック**（1098 行あたり〜）: `requestAnimationFrame` の
  `playbackLoop` が `duration` を進め、尽きたら次のスライドへ。実速度は
  `playbackRate * baseSpeedMultiplier`（1.4）
- **読み上げ**: 2 系統を `toggle-voice-engine-btn` で切り替える。
  `speech` = Web Speech API（`SpeechSynthesisUtterance`）、
  `online` = Google Translate TTS の URL を `Audio` で再生（180 文字で切る）。
  どちらも読み終わりのイベントが来ないことがあるので、`duration` から
  計算した安全タイマーで次へ進める作りになっている

## 触るときの注意

- **スライドの拡大縮小は container query に頼っている。** `.video-viewport` が
  `container-type: inline-size` で、`render()` の中は `cqw` と
  `clamp()` で書く。`px` や `rem` 直書きは 16:9 を縮めたときに崩れる
- **768px 未満は container query とは別系統で縮小している。**
  `#viewport-frame` が 16:9 の外枠になり、`setupViewportScale()` が
  `--vp-scale` を入れて `#player-viewport`（中身は 960x540 のまま）を
  `transform: scale()` で縮める（TODO-001）。**縮むのは枠の中身すべてで、
  `cqw` や `clamp()` で書いていない固定 px のものも例外ではない。**
  768px 未満では `md:` は効かない（`md:` は `min-width: 768px`）ので、
  枠の中のクロームは `text-xs` などの小さい方が選ばれ、それがさらに
  `--vp-scale`（0.34〜0.77）倍される。実際、枠の上の
  `#slide-category` と `SLIDE nn / 17` は 390px 幅で 4.5〜5.2px になる
  （補助的な情報なので、読めなくてよいものとして残している。TODO-001）
- **字幕バナー（`#subtitle-banner`）だけは枠の外**（`#viewport-stage` 直下）に
  あり、縮小されない。PC では絶対配置で枠に重ね、768px 未満では枠の下に流す。
  `margin: 1px` は `#player-viewport` の 1px ボーダーを打ち消す値で、
  通常時とフルスクリーン中の両方に効く。ボーダーの太さを変えたら一緒に直す
- **擬似フルスクリーンのレターボックスは `#viewport-stage.is-fullscreen` だけが
  持つ。** 中身（`.video-viewport.pseudo-fullscreen`、768px 未満では
  `#viewport-frame`）も字幕も、このラッパーを基準に置いているので、
  比率やサイズを変えるのはここ 1 か所でよい（TODO-001）。
  字幕はフルスクリーン中、PC では枠に重なり、768px 未満では `top: 100%` で
  枠のすぐ下（暗幕の上）に出る
- **`body.fs-lock`（裏のスクロール止め）と暗幕（`::before`）は 768px 未満だけ。**
  PC で裏をスクロール禁止にするとスクロールバーが消え、`100vw` 基準の
  レターボックスが横にずれる。暗幕のタップでフルスクリーンを抜ける
  （ハンドラは `#viewport-stage` の click で、`e.target` がラッパー自身の
  ときだけ反応する＝枠の中身や字幕のタップでは閉じない）
- **スライド枚数は 2 か所にある。** `slideData` を増減したら、420 行の
  `playlist-count`（`17 Slides`）も直す。`total-slides` の方は
  `initPlaylist()` が `slideData.length` で上書きするので触らなくてよい
- `total-time-display` の初期値 `3:15` も同様の直書き（再生開始後に上書きされる）
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
