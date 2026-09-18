# verifier への依頼（TODO-016）

## 目的

implementer の実装が依頼どおりか、参照漏れが無いかを確かめる。
**修正はしない。** 見つけたことを報告する。

## 読むもの

- 依頼: `archives/agents/TODO-016/implementer-request.md`（1〜10 の一覧と対象外）
- 実装の報告: `archives/agents/TODO-016/implementer-report.md`
- 差分: `git diff claude_memo.html`（未コミット）

## 確かめること

1. 依頼の 1〜10 が**それぞれ**入っているか。1 項目ずつ差分の該当箇所を示す
2. 「手を付けないもの」に手が入っていないか
   （`playlist-count` の直書き、`updateWaveState()`、音声選択の正規表現、
   Web Speech 経路、`speakOnlineTTS()` の `finished`/`handleEnd`、
   スライド定義 `L491-1148`）
3. `<script>` を取り出して `node --check` が通るか
4. 消した識別子（`brand-`, `font-heading`, `Urbanist`, `speechActive`,
   `playlist-item-`）の参照が 0 件か
5. implementer が報告している測定（headless Chromium での矩形と JS の挙動の
   突き合わせ）を**自分でもう一度走らせて、同じ結果になるか**。
   報告の数字をそのまま書き写さず、自分が実際に出した値を報告に書く
6. 既存のコメントが実態と食い違っていないか（特に @media を統合した箇所と、
   `L1895-1896` にあった「@media 2 か所」への言及）

## 完了条件

上の 1〜6 それぞれについて、確かめた結果が報告にある。
**確かめられなかったものは「確かめられなかった」と書く**（推測で埋めない）。

## 報告

`archives/agents/TODO-016/verifier-report.md` に書く。
中身は **確認結果 / 食い違い / 残る懸念** に絞る。
返事は「終わったか・報告ファイルのパス・判断が要る点」を 5 行以内で。

目安 20 分。超えそうなら、そこまでの状態を報告する。
