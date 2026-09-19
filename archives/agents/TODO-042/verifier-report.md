# TODO-042 検証報告（verifier）

対象: `docs/Usage.md`（新規作成）。`player.html`・`tools/measure-duration.py`・
`slides-claude-memo.js` と突き合わせた。コードも文書も変更していない。

## 1. 手順の再現（最小の例）

`docs/Usage.md` の「最小の例」をそのまま `slides-sample.js` としてリポジトリ
直下に作成し、確認後に `\rm slides-sample.js` で削除済み（削除を確認済み）。

- `node --check slides-sample.js` → 構文エラー無し
- `player.html` が参照するキー（`slide.id` / `slide.title` / `slide.duration`
  / `slide.narration` / `slide.render()`、`deckConfig.title` /
  `deckConfig.heading`）を grep で洗い出し、例のオブジェクトと突き合わせた。
  例には全キーが揃っており、不足は無い。
- ブラウザは使っていない（実際に `player.html?deck=sample` を開いての
  目視確認はしていない）。静的な突き合わせのみ。

## 2. コマンド例の再現

`curl` と `ffprobe` は両方入っていたので実行できた。

```
$ python3 tools/measure-duration.py --text 'これはサンプルのスライドです。'
下書き: 原文 15 字 / 読み 15 字 / 実測 2.784s / 1.4 倍速 1.99s -> duration: 2
exit:0
```

出力の並び（`原文 N 字 / 読み N 字 / 実測 Xs / 1.4 倍速 Ys -> duration: Z`）は
文書の例と構造が一致する。

**軽微な食い違い**: 文書の例は
`原文 12 字 / 読み 12 字 / 実測 4.2s / 1.4 倍速 3.0s -> duration: 3` と
小数第1位で書いているが、実際の `main()` は `実測` を `:.3f`（小数第3位）、
`1.4 倍速` を `:.2f`（小数第2位）で出す。実行結果は `実測 2.784s / 1.4 倍速
1.99s` のように桁数が違う。数値自体は例示なので誤りとは言えないが、桁数の
書き方は実際の出力と異なる。実害は無い（読めば分かる）が、事実と厳密には
食い違う。

## 3. 事実の照合

- `<名前>` に使える文字: `player.html` 466 行 `replace(/[^\w-]/g, '')`。
  `\w` は英数字とアンダースコアなので、文書の「英数字・`_`・`-`」の記述と一致。
- `?deck=` 省略時の既定: 465-466 行で `|| 'claude-memo'` になっており、
  文書の記述と一致。
- 読み込み失敗時のメッセージ: 477-479 行の文字列は
  `` `スライドのデータ slides-${deckName}.js を読み込めませんでした。` `` で、
  文書の引用と完全に一致（1 文字も違わない）。
- 枚数・総時間の自動算出: `initPlaylist()`（1003 行〜）が
  `slideData.length` から枚数を、`totalDurationSeconds`（554, 566 行、各
  `slide.duration` の合計）から総時間を出しており、文書の「自動で出る」と
  一致。
- 960x540 / container query: CSS に `container-type: inline-size`
  （51 行）、`width: 960px` `height: 540px`（215-216, 229-230 行）があり、
  文書の記述と一致。
- `duration` は「Online TTS を 1.4 倍速で再生した実測秒数」: `player.html`
  の `BASE_SPEED_MULTIPLIER` の使われ方、および
  `tools/measure-duration.py` 冒頭の docstring
  「`slideData` の `duration` には『Online TTS の音声を 1.4 倍速で再生した
  実測秒数』が入っている（TODO-018）」と一致。
- `--text` はデッキに依らず使え、番号指定は `slides-claude-memo.js` 固定:
  `measure-duration.py` 28 行 `SRC = ... / 'slides-claude-memo.js'` で
  ハードコードされており、`--text` はこの `SRC` を使わない
  （`jobs.append(('下書き', args.text))` のみ）ので、文書の記述と一致。
- Online TTS の 180 文字制限と `★180 字で切れる`: `TTS_MAX_CHARS = 180`
  （31 行）、113 行
  `cut = ' ★180 字で切れる' if len(spoken) > TTS_MAX_CHARS else ''`
  で文言も一致。
- `prepareSpeechText()` の置換表と `measure-duration.py` の `RULES` が
  写しである件: `player.html` 601-625 行の `.replace(...)` の並びと
  `measure-duration.py` 34-56 行の `RULES` を並べて突き合わせ、対象文字列・
  置換後の文字列・順序とも一致していることを確認した（実際に一致している。
  現時点でずれは無い）。
- `md:` ブレークポイントを枠内で使わない件、幅 768px 未満とタッチ画面で
  `transform: scale()` に切り替わる件: `setupViewportScale()` の
  `matchMedia('screen and (max-width: 767.98px), screen and (pointer:
  coarse)')`（1300-1301 行）と一致。

## 確かめられなかったこと

- 実際にブラウザで `player.html?deck=sample` を開いての目視確認はしていない
  （headless ブラウザ等が用意されていなかったため、静的な突き合わせのみ）。
  構文チェックとキーの突き合わせでは不足は見つからなかったが、実際の描画
  （Tailwind クラスの当たり方、`render()` の返す HTML の見た目）までは
  保証できない。
- `duration` の実測値そのものの妥当性（TTS の音質・速度が変わっていないか
  など）は確認範囲外。

## 検証コマンドの終了コード

- `node --check slides-sample.js` → 0
- `python3 tools/measure-duration.py --text '...'` → 0
