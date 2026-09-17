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

- **`slideData`**（353 行あたり〜）: スライド 17 枚の配列。1 要素が
  `{ id, category, title, duration, narration, render() }`。`render()` は
  Tailwind クラス付きの HTML 文字列を返す関数で、`slide-canvas` に差し込まれる。
  スライドの追加・修正はここだけを触る
- **再生ロジック**（1012 行あたり〜）: `requestAnimationFrame` の
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
- **スライド枚数は 2 か所にある。** `slideData` を増減したら、334 行の
  `playlist-count`（`17 Slides`）も直す。`total-slides` の方は
  `initPlaylist()` が `slideData.length` で上書きするので触らなくてよい
- `total-time-display` の初期値 `3:15` も同様の直書き（再生開始後に上書きされる）
- `narration` は `prepareSpeechText()` を通してから読み上げられる。
  記号や英単語の読みがおかしいときはここを見る
