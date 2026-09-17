# TODO-002 確認依頼（verifier）

## 目的

implementer の変更（`git diff`、`claude_memo.html` のみ）が依頼どおりか確かめる。
**コードは直さない。** 見つけたことは報告するだけ。

## 読むもの

- `archives/agents/TODO-002/implementer-request.md`（依頼内容）
- `archives/agents/TODO-002/implementer-report.md`（実装の報告）
- `git diff`

## 確かめること

1. 依頼書の「やること」1・2 が両方とも入っているか
2. 依頼書の「やらないこと」（180 文字の切り詰め、safety timeout、`duration`、
   無関係なリファクタリング）に手が入っていないか
3. `<script>` の中身に構文エラーが無いか（自分で確かめ直すこと。
   実装の報告を鵜呑みにしない）
4. `fallbackAudioElement` を触る箇所を全部たどり、使い回しにしたことで
   壊れるところが無いか（`stopSpeech()`、音声エンジンの切替、ミュート、
   スライドの移動、最後まで再生したとき）
5. PC の Chrome で今までどおり動くか。実機（Android）は利用者が見るので不要。
   ブラウザで開いて確かめられるなら確かめる（`run` skill が使えるなら使う）

## 報告

`archives/agents/TODO-002/verifier-report.md` に、確かめた項目と結果、
気になった点を書く。返事は 5 行以内。目安 15 分。
