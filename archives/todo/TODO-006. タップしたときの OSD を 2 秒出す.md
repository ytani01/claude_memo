# TODO-006. タップしたときの OSD を 2 秒出す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main のみ |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 3,697 | 6,434 | 72% |
| verifier | Haiku 4.5 | 記載なし | 14,248 | 39,227 | 28% |
| 合計 |  |  | 17,945 | 45,661 | 概算 $0.7 |

- 見込みでは「main のみ」としたが、コードを変える項目なので確認は分けるという
  規約（`~/.claude/CLAUDE.md`）に従い、着手後に verifier を足した
- verifier の定義に `effort` の行は無い。Haiku は effort に対応しないため
- 集計の終点は決着のコミットより前（まだ完了していない状態で数えた）

## きっかけ

TODO-005 で入れた ▶ / ‖ の表示が 0.5 秒では短い、と利用者が実機で確認した。

## やったこと

`claude_memo.html` の 2 か所。`#tap-feedback-icon.is-shown` の
`animation` を 2 秒にし、`@keyframes tapFeedback` を 4 つのキーフレームにした。

```css
0%   { opacity: 0.9; transform: scale(0.8); }
10%  { opacity: 0.9; transform: scale(1); }
75%  { opacity: 0.9; transform: scale(1); }
100% { opacity: 0; transform: scale(1.3); }
```

全体をゆっくり薄くするのではなく、**出したあと 1.5 秒はそのままで、
最後の 0.5 秒で消す**。利用者が選んだ出し方。

## 確かめたこと

- **headless chromium 152 での実測（main）** — `#player-viewport` を
  クリックしてアニメーションを掴み、`a.pause()` してから `currentTime` を
  動かして `opacity` を読んだ。`duration` は 2000ms、0〜1500ms は 0.9 のまま、
  1700ms で 0.386、2000ms で 0
- **verifier による確認** — 差分が 2 か所だけで、キーフレームが仕様どおりで
  あること。報告は `archives/agents/TODO-006/verifier-report.md`。
  **ただし実測はしていない**（依頼文に測り方まで書いたが、
  「headless chromium での JavaScript 実行結果の出力は技術的に困難」として
  静的な確認で済ませた）

## 分担の振り返り

- verifier（Haiku 4.5）が見つけたものは無い。差分の範囲とキーフレームの
  読み合わせだけで、依頼した実測には届かなかった
- 見込み（main のみ）と食い違ったのは、規約どおり確認を分けたため。
  分けた判断自体は正しいが、**測り方まで書いた依頼を踏めなかった**のは
  モデルの選択を誤った
- **次に同じ規模（CSS の数値 1 か所）で実測が要るなら、verifier には
  Sonnet 5 以上を充てる。** Haiku は「手順どおりに測る」依頼でも、
  途中で難しいと判断すると静的な確認へ逃げる（TODO-004 では Sonnet 5 が
  「環境が無い」として同じ逃げ方をしたので、依頼文に環境と測り方を
  書くだけでは足りない）。**報告に「実測した」と書かれていても、
  測った値が載っていなければ測っていないと見ること**
