# TODO-058 レビュー報告

対象: `git diff`（`deck` → `slides` の識別子リネーム、旧 `?deck=` の後方互換、
`slides/_rules.js` の読みの置換表、「デッキ」→「スライド一式」の言い換え、
`duration` の測り直し）。「動くか」は verifier の担当のため、ここでは規約・
設計との整合だけを見た。コードは直していない。

## 検討

1. **`archives/agents/TODO-058/wording-report.md` の「duration の測り直し
   対象」が実際の変更より少ない。**
   報告には `slides/readme.js` スライド 9 の 1 件しか挙がっていないが、
   実際に `git diff` を見ると、ナレーションの言い換え（識別子の機械置換
   ではなく、文言そのものの言い換え）は次の 2 件も入っている。
   - `slides/readme.js`「すぐ試す」: 「deckにスライドの名前を…」→
     「URLにスライドの名前を…」
   - `slides/developer.js`「全体の作り」: 「player.htmlはdeckの名前から…」
     → 「player.htmlはURLで指定された名前から…」
   実害は無い。`tools/measure-duration.py --text` で該当 4 箇所（上記 2 件
   と、識別子置換のみの `slides/readme.js`「足すファイルには…」、
   `slides/user.js`「手順2と3」）を実測したところ、現在の `duration` の値
   （11 / 10 / 10、`developer.js` の 18）はいずれも実測値と一致していた
   （実測して確認）。`slides/developer.js`「まとめ」の `duration`
   （14→15）もナレーション文言は変わっていないが実測は 15 で正しい
   （実測して確認）。おそらく main が各スライド一式ごとに
   `--all --write` を流したため、報告に載らなかった箇所も含めて
   全件が測り直されている。**コードは正しいが、報告書だけが実態を
   反映していない。** 次に同じ分担をするときのために、報告の記載範囲を
   実際の差分と揃えるよう伝えるとよい。

## 好みの範囲

1. **`tools/measure-duration.py` の `--slides` の `dest='slices_name'` の件。**
   位置引数 `slides`（スライド番号のリスト）と `--slides`（スライド一式名）
   が同じ語を指すため名前の衝突が起きる、という制約の中では、
   `dest=slides_name` は素直な回避策。ヘルプ表示でも usage 行に
   `[--slides SLIDES_NAME]` と出て、位置引数の `slides` と区別できている
   （`--help` で実行して確認）。他に「`--slides` 自体を別の言葉にする」
   案もあり得るが、CLI の見た目（`--slides <名前>`）を `docs/User.md` /
   `README.md` の記述と揃えたいという TODO の要求を満たすには、
   今回の形が妥当。

## 問題なし

- **`player.html` の `params.get('slides') || params.get('deck')` の空文字
  時の挙動。** `?slides=` のように空文字を渡すと空文字は偽値なので
  `deck` 側にフォールバックする。これは変更前の
  `params.get('deck') || 'readme'` も同じ挙動（空文字は `'readme'` に
  落ちる）だったので、新旧で扱いの一貫性は保たれている。意図した設計
  として問題なし
- **`.replace(/[^\w-]/g, '')` によるサニタイズ。** `slides` と `deck` を
  結合した後に通しており、`/` や `.` は除去される。新しく増えた分岐でも
  トラバーサル等の抜け道は増えていない（未確認だが、旧実装と同じ経路を
  そのまま通しているだけなので新規のリスクは考えにくい）
- **`slides/_rules.js` の置換表。** `deckConfig`/`\bdeck\b` の削除と
  `slidesConfig` の追加はセットで行われており、`\bslides\b` より前に
  `slidesConfig` を置いている（`\bslides\b` は語境界の性質上どのみち
  `slidesConfig` にはマッチしないが、旧 `deckConfig`/`\bdeck\b` の並びを
  踏襲した書き方で一貫している）。`grep -rn deck slides/ player.html
  tools/` で確認した限り、置換対象の「デッキ」を読ませる語は残っていない
- **読みの劣化。** `slides/*.js` に `deck` の文字列が残っていないことを
  確認した（`grep -n "deck" slides/*.js player.html tools/*.py` の結果、
  残るのは `player.html` の旧 `?deck=` 対応コードとそのコメントのみ）
- **`docs/User.md` と `docs/Developer.md` の記述と実装の整合。**
  「当たる順はスライド一式が先、共通が後」という記述は `player.html`
  の `(slidesConfig.rules || []).concat(SPEECH_RULES)` と一致している
- **「旧 `?deck=` も動くことを文書に書かない」という決めごと。**
  `docs/`、`README.md`、`CLAUDE.md` を `grep -rn deck` した結果、
  `TODO.md` 以外に「デッキ」も `deck` も残っていない。`player.html` の
  コメントにだけ理由が残っており、決めごとどおり
- **`CLAUDE.md` の規約（`docs/` に TODO 番号を書かない、`archives/` を
  現行仕様として参照しない）。** 差分を見た限り違反は無い
- **範囲。** `git diff --stat` の対象は TODO-058 の「変えるもの」表に
  挙がったファイル（`player.html`、`slides/*.js` 4 本、`tools/` 2 本）と、
  言い換え対象の `README.md`・`CLAUDE.md`・`docs/*.md` のみ。範囲外の
  変更は見当たらない
- **`slidesConfig` と `slideData` が 1 文字違いで並ぶ件。** TODO の決めごと
  どおり `slideData` は変えていない
- **`python3 tools/test_measure_duration.py`** → `OK`（実行して確認）

## 未確認

- `.replace(/[^\w-]/g, '')` のサニタイズを抜け道にする入力が本当に無いか
  は、既存コードと同じ経路であることの確認に留めた。網羅的な入力走査は
  していない
