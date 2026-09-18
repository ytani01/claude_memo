# TODO-009 レビュー報告

対象: `claude_memo.html` の未コミット差分（`git diff`）。
メディアクエリ `@media screen and (max-width: 767.98px)` を
`@media screen and (max-width: 767.98px), screen and (pointer: coarse)` へ
広げた変更。Playwright（`/tmp/verify064/node_modules/playwright`、system chromium）で
実測して裏を取った。

## 要修正

### 1. `claude_memo.html:203`（`#viewport-frame` 系のメディアクエリ）— フルスクリーン外の通常再生にも縮小経路が及ぶ

TODO-009 のチェック項目は「タッチ画面の**フルスクリーンでも**、960x540 を
`--vp-scale` で縮小する経路に入れる」だが、実際の変更は共有のメディア
クエリ自体を広げたため、**フルスクリーンでない通常再生**でもタッチ画面
なら縮小経路に入る。ブロック内のルール（`#viewport-frame` の
`aspect-ratio`/`overflow`、`#player-viewport` の `position: absolute` +
`width:960px` + `transform: scale()`、`#subtitle-banner` の
`position: static`）はどれも `#viewport-stage.is-fullscreen` に
スコープされていない（スコープされているのは
`.video-viewport.pseudo-fullscreen` と
`#viewport-stage.is-fullscreen > #subtitle-banner` の 2 つだけ）。

実測（`file://.../claude_memo.html`、フルスクリーンにしていない通常表示）:

| 条件 | `#player-viewport` position | width | transform | `#subtitle-banner` position |
|---|---|---|---|---|
| 1366x768, mouse | `relative`（ネイティブ） | 918px（実寸） | `none` | `absolute`（枠に重ねる） |
| 1366x768, touch | `absolute` | 960px 固定 | `scale(0.956)` | `static`（枠の下へ流れる） |
| 1024x768, touch | `absolute` | 960px 固定 | `scale(0.756)` | `static`（枠の下へ流れる） |

`#slide-category` の実描画高さも 1366px touch で 19.125px（mouse は
20px）と、fixed-px のクロームが `--vp-scale` 分だけ余計に縮む
（1024px touch なら係数 0.756 になるのでさらに縮む）。

つまりタッチ対応ノート PC（1366px 相当）やタブレット横持ち（1024px 相当）は、
**フルスクリーンにしなくても**字幕が枠に重ならず下へ流れ、クローム文字が
一段小さくなるという見た目の変化を受ける。これは指示にあった懸念
「タッチ対応 PC で見た目が変わってしまわないか」がそのまま実害として
出ているケース。

根拠:
- TODO.md の TODO-009 節: 「タッチ画面の**フルスクリーンでも**」という
  文言（フルスクリーン限定の意図に読める）
- `archives/todo/TODO-003. 横持ちのスマホでフルスクリーンから抜けられないのを直す.md`:
  「`--vp-scale` による縮小は 767.98px 未満のままで、**変えていない**」と
  明記されており、`pointer: coarse` を足したのは暗幕と `fs-lock` の
  2 ルールだけだったという前例がある。今回はその前例と逆に、縮小経路の
  メディアクエリそのものを広げている
- 実測（上表）

この広がりが利用者の狙いどおりなら実装として問題無いが、TODO の文言と
過去の設計判断（TODO-003）からは「フルスクリーンだけ」のつもりだった
可能性があり、確認が要る。狙いどおりでなければ、`#player-viewport` /
`#subtitle-banner` の縮小系ルールを `#viewport-stage.is-fullscreen` の
中だけに絞る（メディアクエリ自体は広げつつ、フルスクリーンでない通常時は
今までどおり PC の経路のままにする）作りに直す必要がある。

## 検討

### 2. `CLAUDE.md`（触るときの注意）が今回の変更を反映していない

`CLAUDE.md` の「768px 未満は container query とは別系統で縮小している」の
節は、幅の条件しか書いておらず、`(pointer: coarse)` を足したことに
触れていない。`git diff -- CLAUDE.md` は差分無し。

根拠: TODO-003 では同種の変更（暗幕/`fs-lock` への `pointer: coarse` 追加）の
際に「`CLAUDE.md` の `body.fs-lock` の節を条件に合わせて書き直した」と
明記されており、同じプロジェクトの前例がある。今回はその節（`#subtitle-banner`
やフルスクリーンの説明の前段）を直していないので、次にここを読む人が
「768px 未満だけの話」と誤読する恐れがある。

## 情報（問題なし、確認した点）

- **暗幕/`fs-lock` のメディアクエリ（1 行目 269）との整合**: 今回変更した
  `#viewport-frame` 側のメディアクエリと文字列が完全に一致しており
  （どちらも `screen and (max-width: 767.98px), screen and (pointer: coarse)`）、
  条件のずれは無い
- **clamp() の下限直書き**: `grep -c "clamp("` で 152 件すべてが `cqw` を
  中間項に使っており、`vw` や固定値だけに頼っている `clamp()` は残っていない
  （`--vp-scale` の transform 経路がスケール不変であることの前提が崩れていない）
- **範囲**: 変更はメディアクエリの条件とそれに対応するコメント 2 か所のみ。
  指示に無い変更の混入は無い

## 判断が要る点（まとめ）

要修正 1 件は「TODO-009 の意図がフルスクリーン限定かどうか」の確認が先。
フルスクリーン限定でよいなら実装をそのスコープに絞る直しが要る。
広く縮小経路に入れる意図（PC 経路そのものをタッチ画面では使わない、という
判断）なら、TODO-003 の前例と食い違う理由を `TODO-009` の記録に残すのが
筋。
