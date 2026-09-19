# player.html で別のスライドを作る

`player.html` は再生エンジンだけを持っていて、スライドの中身は
`slides/<名前>.js` に分かれている。新しいスライドを作るときは、
**`player.html` は触らず、`slides/<名前>.js` を 1 つ足すだけでよい。**
再生エンジンのほうを直すなら [Developer.md](Developer.md) を読む。

## 手順

1. `player.html` と同じディレクトリの `slides/` に `<名前>.js` を作る
   （`<名前>` に使えるのは英数字・`_`・`-` だけ。それ以外は捨てられる）
2. 中に `deckConfig` と `slideData` を書く（下記）
3. ブラウザで `player.html?deck=<名前>` を開く

`?deck=` を省くと `slides/claude-memo.js` を読む。読み込みに失敗すると、
白画面ではなく「スライドのデータ slides/<名前>.js を読み込めませんでした。」と
表示して止まる。

## `slides/<名前>.js` の中身

グローバルに 2 つ定義する。どちらも `const` で、この名前でないと読まれない。

```js
const deckConfig = {
    title: 'ブラウザのタブに出る文字列',
    heading: 'ヘッダーに出る見出し',
};

const slideData = [
    {
        title: 'プレイリストに出る題名',
        duration: 10,
        narration: '読み上げる文章。',
        render: function() {
            return `<div class="...">…</div>`;
        }
    },
    // 以下、スライドの数だけ続ける
];
```

| キー | 中身 |
|------|------|
| `title` | プレイリストと再生バーの上に出る題名 |
| `duration` | このスライドの秒数。**読み上げの実測値を入れる**（後述） |
| `narration` | 読み上げる文章。字幕にもそのまま出る |
| `render()` | スライドの HTML を**文字列で返す関数**。`#slide-canvas` の `innerHTML` に入る |

**スライドの番号も枚数もどこにも書かない。** `SLIDE 01 / 17` の番号は
`slideData` の並び順から、総枚数と総時間は `slideData.length` と
`duration` の合計から自動で出る。

## `render()` の書き方

差し込み先の `#slide-canvas` は縦に伸びる箱で、その外側が **960x540 の
16:9 の枠**になっている。Tailwind・Google Fonts・FontAwesome は
`player.html` が CDN から読んでいるので、クラス名とアイコンはそのまま使える
（オフラインでは崩れる）。

- **サイズは `cqw` と `clamp()` で書く。** 枠は container query
  （`container-type: inline-size`）で拡大縮小するので、`px` や `rem` の
  直書きは 16:9 を縮めたときに崩れる。
  例: `style="font-size: clamp(1.4rem, 3.2cqw, 2.5rem);"`、
  余白は `px-[3cqw]` `gap-[1.2cqw]` のように書く
- **`md:` などのブレークポイントは枠の中では使わない。** 幅 768px 未満と
  タッチ画面では枠ごと `transform: scale()` で縮める別経路に入るため、
  画面幅で分岐させると意図しない側が選ばれる
- 高さは 540px 相当しかない。既存のスライドは
  `flex flex-col h-full justify-center` で縦に詰めている

既存の 17 枚が `slides/claude-memo.js` にあるので、**近い見た目のものを
コピーして中身を差し替えるのが早い。**

## `narration` と `duration`

`duration` には **Online TTS の音声を `BASE_SPEED_MULTIPLIER` 倍で再生した
実測秒数**が入る。
進行バーと残り時間はこの値で描かれる。実際のスライド送りは
読み上げの終了で起きるので、値がずれてもスライドは飛ばないが、
バーが先に 100% になったり、読み終わってから待たされたりする。

測るには `tools/measure-duration.py` を使う。**`--text` に文章を渡せば、
どのデッキでも測れる。**

```bash
$ tools/measure-duration.py --text 'ここに読み上げる文章'
下書き: 原文 10 字 / 読み 10 字 / 実測 2.376s / BASE_SPEED_MULTIPLIER=1.4 倍速 1.70s -> duration: 2
```

最後に出る `duration: 2` をそのまま書けばよい。`curl` と `ffprobe` が要る。

引数にスライド番号を渡す使い方（`tools/measure-duration.py 2 17`）と
`--write` は **`slides/claude-memo.js` 固定**なので、他のデッキでは使えない。
`--write` を付けると、書き写す代わりに `duration` を直接書き換える。

```bash
$ tools/measure-duration.py --all --write
（17 枚の測定結果）
スライド 15: duration 17 -> 16
claude-memo.js: 1 枚を書き換えた
```

変わった枚だけ出る。書き換えた結果が気に入らなければ `git checkout` で戻す。

書くときの注意:

- **1 文が長いと `TTS_MAX_CHARS` で切れる**（Online TTS の制限）。
  `measure-duration.py` は超えると `★TTS_MAX_CHARS=180 字で切れる` と出す
- 記号や英単語の読みは `player.html` の `prepareSpeechText()` の置換表を
  通してから読み上げられる。読みがおかしいときはそこを見る。
  **置換表を直したら `tools/measure-duration.py` の `RULES` も直す**
  （写しなので、片方だけだと測った秒数がずれる）

## 公開

このディレクトリは `public_html/` の下なので、ファイルを置けばそのまま
公開される。ビルドも依存関係のインストールも無い。

## 最小の例

`slides/sample.js` として保存し、`player.html?deck=sample` で開く。

```js
const deckConfig = {
    title: 'サンプル',
    heading: 'サンプルのスライド',
};

const slideData = [
    {
        title: 'はじめに',
        duration: 5,
        narration: 'これはサンプルのスライドです。',
        render: function() {
            return `
                <div class="flex flex-col h-full justify-center px-[3cqw]">
                    <h1 class="font-extrabold text-slate-50"
                        style="font-size: clamp(1.8rem, 5cqw, 3.8rem);">
                        サンプル
                    </h1>
                    <p class="text-slate-200 mt-[1.5cqw]"
                       style="font-size: clamp(1.15rem, 2.8cqw, 2.1rem);">
                        本文はここに書く
                    </p>
                </div>
            `;
        }
    },
];
```
