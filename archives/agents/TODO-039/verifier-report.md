# TODO-039 verifier 報告

## 実行した検証

### 1. `tools/measure-duration.py 6`

```
$ python3 tools/measure-duration.py 6
スライド 6: 原文 176 字 / 読み 171 字 / 実測 32.472s / 1.4 倍速 23.19s -> duration: 23
```

- 実測 32.472s、1.4 倍速で 23.19s → `duration` に入れるべき値は **23**
- 現在の `duration` は 19 のまま。**未更新**（要修正）
- ★180 字で切れる、の警告は出ていない（読み 171 字で `TTS_MAX_CHARS`=180 未満）
- 注釈のスタイル変更（枠付き・lime 色に変更）後に測り直したが、ナレーション文言は
  変わっていないため結果は変わらなかった（表示上の色・枠は音声合成に影響しない）

### 2. 表示確認（Playwright, `chromium.launch()` をローカル `http.server`（port 8791）に接続）

コーディネーターからの指示で注釈のスタイルが変更されたため、最新の
`claude_memo.html` を読み直してから撮り直した。`renderSlide(5)`（0 始まり、
スライド 6）を呼んでスクリーンショットを取得。

- **1280x720（PC、マウス想定）**: 注釈（枠付き・lime 色のボックス）は
  4 項目の表の下、フッターの上に収まっている。テキストの折り返しや
  下端でのはみ出しは無い。
  画像: `~/tmp/playwright-mcp/todo039b-slide6-1280x720.png`
- **844x390（横持ちスマホ想定）**: 実機のスマホは `pointer: coarse` なので、
  最初 `hasTouch`/`isMobile` を指定せずに撮ったところ `--vp-scale` の縮小が
  効かず、枠が画面下にはみ出す誤った表示になった。`hasTouch: true,
  isMobile: true` でタッチを模したところ、CSS の
  `@media (max-width: 767.98px), (pointer: coarse)` が効いて正しく縮小
  表示され、注釈まで含めて枠内に収まっていることを確認した。
  画像: `~/tmp/playwright-mcp/todo039b-slide6-844x390-touch.png`
  （タッチを付けない版: `~/tmp/playwright-mcp/todo039-slide6-844x390.png`
  → はみ出す。実機挙動とは異なるため参考にはしないこと）

いずれのサイズでも「本文が切れている」「注釈が下にはみ出している」は
見られなかった。

## 変更ファイルの確認

- 変更されたのは `claude_memo.html` のみ（対象範囲どおり）
- 差分はスライド 6 の `narration` 文言と、注釈 `<p>` タグの追加（後にスタイルを
  枠付き・lime 色・`clamp(1.0rem, 2.0cqw, 1.4rem)` に変更）の 2 箇所のみ。
  他のスライドやロジックへの変更は無い
- `git status` は `claude_memo.html` の modified と、`archives/agents/TODO-039/`
  の untracked のみ（指示の範囲内）

## 確かめられなかったこと・判断が要る点

- **`duration` の値がまだ 19 のまま。23 に更新されていない。** これは
  コードの修正判断なので、直さず報告のみとする
- 844x390 の検証は Playwright の `hasTouch`/`isMobile` で `pointer: coarse`
  を模した。実機のブラウザでの見え方そのものではないので、その点は
  近似であることを明記しておく
- スタイル変更（lime 色・枠）が意図した見た目かどうかは、色の好みの話であり
  検証の対象外と判断した（表示が枠内に収まるかだけを確認した）
