# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 構成

`player.html`（外枠と再生エンジン）、`slides-claude-memo.js`（スライドの
データ）、`claude_memo.html`（旧 URL からのリダイレクト）と、`tools/` の
補助スクリプトだけ。ビルド、依存関係のインストール、テストは無い。
配置場所が `public_html/` なので、これらのファイルがそのまま公開される。
確認はブラウザで `player.html?deck=claude-memo` を開くだけでよい。

「Claude Code の使い方」を紹介する日本語スライドを、動画プレイヤー風の UI で
自動再生するページ。`player.html` は `?deck=<名前>` で `slides-<名前>.js` を
読む（既定は `claude-memo`）。

## 触る前に読むもの

**中身の説明は `docs/` にある。ここには写しを置かない**（二重管理を避ける
ため。TODO-043）。

- **`player.html` を直すなら [`docs/Developer.md`](docs/Developer.md)。**
  再生ロジックと `duration` の決まり、読み上げの 2 系統と安全タイマー、
  container query と狭い画面の縮小経路、擬似フルスクリーン、触ると鳴らなく
  なるもの。**直す前に必ず目を通すこと**
- **スライドを足す・作るだけなら [`docs/Usage.md`](docs/Usage.md)。**
  `slides-<名前>.js` の書き方と `duration` の測り方

個々の変更の経緯は `archives/todo/` にある。`docs/` は利用者向けなので
TODO 番号を書かない。番号で参照してよいのはこのファイルと `archives/` の中だけ。
