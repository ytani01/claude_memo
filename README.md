# yt_slide

ナレーション付きのスライドをブラウザで再生するプレイヤー。スライドを順に
表示しながら読み上げ、字幕・再生速度・フルスクリーンを切り替えられる。

再生エンジンの `player.html` と、スライドの中身の `slides/<名前>.js` に
分かれていて、**プレイヤーを触らずにスライドだけ足せる。**
実例として「私の Claude Code の使い方」17 枚が入っている。

ビルドも依存関係のインストールも無い。ファイルを置けばそのまま動く
（Tailwind・Google Fonts・FontAwesome・読み上げの音声は外から取るので、
ネット接続は要る）。

## ファイル構成

| ファイル・ディレクトリ | 中身 |
|------------------------|------|
| `player.html` | 外枠の HTML・CSS と再生ロジック。**これ 1 つが本体** |
| `slides/<名前>.js` | スライドのデータ。`player.html?deck=<名前>` で読まれる |
| `slides/claude-memo.js` | 実例のスライド 17 枚（既定のデッキ） |
| `docs/` | 説明（下記） |
| `tools/measure-duration.py` | ナレーションの読み上げ秒数を測り、`duration` に書き戻す |
| `tools/test_measure_duration.py` | 書き戻しの置換だけを確かめる自己テスト |
| `archives/` | 決着した TODO 項目と、サブエージェントの報告。**現行仕様ではない** |
| `TODO.md` | 進行中の項目と、完了済みの目次 |
| `CLAUDE.md` | Claude Code 向けのプロジェクト規約 |

## 手元で動かす

`player.html` と `slides/` があるディレクトリで:

```bash
python3 -m http.server 8000
# => http://localhost:8000/player.html?deck=claude-memo
```

`?deck=` を省くと `slides/claude-memo.js` を読む。`file://` で直接開くのは
試していないので、HTTP で配るのが確実。

## 説明

- [docs/Usage.md](docs/Usage.md) — **スライドを作る人へ。**
  `player.html` は編集せず、`slides/<名前>.js` を 1 つ足す手順
- [docs/Developer.md](docs/Developer.md) — **`player.html` を直す人へ。**
  全体の作り、再生ロジック、読み上げ、レイアウトの事情
