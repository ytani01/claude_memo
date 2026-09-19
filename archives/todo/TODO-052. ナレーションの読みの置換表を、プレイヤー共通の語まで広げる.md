# TODO-052. ナレーションの読みの置換表を、プレイヤー共通の語まで広げる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + reviewer |
| 実施 | Opus 5 / effort high | verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 9,708 | 50,521 | 83% |
| verifier | Sonnet 5 | medium | 5,670 | 36,936 | 17% |
| 合計 |  |  | 15,378 | 87,457 | 概算 $1.4 |

- verifier は定義（`~/.claude/agents/verifier.md`）のまま Sonnet 5 / effort
  medium。上書きしていない
- reviewer は使わなかった。分岐や条件式が変わらず、変えたのは置換表の
  並びと `duration` の数値だけだったため
- **この表は、置換表を足した分（`97d62e5`）を含まない。** その作業は
  TODO-053・TODO-054 と時期が重なっていて、`token-usage.py` では範囲を
  切り分けられない。数えたのは TODO-054 の決着コミット以降

## きっかけ

TODO-051 で作った 3 デッキ（`readme`・`user`・`developer`）のナレーションには、
置換表に無い英単語が多く残っていた。読み上げると崩れる。数えたところ
`player.html` が 12 回、`duration` が 8 回、`slides` と `slideData` が各 7 回、
ほかに `deckConfig`、`cqw`、`clamp`、`Online TTS`、`Web Speech`、
`measure-duration.py`、`requestAnimationFrame` など。

それまでの置換表は `claude-memo` のための語が中心で、**プレイヤー自身を
説明する語が入っていなかった**。`user` と `developer` のデッキはその語ばかり
使う。

利用者と決めたこと:

- **先に一括で足してから聴く。** 頻出語をまとめて置換表に入れ、そのうえで
  実際に再生して確かめる（1 語ずつ聴いて決めると回数がかさむ）
- **置換表は `player.html` と `tools/measure-duration.py` の 2 か所にある。**
  片方だけ直すと測った秒数が実際とずれるので、必ず両方直す

## やったこと

1. 置換表に 38 語を足した（`97d62e5`）。ファイル名（`player.html`、
   `measure-duration.py`、`CLAUDE.md`）、スライドデータの用語（`slideData`、
   `deckConfig`、`duration`、`deck`）、CSS と Web API の語（`cqw`、`clamp`、
   `px`、`rem`、`transform`、`requestAnimationFrame`、`container query`）、
   デッキ名（`readme`、`user`、`developer`）など。
   `player.html` と `tools/measure-duration.py` の両方に同じものを入れた
2. その直後に TODO-054 で置換表を `slides/_rules.js` へ外に出したので、
   **今の置換表は 1 か所**になっている
3. 4 デッキの `duration` を測り直した
   （`tools/measure-duration.py --deck <名前> --all --write`）。
   変わったのは 5 枚

   | デッキ | スライド | 旧 | 新 |
   |--------|---------|----|----|
   | `readme` | 1 | 12 | 11 |
   | `readme` | 4 | 8 | 9 |
   | `readme` | 10 | 10 | 9 |
   | `user` | 3 | 10 | 11 |
   | `developer` | 1 | 11 | 12 |

   `claude-memo` は変更なし

## 確かめたこと

- **置換表を当てた後のナレーションに、崩れる英単語が残っていないこと。**
  `prepare()` を 4 デッキ分の narration に当て、残った ASCII 英字を数えた。
  `readme`・`user`・`developer` はゼロ。`claude-memo` に残るのは `AI`・`MCP`・
  `SSH`・`Codex`・`Raspberry Pi` などで、元からそのまま読ませている語
- **`duration` が実測と合っていること。** 変わった 5 枚を測り直し、
  ファイルの値と一致した
- **`player.html` の `prepareSpeechText()` と `tools/measure-duration.py` の
  `prepare()` が、同じ表を同じ順（デッキ側が先、共通が後）で当てていること**
- 変更が `duration:` の数値だけで、ナレーション本文に手が入っていないこと
- `TTS_MAX_CHARS`（180 字）で切れるスライドが 1 枚も無いこと

確認の担当の報告は
[`archives/agents/TODO-052/verifier-report.md`](../agents/TODO-052/verifier-report.md)。

## 見送ったこと

**「実際に再生して読みを聴く」はやらなかった。** 置換表を当てた後の文字列に
英単語が 1 つも残っていないことを確かめたので、それで足りると利用者が判断した。
気になる読みが出てきたら、そのとき別の項目を立てる。

## 分担の振り返り

- **verifier が見つけたこと。** 検証はすべて通った。そのうえで
  `_rules.js` の `px\b` に前側の `\b` が無い点を「将来の誤爆の余地」として
  報告した。調べると `768px` を読ませるために必要な形で、意図どおりだった。
  直していない。**「実害は未確認」と添えて報告し、直すかどうかを管理者に
  委ねた**のは、確認の担当として正しい振る舞い
- **見込みと食い違った点。** reviewer を使わなかった。立てたときは置換表の
  パターンが分岐に当たると見ていたが、実際に変えたのは置換表の並びと
  `duration` の数値だけで、条件式は動いていない。
  置換表そのものの妥当性は verifier の項目 4 で見られた
- **次に同じ規模なら。** 置換表を足す類いの項目は、**「置換後の文字列に
  ASCII 英字が残らないこと」を機械で数えれば大半が片付く**。聴かなくても
  漏れは出せる。main が先にその数え上げをやってから verifier に渡すと、
  verifier は「独立に数え直す」だけで済み、安く回る。今回の main 83% は
  その数え上げと `duration` の測り直し（49 枚 × curl）が主で、削る余地は
  あまり無い
