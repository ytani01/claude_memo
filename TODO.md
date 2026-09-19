# TODO

**残っている項目: TODO-049。** これまでに 48 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-050` から。**

---

## TODO-049. ドキュメントとスクリプトの数値を定数名に置き換える

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | verifier |

- [ ] `docs/Developer.md` の 6 箇所を定数名に直す
- [ ] `docs/Usage.md` の 3 箇所を定数名に直す
- [ ] `docs/Developer.md:66` の `baseSpeedMultiplier` を正しい名前に直す
- [ ] `tools/measure-duration.py` の docstring・help・結果表示を直す
- [ ] `docs/Usage.md` の実行例を、直したあとの出力に合わせる

`player.html` で定数に名前が付いている値（TODO-024）が、文書には数値のまま
書いてある。コードを直したときに文書だけ古くなる。**文書では定数名だけを書き、
数値は併記しない**（併記すると片方だけ古くなるので、直す意味が薄れる）。

| 場所 | 今の記述 | 定数 |
|------|----------|------|
| `Developer.md` 63・66・67・76 | `1.4` | `BASE_SPEED_MULTIPLIER` |
| `Developer.md` 96 | `180 文字で切る` | `TTS_MAX_CHARS` |
| `Developer.md` 105 | `4.5` | `SPEECH_CHARS_PER_SECOND` |
| `Developer.md` 108 | `3 秒足した` | `TTS_END_MARGIN_MS` |
| `Developer.md` 118 | `40 文字程度` | `splitForSpeech()` の `maxLen` の既定値 |
| `Developer.md` 144 | `960x540` | `SLIDE_BASE_WIDTH_PX`（`SLIDE_ASPECT_RATIO` と組）|
| `Usage.md` 56 | `960x540` | 同上 |
| `Usage.md` 77 | `1.4 倍速` | `BASE_SPEED_MULTIPLIER` |
| `Usage.md` 97 | `180 文字で切れる` | `TTS_MAX_CHARS` |

`Developer.md:66` の `baseSpeedMultiplier` は実在しない名前（正しくは
`BASE_SPEED_MULTIPLIER`）。

### `tools/measure-duration.py`

スクリプトの側にも、31・32 行の定数と別に数値が書いてある。

| 行 | 今の記述 | 直し方 |
|----|----------|--------|
| 4 | docstring の `1.4 倍速` | 定数名で書く |
| 9・97 | `17 枚すべて` | 枚数はデータ次第なので「すべて」に変える |
| 68 | docstring の `1.4 倍速` | 定数名で書く |
| 113 | `★180 字で切れる` | 定数から埋め込む |
| 115 | `1.4 倍速` | 定数から埋め込む |

**結果表示は `定数名=値` の形で、実際の値も一緒に出す。** 定数から
埋め込むので、`player.html` に合わせて写しを直せば表示も追従する。

```
スライド 2: 原文 78 字 / 読み 92 字 / 実測 29.760s
  / BASE_SPEED_MULTIPLIER=1.4 倍速 21.26s -> duration: 21

スライド 5: 原文 210 字 / 読み 245 字 ★TTS_MAX_CHARS=180 字で切れる
  / 実測 55.200s / BASE_SPEED_MULTIPLIER=1.4 倍速 39.43s -> duration: 39
```

`docs/Usage.md` 87 行の実行例と 98 行の `★180 字で切れる` は、この出力に
合わせて書き直す。ここは**実際に動かした出力を貼る**（手で書かない）。

**定数に対応しない数値はそのまま残す。** `767.98px`（CSS に直接書く値）、
`324 秒`・`0.34〜0.77`・`3px`（実測値）、`15 秒`（Chrome の挙動）。

確認の担当には、書いた定数名が `player.html` に実在するか、値の対応が
合っているか、`docs/Usage.md` の実行例が実際の出力と一致するかを見てもらう。

---

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-048.** スライドデータから `id` を外す](archives/todo/TODO-048.%20スライドデータから%20id%20を外す.md)
- [**TODO-047.** 旧 URL 用の `claude_memo.html` を削除する](archives/todo/TODO-047.%20旧%20URL%20用の%20claude_memo.html%20を削除する.md)
- [**TODO-046.** スライドのデータを `slides/` に置く](archives/todo/TODO-046.%20スライドのデータを%20slides%20に置く.md)
- [**TODO-045.** リポジトリの入口として `README.md` を作る](archives/todo/TODO-045.%20リポジトリの入口として%20README.md%20を作る.md)
- [**TODO-044.** `public_html/` 以外へ移しても動くことを `docs/Developer.md` に書く](archives/todo/TODO-044.%20public_html%20以外へ移しても動くことを%20docs%20Developer.md%20に書く.md)
- [**TODO-043.** `player.html` を直す人向けの `docs/Developer.md` を作る](archives/todo/TODO-043.%20player.html%20を直す人向けの%20docs%20Developer.md%20を作る.md)
- [**TODO-042.** `player.html` で他のスライドを作る手順を `docs/Usage.md` に書く](archives/todo/TODO-042.%20player.html%20で他のスライドを作る手順を%20docs%20Usage.md%20に書く.md)
- [**TODO-041.** プレイヤーの共通部分とスライドのデータを別ファイルに分ける](archives/todo/TODO-041.%20プレイヤーの共通部分とスライドのデータを別ファイルに分ける.md)
- [**TODO-040.** Inworld AI の声に差し替えるか検討する（対応しない）](archives/todo/TODO-040.%20Inworld%20AI%20の声に差し替えるか検討する.md)
- [**TODO-035.** 字幕を ON にしたとき全文を表示する](archives/todo/TODO-035.%20字幕を%20ON%20にしたとき全文を表示する.md)
- [**TODO-039.** スライド 6 に担当とモデルが固定でない旨の注釈を入れる](archives/todo/TODO-039.%20スライド%206%20に担当とモデルが固定でない旨の注釈を入れる.md)
- [**TODO-038.** スライド 4 に「壁打ちで精査」を入れる](archives/todo/TODO-038.%20スライド%204%20に「壁打ちで精査」を入れる.md)
- [**TODO-037.** まとめスライドの内容とナレーションの長さを見直す](archives/todo/TODO-037.%20まとめスライドの内容とナレーションの長さを見直す.md)
- [**TODO-034.** タイトルスライドのナレーションを短くする](archives/todo/TODO-034.%20タイトルスライドのナレーションを短くする.md)
- [**TODO-036.** ステータスラインの実例の区切りの段差を直す](archives/todo/TODO-036.%20ステータスラインの実例の区切りの段差を直す.md)
- [**TODO-033.** 説明の順番を変え、冒頭を自己紹介から入る流れに直す](archives/todo/TODO-033.%20説明の順番を変え、冒頭を自己紹介から入る流れに直す.md)
- [**TODO-028.** トークンの話を呼応させる](archives/todo/TODO-028.%20トークンの話を呼応させる.md)
- [**TODO-027.** 冒頭を掴みにして、予防線を減らす](archives/todo/TODO-027.%20冒頭を掴みにして、予防線を減らす.md)
- [**TODO-026.** まとめに「その他の便利な使い方」を足す](archives/todo/TODO-026.%20まとめに「その他の便利な使い方」を足す.md)
- [**TODO-025.** スライドの並びを章立てに合わせる](archives/todo/TODO-025.%20スライドの並びを章立てに合わせる.md)
- [**TODO-032.** スライド 15 の `duration` のずれを直す](archives/todo/TODO-032.%20スライド%2015%20の%20duration%20のずれを直す.md)
- [**TODO-031.** 「使い方」の読みを直す](archives/todo/TODO-031.%20「使い方」の読みを直す.md)
- [**TODO-030.** `duration` の測定スクリプトをリポジトリに入れる](archives/todo/TODO-030.%20duration%20の測定スクリプトをリポジトリに入れる.md)
- [**TODO-029.** フッターと category ラベルを削除する](archives/todo/TODO-029.%20フッターと%20category%20ラベルを削除する.md)
- [**TODO-024.** JS の数値リテラルに名前を付ける](archives/todo/TODO-024.%20JS%20の数値リテラルに名前を付ける.md)
- [**TODO-023.** スライド 2 を「主なコマンド一覧」から「全体の概要」に差し替える](archives/todo/TODO-023.%20スライド%202%20を「主なコマンド一覧」から「全体の概要」に差し替える.md)
- [**TODO-022.** 再生速度をプルダウンで選べるようにする](archives/todo/TODO-022.%20再生速度をプルダウンで選べるようにする.md)
- [**TODO-020.** ナレーション後の待ちの間も経過時間を進める](archives/todo/TODO-020.%20ナレーション後の待ちの間も経過時間を進める.md)
- [**TODO-021.** ナレーション後の待ち秒数を選べるようにする](archives/todo/TODO-021.%20ナレーション後の待ち秒数を選べるようにする.md)
- [**TODO-019.** Online TTS に安全タイマーを入れる](archives/todo/TODO-019.%20Online%20TTS%20に安全タイマーを入れる.md)
- [**TODO-018.** 進行バーと時間表示を実時間に合わせる](archives/todo/TODO-018.%20進行バーと時間表示を実時間に合わせる.md)
- [**TODO-017.** スライド 3「現状の課題」をまとめの直前へ移す](archives/todo/TODO-017.%20スライド%203「現状の課題」をまとめの直前へ移す.md)
- [**TODO-016.** 未使用の定義と冗長な記述を削る](archives/todo/TODO-016.%20未使用の定義と冗長な記述を削る.md)
- [**TODO-015.** オンライン音声に無料で使える他の選択肢がないか検討する（対応しない）](archives/todo/TODO-015.%20オンライン音声に無料で使える他の選択肢がないか検討する.md)
- [**TODO-014.** 見た目と動作を変えない範囲でコードの重複を整理する](archives/todo/TODO-014.%20見た目と動作を変えない範囲でコードの重複を整理する.md)
- [**TODO-013.** スライド 4 のナレーションから「スマホから SSH」を外す](archives/todo/TODO-013.%20スライド%204%20のナレーションから「スマホから%20SSH」を外す.md)
- [**TODO-011.** 横持ちスマホの通常表示でもスライド全体を画面に収める](archives/todo/TODO-011.%20横持ちスマホの通常表示でもスライド全体を画面に収める.md)
- [**TODO-012.** 「主なコマンド」のナレーションから「頻繁に」を外す](archives/todo/TODO-012.%20「主なコマンド」のナレーションから「頻繁に」を外す.md)
- [**TODO-010.** スマホのスワイプでスライドを切り替える](archives/todo/TODO-010.%20スマホのスワイプでスライドを切り替える.md)
- [**TODO-009.** 横持ちスマホのフルスクリーンでスライド本文が上段に被る](archives/todo/TODO-009.%20横持ちスマホのフルスクリーンでスライド本文が上段に被る.md)
- [**TODO-008.** スライド 12 の記述例からコミットの行を外す](archives/todo/TODO-008.%20スライド%2012%20の記述例からコミットの行を外す.md)
- [**TODO-007.** スライド 12 の TODO.md 記述例から `/clear` の行を外す](archives/todo/TODO-007.%20スライド%2012%20の%20TODO.md%20記述例から%20clear%20の行を外す.md)
- [**TODO-006.** タップしたときの OSD を 2 秒出す](archives/todo/TODO-006.%20タップしたときの%20OSD%20を%202%20秒出す.md)
- [**TODO-005.** スライドのタップで再生と一時停止を切り替える](archives/todo/TODO-005.%20スライドのタップで再生と一時停止を切り替える.md)
- [**TODO-004.** 横持ちのスマホでフルスクリーンの高さを画面に合わせる](archives/todo/TODO-004.%20横持ちのスマホでフルスクリーンの高さを画面に合わせる.md)
- [**TODO-003.** 横持ちのスマホでフルスクリーンから抜けられないのを直す](archives/todo/TODO-003.%20横持ちのスマホでフルスクリーンから抜けられないのを直す.md)
- [**TODO-002.** Android Chrome での読み上げを直す](archives/todo/TODO-002.%20Android%20Chrome%20での読み上げを直す.md)
- [**TODO-001.** スマホ縦画面で 16:9 のまま幅いっぱいに表示する](archives/todo/TODO-001.%20スマホ縦画面で%2016:9%20のまま幅いっぱいに表示する.md)
