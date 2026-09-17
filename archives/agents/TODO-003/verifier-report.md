# TODO-003 verifier report

## 検証方法

`pip3 install --user playwright` でインストールし、システムの
`/usr/bin/chromium` を `executable_path` に指定して Playwright から
無事に起動できたため、実ブラウザでの実測を行った（別途ブラウザバイナリの
ダウンロードは不要だった）。

- 3 条件（844x390 タッチ、390x844 タッチ、1280x800 マウス）で
  `claude_memo.html` を `file://` で読み込み、`#fullscreen-btn` をクリックして
  擬似フルスクリーンへ入れた状態で、`document.body` の class・
  computed `overflow`、`#viewport-stage::before` の computed style、
  `documentElement` の `scrollWidth/clientWidth/scrollHeight/clientHeight`
  を取得した。
- `git stash` で変更前の状態に戻し、同じスクリプトを再実行して差分を比較した。
- 暗幕タップで抜ける経路は、844x390 タッチ条件で `#viewport-stage` へ
  `target` をラッパー自身にした合成 `click` イベントを dispatch し、
  `is-fullscreen` クラスが外れることを確認した。
- 追加確認として、レターボックスの余白にあたる実座標を
  `page.mouse.click(x, y)` で叩き、`elementFromPoint` と `is-fullscreen`
  の変化を見た（下記「追記」節）。

使用したスクリプトはスクラッチパッド
（`/tmp/claude-649/.../scratchpad/verify.py`, `verify_tap.py`,
`verify_tap_real.py`）に置いた。リポジトリには置いていない。

## 1. CSS が壊れていないか

`claude_memo.html` 207〜260 行付近を読んだ。

- `@media screen and (max-width: 767.98px) { ... }`（190〜222 行）から
  `body.fs-lock` と `#viewport-stage.is-fullscreen::before` のルールが
  消えている。このブロックに残っているのは `#viewport-frame`、
  `#subtitle-banner`、`#viewport-stage.is-fullscreen > #subtitle-banner`、
  `#player-viewport`、`.video-viewport.pseudo-fullscreen` の 5 ルールで、
  ブレースは対応している。
- 新しく足された `@media screen and (max-width: 767.98px), screen and
  (pointer: coarse) { ... }`（224〜251 行）に、上記 2 ルールが 1 組だけ
  移っている。`grep -n "fs-lock\|is-fullscreen::before" claude_memo.html`
  の結果は CSS 側 2 行（238, 245 行目）と JS 側 1 行（1717 行目、
  `classList.toggle`）のみで、重複や取りこぼしは無い。
- `<style>` ブロック全体を通してブレース対応が崩れている様子は無い
  （該当範囲を目視で確認。ビルドツールが無いプロジェクトなので、
  CSS パーサーによる機械チェックまでは行っていない）。

**結果: 問題なし。**

## 2. 767.98px 未満の挙動が変更前と変わらないか

Playwright で 390x844（タッチ）を変更前後で比較した。

- 変更前: `{'hasFsClass': True, 'hasFsLock': True, 'bodyOverflow': 'hidden', 'beforeContent': '""', 'beforeZ': '-1', 'beforeDisplay': 'block', 'scrollWidth': 390, 'clientWidth': 390, 'scrollHeight': 844, 'clientHeight': 844}`
- 変更後: 上と完全に同一の値。

`--vp-scale` を使う `#player-viewport` のルール・字幕の位置ルールは
移動対象外で diff にも出ていないため、コードとしても変更が無いことを
確認済み（diff 参照）。

**結果: 767.98px 未満の実測値は変更前後で完全一致。挙動は変わっていない。**

## 3. マウスの PC（幅 768 以上・pointer: fine）で暗幕・fs-lock が効かないままか

1280x800・タッチ無しで比較した。

- 変更前: `{'hasFsClass': True, 'hasFsLock': True, 'bodyOverflow': 'hidden auto', 'beforeContent': 'none', 'beforeZ': 'auto', 'beforeDisplay': 'inline', ...}`
- 変更後: 上と完全に同一の値。

`hasFsLock`（class の有無）は JS が無条件に付けるため True のままだが、
`bodyOverflow` は `hidden auto`（＝ページ全体で元々 `overflow-x: hidden`
だった分のみで、fs-lock の `overflow: hidden` は掛かっていない）、
`beforeContent` は `none`（暗幕が描画されていない）で、これは
`body { overflow-x: hidden; }`（47 行目、fs-lock とは無関係の既存ルール）
による見た目の一致であり、fs-lock 由来の効果ではないことを、変更前との
一致で確認した。

**結果: PC・マウスでは暗幕・fs-lock の実効果は変更前後とも掛かっていない。**

## 4. 幅 768 以上のタッチ画面で暗幕・fs-lock・暗幕タップで抜ける経路が成立するか

844x390（タッチ）で比較。

- 変更前: `beforeContent: 'none'`, `bodyOverflow: 'hidden auto'`
  （暗幕が出ず、fs-lock も効かない＝TODO-003 が説明する不具合そのもの）
- 変更後: `beforeContent: '""'`, `beforeZ: '-1'`, `beforeDisplay: 'block'`,
  `bodyOverflow: 'hidden'`（暗幕が描画され、裏のスクロールも止まる）

暗幕タップで抜ける経路は、`#viewport-stage` へ `target` をラッパー自身に
した合成 click イベントを dispatch したところ、`is-fullscreen` クラスが
`True` → `False` に変わることを確認した（実座標での確認は下記「追記」節）。

JS 側の前提（`setFullscreen`・`#viewport-stage` の click ハンドラが幅で
分岐していないこと）は、`grep -n "setFullscreen\|viewport-stage"
claude_memo.html` で該当箇所（1712〜1734 行）を読み、`innerWidth` や
`matchMedia` を使った分岐が無いことを確認した。分岐は CSS の `@media` に
だけあり、JS はクラスの付け外しのみを行っている。

**結果: 768 以上・タッチでも、暗幕・fs-lock・暗幕タップで抜ける経路が
すべて成立することを実測で確認した（実座標での再現は下記「追記」節でも
確認済み）。**

## 5. 裏のページに横スクロールバー・余分な縦スクロールが出ていないか

3 条件すべてで `documentElement.scrollWidth === clientWidth`
（844=844, 390=390, 1280=1280）だった。横スクロールは出ていない。

縦方向は 844x390 条件で `scrollHeight: 812 > clientHeight: 390` と、
コンテンツの高さが表示領域を超えている（字幕がはみ出す分、TODO.md で
「見えなくてよい」と決めた点に該当）。ただし `bodyOverflow: 'hidden'`
（fs-lock の効果）により `overflow` が禁止されているため、**この超過分は
スクロールバーとしては現れない**（overflow: hidden はスクロール自体を
禁止する）。実測上、Playwright はスクロールバーの有無を直接は返さないが、
`overflow: hidden` の computed style が確認できているため、スクロール
可能な UI が出ないことは論理的にも確認できる。

**結果: 横スクロールバーは出ない。縦方向は overflow: hidden により
スクロールとしては現れない（はみ出し自体は TODO.md で許容済み）。**

## 追記: 暗幕タップを実座標で確認

管理者からの追加指示により、合成イベントではなく実座標でのクリックを
`page.mouse.click(x, y)` で行い、レターボックスの余白（箱の外）に実際に
タップが当たるかを確認した。

- 844x390（タッチ）: `#viewport-frame` の矩形は
  `left: 75.3, right: 768.7, top: 0, bottom: 0`（横長なので左右に余白）。
  余白の内側の点 `(10, 195)` で `elementFromPoint` を取ると
  `viewport-stage`（暗幕を含むラッパー自身）が返り、実クリック後に
  `is-fullscreen` が `True → False` に変わった。
- 390x844（タッチ）: `#viewport-frame` の矩形は
  `left: 0, right: 390, top: 312.3, bottom: 531.7`（縦長なので上下に余白）。
  余白の点 `(195, 10)` でも同じく `elementFromPoint` は `viewport-stage`、
  実クリック後に `is-fullscreen` が `True → False` に変わった。

**変更前（`git stash` で確認）との比較:**

- 844x390: 変更前は `elementFromPoint` が `MAIN`（暗幕が無いので裏の
  要素が拾われる）で、実クリック後も `is-fullscreen` は `True` のまま
  （抜けられない＝TODO-003 が指す不具合そのもの）。変更後は
  `viewport-stage` が拾われ、`False` に変わる。**この点だけが変更前後で
  変わっており、直したい対象がちょうど直っている。**
- 390x844: 変更前・変更後とも `elementFromPoint` は `viewport-stage`、
  実クリック後は `True → False`。**縦画面は変更の前後で挙動が変わって
  いない。**

**結果: z-index: -1 の暗幕は、実際のタップ座標でも `#viewport-stage`
自身（＝ `e.target === stage` の条件を満たす要素）としてヒットテストされ、
768 以上・横持ちタッチでも実タップでフルスクリーンを抜けられることを
確認した。縦画面の実タップ挙動は変更前後で変わっていない。**

## 変更ファイルの確認

`git status` / `git diff --stat`:

```
 CLAUDE.md        |  8 +++++---
 claude_memo.html | 51 +++++++++++++++++++++++++++++----------------------
 2 files changed, 34 insertions(+), 25 deletions(-)
```

指示された対象範囲（`claude_memo.html` と `CLAUDE.md` のみ）と一致する。
`CLAUDE.md` の変更は、既存の説明文を新しい条件に合わせて書き直しただけで、
指示（TODO-003 の節）の内容と食い違いは無い。

## 確かめられなかったこと・判断できないこと

- 実ブラウザでの `#fullscreen-btn` の可視性・実クリック可否（座標がボタンを
  覆っていないか等）までは踏み込んでいない。JS の `.click()` で直接
  イベントを発火させて確認した。
- 暗幕タップの経路は、当初は合成イベントのみで確認していたが、追加指示を
  受けて実座標でのクリックでも確認した（上記「追記」節）。今回試した点は
  各条件 1 点のみで、余白の別の位置（角に近い部分など）まで網羅的には
  試していない。
- CSS の構文チェックは専用パーサーではなく目視・grep によるもの。
