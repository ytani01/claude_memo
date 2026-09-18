# TODO-037 / TODO-038 の分担

どちらもナレーションの差し替えと `duration` の測り直しで、当たるスライドが
違うだけだったので、**まとめて着手した**（測定は `tools/measure-duration.py 4 17` の
1 回、確認も verifier 1 人でまとめられる）。

- **main**（Opus 5 / effort high）: スライドの文面と HTML の変更、`duration` の測定
- **verifier**（Sonnet 5 / effort medium）: Playwright で実描画を測り、
  枠からのはみ出しと箱の高さを確認

確認を別の担当にしたのは、レイアウトが崩れていないかは実装した本人の
目視では見落とすため。実際、スライド 4 の箱の高さ不揃いは verifier だけが
見つけた。

- [verifier-report.md](verifier-report.md)
