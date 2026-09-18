# TODO-025 検証報告

## 差分の範囲

`git diff HEAD -- claude_memo.html` を確認した。変更は依頼どおり 2 種類のみ:

1. スライド並べ替え: 旧 `id: 10`（マルチエージェントで役割分担）と
   旧 `id: 11`（TODO.md の実際の記述例）の中身がまるごと入れ替わり、
   `id: 10` = 記述例、`id: 11` = 役割分担 になっている。`// Slide 10` /
   `// Slide 11` のコメントも中身と一致
2. スライド 2: 2x2・4 枚 + 末尾 1 行 → 2x3・6 枚のカードに書き直し。
   `gap` は `1.5cqw` → `1.2cqw`、カードの `padding` は `1.6cqw` → `1.3cqw`
   に詰めてある（diff で確認）。ナレーションも新しい 6 項目に合わせて
   書き直されている

指示に無いファイルの変更は無い（`archives/agents/TODO-025/` は今回作成した
未追跡ディレクトリのみ）。

## 完了条件ごとの確認

- **`slideData` の並びと `id`**: `grep -n "id: [0-9]*,"` で 1〜17 が配列の
  出現順と完全一致することを確認
- **`// Slide N` コメントと `id` のずれ**: `grep -n "// Slide"` の行番号順が
  1〜17 で、直後の `id:` と一致することを確認（並べ替え後もずれ無し）
- **スライド 10/11 のタイトル**: `id: 10` の直後の `title` が
  `'TODO.md の実際の記述例'`、`id: 11` が `'マルチエージェントで役割分担'`
  であることを `sed` で実測確認
- **`duration` 合計**: 全 17 件の `duration` 値
  `18,19,19,19,21,19,19,19,18,21,19,15,17,17,17,17,22` を `python3` で
  合計し `316`。`formatTime` は `Math.floor` ベースの mm:ss 変換なので
  316 秒 = `5:16` になる
- **スライド 2 のナレーション実測**: `prepareSpeechText()` の置換ルール
  （`TODO.md` → 読み上げ表記、`main`/`implementer` の単語境界置換など全 19 件）
  と `TTS_MAX_CHARS = 180`、`BASE_SPEED_MULTIPLIER = 1.4` を、
  `claude_memo.html` の実装（1137, 1164, 1243-1266 行）と、依頼にあった
  `measure.py` を **1 行ずつ突き合わせて確認**。正規表現・置換文字列・順序とも
  完全一致していた。実測:
  ```
  slide 2: 原文 114字 / 読み 126字 / 実測 27.240s / 1.4倍速 19.46s -> duration: 19
  ```
  切り詰め無し（126字 < 180字）。四捨五入後の `duration: 19` は
  `slideData[1].duration = 19` と一致
- **JS エラー**: Playwright（`chromium`）で `console.error` /
  `pageerror` を監視しながら、機能テスト・play/pause スモークテストを
  実行し、0 件だった
- **送りと再生**: 17 枚あり、`#next-btn` を 16 回押して `slide-num` が
  `17` になり、17 で止まったまま 17 回目を押してもクラッシュせず
  `17` のまま。`#prev-btn` を 16 回押して `01` に戻ることを確認
- **プレイリストの番号と見出し**: `#playlist-items` を全件取得し、
  `10 TODO.md の実際の記述例` → `11 マルチエージェントで役割分担` の順で
  出ていることを実測（他の項目も 1〜17 で番号とタイトルが対応）
- **レイアウトのはみ出し**: `archives/agents/TODO-029/layout-check.mjs` を
  コピーして直し（`archives/agents/TODO-025/` には置いていない。作業ファイルは
  `/tmp/verify064b/` に置いた）、`measureOverflow()` の `page.goto` 直後に
  `#next-btn` クリックでスライド 2 へ進めてから測るよう変更した。
  BEFORE（`git show HEAD:claude_memo.html`）と AFTER（作業ツリー）を
  それぞれ `python3 -m http.server` でローカルに立てて比較。
  4 条件すべてで **ドキュメント全体のスクロール量は before/after で差分 0px**:
  ```
  PC 1280x800:            dX=0 dY=0
  横持ち 844x390 通常:     dX=0 dY=0（overflowY=841px は before/after とも同じ。今回の変更起因ではない既存の値）
  横持ち 844x390 フルスクリーン: dX=0 dY=0
  縦持ち 390x844 フルスクリーン: dX=0 dY=0
  ```
  ただしこの計測は `document.scrollWidth/Height` ベースで、
  `#slide-canvas` は `overflow-hidden` が掛かっているため、ページ全体は
  はみ出さなくても **カード内部で見切れている可能性**は別途確かめる必要が
  あると判断し、追加で `#slide-canvas` の `scrollHeight/clientHeight` と、
  カードのグリッド（`.grid`）の `getBoundingClientRect()` を
  `#player-viewport` の枠と突き合わせて実測した（AFTER のみ、4 条件）:
  ```
  PC 1280x800:                  internalOverflow X=0px Y=0px / grid.bottom - viewport.bottom = -73.0px（余裕あり）
  横持ち 844x390 通常:           internalOverflow X=0px Y=0px / grid.bottom - viewport.bottom = -61.7px
  横持ち 844x390 フルスクリーン: internalOverflow X=0px Y=0px / grid.bottom - viewport.bottom = -43.6px
  縦持ち 390x844 フルスクリーン: internalOverflow X=0px Y=0px / grid.bottom - viewport.bottom = -31.7px
  ```
  いずれも負の値（= グリッドの下端が枠の下端より上にあり、はみ出していない）。
  最も余裕が少ないのは縦持ちフルスクリーンで 31.7px。内部スクロールも
  4 条件とも 0px

## Playwright スクリプトの実行結果

`archives/agents/TODO-029/layout-check.mjs` を直したもの
（`/tmp/verify064b/layout-check-025.mjs`、`#next-btn` クリックを追加）を実行し
15 件中 15 件 OK（`SUMMARY: 15/15 passed`、終了コード 0）。

内部見切れ確認用に追加で書いたスクリプト
（`/tmp/verify064b/slide2-internal-overflow.mjs`）も実行し、上記の通り 4 条件
すべて問題無かった。

## 測っていないこと・判断が要ること

- **BEFORE 側のスライド 2 の内部はみ出し measurement は実施していない**
  （BEFORE は 4 枚構成で今回の懸念点ではないため）。AFTER のみ測った
- **「はみ出しが変更前から増えていない」の判定は、ドキュメント全体の
  スクロール量（`document.scrollWidth/Height`）でしか before/after 比較
  していない。** `#slide-canvas` の内部見切れは AFTER 単体でしか測っておらず、
  BEFORE との差分としては見ていない（BEFORE のスライド 2 は構成が違うため
  単純比較しにくいと判断したが、この判断自体は管理者の確認を仰ぎたい）
- 横持ち通常条件で before/after とも `overflowY=841px` という値が出ている。
  これは既存の（今回の変更と無関係の）挙動と見ているが、詳しい原因は
  追っていない
- フルスクリーン計測は headless Chromium の Fullscreen API 制約により、
  `#fullscreen-btn` クリックによる近似（TODO-029 のスクリプトの手法を踏襲）。
  実ブラウザでの目視確認はしていない
