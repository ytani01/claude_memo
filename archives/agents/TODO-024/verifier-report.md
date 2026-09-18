# TODO-024 確認担当報告

## 1. 構文チェック

```
sed -n '484,1998p' claude_memo.html > /tmp/x.js && node --check /tmp/x.js
```
→ エラー無し（終了コード 0）。

## 2. 置換前後の数値の一致（git diff を 1 箇所ずつ確認）

`git diff claude_memo.html` の全 hunk を確認した。以下は式の形（演算の順序・
括弧）が変わっていないことを、定数の値と突き合わせて確認した結果。

- `1.4` → `BASE_SPEED_MULTIPLIER`（`getEffectiveSpeed` 内、同じ掛け算の形）
- `1000` → `MS_PER_SECOND`（秒→ミリ秒換算、全 8 箇所とも `* 1000` の位置のまま）
- `60` → `SECONDS_PER_MINUTE`（`formatTime` の `/ 60`, `% 60`）
- `100` → `PROGRESS_MAX_PERCENT`（`Math.min(100, ...)` と `* 100` の 2 箇所、
  `Math.min` の引数順そのまま）
- `960` → `SLIDE_BASE_WIDTH_PX`、`16 / 9` → `SLIDE_ASPECT_RATIO`
  （`node -e "console.log(16/9)"` で `1.7777777777777777`。定数化しても
  同じ値が実行時に計算されるだけなので浮動小数点の丸めも変わらない）
- `2.0` → `MAX_SPEECH_RATE`（`Math.min(2.0, ...)` の 2 箇所とも）
- `0.95` → `WEB_SPEECH_RATE_FACTOR`、`0.85` → `WEB_SPEECH_PITCH`
- `50` → `SPEECH_START_DELAY_MS`（`setTimeout` の第 2 引数）
- `6000` / `4.5` / `3000` → `SPEECH_SAFETY_MIN_MS` / `SPEECH_CHARS_PER_SECOND` /
  `SPEECH_SAFETY_MARGIN_MS`（`Math.max(...)` の式は改行が入っただけで
  演算子の並びは同じ）
- `180` → `TTS_MAX_CHARS`
- 3 箇所の `... * 1000 + 3000` → `... * MS_PER_SECOND + TTS_END_MARGIN_MS`
  （加算の位置そのまま）

いずれも「リテラルを同じ位置の定数に置き換えただけ」で、演算子の追加・
削除・順序変更は無かった。改行を入れた箇所（`Math.max` や `Math.min` の
複数行化）も、JS の演算子優先順位は行分けの影響を受けないため問題ない。

## 3. 定数名と使われ方の対応

- `MS_PER_SECOND` は秒→ミリ秒換算にのみ使用（8 箇所）。他の用途への流用は無い。
- `MAX_SPEECH_RATE` は Web Speech と Online TTS 両方の `playbackRate`/`rate`
  上限に使われている。1 箇所専用ではないが、コメント通り「rate の上限」という
  同じ意味で使われており、命名として矛盾は無い。
- 他の定数（`SECONDS_PER_MINUTE`, `PROGRESS_MAX_PERCENT`,
  `SLIDE_BASE_WIDTH_PX`, `SLIDE_ASPECT_RATIO`, `WEB_SPEECH_RATE_FACTOR`,
  `WEB_SPEECH_PITCH`, `SPEECH_START_DELAY_MS`, `SPEECH_SAFETY_MIN_MS`,
  `SPEECH_CHARS_PER_SECOND`, `SPEECH_SAFETY_MARGIN_MS`, `TTS_END_MARGIN_MS`,
  `TTS_MAX_CHARS`）はいずれも 1 箇所ずつの使用で、名前と用途が一致している。

## 4. 旧名 `baseSpeedMultiplier` の残存

```
grep -n "baseSpeedMultiplier" claude_memo.html
```
→ 一致なし。コード・コメント（2 箇所）とも `BASE_SPEED_MULTIPLIER` に
揃っている。

## 5. 置換漏れの洗い出し（484〜1998 行、`slideData` の `id`/`duration` を除く）

`slideData` は 484〜1144 行。1145〜1998 行に残る数値リテラルを全て
目視で確認した。

**定数にすべきだったのに残っている可能性があるもの（判断が要る）:**

- `function splitForSpeech(text, maxLen = 40, minLen = 20)`（1292 行付近）
  — 発話を分割する際の文字数の閾値で、TODO の対象である「音声関連の数値」に
  近い性質を持つ。今回の diff には含まれておらず、定数化されていない。
  TODO 文には個別の列挙に `40`/`20` は挙がっておらず、「進行バーやミリ秒換算
  など、その他の数値も対象にする」という広い合意との整合性は判断できない
  （自明とまでは言えない数値なので、対象外にした理由が要ると考える）。

**自明として残してよいと判断したもの:**

- `let playbackRate = 1.0;` / `let pauseSeconds = 2;` — 変数名が意味を
  表しており、UI の初期値としての代入。マジックナンバーというより
  「初期状態」の値。
- `slideNum.textContent = String(slide.id).padStart(2, '0')` の `2` —
  2 桁ゼロ埋めという自明な書式。
- `SWIPE_MIN_PX = 50` — 既に名前付き定数（今回の diff の対象外、TODO-024
  着手前から存在）。
- ループや配列操作の `0`, `1`, `-1`（`currentIndex - 1` 等）— 自明な
  インデックス操作。

## 6. 変更ファイルの範囲

`git status` では `claude_memo.html` の変更のみ。指示の範囲（JS 部分の
マジックナンバー定数化）と一致している。`archives/agents/TODO-024/` は
本報告のための新規ディレクトリ。

## 確かめられなかったこと・判断が要る点

- `splitForSpeech` の `maxLen = 40` / `minLen = 20` を定数化対象に含める
  べきだったかは、TODO 文の個別列挙にこれらが無く、「その他の数値も対象」
  という記述との整合性を確認する必要がある。管理者の判断を仰ぎたい。
- ブラウザでの実際の読み上げ・進行バー描画などの実行時挙動は確認して
  いない（`node --check` は構文のみ）。diff の各式が数値として一致する
  ことは目視で確認済みだが、ブラウザ実行での再現テストは行っていない。
