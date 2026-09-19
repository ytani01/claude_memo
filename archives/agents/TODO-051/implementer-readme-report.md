# TODO-051 slides/readme.js 実装報告

## 作ったもの

`slides/readme.js`（新規）。`player.html?deck=readme` で再生される。
`slides/claude-memo.js` を手本に、`deckConfig` と `slideData`（10 枚）を定義。

## スライド一覧

| # | title | 内容 |
|---|-------|------|
| 1 | yt_slide | タイトル。「HTML 1 枚でナレーション付きのプレゼンが動き出す」を最初に出す |
| 2 | できること | 読み上げ・字幕、自動再生、再生速度、フルスクリーン、スマホ対応を並べる |
| 3 | すぐ試す | `python3 -m http.server` と `player.html?deck=<名前>` |
| 4 | 自分のスライドを作る | 「player.html は触らない、slides/ に 1 つ足すだけ」の見出しカード |
| 5 | deckConfig と slideData | 最小のコード例（コードブロックは HTML として静的に書き、`duration:`→`narration:` の並びを避けるため 1 行にまとめた） |
| 6 | 1枚のスライドの要素 | `title` / `duration` / `narration` / `render()` の 4 マス |
| 7 | render() の書き方 | `cqw`/`clamp()`、`md:` を使わない、`claude-memo.js` をコピーする |
| 8 | duration の測り方 | `tools/measure-duration.py --all --write` の実行例 |
| 9 | 入っているスライド | README.md の表と同じ内容（readme/usage/developer/claude-memo） |
| 10 | まとめ | HTML 1 枚・slides/ に 1 つ足すだけ・ビルド不要、の 3 点 |

`duration` は指示どおり「ナレーション文字数 ÷ 7 の四捨五入」の仮値で入れた。

## 検証

1. `node --check slides/readme.js` → 構文エラー無し（`node` は使用可能だった）
2. `tools/measure-duration.py --deck readme --all` → 10 枚すべてナレーションを
   拾えた（1 枚も落ちず）。実測結果（`--write` は付けていないので未反映）:

   ```
   スライド 1: duration: 12   スライド 6: duration: 9
   スライド 2: duration: 11   スライド 7: duration: 8
   スライド 3: duration: 11   スライド 8: duration: 8
   スライド 4: duration: 8    スライド 9: duration: 12
   スライド 5: duration: 10   スライド 10: duration: 10
   ```

   実測値への書き戻しは指示どおり main が行う想定なので、ここでは仮値のまま
   残している。

## 迷った点・気づいたこと

- Slide 5 のコード例は `render()` の中に「実際のコード例」を書く場面
  だったため、`measure-duration.py` の正規表現（`duration: \d+,\n *narration: '`）
  を誤爆させないよう、サンプルコードの `duration` と `render()` を 1 行に
  まとめて改行を挟まない書き方にした。文法的な JS のコード例としては
  やや不自然（`render() { ... }` を 1 行に圧縮）だが、指示の制約を優先した
- README.md には他に「入っているスライド」の表に `usage`/`developer` の説明
  があるが、それらのデッキ自体はまだ存在しない（TODO-051 の別担当がこの後
  作る想定）。9 枚目はその前提で、既存の README.md の記述をそのまま使った
- 8〜12 枚の範囲の下限寄り（10 枚）にした。README.md の「入っているスライド」
  「ファイル構成」の 2 つの表のうち、「ファイル構成」（`player.html` /
  `docs/` 等の一覧）は今回のスライドには含めていない（プレゼンを作りたい人
  への訴求としては優先度が低いと判断したが、範囲外の判断なので必要なら
  差し戻してほしい）
