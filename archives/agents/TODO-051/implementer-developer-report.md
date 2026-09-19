# TODO-051 実装報告（implementer-developer）

## 変更したファイル

- `slides/developer.js`（新規作成）— `docs/Developer.md` をもとにした
  11 枚のスライド。`deckConfig`、`slideData` の形は `slides/claude-memo.js` を
  手本にした。

## スライド一覧（何を載せたか）

1. タイトル — `player.html` を直す人へ。対象読者と Usage.md との住み分け
2. リポジトリの構成 — `player.html`/`slides/`/`tools/measure-duration.py`、
   ビルド不要・CDN 依存
3. 置き場所は選ばない — 相対パスは 1 か所だけ、同じディレクトリに置けば
   `public_html/` の外でも動く、ネット接続は必須
4. 全体の作り — HTML → slideData → 再生ロジックの 3 段、`document.write` の
   読み込み順は入れ替え不可
5. 再生ロジック — スライド送りは読み上げ終了イベントで起きる、
   `BASE_SPEED_MULTIPLIER` を時間軸に掛けない
6. `duration` は実測値 — Online TTS の実測秒数、置換表を直したら
   `measure-duration.py` で測り直す
7. 読み上げの 2 系統 — online（既定）/speech の実装と制限、安全タイマー
8. **触ると鳴らなくなるもの**（3 点、Developer.md の要注意事項を全部残した）—
   Audio 要素の使い回し、Web Speech の分割、`no-referrer` を外さない
9. レイアウト — `cqw`/`clamp()`、幅 768px 未満とタッチ画面の別経路、
   字幕バナーは枠の外
10. 直書きしない値 — `SLIDE nn / NN` と `total-time-display` は自動で埋まる
11. まとめ — 上記の要点を 3 行に集約、詳細は `archives/todo/` へ誘導

## 落とした内容（意図して省いたもの）

- 擬似フルスクリーンの `100dvh` の理由、`body.fs-lock` と暗幕の 3px のずれ、
  暗幕の帯が 16:9 ちょうどで 0px になる話 — レイアウトの節に要点だけ残し、
  条件式の細部は Developer.md 側に譲った
- `tools/test_measure_duration.py` の存在、`splitForSpeech()` の `maxLen` の
  既定値、`TTS_END_MARGIN_MS`・`SPEECH_CHARS_PER_SECOND` などの定数名
- 「触ると鳴らなくなるもの」は 3 点とも落とさず載せた（指示どおり）

## 検証

- `node --check slides/developer.js` → 構文エラー無し（`OK_SYNTAX`）
- `python3 tools/measure-duration.py --deck developer --all`（`--write` 無し）
  → 11 枚全部でナレーションを拾えた。落ちたスライドは無い。
  実測 duration（倍速後）はスライド順に
  12, 15, 15, 16, 12, 12, 12, 13, 14, 9, 14 秒。
  ファイルに仮で入れた値（文字数 ÷ 7 四捨五入）との差は最大 3 秒
  （スライド 2 の 17→15、スライド 9 の 13→14 など）。
  **`--write` は指示どおり付けていない。** 実測値への書き戻しは main が行う想定。

## 判断が要る点・懸念

- 特になし。`docs/Usage.md` の書式規約（`cqw`/`clamp()`、`md:` 不使用、
  コード例で `duration:` の次行に `narration:` を続けない）はすべて守った。
