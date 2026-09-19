#!/usr/bin/env python3
"""ナレーションの読み上げ秒数を測り、`duration` に入れる値を出す。

`slideData` の `duration` には「Online TTS の音声を `BASE_SPEED_MULTIPLIER`
倍で再生した実測秒数」が入っている（TODO-018）。ナレーションや読みの置換表を
変えると長さが変わるので、当たるスライドを測り直す必要がある。

    tools/measure-duration.py 2 17          # スライド 2 と 17 を測る
    tools/measure-duration.py --all         # すべて
    tools/measure-duration.py --all --write # すべて測って duration を書き戻す
    tools/measure-duration.py --deck user --all --write
    tools/measure-duration.py --text 'ここに下書き'

`--text` は、差し替える前に案の長さを見るためのもの。
`--write` は測った値を `duration` に書き込む（変わった枚だけ `17 -> 16` と
出す。戻すのは git の差分で足りる）。`--deck` はどのデッキを読むかで、
既定は `DEFAULT_DECK`（下で定める）のデッキ。

**この下の定数と RULES は player.html の写し。**
`prepareSpeechText()` の置換表、`TTS_MAX_CHARS`、`BASE_SPEED_MULTIPLIER` を
変えたら、**ここも一緒に直す**。片方だけ直すと、測った秒数が実際とずれる。

`curl` と `ffprobe` が要る。
"""
import argparse
import itertools
import os
import pathlib
import re
import subprocess
import tempfile
import urllib.parse

SLIDES = pathlib.Path(__file__).resolve().parent.parent / 'slides'
DEFAULT_DECK = 'readme'

# player.html の写し ---------------------------------------------------
TTS_MAX_CHARS = 180
BASE_SPEED_MULTIPLIER = 1.4

RULES = [
    (r'archives/todo', 'アーカイブズ スラッシュ トゥードゥー', re.I),
    (r'TODO\.md', 'トゥードゥー ドット エムディー', re.I),
    (r'TODO-([0-9]+)', r'トゥードゥー \1', re.I),
    (r'TODO', 'トゥードゥー', re.I),
    (r'ccstatusline', 'シーシー ステータス ライン', re.I),
    (r'/clear', 'スラッシュ クリア', re.I),
    (r'/goal', 'スラッシュ ゴール', re.I),
    (r'/doctor', 'スラッシュ ドクター', re.I),
    (r'/rc', 'スラッシュ アールシー', re.I),
    (r'/login', 'スラッシュ ログイン', re.I),
    (r'CLAUDE\.md', 'クロード ドット エムディー', re.I),
    (r'claude-memo', 'クロード メモ', re.I),
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
    (r'measure-duration\.py', 'メジャー デュレーション ドット パイ', re.I),
    (r'player\.html', 'プレイヤー ドット エイチティーエムエル', re.I),
    (r'public_html', 'パブリック エイチティーエムエル', re.I),
    (r'User\.md', 'ユーザー ドット エムディー', re.I),
    (r'yt_slide', 'ワイティー スライド', re.I),
    (r'\.js\b', ' ドット ジェイエス', re.I),
    (r'slideData', 'スライドデータ', re.I),
    (r'\bslides\b', 'スライズ', re.I),
    (r'deckConfig', 'デッキ コンフィグ', re.I),
    (r'\bdeck\b', 'デッキ', re.I),
    (r'\bduration\b', 'デュレーション', re.I),
    (r'Online TTS', 'オンライン ティーティーエス', re.I),
    (r'Web Speech', 'ウェブ スピーチ', re.I),
    (r'requestAnimationFrame', 'リクエスト アニメーション フレーム', re.I),
    (r'container query', 'コンテナ クエリ', re.I),
    (r'no-referrer', 'ノー リファラー', re.I),
    (r'\bmeta\b', 'メタ', re.I),
    (r'\bAudio\b', 'オーディオ', re.I),
    (r'\btransform\b', 'トランスフォーム', re.I),
    (r'\bclamp\b', 'クランプ', re.I),
    (r'\bcqw\b', 'シーキューダブリュー', re.I),
    (r'px\b', 'ピクセル', re.I),
    (r'\brem\b', 'レム', re.I),
    (r'\bwrite\b', 'ライト', re.I),
    (r'Tailwind', 'テイルウィンド', re.I),
    (r'\bCDN\b', 'シーディーエヌ', re.I),
    (r'JavaScript', 'ジャバスクリプト', re.I),
    (r'HTML', 'エイチティーエムエル', re.I),
    (r'\bURL\b', 'ユーアールエル', re.I),
    (r'\bPython\b', 'パイソン', re.I),
    (r'\btools\b', 'ツールズ', re.I),
    (r'\breadme\b', 'リードミー', re.I),
    (r'\buser\b', 'ユーザー', re.I),
    (r'\bdeveloper\b', 'デベロッパー', re.I),
]
# --------------------------------------------------------------------------


def prepare(text):
    """prepareSpeechText() と同じ置換を掛ける。"""
    # re.A が要る。付けないと Python の \b は日本語を語の一部と見なすので、
    # 「slidesフォルダ」のように和文が続く語で JS と結果が食い違う。
    for pattern, replacement, flags in RULES:
        text = re.sub(pattern, replacement, text, flags=flags | re.A)
    return text


def measure(text):
    """読み上げ音声を取ってきて、実測秒数と BASE_SPEED_MULTIPLIER 倍での秒数を返す。"""
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


# duration の直後に narration が来る並びを当てにしている（slideData の書き方）。
DURATION_RE = re.compile(r"(duration: )(\d+)(,\n *narration: ')")


def narrations(text):
    """デッキの本文から narration を並び順に取り出す。"""
    return re.findall(r"narration: '(.*?)',\n", text)


def apply_durations(text, updates):
    """{スライド番号: 秒数} を当てた本文と、変わった分 [(番号, 旧, 新)] を返す。"""
    changed = []
    counter = itertools.count(1)

    def replace(m):
        number = next(counter)
        old = int(m.group(2))
        new = updates.get(number, old)
        if new != old:
            changed.append((number, old, new))
        return f'{m.group(1)}{new}{m.group(3)}'

    written = DURATION_RE.sub(replace, text)
    return written, changed, next(counter) - 1


def write_durations(src, updates):
    """{スライド番号: 秒数} を書き込み、変わった分を [(番号, 旧, 新)] で返す。"""
    text = src.read_text(encoding='utf-8')
    written, changed, found = apply_durations(text, updates)
    if found != len(narrations(text)):
        raise SystemExit(f'{src} の duration が {found} 個しか見つからない。'
                         'slideData の書き方が変わっていないか確かめること')
    if changed:
        src.write_text(written, encoding='utf-8')
    return changed


def main():
    parser = argparse.ArgumentParser(
        description='ナレーションの読み上げ秒数を測る')
    parser.add_argument('slides', nargs='*', type=int, help='スライド番号')
    parser.add_argument('--text', help='下書きの文字列を直接測る')
    parser.add_argument('--all', action='store_true', help='すべてのスライド')
    parser.add_argument('--write', action='store_true',
                        help='測った値をデッキの duration に書き戻す')
    parser.add_argument('--deck', default=DEFAULT_DECK,
                        help=f'slides/<名前>.js の <名前>（既定は {DEFAULT_DECK}）')
    args = parser.parse_args()

    src = SLIDES / f'{args.deck}.js'
    if (args.slides or args.all) and not src.exists():
        parser.error(f'{src} が無い')

    jobs = []
    if args.text:
        jobs.append((None, '下書き', args.text))
    if args.slides or args.all:
        found = narrations(src.read_text(encoding='utf-8'))
        ids = range(1, len(found) + 1) if args.all else args.slides
        for i in ids:
            jobs.append((i, f'スライド {i}', found[i - 1]))
    if not jobs:
        parser.error('スライド番号か --text か --all を渡す')
    if args.write and not (args.slides or args.all):
        parser.error('--write はスライド番号か --all と一緒に渡す')

    updates = {}
    for number, label, text in jobs:
        spoken, raw, scaled = measure(text)
        cut = (f' ★TTS_MAX_CHARS={TTS_MAX_CHARS} 字で切れる'
               if len(spoken) > TTS_MAX_CHARS else '')
        print(f'{label}: 原文 {len(text)} 字 / 読み {len(spoken)} 字{cut}'
              f' / 実測 {raw:.3f}s'
              f' / BASE_SPEED_MULTIPLIER={BASE_SPEED_MULTIPLIER} 倍速'
              f' {scaled:.2f}s -> duration: {round(scaled)}')
        if number is not None:
            updates[number] = round(scaled)

    if args.write:
        changed = write_durations(src, updates)
        for number, old, new in changed:
            print(f'スライド {number}: duration {old} -> {new}')
        print(f'{src.name}: {len(changed)} 枚を書き換えた'
              if changed else f'{src.name}: 変更なし')


if __name__ == '__main__':
    main()
