# TODO-001 reviewer 報告（3 巡目）

対象: `claude_memo.html` / `CLAUDE.md` / `TODO.md` の未コミット差分（`git diff`）。
コードは直していない。コミットもしていない。

## 実測の環境

Chromium `/home/ytani/.cache/ms-playwright/chromium-1234/chrome-linux/chrome`、
`playwright-core`（`/home/ytani/work/ytBackgammon/node_modules`）、`file://` 読み込み。
比較用の HEAD 版は `git show HEAD:claude_memo.html` を別ファイルに出して同条件で測った。
スクリプトは scratchpad の `rv3/t1.js`〜`t9.js`。

---

## 要修正

### 1. `CLAUDE.md:41` の `md:` の説明が逆。1 巡目の指摘 1 の後半も未解決のまま

**場所**: `CLAUDE.md:38-42`、`claude_memo.html:160-163`（`/* Mobile: 中身は PC と
同じ 960x540 のまま描き… */` のコメント）。

**何が問題か（文書）**: `CLAUDE.md:41` は

> そのため `#player-viewport` の中の `md:` ユーティリティも縮小の対象になり、

と書いているが、`md:` は `min-width: 768px` なので **768px 未満ではそもそも
適用されない**。実測（t7、`#slide-category` の computed font-size）:

| ビューポート幅 | `#slide-category` | ヘッダー行 | `#slide-num` |
|---|---|---|---|
| 390 / 767 | 12px（`text-xs`） | 14px | 14px |
| 768 / 1280 | **14px**（`md:text-sm`） | **16px** | **16px** |

縮小されるのは `md:` の**付いていない側**（スマホ向けに小さい方）で、`md:` が
効いているものではない。同じ理由で `claude_memo.html:162-163` の
「cqw も clamp() も常に 960px 基準で解決されるので、**PC の見た目がそのまま
小さくなる**」も成立していない。この文は 1 巡目の指摘 1 が名指しで
「この 4 要素については成立していない」と書いたものが、そのまま残っている。

**何が問題か（実装）**: 1 巡目の指摘 1（要修正）は「字幕バナー**と
スライド上部の情報**が 5px 前後になり、読めない」だった。2 巡目で字幕は
枠の外に出して解決したが、**スライド上部のクロームは手当てされていない**。
390x844 で実測（t8）:

| 要素 | 今回の実効サイズ | HEAD |
|---|---|---|
| `#slide-category`（CLAUDE CODE WORKFLOW） | **4.5px** | 12px |
| `SLIDE 01 / 17` の行 | **5.2px** | 14px |
| 参考: スライド本文 `h1` | 17.0px | 28.8px |

`--vp-scale` が 0.373 なので、`text-xs`(12px) と `text-sm`(14px) がそのまま
0.373 倍される。本文は `cqw` 基準なので 17px 残る。

**どうなると困るか**: `CLAUDE.md` は次に触る人が読む唯一の注意書きなので、
`md:` の効き方を逆に覚えると「`md:` を付ければ大きくなる」と誤解して直す。
実装側も、1 巡目に要修正と判定された 2 つのうち片方だけが直っている。

**分けて判断できる**: 見送ると決めたのならクロームの大きさは残してよいが、
その場合でも `CLAUDE.md:41` と `claude_memo.html:162-163` の説明は
事実と違うので直す必要がある（`archives/` に見送りの記録は見当たらなかった）。

---

## 検討

### 2. `scrollPlaylistIntoView()` は `#playlist-items` に `position` が付くと壊れる

**場所**: `claude_memo.html:1519-1528`。

**何が問題か**: `item.offsetTop - box.offsetTop` は、`item` と `box` の
`offsetParent` が**同じ**であることに乗っている。実測（t1）で現状は

- `box.offsetParent` = `BODY`、`item.offsetParent` = `BODY`（一致）
- `box` の `position: static` / `border-top: 0` / `padding-top: 0`

なので計算は正しい。ただし `#playlist-items` に `position: relative` が付くと
`item.offsetParent` が `box` 自身に変わり、`box.offsetTop`（= BODY 起点）を
引いてしまうので値が壊れる。実際に `box.style.position = 'relative'` にして
17 枚送ると、**9 枚目以降で項目が枠の外へ出た**（t6。`relTop` が 414 → 644 と
`clientHeight` 441 を超えていく）。項目側に `relative` が付く分には壊れない
（`offsetParent` は変わらないため）。

**どうなると困るか**: `#playlist-items` は Tailwind クラスだけで組まれていて、
今回の差分でも `#viewport-stage { position: relative }` を「重ねる基準」として
足している。同じ感覚で一覧側に `relative` が付くと、直したはずのスクロールが
静かに壊れる（例外も出ない）。`getBoundingClientRect()` の差 + `scrollTop` で
書くか、`box` が static であることをコメントに残すか、どちらかの手当てを
入れるかは判断が要る。

### 3. 768px 未満で画面が低いと、フルスクリーン中の字幕が画面外に出て切られる

**場所**: `claude_memo.html:181-192`（`#viewport-stage.is-fullscreen > #subtitle-banner`）。

**何が問題か**: 字幕は `top: 100%` + `margin-top: 0.75rem` で枠の下に置くので、
下側の暗幕の帯（高さ `(H - W*9/16) / 2`）に 12 + 97.5 = 109.5px 以上が要る。
帯が足りないと画面の下に出て、`body.fs-lock` の `overflow: hidden` で
スクロールもできずに切られる。条件は `H < W * 9/16 + 219`。実測（t9）:

| ビューポート | 字幕のはみ出し |
|---|---|
| 390x844 / 390x600 / 390x480 / 360x640 | 無し |
| **767x600** | **25.2px** |
| **767x500** | **75.2px**（97.5px 中） |

**どうなると困るか**: 幅 767px 前後で高さが 650px を切ると字幕がほぼ見えない。
小さいタブレット、折りたたみ端末、PC で窓を 768px 未満に狭めた場合が当たる。
なお「横持ちで高さが足りない件」と同根なら、今回の対象外という整理でよい。

### 4. 768px 以上には暗幕も `fs-lock` も無いので、スマホを横にすると出口が消える

**場所**: `claude_memo.html:167`（`@media screen and (max-width: 767.98px)`）。

**何が問題か**: メディアクエリの切り替え自体は辻褄が合っている。390x844 で
フルスクリーンに入り 844x390 → 390x844 と往復した実測（t5）で、
字幕の `position`、`body` の `overflow`、`::before` の有無が毎回揃って
切り替わり、Esc 後もクラスは残らなかった。

問題は横のときの中身。844x390 では幅が 768 以上なので PC 扱いになり、

- 暗幕が無い → 帯（左右 75px）のタップは裏のページに当たる
  （実測: `#viewport-stage` ではなく `max-w-7xl` にヒット。抜けられない）
- `fs-lock` が効かない → ホイールで裏が動いた（`scrollY` 0 → 400）
- フルスクリーンのボタンは箱の裏なので押せない

**どうなると困るか**: 同じ端末なのに、縦では暗幕タップで抜けられて横では
抜けられない。物理キーボードが無ければ横向きだけ再読み込みしか出口が無い。
768px という**幅**の境界で「スマホかどうか」を決めている以上の帰結なので、
直すなら `(pointer: coarse)` を足すなど別の切り口が要る。縦に戻せば辻褄は
合うので、退行ではなく残った穴。

---

## 好みの範囲

### 5. `CLAUDE.md:45`「通常時の `margin: 1px`」は範囲が実物より狭い

`#subtitle-banner { margin: 1px }`（`claude_memo.html:156-158`）は無条件の
ルールで、PC の**フルスクリーン中にも効いている**。そこでも値は正しく、
1280x800 のフルスクリーンで字幕は `17, 647, 1246, 100` と HEAD に一致した
（t3 と同条件で確認）。「通常時の」と書くと 768px 未満の上書きと紛らわしい。

---

## 問題無しと判断したもの（重点項目への回答）

- **1. `scrollPlaylistIntoView()` の計算**: 上の指摘 2 の条件を除けば正しい。
  390x844 と 1280x800 で 17 枚を前送り・後戻りした実測（t1）で、
  **毎回その項目が枠内に収まり**（`visible: true`）、`window.scrollY` は
  0 のまま動かなかった。先頭は `scrollTop` 0、末尾は上限 333 で止まる。
  ページを 200 まで下げてから送った比較（t2）では、**HEAD は 200 → 432 まで
  動いたのに対し今回は 200 のまま**で、狙った不具合が消えている。
  `ArrowRight` を 30ms 間隔で連打しても（smooth スクロールの途中で
  再呼び出しされる状況）最終位置は正しく、一覧の項目を直接クリックして
  先頭へ戻す経路も正常。上下の判定は `scrollIntoView({block:'nearest'})` と
  同じ意味になっている
- **2. 通常時の配置**: 1280 / 1024 / 900 / 768px で、`#player-viewport`・
  `#subtitle-banner`・`#slide-canvas`・`#sidebar`・`#fullscreen-btn` の矩形と
  `documentElement.clientWidth`・`scrollHeight` が **4 幅すべてで HEAD と
  完全一致**（t3、スクロールバーを表示した状態）。`#viewport-stage` に
  レターボックスを移したことによる通常時の影響は無い。768px 未満の配置が
  変わるのは TODO-001 の目的そのもの
- **3. 暗幕のタップ判定**: 390x844 / 360x800 / 767x900 のフルスクリーンで
  （t4）、暗幕（上下の帯）のタップは `is-fullscreen` /`pseudo-fullscreen` /
  `fs-lock` の 3 つとアイコンを揃って解除した。スライド中央のタップは
  `#slide-canvas` の子に、字幕のタップは `#caption-text` に当たり、
  どちらもフルスクリーンのまま。PC（1280x800）では帯が `header` / `footer` に
  当たるので `e.target === stage` にならず、誤って閉じることも無い
  （PC で帯のクリックが裏に抜けるのは HEAD と同じ）。ハンドラは
  `setupEventListeners()` の中で 1 回だけ付き、中で `is-fullscreen` を
  見ているので、付け外しのずれは原理的に起きない
- **4. `fs-lock` の 768px 未満限定**: 上の指摘 4 のとおり、CSS の切り替え
  自体は回転に追従する（JS 側に幅を見る処理は無い）
- **5. `CLAUDE.md` の行番号**: `grep -n` で `const slideData` = 439、
  `let currentIndex` = 1098、`playlist-count` = 420。記述と一致。
  `CLAUDE.md:47-52`「レターボックスは `#viewport-stage.is-fullscreen` だけが
  持つ」も、`100vh` / `100vw` を使う箱が `claude_memo.html:120-124` の
  1 か所だけであることを `grep` で確認（他の `16 / 9` は
  `.video-viewport` と `#viewport-frame` の通常の縦横比）。
  `CLAUDE.md:53-57` の `fs-lock`・暗幕・タップ条件も実測どおり
- **インデント**（2 巡目の指摘 9）: `claude_memo.html:284-334` は
  stage 16 / frame 20 / `.video-viewport` 24 / 子 28、字幕は stage の子として
  20 と、4 空白ずつに揃った
- **コンソール**: 全条件で `pageerror` 0 件

## 範囲について

差分は `claude_memo.html`・`CLAUDE.md`・`TODO.md` の 3 ファイル。
`TODO.md` の変更は TODO-001 への追記と TODO-002 の書き換えで、指示の範囲内。
音声・スライドの中身には触れていない。指示に無い変更は見当たらない。
テストの無いリポジトリなのでテストの追加は求めない。新しいコメントは
いずれも「なぜ」を書いているが、`claude_memo.html:162-163` だけは
内容が事実と違う（指摘 1）。
