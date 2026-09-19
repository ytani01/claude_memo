# TODO-051 slides/usage.js 実装報告（担当: implementer-usage）

## 作ったもの

`slides/usage.js` を新規作成。`docs/Usage.md` の要点を 11 枚にまとめた。
`player.html?deck=usage` で再生される。`slides/claude-memo.js` の形式
（`deckConfig` / `slideData`、Tailwind + `cqw` + `clamp()`）に倣った。

## スライド一覧

| # | title | 載せた内容 |
|---|-------|-----------|
| 1 | player.html で別のスライドを作る | タイトル |
| 2 | 基本方針 | player.html は触らない／slides/<名前>.js を1つ足すだけ |
| 3 | 手順1 ファイルを作る | slides/<名前>.js の場所、名前に使える文字 |
| 4 | 手順2と3 書いて開く | deckConfig/slideData を書く、`?deck=` で開く、省略時は claude-memo.js |
| 5 | slideData の中身 | title/duration/narration/render() の4キー |
| 6 | 番号と枚数は自動 | スライド番号・総枚数・総時間は自動計算される |
| 7 | render() の書き方 | 960x540・16:9、cqw と clamp() で書く、md: を使わない |
| 8 | 近い見た目をコピーする | claude-memo.js からコピーが早い、細部は Usage.md へ誘導 |
| 9 | duration の測り方 | measure-duration.py --text の使い方 |
| 10 | まとめて書き戻す | --all --write の挙動、変わった枚だけ表示、git checkout で戻せる |
| 11 | まとめ | 3行まとめ |

## 落とした内容（細部は docs/Usage.md 側に任せた）

- `TTS_MAX_CHARS` で1文が切れる注意、置換表と RULES を一緒に直す注意
- `duration` の書き戻しツールが `slides/claude-memo.js` の書き方（duration の
  直後に narration が続く並び）を前提にしている、という実装都合の話
- 公開について（public_html 配下でそのまま公開、ビルド不要）
- 最小の例（sample.js）の具体コード

これらは「スライドを作る人」の初回導入には必須ではなく、詳しいドキュメント
（docs/Usage.md）に任せる方が要点が絞れると判断した。

## duration 書き戻し正規表現への配慮

`tools/measure-duration.py` の `DURATION_RE` / `narrations()` は
`duration: N,\n narration: '...',\n` という**実際の改行パターン**にだけ
反応する。スライド内でコード例やキー名（`title`、`duration`、`narration`、
`render()` など）を文言として見せてはいるが、実際の JS の
`duration: N,` の直後に改行して `narration: '` が続く並びは、本物の
`slideData` の11要素以外には作っていない。検証スクリプトで
`DURATION_RE` のマッチ数と `narrations()` のマッチ数がどちらも 11
（スライド数と一致）であることを確認済み。

## 検証

1. `node --check slides/usage.js` → 構文エラーなし（終了コード 0）
2. `DURATION_RE` / `narrations()` の正規表現マッチ数を Python で確認 →
   どちらも 11 件（誤爆なし）。各 narration の文字数も出力し、すべて
   180 字未満であることを確認（最大 86 字）
3. `tools/measure-duration.py --deck usage --all`（`--write` なし）を実行 →
   11 枚すべてナレーションを拾い、`duration: N` の下書き値を出力できた。
   エラーなし

## 判断が要る点・懸念

- 各スライドの `duration` は仮値（ナレーション文字数 ÷ 7 の四捨五入）を
  入れてある。実測値は上記コマンドの `--write` 付き実行で main が
  書き戻す想定（指示どおり `--write` は付けていない）
- 範囲外だが気づいたこと: 特になし
