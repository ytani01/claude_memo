# TODO-001 implementer 報告（2 巡目）

対象は `claude_memo.html` のみ。1 巡目の未コミット差分を土台に、reviewer の
指摘 1〜5・7〜9 を指示どおり直した。コミットはしていない。

## 直した点（`ファイル:行` は修正後の行番号）

### 1. 字幕バナーを縮小枠の外へ出した（指摘 1）

- `claude_memo.html:284` `<div id="viewport-stage">` を新設し、
  `#viewport-frame` と `#subtitle-banner` を兄弟にした
- `claude_memo.html:334` 閉じタグ（`<!-- /#viewport-stage -->`）
- `claude_memo.html:291-333` バナーの DOM を `#player-viewport` の外へ移動
- `claude_memo.html:137-139` `#viewport-stage { position: relative }`（PC で
  バナーを枠に重ねる基準）
- `claude_memo.html:176-182` 768px 未満では `position: static; margin: 0.75rem 0 0`
  で枠の下へ流す

**1px のずれを消した**: `claude_memo.html:149-152` `#subtitle-banner { margin: 1px }`。
基準の箱が `#player-viewport` のパディングボックス（1px ボーダーの内側）から
`#viewport-stage` のコンテンツボックス（＝ボーダーボックス）に変わるので、
そのままだと PC でバナーが 1px 下・2px 広くなる。margin で戻して HEAD と
ピクセル一致させた（下の検証参照）。

**フルスクリーン中の字幕**: `claude_memo.html:154-165`
`#viewport-frame.is-fullscreen ~ #subtitle-banner`。バナーを枠の外へ出した
副作用で、そのままだとフルスクリーン中（PC・スマホとも）に字幕が暗幕や
レターボックスの裏に隠れて見えなくなる。HEAD ではフルスクリーンでも字幕が
出ていたので、`min()` でレターボックスの位置を計算して同じ場所に固定した。
PC のフルスクリーン時のバナー矩形は HEAD と完全一致（実測）。

### 2. 暗幕を実体のある要素にした（指摘 2）

- `claude_memo.html:216-230` `#viewport-frame.is-fullscreen::before`
  （`position: fixed` で全面、`background: rgba(2,6,23,0.92)`、`touch-action: none`、
  `z-index: -1`）。`box-shadow` による暗幕は削除した
- `claude_memo.html:129-132` `body.fs-lock { overflow: hidden }` と
  `claude_memo.html:1633` の `classList.toggle('fs-lock', on)` で、フルスクリーン中は
  裏のページをスクロールさせない
- `claude_memo.html:212-213` `#viewport-frame.is-fullscreen { overflow: visible }`。
  下の `overflow: hidden`（指摘 4）で暗幕が切られないようにするため

### 3. `:has()` をやめて JS でクラスを付けた（指摘 3）

- `claude_memo.html:1626-1636` `setFullscreen(on)` を新設。
  `#player-viewport` の `pseudo-fullscreen`、`#viewport-frame` の `is-fullscreen`、
  `body` の `fs-lock`、ボタンのアイコンを 1 か所でまとめて入れ替える
- `claude_memo.html:1638-1641` ボタンの click は `setFullscreen(!現在の状態)` を呼ぶだけ
- `claude_memo.html:1673-1676` Esc も同じ `setFullscreen(false)` を呼ぶ
  （以前はアイコン更新が 2 か所に重複していた）
- `claude_memo.html:200` CSS は `#viewport-frame.is-fullscreen` に変更

### 4. 縮小の境界を 768px に上げた（指摘 5）

- `claude_memo.html:169` `@media screen and (max-width: 767.98px)`。
  ちょうど 768px では Tailwind の `md:` が効くので、二重に当たらないよう
  Tailwind と同じ `767.98px` にした

### 5. 細かい直し

- `claude_memo.html:172-175` `#viewport-frame { overflow: hidden }` を
  **768px 未満のみ**に入れた（指摘 4）。
  **PC には入れていない**: PC で入れると `.video-viewport` の
  `box-shadow: 0 25px 50px -12px` が枠で切られ、プレイヤー下の影が消える
  （スクリーンショット比較で検出。差分 16 万画素）。PC では 960px の箱に
  ならないので、そもそも保険が要らない
- `claude_memo.html:1715-1721` `setupViewportScale()` から
  `else { window.addEventListener('resize', update) }` を削除（指摘 7）。
  `ResizeObserver` が無ければ早期 return する
- `claude_memo.html:1719-1720` `clientWidth` → `getBoundingClientRect().width`（指摘 8）
- `#slide-canvas .overflow-x-auto .inline-flex { flex-shrink: 0 }` を削除（指摘 9）

### 6. `CLAUDE.md` は**触っていない**（指摘 6）

自分の役割では文書を触らないことになっているため、下書きだけ置く（文面は
管理者・wording の判断で）。

```
- **768px 未満は container query と別系統で縮小している。** `#viewport-frame`
  が 16:9 の外枠になり、`setupViewportScale()` が `--vp-scale` を入れて
  `#player-viewport`（960x540 のまま）を `transform: scale()` で縮める（TODO-001）
- そのため `#player-viewport` の中の `md:` ユーティリティは縮小の対象になる。
  固定 px のクロームを枠の中に足すとスマホで読めない大きさになる
- 字幕バナー（`#subtitle-banner`）だけは縮小されないよう枠の外
  （`#viewport-stage` 直下）に置いてある
```

## 検証

このリポジトリにビルド・テストは無い（`CLAUDE.md`）ので、Chromium
（`~/.cache/ms-playwright/chromium-1234`、`playwright-core`、`file://`）で実測した。
スクリプトは scratchpad に置いた（`check2.js` / `cmp.js` / `fs.js` / `dom.js`）。
すべて終了コード 0、**コンソールエラー・pageerror はどのサイズでも 0 件**。

### はみ出しの検出方法と結果

`#slide-canvas` の全子孫の矩形を canvas の矩形と比べ、上下は全要素、左右は
`.overflow-x-auto` の外にある要素だけを見て 1px 超のはみ出しを数えた。
検出器の妥当性は HEAD で確認済み（HEAD の 641x900 で
`s4:+14, s8:+45, s12:+26, s13:+14, s15:+8, s17:+3` を検出。reviewer の
「スライド 4 / 13 / 17 で +14 / +14 / +3」と一致する）。

修正後は **全 11 サイズ × 17 スライドではみ出し 0**。

| 幅x高 | 枠 | scale | 字幕 font | バナー位置 |
|-------|----|-------|-----------|-----------|
| 360x800 | 328x184.5 | 0.342 | 14px | static（枠の下） |
| 390x844 | 358x201.4 | 0.373 | 14px | static |
| 430x932 | 398x223.9 | 0.415 | 14px | static |
| 641x900 | 609x342.6 | 0.634 | 14px | static |
| 700x900 | 668x375.8 | 0.696 | 14px | static |
| 767x900 | 735x413.4 | 0.766 | 14px | static |
| 768x900 | 720x405 | 1.0 | 16px | absolute（枠に重なる） |
| 844x390（横持ち） | 796x447.8 | 1.0 | 16px | absolute |
| 932x430（横持ち） | 884x497.3 | 1.0 | 16px | absolute |
| 1280x800 | 918x516.4 | 1.0 | 16px | absolute |
| 1440x900 | 918x516.4 | 1.0 | 16px | absolute |

`scrollWidth == innerWidth` が全サイズで成立（横方向のはみ出し無し）。

### PC で HEAD と同じか

1280x800 / 1440x900 / 1920x1080 で、HEAD 版（`git show HEAD:` を別ファイルに
出したもの）と比較した。

- 主要 7 要素（header / `#player-viewport` / `#slide-canvas` / `#subtitle-banner` /
  `#seekbar-container` / `#fullscreen-btn` / footer）の矩形が
  **3 サイズとも小数点以下まで完全一致**。バナーは HEAD・修正後とも
  1280 で `41,492.4,884,100`
- フルスクリーン時も一致。1280 で viewport `0,40,1280,720`、
  バナー `17,647,1246,100`（HEAD と同じ）
- スクリーンショットのピクセル差分: 差のある画素は
  `bbox (40,604)-(926,645)` の 1777 画素のみ、**最大差 7/255**。
  位置はプレイヤー直下の影のグラデーション帯で、合成時の丸め差。
  目視できるずれではない（枠・文字・バナーの位置は 1 画素も動いていない）

### フルスクリーン（縦画面、`isMobile: true` / `hasTouch: true`）

360x800 / 390x844 / 430x932 / 767x900 の 4 サイズで実測。

- 外枠が画面幅いっぱいの 16:9 レターボックスになり、中身は `--vp-scale` で
  そのまま縮む（390x844 で frame `0,312,390,219`、scale 0.406）
- `elementFromPoint` の四隅（`(5,5)` / 上中央 / 下中央 / 右下）が
  **すべて `viewport-frame`**（＝暗幕）を返す。reviewer が報告した
  「ヘッダーやフッターに当たる」状態は解消
- フルスクリーン中に `mouse.wheel(0, 500)` しても `scrollY` は 0 のまま
- 字幕はレターボックスの下端（`bottom-3` 相当）に `z-index: 10000` で出る
- Esc で `pseudo-fullscreen` / `is-fullscreen` / `fs-lock` の 3 つとも外れ、
  アイコンが `fa-expand` に戻り、バナーが `static` に戻る

### DOM 構造

`#viewport-stage` の子は `[viewport-frame, subtitle-banner]`、
stage の次の兄弟がコントロールパネル。タグの閉じ忘れは無い。

## 判断が要る点・残る懸念

1. **`CLAUDE.md` は未修正**（上に下書きあり）。管理者側で入れてほしい。
2. **横持ち（844x390、932x430）は縮小の対象に入らない。** 指示では
   「768px に上げれば横持ちも縮小の対象に入る」とあったが、844 も 932 も
   768 より大きいので PC と同じ経路のままになる。実測でははみ出しが無く、
   枠も幅いっぱい（796px / 884px）なので完了条件は満たすが、枠の高さ
   （448px / 497px）が画面の高さ（390 / 430）を超えるため、スライド全体を
   見るには縦スクロールが要る。これは HEAD と同じ挙動。直すなら
   「高さでも縮小する」話になり範囲外なので手を付けていない。
3. **`body.fs-lock` は PC のフルスクリーンにも効く**（HEAD では裏のページが
   スクロールできた）。見た目は変わらないが挙動の変化なので明記しておく。
   iOS Safari では `body { overflow: hidden }` だけだとスクロールが
   止まりきらないことがあり、暗幕の `touch-action: none` と併用している。
   それでも漏れるようなら `position: fixed` + スクロール位置の保存が要る。
4. **フルスクリーン中の字幕位置は `min()` の計算に依存する。**
   `.video-viewport.pseudo-fullscreen` のレターボックス指定（`max-width:
   calc(100vh * (16/9))` など）を変えたら、`#viewport-frame.is-fullscreen ~
   #subtitle-banner` の `left` / `right` / `bottom` も一緒に直す必要がある。
   同じ比率が 2 か所に書かれている状態。
5. **PC のプレイヤーの影と `overflow: hidden` は両立しない。** 指摘 4 の
   `overflow: hidden` を PC にも入れると影が消えるので、768px 未満限定にした。
   指示からの逸脱にあたるため、意図的である旨をここに残す。
6. 縮小されたままの `#slide-category` などのクローム（指示どおり対応せず）は、
   360px 幅で 4〜5px のままになる。
