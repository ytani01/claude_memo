# TODO-019 レビュー報告（reviewer）

対象: `git diff` の `claude_memo.html`（`stopSpeech()` 1265-1283 行、
`speakOnlineTTS()` 1411-1467 行）。コードは直していない。

## 要修正

### 1. `onloadedmetadata` が「次スライドへ 2 秒待ち」のタイマーを上書きして殺しうる

`slideTransitionTimeout` を、(a) 安全タイマー、(b) `onSlideAudioFinished()` が
張る「読了後 2 秒待ってから次スライドへ」のタイマー、の 2 用途で共有している
（1437-1443 行の `setEndTimeout` と 1295 行）。

`setEndTimeout` は呼ばれるたびに無条件で
`if (slideTransitionTimeout) clearTimeout(slideTransitionTimeout);` して上書きする
（1438 行）。一方 `onloadedmetadata`（1457-1461 行）と `onerror`（1449-1452 行）の
コールバックは、`handleEnd()` が既に走った（`finished === true`）かどうかを
見ずに `setEndTimeout` を呼ぶ。

想定できる順序:

1. 通信が遅く `onended` が来ない → 1456 行の初期見積もりタイマーが先に発火し
   `handleEnd()` → `onSlideAudioFinished()` が呼ばれ、次スライドへの 2 秒待ち
   タイマーが `slideTransitionTimeout` に入る。
2. その後（遅れて）`onloadedmetadata` が発火し、`audioSec` が有効な値なら
   `setEndTimeout(...)` を呼ぶ。これが手順 1 の 2 秒待ちタイマーを
   `clearTimeout` で消し、代わりに新しいタイマーを入れる。
3. 新しいタイマーのコールバックは `if (finished || !isPlaying) return;` で
   `finished === true` のため何もしない。

結果、次スライドへ進む処理が握り潰され、現在のスライドで止まったままになる。
まさにこの変更が対象にしている「通信が途中で止まった」場面（コメント
1454-1455 行）で起きうる並びなので、机上の空論ではない。

根拠: コード読解（1265-1467 行）。ブラウザでの再現はしていない（未実測）。
`onloadedmetadata` は仕様上 1 回しか発火しないため、`onended` より後に来ることは
無いはずだが、「初期見積もりタイマーの発火より後に `onloadedmetadata` が来る」
順序は仕様上妨げられない。

### 2. `.play().catch()` のコールバックは `stopSpeech()` で消せない

`stopSpeech()`（1265-1283 行）は `fallbackAudioElement.onended` /
`onerror` / `onloadedmetadata` を `null` にするが、これは DOM 要素の
プロパティであって、`speakOnlineTTS()` の `fallbackAudioElement.play()` が
返す Promise（1463-1466 行）には効かない。この `.catch` コールバックは
古い呼び出しのクロージャ（`finished` ローカル変数、`setEndTimeout` 関数）を
そのまま持っており、`stopSpeech()` を挟んで次のスライドの
`speakOnlineTTS()` が新しく `slideTransitionTimeout` を張った後でも、
古い呼び出しの `.catch` が遅れて解決すれば `setEndTimeout` を呼んで
新しい呼び出しの `slideTransitionTimeout` を上書きしうる。

Web Speech 側（`speakCurrentNarration()`）は `runId !== speechRunId` を
各コールバックでチェックして古い実行を無効化しているが（1334, 1355, 1361,
1386, 1399 行）、`speakOnlineTTS()` には同種のガードが無い。DOM ハンドラは
`stopSpeech()` が握りつぶせるので実害が出にくいが、Promise コールバックは
握りつぶせない分だけ抜け道になっている。

依頼にある「`speechRunId` を見ていないが、`stopSpeech()` の後始末だけで
足りているか」への回答: **DOM イベントハンドラ分（`onended`/`onerror`/
`onloadedmetadata`）は足りているが、`.play().catch()` の分は足りていない。**

根拠: コード読解。実機での再現はしていない（`.play()` の拒否は通常ほぼ
即座に解決するため、発生確率は低いと見るが未確認）。

## 検討

### 3. `CLAUDE.md` の記述が今回の変更で古くなる

`CLAUDE.md` 40-42 行に「**Online TTS 側には安全タイマーが無い**
（`onended`・`onerror`・`play()` の拒否だけ）。通信が途中で止まると
読み終わりのイベントが来ず、そこで止まったままになる（TODO-019）」とある。
これはこの diff が直そうとしている旧状態そのものの説明で、今回のコード変更に
合わせて更新されていない（diff は `claude_memo.html` のみで `CLAUDE.md` は
変更なし）。ユーザー全体の `CLAUDE.md` は「対で保守すべきもの」の整合を
求めており、このままマージすると文書が実装と食い違う。

根拠: `/net/.../claude_memo/CLAUDE.md` 40-42 行と、今回の diff に
`CLAUDE.md` の変更が含まれていないこと（`git status`／`git diff` で確認済み）。

### 4. 安全タイマーの見積もり式が `getEffectiveSpeed()` と食い違う

`speakOnlineTTS()` の見積もり（1451, 1456, 1465 行）は
`slideData[currentIndex].duration / playbackRate` を使うが、実際の音声再生
レートは `Math.min(2.0, getEffectiveSpeed())`（1428 行、
`getEffectiveSpeed() = playbackRate * baseSpeedMultiplier`、
`baseSpeedMultiplier = 1.4`）。Web Speech 側の同種の安全タイマー（1397 行）は
`getEffectiveSpeed()` を使っており、基準がそろっていない。

`baseSpeedMultiplier`（1.4）が 1 より大きい間は
`duration / playbackRate ≥ duration / getEffectiveSpeed()` が常に成り立ち、
見積もりは常に実際の再生時間より長め＝安全側に振れる（`speedOptions`
0.75〜2.0 の全域で確認、根拠は算数のみで実測はしていない）。ただしこれは
`baseSpeedMultiplier > 1` という前提に暗黙で依存しており、今回の diff で
`onloadedmetadata` 到達前の初期見積もり（1456 行）という新しい利用箇所が
増えた分、この暗黙の前提への依存が広がった。式自体は今回の diff で
新規に書かれたものではなく、`onerror`／`play().catch()` の既存の式
（1451, 1465 行）をそのまま流用している。

### 5. 安全タイマーがバーより先にスライドを送りうる（TODO-018 との関係）

安全タイマーは `renderSlide()` を経由してのみスライドを進め、
`currentSlideElapsedTime` を直接は触らないため、TODO-018 で合わせた
進行バー・時間表示のロジック自体への直接の悪影響は見当たらない。ただし、
安全タイマーが実際の音声終了より早く発火した場合、バーが 100%（`slide.duration`）
に達する前にスライドが切り替わる見た目にはなりうる。これは「読み上げの
終了イベントで送る」という既存設計（`CLAUDE.md` 30-31 行）の範囲内の挙動で、
今回の diff が新しく持ち込んだリグレッションではない。

## 問題なし

- `onloadedmetadata` は `.src` 差し替え前（1425 行、差し替えは 1426 行）と
  `stopSpeech()`（1281 行）の両方でクリアされている。使い回しの
  `fallbackAudioElement` に前のスライドの `onloadedmetadata` が残ることは無い。
- `onended` が正常に来たケースでは `finished` フラグにより
  `handleEnd()` の二重実行は防げている。
- `onerror` / `play()` 拒否側の待ち時間（`slide.duration / playbackRate`）は
  変えられていない（決めたことどおり）。
- 差分は `stopSpeech()` と `speakOnlineTTS()` のみで、指示の範囲外の変更は
  無い。
- コメント（1454-1455 行）は「何を」ではなく「なぜ（受け皿である理由、
  張り直す理由）」を書いており、規約に沿っている。

## 好みの範囲

- `speechRunId` を使わない設計にした理由（DOM ハンドラの使い回しで足りる、
  という判断）がコードに残っていない。上記「検討 2」と合わせて、次に読む人が
  「なぜ Web Speech 側と作りが違うか」を追わずに済むよう、一言コメントが
  あるとよい。
