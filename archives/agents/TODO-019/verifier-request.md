# TODO-019 確認依頼（verifier）

## 目的

`speakOnlineTTS()`（`claude_memo.html`）に足した安全タイマーが、指示どおりに
入っているかを確かめる。コードは直さないこと。見つけたことは報告だけする。

## 対象範囲

`git diff` の差分（`claude_memo.html` の `stopSpeech()` と
`speakOnlineTTS()` のみ）。

## 決めたこと

- 待ち時間の基準は「音声の `duration` 属性 + 余裕 3 秒」。
  `loadedmetadata` で実長が取れなければ、スライドの `duration` を使う
- 既存の `onerror` / `play()` 拒否の待ち時間（`slide.duration / playbackRate`）は
  変えない

## 完了条件

1. `onended` が来なくても、音声の実長 + 3 秒で `onSlideAudioFinished()` へ進む
2. 実長が取れない（`NaN`・0）ときは、スライドの想定秒数 + 3 秒で進む
3. `onended` が正常に来たときは、安全タイマーで二重に進まない
4. 一時停止・スライド移動（`stopSpeech()`）の後にタイマーが残って
   勝手に進むことがない
5. `onerror` / `play()` 拒否の待ち時間が従来と同じ

## 検証方法

ブラウザ（Chromium 系）で `claude_memo.html` を開いて確かめる。
`translate.google.com` への通信を DevTools の Network から
オフライン/ブロックにすると、`onended` が来ない状況を作れる。
実測した秒数を報告に書くこと（「たぶん動く」では不可）。
ヘッドレスで音声が鳴らせない場合は、その旨と、代わりに何で確かめたかを書く。

目安 20 分。詰まったら、どこで詰まったかを書いて報告を返すこと。

## 報告先

`archives/agents/TODO-019/verifier-report.md`
返事は 5 行以内（終わったか・報告のパス・判断が要る点）。
