# TODO-041. プレイヤーの共通部分とスライドのデータを別ファイルに分ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 20,384 | 73,133 | 59% |
| verifier | Sonnet 5 | medium | 24,073 | 74,305 | 23% |
| reviewer | Sonnet 5 | high | 20,519 | 63,191 | 18% |
| 合計 |  |  | 64,976 | 210,629 | 概算 $4.5 |

- reviewer は見込みに入れていなかったが、`?deck=` の分岐が新しく入るので足した
  （`~/.claude/CLAUDE.md` の「挙動が変わる項目、分岐や条件式が変わる項目には
  確認の担当とは別にレビューの担当も入れる」）
- verifier は定義のモデルが sonnet。ブラウザでの確認は判断が要らないので
  上書きせずそのまま使った。reviewer も定義のまま

## きっかけ

`claude_memo.html` が 1971 行の 1 ファイルで、スライドを 1 枚直すにも
860 行の再生エンジンごと読み込むことになっていた。エンジンがスライドから
読むのは `title` / `duration` / `narration` / `render()` の 4 つだけで、
境界は既にできていた。

## やったこと

- `slides-claude-memo.js`（663 行）… `deckConfig` と `slideData` 17 枚
- `player.html`（1333 行）… 外枠の HTML・CSS と再生エンジン。
  `?deck=<名前>` の `<名前>` を `[^\w-]` で濾してから、
  `document.write` で `slides-<名前>.js` を読む（既定は `claude-memo`）。
  再生エンジンの `<script>` より先に走らせる必要があるので `document.write`
- `claude_memo.html` … `player.html?deck=claude-memo` へのリダイレクト。
  `location.replace()` で送り、`<noscript>` に meta refresh を残した
- deck 固有のハードコードを `deckConfig` と `slideData.length` から埋めるようにした。
  `<title>`、ヘッダーの見出し、`total-slides` の `17`、
  それに項目には挙げていなかった `playlist-count` の `17 Slides`
- デッキの読み込みに失敗したときは、枠の中に理由を出して `throw` で止める。
  **ガードは再生エンジンの `<script>` の先頭に置く**。`startApp()` に置くと、
  トップレベルで走る `recalcTimeline()` が先に `slideData` を読んで
  TypeError になり、ガードまで届かない（verifier が実測で見つけた）
- `CLAUDE.md` と `tools/measure-duration.py`（参照先を
  `slides-claude-memo.js` に変更）を新しい構成に追従させた

`render()` が返す Tailwind の生の HTML は、そのままデータ側に置いた。
宣言的なレイアウトの語彙に置き換えるのは、17 枚それぞれレイアウトが違って
語彙が 17 種類できるのでやらない。2 本目のスライドを作って共通の型が
見えてから考える。

## 確かめたこと

verifier が Playwright でブラウザから確認（報告は
`archives/agents/TODO-041/verifier-report.md`）。

- スライド 1 の見た目が分割前とピクセル単位で一致
- `<title>` とヘッダーの見出しが `deckConfig` から入る
- `SLIDE 01 / 17`、`17 Slides`、プレイリスト 17 項目、合計時間が埋まる
- 再生・次へ・前へ・プレイリストのクリックが動く
- `claude_memo.html` から飛び、戻るボタンでループしない
- `?deck=nosuch` で枠の中にメッセージが出る。`recalcTimeline` 由来の
  TypeError は出ない
- コンソールエラーは分割前と同じ 0 件
- `tools/measure-duration.py` がナレーションを 17 件取り出せる

reviewer の指摘は要修正 0 件、検討 2 件（読み込み失敗時のガード、
meta refresh が履歴に残る点）。どちらも直した。

## 分担の振り返り

- **verifier が見つけたもの**: ガードの置き場所が遅すぎて効いていないこと。
  静的な読み合わせでは「ガードを書いた」で通ってしまう類いで、
  ブラウザで実際に `?deck=nosuch` を開いたから出た
- **reviewer が見つけたもの**: 読み込み失敗時に白画面になること、
  meta refresh が履歴に残ること。分割そのもの（落ちた行・重複）は 0 件
- **見込みと食い違った理由**: 見込みに reviewer を入れていなかった。
  「ファイルを分けるだけ」と見ていたが、`?deck=` という分岐が新しく入る。
  検討 2 件はどちらも reviewer が出したもので、入れた分は回収できている
- **次に同じ規模なら**: 分割のような「行が移るだけ」の変更でも、
  新しい入口や引数が 1 つでも増えるなら reviewer を入れる。
  逆に、行の突き合わせ（落ちた行・重複の検査）は reviewer に投げるより
  main が `diff` で機械的に見た方が安い。reviewer への依頼は
  新しく入った分岐と、その失敗経路に絞ってよかった
