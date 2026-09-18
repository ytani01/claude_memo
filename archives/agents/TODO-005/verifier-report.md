# TODO-005 verifier report

## 検証環境
このプロジェクトはビルド・自動テストが無い 1 ファイルの静的 HTML。
`chromium --headless` で `claude_memo.html` のコピー（末尾に計測用
`<script>` を追記したもの）を読み込み、DOM 操作の結果を `--dump-dom` で
拾って確かめた。元ファイルは変更していない。

- コピー先: `/tmp/claude-649/.../scratchpad/verify_copy.html`,
  `verify_fs.html`, `verify_toggle2.html`（セッション終了で消える一時領域。
  リポジトリには残っていない）
- 実行例:
  `chromium --headless --disable-gpu --no-sandbox --window-size=1280,800 --virtual-time-budget=5000 --dump-dom "file://<コピー>"`
- 試した窓幅: 1280x800（PC）、500x900（chromium の最小幅。768px 未満の
  経路に入ることは確認できたが、実機の 390px 相当は測れていない。後述）

## git status / git diff
`git status` は `claude_memo.html` の変更のみ（他ファイルの変更なし）。
`git diff` は下記 3 箇所のみで、指示の範囲と一致している。
- CSS の `#tap-feedback-icon` / `.is-shown` / `@keyframes tapFeedback`
- `#player-viewport` 内、`#slide-canvas` の直後に追加した
  `pointer-events-none` の div と `<i id="tap-feedback-icon">`
- `setupEventListeners()` 内、`#player-viewport` の click ハンドラの追加

余計な変更は見当たらなかった。

## TODO-005 のチェック項目（3 件とも実測で確認）

1. **クリック / タップで `togglePlay()` を呼ぶ** — 確認できた。
   `#player-viewport` を `click()` すると再生⇄一時停止の状態
   （`#play-icon` の `fa-pause`/`fa-play` で判定）が毎回反転した。
   通常表示（1280x800）・フルスクリーン状態の両方で確認。

2. **切り替えたとき、中央に ▶ / ‖ を一瞬出す** — 確認できた。
   1 回目クリック（再生開始）で `#tap-feedback-icon` のクラスが
   `fa-solid fa-play is-shown`、2 回目（一時停止）で
   `fa-solid fa-pause is-shown` になった。3 回連続クリックでも毎回
   `is-shown` が付き直ることを確認（`offsetWidth` 読み出しによる
   reflow でアニメーションが再トリガーされている）。
   ```
   classes_click1: "fa-solid fa-play is-shown"
   classes_click2: "fa-solid fa-pause is-shown"
   classes_click3: "fa-solid fa-play is-shown"
   ```
   「今再生中なら ▶、今一時停止なら ‖」という向きは、既存の
   `#play-icon`（再生ボタン内のアイコン。再生中は次にできる操作を示す
   `fa-pause` になる）とは逆向きだが、動画プレイヤーで一般的な
   「アクションの結果」を示す向き（再生開始→▶、一時停止→‖）と一致しており、
   意図どおりと判断した。

3. **スマホのフルスクリーンでタップが効くこと・暗幕で抜けられること** —
   確認できた。500x900 の窓（chromium が取れる最小幅。767.98px 未満の
   CSS 経路には入っている）でフルスクリーンボタンを押した状態から:
   - `#player-viewport` を click → 状態が反転し、フルスクリーンは
     維持されたまま（`is-fullscreen` 継続）
   - `#viewport-stage` 自身を `target` にした click（枠の外＝暗幕相当）→
     フルスクリーンが解除された
   ```
   is_fullscreen_after_btn: true
   toggled_in_fs: true
   still_fullscreen_after_viewport_click: true
   fullscreen_after_stage_click: false
   ```

## 干渉の確認
- `#player-viewport` の子要素として `#play-btn` / `#seekbar-container` /
  `#playlist-items`（チャプター一覧）は含まれていない
  （HTML 上、`#player-viewport` は 324〜352 行、これらは 406 行以降の
  別ブロック）。よって新しい click ハンドラのバブリングとは無関係で、
  `#play-btn` を click しても状態は 1 回だけ反転することを確認した
  （`playBtn_click_toggles: true`）。
- 暗幕のハンドラ（`#viewport-stage` の click、`e.target === stage` の
  ときだけ反応）はこの diff では変更されておらず、上記の実測でも
  クリック位置の判定は従来どおり効いていた。

## `pointer-events-none` の遮りの確認
1280x800 で `#player-viewport` の中心に対して `document.elementFromPoint`
を取ったところ、返ってきたのはスライド本文側の要素（`H1`）で、
`#tap-feedback-icon` や、それを包む div ではなかった
（`elAtCenter_is_icon_or_wrapper: false`）。オーバーレイが枠内のクリックを
塞いでいないことを確認した。

## 768px 未満でのアイコンの大きさ（cqw と `--vp-scale` の掛かり方）
- `#tap-feedback-icon` はコンテナクエリの起点である `#player-viewport`
  自身の子孫にある。767.98px 未満では `#player-viewport` は
  `width: 960px` 固定＋`padding: 1.5rem` になり、`transform: scale(var(--vp-scale))`
  で縮小表示される。コンテナクエリのサイズ判定は transform 前の
  レイアウト幅（960px から padding を引いた分）を基準に解決されるため、
  `getComputedStyle` で読める `font-size` は常に 960px 基準の値
  （実測 81.9px、`clamp(28px, 9cqw, 96px)` の 9cqw 側で頭打ちにはならず
  素直に解決された値）になる。この値は他のスライド本文の cqw 指定と
  同じく、実際の見た目は `--vp-scale` でさらに比例縮小される
  （CSS のコメントにもその設計意図が書かれている）。
- **実測できた最小窓幅は 500px**（chromium ヘッドレスの制約。指示にも
  記載あり）。500px 幅では `--vp-scale` は概ね 0.48 程度になり、
  アイコンの見た目のサイズは 40px 弱と計算できた。実機の 390px 幅
  相当（`--vp-scale` 約 0.41）は実測できておらず、比例計算での推定に
  留まる。クランプの下限 28px は「transform 前の」font-size にしか
  掛からないため、非常に狭い画面では見た目のアイコンが 28px を
  下回りうる。これは既存の 960x540 固定→scale という設計（TODO-001）と
  同じ振る舞いであり、この diff 固有の問題ではないと考えるが、
  「小さすぎて見えない」水準になるかどうかは実機での目視確認が要る
  （判断できない点）。

## 判断できなかったこと・確かめられなかったこと
- 実機の縦持ちスマホ（390px 幅程度）でのアイコンの実際の見た目の
  大きさ。ヘッドレス chromium の窓幅下限（500px）により直接測れず、
  比例計算での推定にとどまる。
- ▶ / ‖ の向き（「今の状態」を示すか「これからできる操作」を示すか）が
  利用者の意図と一致しているかは、コードとしては一貫しているが、
  好みの問題であり判断できない。
