# TODO-022. 再生速度をプルダウンで選べるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + reviewer |
| 実施 | Opus 5 / effort high | verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 8,682 | 16,454 | 64% |
| reviewer | Sonnet 5 | high | 17,959 | 56,111 | 27% |
| verifier | Sonnet 5 | medium | 4,851 | 28,600 | 9% |
| 合計 |  |  | 31,492 | 101,165 | 概算 $1.8 |

- 担当は 2 つとも定義のまま（`~/.claude/agents/`）

## きっかけ

再生速度がボタンのクリックで 0.75 → 0.9 → 1.0 → 1.25 → 1.5 → 1.75 → 2.0 と
循環する作りで、目当ての速度まで何度も押すことになっていた。TODO-021 で待ち
秒数をプルダウンにしたので、そちらと揃える。

決めたこと（2026-09-18）:

- 選択肢は 0.75 / 1.0 / 1.25 / 1.5 / 2.0 の 5 段階、既定は 1.0（0.9 と 1.75 は落とす）
- 並びは左が速度、右が待ち
- 選んだ値は覚えない（待ち秒数と揃える）

## やったこと

`claude_memo.html` のみ。

- `#speed-btn`（`button`）を `#speed-select`（`select`）に置き換え、字幕ボタンの
  右、待ち秒数のプルダウンの左に置いた。クラス指定は `#pause-select` と同じ
- ラベルは「速度 0.75x」「速度 1.0x」…「速度 2.0x」。待ち側の「待ち 2秒」と揃えた
- 循環のロジック（`speedOptions` の配列と `indexOf`）と、ラベルを組み立てる
  コードを消した。`change` で `playbackRate` に入れ、再生中なら
  `speakCurrentNarration()` を呼び直すだけになった

## 確かめたこと

verifier と reviewer が Playwright（Chromium, headless）で実測した。

- 選択肢は 5 つ、既定は 1.0。`speedBtn` / `speed-btn` の残骸は無い
- 選ぶと `playbackRate` が変わる（1.25 を選んで `playbackRate` 1.25、
  `getEffectiveSpeed()` 1.75 を実測）
- `localStorage` などへの保存は無い
- `0.9` と `1.75` に戻る経路は他に残っていない
- `<script>` を切り出しての `node --check` が通る

要修正は 0 件。Online TTS の音声を実際に鳴らしての確認は行っていない。

## 分担の振り返り

分担は `archives/agents/TODO-022/README.md`。

- **どちらも指摘は出なかった。** reviewer は「落とした 0.9 / 1.75 に戻る経路が
  他に無いか」を実測で潰しており、これは差分を読むだけでは断定できない点
  だった。verifier は完了条件どおりの確認で、こちらは短時間で済んでいる
- **見込みとの差**: 見込みどおり 1 巡。TODO-020 と同じく、依頼文に
  「playwright が使える」と書いたので最初から実測して返ってきた
- main が料金の 64% と重いが、これは会話が長くなったぶん（`cache_read` が
  170 万）で、この項目の実装そのものは小さい
- **次に同じ規模なら**: 既存の UI を 1 つ置き換えるだけの項目なら、
  verifier は今回のように軽く、reviewer に「落としたものの後始末」を
  名指しで見させる形でよい。担当は減らさない
