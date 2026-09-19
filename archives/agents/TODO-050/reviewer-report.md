# TODO-050 reviewer 報告

## 要修正

1. `CLAUDE.md:9` / 「ビルド、依存関係のインストール、テストは無い。」が
   古いまま / この差分で `tools/test_measure_duration.py` を追加し、
   `docs/Developer.md` 側は「テストは `tools/test_measure_duration.py` の
   1 本だけ」に更新済みなのに、ほぼ同じ主張を持つ `CLAUDE.md` 側だけ
   取り残されている（`git diff --stat` で `CLAUDE.md` は変更対象外と確認済み）。
   対で保守すべき記述の片方だけが変わっている。直すなら
   `CLAUDE.md` の「テストは無い」を実情に合わせて外すか書き換える。

## 検討

2. `docs/Developer.md:17` / 1 行が 185 バイトあり、同ファイルの他の段落行
   （105〜114 バイト程度で改行している）から見て異常に長い
   （`awk '{print length}' docs/Developer.md` で実測）。既存の折り返し習慣に
   合わせて 2 行程度に割るのが自然。

3. `tools/measure-duration.py:117-123`（`write_durations()`）/
   `text = SRC.read_text(...)` で読んだあと、直後の `narrations()` 呼び出しが
   `SRC.read_text(...)` をもう一度実行しており、同じファイルを 2 回読んでいる
   （`main()` 側の `found = narrations()` と合わせると都合 3 回）。実害はほぼ
   無いが、`len(re.findall(..., text))` のように既読の `text` を使い回せば
   二重読みを避けられる。

4. `tools/measure-duration.py:91-92`（`DURATION_RE`）/ 「`duration: N,\n
   *narration: '`」という並びに依存する正規表現で、依頼どおり
   `render()` の返す HTML 文字列内に同じ並びが偶然現れると誤爆しうる作り。
   ただし実測では `slides/claude-memo.js` 中の `duration:` は 17 件のみで
   すべて本来のプロパティ（`grep -c duration: slides/claude-memo.js` = 17、
   `render()` 内に同種の並びは無し）。`write_durations()` の
   `found != len(narrations())` チェックと、`test_measure_duration.py` が
   `render` 内の `duration: 99,` を巻き込まないことを明示的に確認しており
   （実行して `OK` を確認済み）、現状の安全網としては足りている。今後
   `render()` にスライドデータの書き方をそのまま見せるような文面
   （このデッキ自体が Claude Code の使い方を説明するので、あり得なくはない）
   を足すときは注意が要る、という程度の指摘。

## 確認できた点（問題なし）

- **書き戻しの安全さ。** `measure()`（`curl`/`ffprobe`）が失敗すると例外が
  `main()` のループ内で送出され、`write_durations()` に到達する前に
  プロセスが終了する。`SRC.write_text()` は全スライドの測定が終わったあと
  一度だけ呼ばれるので、途中失敗時にファイルが半端に書き換わることは無い
  （コード読みで確認。一時ファイル→rename の完全なアトミック書き込みでは
  ないが、TODO-050 で「戻すのは git の差分で足りる」と決めた前提と整合する）。
- `--text` と番号を混ぜたとき、`--text` 分は `number=None` のため
  `updates` に入らず書き戻し対象にならない。`--write` を `--text` 単独と
  組み合わせた場合は `args.slides or args.all` が偽になるため
  `parser.error()` で弾かれる（コード読みで確認、ネットワークに触れる前に
  終了する分岐）。
- `apply_durations()` / `write_durations()` の分割は、ファイルに触れない
  純粋な置換ロジックをテスト可能にするためのもので、過剰な分割ではない。
  `tools/test_measure_duration.py` はこの分割を活かして `apply_durations()`
  だけを見ており、ネットワーク不要（実行して `OK` を確認済み）。
- `player.html` の写しである旨の docstring 注意書き（定数・`RULES` の写し）
  は今回の差分でも維持されており、薄まっていない。
- README.md / docs/Usage.md の追記は実装と一致（コード読みで突き合わせ済み。
  動作確認自体は verifier 側で実施・一致を確認済み）。日本語も直訳調ではなく、
  既存の「書き戻す」という言い回し（`TODO.md` の項目名と同じ）をそのまま
  使っている。

## 判断が要る点

- 要修正 1 件（`CLAUDE.md` の古い記述）をこの場で直すか、TODO-050 の範囲外
  として別項目にするかは main の判断。
