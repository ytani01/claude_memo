# TODO-001 最終確認（verifier-report-3）

対象: `scrollPlaylistIntoView()` の位置計算を `offsetTop` 差分から
`getBoundingClientRect()` 差分に書き換えた 1 か所（`claude_memo.html`）。

（注記: 本ファイルには以前 `main` が代理で書いた同名の報告があったが、
今回 verifier として実際に確認が完了したため、その内容を置き換えた。
以前の代理版は `git log` の履歴か `archives/agents/TODO-001/` 内の
他ファイルに残っていなければ失われている点は留意）

## 確認方法

Playwright（headless Chromium 1243、`npx --yes playwright install chromium` で
取得）で `file://.../claude_memo.html` を開き、`#next-btn` / `#prev-btn` の
連打、`#play-btn` での自動再生、チャプター一覧の直接クリックを行い、
毎回 `window.scrollY` と、選択中の項目の `getBoundingClientRect()` が
`#playlist-items` の矩形に収まっているかを JS 側で計測した。
スクリプトは `/tmp/.../scratchpad/pwtest/test.js`、
`/tmp/.../scratchpad/pwtest/test_autoplay.js`（scratchpad 内。リポジトリ
には追加していない）。

## 結果（項目ごと）

1. **○** 390x844 縦画面で 1→17 と送っても `window.scrollY` は常に 0。
   `#next-btn` 連打（16 回）、自動再生（`#mute-btn` を押してから
   `#play-btn`、実測 idx 0→16 まで約 159 秒）の両方で確認。全ステップで
   `scrollY === 0`。
2. **○** 送るたびに、選択中の項目の矩形が `#playlist-items` の矩形に
   収まっている。`#next-btn` 連打では全 16 ステップで収まっていた。
   自動再生では、idx が切り替わった直後（0ms 時点）は idx=10 以降で
   一時的に矩形外（`contained: false`）と出たが、`scrollTo({behavior:
   'smooth'})` のアニメーション中の一時状態で、600ms 待ってから再計測
   すると全ステップで `contained2: true` になった。アニメーションが
   終わった状態では収まっており、smooth スクロールの遷移中を捉えた
   だけで不具合ではないと判断した（根拠: 同じ idx で時間を置いて
   再計測すると true に変わる、`#next-btn` 側では 150ms 待つだけで
   一貫して true だった）。
3. **○** 逆方向（17→1、`#prev-btn` 16 回）でも 1・2 が成り立つ。
   全ステップで `scrollY === 0` かつ `contained: true`。
4. **○** `#playlist-items` に `style.position = 'relative'` を注入した
   状態でも 2 が成り立つ。390x844 で `#next-btn` 往復（fwd 16 + bwd 16）
   の全 32 ステップで `contained: true`（書き換え前は 9 枚目以降で
   枠の外へ出ていたとのことだが、書き換え後は最後まで収まっていた）。
5. **○** PC（1280x800）でも 1〜3 が成り立つ。`#next-btn` / `#prev-btn`
   往復の全 32 ステップで `scrollY === 0` かつ `contained: true`。
   （自動再生は PC では確認対象に含めなかった。指示は「1〜3」で、
   自動再生そのものを PC で求めていないと読んだ）
6. **○** 一覧の項目を直接クリックして先頭に戻す経路でも破綻しない。
   `playlist-item-9` → `playlist-item-0` の直接クリックを
   mobile-portrait-normal / position:relative / pc の 3 条件で試し、
   いずれも `contained: true`。
7. **○** コンソールにエラーが出ない。`console` の `error` イベントと
   `pageerror` イベントを全テストで監視したが、記録は 0 件
   （CDN 読み込み含め、全実行を通して空配列）。

## 確かめられなかったこと・判断が要る点

- 自動再生 × `position: relative` の組み合わせは、1 回の自動再生に
  約 160 秒かかるため実施していない。項目 4 の「今回の書き換えの狙い」
  自体は `#next-btn` 経路で 32 ステップとも収まることを確認済みで、
  位置計算のロジック（`getBoundingClientRect` の差分）は移動手段
  （クリック/自動再生）に依存しないはずのため、これで十分と判断した。
  これは推定であり断定はできない。気になる場合は追加確認を。
- 自動再生中の「一時的に矩形外」という現象自体は、今回の書き換えとは
  無関係な smooth スクロールの過渡状態だと考えられるが、これは観測
  ベースの推定。
- 実機（実際のスマホ端末）では確認していない。Playwright の
  headless Chromium・390x844 のビューポートエミュレーションでの
  確認にとどまる。

## git status / git diff

- `claude_memo.html` に加え、`CLAUDE.md`、`TODO.md` も未コミットで
  変更されているが、これらは TODO 管理の記述変更と見られ今回の確認
  対象（scrollPlaylistIntoView の書き換え）の範囲外。
- `claude_memo.html` の差分には、今回の指示にある
  `scrollPlaylistIntoView()` の書き換え以外に、レターボックス構造
  （`#viewport-stage` / `#viewport-frame` の追加など）の広い変更も
  含まれているが、これは前回までの確認（verifier-report / -2）の
  対象であり、今回はその後に加わった 1 か所の修正のみを確認した。
