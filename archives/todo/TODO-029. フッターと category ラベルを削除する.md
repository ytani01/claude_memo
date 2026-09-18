# TODO-029. フッターと category ラベルを削除する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 9,278 | 21,331 | 75% |
| verifier | Sonnet 5 | medium | 10,555 | 43,686 | 25% |
| 合計 |  |  | 19,833 | 65,017 | 概算 $1.5 |

- verifier は定義（`~/.claude/agents/verifier.md`）のまま（sonnet / medium）
- 集計は `--since '2026-09-18 18:40:42'`（項目を立てたコミットの時刻）で切った。
  立てたコミットのメッセージが `TODO-025〜029` なので、番号では範囲を切れない。
  この範囲には TODO-025 の下準備（`duration` の測定スクリプトと
  スライド 2 のナレーション案の実測）も少し混ざっている

## きっかけ

プレゼンテーションとしての全体レビューで、どちらも視聴者の役に立っていないと
分かった。

- **`category`**（`CLAUDE CODE WORKFLOW` など）は日本語のプレゼンに英語で、
  かつ 390px 幅では 4.5〜5.2px にしかならない。`CLAUDE.md` 自身が
  「補助的な情報なので、読めなくてよいものとして残している」と書いていた
  （TODO-001）
- **フッター**の `Claude Code Interactive Presentation Video © 2026 |
  Audio-Synced Presentation Engine` は、視聴者に関係のない自己言及

## やったこと

`claude_memo.html` の 4 か所を消した（1 insertion / 29 deletions）。

1. **枠の上のヘッダー**から `#slide-category` の span と、その隣の
   パルス点（`animate-pulse` の緑の丸）を削除。ラベルが無くなると点だけが
   残って意味を成さないため、一緒に消した。残った `SLIDE nn / 17` が
   左に寄らないよう、親の flex を `justify-between` → `justify-end` にした
2. **`<footer>`** を丸ごと削除
3. **JS** の `slideCategory` の取得と `slideCategory.textContent = slide.category;`
4. **`slideData`** 全 17 要素の `category: '...',`

ナレーションは変えていないので、`duration` は測り直していない。

## 確かめたこと

verifier が Playwright（chromium, headless）で、変更前（`git show HEAD:`）と
変更後をそれぞれローカル HTTP サーバーに載せて比較した。15 項目すべて通過。
報告は `archives/agents/TODO-029/verifier-report.md`。

- `category` / `footer` の語は `claude_memo.html` に 0 件
- コンソールのエラーは、機能テスト中も再生のスモークテスト中も 0 件
- スライドは 17 枚。`next` を 16 回で 17 まで進み、最後で止まり、
  `prev` を 16 回で 01 まで戻る
- `SLIDE nn / 17` はヘッダー行の右端との差 0.0px（左端とは 712.0px）で、
  右寄せのまま
- はみ出しは 4 条件すべてで悪化なし。PC 1280x800 と縦持ち 390x844
  フルスクリーンは前後とも 0px。横持ち 844x390 は通常が 926 → 885px、
  フルスクリーンが 466 → 425px と、フッターが無くなった分 41px 減った

## 残ること

- **フルスクリーンは近似でしか測っていない。** headless chromium では
  Fullscreen API を再現できないため、verifier は `fullscreen-btn` の
  クリックで代用した。変更前後を同じ方法で比べているので相対比較としては
  有効だが、実機のフルスクリーンでの絶対値は未確認
- **見た目の印象は見ていない。** 矩形のはみ出しだけで、ヘッダー行が
  右端の 1 要素だけになったバランスは実機で見ていない

## 分担の振り返り

- **verifier は「壊れていないこと」を数字で示したが、指摘は出さなかった。**
  15 項目すべて通過で、直すべき点は 0 件。横持ちの overflowY が 41px
  減ったことを実測で出してきたのは、フッター削除の副作用の裏付けになった
- **見込み（verifier 1 人）と食い違わなかった。** 削除だけで分岐も条件式も
  変わらないため、実装を分けず main が直接書き、レビューも立てなかった。
  これで足りた
- **次に同じ規模（表示要素の削除だけ）をやるなら、同じく verifier 1 人でよい。**
  ただし今回 verifier の cache_creation が 43,686 と main より多い。
  変更前後の 2 本のサーバーを立てて Playwright を組ませた分で、
  **同じ「前後比較」を次もやるなら、そのスクリプトを捨てずに
  `archives/agents/` へ残して使い回させる**（毎回組ませると同じ額がかかる）
