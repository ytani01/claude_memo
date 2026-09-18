# TODO-035 verifier 報告

## 対象

`claude_memo.html` への 2 回のパッチ:

1. `#caption-text` から `line-clamp-2 overflow-hidden` を削除（全文表示）
2. `#subtitle-banner` を PC でもスライド枠に重ねず、常に枠の下へ流す
   （クラスを `absolute bottom-3 left-4 right-4` → `mt-3`、擬似フルスクリーン用の
   `#viewport-stage.is-fullscreen > #subtitle-banner { position: absolute; top: 100%; ... }`
   を @media の外（全画面幅共通）へ移動）

`git diff claude_memo.html` は依頼に書かれた変更点と一致。`TODO.md` の差分も
「PC でも字幕をスライドの下に出す」の追記のみで、コードの変更範囲と齟齬なし。

## 確認方法

`/tmp/verify064`（既存の playwright インストール済みディレクトリ）に検証スクリプトを
置き、Chromium ヘッドレスで `claude_memo.html` を `file://` で開いて確認した。
ナレーションは `narration: '...'` を正規表現で全 17 件抽出し、文字数で比較 →
**スライド 6「マルチエージェントで役割分担」の 176 文字が最長**（次点は
スライド 3 の 154 文字）。字幕は `renderSlide()` 内で `captionText.textContent =
slide.narration` と、音声再生の有無に関わらず設定されるため、TTS を動かさず
「次へ」ボタンでスライド 6 まで進めてから字幕トグルをクリックする方法で検証した。

## 1〜3: 全文表示・崩れの有無（通常表示）

`scrollHeight` と `clientHeight` が一致すれば切れていない証拠として計測。

| 画面 | textLength | scrollHeight | clientHeight | 一致 |
|---|---|---|---|---|
| PC 1280x800 | 176 | 72 | 72 | 一致（切れなし） |
| 横持ちスマホ 844x390 | 176 | 96 | 96 | 一致（切れなし） |
| 縦持ちスマホ 390x844 | 176 | 205 | 205 | 一致（切れなし） |

比較のため、`line-clamp-2 overflow-hidden` を戻した複製ファイル
（本物のリポジトリは変更していない。`/tmp/.../scratchpad/claude_memo_before.html`
に複製を作って検証しただけ）でも同じ横持ちスマホを計測したところ
`scrollHeight=96` に対し `clientHeight=48` で、**確かに以前は 2 行で切れていた**
ことを確認した（今回の 1 点目の修正が効いている根拠）。

崩れの有無はスクリーンショットで確認。PC・横持ち・縦持ちいずれも、字幕バナーが
伸びたことでスライド本文や操作パネルが隠れたり画面外にはみ出したりする様子は
無かった（下記 4 のとおり、PC は枠との重なりも 2 点目の修正で解消済み）。

## 4: PC 通常表示でスライド枠に重ならないか

`slide-canvas`（スライド枠）の `bottom` と `subtitle-banner` の `top` を比較。

- `slide-canvas.bottom = 580.375`
- `subtitle-banner.top = 617.375`（枠の下、重なり無し）
- `subtitle-banner.bottom = 741.375`
- `progress-bar.top = 772.375`（バナーの下、こちらも重なり無し）

スクリーンショット（`todo035-v2-normal-pc.png`）でも、字幕バナーが枠の下に
独立して表示され、シークバー・再生ボタン等の操作パネルも隠れずに見えることを
目視で確認した。

## 5: 擬似フルスクリーンでの字幕（要確認: 問題あり）

`getBoundingClientRect().bottom` と `window.innerHeight` を比較。

| 画面 | subtitle-banner.bottom | window.innerHeight | はみ出し |
|---|---|---|---|
| PC 1280x800 | 896 | 800 | **96px はみ出す** |
| 横持ちスマホ 844x390 | 574 | 390 | **184px はみ出す** |
| 縦持ちスマホ 390x844 | 764.6875 | 844 | はみ出さない（79px 余裕） |

**PC と横持ちスマホの擬似フルスクリーンでは、字幕が画面の下端からはみ出して
読めなくなっている。** スクリーンショットで実際に確認済み:

- `todo035-v2-fullscreen-pc.png` — 字幕本文がほぼ画面外。ヘッダー行
  「ナレーション字幕」のごく一部だけが下端にかろうじて見える程度で、本文は
  見えない
- `todo035-v2-fullscreen-phone-landscape.png` — 字幕バナー自体が完全に画面外で、
  何も見えない
- `todo035-v2-fullscreen-phone-portrait.png` — 字幕は画面内に収まり、問題なし

原因（推定）: `#viewport-stage.is-fullscreen` は 16:9 のレターボックスを
`position: fixed` で画面いっぱいに confineし、`#subtitle-banner` はその
`top: 100%`（レターボックス下端）に絶対配置される。レターボックスが画面の
幅または高さいっぱいまで広がる（16:9 に近い画面）と、その下に字幕の高さ分の
余白が残らず、字幕全体が画面外に押し出される。1 点目の修正で字幕が長文化した
ことで、この問題がより起きやすくなっている可能性がある（これは推定であり、
実測はしていない）。

## 6: 横持ち・縦持ちスマホの通常表示が以前と変わっていないか

依頼にある「これまでと変わっていないか」については、"以前" の版（1 点目の
修正のみ適用した状態）とも比較した。

- 1 点目の修正のみの版（字幕は `position: absolute; bottom-3 left-4 right-4`
  のまま）で横持ちスマホを計測すると、`subtitle-banner.top = -51.25` と
  画面上端より上にはみ出しており、字幕を見るには下へスクロールする必要が
  あった
- 2 点目の修正後は `subtitle-banner.top = 121.75` で、スクロール無しの
  初期表示のまま画面内に収まっている（`todo035-v2-normal-phone-landscape.png`）

**通常表示に関しては、横持ちスマホの見え方はむしろ改善している。**
「変わっていない」ではなく「良くなっている」というのが実測結果。崩れは無い。

縦持ちスマホの通常表示も、字幕・操作パネル・チャプター一覧いずれも隠れず
表示されている（`todo035-v2-normal-phone-portrait.png`）。

## スクリーンショット一覧（`~/tmp/playwright-mcp/`）

- `todo035-caption-before-phone-landscape.png` — 1 点目のみ・修正前相当（比較用）
- `todo035-v2-normal-pc.png` / `-phone-landscape.png` / `-phone-portrait.png` — 通常表示
- `todo035-v2-fullscreen-pc.png` / `-phone-landscape.png` / `-phone-portrait.png` — 擬似フルスクリーン

## 検証スクリプト

`/tmp/verify064/verify_todo035_v2.js`（playwright は `/tmp/verify064/node_modules`
のものを利用。プロジェクト側に playwright は入っていない）。セッション終了後は
消える一時ディレクトリなので、再現する場合は同じ内容を再作成する必要がある。

## 判断できなかったこと・残る懸念

- **PC と横持ちスマホの擬似フルスクリーンで字幕がはみ出す件は、今回の依頼の
  確認観点そのもの（5 番）であり、実装のやり直しが要るかどうかは判断できない。**
  管理者の判断を仰ぎたい。
- はみ出しの原因は推定にとどまる（CSS の重なりを手を動かして直してはいないため、
  「直せばこうなる」という検証はしていない）。
- 縦持ちスマホの擬似フルスクリーンで、ヘッダー等の暗幕が実際に効いているか
  （色の濃淡）までは検証していない。今回の依頼の範囲外と判断し省略した。
