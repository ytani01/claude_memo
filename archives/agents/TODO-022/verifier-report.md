# TODO-022 verifier 報告

## 走らせた検証

1. `git diff -- claude_memo.html` の全文確認（60 行、全て目視）
2. `grep -n "speed-btn\|speedBtn\|speedOptions\|baseSpeedMultiplier"` で旧実装の残骸を確認
3. `<script>` を切り出しての `node --check`
   - 結果: 成功（終了コード 0、`OK` 出力）
4. Playwright（Chromium, headless, `python3` + `playwright.async_api`）で
   `file://.../claude_memo.html` を開き実測。スクリプトは scratchpad に置き、
   リポジトリには残していない
   - 結果: 全項目成功（終了コード 0、例外無し）

## 完了条件ごとの実測結果

1. **`speed-btn` が `#speed-select` になっている**
   - `speed-select exists: True`, `speed-btn exists: False`
   - `grep` でも `speedBtn` / `speed-btn` / `speedOptions` の残骸は無し（ヒット無し）

2. **選択肢は 0.75 / 1.0 / 1.25 / 1.5 / 2.0 の 5 段階、既定は 1.0**
   ```
   OPTIONS: [{'value': '0.75', 'text': '速度 0.75x', 'selected': False},
             {'value': '1', 'text': '速度 1.0x', 'selected': True},
             {'value': '1.25', 'text': '速度 1.25x', 'selected': False},
             {'value': '1.5', 'text': '速度 1.5x', 'selected': False},
             {'value': '2', 'text': '速度 2.0x', 'selected': False}]
   default playbackRate JS var: 1
   ```
   5 段階・既定 1.0 を確認。0.9 と 1.75 は含まれていない。

3. **並びは左が速度、右が待ち。ラベルの調子が揃っている**
   - DOM 上の兄弟要素の並び（id）:
     `['toggle-caption-btn', 'speed-select', 'pause-select', 'mute-btn', 'fullscreen-btn']`
     → speed-select が pause-select より先（左）
   - ラベル文字列（`grep` 実測）:
     `速度 0.75x` / `速度 1.0x` / `速度 1.25x` / `速度 1.5x` / `速度 2.0x`
     `待ち 1秒` / `待ち 2秒` / `待ち 3秒`
     → 「◯◯ 値+単位」の調子で揃っている（間に半角スペース 1 つ）

4. **選ぶと `playbackRate` が変わり、再生中なら読み上げがやり直される**
   - `<select>` を `1.5` に変更 → `playbackRate after selecting 1.5: 1.5`（変わった）
   - `speakCurrentNarration` にスパイを仕込んで検証:
     - `isPlaying = false` の状態で `2` に変更 →
       `speakCurrentNarration calls when NOT playing: 0`（呼ばれない）
     - `isPlaying = true` にしてから `0.75` に変更 →
       `speakCurrentNarration calls after setting isPlaying=true and changing: 1`（1 回呼ばれた）
       `playbackRate final: 0.75`

5. **選んだ値を保存していない**
   - `localStorage keys: []`（操作前後とも空、`pause-select` と同様に保存していない）
   - コード全体を `grep -n "localStorage"` した結果もヒット無し

## 変更ファイルと範囲

- `git status` / `git diff` で変更されているのは `claude_memo.html` のみ。
  TODO-022 の対象範囲（`claude_memo.html` の未コミット差分）と一致している。
- 差分は以下の 3 箇所のみ（全て目視確認済み）:
  - HTML: `speed-btn` の `<button>` を削除し、`<select id="speed-select">` を
    `pause-select` の手前（左）に追加
  - JS 変数宣言: `speedBtn` → `speedSelect`
  - イベントハンドラ: `click` による循環ロジック（`speedOptions` 配列・
    `indexOf` での次候補計算・`textContent` 更新）を削除し、
    `change` イベントで `Number(speedSelect.value)` を代入する形に置き換え
- 指示に無いファイルの変更は無い。

## 確かめられなかったこと・判断できないこと

- 実際のブラウザ（Chromium 以外、特に Android Chrome）での見た目・操作感は未確認
  （TODO-022 の完了条件には含まれていないため対象外とした）。
- CSS の見た目（幅・折返しなど）は目視でのみ確認、レイアウト崩れの有無は
  スクリーンショット等では確かめていない。指示に画面サイズの確認は無かったため
  実施していない。判断が必要なら追加で実測する。
