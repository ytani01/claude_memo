# TODO-023 verifier への依頼

## 目的

`claude_memo.html` のスライド 2 を「主なコマンド一覧」から「全体の概要」へ
差し替えた。指示どおりの変更になっているか、表示が崩れていないかを確かめる。
**修正はしない。** 見つけたことを報告する。

## 対象範囲

- `claude_memo.html` の未コミット差分（`git diff`）
- 直前のコミットは `docs(todo): …TODO-023 として立てる`

## 確かめること（すべて数字か引用で示す）

1. 差分が `slideData[1]`（`// Slide 2` の要素）だけに収まっていること。
   他のスライド、再生ロジック、`playlist-count`（465 行付近）に差分が無いこと
2. `slideData.length` が 17 のままで、`duration` の合計が 317 秒であること
3. スライド 2 の `duration` が 19 で、これがナレーションの実測と合うこと。
   確かめ方は TODO-018 と同じ:
   `prepareSpeechText(slideData[1].narration).substring(0,180)` を
   `https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q=<URL エンコード>`
   から `curl --referer '' -A 'Mozilla/5.0'` で取得し、`ffprobe` で秒数を測る。
   **1.4 で割った値の四捨五入**が `duration` と一致するか
   （main の実測は 1.0 倍で 26.256 秒 → 1.4 倍速で 18.75 秒 → 19）
4. 表示が崩れないこと。playwright で次の 4 条件を実測する
   （`archives/agents/TODO-011/measure.js.txt` が使える雛形）。
   スライド 2 を表示させた状態で、**カード 4 枚と「5. 現状の課題とまとめ」の行が
   `#slide-canvas` の矩形の中に収まっているか**（はみ出し px を出す）:
   - PC 1280x800（タッチ無し・通常表示）
   - 横持ち 844x390（タッチ有り・通常表示）
   - 横持ち 844x390（タッチ有り・フルスクリーン）
   - 縦持ち 390x844（タッチ有り・フルスクリーン）
   スライド 2 へは `#slide-canvas` 描画後に次スライドボタン 1 回で移れる
   （セレクタは自分で確かめること）
5. 参考として、変更前のスライド 2（`git stash` せず `git show HEAD:claude_memo.html`
   を別ファイルに出して開く）と比べ、はみ出しが増えていないこと

## 完了条件

上の 1〜5 について、実測した数字を添えて報告する。
**数字の無い「問題なし」は報告として受け付けない。**

## 報告

`archives/agents/TODO-023/verifier-report.md` に書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」を 5 行以内で。

所要の目安は 10〜15 分。playwright の起動が遅くても待ってよい。
