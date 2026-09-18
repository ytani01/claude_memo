# TODO-011 の分担

レイアウトの挙動が変わる項目なので、`~/.claude/CLAUDE.md` の決まりどおり
確認とレビューを別の担当に分けた。実装は 1 ファイルの CSS / JS だけなので
main が手を動かし、implementer は立てていない。

| 担当 | 役割 | 報告 |
|------|------|------|
| main | 実装、実測、判断 | — |
| verifier | 指示どおり直っているかの実測 | [1 巡目](verifier-report.md) / [2 巡目](verifier-report-2.md) |
| reviewer | 規約と設計に照らした指摘 | [1 巡目](reviewer-report.md) / [2 巡目](reviewer-report-2.md) |

2 巡したのは、1 巡目の CSS 版（高さの基準を 89px の定数で書いたもの）が
640〜712px 幅の帯で破れることを reviewer の実測が示し、JS 実測の版に
作り直したため。

`measure.js.txt` は main が 1 巡目に使った測定スクリプト。
決着の内容は `archives/todo/TODO-011. 横持ちスマホの通常表示でもスライド全体を画面に収める.md`。
