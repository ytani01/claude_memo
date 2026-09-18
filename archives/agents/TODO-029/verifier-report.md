# TODO-029 検証報告

## 検証方法

`git show HEAD:claude_memo.html`（変更前）と作業ツリーの `claude_memo.html`
（変更後）を、それぞれローカル HTTP サーバー（127.0.0.1:18900 / 18899）で
配信し、Playwright (chromium, headless, node_modules は `/tmp/verify064` の
既存インストールを再利用) で自動操作した。スクリプトは
`/tmp/verify064/test_todo029.mjs`。

## 結果: 15/15 passed（終了コード 0）

```
OK total-slides = 17 :: got=17
OK slide-num starts at 01 :: got=01
OK playlist has 17 items :: got=17
OK after 16x next -> slide-num 17 :: got=17
OK next at last slide stays at 17 (no crash) :: got=17
OK after 16x prev -> slide-num 01 :: got=01
OK #slide-category element absent
OK <footer> element absent
OK SLIDE badge sits at right edge of header (not left) :: gapToRight=0.0 gapToLeft=712.0
CONSOLE_ERRORS(after, functional test): []
OK no console errors during functional test :: []
CONSOLE_ERRORS(after, play smoke): []
OK no console errors during play/pause smoke :: []
--- PC 1280x800 ---
  before: overflowX=0px overflowY=0px viewportRight=942 viewportBottom=605.375 innerW=1280 innerH=800
  after : overflowX=0px overflowY=0px viewportRight=942 viewportBottom=605.375 innerW=1280 innerH=800
OK overflow not increased: PC 1280x800 :: dX=0 dY=0
--- 横持ち 844x390 通常 ---
  before: overflowX=0px overflowY=926px viewportRight=820 viewportBottom=536.75 innerW=844 innerH=390
  after : overflowX=0px overflowY=885px viewportRight=820 viewportBottom=536.75 innerW=844 innerH=390
OK overflow not increased: 横持ち 844x390 通常 :: dX=0 dY=-41
--- 横持ち 844x390 フルスクリーン ---
  before: overflowX=0px overflowY=466px viewportRight=768.65625 viewportBottom=390 innerW=844 innerH=390
  after : overflowX=0px overflowY=425px viewportRight=768.65625 viewportBottom=390 innerW=844 innerH=390
OK overflow not increased: 横持ち 844x390 フルスクリーン :: dX=0 dY=-41
--- 縦持ち 390x844 フルスクリーン ---
  before: overflowX=0px overflowY=0px viewportRight=390 viewportBottom=531.6875 innerW=390 innerH=844
  after : overflowX=0px overflowY=0px viewportRight=390 viewportBottom=531.6875 innerW=390 innerH=844
OK overflow not increased: 縦持ち 390x844 フルスクリーン :: dX=0 dY=0
SUMMARY: 15/15 passed
```

## 完了条件ごとの確認結果

- **`category` / `footer` の語が残っていない**: `grep -ni "category" claude_memo.html`
  と `grep -ni "footer" claude_memo.html` はいずれも 0 件（確認済み）
- **JS エラーが出ない**: 機能テスト中・play/pause のスモークテスト中とも
  console error / pageerror は 0 件（上記ログの `CONSOLE_ERRORS` 参照）
- **スライドが 17 枚とも表示され、送りと再生が動く**: `#total-slides` は
  17、`#playlist-items` の子要素は 17 個。`next-btn` を 16 回押して
  `#slide-num` が `17` まで進み、最後で止まって（次を押しても壊れず
  `17` のまま）、`prev-btn` を 16 回押して `01` まで戻ることを確認。
  再生ボタン (`#play-btn`) を押してもエラーは出ない（実際の音声再生・
  字幕の同期の秒数レベルの検証まではしていない）
- **`SLIDE nn / 17` が枠の右上に残っている**: ヘッダー行の右端との差
  (`gapToRight`) が 0.0px、左端との差 (`gapToLeft`) が 712.0px で、
  明確に右寄せになっている（実測値）
- **レイアウトのはみ出しが変更前から増えていない**: 指定された 4 条件
  すべてで、変更前後の overflowX / overflowY を実測して比較。
  PC と縦持ちフルスクリーンは差分 0px（変化なし）、横持ち 2 条件は
  むしろ overflowY が 41px 減った（footer 削除でページ全体の高さが
  減ったため。悪化なし）

## 変更ファイルの確認

`git status` / `git diff --stat`: 変更されたのは `claude_memo.html` のみ
（1 file changed, 1 insertion(+), 29 deletions(-)）。`archives/agents/TODO-029/`
は未追跡の報告用ディレクトリで、これ以外の意図しないファイル変更は無い。

`git diff` の中身は依頼書の 4 種類の変更（ヘッダーの category span と
パルス点の削除・`justify-between`→`justify-end`、`<footer>` の削除、
`slideCategory` の取得と代入の削除、17 要素すべての `category: '...',` の
削除）とちょうど一致している。

## 確かめられなかったこと・判断が要る点

- **横持ち／縦持ちのフルスクリーン条件は、headless chromium の制約で
  `requestFullscreen()` を実ブラウザ相当には再現できていない。**
  `#fullscreen-btn` をクリックする形で近似したが、実際に fullscreen API
  が発火したかは未確認。ただし変更前・変更後を**同じ近似方法**で
  比較しているため、相対的な「はみ出しが増えたか」の判定自体は
  有効だと考える（絶対値としての実機フルスクリーン表示は未確認）
- 再生の音声・字幕同期（TTS の実際の発話とキャプション送りのタイミング）
  は今回の変更対象外のため検証していない
- Playwright は本プロジェクトに `node_modules` が無かったため、
  同じマシン上の他プロジェクト用に既に `npm install` 済みだった
  `/tmp/verify064/node_modules` を再利用した（このプロジェクトの
  `package.json` 等は変更していない）
