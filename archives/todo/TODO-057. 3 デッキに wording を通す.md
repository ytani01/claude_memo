# TODO-057. 3 デッキに wording を通す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | wording + verifier |
| 実施 | Opus 5 / effort high | wording × 2 + verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 36,633 | 73,903 | 63% |
| wording（1 回目） | Haiku 4.5 | 記載なし | 11,464 | 66,894 | 3% |
| wording（2 回目） | Sonnet 5 | 記載なし | 38,735 | 128,628 | 17% |
| verifier | Sonnet 5 | medium | 19,001 | 82,443 | 17% |
| 合計 |  |  | 105,833 | 351,868 | 概算 $6.3 |

- **wording の 2 回目だけ Sonnet 5 に上書きした。** 定義（`~/.claude/agents/wording.md`）は
  `haiku`。1 回目が薄すぎたため上げた（下の「分担の振り返り」）
- wording の定義に `effort` の行が無い。Haiku は effort に対応しないので
  1 回目は書いても効かず、2 回目は Sonnet 5 の既定（`high`）で動いた
- **この範囲には TODO-058 と TODO-059 の相談も入っている。**
  「デッキ」という語の是非、識別子 `deck` の改名、「HTML 1 枚で動く」の
  誤りの指摘を同じセッションで扱ったため、main の 63% にはその分が含まれる

分担の理由と各担当の報告は [archives/agents/TODO-057/](../agents/TODO-057/README.md)。

## きっかけ

TODO-055 で `README.md` / `docs/User.md` / `docs/Developer.md` の日本語を
推敲したが、同じ内容をスライドにした 3 デッキは手つかずだった。
TODO-051 でデッキを作ったあと文書だけが 2 度動いた（TODO-055、TODO-056）ため、
語が食い違っていた。`docs/Developer.md` の見出しは「副作用のある実装」に
直したのに、`slides/developer.js` のスライド 8 は「触ると鳴らなくなるもの」の
ままだった。

## やったこと

`slides/readme.js` / `slides/user.js` / `slides/developer.js` の
**`title`・`narration`・`render()` が返す日本語**を、対応する `.md` に揃えた。
32 枚のうち 12 枚を直した。

- 用語を揃えた。「要らない」→「不要」、「中身」→「役割」、
  「書き戻す」→「書き込む／入れる」、「当たるスライド」→「対象スライド」、
  「TTS_MAX_CHARS で切る」→「分割」、「それ以外は捨てられる」→「その他は無視される」
- 見出しを 3 つ合わせた。`slides/developer.js` の「触ると鳴らなくなるもの」→
  「副作用のある実装」と「置き場所は選ばない」→「場所を選ばない」、
  `slides/user.js` の「まとめて書き戻す」→「まとめて書き換える」
  （最後の 1 つは、同じデッキ内でナレーションだけ「書き換える」になっていた）
- **事実を 1 つ更新した。** `slides/developer.js` スライド 3 の
  「ローカルを指すのは `slides` を読む 1 か所だけ」を、
  「`slides/_rules.js` と `slides/<名前>.js` の 2 つだけ」にした。
  TODO-054 で置換表を外に出したときに増えていたもので、
  `player.html` の実際の記述とも一致する

**キャッチコピーは文書と揃えなかった。** `slides/readme.js` スライド 1 の
「HTML 1枚で、ナレーション付きのプレゼンが動き出す」は、`README.md` では
「動く」に直したが、表題としての勢いを残した（この文そのものが事実として
誤っている件は TODO-059 で別に扱う）。`slides/user.js` スライド 1 の
`h1`「player.html で別のスライドを作る」も、`docs/User.md` の題
「スライドを作る」と字面は違うが、表紙としてはこちらのほうが内容が伝わるので
そのままにした。

**`duration` を測り直した。** `tools/measure-duration.py --deck <名前> --all --write`
で 3 デッキ分。`readme` 2 枚、`developer` 3 枚が動き、`user` は変化なし。

`slides/claude-memo.js` と `slides/_rules.js`、`.md` は触っていない。

## 確かめたこと

verifier が確認した（[報告](../agents/TODO-057/verifier-report.md)）。

- 削除行と追加行を突き合わせ、**推敲で文や事実が消えていないこと**。
  1 回目の担当が削った「どれも実機で確かめて分かりました。」が
  戻っていることも確認
- 変更行から識別子・ファイル名・オプション名・数値を抜き出して集合で比較 →
  差分ゼロ。`TTS_MAX_CHARS`、`BASE_SPEED_MULTIPLIER`、960x540、0.75〜2.0 倍も確認
- `slides/developer.js` スライド 3 の「2 つだけ」が、`player.html` の実際の
  参照（`slides/_rules.js` と `document.write` の 1 行）と `docs/Developer.md` の
  記述の両方に合っていること
- `slides/_rules.js` と各 `deckConfig.rules` の置換対象の語が、
  ナレーションから消えていないこと
- ナレーション内の半角スペースの入れ方が、デッキの中で揃っていること
- 3 デッキとも `--all`（`--write` 無し）の実測値と `duration` が一致すること
- `node --check` 3 ファイル、`python3 tools/test_measure_duration.py`
- **ブラウザでの表示。** playwright で文言の変わった 12 枚を開き、
  `scrollHeight`/`clientHeight` と `scrollWidth`/`clientWidth` の一致で
  はみ出しが無いことを確認。スクリーンショットは
  `~/tmp/playwright-mcp/TODO-057-*.png` の 12 枚

verifier が `slides/developer.js` スライド 11 の `duration` の不一致
（15 と実測 14）を見つけたが、**測り直し漏れではなかった。**
Google TTS が返す音声の長さが取得のたびに 20.304s / 20.280s とぶれ、
1.4 倍速換算で 14.50 / 14.49 になり、四捨五入の境目をまたいでいた。
main が `--write` で 14 に確定させ、3 デッキとも「変更なし」を確認した。

## 残ること

- **768px 未満のスマホ幅とタッチ画面の別経路は確認していない。**
  ビューポートは 1280x800 のみ
- **音声を鳴らしての字幕との同期は確認していない**（今回の対象外）

## 分担の振り返り

- **1 回目の wording（Haiku 4.5）は失敗した。** 32 枚中 4 枚しか直さず、
  素材の `.md` を読めば分かる不一致（`README.md` の「不要」など）を
  そのまま残した。しかも TODO-055 と同じく、依頼文で明示的に禁じた
  「簡潔化のための削除」をやった。**TODO-055 の振り返りで書いた
  「依頼文に明記する」という対策は効かなかった。** Haiku には、
  この規模を最後まで見る持久力が無い
- **2 回目（Sonnet 5）は 12 枚を直し、1 回目の削除も自分で戻した。**
  判断に迷った点（`slides/user.js` スライド 1 の `h1`）を直さずに
  報告へ回したのも正しい。料金は 1 回目の $0.2 に対して $1.1 だが、
  やり直しの手間を考えれば最初から Sonnet 5 のほうが安い
- **verifier（Sonnet 5 / medium）は期待どおり働いた。**
  `duration` の不一致を数値で捕まえた。原因の診断（測り直し漏れ）は
  外していたが、**確認の担当に原因究明までは求めていない**ので問題ない。
  ブラウザ確認を追加で頼んだときも、目視だけでなく
  `scrollHeight`/`clientHeight` の数値で判定していた
- **次に同じ規模の推敲をやるなら、wording を Sonnet 5 で起動する。**
  `~/.claude/agents/wording.md` は `haiku` のままでよいが、
  **10 ファイル・30 枚を超える推敲では呼び出し側で上書きする。**
  目安は「素材と突き合わせる対象が 10 を超えるか」
- **ブラウザでの確認は、最初の依頼文に入れる。** 今回は後から追加で
  頼んだため verifier が 2 回起動している。文字数が変わる推敲では
  はみ出しが起きうるので、確認項目として最初から書く
