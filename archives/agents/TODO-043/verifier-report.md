# TODO-043 検証報告（verifier）

コードは変更していない。確認のみ。

## 1. 移し漏れ・変質の照合

`git show HEAD:CLAUDE.md`（移す前）と、縮めた `CLAUDE.md` + 新規
`docs/Developer.md` を突き合わせた。TODO 番号が落ちているのは意図どおり
なので対象外。

- 「構成」「中身」「触るときの注意」の各事実は、`docs/Developer.md` に
  すべて残っている（1 項目ずつ突き合わせて確認済み）。落ちている事実は無い。
- `#slide-category` の記述だけは意図的に落としている（後述 2 で妥当性を確認）。
- 落ちてはいないが**移す前から誤っていた記述**が 1 件、そのまま
  `docs/Developer.md` に持ち越されている（後述 2 の項目 8）。

## 2. 事実の照合（`player.html` / `tools/measure-duration.py` との突き合わせ）

一致（詳細は省略、該当行番号のみ記す）:

- `document.write` の位置（464〜467行）と、再生ロジックの `<script>` より先
  という記述 — 一致
- 進行バーが実時間（`deltaTime * playbackRate`、945行）で進み、1.4倍
  （`BASE_SPEED_MULTIPLIER`、494行）が読み上げ速度にだけ掛かる件 — 一致
- `duration` を待ち時間に使うのが消音中・`onerror`・`play()` 拒否のときだけ
  という件（719, 858, 874行） — 一致
- Web Speech の安全タイマー式 `textToSpeak.length / 4.5 / getEffectiveSpeed()`
  （`SPEECH_CHARS_PER_SECOND = 4.5`、516行、800行で使用） — 一致
- Online TTS の安全タイマー（`onloadedmetadata` の実長を優先、初期値は
  `duration`、`TTS_END_MARGIN_MS = 3000`（519行）を加算、867〜872行） — 一致
- 既定 `online`（523行）、`toggle-voice-engine-btn`（282, 595行）、
  `TTS_MAX_CHARS = 180`（521, 820行） — 一致
- 縮小経路のメディアクエリ `max-width: 767.98px, pointer: coarse`
  （192, 1301行）、`setupViewportScale()` が `--vp-scale` を入れる件
  （1296〜1327行）、`#viewport-frame` と `#player-viewport`（960x540）の
  関係（193〜225行） — 一致
- `#viewport-stage.is-fullscreen` と `100dvh`／`vh` の行が両方残っている件
  （129, 136〜139行） — 一致
- `body.fs-lock` と暗幕の条件（幅768px未満または `pointer: coarse`、
  242, 249行）、暗幕タップで抜けるハンドラが `e.target === stage` に
  限っている件（1217行） — 一致
- `initPlaylist()` が `total-slides` / `playlist-count` / 総時間を埋める件
  （1004〜1006行）、`total-time-display` の初期値 `--:--`（368行） — 一致

**食い違い（1件）**

8. `docs/Developer.md` の「字幕バナーだけは枠の外」節にある
   `margin: 1px は #player-viewport の 1px ボーダーを打ち消す値` という記述は、
   現在の `player.html` と一致しない。`#subtitle-banner` に `margin: 1px` は
   存在せず、`mt-3`（通常表示）と `top: 100%`（フルスクリーン中）に置き換
   わっている。`git log -S"margin: 1px"` で追うと、2026-09-18 の
   TODO-035（コミット a5480ef「字幕を全文表示し、枠の下へ流す」）で
   この `margin: 1px` の指定自体が削除されている。
   **この誤りは TODO-043 の移し替えで生じたものではなく、移す前の
   `CLAUDE.md` に既にあった古い記述をそのまま写した**（`git show HEAD:CLAUDE.md`
   にも同じ文言がある）。TODO-043 の作業自体の問題ではないが、内容としては
   現状と食い違っているので報告する。

**`#slide-category` を落とした判断について**

移す前の `CLAUDE.md` には「枠の上の `#slide-category` と `SLIDE nn / 17` は
390px 幅で 4.5〜5.2px になる」とあったが、`docs/Developer.md` では
「枠の上の `SLIDE nn / NN` は 390px 幅で 5px 前後になる」とだけ書き、
`#slide-category` を落とし、数値も「5px 前後」に丸めている。
`player.html` を `grep -n "slide-category"` で検索したが該当箇所は無く、
`id="slide-num"` と `id="total-slides"` のみ存在する（312行）。
**この判断は妥当。** `#slide-category` という要素は現状の `player.html` に
無い。

## 3. リンクの確認

- `CLAUDE.md` → `docs/Developer.md`、`docs/Usage.md` ともに実在（`ls docs/`
  で確認）
- `docs/Usage.md` → `Developer.md`、`docs/Developer.md` → `Usage.md` の
  相互リンクも実在するファイルを指している
- `docs/Usage.md`・`docs/Developer.md` に `TODO-` の文字列は無い
  （`grep -rn "TODO-" docs/*.md` で 0 件）

## 確かめられなかったこと

- 実際にブラウザで `player.html` を動かして目視での挙動確認はしていない
  （静的な記述とソースコードの突き合わせのみ）。
- 上記「食い違い（1件）」の扱い（このタイミングで直すか、別項目にするか）は
  管理者の判断が要る。
