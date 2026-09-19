# TODO-046. スライドのデータを `slides/` に置く

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + reviewer |
| 実施 | Opus 5 / effort high | verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 18,550 | 54,466 | 66% |
| reviewer | Opus 5 | high | 13,851 | 55,797 | 26% |
| verifier | Sonnet 5 | medium | 6,622 | 38,047 | 8% |
| 合計 |  |  | 39,023 | 148,310 | 概算 $3.5 |

- reviewer は定義のモデルが sonnet。直し漏れの判断が要ると見て Opus 5 に
  上書きした
- verifier は定義のまま（`model: sonnet` / `effort: medium`）
- **この集計には TODO-047 の作業も混じっている。** 項目を立てるコミットが
  046 と 047 の 2 つを 1 回でまとめており、終点も同じセッションの中にある

## きっかけ

デッキが増えるとリポジトリ直下に `slides-*.js` が並んで散らかる。
スライドのデータを `slides/` にまとめることにした。

ファイル名は `slides/<名前>.js` にした。ディレクトリ名で種類が分かるので、
`slides-` の接頭辞は重複になる。URL は `player.html?deck=claude-memo` の
ままで変わらない。

## やったこと

- `slides-claude-memo.js` を `git mv` で `slides/claude-memo.js` へ移した
- `player.html` の読み込み先を `slides/${deckName}.js` にし、
  デッキが読めなかったときのメッセージも `slides/<名前>.js` に直した
- `tools/measure-duration.py` の `SRC` を `slides/claude-memo.js` に向けた
- `README.md`・`CLAUDE.md`・`docs/Usage.md`・`docs/Developer.md` の記述を
  追従させた。`docs/Developer.md` の「置き場所は選ばない」は、
  `slides-*.js` を並べて置く書き方だったので、`slides/` を並べて置く形に
  書き直した
- `docs/Usage.md` の手順 1 は、置き場所の説明を括弧に入れたら括弧が 2 つ
  続いて読みにくくなったので、`player.html` と同じディレクトリの `slides/` に
  `<名前>.js` を作る、という 1 文に直した（reviewer の指摘）

## 確かめたこと

verifier が `python3 -m http.server` で配って実測した
（[verifier-report.md](../agents/TODO-046/verifier-report.md)）。

- `player.html?deck=claude-memo` で 1 枚目が表示され、`slides/claude-memo.js`
  が 200。コンソールエラーは無し（Tailwind CDN の既存の warning のみ）
- `player.html?deck=nosuch` で、白画面ではなく枠の中に
  「スライドのデータ slides/nosuch.js を読み込めませんでした。」が出る
- `tools/measure-duration.py --text 'テスト'` と
  `tools/measure-duration.py 1 1` がどちらも終了コード 0
- `archives/` を除いて `slides-` の残りが無い

reviewer は要修正 0 件で、`deckName` のサニタイズ
（`.replace(/[^\w-]/g, '')`）にパストラバーサルの余地が無いことを node と
HTTP で実測した（[reviewer-report.md](../agents/TODO-046/reviewer-report.md)）。
`\w` に `u` フラグが無く ASCII の `[A-Za-z0-9_]` なので、`.` も `/` も
落ちる。`?deck=../../etc/passwd` は `slides/etcpasswd.js` になる。

## 分担の振り返り

- **verifier は問題を 1 件も見つけなかった。** ただし Playwright での実機
  確認は、実装した本人だと「パスを直したのだから動くはず」で済ませる類い
  なので、見つからなかったことに意味がある
- **reviewer は 2 件挙げた。** どちらも文書の細部（`claude_memo.html` の
  コメントに残る旧名、`docs/Usage.md` 手順 1 の括弧の重なり）で、
  要修正は無し。サニタイズの実測表は、パスにディレクトリが 1 段増えた
  今回の変更で確かめる価値があった
- **見込みとは食い違わなかった**（verifier + reviewer のまま）。ただし
  main のモデルは過剰だった。実際にやったのは 6 ファイルの機械的な置換と
  担当への依頼で、判断らしい判断は「`slides/<名前>.js` か
  `slides/slides-<名前>.js` か」の 1 点。それも利用者に聞いたので main 側
  では消えている
- **次に同じ規模（パス文字列の置換と文書の追従）なら、main は effort
  medium、reviewer は定義のまま Sonnet 5 で組む。** reviewer を Opus に
  上げた分が料金の 26% を占めたが、挙げた 2 件はどちらも文書の細部で、
  Sonnet でも拾えた見込みが高い。verifier は残す
- この項目の途中で、**モデルと effort は「多分大丈夫」の水準まで低めに
  設定し、問題が出てから上げる**方針が決まった。以後、担当のモデルは
  定義のまま使い、Agent ツールでの上書きは実際に失敗した実績があるときだけ
  にする
