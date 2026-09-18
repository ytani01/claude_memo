# TODO-004. 横持ちのスマホでフルスクリーンの高さを画面に合わせる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 3,726 | 48,327 | 80% |
| verifier | Sonnet 5 | medium | 6,872 | 31,161 | 20% |
| 合計 |  |  | 10,598 | 79,488 | 概算 $0.9 |

- verifier は定義（`~/.claude/agents/verifier.md`）のまま Sonnet 5 / effort medium。
  確かめる中身が CSS 1 か所とレターボックスの計算だけなので上書きしていない
- 集計の終点は実装のコミット（`1537607`）。そのあとに行った headless chromium での
  実測と、この決着の作業は入っていない

## きっかけ

横持ちのスマホで擬似フルスクリーンにすると、16:9 の箱の高さが画面に合わず、
下へはみ出していた。

横持ち（844x390 など）は幅が 768 以上なので、768px 未満の縮小の経路ではなく
PC 側の経路に入る。そこでは `#viewport-stage.is-fullscreen` が
`height: 100vh` と `max-width: calc(100vh * (16 / 9))` で箱を決めていた。
スマホの `100vh` は URL バーを含んだ高さなので、実際に見えている高さより
大きくなる。

## やったこと

`claude_memo.html` の `#viewport-stage.is-fullscreen` に、`dvh`（表示中の
ブラウザ UI を除いた高さ）の行を足した。変えたのはこの 1 か所だけ。

```css
height: 100vh;
height: 100dvh;
max-width: calc(100vh * (16 / 9));
max-width: calc(100dvh * (16 / 9));
```

`dvh` 非対応のブラウザは 2 行目を無効な宣言として捨て、1 行目の `vh` が
そのまま残る。`max-height: calc(100vw * (9 / 16))` は幅基準なので触っていない。

## 確かめたこと

- **実機（横持ちのスマホ）** — 利用者が目視。はみ出さず、暗幕のタップでも抜けられる
- **headless chromium 152 での実測** — `#fullscreen-btn` をクリックした状態で
  `#viewport-stage` の矩形を測った。844x390 の窓で 538.7x303、
  1280x800 の窓で 1267.5x713。どちらも比は 16:9 で、下端が
  `innerHeight` と一致（はみ出し 0）。`CSS.supports('height','100dvh')` は true
- **verifier による静的な確認** — 差分が TODO の範囲どおりであること、
  `vh` → `dvh` の上書き順が正しいこと、`#viewport-stage.is-fullscreen` を
  基準にしている他の規則（`.video-viewport.pseudo-fullscreen`、
  `#subtitle-banner`、768px 未満の `@media`、暗幕の `::before`）が
  すべて相対値で組まれていて影響を受けないこと。ファイル内に他の `vh` の
  使用が残っていないこと。報告は
  `archives/agents/TODO-004/verifier-report.md`

縦持ちのスマホと PC では、高さが `max-height`（幅基準）で決まるため
見た目は変わらない。暗幕の帯は `dvh < vh` のとき広がる方向にしか動かないので、
TODO-003 の「暗幕のタップで抜ける」出口は狭くならない。

## 分担の振り返り

- verifier が見つけたのは「周辺の規則がすべて相対値で組まれていて影響を
  受けない」ことの裏取りと、他に `vh` が残っていないことの確認。
  差分そのものの誤りは見つかっていない（1 行の追加なので当然ではある）。
  一方で「実機でないと確かめられない」と正しく線を引いて返してきたのは
  有用だった
- 見込み（main + verifier）と食い違いは無し。実装まで分けなかったのも、
  変更が CSS 1 か所で妥当だった
- **次に同じ規模（1 ファイルの CSS を数行）をやるなら、verifier に
  「手計算」ではなく最初から headless chromium での実測を指示する。**
  今回 verifier は「環境が無い」として手計算で済ませたが、実際には
  `chromium --headless --dump-dom` で測れた。依頼文に測り方まで書けば、
  main が後から測り直した分（main の料金 80% の一部）を減らせる
