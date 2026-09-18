# TODO-041 レビュー報告（reviewer）

対象: `git diff`（`CLAUDE.md`, `claude_memo.html`, `tools/measure-duration.py`）
と新規 2 ファイル（`player.html`, `slides-claude-memo.js`）。分割前の版は
`git show 0b158ca:claude_memo.html`（1971 行）。

## 確認した方法

- `sed` で分割前ファイルを「head（1〜461 行）」「slideData（462〜1116 行）」
  「tail（1117〜1971 行）」に切り、それぞれ新ファイルの対応部分と `diff` で
  突き合わせた（行単位の機械比較）
- `node --check` で 3 つのインライン `<script>`（deckConfig 読み込み・
  tailwind config・再生エンジン）と `slides-claude-memo.js` の構文を確認
- `python3 -m http.server` でローカルに立て、`chromium --headless --dump-dom`
  で `?deck=claude-memo`（正常系）と `?deck=nonexistent` / `?deck=..%2f..%2fetc%2fpasswd`
  （異常系）を実行して DOM を確認
- `tools/measure-duration.py --text 1 1` を実行し、`slides-claude-memo.js` から
  narration を正しく拾えることを確認

## 検討（実装として妥当だが、判断が要る／記録しておきたい点）

1. **`?deck=` に存在しないデッキ名を渡すと、ページ全体が無音で壊れる。**
   `player.html:1315-1316` の `startApp()` は
   `document.title = deckConfig.title;` を無条件に呼ぶ。`slides-<名前>.js` が
   404 のとき `deckConfig` は未定義になり、ここで `ReferenceError` が起きて
   `setupViewportScale()` 以降（`initPlaylist()`、`renderSlide()`、
   `setupEventListeners()`）が一切走らない。
   実測: `chromium --headless --dump-dom "player.html?deck=nonexistent"` で
   `<title>` は既定の「プレゼン動画プレイヤー」のまま、`#deck-heading` /
   `#total-slides` / `#playlist-count` は空のまま（`?deck=claude-memo` では
   それぞれ正しく埋まることも実測で確認）。つまりスライドも操作パネルも
   出ない白紙に近い画面になる。
   これは分割前には無かった失敗経路（分割前は `slideData` が同じ HTML に
   埋め込まれていたので「デッキが見つからない」状態自体が存在しなかった）。
   個人ページで既定値 `claude-memo` を打ち間違えない限り踏まないので、
   対応するかどうかは利用側の判断。対応するなら
   `<script>` の `onerror` か `deckConfig` の存在チェックで足りる規模。

2. **`claude_memo.html` の `meta refresh` はブラウザ履歴に残る。**
   `content="0"` で即座に `player.html?deck=claude-memo` へ飛ぶが、
   `location.replace` と違い履歴エントリを消さない。ブラウザによっては
   「戻る」を押すと `claude_memo.html` に戻り、そこから即座に転送し直される
   （二度手間）。実際にブラウザで戻るボタンを押す検証はしていない
   （未確認）。ビルド・依存関係なしの静的ファイルという構成上、JS の
   `location.replace` を使わず meta refresh に留めた判断は
   `CLAUDE.md` の「ビルド、依存関係のインストール、テストは無い」という
   簡潔さの方針とは矛盾しない。実害は小さいので指摘のみ。

## 確認して問題が無かった点

- **分割の過不足**: `slideData` 配列（分割前 462〜1116 行）は
  `slides-claude-memo.js` に 1 文字も変えずコピーされている（`diff` 差分なし）。
  head/tail 側も、意図した 4 箞所の差分（`<title>` 空／`deck-heading` へ置換／
  `total-slides` の `17` 削除／`playlist-count` の `17 Slides` 削除、
  および `playlistCount` 変数追加と `deckConfig` 反映の 2 行追加）以外に
  差分は無い。行の欠落・重複は無い
- **4 箇所のハードコード撤去と実行時の穴埋め**: `<title>`・見出し・
  `total-slides`・`playlist-count` の 4 つとも `startApp()` の中で
  `deckConfig` / `slideData.length` から埋まる経路になっており、
  正常系では実機（ヘッドレス Chromium）で実際に埋まることを確認した
- **`?deck=` のディレクトリ遡り**: `.replace(/[^\w-]/g, '')` は `/` や `.` を
  含めすべて `\w`（英数字とアンダースコア）・`-` 以外を落とす。
  `deck=../../etc/passwd` を渡すと `etcpasswd` になり、遡りは成立しない
  （実測で確認）
- **`document.write` の使い方**: 同一オリジンの外部スクリプト
  （`slides-<名前>.js`）を、パーサーを止めたまま挿入する古典的な手法として
  妥当。Chrome が問題視するのは低速回線でのクロスオリジン読み込みへの
  介入で、これは同一オリジンなので該当しない
- **`deckConfig` / `slideData` の変数名衝突**: `player.html` 側に同名の
  `const` 宣言は無く、`slides-claude-memo.js` の宣言のみ（`grep` で確認）
- **`tools/measure-duration.py` の参照先変更**: `SRC` を
  `slides-claude-memo.js` に向け、`TTS_MAX_CHARS` / `BASE_SPEED_MULTIPLIER` の
  コメントを「player.html の写し」に直した先が実際の定義位置
  （`player.html` 側）と一致している。`--text 1 1` を実行し、
  narration の抽出が動くことを確認した
- **`CLAUDE.md` の記述**: 旧い行番号（473 行あたり、1131 行あたり、420 行）や
  「`claude_memo.html` 1 ファイル」という記述は残っておらず、新しい構成
  （`player.html` / `slides-claude-memo.js` / `claude_memo.html`）に
  合わせて書き直されている
- 範囲外の変更（無関係なコードの巻き込み）は見当たらない

## 総評

要修正は無し。「検討」の 2 件は、個人の静的ページという性質上、
対応してもしなくても筋が通る規模の指摘。
