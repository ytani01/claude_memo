# TODO-058. 「デッキ」をやめ、識別子の `deck` も `slides` に変える

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + wording + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + wording + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 84,773 | 257,690 | 65% |
| verifier | Sonnet 5 | medium | 28,520 | 128,538 | 11% |
| implementer | Sonnet 5 | medium | 27,888 | 83,927 | 10% |
| wording | Haiku 4.5 | 記載なし | 50,899 | 131,524 | 9% |
| reviewer | Sonnet 5 | high | 18,578 | 71,628 | 5% |
| 合計 |  |  | 210,658 | 673,307 | 概算 $13.5 |

- モデルはすべて定義ファイルのまま。上書きしていない
- wording は定義に `effort` の行が無い（Haiku は effort に対応しない）

分担の理由と各担当の報告は [`archives/agents/TODO-058/`](../agents/TODO-058/README.md)。

## きっかけ

「デッキ」はスライドの束を指すつもりで使ってきたが、一般的な日本語ではない。
カセットデッキやカードゲームを連想されやすく、特に**読み上げでは耳で意味が
取れない**。`slides/_rules.js` に `deck`→「デッキ」の読みの置換があること自体、
識別子が音声に漏れている証拠になっていた。

`deckConfig` は `docs/User.md` で利用者に書かせる名前なので、
**文章側だけを直しても「デッキ」は消せない。**

日本語は「スライド一式」、識別子は `slides` に統一すると決めた。

## やったこと

### 1. 識別子のリネーム

| いま | あと |
|------|------|
| `?deck=<名前>` | `?slides=<名前>` |
| `deckConfig` | `slidesConfig` |
| `--deck` | `--slides` |
| `deck-heading` | `slides-heading` |
| `deckName` | `slidesName` |
| `DEFAULT_DECK` | `DEFAULT_SLIDES` |
| `deck_rules_from_text` | `slides_rules_from_text` |
| `load_deck_rules` | `load_slides_rules` |

`slideData` は 1 文字違いで並ぶが、決めたとおり変えていない。

`tools/measure-duration.py` の `--slides` は、位置引数の `slides`
（スライド番号のリスト）と `dest` が衝突するため `dest='slides_name'` に
した。理由はコードのコメントに残してある。

### 2. 旧 `?deck=` も受ける

公開済みのリンクが切れるため、`player.html` で `slides` を先に見て、
無ければ `deck` を見る。

```javascript
const params = new URLSearchParams(location.search);
const slidesName = (params.get('slides') || params.get('deck')
    || 'readme').replace(/[^\w-]/g, '');
```

**この後方互換は文書に書かない。** 書くと利用者が古い書き方を使い続けるため、
`player.html` のコメントにだけ理由を残した。

`?slides=` と空で渡すと `deck` 側に落ち、どちらも無ければ `readme` になる。
変更前の `params.get('deck') || 'readme'` と同じ扱いで、一貫している。

### 3. 読みの置換表の入れ替え

`slides/_rules.js` から 2 行を外し、1 行足した。

```diff
-    [/deckConfig/gi, 'デッキ コンフィグ'],
-    [/\bdeck\b/gi, 'デッキ'],
+    [/slidesConfig/gi, 'スライズ コンフィグ'],
```

`slidesConfig` の行は `[/\bslides\b/gi, 'スライズ']` より前に置いた。
語境界の性質上どのみち `\bslides\b` は `slidesConfig` に当たらないが、
外した 2 行と同じ並びにしてある。

### 4. 日本語の言い換え（44 箇所）

「デッキ」を「スライド一式」などに言い換えた。機械的な一括置換にはせず、
不自然になる箇所は文ごと組み立て直した（`README.md` の表の見出し、
「デッキごとに」「4 デッキ」のような言い回し）。

ナレーションは、リネームで紛らわしくなった 2 箇所も直した。

| ファイル | 旧 | 新 |
|----------|----|----|
| `slides/developer.js`「全体の作り」 | `player.htmlはslidesの名前からslides配下の…` | `player.htmlはURLで指定された名前から、slides配下の…` |
| `slides/readme.js`「すぐ試す」 | `slidesにスライドの名前を指定すると` | `URLにスライドの名前を指定すると` |

`slides` が「URL のパラメータ名」と「ディレクトリ名」の 2 つの意味で並び、
耳で聞いて区別できなくなっていた。

### 5. `duration` の測り直し

4 つとも `tools/measure-duration.py --slides <名前> --all --write` を流した。
変わったのは `slides/developer.js` の 2 枚だけ。

| スライド一式 | スライド | 旧 | 新 |
|--------------|----------|----|----|
| `developer` | 4 | 16 | 18 |
| `developer` | 11 | 14 | 15 |

## テスト

- `python3 tools/test_measure_duration.py` → OK。
  `slides/_rules.js` の行を一時的に消すと落ちることも確かめた（確認後に復元）
- `node --check` で `player.html` と `slides/*.js` 4 本の構文
- `?slides=`、旧 `?deck=`、両方無し（既定 `readme`）、両方あり（`slides` が勝つ）
  の 4 通り
- `tools/measure-duration.py` を `--slides` あり／なし、`--text`、番号指定、
  `--all` で実行
- `--write` 無しで表示される値と、ファイルに書かれた `duration` が
  4 つとも一致すること
- `grep` で `deck` と「デッキ」が残っていないこと
  （残るのは `player.html` の後方互換の 2 行だけ）

verifier・reviewer とも要修正は 0 件。

## 分担の振り返り

### 各担当が何を見つけたか

- **implementer** は `docs/Developer.md:109` の `deckConfig.rules` が
  依頼の対象表から漏れていることに気づき、勝手に直さず報告した。
  これは main の依頼漏れだった。`--slides` の `dest` 衝突も自分で解いて
  理由をコメントに残した
- **wording** は 44 箇所の言い換えを終えたが、**依頼に明記した
  `slides/developer.js` のナレーションの直し（`slides` が 2 つの意味で
  並ぶ件）に手を付けなかった。** 報告では「ナレーション変更は
  `slides/readme.js` スライド 9 のみ」としていたが、実際の差分は 5 行あった。
  main が差分を見て気づき、自分で直した
- **verifier** は 9 項目すべてを確かめ、問題を見つけなかった。
  「わざと壊すと落ちるか」も実施して復元まで確認している
- **reviewer** も要修正 0 件。ただし **wording の報告と実際の差分の
  食い違いを指摘した**（コードは正しいが報告が実態を反映していない）。
  verifier はコードだけを見ていたので、この食い違いは捕まえていない

### 見込みと食い違ったのはなぜか

担当の顔ぶれは見込みどおり。食い違ったのは**依頼の書き方**のほうで、
2 つ出た。

1. **対象ファイルの表に `docs/Developer.md` を入れ忘れた。**
   「`deckConfig` → `slidesConfig`」の行に置き場所を列挙したが、
   `docs/User.md` だけ書いて `docs/Developer.md` を落とした。
   列挙する形は書き漏らすので、**`grep` のコマンドを渡して
   「これで出るもの全部」と書くほうが確実**だった（wording への依頼では
   そうしてあり、そちらは漏れなかった）
2. **Haiku に「文脈を読んで直す」判断を混ぜた。** wording への依頼 5 は
   「紛らわしいので耳で分かる言い回しに直せ」という判断の要る指示で、
   一括置換の指示 44 箇所の中に埋もれていた。**Haiku は機械的な置換は
   こなしたが、判断の要る 1 件だけを落とした。**

### 次に同じ規模の項目をやるなら

- **依頼の対象範囲は、ファイルの列挙ではなく `grep` のコマンドで渡す。**
  列挙は書き漏らす。「このコマンドで出る全部」と書けば漏れない
- **wording（Haiku）には、機械的な置換だけを渡す。** 文脈を読んで
  言い回しを作り直す作業を同じ依頼に混ぜると、そこだけ落ちる。
  判断の要る言い換えは、件数が少ないなら main が自分でやるほうが早い
  （今回 2 件で、main の手直しは数分だった）
- **報告の記載漏れは reviewer が捕まえた。** verifier はコードしか見て
  いないので、担当の報告と実際の差分の突き合わせは reviewer の側に残る。
  **「差分と報告が合っているかも見る」を reviewer への依頼に明記する**と
  偶然に頼らずに済む
- 料金は main が 65%（$8.7）。差分の確認と手直しを main がやったぶんが
  大きい。wording が判断の要る箇所を落とさなければ、main の手戻りは
  減らせた
