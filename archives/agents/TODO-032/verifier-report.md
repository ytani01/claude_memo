# TODO-032 検証報告

## 結論

**問題無し。** TODO-030 で見つけたスライド 15 のずれは解消され、完了条件は
すべて満たしている。コードは直していない。

## 変更ファイルの範囲

`git diff HEAD` で確認。`claude_memo.html`（スライド 15 の
`duration: 17` → `16`）と `CLAUDE.md`（合計 316 → 315 秒）に加えて、
`TODO.md` の TODO-032 自身の節（原因調査の追記とチェック）が変更されている。
依頼書は「`git diff` で見えるのはこの 2 行だけのはず」としていたが、
`TODO.md` の更新は項目自身の記録更新であり、コードやレイアウトへの
影響は無い。指示外のコード変更は無い。

## 1. `tools/measure-duration.py --all` と `duration` の全枚一致

```
$ tools/measure-duration.py --all
スライド 1: ... -> duration: 16
スライド 2: ... -> duration: 19
スライド 3: ... -> duration: 19
スライド 4: ... -> duration: 19
スライド 5: ... -> duration: 21
スライド 6: ... -> duration: 19
スライド 7: ... -> duration: 19
スライド 8: ... -> duration: 19
スライド 9: ... -> duration: 18
スライド 10: ... -> duration: 21
スライド 11: ... -> duration: 19
スライド 12: ... -> duration: 15
スライド 13: ... -> duration: 17
スライド 14: ... -> duration: 17
スライド 15: ... -> duration: 16
スライド 16: ... -> duration: 18
スライド 17: ... -> duration: 23
```

`grep -oP "duration:\s*\K[0-9]+" claude_memo.html` で拾った実装値
（16, 19, 19, 19, 21, 19, 19, 19, 18, 21, 19, 15, 17, 17, 16, 18, 23）
と 17 枚分すべて突き合わせた。**17 枚全枚一致。** TODO-030・031 の時点で
残っていたスライド 15 のずれ（実測 16 / 実装 17）は解消されている。

## 2. `duration` 合計

```
grep -oP "duration:\s*\K[0-9]+" claude_memo.html | awk '{s+=$1} END {print s, NR}'
→ 315 17
```

17 枚の合計は **315 秒**。`CLAUDE.md` の記述（315）と一致。
`formatTime(315)` を Node で確認 → `5:15`（一致）。

## 3. `#total-time-display` の初期表示

Playwright（PC 1280x800）でページを開いた直後の `#total-time-display`
の値を読んだ。

```
total-time-display= 5:49
```

`duration` 合計 315 秒 + `pauseSeconds`（既定 2 秒）× 17 枚 = 349 秒
（`315 + 2*17 = 349`）。`formatTime(349)` は `5:49` で、実測値と一致。
依頼書のとおり、この値は `duration` の合計（`5:15`）とは別物であり、
`5:15` になっていなくてよいことを確認した。

## 4. JS エラー・送り/再生

```
total-slides= 17
slide-num after 16 next= 17
CONSOLE_ERRORS: []
```

コンソールエラー無し。17 枚への送り、play/pause も問題無し。

## やらなかったこと・判断できないこと

特になし。レイアウトの測り直しは依頼どおり行っていない（画面は
変えていないため）。
