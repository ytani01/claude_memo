# TODO-023 verifier report

## 1. 差分の範囲

`git diff claude_memo.html` のハンクは 1 個のみ:

```
@@ -512,34 +512,37 @@
```

行 512〜548 付近（`slideData[1]`, `// Slide 2` の要素）に収まっている。
`git diff claude_memo.html | grep -c "playlist-count"` → `0`（差分無し）。
他のスライド（`id: 1`, `id: 3`〜`id: 17`）や再生ロジックへの差分も無い。

## 2. slideData.length と duration 合計

`id:` は 1〜17 の 17 個（`grep -n "id: [0-9]*,"` で確認、`id: 17` が最後）。

各 `duration` の値:
`18, 19, 19, 19, 21, 19, 19, 19, 18, 20, 21, 15, 17, 17, 17, 17, 22`

合計 = **317**（`python3 -c "print(sum([...]))"` で算出。17 個の要素数とも一致）。

## 3. スライド 2 の duration とナレーション実測

- `slideData[1].duration` = 19
- narration: `このあとの流れです。まず常時稼働させている利用環境、次に日常の対話のしかたと設定の考え方、そして最も重要な TODO.md によるタスク管理、さらにマルチエージェントでの役割分担、最後に現状の課題とまとめ、という順にご紹介します。`
- `prepareSpeechText()` は `TODO.md` → `トゥードゥー ドット エムディー` の置換のみが該当（他の置換パターンは本文に含まれない）。置換後 `.substring(0,180)` は 124 文字（180 未満のため全文がそのまま渡る）。
- `curl --referer '' -A 'Mozilla/5.0' "https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q=<urlencode>"` で取得した mp3（210KB, MPEG ADTS v2 64kbps 24kHz）を `ffprobe` で計測:
  ```
  ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 slide2.mp3
  26.256000
  ```
- 26.256 / 1.4 = 18.754… → 四捨五入で **19**。`duration: 19` と一致。
  依頼文にある main の実測（26.256 秒）とも一致した。

## 4. 表示崩れの実測（Playwright）

`#slide-canvas` 描画後、`#next-btn` をクリックしてスライド 2 へ移動。
`#slide-canvas` の矩形と、カード 4 枚（`.grid > div`）・
「5. 現状の課題とまとめ」の行（`.mt-[1.5cqw]` 要素）の矩形を比較し、
`right/bottom/left/top` それぞれのはみ出し px を計測。

計測条件と結果（すべて `overflowRight/Bottom/Left/Top` = 0 px、5 要素全て）:

| 条件 | canvasRect (l,t,w,h) | カード4枚+行のはみ出し |
|---|---|---|
| PC 1280x800（タッチ無し・通常） | 49, 152, 868, 428.4 | 0px（全方向・全5要素） |
| 横持ち 844x390（タッチ有り・通常） | 168.4, 124.1, 507.2, 251.9 | 0px（全方向・全5要素） |
| 横持ち 844x390（タッチ有り・フルスクリーン） | 93.4, 45.5, 657.2, 326.4 | 0px（全方向・全5要素） |
| 縦持ち 390x844（タッチ有り・フルスクリーン） | 10.2, 336.3, 369.7, 185.3 | 0px（全方向・全5要素） |

いずれの条件でもカード・行の矩形は `#slide-canvas` の矩形内に完全に収まっている
（はみ出し 0 px）。

補足: `fullscreen-btn` と `next-btn` は `page.click()` だとフルスクリーン時に
`<h1>` 等が pointer イベントを奪って 30 秒タイムアウトしたため、
`page.evaluate(() => el.click())` で直接クリックイベントを発火させて回避した
（クリック手段を変えただけで、測定対象のレイアウトには影響しない）。

## 5. 変更前との比較

`git show HEAD:claude_memo.html` を別ファイルに出し、同じ 4 条件・同じ計測方法で
スライド 2（HEAD 版は「主なコマンド一覧」の 4 カードのみ、5 番目の行は無し）を測定。
結果は 4 条件すべて、カード（HEAD は 4 枚）のはみ出しが 0 px。

→ 変更前・変更後とも、はみ出しは 0 px。**はみ出しが増えていない**
（両方ゼロなので差分もゼロ）。

## 検証コマンド・終了コード

- `git diff` 系コマンド: すべて終了コード 0
- `curl` + `ffprobe`: 終了コード 0、mp3 取得・秒数取得に成功
- Playwright 計測スクリプト（`/tmp/verify064/measure_todo023.js`、
  `chromium.launch()` を使用、対象リポジトリの `node_modules` には
  playwright が無かったため既存の `/tmp/verify064/node_modules/playwright`
  を使って実行）: 新版・HEAD 版とも 4 条件で正常終了（終了コード 0、
  クリックを `evaluate` 経由に変更した後はタイムアウト無し）

## 確かめられなかったこと・判断が要る点

- 依頼文にある「main の実測は 1.0 倍で 26.256 秒」との一致は数値上確認できたが、
  Google Translate TTS の音声合成結果は実行タイミングやサーバ側の実装で
  変動する可能性があり、将来同じ手順を再実行して秒数が変わっても
  それ自体は本項目の不備ではない（参考情報として記載）。
- レイアウトの目視確認（実際のブラウザでの見た目）は行っていない。
  矩形の重なり計算のみで判定した。CSS の視覚的な崩れ（文字の potentially
  overlapping look, 色, フォントサイズの見え方など）は確認していない
  （依頼の確認事項が「はみ出し px」に限定されているため、それ以上は
  reviewer 側の担当と判断した）。
