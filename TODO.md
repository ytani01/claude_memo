# TODO

**残っている項目: TODO-051。** これまでに 50 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-052` から。**

---

## TODO-051. `README.md` と `docs/` の内容をスライドにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer × 3 + verifier + reviewer |

- [ ] `tools/measure-duration.py` を `claude-memo.js` 以外のデッキでも使えるようにする
- [ ] `README.md` を、このリポジトリの魅力が伝わる内容に書き直す
- [ ] `slides/readme.js`（リポジトリの紹介、8〜12 枚）
- [ ] `slides/usage.js`（別のスライドを作る人向け、8〜12 枚）
- [ ] `slides/developer.js`（`player.html` を直す人向け、8〜12 枚）
- [ ] 3 デッキの `duration` を測って入れる
- [ ] `README.md` と `docs/` からリンクする

`player.html` の使い方と作りは `docs/` の文章でしか読めない。
このリポジトリ自身がプレゼンプレイヤーなので、同じ内容をスライドでも
見られるようにする。**リポジトリの紹介そのものをスライドで見せられるのが、
このプレイヤーの一番分かりやすい実例になる。**

利用者と決めたこと:

- **デッキは 3 つに分ける。** `slides/readme.js`、`slides/usage.js`、
  `slides/developer.js`。読み手が違うので、ドキュメントの分かれ方に揃える
- **`README.md` の本体も書き直す。** 今はファイル構成が中心なので、
  「HTML 1 枚で、読み上げ付きのプレゼン動画が作れる」ことが先に伝わる
  内容にする。**アピールする相手はプレゼンを作りたい人**で、道具としての
  魅力を前に出す（Claude Code との作り方の話は後ろ）。
  `slides/readme.js` は書き直した `README.md` と同じ内容にする
- **ナレーションを付け、`duration` も測って入れる。** `claude-memo.js` と
  同じ形にする。そのため `tools/measure-duration.py` の書き戻しを
  デッキ指定できるようにする（今は `claude-memo.js` 固定）
- **要点だけを載せる**（各 8〜12 枚）。見出し単位で拾い、細かい注意書きは
  ドキュメント側へ誘導する。ドキュメントを全文なぞらない

**スライドの中でスライドデータの書き方を見せるときは、`duration: 20,` の
次の行に `narration: '` が来る書き方を避ける。** `--write` の置換が
そこに当たってしまう（TODO-050 の reviewer の指摘）。

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-050.** 測った `duration` をスライドデータへ自動で書き戻す](archives/todo/TODO-050.%20測った%20duration%20をスライドデータへ自動で書き戻す.md)
- [**TODO-049.** ドキュメントとスクリプトの数値を定数名に置き換える](archives/todo/TODO-049.%20ドキュメントとスクリプトの数値を定数名に置き換える.md)
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
