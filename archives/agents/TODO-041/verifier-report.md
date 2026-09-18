# TODO-041 確認担当 報告

## 検証手段
- ローカルで `python3 -m http.server 8791`（プロジェクト直下）と
  `python3 -m http.server 8792`（分割前の `claude_memo.html` を
  `git show 0b158ca:claude_memo.html` で取り出した一時ファイルを配置）を起動
- `playwright`（chromium, headless）で両方を開き、比較・操作した
  （スクリプトは `/tmp/.../scratchpad/check.py`, `check2.py`, `check3.py`。
  作業ディレクトリはセッション固有の一時ディレクトリで、報告後は不要）

## 1. スライド 1 の見た目比較
分割前後を同条件（1280x720、`networkidle` 後 1 秒待ち）でスクリーンショットし、
Pillow の `ImageChops.difference` で差分を取った。
`diff.getbbox()` → `None`（**ピクセル単位で完全一致**）。

## 2. title / ヘッダー見出し
- 旧: title = `Claude Code 活用法 - プレゼン動画プレイヤー` / h1 = `私の Claude Code の使い方`
- 新（`player.html?deck=claude-memo`）: title 同一 / `#deck-heading` 同一
一致を確認。

## 3. `SLIDE 01 / 17` と `17 Slides`
`#slide-num`=`01`, `#total-slides`=`17`, `#playlist-count`=`17 Slides` を
Playwright で読み取り確認。ハードコードでなく `slideData.length` から
埋まっていることは、旧ファイルとの diff でも確認済み
（旧は `<span id="total-slides">17</span>` と直書き、新は空で
`initPlaylist()` が埋める形に変わっている）。

## 4. プレイリスト 17 項目・合計時間
`#playlist-items > *` の要素数 = 17。`#total-time-display` = `5:58`
（`--:--` ではない）。

## 5. 再生・前後移動・プレイリストクリック
`#mute-btn` でミュートしたうえで操作。
- `#next-btn` クリック: `01` → `02`
- `#prev-btn` クリック: `02` → `01`
- プレイリスト 5 番目（index 4）クリック: `#slide-num` = `05`
- `#play-btn` クリックし 3 秒待機: `#current-time-display` が `0:00` から
  `1:24` に進行（音声はミュートしたが、`requestAnimationFrame` の進行自体は
  独立して動くため妥当）
いずれも意図通り。**コンソールエラーは 0 件**（この一連の操作を通して）。

## 6. `claude_memo.html` のリダイレクト
`http://127.0.0.1:8791/claude_memo.html` を開き、`page.url` が
`http://127.0.0.1:8791/player.html?deck=claude-memo` になることを確認。

## 7. 存在しない `?deck=` を渡したとき
`?deck=nonexistent-xyz` で開いた。結果:
- `slides-nonexistent-xyz.js` の読み込みで **404**
- コンソールに `pageerror: slideData is not defined`
- ただし **画面は真っ白にならず**、ヘッダー（`AI Presentation Video` /
  「インタラクティブ・プレゼンテーション動画プレイヤー」）、再生コントロール、
  速度・待ち時間のセレクタなど外枠は表示された
  （`body_visible=True`、スクリーンショット
  `/tmp/.../scratchpad/unknown_deck.png` に保存。セッション終了で消える
  一時パスなので、再現したい場合は同じ手順で撮り直しが必要）
指示の「エラーは出てよい。少なくとも外枠は出るはず」を満たす。

## 8. コンソールエラーの増減
- 既知の `deck=claude-memo` を開いた場合: 旧ページ・新ページとも
  コンソールエラー 0 件（`cdn.tailwindcss.com should not be used in
  production` という warning は両方に出るが、旧ファイルにも同じ
  `<script src="https://cdn.tailwindcss.com">` があり、分割由来ではない
  pre-existing のものと確認済み）。
- 増えていない。

## 9. `tools/measure-duration.py`
- `python3 tools/measure-duration.py --help` → 終了コード 0、
  使い方が表示された
- `narrations()` 関数（`slides-claude-memo.js` を正規表現で読む部分）を
  直接呼び出して件数を確認 → **17 件**。1 件目・17 件目の冒頭も
  スライド 1・17 の内容と一致することを確認した
- `--all` は指示どおり実行していない（TTS への curl が必要なため）

## 変更ファイルと指示の範囲
`git status --short`:
```
 M CLAUDE.md
 M claude_memo.html
 M tools/measure-duration.py
?? player.html
?? slides-claude-memo.js
```
指示にあった 3 ファイル（新規 2 + リダイレクト用 1）に加え、
`CLAUDE.md` と `tools/measure-duration.py` が変更されている。

- `tools/measure-duration.py`: 指示の 9 番目にある「参照先を
  `slides-claude-memo.js` に直した」変更そのもの。`SRC` 定数が
  `slides-claude-memo.js` を指すよう変わっている（`git diff` で確認済み）。
  範囲内。
- `CLAUDE.md`: 分割後の構成説明（`player.html` / `slides-claude-memo.js` /
  `claude_memo.html` の役割、スライド枚数がハードコードでなくなった旨）に
  更新されている。実装と食い違う記述は見当たらない。文書のみの変更で、
  指示に明記された確認対象ではないが、今回の分割と整合しており、
  意図しない変更が混ざっている様子はない。

指示に無いファイルの変更は見当たらなかった（`CLAUDE.md` は分割の説明
文書であり、範囲外の実装変更ではない）。

## 確かめられなかったこと・判断が要る点
- 実際の音声再生（TTS 音声の発話）そのものは確かめていない
  （指示どおりミュートで進行のみ確認）。
- `tools/measure-duration.py --all` は指示により未実行。TTS を叩く
  17 件分の実測値が分割前と変わっていないかは未確認（指示の範囲外）。
- `CLAUDE.md` の変更が「コードやファイルを変える項目」の確認範囲に
  含まれるかどうかは、管理者の判断が要ると思う。今回は文書として矛盾が
  無いことだけ確認した。

## 追加修正の再確認

### 検証手段
`python3 -m http.server 8791`（プロジェクト直下）を起動し、Playwright
（chromium, headless）で操作した。

### 1. `?deck=` に存在しない名前を渡したときのガード → 効いていない（不具合）
`?deck=nosuch` で `player.html?deck=nosuch` を開いた。

- 期待: 枠の中に「スライドのデータ slides-nosuch.js を読み込めませんでした。」
  と出て、`startApp` 由来の例外は出ない
- 実際: **メッセージは出ず**、コンソールに従来どおり
  `[pageerror] slideData is not defined` が出た

```
=== 1. unknown deck ===
body text contains message: False
console/page errors: ['[warning] cdn.tailwindcss.com should not be used in production. ...', '[error] Failed to load resource: the server responded with a status of 404 (File not found)', '[pageerror] slideData is not defined']
```

**原因（推定、コードは直していない）**: `player.html` 558 行目、
`startApp()` より前のトップレベルで `recalcTimeline()` が即時に呼ばれており
（547〜558 行）、その中の `slideData.map(...)`（551 行）が `slideData` 未定義で
先に例外を投げる。`startApp()` 内（1314〜1329 行）に入れたガードは
`typeof slideData === 'undefined'` のチェックだが、そこへ辿り着く前に
落ちている。

```
541	        // 各スライドの尺は、ナレーションの長さ＋読み終わり後の待ち（TODO-020）
542	        const slideSpan = index => slideData[index].duration + pauseSeconds;
...
549	        function recalcTimeline() {
550	            let accumTime = 0;
551	            slideStartTimes = slideData.map((slide, idx) => {
...
558	        recalcTimeline();
```

画面自体は白画面にはならず、ヘッダーや操作パネルなど枠は出た
（`unknown_deck_guard.png` に保存。一時ディレクトリのため再現するには
同じ手順で撮り直しが必要）。ただし指示の「メッセージが出ること」
「startApp 由来の例外が出ないこと」は満たしていない。

### 2. `claude_memo.html` を `location.replace()` に変更 → 意図通り
`http://127.0.0.1:8791/` → `claude_memo.html` → （自動で `player.html?deck=
claude-memo` へ）という順で開き、ブラウザの戻る操作を行った。

```
=== 2. redirect + back ===
url after redirect: http://127.0.0.1:8791/player.html?deck=claude-memo
url after back button: http://127.0.0.1:8791/
url after back again: about:blank
```

`claude_memo.html` が履歴に残らないため、戻るボタンで
`claude_memo.html` に戻って再び飛ばされるループにはならず、
その前のページ（`http://127.0.0.1:8791/`）に直接戻った。
`<noscript>` に meta refresh が残っていることも `claude_memo.html` の
中身で確認済み。指示どおり。

### 前回通した項目 1〜5（正常系）の再確認 → 壊れていない
`player.html?deck=claude-memo` で以下を再確認した。

```
title: Claude Code 活用法 - プレゼン動画プレイヤー
heading: 私の Claude Code の使い方
slide/total: 01 17
playlist_count: 17 Slides
total_time: 5:58
items: 17
console errors: ['[warning] cdn.tailwindcss.com should not be used in production. ...']
```

next/prev/プレイリストクリック/再生も再実行し、以前と同じ結果
（`01→02→01`、プレイリスト5番目クリックで`05`、再生3秒で
`0:00→1:24`、コンソールエラー0件）だった。回帰は無い。

### 今回の判断
1 は指示どおりに直っていない。2 は指示どおり。

## 追加修正の再々確認（ガード位置の移動後）

### 検証手段
同じく `python3 -m http.server 8791` + Playwright（chromium, headless）。
コードは `player.html` 470〜480 行を確認。ガードが `startApp()` から
再生エンジンの `<script>` 先頭（`let currentIndex = 0;` の直前）へ移り、
`typeof slideData === 'undefined'` のときメッセージを出したあと
`throw new Error(...)` で以降の読み込み時処理（`recalcTimeline()` 含む）を
止める形になっていることを確認した。

### 1. `?deck=nosuch` → 直った
```
=== 1. unknown deck ===
body text contains message: True
console/page errors: ['[warning] cdn.tailwindcss.com should not be used in production. ...', '[error] Failed to load resource: the server responded with a status of 404 (File not found)', '[pageerror] deck not found: nosuch']
```
- 枠の中に「スライドのデータ slides-nosuch.js を読み込めませんでした。」が
  表示された（`body text contains message: True`）
- コンソールは `deck not found: nosuch` の Error と script の 404 のみ。
  `recalcTimeline` 由来の TypeError（`slideData.map is not a function` 等）は
  出ていない

### 2. 正常系（`?deck=claude-memo`）→ 壊れていない
```
title: Claude Code 活用法 - プレゼン動画プレイヤー
heading: 私の Claude Code の使い方
slide/total: 01 17
playlist_count: 17 Slides
total_time: 5:58
items: 17
console errors: ['[warning] cdn.tailwindcss.com should not be used in production. ...']
```
スライド 1 のスクリーンショットを分割前（`old_slide1.png`）と
`ImageChops.difference` で比較 → `diff bbox: None`（ピクセル完全一致）。
next/prev/プレイリストクリック/再生も再実行し、以前と同じ結果
（`01→02→01`、プレイリスト5番目クリックで`05`、再生3秒で
`0:00→1:24`、コンソールエラー0件）だった。

### 結論
1・2 とも指示どおり。前回指摘した不具合は解消されている。
