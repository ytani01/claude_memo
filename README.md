# yt_slide

**HTML 1 枚で、ナレーション付きのプレゼンが動き出す。**

スライドを順に映しながら読み上げ、字幕を出し、時間どおりに次へ送る。
動画に書き出す必要は無く、URL を渡せばそのまま見てもらえる。

ビルドもインストールも要らない。`player.html` と `slides/` を Web サーバーに
置くだけで公開できる。

## できること

- **読み上げ**。Google Translate TTS と、ブラウザの Web Speech API を
  ボタンで切り替えられる
- **字幕**。ナレーションの全文を画面下に出す。消すこともできる
- **自動再生**。読み終わると数秒待って次のスライドへ。待ち時間は 1〜3 秒から選ぶ
- **再生速度** 0.75〜2.0 倍。進行バーと残り時間は実際の再生時間に追従する
- **フルスクリーン**と、前後送り・頭出し
- **スマホでも操作しやすい**。左右のスワイプでスライドを送り、
  タップで再生と一時停止

## すぐ試す

```bash
python3 -m http.server 8000
# => http://localhost:8000/player.html
```

`player.html?deck=<名前>` で `slides/<名前>.js` を読む。`?deck=` を省くと
このリポジトリの紹介（`slides/readme.js`）が流れる。

## 自分のスライドを作る

**`player.html` は触らない。** `slides/` に JavaScript を 1 つ足すだけ。

```javascript
const deckConfig = { title: 'ブラウザのタブに出る名前', heading: '画面上部の見出し' };

const slideData = [
    {
        title: '1 枚目',
        duration: 10,                    // 読み上げにかかる秒数
        narration: 'ここが読み上げられ、字幕にも出ます。',
        render: function() {
            return `<h1 class="text-4xl font-bold">好きな HTML を書く</h1>`;
        }
    },
];
```

`duration` は目分量で決めず、`tools/measure-duration.py --deck <名前> --all --write`
で実測して入れる。手順は [docs/Usage.md](docs/Usage.md) にある。

## 入っているスライド

| デッキ | 中身 |
|--------|------|
| `readme` | このリポジトリの紹介（既定） |
| `usage` | スライドの作り方 |
| `developer` | `player.html` の作り |
| `claude-memo` | 実例。「私の Claude Code の使い方」17 枚 |

`docs/` の説明と、同じ内容をスライドでも見られる。

## ファイル構成

| ファイル・ディレクトリ | 中身 |
|------------------------|------|
| `player.html` | 外枠の HTML・CSS と再生ロジック。**これ 1 つが本体** |
| `slides/<名前>.js` | スライドのデータ。`player.html?deck=<名前>` で読まれる |
| `docs/` | 説明（下記） |
| `tools/measure-duration.py` | 読み上げ秒数を測り、`duration` に書き戻す |
| `tools/test_measure_duration.py` | 書き戻しの置換を確かめる自己テスト |
| `archives/` | 決着した TODO 項目と、サブエージェントの報告。**現行仕様ではない** |
| `TODO.md` | 進行中の項目と、完了済みの目次 |
| `CLAUDE.md` | Claude Code 向けのプロジェクト規約 |

Tailwind・Google Fonts・FontAwesome・読み上げの音声は外から取るので、
**見る側にネット接続が要る**。`file://` で直接開くのは試していないので、
HTTP で配るのが確実。

## 説明

- [docs/Usage.md](docs/Usage.md) — **スライドを作る人へ。**
  `player.html` は編集せず、`slides/<名前>.js` を 1 つ足す手順
- [docs/Developer.md](docs/Developer.md) — **`player.html` を直す人へ。**
  全体の作り、再生ロジック、読み上げ、レイアウトの事情
