# TODO-016. 未使用の定義と冗長な記述を削る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| reviewer | Opus 5 | high | 31,872 | 131,643 | 35% |
| main | Opus 5 | high | 14,600 | 30,804 | 33% |
| implementer | Opus 5 | medium | 21,978 | 59,037 | 24% |
| verifier | Sonnet 5 | medium | 16,531 | 56,529 | 9% |
| 合計 |  |  | 84,981 | 278,013 | 概算 $6.1 |

- implementer は定義のモデルが sonnet。`@media` の統合と `width` の削除が
  計算値に効くので Opus 5 に上書きした
- reviewer も定義のモデルが sonnet。この項目の合否が「動作が変わらないこと」の
  判定そのものなので Opus 5 に上書きした
- verifier は定義のまま（sonnet / effort medium）。手順の決まった確認なので上げなかった

分担の理由と各担当の報告は [archives/agents/TODO-016/](../agents/TODO-016/README.md) にある。

## きっかけ

`/ponytail-review` で `claude_memo.html` 全体を見て出た指摘のうち、
**描画結果と動作が変わらないものだけ**を拾って項目にした。TODO-014 と同じ趣旨の続き。
行番号は着手時点（1939 行）のもの。

## やったこと

`claude_memo.html` の 10 か所。1939 行 → 1900 行（33 挿入 72 削除）。

- [x] tailwind.config の `colors.brand`（6 色）を消した。`brand-` の参照は 0
- [x] `fontFamily.heading` を消し、Google Fonts の読み込みから `Urbanist` を外した。
      `font-heading` の参照は 0 で、フォント 1 つ分の読み込みも減った
- [x] `.video-viewport` の `width: 100%` と `max-width: 100%` を消した
- [x] `#viewport-frame { width: 100% }` をルールごと消した
      （どちらも flex 列の子は既定で幅いっぱいになるため）
- [x] 同一条件の `@media` 2 ブロックを 1 つに統合し、
      `setupViewportScale()` の「@media 2 か所」への言及も実態に合わせた
- [x] `speechActive` を消した（代入 4 回・参照 0 回）
- [x] `btn.id = playlist-item-${idx}` を消した（TODO-014 で配列参照に変えた名残）
- [x] `initPlaylist()` 冒頭の `innerHTML = ''` と `playlistItems.length = 0` を消した
- [x] `slideStartTimes` の累積ループを `map()` にした
- [x] 字幕トグル・音声エンジン切替・速度の巡回の 3 ハンドラを、
      `classList.toggle` と剰余で短くした

reviewer の指摘で、`#viewport-frame` についての PC 側の説明がモバイル用 `@media` の
解説末尾に置かれていて読み違えやすかったので、独立したコメントとして `@media` の
外へ出した。

**この項目に入れないもの**（表示か動作が変わるので別扱い。まだ手を付けていない）:

- `playlist-count` の `17 Slides` 直書き（JS から更新していない）
- `updateWaveState()` が組み立てるクラスと HTML の初期値の食い違い
  （`text-[9px]` / `text-xs`）
- Web Speech の音声選択の正規表現（名前の当て推量で 3 段になっている）
- Web Speech 経路そのものの削除
- `speakOnlineTTS()` の `finished` フラグ削除（等価とは言い切れない）

## 確かめたこと

ビルドもテストも無いので、静的な確認と headless Chromium での突き合わせまで。
ブラウザでの実見は利用者に残る。

- `<script>` を取り出しての `node --check` — 成功
- 消した識別子（`brand-`, `font-heading`, `Urbanist`, `speechActive`,
  `playlist-item-`）の参照が 0 件であることを grep で確認
- 変更前後の 2 版を headless Chromium で開き、6 条件
  （PC / 幅 768 未満 / `pointer: coarse` を再現した 900x600・844x520 を含む）
  × 通常・字幕オン・擬似フルスクリーンで、矩形と class 集合を突き合わせ。
  差は `#player-viewport` の `max-width` の計算値が `100%` → `none` に
  なった 1 点だけで、**使用値の幅は同じ**
- `slideStartTimes` の値、速度の巡回（`indexOf` が -1 になる場合と一周する場合）、
  音声エンジンの巡回が、変更前と一致することを確認
- 「この項目に入れないもの」に手が入っていないことを確認

reviewer の判定で**動作が変わるものは 0 件**。

### 戻さないと決めたこと

reviewer から「`initPlaylist()` の `innerHTML = ''` を消したことで冪等性が
失われ、HTML のプレースホルダのコメントノードが DOM に残る」という指摘が出たが、
**戻さない**。呼び出しは `startApp()` からの 1 回だけで、描画差も無い。
再実行が要るようになった時点で足せばよい。

### 計測のゆらぎ

verifier が implementer の測定を再現したところ、`#slide-canvas` の矩形が
768x1024 と 390x844 で変更前後に差が出た。ただし**変更前の同じファイルを
2 回測っても同じ差が出る**ことを verifier 自身が確認しており、reviewer 側の
6 条件の計測では差が出ていない。フォント読み込みのタイミングなど計測側の
ゆらぎと判断した。implementer の報告にあった「全 45 行完全一致」は、
そのままは再現できていない。

## 分担の振り返り

- **各担当が何を見つけたか。** implementer は 10 か所すべてを入れ、headless
  Chromium での突き合わせまで自前で走らせた。verifier は、報告の数字を写さずに
  自分で測り直したことで「implementer の完全一致が再現しない」ことを見つけた。
  これは**再現させたからこそ出た**もので、報告を読むだけの確認では出ない。
  reviewer は動作が変わるもの 0 件を 6 条件の計測で裏付けたうえ、コメントの
  置き場所と `initPlaylist()` の冪等性という、テストでは捕まらない 2 点を出した
- **見込みと食い違ったのはなぜか。** main のモデルも担当の顔ぶれも見込みどおり。
  食い違ったのは料金で、TODO-014（同型、$3.4）の 1.8 倍の $6.1 になった。
  原因は計測の重複で、**同じ headless Chromium の突き合わせを implementer・
  verifier・reviewer が 3 回別々に組んで走らせた**（reviewer だけで $2.1）。
  「verifier に測り直させる」指示が重複を生んだが、上のとおり収穫もあった
- **次に同じ規模の項目をやるなら。** 計測スクリプトは implementer に 1 本だけ
  作らせ、`archives/agents/TODO-NNN/` に置かせて verifier と reviewer に
  使い回させること。組み直しは 3 回とも Opus 5 の時間を食う。ただし
  **verifier に「自分で走らせて値を報告させる」ところは変えない**
  （ゆらぎはそれで見つかった）。reviewer は Opus 5 のままにする。
  verifier は Sonnet 5 で足りた（料金の 9%）

## 残ること

- **実機での確認。** タッチ端末での見た目と操作、実際の音声再生は未確認
- 「この項目に入れないもの」の 5 件。表示か動作が変わるので、必要なら別項目にする
