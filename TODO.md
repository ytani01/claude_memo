# TODO

**残っている項目: TODO-057、TODO-058、TODO-059。** これまでに 56 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-060` から。**

---

## TODO-057. 3 デッキに wording を通す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | wording + verifier |

- [ ] `slides/readme.js` / `slides/user.js` / `slides/developer.js` の表示テキストと
      ナレーションを推敲する
- [ ] ナレーションが変わったスライドの `duration` を測り直す
- [ ] 3 デッキをブラウザで開いて確かめる

TODO-055 で `README.md` / `docs/User.md` / `docs/Developer.md` を推敲したが、
同じ内容を載せた 3 デッキは手つかずで、語が食い違っている。例:
`docs/Developer.md` の見出しは「副作用のある実装」に直したが、
`slides/developer.js` のスライド 8 は「触ると鳴らなくなるもの」のまま。

- **用語は文書に揃えるが、キャッチコピー的な文は残す。** スライド 1 の
  「動き出す」は `README.md` では「動く」に直したが、表題としてはそのまま
- `slides/claude-memo.js` は対応する文書が無いので対象外。`slides/_rules.js` も触らない
- `duration` は `tools/measure-duration.py --deck <名前> --all --write` で測り直す
- 文言だけで分岐は変わらないので reviewer は入れない
- wording への依頼文に、TODO-055 の振り返りどおり
  **「簡潔化のために文を削らない。1 文に 2 つ書いてあるときは両方残して分ける」**
  を明記する

---

## TODO-058. 「デッキ」をやめ、識別子の `deck` も `slides` に変える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + wording + verifier + reviewer |

- [ ] 識別子の `deck` を `slides` に変える（`?slides=`、`slidesConfig`、`--slides`）
- [ ] 旧 `?deck=` も受けるようにする
- [ ] `slides/_rules.js` から `deck` と `deckConfig` の読みの置換を外す
- [ ] 日本語の文章の「デッキ」を「スライド一式」に言い換える
- [ ] ナレーションが変わったスライドの `duration` を測り直す

「デッキ」はスライドの束を指すつもりで使ってきたが、一般的な日本語ではない。
カセットデッキやカードゲームを連想されやすく、特に**読み上げでは耳で意味が
取れない**。`slides/_rules.js` に `deck`→「デッキ」の読みの置換があること自体、
識別子が音声に漏れている証拠になっている。
`deckConfig` は `docs/User.md` で利用者に書かせる名前なので、
**文章側だけを直しても「デッキ」は消せない。**

**日本語は「スライド一式」、識別子は `slides` に統一する。**

### 変えるもの

| いま | あと | 場所 |
|------|------|------|
| `?deck=<名前>` | `?slides=<名前>` | `player.html` |
| `deckConfig` | `slidesConfig` | `player.html`、`slides/*.js` 4 本、`tools/` 2 本 |
| `--deck` | `--slides` | `tools/measure-duration.py` |
| `deck-heading` | `slides-heading` | `player.html` |

- **旧 `?deck=` も受ける。** 公開済みのリンクが切れるため。`player.html` で
  `slides` を先に見て、無ければ `deck` を見る
- **`slides/claude-memo.js` も対象。** 日本語の文章は変えないが、
  `deckConfig` を持っているため
- **`CLAUDE.md` も対象。** 識別子を 1 箇所書いている
- `slidesConfig` と `slideData` が 1 文字違いで並ぶのは承知のうえ。
  `slideData` は変えない
- **`docs/User.md` に「旧 `?deck=` も動く」とは書かない。** 書くと利用者が
  古い書き方を使い続ける。動くが、文書には出さない。
  `player.html` のコメントにだけ、旧名を受ける理由を残す

分岐が 1 つ増える（`slides` が無ければ `deck` を見る）ので reviewer を入れる。
**TODO-057 が決着してから着手する。** 同じ 3 ファイルを触るため。

---

## TODO-059. 「HTML 1 枚で動く」という誤りを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | wording + verifier |

- [ ] `README.md` と `slides/readme.js` の 5 箇所を書き換える
- [ ] ナレーションが変わったスライドの `duration` を測り直す

**動かすのに要るのは 3 ファイル**で、「HTML 1 枚」は事実ではない。
`docs/User.md` の「他のサーバーへ持っていくとき」自身が「渡すのは次の 3 つだけ」
として `player.html` / `slides/_rules.js` / `slides/<名前>.js` を挙げている。
`player.html` は `slides/_rules.js` を無条件に読み、`prepareSpeechText()` が
その `SPEECH_RULES` を参照するため、欠けると読み上げで落ちる。

TODO-041 で `player.html` とスライドデータを分け、TODO-054 で置換表を
`_rules.js` に出した結果、**分割前の `claude_memo.html` 時代の言い方だけが
残った。**

**「ファイル 3 つを置くだけで、ナレーション付きのプレゼンが動く」に変える。**
「ビルドもインストールも不要」はそのまま使える。

| ファイル | 箇所 |
|----------|------|
| `README.md:3` | 冒頭の一文 |
| `slides/readme.js:5` | `deckConfig.title`（ブラウザのタブに出る） |
| `slides/readme.js:23,31` | スライド 1 のナレーションと `h1` |
| `slides/readme.js:260,270` | まとめスライドのナレーションと本文 |

- `slides/user.js` などの「1 枚のスライド」はスライドの枚数の話なので**対象外**
- `README.md:40` と `tools/test_measure_duration.py:19` の `'1 枚目'` は
  サンプルの題名なので**対象外**
- 事実の言い換えだけで分岐は変わらないので reviewer は入れない
- **TODO-057 が決着してから着手する。** `slides/readme.js` を触るため

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由も記載してある。** 蒸し返す前に読むこと。

- [**TODO-056.** 他のサーバーへ公開するときに要るファイルを `docs/User.md` に書く](archives/todo/TODO-056.%20%E4%BB%96%E3%81%AE%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC%E3%81%B8%E5%85%AC%E9%96%8B%E3%81%99%E3%82%8B%E3%81%A8%E3%81%8D%E3%81%AB%E8%A6%81%E3%82%8B%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%20docs%20User.md%20%E3%81%AB%E6%9B%B8%E3%81%8F.md)
- [**TODO-055.** 各ドキュメントに wording を通す](archives/todo/TODO-055.%20各ドキュメントに%20wording%20を通す.md)
- [**TODO-052.** ナレーションの読みの置換表を、プレイヤー共通の語まで広げる](archives/todo/TODO-052.%20ナレーションの読みの置換表を、プレイヤー共通の語まで広げる.md)
- [**TODO-054.** 読みの置換表を外に出し、デッキごとに足せるようにする](archives/todo/TODO-054.%20%E8%AA%AD%E3%81%BF%E3%81%AE%E7%BD%AE%E6%8F%9B%E8%A1%A8%E3%82%92%E5%A4%96%E3%81%AB%E5%87%BA%E3%81%97%E3%80%81%E3%83%87%E3%83%83%E3%82%AD%E3%81%94%E3%81%A8%E3%81%AB%E8%B6%B3%E3%81%9B%E3%82%8B%E3%82%88%E3%81%86%E3%81%AB%E3%81%99%E3%82%8B.md)
- [**TODO-053.** `docs/Usage.md` を `docs/User.md` に変える](archives/todo/TODO-053.%20docs%20Usage.md%20を%20docs%20User.md%20に変える.md)
- [**TODO-051.** `README.md` と `docs/` の内容をスライドにする](archives/todo/TODO-051.%20README.md%20と%20docs%20の内容をスライドにする.md)
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
