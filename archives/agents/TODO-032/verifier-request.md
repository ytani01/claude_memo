# TODO-032 検証依頼

## 目的

スライド 15 の `duration` を 17 → 16 に直した。合計の整合を確かめる。

## 対象

- `claude_memo.html` のスライド 15 の `duration` 1 行
- `CLAUDE.md` の合計秒数（316 → 315）

`git diff HEAD` で見えるのはこの 2 行だけのはず。

## 完了条件

- **`tools/measure-duration.py --all` の 17 枚が、`slideData` の
  `duration` と全枚一致すること。** TODO-030・031 の時点で残っていた
  スライド 15 のずれが、これで消える
- `duration` の合計が 315 秒で、`CLAUDE.md` の記述と一致
  （`formatTime(315)` は `5:15`）
- `#total-time-display` の初期表示が、`duration` の合計 +
  `pauseSeconds`（既定 2 秒）× 17 枚で計算されていること。
  **この値は `duration` の合計とは別物**なので、
  `5:15` になっていなくてよい。**実際に出る値を数字で報告すること**
- JS エラーが出ない。17 枚の送りと再生が動く

## やらないこと

**コードは直さない。** レイアウトの測り直しは要らない（画面は変えていない）。

## 報告

`archives/agents/TODO-032/verifier-report.md` に書く。
**返事は 5 行以内**。

## 目安

10 分。`--all` は 17 回 `curl` を叩く。
