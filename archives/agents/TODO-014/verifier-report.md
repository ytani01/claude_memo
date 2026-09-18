# TODO-014 確認担当の報告

対象: `claude_memo.html` の未コミット差分（`git diff --stat` = 1 file changed, 58 insertions(+), 91 deletions(-)）。

## 検証したこと

### 1. `git status` / 変更範囲
```
$ git status --short
 M claude_memo.html
?? archives/agents/TODO-014/
```
変更されたファイルは `claude_memo.html` のみ。指示の範囲どおり。

### 2. `node --check`（自分で実行）
`<script>`（`src` 無し 2 つ）を正規表現で抜き出し、一時ファイル
（`/tmp/claude-649/scratch/script_0.js`, `script_1.js`、それぞれ 763 文字 /
90493 文字）に保存して実行。
```
== script_0.js ==
exit: 0
== script_1.js ==
exit: 0
```
両方成功。一時ファイルは検証用スクラッチディレクトリのもので、プロジェクトには残していない。

### 3. 削除した識別子の参照漏れ（自分で grep）
```
$ grep -n "accumulated" claude_memo.html   → 該当なし
$ grep -n "slideOffset" claude_memo.html   → 該当なし
$ grep -n "playlist-item-" claude_memo.html
1604:                btn.id = `playlist-item-${idx}`;   （代入のみ、読む側なし）
$ grep -n "getElementById('player-viewport')" claude_memo.html
1750:            const playerViewport = document.getElementById('player-viewport');  （定義の1回だけ）
$ grep -n "PLAYLIST_ITEM|playlistItems|setPlaylistItemState" claude_memo.html
→ 定義（L1584-1591, 1587）と使用（L1597, 1603, 1612, 1616, 1640, 1641）が対応、孤立参照なし
```
報告どおり。

### 4. 9 項目それぞれの実施箇所（diff 該当行）

| # | 項目 | diff 該当箇所 | 判定 |
|---|------|---------------|------|
| 1 | `.video-viewport.pseudo-fullscreen` の重複解消 | 旧 L157-172（基底）/ 旧 L253-266（メディアクエリ）→ 新メディアクエリは `right`/`bottom`/`width`/`height`/`z-index` の5行のみ | 実施（下記5節で計算値一致を確認） |
| 2 | `play()` の非 Promise 分岐削除 | `unlockFallbackAudio()` 内、`const p = ...; if (p && p.then) {...} else {...}` → `play().then().catch()` | 実施（TODO-014のCLAUDE.md注記どおり意図的） |
| 3 | `formatTime()` | `${secs<10?'0':''}${secs}` → `String(secs).padStart(2,'0')` | 実施 |
| 4 | `updateWaveState()` | `if(active){...}else{...}` → `classList.toggle` + `className` 1本の連結 | 実施 |
| 5 | プレイリスト項目クラスの共通化 | `PLAYLIST_ITEM_CLASS` / `_ACTIVE_CLASSES` / `_IDLE_CLASSES` / `setPlaylistItemState()` を新設し `initPlaylist()` から利用 | 実施 |
| 6 | `getElementById('playlist-item-N')` の引き直し廃止 | `playlistItems` 配列に保持、`updatePlaylistSelection()` はその配列を走査 | 実施 |
| 7 | `playerViewport` 定数の利用 | `setFullscreen()`、`fullscreenBtn` click、`Escape` 分岐の3箇所で `document.getElementById('player-viewport')` を `playerViewport` に置換 | 実施 |
| 8 | シークバー対象スライド探索 | 手書き累積ループ → `slideStartTimes.findLastIndex(t => t < targetSec)` | 実施（下記6節で独自に再現検証） |
| 9 | null ガード4つの削除 | `if (stage)`（2箇所）、`if (fsIcon)`、`if (toggleVoiceEngineBtn)`、`if (!tapFeedbackIcon) return` を削除 | 実施 |

9項目すべて、diff 上に該当箇所を確認できた。

### 5. CSS: `.video-viewport.pseudo-fullscreen` の計算結果突き合わせ

基底（旧 L157-172、変更なし）と、旧メディアクエリ（旧 L253-266）、新メディアクエリ（新 L253-259）の
全プロパティを列挙し、カスケード計算（同じセレクタ・同じ詳細度・両方 `!important`、後勝ち。
基底が先、メディアクエリが後）で突き合わせた。

```
prop           base                          old_media(宣言)               old有効値                      new_media(宣言)      new有効値                     判定
border-radius  0                             (基底のみ)                     0                             (無し→基底)          0                             OK
bottom         0                             auto                          auto                          auto                auto                          OK
box-shadow     0 0 80px rgba(0,0,0,0.95)     (基底のみ)                     0 0 80px rgba(0,0,0,0.95)     (無し→基底)          0 0 80px rgba(0,0,0,0.95)     OK
height         100%                          540px                         540px                         540px               540px                         OK
left           0                             0                             0                             (無し→基底)          0                             OK
margin         0                             0                             0                             (無し→基底)          0                             OK
max-height     none                          none                          none                          (無し→基底)          none                          OK
max-width      none                          none                          none                          (無し→基底)          none                          OK
padding        1.5rem                        1.5rem                        1.5rem                        (無し→基底)          1.5rem                        OK
position       absolute                      absolute                      absolute                      (無し→基底)          absolute                      OK
right          0                             auto                          auto                          auto                auto                          OK
top            0                             0                             0                             (無し→基底)          0                             OK
width          100%                          960px                         960px                         960px               960px                         OK
z-index        (無し)                         1                             1                             1                   1                             OK
```
全14プロパティで新旧の計算結果が一致。`border-radius` / `box-shadow` はメディアクエリ側に
元から無く基底のみが効いていたので変化なし、という報告の記述も確認できた。

### 6. シークバー探索ロジックの等価性（独立に再現して検証）

実装報告の1055ケース・差分0件を鵜呑みにせず、`slideData` の実際の `duration`（17枚、
`grep -oP '(?<=duration: )\d+' claude_memo.html` で抽出、合計214秒）を使って
旧ロジック（手書き累積ループ）と新ロジック（`findLastIndex`）を Node で独立実装し、
0〜total を1000分割した点、各スライド開始時刻とその±1e-9、0秒、total秒（計1054点、
実装側の1055件とは重複除去の丸め程度の差で近い値）を突き合わせた。
```
$ node (独自スクリプト)
cases 1054 diffs 0 total 214
```
差分0件。実装報告の主張（境界の扱いが一致）を独立に再現確認できた。

### 7. 「この項目に入れないもの」に手が入っていないか

`git diff claude_memo.html` 全体を `female|Female|fontawesome|FontAwesome|splitForSpeech|vp-scale|SILENT_WAV|getVoices`
で grep したところ、`SILENT_WAV` は変更なしの文脈行としてのみ出現（`+`/`-` 無し）。
女性音声の絞り込み、FontAwesome のインライン SVG 化、`splitForSpeech()`、`--vp-scale`、
`unlockFallbackAudio()` の解錠手順（無音 WAV を volume 0 で鳴らして `then`/`catch` で
`volume = 1` に戻す流れそのもの）には手が入っていない。
`voiceEngineMode === 'speech'` の行は `-`/`+` 両方に出るが、これは項目9で
`if (toggleVoiceEngineBtn) {...}` のガードを外してインデントが1段浅くなっただけで、
中身のロジックは変わっていない（diff を目視で確認済み）。

### 8. 範囲外の変更が混ざっていないか

`git diff claude_memo.html` のハンク数は11。内訳は上記表の9項目に対応
（項目5・6が1ハンクにまとまり、項目7が「setFullscreen 周り」と「Escape」で2ハンクに
分かれ、項目9のガード4つが複数ハンクに分散）。9項目の範囲外と判断できる変更は
見当たらなかった。

ただし実装報告が自ら申告している**範囲を1つ超えた変更**が1件ある。
Escape 分岐の `if (viewport && viewport.classList.contains(...))` の
`viewport &&` の削除。項目9が名指ししたのは `stage`/`fsIcon`/
`toggleVoiceEngineBtn`/`tapFeedbackIcon` の4つで、`playerViewport`（項目7で
定数化した変数）はそこに含まれていない。実装報告どおり、`playerViewport` は
同じファイルの静的要素で項目9と同じ性質のガードではあるが、**チェックリストの
文言には無い**。差分としては1行、実害があるようには見えないが、名指しの範囲を
超えているかどうかの判断は管理者に委ねる。

## 判断が要る点

- 上記「範囲外の変更」に書いた `viewport &&` ガード削除（1箇所）。項目9の
  名指しには含まれないが、実装報告は自己申告した上で「同じ性質」と判断して
  実施している。戻すかどうかは管理者判断。
- 項目2（`play()` の非Promise分岐削除）は、`CLAUDE.md`「この項目に入れないもの」の
  `unlockFallbackAudio()` の解錠と行番号が重なる。実装報告は「解錠の手順自体は
  変えていない」という理由で実施している。これは TODO.md のチェックリストで
  L1186-1195 と明示されており、対象範囲内と判断したが、この解釈が管理者の
  意図と一致するかは確認が要る。

## 確かめられなかったこと

- ブラウザでの実際の見た目・動作確認（PC / 幅390px相当・横持ち相当のタッチ画面での
  通常表示・擬似フルスクリーン、再生系の一通りの操作、横スワイプ）は行っていない。
  静的な差分の読み比べと計算値の突き合わせのみで、実ブラウザでのレンダリングは
  別途確認が必要（レビュー担当か、ブラウザで開ける環境での確認を推奨）。
