# TODO-018 確認報告（verifier、2 回目）

対象: `git diff`（未コミット）— `CLAUDE.md` / `claude_memo.html`。**修正はしていない。**

## 1. `duration` の並び・合計

```
$ node -e '
const fs = require("fs");
const html = fs.readFileSync("claude_memo.html", "utf8");
const m = html.match(/const slideData = (\[[\s\S]*?\n        \]);/);
const slideData = eval(m[1]);
console.log(slideData.map(s => s.duration).join(","));
console.log("total=", slideData.reduce((a,s)=>a+s.duration,0));
'
18,19,19,19,21,19,19,19,18,20,21,15,17,17,17,17,22
total= 317
```

指示どおりの並び・合計と一致。**OK。**

## 2. 入れ替えたのは `duration` だけか

```
$ git diff -- claude_memo.html | grep -E '^[+-]' | grep -v '^[+-][+-][+-]' \
  | grep -vE 'duration:|total-time-display|playbackRate|getEffectiveSpeed|^\+ *//|^\+$'
-            // Advance time based on effective speed multiplier
```

`id` / `category` / `title` / `narration` / `render` に差分は無い。
`duration` 以外の実質的な変更は、`playbackLoop` と `muteWaitMs` 計算の
`getEffectiveSpeed()` → `playbackRate`（4 箇所）と、その付近のコメント。

**これは今回渡された指示（duration の入れ替え・コメント・CLAUDE.md の書き直し）
には書かれていないが、`TODO.md` の TODO-018 の元々のチェック項目
（「`playbackLoop` の経過時間から `baseSpeedMultiplier` を外し `deltaTime *
playbackRate` で進める」「`duration` を待ち時間に使っている箇所も
`duration / playbackRate` に揃える」）には含まれている。** 今回の指示文だけを
見ると範囲外に見えるが、TODO 全体の指示には沿っている。念のため報告する。
`utterance.rate` と `fallbackAudioElement.playbackRate`、Web Speech の
安全タイマー（`getEffectiveSpeed()` のまま）は TODO のチェック項目どおり
変わっていないことも確認した（該当行 1364, 1396, 1426）。

## 3. `formatTime(317)`

コード中の `formatTime`（1259〜1263 行）をそのまま使って確認。

```
$ node -e '(実装と同じ formatTime を再実装して total=317 を渡す)'
formatTime(total)= 5:17
```

`5:17` になる。**OK。**

## 4. reviewer 報告の「実再生(1.4x)」列との突き合わせ

reviewer 報告（`archives/agents/TODO-018/reviewer-report.md`）の表の
「実再生(1.4x)」列を四捨五入（`Math.round` 相当、.5 は切り上げ）した値と、
入れた `duration` を 1 件ずつ突き合わせた。

| # | 実再生(1.4x) | 四捨五入 | 入れた duration | 一致 |
|---|---|---|---|---|
| 1 | 18.1 | 18 | 18 | ○ |
| 2 | 19.4 | 19 | 19 | ○ |
| 3 | 18.8 | 19 | 19 | ○ |
| 4 | 18.5 | 19 | 19 | ○ |
| 5 | 20.7 | 21 | 21 | ○ |
| 6 | 19.4 | 19 | 19 | ○ |
| 7 | 18.6 | 19 | 19 | ○ |
| 8 | 19.3 | 19 | 19 | ○ |
| 9 | 18.4 | 18 | 18 | ○ |
| 10 | 19.6 | 20 | 20 | ○ |
| 11 | 21.2 | 21 | 21 | ○ |
| 12 | 14.8 | 15 | 15 | ○ |
| 13 | 17.0 | 17 | 17 | ○ |
| 14 | 17.3 | 17 | 17 | ○ |
| 15 | 16.5 | 17 | 17 | ○ |
| 16 | 16.6 | 17 | 17 | ○ |
| 17 | 21.9 | 22 | 22 | ○ |

17 件すべて一致。**ずれ無し。**

（reviewer 報告の表の合計は「計」の行が 316.2s と出ているが、これは
1 件ずつの実測小数値の合計であって、四捨五入後の合計 317 とは 0.8 の差が
出て当然のもの。矛盾ではない。）

## 5. 構文チェック

`node --check` は `.html` を直接扱えないため、`<script>` ブロックを 2 つ
抜き出して個別にチェックした。

```
$ node --check /tmp/claude-649-script-0.js && echo OK
OK
$ node --check /tmp/claude-649-script-1.js && echo OK
OK
```

両方 OK。壊れていない。

## 6. `CLAUDE.md` の書き換えと実装の一致

- 「`duration` には 1.4 倍速で再生した実測秒数が入っている（合計 317 秒）」
  → 上記 1 で確認済み。**合っている。**
- 「Online TTS 側には安全タイマーが無い」
  → `speakOnlineTTS()`（1410〜1450 行）を読んだ。`onended` / `onerror` /
    `play().catch()` の 3 箇所以外に、時間経過だけで無条件に発火する
    `setTimeout` は無い。`onerror` と `catch` の中の `setTimeout` は
    「エラーが起きたときのフォールバック待ち時間」であって、再生が
    始まったまま何も起きず止まった場合（通信が途中で切れて `onended` も
    `onerror` も来ない）を救うタイマーではない。**CLAUDE.md の記述と
    実装は一致している。**
- 「`total-time-display` の初期値は `--:--`」
  → `claude_memo.html:384` で確認。**一致。** `initPlaylist()`
    （1574〜1595 行）が `totalTimeDisplay.textContent =
    formatTime(totalDurationSeconds)` で上書きする作りも記述どおり。
- 行番号
  → `grep -n "const slideData = \["` は 476 行付近（`slideData:` の
    コメント行は 473 行）、`playbackLoop` 関数は 1505 行付近から。
    CLAUDE.md の「473 行あたり〜」「1131 行あたり〜」はいずれも
    実際の行と近く、誤差は「あたり」の範囲内。**問題なし。**

## 変更ファイルの一覧と指示との整合

```
$ git status
 M CLAUDE.md
 M claude_memo.html
?? archives/agents/TODO-018/
```

指示された範囲（`slideData` の `duration`、関連コメント、`CLAUDE.md`）に
収まっている。`claude_memo.html` 側の `playbackRate` 化は前述のとおり
TODO-018 本体の指示に含まれるものであり、範囲外の変更ではないと判断した。

## 確かめられなかったこと・判断が要る点

- **reviewer 報告の 1.4x 実測値そのものの再現はしていない。** Google
  Translate TTS への再アクセスと `ffprobe` 計測はこの回では行っておらず、
  reviewer 報告の数値を信頼して四捨五入の突き合わせだけを行った。
  実測をもう一度取り直すべきかは判断できない。
- ブラウザでの実際の目視確認（バーの動き、`--:--` が実際に上書きされる様子）
  は行っていない。静的なコードの読み合わせとロジックの追跡にとどまる。
