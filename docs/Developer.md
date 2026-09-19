# player.html を直す人へ

**同じ内容をスライドでも見られる**（`player.html?deck=developer`）。

再生エンジン `player.html` を直すときに、先に知っておきたいことをまとめる。
**スライドを足したい・作りたいだけなら [User.md](User.md) を読めばよい。**
こちらを読む必要は無い。

## リポジトリの構成

| ファイル | 中身 |
|----------|------|
| `player.html` | 外枠の HTML・CSS と再生ロジック。**これ 1 つが本体** |
| `slides/<名前>.js` | スライドのデータ。`readme`・`user`・`developer`・`claude-memo` |
| `tools/measure-duration.py` | 読み上げ秒数を測り、`duration` に書き戻す |
| `tools/test_measure_duration.py` | 書き戻しの置換を確かめる自己テスト |

**ビルドも、依存関係のインストールも無い。**
テストは `tools/test_measure_duration.py` の 1 本だけで、`duration` の
書き戻しの置換を見る（実行に `python3` 以外は要らない）。 Tailwind・Google Fonts・
FontAwesome は CDN から読む（オフラインでは崩れる）。置き場所が `public_html/`
なので、ファイルを置けばそのまま公開される。

確認はブラウザで `player.html` を開くだけ。

### 置き場所は選ばない

`player.html` がローカルを指しているのは `slides/<名前>.js` の 1 か所だけで、
しかも相対パス。残りは全部 CDN の https。**`player.html` と `slides/` を
同じディレクトリに置けば、`public_html/` の外でもそのまま動く**。

手元で試すなら、そのディレクトリで:

```bash
python3 -m http.server 8000
# => http://localhost:8000/player.html
```

- **`file://` で直接開くのは試していない。** `document.write` で足した相対の
  `<script>` の読み込みと、外部への音声要求がブラウザの制限に当たる可能性が
  ある。HTTP で配るのが確実
- **ネット接続は要る。** Tailwind・Google Fonts・FontAwesome・読み上げの音声を
  外から取るので、オフラインでは崩れるし鳴らない
- 公開 URL を変えたくないなら、元の場所にリダイレクトかシンボリックリンクを
  残す

## 全体の作り

**HTML → `slideData` → 再生ロジック** の 3 段で、データだけが別ファイルに
分かれている。

`player.html` は `?deck=<名前>` の `<名前>` から `slides/<名前>.js` を読む
（既定は `readme`）。読み込みは `</main>` の直後の `document.write` で、
**再生ロジックの `<script>` より先に走らせている**。その下の `<script>` が
読み込み時点で `slideData` を参照するので、順番を入れ替えると動かない。
デッキが読めなかったときは、白画面にせず理由を出して `throw` で止めている。

`slideData` の 1 要素は `{ title, duration, narration, render() }`。
スライド番号は持たせず、並び順から出す（TODO-048）。
それぞれの意味は [User.md](User.md) にある。

## 再生ロジック

`requestAnimationFrame` の `playbackLoop` が経過時間を進め、`duration` が
尽きたら次のスライドへ移る。ただし**実際のスライド送りは、読み上げの終了
イベントで起きる**。`duration` を待ち時間として使うのは、消音中と、音声が
鳴らせなかったとき（`onerror`・`play()` の拒否）だけ。

### 時間軸に `BASE_SPEED_MULTIPLIER` を掛けない

進行バーと時間表示は**実時間**（`deltaTime * playbackRate`）で進める。
**`BASE_SPEED_MULTIPLIER` が掛かるのは読み上げの速度だけ**
（`playbackRate * BASE_SPEED_MULTIPLIER`）。時間軸のほうにも掛けると
バーだけが先走り、`duration` で頭打ちになって読み終わりまで止まって見える。

音声が `duration` より長ければ、バーは 100% のまま読み終わりを待つ。
これは仕様として受け入れている。Web Speech に切り替えると音声の長さが
変わるので、バーとは必然的にずれる。

### `duration` は実測値

`duration` には **Online TTS の音声を `BASE_SPEED_MULTIPLIER` 倍で再生した
実測秒数**が入っている。`slides/claude-memo.js` の 17 枚は `ffprobe` で測って入れた値
（合計 324 秒）で、目分量の数字ではない。

**`prepareSpeechText()` の置換表を変えると読み上げの長さも変わる。**
当たるスライドの `duration` を測り直すこと。測るには
`tools/measure-duration.py` を使う（`--deck <名前>` でデッキを選び、
案の下見は `--text`）。**`--write` を付けると、測った値を
そのデッキの `duration` に書き戻す**（TODO-050、TODO-051）。
ナレーションを直したあとは
`tools/measure-duration.py --deck <名前> --all --write` でまとめて合わせられる。

**このスクリプトは `prepareSpeechText()` の置換表と `TTS_MAX_CHARS`・
`BASE_SPEED_MULTIPLIER` を写している。** `player.html` 側を直したら、
スクリプトの `RULES` と定数も一緒に直す。片方だけだと測った秒数が実際と
ずれる。

## 読み上げ

2 系統を `toggle-voice-engine-btn` で切り替える。**既定は `online`。**

| モード | 実装 | 制限 |
|--------|------|------|
| `online` | Google Translate TTS の URL を `Audio` で再生 | `TTS_MAX_CHARS` で切る |
| `speech` | Web Speech API（`SpeechSynthesisUtterance`） | 長い発話が途中で切れる |

`narration` は `prepareSpeechText()` を通してから読み上げられる。記号や
英単語の読みがおかしいときはここを見る。

どちらにも安全タイマーがある。読み終わりのイベントが来なくても次へ進むため。

- **Web Speech**: **文字数**から計算する
  （`textToSpeak.length / SPEECH_CHARS_PER_SECOND / getEffectiveSpeed()`）。Web Speech は
  読み終わりのイベントが来ないことがある
- **Online TTS**: **音声の実長**（`loadedmetadata` で取る。取れなければ
  スライドの `duration`）に `TTS_END_MARGIN_MS` 足した時点で進める

### 触ると鳴らなくなるもの

次の 3 つは、どれも実機で鳴らなくなって分かったもの。理由を知らずに
「整理」すると再発する。

- **`Audio` 要素（`fallbackAudioElement`）は 1 個を使い回す。**
  再生ボタンのクリックの中で unlock しているので、`null` にして作り直すと
  Android Chrome で自動再生がブロックされて鳴らなくなる
- **Web Speech は `splitForSpeech()` で `maxLen` の既定値ぶんに分けて順に
  読ませる。**
  Chrome は PC も Android も、長い発話を 15 秒ほどで打ち切る。1 つにまとめる
  と途中で切れる
- **`<meta name="referrer" content="no-referrer">` を外さない。**
  Google Translate TTS は Referer が付いた要求に 404 を返すので、外すと
  Online TTS が鳴らなくなる

## レイアウト

### 拡大縮小は container query

`.video-viewport` が `container-type: inline-size` で、`render()` の中は
`cqw` と `clamp()` で書く。**`px` や `rem` の直書きは、16:9 を縮めたときに
崩れる。**

### 狭い画面とタッチ画面は別系統

**幅 768px 未満とタッチ画面は、container query とは別の経路で縮小している。**
条件は `@media screen and (max-width: 767.98px), screen and (pointer: coarse)`。

タッチ画面を条件に加えたのは、横持ちのスマホ（844x390 など）が幅 768 以上で
PC 扱いになり、レターボックスの中では `clamp()` の下限 px が効いて本文が
縮まず、枠内上段に重なるため。**フルスクリーン中に限らず、タッチ画面なら
通常表示でもこの経路に入る**（タブレットやタッチ対応 PC も同じ）。

この経路では、`#viewport-frame` が 16:9 の外枠になり、`setupViewportScale()`
が `--vp-scale` を入れて `#player-viewport`（中身は 960x540 のまま）を
`transform: scale()` で縮める。

**縮むのは枠の中身すべてで、`cqw` や `clamp()` で書いていない固定 px の
ものも例外ではない。** 幅 768px 未満では `md:` が効かない
（`md:` は `min-width: 768px`）ので、枠の中のクロームは `text-xs` などの
小さい方が選ばれ、それがさらに `--vp-scale`（0.34〜0.77）倍される。実際、
枠の上の `SLIDE nn / NN` は 390px 幅で 5px 前後になる。補助的な情報なので、
**読めなくてよいものとして残している。**

### 字幕バナーだけは枠の外

`#subtitle-banner` は `#viewport-stage` の直下にあり、**縮小されない**。
枠に重ねず、**画面幅によらず常に枠の下へ流す**（全文を出すので、重ねると
スライドを隠してしまう）。

通常表示はクラスの `mt-3` だけで足りるので、CSS に書いてあるのは擬似
フルスクリーン中の位置（`position: absolute; top: 100%`）だけ。ラッパーが
レターボックスそのものなので、`top: 100%` がそのまま枠の下端になる。

### 擬似フルスクリーン

レターボックスは `#viewport-stage.is-fullscreen` だけが持ち、**高さの基準は
`100dvh`**（`vh` の行は dvh 非対応ブラウザ用に残してある）。スマホの
`100vh` は URL バーを含んだ高さなので、`vh` のままだと横持ちで箱が画面の下へ
はみ出す。

中身（`.video-viewport.pseudo-fullscreen`、縮小経路では `#viewport-frame`）
も字幕も、このラッパーを基準に置いている。**比率やサイズを変えるのは
ここ 1 か所でよい。**

字幕はフルスクリーン中、`top: 100%` で枠のすぐ下（暗幕の上）に出る。

### `body.fs-lock` と暗幕

裏のスクロール止め（`body.fs-lock`）と暗幕（`::before`）は、**幅 768px 未満
または `(pointer: coarse)` のときだけ**掛ける。

マウスの PC で裏をスクロール禁止にするとスクロールバーが消え、裏のページ
全体がスクロールバー幅ぶん、`100vw` 基準のレターボックスがその半分だけ横に
動く（実測でずれは 3px 程度。比率によっては掛けた方が正しい位置になる）。
タッチ画面を条件に加えたのは、横持ちのスマホが幅 768 以上で PC 扱いになり、
**フルスクリーンから抜けられなくなる**ため。

暗幕をタップするとフルスクリーンを抜ける。ハンドラは `#viewport-stage` の
click で、`e.target` がラッパー自身のときだけ反応する（枠の中身や字幕の
タップでは閉じない）。

**暗幕の帯の太さは画面の比率で決まる。** 16:9 ちょうどの画面では帯が 0px に
なり、タップで抜ける出口が無くなる。**これは対応しないと決めている**
（キーボードとボタンからは抜けられる）。

## 直書きしない値

- **スライドの枚数を書かない。** `total-slides` も `playlist-count` も
  `initPlaylist()` が `slideData.length` で埋める
- **総時間を書かない。** `total-time-display` の初期値は `--:--` で、
  `initPlaylist()` が `duration` の合計で上書きする

---

個々の変更の経緯（なぜその条件式になったか、何を試して駄目だったか）は
`archives/todo/` に 1 件 1 ファイルで残してある。
