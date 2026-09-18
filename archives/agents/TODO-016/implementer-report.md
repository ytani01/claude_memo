# implementer の報告（TODO-016）

対象は `claude_memo.html` のみ。1939 行 → 1898 行（32 挿入 / 73 削除）。

## 変更点

依頼の 1〜10 はすべて入れた。行番号は変更後のもの。

1. **`colors.brand` を削除**（旧 L22-31）。`tailwind.config` の `extend` は
   `fontFamily` だけになった（L21-26）
2. **`fontFamily.heading` を削除**（旧 L34）。あわせて Google Fonts の URL から
   `family=Urbanist:wght@600;800&` を外した（L14）。外した URL は HTTP 200 を返す
3. **`.video-viewport` の `width: 100%` / `max-width: 100%` を削除**（旧 L63-64）
4. **`#viewport-frame { width: 100% }` をルールごと削除**（旧 L183-185）。
   残ったコメントは、説明の中身を @media 側へ移した（L178-179 の「外枠は
   マウスの PC では素通し」、L198-201 の「PC では overflow を触らない」）
5. **同条件の `@media` 2 ブロックを 1 つに統合**（L184-269）。暗幕と `fs-lock` の
   コメントは統合後のブロックの中に残した（L245-251）。
   これに合わせて `setupViewportScale()` の上のコメントを
   「@media 2 か所」→「@media」に直した（L1854-1855）
6. **`speechActive` を宣言・代入とも削除**（旧 L1157, 1301, 1306, 1393, 1407）。
   読み出しは元から 0 箇所
7. **`btn.id = playlist-item-${idx}` を削除**（旧 L1604）。参照は 0 箇所
8. **`initPlaylist()` 冒頭の `innerHTML = ''` と `playlistItems.length = 0` を削除**
   （旧 L1596-1597）。呼び出しは `startApp()` からの 1 回だけ
9. **`slideStartTimes` を `map()` に変更**（L1172-1177）。値は変更前と同じ
10. 3 ハンドラを短縮:
    - 字幕トグル（L1636-1643）: `classList.toggle(cls, 条件)` に統一
    - 音声エンジン切替（L1646-1651）: 三項演算子に統一
    - 速度の巡回（L1676-1678）: `% speedOptions.length`。`indexOf` が -1 のときも
      `(-1 + 1) % n === 0` で先頭に戻り、元の `nextIdx < 0` の分岐と同じ

「手を付けないもの」には触れていない。

## 検証結果

すべて成功。

| 検証 | 内容 | 結果 |
| --- | --- | --- |
| `node --check` | `<script>` 2 ブロックを取り出して構文検査 | 成功（終了コード 0） |
| CSS の括弧 | `<style>` 内の `{` と `}` の数 | 38 / 38 で一致 |
| `grep` | `brand-`, `font-heading`, `Urbanist`, `speechActive`, `playlist-item-` | 一致 0 件（終了コード 1） |
| `@media` | CSS 内 1 か所、コメントでの言及 1 か所 | 統合できている |
| `curl` | 変更後の Google Fonts URL | HTTP 200 |

### 3, 4（幅の指定を消した件）のレイアウト実測

`chromium --headless=new --dump-dom` で、変更前（`git show HEAD:` の版）と
変更後に同じ計測スクリプトを差し込み、`getBoundingClientRect()` と
`getComputedStyle()` を比べた。計測対象は `#viewport-stage` /
`#viewport-frame` / `#player-viewport` / `#subtitle-banner` / `#slide-canvas`、
状態は「通常」「字幕を出した状態」「擬似フルスクリーン」の 3 つ、
ウィンドウは 1280x900 / 768x1024 / 390x844 の 3 つ。

- **矩形（x, y, width, height）は全 45 行が完全に一致**した
- 差は `#player-viewport` の `max-width` の計算値が `100%` → `none` に
  なった 4 行だけで、使用値の幅（`918px` / `714px`）は変わらない
- 390x844 では出力が完全一致（縮小経路では `#player-viewport` に
  `max-width: none` が元から掛かっているため）

根拠: どちらもブロックレベルの要素で、`box-sizing: border-box`（Tailwind の
preflight）なので `width: auto` の使用値は `width: 100%` と同じ。
`margin-inline: auto` と JS が入れる `max-width` を使う縮小経路でも、
`width: auto` のまま max-width で絞られて中央に置かれる（上の 390x844 の
実測で確認）。

### 6〜10（JS）の動作実測

同じく headless Chromium で、変更前後の版に対して
字幕トグル 2 回、音声エンジン切替 2 回、速度ボタン 9 回を順に押し、
各段階で `#toggle-caption-btn` / `#caption-icon` / `#subtitle-banner` の
class、`#speech-status-indicator` の文言と class、`#speed-btn` の表示、
`#playlist-items` の子要素数と先頭・末尾の innerHTML、
`#total-slides` / `#total-time-display`、`slideStartTimes` を記録した。
**68 行の出力が変更前後で完全に一致**（`diff` が空）。
速度は 1.0x → 1.25 → 1.5 → 1.75 → 2.0 → 0.75 → 0.9 → 1.0 と元どおり巡回する。
プレイリストは 17 件、`slideStartTimes` は
`[0,12,25,35,49,61,73,85,99,113,125,139,153,164,175,187,199]` で一致。

## 残る懸念

- 実測は headless Chromium のみ。`pointer: coarse` の実機（スマホ・タブレット）
  では試していない。ただし 390x844 では縮小経路（`#player-viewport` が
  `position: absolute; width: 960px`）に入っていることを確認済みで、
  この項目で消した宣言はその経路では元から上書きされている
- 5 の統合で 2 つのブロックのコメントが隣り合った。読みにくければ
  文面の整理は `wording` の担当で（今回は内容を変えず、実態に合う範囲だけ直した）
- 範囲外で気づいた点: `#subtitle-banner` は初期状態で `hidden` だが、
  `#caption-icon` には `text-slate-400` が最初から付いていない。
  1 回目のトグルで消そうとする class が無く、2 回目で付く。
  見た目は元から同じ（親の `text-slate-400` を継承）なので触っていない
