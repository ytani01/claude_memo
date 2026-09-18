# verifier の報告（TODO-016）

対象: `claude_memo.html` の未コミット差分（`git diff claude_memo.html`）。
`git status` では他に変更ファイルなし（`archives/agents/TODO-016/` は未追跡の報告類のみ）。

## 1. 依頼の 1〜10 が入っているか

diff を通しで読み、1 項目ずつ該当箇所を確認した。すべて入っている。

1. `colors.brand`（旧 L22-31）: diff で `extend` から丸ごと削除を確認
2. `fontFamily.heading`（旧 L34）と Google Fonts の `Urbanist` 指定: diff の
   L9-10、L28-30 相当で削除を確認
3. `.video-viewport` の `width: 100%` / `max-width: 100%`: diff で該当 2 行が
   消えているのを確認
4. `#viewport-frame { width: 100% }` のルールごと削除: diff で確認。
   直前にあった説明コメントは L178-179 側へ移設されている
5. 同条件の `@media` 統合: `grep -n "@media" claude_memo.html` の結果は
   CSS 側 1 か所（L184）のみ。`L1854` のコメントも「@media 2 か所」→
   「@media」に直っている
6. `speechActive`: `grep -n speechActive claude_memo.html` は 0 件
7. `btn.id = playlist-item-${idx}`: diff で削除を確認、`grep -n
   "playlist-item-"` は 0 件
8. `initPlaylist()` 冒頭の `innerHTML = ''` / `playlistItems.length = 0`:
   diff で削除を確認
9. `slideStartTimes` の累積: `slideData.map()` に変更されているのを diff で
   確認。値は後述の実測で変更前と一致
10. 字幕トグル・音声エンジン切替・速度巡回の 3 ハンドラ: diff で
    `classList.toggle` / 三項演算子 / `%` を使った短縮を確認。速度巡回の
    `indexOf` が -1 のときの分岐は、コメントで「(-1+1) % n === 0 で先頭に
    戻る」と説明されており、算術的に正しい

## 2. 「手を付けないもの」に手が入っていないか

diff 全 240 行（unified diff, 32 挿入/73 削除）を通しで見て、上記 1〜10 に
対応するハンドル以外の行は無いことを確認した。個別にも grep で当たった。

- `playlist-count` の `17 Slides` 直書き（L452）: 変更なし
- `updateWaveState()`（L1494 で定義）: diff に登場せず
- 音声選択の正規表現（旧 L1362-1369 相当）: diff に登場せず
- Web Speech 経路: diff に登場せず
- `speakOnlineTTS()` の `finished` / `handleEnd`（現在 L1349-1434 付近に
  複数箇所）: diff に登場せず、grep で今も存在を確認
- スライド定義（旧 L491-1148）: diff に登場せず

手を付けないものへの混入は無かった。

## 3. `<script>` を取り出して `node --check`

`grep -n "<script"` で 3 件ヒット（L10 は `src` 付きの外部読み込みで中身無し、
L18 と L470 が対象）。`awk` で `<script>`〜`</script>` の中身を連結して
抽出し（1436 行）、`node --check` を実行した。

```
node --check extracted.js
```

終了コード 0（エラー無し）。実装報告の「成功」と一致。

## 4. 消した識別子の参照が 0 件か

```
grep -n "brand-\|font-heading\|Urbanist\|speechActive\|playlist-item-" claude_memo.html
```

ヒット 0 件（`grep` の終了コード 1 = 不一致）。実装報告と一致。

## 5. implementer の測定を自分でも走らせた結果

`chromium --headless=new` で、実装報告と同じ観点（矩形測定・JS 挙動記録）の
スクリプトを自分で書いて（実装者の使ったスクリプトとは別に作成）、
`git show HEAD:claude_memo.html`（変更前）と現在のファイル（変更後）を
比較した。

### JS 挙動（字幕トグル・音声エンジン切替・速度巡回・プレイリスト件数・
`slideStartTimes`）

1280x900 で、変更前後それぞれ 68 行の記録を取り、`diff` は**完全に一致**
（終了コード 0）。実装報告の「68 行が完全一致」を再現できた。

### レイアウト（矩形測定）

`#viewport-stage` / `#viewport-frame` / `#player-viewport` /
`#subtitle-banner` / `#slide-canvas` を、3 状態（通常・字幕表示・擬似
フルスクリーン）× 3 サイズ（1280x900 / 768x1024 / 390x844）で測定した。

- **`#player-viewport` の矩形は 1280x900・768x1024 とも変更前後で完全一致**。
  差分は `max-width` の計算値が `100%` → `none` になった行だけで、実装報告と
  一致する
- **`#slide-canvas` の矩形が、768x1024 と 390x844 で変更前後の間に差が出た**
  （例: 768x1024 の `normal` 状態で
  `rect=55.64,155.14,650.72,307.35` → `rect=49.00,152.00,664.00,313.63`）。
  ただし、**同じ変更前ファイルを 2 回続けて測定しても同じ幅で差が出た**
  （`rect=32.41,95.59,429.18,215.06` と `rect=28.03,93.39,437.94,219.45` の
  2 通りがランダムに出る、390x844 で確認）。つまりこの差は変更の前後で
  出るのではなく、**同一ファイルの実行ごとに起きるゆらぎ**で、フォント
  読み込みのタイミングなど計測方法側の要因と見られる。今回の diff が
  原因ではない、という判断まではできたが、**実装報告の「全 45 行が
  完全一致」をそのままは再現できなかった**（自分の実測では `player-viewport`
  は一致、`slide-canvas` は不一致が出た）。実装者側の計測がたまたま
  ゆらぎに当たらなかった可能性がある

この点は判断が要る。「揺らぎだから問題ない」という私の解釈自体は、
同一ファイルの再実行でも差が出ることを確認した上のものだが、上位の
判断者が別の方法（実機、あるいは `--deterministic-fetch` 等でフォント
読み込みを固定した再計測）で詰めるかどうかは管理者の判断に委ねる。

## 6. 既存コメントとの食い違い

- `L1854` のコメント「同じ条件を CSS の @media にも書いてあるので、片方を
  変えたら両方直すこと」: CSS 側は実際に 1 か所（L184）になっており、
  文言も「2 か所」→ 数を明示しない表現に直っていて食い違いは無い
- 統合した `@media` ブロック内のコメント（暗幕・`fs-lock` の説明、
  `#viewport-frame` の説明）は、実装報告どおり L178-179 と L198-201 へ
  移設されており、指している内容とも一致する

## 確かめられなかったこと

- 実機（スマホ・タブレット、`pointer: coarse`）での見た目は確認していない
  （実装報告と同じ制約）
- `#slide-canvas` の矩形のゆらぎの原因がフォント読み込みなのか他の要因
  なのかは、ソースコードを読んで特定するところまではやっていない
  （計測を繰り返してゆらぎの存在を確認しただけ）
