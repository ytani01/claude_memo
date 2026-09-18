# TODO-036. ステータスラインの実例の区切りの段差を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier |
| 実施 | Opus 5 / effort high | verifier のみ（実装は main） |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 5,012 | 47,582 | 75% |
| verifier | Sonnet 5 | medium | 8,525 | 41,067 | 25% |
| 合計 |  |  | 13,537 | 88,649 | 概算 $1.3 |

- 変更が 6 行の属性だけと分かったので、implementer は立てず main が直した。
  確認は定義どおり verifier（`~/.claude/agents/verifier.md`、`model: sonnet` /
  `effort: medium`）に分けた
- 挙動（分岐や条件式）は変わらず見た目だけなので、reviewer は立てていない

## きっかけ

スライド 13（ccstatusline の実例）の powerline 風の区切りの三角が、
前後の帯（`<span>`）より短く、上下に段差ができていた。三角の先も潰れていた。

原因は区切りの SVG に `h-[1.2cqw]` の固定高さが付いていたこと。帯の高さは
文字サイズと `py-[0.15cqw]` で決まるので、固定値とは一致しない。さらに
SVG の既定の `preserveAspectRatio`（`xMidYMid meet`）では、viewBox
（8x16）の比率を保ったまま収まるように縮むため、先が潰れて見えていた。

## やったこと

`claude_memo.html` の 953・960・962・969・971・978 行目の 6 個の SVG で、

- `h-[1.2cqw]` を `self-stretch` に替えた。親は `inline-flex items-center`
  なので、`align-self: stretch` にすると帯と同じ高さになる
- `preserveAspectRatio="none"` を足した。幅 `w-[0.5cqw]`・高さ帯いっぱいの
  枠に三角をそのまま引き伸ばす

色（`fill-` と `bg-` の組）・文字・並びは触っていない。

## 確かめたこと

verifier が playwright（headless chromium、`file://`）で実測した。
報告は `archives/agents/TODO-036/verifier-report.md`。

- 6 個の SVG と、その直前・直後の `<span>` の `getBoundingClientRect()` の
  height / top / bottom が、PC 1280x800・横持ちスマホ 844x390 のどちらでも
  小数点以下まで一致（PC: 高さ 22.7397px、スマホ: 20.1841px）。段差 0px
- スクリーンショット（`deviceScaleFactor: 3` で帯を拡大）で、三角の先端が
  潰れていないこと、色・文字・並びが変わっていないことを確認
- `self-stretch` は 6 箇所のみ。他のスライドへの影響は無い

## 分担の振り返り

- verifier は「段差が消えたか」を目視ではなく `getBoundingClientRect()` の
  数値で出した。依頼文に「数値で報告する（目視だけで済ませない）」と
  測る画面サイズ（1280x800 / 844x390）を先に書いたのが効いた
- 見込みは implementer + verifier だったが、実際の変更は属性 2 つの
  置き換えで、該当箇所を読んだ時点で diff が確定していた。実装を分けると
  依頼文を書く分だけ高くつくので main が直した
- 次に同じ規模（1 ファイル・数行・見た目だけ）なら、同じく main が実装し、
  確認だけ Sonnet の verifier に分けるのでよい。依頼文には測る画面サイズと
  「数値で報告する」を必ず入れる
