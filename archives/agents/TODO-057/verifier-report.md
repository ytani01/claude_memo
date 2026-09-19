# TODO-057 確認報告（verifier）

## 走らせた検証

- `node --check slides/developer.js` / `slides/readme.js` / `slides/user.js`
  → いずれも構文エラー無し（終了コード 0）
- `python3 tools/measure-duration.py --deck <名前> --all`（`--write` 無し）を
  readme / user / developer の 3 デッキとも実行 → 終了コード 0
- `python3 tools/test_measure_duration.py` → `OK`、終了コード 0

## duration の実測一致（確認事項 6）

readme（10 枚）・user（11 枚）は、ファイルの `duration:` と実測値が
**全枚一致**した。

developer（11 枚）で **1 件だけ不一致**を見つけた。

- スライド 11（「まとめ」）: ファイルは `duration: 15`。
  `measure-duration.py --deck developer --all` を 2 回実行し、どちらも
  `スライド 11: ... -> duration: 14` （実測 20.280s）で、15 にはならない。

原因の推定（未確認）: `archives/agents/TODO-057/wording-report.md` による
と、main が `--write` で測り直した**あとに**、2 度目の wording 担当が
スライド 11 の narration を「鳴らなくなる3つの注意点」→「副作用のある
3つの注意点」に直している（スライド 8 の新しい見出しに合わせるため）。
この文字差し替えで読み上げの尺が 1 秒短くなったが、`duration` は
測り直されていない。他の narration を書き換えた箇所（developer スライド
2・3・8、readme スライド 1・2・8、user スライド 1・9）はすべて実測と
一致しており、不一致はこのスライド 11 のみだった。

**対応が要る**: `tools/measure-duration.py --deck developer --all --write`
を再度走らせて `duration: 15` → `14` に直すか、director の判断を仰ぐ。

## 情報の欠落（確認事項 1）

`slides/developer.js` スライド 8 の narration「どれも実機で確かめて
分かりました。」は現在のファイルに**残っている**（1 度目の担当が削り、
2 度目が戻したとおり）。他の narration の diff も見比べたが、1 文に
2 つあった情報が 1 つに減っている箇所は見当たらなかった。

## 変えてはいけないものの確認（確認事項 2）

`git diff` の追加・削除行からインラインコード・識別子・数値を拾って
比較した。`--deck` `--all` `--write` `--text`、`BASE_SPEED_MULTIPLIER`、
`TTS_MAX_CHARS` はいずれも変更行に現れるが文字列そのものは変わっていない
（前後の日本語だけが変わっている）。

`readme.js` スライド 2 で「0.75倍から2倍」→「0.75倍から2.0倍」に
変わっている点だけ数字表記が増えているが、`player.html` の速度選択肢を
確認すると最大値は `<option value="2">速度 2.0x</option>` で、実際の表記に
合わせた修正であり、指示にある「0.75〜2.0倍」とも一致する。問題無いと
判断した。

HTML 構造・`class`/`style` 属性・アイコン指定・数値（960x540、16:9、768px
など）は diff に現れず、変更されていない。

## 事実の正しさ（確認事項 3）

`slides/developer.js` スライド 3 の
「`player.html` がローカルを指すのは `slides/_rules.js` と
`slides/<名前>.js` の2つだけ」を `player.html` で確認した。

```
464: <script src="slides/_rules.js"></script>
471: document.write(`<script src="slides/${deckName}.js"><\/script>`);
```

ローカルの `slides/` を指す `<script src>` はこの 2 か所のみで、記述は
正確。`docs/Developer.md` 29〜30 行目の記述とも文言まで一致している。

## 置換表の語（確認事項 4）

`slides/_rules.js` の `SPEECH_RULES` と各デッキの `deckConfig.rules` を
確認した。置換対象の語（`player.html`、`slides`、`duration`、`deck`、
`measure-duration.py`、`User.md` など）は、変更後の narration からも
消えていない。narration の書き換えはいずれも置換対象になっていない
語（「要らない」「無く」「書き戻す」など）の言い換えだった。

## 表記の揺れ（確認事項 5）

`slides/developer.js` スライド 8 の narration
「Audio要素は使い回すこと、Web Speechは文章を分けて読ませること」は、
半角スペース無しで、同じデッキの他の narration（スライド 7 の
「Online TTSとWeb Speechの2系統」など、英単語列の内部にはスペースを
入れるが日本語との境には入れない書き方）と揃っている。1 度目の担当が
入れたスペースは 2 度目で外されている。

## 変更ファイルの範囲（確認事項 9）

```
$ git status --porcelain
 M slides/developer.js
 M slides/readme.js
 M slides/user.js
?? archives/agents/TODO-057/
```

指示どおり、`slides/` の 3 ファイルと `archives/agents/TODO-057/` のみ。

## 確かめられなかったこと・判断できないこと

- developer スライド 11 の `duration` 不一致について、`--write` で
  直すべきか、director が narration の変更自体を見直すべきかは判断できない
  （元の narration に戻すか、新しい narration のまま測り直すかは方針の
  問題であり、こちらでは決められない）
- 実測秒数は Online TTS を実際に呼ぶため、ネットワークの状態などで
  多少の揺れがあり得る。ただし今回は 2 回とも同じ 14 秒だったので、
  単発の揺れではないと考える

## 追記：duration 不一致の決着（coordinator からの説明を反映）

coordinator によると、developer スライド 11 の `duration` 不一致は測り直し
漏れではなく、Google TTS が返す音声長が取得のたびに 20.304s / 20.280s と
ぶれ、1.4 倍速換算で 14.50 / 14.49 秒になり四捨五入の境目をまたいだため、
とのこと。現在のファイルを見ると `duration: 14` になっており
（`slides/developer.js` 304 行目）、`--write` で確定させたとおりになっている
ことを確認した。この経緯自体はこちらでは再現・検証していない
（coordinator からの報告をそのまま記載）。

## 追記：ブラウザでの表示確認

`python3 -m http.server 8791` をリポジトリのトップで立て、Playwright
（Chromium）で `http://localhost:8791/player.html?deck=<名前>` を開き、
`renderSlide(index, true)` を直接呼んで文言が変わった 12 枚を表示した。

対象: readme 1, 2, 8 / user 1, 3, 10 / developer 2, 3, 6, 7, 8, 11

各スライドで `#slide-canvas`（スライド本文が入るコンテナ。
`overflow-hidden`）の `scrollHeight`/`clientHeight` と
`scrollWidth`/`clientWidth` を取った。12 枚とも

```
scrollWidth === clientWidth  (868 === 868)
scrollHeight === clientHeight (428 === 428)
```

で、**はみ出し・クリップは検出されなかった**。`scrollHeight` が
`clientHeight` を超えていれば `overflow-hidden` で見えない形の
はみ出しが起きているはずだが、その差は無かった。

特に懸念された developer スライド 3（「場所を選ばない」カード文言が
「slides/_rules.js と slides/&lt;名前&gt;.js の2つだけ」に伸びた箇所）も、
スクリーンショットで見ても 1 行に収まっており、下のカードとの重なりも
無い。

数値だけでなく、対象 12 枚すべてのスクリーンショットを目視した。
いずれも折り返し・重なり・枠からのはみ出しは無い。

- readme 1（キャッチコピー。長い見出しが 2 行になるが、下の本文・余白との
  重なりは無い）
- readme 2（「再生速度 0.75〜2.0 倍」のカード）
- readme 8（duration の測り方。コードブロックと本文の重なり無し）
- user 1（`player.html` で別のスライドを作る、の見出し）
- user 3（「その他は無視される」の注意書き、1 行に収まっている）
- user 10（「まとめて書き換える」。コマンド行と注意書きに重なり無し）
- developer 2（リポジトリの構成。表の「役割」列、行の高さも揃っている）
- developer 3（最も懸念された「場所を選ばない」。2つだけの文言が
  1 行に収まり、下のカードとも重ならない）
- developer 6（duration は実測値。2 行になった本文と警告ボックスの重なり
  無し）
- developer 7（読み上げの2系統。表の「TTS_MAX_CHARS で分割」列、はみ出し
  無し）
- developer 8（副作用のある実装。3 枚のカードとも 1 行に収まっている）
- developer 11（まとめ。4 枚のカードとも 1 行に収まっている）

### 保存したスクリーンショット

`~/tmp/playwright-mcp/` に以下の 12 枚を保存した（1280x800 のビューポート）。

```
TODO-057-readme-01.png
TODO-057-readme-02.png
TODO-057-readme-08.png
TODO-057-user-01.png
TODO-057-user-03.png
TODO-057-user-10.png
TODO-057-developer-02.png
TODO-057-developer-03.png
TODO-057-developer-06.png
TODO-057-developer-07.png
TODO-057-developer-08.png
TODO-057-developer-11.png
```

### 確かめられなかったこと（ブラウザ確認分）

- ビューポートは 1280x800（デスクトップ幅）のみで確認した。指示にあった
  768px 未満（スマホ幅）やタッチ画面向けの別経路（`player.html` に記載が
  ある）は今回の対象スライドではなく、確認していない
- 音声を実際に鳴らして字幕とナレーションの同期がずれていないかは、
  指示どおり確認していない（消音・自動再生無しでスライド送りのみ）
（対象 12 枚は数値と目視の両方で確認できた）
