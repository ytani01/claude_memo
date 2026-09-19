# TODO-049 確認報告

## 確認した項目と結果

### 1. 定数名の実在と対応

`player.html` に以下がすべて実在し、綴りも文書の説明も一致する。

- `BASE_SPEED_MULTIPLIER = 1.4`（494行）
- `SPEECH_CHARS_PER_SECOND = 4.5`（516行）
- `TTS_END_MARGIN_MS = 3000`（519行）
- `TTS_MAX_CHARS = 180`（521行）
- `splitForSpeech(text, maxLen = 40, minLen = 20)`（629行）— `maxLen` の既定値は 40 で、`docs/Developer.md` は数値を書かず「既定値ぶん」とだけ書いており、値の食い違いは無い

問題なし。

### 2. 「時間軸に `BASE_SPEED_MULTIPLIER` を掛けない」節の意味

旧文「時間軸のほうに 1.4 を掛けると」→新文「時間軸のほうにも掛けると」。
`getEffectiveSpeed = playbackRate * BASE_SPEED_MULTIPLIER`（495行）で、
読み上げ速度には掛けている旨を直前の文で述べているので、「にも」への
言い換えは元の意味（読み上げにだけ掛け、時間軸には掛けない）を保っている。
問題なし。

### 3. `tools/measure-duration.py` の実行例

`curl`・`ffprobe` とも利用可能だったので実際に実行した。

```
$ tools/measure-duration.py --text 'ここに読み上げる文章'
下書き: 原文 10 字 / 読み 10 字 / 実測 2.376s / BASE_SPEED_MULTIPLIER=1.4 倍速 1.70s -> duration: 2
```

`docs/Usage.md` 87行の実行例と文字どおり一致（実測秒数まで含めて完全一致）。

### 4. 180 字超の表示

200 字のテキストで実行し、次を得た。

```
下書き: 原文 200 字 / 読み 200 字 ★TTS_MAX_CHARS=180 字で切れる / 実測 23.016s / BASE_SPEED_MULTIPLIER=1.4 倍速 16.44s -> duration: 16
```

`docs/Usage.md` 98行が説明する `★TTS_MAX_CHARS=180 字で切れる` という形と一致。

### 5. 残すと決めた数値がそのまま残っているか

`767.98px`（Developer.md:138）、`324 秒`（Developer.md:79）、
`0.34〜0.77`（Developer.md:152）、`3px`（Developer.md:186）、
`15 秒`（Developer.md:121）は、いずれも数値のまま残っており、
誤って定数名に置き換えられていない。問題なし。

### 6. 置き換え漏れ

**`960x540` が置き換わっていない（要判断、下記）。**
それ以外の置き換え漏れ・過剰な置き換えは見当たらなかった
（`1.4` `180` `4.5` `40` `3 秒足した` などの文字列を
`docs/Developer.md`・`docs/Usage.md`・`tools/measure-duration.py` で
grep したが、残っているのは `tools/measure-duration.py:32` の定数定義行
自身、`docs/Usage.md:63` の無関係な CSS `clamp(1.4rem, ...)`、
実行例の出力文字列のみで、いずれも問題ない）。

## 判断が要る点

**`960x540` を `SLIDE_BASE_WIDTH_PX` に置き換えていない点が、
依頼された確認範囲と `TODO.md` の計画とで食い違っている。**

- 今回私が受け取った確認依頼の文面には「残すと決めたのは
  `767.98px`、`324 秒`、`0.34〜0.77`、`3px`、`15 秒`、`960x540`
  （CSS に直書きされている値で、`SLIDE_BASE_WIDTH_PX` はその写しなので
  置き換えない）」とあり、`960x540` は意図的に据え置く対象として
  示されていた。
- 一方 `TODO.md` の TODO-049 の節（39〜43行のチェックリスト、
  49〜59行の対応表）を読むと、`Developer.md` 144行・`Usage.md` 56行の
  `960x540` は `SLIDE_BASE_WIDTH_PX`（`SLIDE_ASPECT_RATIO` と組）へ
  置き換える対象として明記されており、「6 箇所」「3 箇所」という
  チェックリストの件数もこの2箇所を含めて数えないと合わない。
  90〜91行の「定数に対応しない数値はそのまま残す」の一覧にも
  `960x540` は含まれていない。
- 実際の作業ツリーの差分では、`Developer.md:144`・`Usage.md:55` の
  `960x540` はどちらも変更されておらず、数値のまま残っている
  （`docs/Developer.md:144-145`、`docs/Usage.md:55` を直接確認した）。

`TODO.md` を書いた時点の計画と、私が受け取った確認依頼の指示が
食い違っている。これが「計画を書いたあとで `960x540` は残す方針に
変えたが `TODO.md` を更新し忘れた」のか、「実装漏れで、本来は
`SLIDE_BASE_WIDTH_PX` に置き換えるべきだった」のかは、この場では
判断できない。どちらであるかは、実装を指示した管理者（main）の
判断が要る。

## 検証したコマンド

- `git diff docs/Developer.md docs/Usage.md tools/measure-duration.py`
- `grep -n` で `player.html` の定数定義と `docs/`・`tools/` の
  該当箇所を確認
- `tools/measure-duration.py --text '...'` を通常長・180字超の
  2パターンで実行（`curl`・`ffprobe` とも利用可能だった）

## 確かめられなかったこと

- `TODO.md` のチェックボックス自体はまだ未チェックのままだった
  （実装がまだ完了扱いになっていないのかもしれない）。これも含めて
  `960x540` の扱いは管理者の判断待ち。
