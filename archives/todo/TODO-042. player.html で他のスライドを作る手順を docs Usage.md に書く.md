# TODO-042. `player.html` で他のスライドを作る手順を `docs/Usage.md` に書く

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 7,420 | 57,807 | 81% |
| verifier | Sonnet 5 | medium | 5,600 | 34,387 | 19% |
| 合計 |  |  | 13,020 | 92,194 | 概算 $1.1 |

- verifier は定義（`~/.claude/agents/verifier.md`）のモデルが sonnet、
  `effort: medium`。文書の再現確認で判断が要らないので上書きしなかった

## きっかけ

TODO-041 で `player.html`（再生エンジン）と `slides-claude-memo.js`
（スライドのデータ）を分け、`?deck=<名前>` で別のデータを読めるようにした。
仕組みはできたが、**新しいデッキの作り方がどこにも書いていない**。
`CLAUDE.md` は Claude 向けの注意書きなので、人が手順として読めるものが要る。

範囲は利用者と相談して**新しいスライドの作り方に絞った**。再生ロジックや
TTS の 2 系統、フルスクリーンの縮小経路といったプレイヤー側の解説は
`CLAUDE.md` にあるので書かない。

## やったこと

`docs/Usage.md` を新規に書いた（`docs/` も新設）。中身は次の順。

- 手順 3 行（ファイルを作る → `deckConfig` と `slideData` を書く →
  `player.html?deck=<名前>` を開く）
- `deckConfig` と `slideData` の形。キーごとの表（`id`・`title`・
  `duration`・`narration`・`render()`）
- `render()` の書き方。960x540 の枠と container query、`cqw` と `clamp()`、
  枠の中で `md:` を使わない理由
- `narration` と `duration`。`tools/measure-duration.py --text` での測り方、
  180 文字で切れる件、`prepareSpeechText()` の置換表と `RULES` が写しである件
- 公開（置くだけ）と、旧 URL 用のリダイレクト HTML
- コピーして動く最小の例

利用者向けの文書なので、TODO 番号での参照は入れていない。

## 確かめたこと

verifier（Sonnet 5 / effort medium）に再現と事実の照合を任せた。報告は
`archives/agents/TODO-042/verifier-report.md`。

- 最小の例を `slides-sample.js` として実際に置き、`node --check` が通ること、
  `player.html` が参照するキーが全部揃っていることを確認（確認後に削除）
- `tools/measure-duration.py --text` を実際に実行し、出力の形が文書の例と
  一致することを確認
- `<名前>` に使える文字、`?deck=` 省略時の既定、読み込み失敗時のメッセージ、
  枚数と総時間の自動算出、960x540 と container query、`--text` はデッキに
  依らず使えて番号指定は `slides-claude-memo.js` 固定である件、180 文字制限、
  置換表と `RULES` が現時点で一致している件を、すべて実装と突き合わせた。
  **事実の誤りは無し**

指摘は 1 件。`measure-duration.py` の出力例の桁数が実際と違っていた
（実測は小数第 3 位、1.4 倍速は小数第 2 位）。実際に実行した出力へ差し替えた。

ブラウザでの描画は確認していない（headless ブラウザが無い）。構文と参照キーの
突き合わせまで。

## 分担の振り返り

- verifier が見つけたのは出力例の桁数 1 件だけ。事実の照合（10 項目）は
  すべて一致で、誤りは出なかった。**書いた本人には見えない指摘が 1 件出た**
  ので、分けた意味はあった（コマンド例を実際に叩いたのは verifier が先）
- 見込みと食い違いは無し。main も担当も見込みどおり
- 次に**文書だけ・コマンド例あり**の項目をやるなら、同じ形（main が書いて
  verifier 1 人に再現させる）でよい。ただし今回 verifier の報告は
  照合 10 項目を全文で書かせたため長くなった。**一致したものは 1 行、
  食い違いだけ詳しく**と依頼に書けば、$0.2 はもう少し下げられる。
  実装担当を分けるほどの量ではない（ファイル 1 つ、200 行）
