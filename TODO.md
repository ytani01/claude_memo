# TODO

**残っている項目: TODO-016。** これまでに 15 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。**番号は `TODO-017` から。**

---

## TODO-016. 未使用の定義と冗長な記述を削る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

- [ ] tailwind.config の `colors.brand`（6 色）と `fontFamily.heading` を消し、
      Google Fonts の読み込みから `Urbanist` を外す（いずれも参照 0）
- [ ] `.video-viewport` の `width: 100%` / `max-width: 100%` と
      `#viewport-frame { width: 100% }` を消す（flex 列の子は既定で幅いっぱい）
- [ ] 同一条件の `@media` 2 ブロックを 1 つに統合する
- [ ] `speechActive` を消す（代入 4 回・参照 0 回）
- [ ] `initPlaylist()` の `btn.id = playlist-item-N` を消す
      （TODO-014 で配列参照に変えた名残で、参照が無い）
- [ ] `initPlaylist()` 冒頭の再初期化 2 行を消す（呼び出しは `startApp()` からの 1 回だけ）
- [ ] `slideStartTimes` の累積ループを短くする
- [ ] 字幕トグル・音声エンジン切替・速度の巡回の 3 ハンドラを、
      `classList.toggle` と剰余で短くする
- [ ] `#viewport-stage` の `getElementById` 2 か所を、上の DOM キャッシュに寄せる

`/ponytail-review` で `claude_memo.html` 全体を見て出た指摘のうち、
**描画結果と動作が変わらないものだけ**を拾った。TODO-014 と同じ趣旨の続き。
行番号は立てた時点（1939 行）のもの。見込み −55 行ほど。

**この項目に入れないもの**（表示か動作が変わるので別扱い）:

- `playlist-count` の `17 Slides` 直書き（JS から更新していない）
- `updateWaveState()` が組み立てるクラスと HTML の初期値の食い違い
  （`text-[9px]` / `text-xs`）
- Web Speech の音声選択の正規表現（名前の当て推量で 3 段になっている）
- Web Speech 経路そのものの削除
- `speakOnlineTTS()` の `finished` フラグ削除（等価とは言い切れない）

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

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
