# TODO-029 検証依頼

## 目的

フッターと `category` ラベルを消したことで、表示と動作が壊れていないかを確かめる。

## 対象

`claude_memo.html`（`git diff` で差分を見る）。変更は 4 種類:

1. 枠の上のヘッダーから `#slide-category` の span と、その隣のパルス点を削除。
   親の `flex` を `justify-between` → `justify-end` に変更
2. `<footer>` を丸ごと削除
3. JS の `slideCategory` の取得と `slideCategory.textContent = slide.category;` を削除
4. `slideData` 全 17 要素の `category: '...',` を削除

## 完了条件

- `category` と `footer` の語が `claude_memo.html` に 1 つも残っていない
- JS エラーが出ない（ブラウザのコンソールに 1 件も出ない）
- スライドが 17 枚とも表示され、送りと再生が動く
- `SLIDE nn / 17` が枠の右上に残っている（左に寄っていない）
- レイアウトのはみ出しが変更前から増えていない。playwright で 4 条件を測る:
  PC 1280x800 / 横持ち 844x390 の通常とフルスクリーン / 縦持ち 390x844 のフルスクリーン

## やらないこと

**コードは直さない。** 見つけたことを報告するだけ。直すかどうかは管理者が決める。

## 報告

`archives/agents/TODO-029/verifier-report.md` に書く。
**返事は 5 行以内**で、「終わったか・報告ファイルのパス・判断が要る点」だけ。
はみ出しの px は実測値を数字で書くこと（測っていない項目は「測っていない」と書く）。

## 目安

10〜20 分。playwright が使えないときは、その旨を報告して他の項目だけ進める。
