# TODO-005 レビュー報告（reviewer）

対象: `claude_memo.html` の `git diff`（CSS の `#tap-feedback-icon`、
`<i id="tap-feedback-icon">`、`#player-viewport` の click ハンドラ）。
動作確認はしていない（verifier の担当）。以下はコードを読んだ上での指摘。

## 直すべき

なし。

## 検討

1. **`unlockFallbackAudio()` / ダミー発話を呼んでいない。**（claude_memo.html:1747-1760）
   `playBtn` の click（1646-1658 行）は `speechSynthesis.resume()` に加えて
   ダミーの `SpeechSynthesisUtterance` を発話させ、`unlockFallbackAudio()`
   （`fallbackAudioElement` を作って無音再生し、Android Chrome の自動再生
   ブロックを解く。TODO-002）を呼んでいる。新しい `#player-viewport` の
   click は `speechSynthesis.resume()` だけで、これは keydown の Space
   ハンドラ（1792-1803 行）を忠実に踏襲したもの（依頼どおり）。

   ただし `fullscreenBtn` は再生状態と無関係にいつでも押せる
   （1774-1777 行）。ユーザーが `play-btn` を一度も押さないままフルスク
   リーンへ入り、暗幕の下に隠れた `play-btn` の代わりに枠のタップで
   初めて再生を始めると、`fallbackAudioElement` は `null` のまま
   `speakOnlineTTS()`（1430 行〜）に入る。既定エンジンは online
   （CLAUDE.md）。そこには
   `// No play button press yet (autoplay will likely be blocked)`
   という既存コメント（1438 行）があり、実装した本人もこの経路を
   ブロックされる可能性のある経路として認識している。
   `speakCurrentNarration()` → `speakOnlineTTS()` は同期呼び出し
   （setTimeout を挟まない、1344-1347 行）なので、クリックのユーザー
   操作としての文脈は保たれているはずで、理屈の上では `play-btn` 経由と
   同じに動くと考えられるが、**実機（Android Chrome）で未確認**。
   このタップ機能はまさに「`play-btn` に触れずに再生を制御する」ための
   ものなので、**「フルスクリーンへ先に入ってから枠をタップして再生を
   始める」経路を verifier に明示的に確認してもらうのがよい**
   （TODO.md のチェック項目「スマホのフルスクリーンで、タップが効くこと」
   はこのケースを含んでいるかが読み取りにくい）。

2. **`speechSynthesis.resume()` の重複が 3 か所になった。**
   （`playBtn` 1648-1655 行、Space 1798-1802 行、今回の viewport 1749-1753 行）
   try/catch を含めてほぼ同じコードが 3 回書かれている。依頼文にある
   「keydown の Space と同じく呼ぶ」を素直に満たしており、今回の変更が
   重複を増やしたわけではない（Space と playBtn は変更前から重複していた）
   が、3 か所目が増えたことで共通化の余地がより目立つ。関数へまとめるか
   どうかは管理者の判断。

## 好みの範囲

- `catch (err)` （1752 行、スペースあり）と、直接倣った Space ハンドラの
  `catch(err)`（1801 行、スペースなし）で空白の有無だけが違う。
  ファイル全体では `catch(e)` と `catch(err)` が混在しており
  （1181, 1290, 1355, 1654 行は `e`、1801 行は既存で `err`）、
  今回の変更がこの混在を悪化させたわけではない。

## 確認できたこと（問題なし）

- **`#player-viewport` をクリック対象にしたことについて**: 現在
  `render()` が返す HTML（439〜1097 行あたり）に `onclick` や `<button>`
  `<a href>` の類いは無く（grep で確認）、`#player-viewport` の直下も
  背景の光彩（`pointer-events-none`）とヘッダー表示だけで、実際に押せる
  ものは無い。コメント（1743-1744 行）の「枠の中に押せるものは無い」は
  現状に対して正確。**ただし将来スライドの中に押せるものを置いたら、
  そのクリックは枠のクリックとしても拾われ、再生/一時停止が同時に
  切り替わってしまう。** そのときは新しい要素側で `e.stopPropagation()`
  を足すか、対象を `#player-viewport` から絞り込む変更が要る
  （今回は「条件分岐を置かない」という決めた仕様の範囲内で問題無い）。
- **暗幕のクリックハンドラとの干渉**: `#viewport-stage` 側は
  `e.target === stage` のときだけ反応する（1785 行）ので、
  `#player-viewport` のクリックがバブリングしても暗幕側は反応しない。
  設計どおり。
- **アイコンの出し方**: `classList.remove` → `void offsetWidth` →
  `classList.add` で再生アニメーションを頭から出し直す手口は、
  `renderSlide()` の `slideCanvas.classList.remove('slide-fade-enter')` /
  `void slideCanvas.offsetWidth` / `.add('slide-fade-enter')`
  （1481-1483 行）と同じ考え方。今回はアイコンの絵柄（fa-play/fa-pause）
  も同時に変える必要があるため `className` を丸ごと入れ替えているが、
  これは合理的な差分で、既存のやり方から外れていない。
- **`cqw` と `clamp()` の使い方**: `#tap-feedback-icon` は
  `clamp(28px, 9cqw, 96px)` を使っており、`px` 直書きを避ける方針
  （CLAUDE.md「触るときの注意」1 項目目）に沿っている。配置場所も
  `container-type: inline-size` を持つ `.video-viewport` の定義
  （50-65 行）の直後で、既存の並びと整合している。
- **`isPlaying` の読み取りタイミング**: `togglePlay()` は
  `playPresentation()`/`pausePresentation()` を同期的に呼び、
  `isPlaying`（1142 行、トップレベル `let`）を即座に更新するので、
  `togglePlay()` の直後に読む `isPlaying` は新しい状態を指している。
  ▶ を「今から再生」、‖ を「今から一時停止」に出す向き
  （`isPlaying ? 'fa-play' : 'fa-pause'`）は動画プレイヤーの一般的な
  挙動（トグル後の状態を示す）と合っている。
- **スコープ**: diff は CSS 1 ブロック、マークアップ 1 か所、
  click ハンドラ 1 か所のみで、依頼にない変更は見当たらない。
- **コメントの粒度**: 新しいコメントは「なぜ」（cqw を使う理由、
  暗幕と当たらない理由）を書いており、周囲の TODO-001〜004 由来の
  日本語コメント（130-280 行あたり）と同じ書き方。

## 判断が要る点

- 検討 1（online TTS 未解錠のまま枠タップで再生を始める経路）を
  verifier に追加確認してもらうか。
- 検討 2（`speechSynthesis.resume()` の 3 重化）を今回まとめるか、
  別項目に送るか。
