# TODO-001 の分担

`.claude/agents/*.md` はこのプロジェクトに無く、`~/.claude/agents/` の
汎用の定義をそのまま使った。

| 担当 | モデル | 何をさせたか |
|------|--------|--------------|
| implementer | Opus 5（上書き） | 縮小方式の設計と実装。3 巡 |
| verifier | Sonnet 5（上書き） | ブラウザでの実測。3 巡 |
| reviewer | Opus 5（上書き） | 挙動の変化のレビュー。3 巡 |

**この分担にした理由**: 見た目が変わる項目で、「はみ出さないか」（verifier）と
「挙動の意味が変わっていないか」（reviewer）は別の観点なので分けた。
実装は container query と `transform` の組み合わせで込み入るため Opus に、
実測は手順が決まっているため Sonnet に充てた。

## 報告ファイル

- `implementer-report.md` / `-2.md` / `-3.md`
- `verifier-report.md` / `-2.md` / `-3.md`
- `reviewer-report.md` / `-2.md` / `-3.md`

振り返りは `archives/todo/TODO-001. スマホ縦画面で 16:9 のまま幅いっぱいに表示する.md` にある。
