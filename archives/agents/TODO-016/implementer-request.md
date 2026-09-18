# implementer への依頼（TODO-016）

## 目的

`claude_memo.html` から、**描画結果と動作が変わらない範囲で**未使用の定義と
冗長な記述を削る。TODO-014 と同じ趣旨の続き。

## 対象範囲

`claude_memo.html` のみ。行番号は着手時点（1939 行）。

1. `L22-31` tailwind.config の `colors.brand`（6 色）を消す。`brand-` の参照は 0
2. `L34` `fontFamily.heading` を消す。`font-heading` の参照は 0。
   あわせて `L14` の Google Fonts URL から `family=Urbanist:wght@600;800&` を外す
3. `L63-64` `.video-viewport` の `width: 100%` と `max-width: 100%` を消す
4. `L183-185` `#viewport-frame { width: 100% }` をルールごと消す
   （3, 4 とも「flex 列の子は既定で幅いっぱい」が根拠。
   **消す前後で計算値が変わらないことを自分で確かめてから消すこと**。
   変わるなら消さずに報告する）
5. `L203` と `L270` の `@media`（条件が同一）を 1 ブロックに統合する。
   統合したら `L1895-1896` の「同じ条件を CSS の @media 2 か所にも書いてある」
   というコメントも実態に合わせて直す
6. `L1157, 1301, 1306, 1393, 1407` の `speechActive` を、宣言も代入も消す
7. `L1604` `btn.id = playlist-item-${idx}` を消す
8. `L1596-1597` `initPlaylist()` 冒頭の `innerHTML = ''` と
   `playlistItems.length = 0` を消す（呼び出しは `startApp()` からの 1 回だけ）
9. `L1194-1199` `slideStartTimes` の累積ループを短くする
10. `L1662-1677`（字幕トグル）、`L1680-1689`（音声エンジン切替）、
    `L1713-1722`（速度の巡回）の 3 ハンドラを、`classList.toggle` と
    剰余（`% speedOptions.length`）で短くする

## 手を付けないもの

以下は**表示か動作が変わる**ので、この項目の対象外。触らないこと。

- `L472` `playlist-count` の `17 Slides` 直書き
- `L1522-1523` `updateWaveState()` のクラス（`text-[9px]` と HTML の `text-xs` の差）
- `L1362-1369` 音声選択の正規表現
- Web Speech 経路そのもの
- `L1451-1460` `speakOnlineTTS()` の `finished` / `handleEnd`
- スライドの定義（`L491-1148`）

## 完了条件

- 上の 1〜10 がすべて入っているか、入れられない理由が報告にある
- **描画結果と動作が変わらない**こと
- 既存のコメントが実態と食い違ったままにならないこと（5 のほか、
  消した記述に言及しているコメントがあれば直す）

## 検証方法

- `<script>` を取り出して `node --check`（ファイルは
  `/tmp/claude-649/.../scratchpad` ではなくあなたの作業用の一時ファイルでよい）
- 消した識別子（`brand-`, `font-heading`, `Urbanist`, `speechActive`,
  `playlist-item-`）を `grep` して参照が残っていないことを確認
- 3, 4 については、削除の前後で該当要素の計算幅が変わらない根拠を示す

## 報告

`archives/agents/TODO-016/implementer-report.md` に書く。
中身は **変更点 / 検証結果 / 残る懸念** に絞る。
返事は「終わったか・報告ファイルのパス・判断が要る点」を 5 行以内で。

目安 20 分。超えそうなら、そこまでの状態を報告する。
