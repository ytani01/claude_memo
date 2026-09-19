# TODO-045. リポジトリの入口として `README.md` を作る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 3,587 | 11,160 | 66% |
| verifier | Sonnet 5 | medium | 5,188 | 38,674 | 34% |
| 合計 |  |  | 8,775 | 49,834 | 概算 $0.7 |

- verifier は定義（`~/.claude/agents/verifier.md`）のまま sonnet / effort
  medium。上書きしていない

## きっかけ

TODO-042 で `docs/Usage.md`（スライドを作る人向け）、TODO-043・TODO-044 で
`docs/Developer.md`（`player.html` を直す人向け）が揃ったが、リポジトリを
開いた人が最初に読むものが無かった。総括的な説明と、2 本の docs への
振り分けを置く。

## 決めたこと

利用者に聞いて、次のように決めた。

- 書くのは 4 つ ― 何のリポジトリか / 各ディレクトリと主なファイルの説明 /
  手元で動かす手順 / 読む人ごとの docs への振り分け
- 含めない ― プレイヤーの機能一覧（ボタンやキー操作の説明）、公開 URL、
  `TODO.md` 運用への言及（構成表の 1 行としての説明は可）
- 言語は日本語のみ

docs 2 本と同じことを書き直さず、リンクで送る方針にした。

## やったこと

`README.md` を新規に作った（45 行）。

- 冒頭 3 段落 ― 何をするものか、`player.html` と `slides-<名前>.js` に
  分かれていてプレイヤーを触らずスライドだけ足せること、ビルドも依存関係の
  インストールも無いこと（CDN と読み上げでネット接続は要る）
- ファイル構成の表 ― `player.html`・`slides-<名前>.js`・
  `slides-claude-memo.js`・`claude_memo.html`・`docs/`・
  `tools/measure-duration.py`・`archives/`・`TODO.md`・`CLAUDE.md`
- 手元で動かす ― `python3 -m http.server 8000` と開く URL、`?deck=` 省略時の
  既定、`file://` は試していない旨
- 説明 ― `docs/Usage.md` と `docs/Developer.md` へのリンクと、どちらを読む人か

冒頭の「字幕・再生速度・フルスクリーンを切り替えられる」は、何ができる
ものかを示す 1 文として残した。除外した「機能一覧」は操作の並べ立てを
指すと解釈した。

## 確かめたこと

verifier が確認した（報告は
[archives/agents/TODO-045/verifier-report.md](../agents/TODO-045/verifier-report.md)）。

- ファイル構成の表を `git ls-files` と突き合わせ、実在と一致・漏れ無し
- 空きポート 8931 で `python3 -m http.server` を実際に起動し、
  `player.html`・`slides-claude-memo.js`・`player.html?deck=claude-memo` が
  いずれも 200。確認後にサーバを停止し、プロセスが残っていないことも確認
- `docs/Usage.md`・`docs/Developer.md` への相対リンクが実在
- 「`?deck=` を省くと `slides-claude-memo.js` を読む」を `player.html` の
  デッキ読み込み部分で裏取り
- 字幕・再生速度・フルスクリーンの各要素、CDN 依存、ビルド無し、実例 17 枚、
  `claude_memo.html` のリダイレクト先が、いずれもコードと一致
- 含めないと決めたもの（公開 URL・`TODO.md` 運用への言及）が入っていない

## 分担の振り返り

- **verifier が見つけたもの**: 事実の誤りはゼロ。代わりに、冒頭の
  「字幕・再生速度・フルスクリーンを切り替えられる」が除外した「機能一覧」に
  当たるか判断できないと報告してきた。直さず報告に留めたのは指示どおり。
  `.gitignore` を表に載せないことも「判断」と明示していた
- **見込みとの食い違い**: 無し。main が書いて verifier が確認する構成で
  そのまま終わった
- **次に同じ規模（既存の文書からリンクで送るだけの新規 1 ファイル）を
  やるなら**: 同じく main + verifier で組む。verifier の料金は全体の 34% で、
  `http.server` を実際に立てる再現を含めてこの額なら削らない。ただし
  **確認項目に「境界線上の判断は報告だけさせる」と書いておく**と、今回のような
  差し戻しの往復を減らせる。書式だけを見る項目なら main のみでよいが、
  今回は動かす手順が入っていたので分けて正解
