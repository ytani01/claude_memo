# TODO-054. 読みの置換表を外に出し、デッキごとに足せるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 31,135 | 162,242 | 49% |
| verifier | Sonnet 5 | medium | 40,635 | 179,316 | 21% |
| implementer | Sonnet 5 | medium | 40,489 | 174,891 | 21% |
| reviewer | Sonnet 5 | high | 32,706 | 104,975 | 10% |
| 合計 |  |  | 144,965 | 621,424 | 概算 $8.3 |

- 3 つとも定義のモデル（sonnet）のまま。上書きしていない
- **verifier と reviewer は 1 回目がセッション上限（429）で落ち、立て直した。**
  その分の消費も上の表に入っている

## きっかけ

置換表が `player.html` の `prepareSpeechText()` に直に書いてあったため、
デッキごとの語まで 1 つの表に溜まっていた。`claude-memo` にしか出ない `tmux` や
`Codex` と、`developer` にしか出ない `requestAnimationFrame` が同じ場所に並ぶ。
`tools/measure-duration.py` がその表の写しを持っている二重管理もあった。

TODO-052 で約 30 語を足したところで、利用者から「置換表を外に出して、デッキごとに
カスタマイズできるようにしたい」という要望が出た。

決めたこと:

- **単位はデッキごと**（1 枚ごとには持たせない）
- **共通表は `slides/_rules.js`。** JSON にしない（`player.html` が `fetch` で
  読むことになり、`file://` で開けなくなる）
- **当たる順はデッキが先、共通が後**（デッキ側で読みを上書きできる）

## やったこと

- `slides/_rules.js` を新設し、共通の 24 語を置いた。`player.html` は
  `document.write` の前に `<script>` タグで読む
- `prepareSpeechText()` の `.replace()` の連なりを消し、
  `deckConfig.rules` → `SPEECH_RULES` の順に回す形にした
- デッキだけの語を各デッキの `deckConfig.rules` へ移した
  （readme 6 / user 2 / developer 12 / claude-memo 14）
- `tools/measure-duration.py` は `RULES` の写しをやめ、`slides/_rules.js` と
  デッキのファイルから読む。JS と Python の差（`\/`、`$1`、フラグ）は
  読み込むときに吸収する
- `docs/User.md` に「読みを直す」の節を作り、`docs/Developer.md` と
  `README.md` を今の作りに合わせた

**振り分けの基準は、途中で「今どのデッキに書かれているか」から
「複数のデッキで使い得る語か」へ改めた**（reviewer の指摘）。`TODO.md`・
`TODO-NNN`・`CLAUDE.md`・`Claude Code` は `claude-memo` 専用になっていたが、
他のデッキがその語を使うと共通の素の `TODO`・`Claude` だけが当たって崩れる。
この 4 語は共通へ移した。

`TTS_MAX_CHARS` と `BASE_SPEED_MULTIPLIER` の 2 定数は、今も
`player.html` の写しのまま（置換表と違い、外に出す先が無い）。

## 確かめたこと

- `python3 tools/test_measure_duration.py` が通る
- **4 デッキ 49 枚すべてのナレーションで、読みの結果が 97d62e5 の時点と
  一字一句同じ。** JS を Node の `vm` で動かした結果と、Python の `prepare()` の
  結果の両方で突き合わせた。`duration` は動かない
- 足したテストが、実装をわざと壊すと落ちること（コメントアウト行の読み飛ばし、
  `\'` を含む置換文、`rules:` の無いデッキの 3 件）
- `docs/User.md` に書いた手順のとおりに `rules` を足すと、実際に読みが変わること

## 分担の振り返り

- **reviewer が要修正を 1 件見つけた。** `tools/measure-duration.py` の
  パーサがコメントアウトした行（`// [/…/gi, '…'],`）も拾ってしまう。JS では
  無効なので、Python だけが静かに違う秒数を出す。テストは通っていたので、
  verifier では捕まらない類い。振り分けの基準の穴（上記の 4 語）も reviewer の指摘
- **verifier は「テストが実際に落ちるか」を見て、穴を 1 つ見つけた。**
  `\'` のテストが、旧い正規表現に戻しても通ってしまう例になっていた。
  「テストが通る」ではなく「壊すと落ちる」を確かめさせたのが効いた。
  これは次も必ず頼むこと
- **implementer は指示どおりに動いたが、自分の書いたテストの弱さには
  気づかなかった。** 実装した本人にテストの強さを判断させない
- 見込みとの食い違いは無い。**ただし途中で要望が入って範囲が変わった**
  （TODO-052 の作業中に「外に出したい」が出た）。項目を分けて先に構造を
  直したのは正解で、TODO-052 の測り直しは 1 回で済む
- **次に同じ規模（複数ファイルにまたがる構造の変更）をやるなら、同じ 3 人で
  よい。** 削るなら reviewer ではなく implementer のほう（指示が細かく
  書けている項目は main が直接書いても変わらない）。**reviewer は削らない。**
  この項目で見つかった 2 件は、どちらも「動くか」を見るだけでは出てこない

## 残ること

TODO-052 の聴き確認と `duration` の測り直し。外出しでは読みが変わらないので、
測り直しは TODO-052 の側で 1 回やればよい。
