# TODO-014. 見た目と動作を変えない範囲でコードの重複を整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| reviewer | Opus 5 | high | 20,710 | 57,822 | 33% |
| implementer | Opus 5 | medium | 18,540 | 59,968 | 33% |
| main | Opus 5 | high | 6,069 | 43,221 | 24% |
| verifier | Sonnet 5 | medium | 9,995 | 44,723 | 9% |
| 合計 |  |  | 55,314 | 205,734 | 概算 $3.4 |

- implementer は定義のモデルが sonnet。CSS の上書き順とシークバーの境界判定を
  伴うので Opus 5 に上書きした
- reviewer も定義のモデルが sonnet。動作が変わらないことの判定が主眼なので
  Opus 5 に上書きした
- verifier は定義のまま（sonnet / effort medium）。手順の決まった確認なので上げなかった

## きっかけ

`/ponytail-review` で `claude_memo.html` 全体を見て出た指摘のうち、
**描画結果と動作が変わらないものだけ**を拾って項目にした。行番号は
着手時点（1972 行）のもの。

## やったこと

`claude_memo.html` の 9 か所。1972 行 → 1939 行（58 挿入 91 削除）。

- [x] `.video-viewport.pseudo-fullscreen` の 2 か所の全文定義を、メディアクエリ側は
      差分（`right` / `bottom` / `width` / `height` / `z-index`）だけの上書きにした（−11 行）
- [x] `play()` が Promise を返さない場合の `else` 分岐を消した（−6 行）
- [x] `formatTime()` の秒のゼロ詰めを `padStart` にした
- [x] `updateWaveState()` の `className` 全文 2 本を、共通部分 + 色のクラスと
      `classList.toggle('paused', !active)` にした（−5 行）
- [x] プレイリスト項目のクラス文字列 4 本を定数 3 本と `setPlaylistItemState()` に
      まとめ、`initPlaylist()` と `updatePlaylistSelection()` の両方から呼ぶようにした
- [x] `updatePlaylistSelection()` の `getElementById('playlist-item-N')` を、
      `initPlaylist()` で作ったボタンの配列に置き換えた
- [x] `playerViewport` があるのに `getElementById('player-viewport')` を
      3 回呼んでいた箇所を、その定数に置き換えた
- [x] シークバーの対象スライド探索の手書き累積ループを、
      `slideStartTimes` と `findLastIndex` に置き換えた
- [x] 同一ファイル内の静的要素に対する null ガード 4 つを消した

見送ったものは無い。

## 確かめたこと

ビルドもテストも無いので、静的な確認まで。ブラウザでの実見は利用者に残る。

- `<script>` 2 本を取り出しての `node --check` — どちらも成功
- 9 項目それぞれについて、差分の該当箇所を verifier が個別に確認
- CSS の重複解消: 元の 2 か所のプロパティを全列挙して突き合わせ、
  計算値 14 プロパティがすべて一致
- シークバー: 新旧のロジックを独立に再現して実データで突き合わせ。
  reviewer 側は 100,056 通りを実測し、差が出るのは `targetSec > 総時間` の
  1 ケースのみ（旧=先頭へ、新=末尾）。この値は `ratio` のクランプで到達しない
- `classList.toggle` への置き換え 2 か所: 元の `className` 全文代入で消えていた
  クラスが toggle 後に残らないことを、クラスの集合を突き合わせて確認
- 削除した識別子の参照漏れが無いことを grep で確認
- 「この項目に入れないもの」に手が入っていないことを確認

reviewer の指摘で**動作が変わるものは 0 件**。

## 残ること

- **ブラウザでの見た目と操作の確認。** PC と、幅 390px 相当・横持ち相当の
  タッチ画面で、通常表示と擬似フルスクリーンが変更前と同じこと。再生・一時停止、
  前後送り、速度、消音、字幕、フルスクリーン、シークバーのクリック、
  チャプター一覧のクリックとスクロール追従、横スワイプ
- `unlockFallbackAudio()` は、`play()` が Promise を返さない環境では
  音量が 0 のまま残る（旧 `else` 分岐が担っていた）。対象ブラウザでは到達しないと
  判断して直していない。必要になったら `catch` に 1 行足す

## 分担の振り返り

- **implementer** は 9 項目を全部実施したうえで、シークバーの新旧を実データ
  1055 ケースで突き合わせ、範囲外の変更（Escape 分岐の `viewport &&` ガード削除）を
  自己申告した。自分で境界を測ったのが効いた
- **verifier** は CSS の計算値 14 プロパティの突き合わせ表と `node --check` の
  実行結果を出した。実測から逃げなかったのは、依頼に「実行したコマンドと出力、
  突き合わせた具体的な値を必ず載せる」と書いたため
- **reviewer** は implementer より広い 100,056 通りでシークバーを測り、
  差が出る唯一の条件（`targetSec > 総時間`）とそれが到達不能な理由を特定した。
  implementer の 1055 ケースでは出なかった差なので、レビューを分けた分は回収できた
- **見込みと食い違わなかった。** 3 担当とも見込みどおり動いた
- **次に同じ規模（1 ファイル内・挙動を変えない整理・10 項目前後）なら、同じ 3 担当で組む。**
  ただし implementer と reviewer が同じ突き合わせを二重に走らせた分
  （合計で料金の 66%）は減らせる。implementer への依頼から「境界の実測」を外し、
  測るのは reviewer だけにすると、品質を落とさずに 1 割ほど減るはず。
  verifier は Sonnet のままでよい（料金の 9% で、CSS の全列挙は出せた）
