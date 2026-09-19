#!/usr/bin/env python3
"""ナレーションの読み上げ秒数を測り、`duration` に入れる値を出す。

`slideData` の `duration` には「Online TTS の音声を 1.4 倍速で再生した
実測秒数」が入っている（TODO-018）。ナレーションや読みの置換表を変えると
長さが変わるので、当たるスライドを測り直す必要がある。

    tools/measure-duration.py 2 17     # スライド 2 と 17 を測る
    tools/measure-duration.py --all    # 17 枚すべて
    tools/measure-duration.py --text 'ここに下書き'

`--text` は、差し替える前に案の長さを見るためのもの。

**この下の定数と RULES は player.html の写し。**
`prepareSpeechText()` の置換表、`TTS_MAX_CHARS`、`BASE_SPEED_MULTIPLIER` を
変えたら、**ここも一緒に直す**。片方だけ直すと、測った秒数が実際とずれる。

`curl` と `ffprobe` が要る。
"""
import argparse
import os
import pathlib
import re
import subprocess
import tempfile
import urllib.parse

SRC = pathlib.Path(__file__).resolve().parent.parent / 'slides' / 'claude-memo.js'

# player.html の写し ---------------------------------------------------
TTS_MAX_CHARS = 180
BASE_SPEED_MULTIPLIER = 1.4

RULES = [
    (r'TODO\.md', 'トゥードゥー ドット エムディー', re.I),
    (r'TODO-([0-9]+)', r'トゥードゥー \1', re.I),
    (r'TODO', 'トゥードゥー', re.I),
    (r'ccstatusline', 'シーシー ステータス ライン', re.I),
    (r'/clear', 'スラッシュ クリア', re.I),
    (r'/goal', 'スラッシュ ゴール', re.I),
    (r'/doctor', 'スラッシュ ドクター', re.I),
    (r'/rc', 'スラッシュ アールシー', re.I),
    (r'/login', 'スラッシュ ログイン', re.I),
    (r'Claude Code', 'クロード コード', re.I),
    (r'Claude', 'クロード', re.I),
    (r'tmux', 'ティーマックス', re.I),
    (r'pyright-lsp', 'パイライト エルエスピー', re.I),
    (r'ponytail', 'ポニーテール', re.I),
    (r'codegraph', 'コードグラフ', re.I),
    (r'git worktree', 'ギット ワークツリー', re.I),
    (r'auto-mode', 'オートモード', re.I),
    (r'考え方', 'かんがえかた', 0),
    (r'使い方', 'つかいかた', 0),
    (r'\bmain\b', 'メイン', re.I),
    (r'\bimplementer\b', 'インプリメンター', re.I),
]
# --------------------------------------------------------------------------


def prepare(text):
    """prepareSpeechText() と同じ置換を掛ける。"""
    for pattern, replacement, flags in RULES:
        text = re.sub(pattern, replacement, text, flags=flags)
    return text


def measure(text):
    """読み上げ音声を取ってきて、実測秒数と 1.4 倍速での秒数を返す。"""
    spoken = prepare(text)
    clean = spoken[:TTS_MAX_CHARS]
    url = ('https://translate.google.com/translate_tts?ie=UTF-8&tl=ja'
           '&client=tw-ob&q=' + urllib.parse.quote(clean, safe=''))
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        tmp = f.name
    try:
        subprocess.run(['curl', '-sS', '-f', '-o', tmp, url], check=True)
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', tmp],
            check=True, capture_output=True, text=True).stdout.strip()
    finally:
        os.unlink(tmp)
    raw = float(out)
    return spoken, raw, raw / BASE_SPEED_MULTIPLIER


def narrations():
    """slides/claude-memo.js から narration を並び順に取り出す。"""
    return re.findall(r"narration: '(.*?)',\n", SRC.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(
        description='ナレーションの読み上げ秒数を測る')
    parser.add_argument('slides', nargs='*', type=int, help='スライド番号')
    parser.add_argument('--text', help='下書きの文字列を直接測る')
    parser.add_argument('--all', action='store_true', help='17 枚すべて')
    args = parser.parse_args()

    jobs = []
    if args.text:
        jobs.append(('下書き', args.text))
    if args.slides or args.all:
        found = narrations()
        ids = range(1, len(found) + 1) if args.all else args.slides
        for i in ids:
            jobs.append((f'スライド {i}', found[i - 1]))
    if not jobs:
        parser.error('スライド番号か --text か --all を渡す')

    for label, text in jobs:
        spoken, raw, scaled = measure(text)
        cut = ' ★180 字で切れる' if len(spoken) > TTS_MAX_CHARS else ''
        print(f'{label}: 原文 {len(text)} 字 / 読み {len(spoken)} 字{cut}'
              f' / 実測 {raw:.3f}s / 1.4 倍速 {scaled:.2f}s'
              f' -> duration: {round(scaled)}')


if __name__ == '__main__':
    main()
