#!/usr/bin/env python3
"""apply_durations() の置換と、置換表が player.html と揃っているかを確かめる。
`tools/test_measure_duration.py` で実行。

ネットワークは要らない（測定そのものは Google TTS 任せなので見ない）。
"""
import importlib.util
import pathlib
import re

spec = importlib.util.spec_from_file_location(
    'measure_duration',
    pathlib.Path(__file__).resolve().parent / 'measure-duration.py')
md = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md)

SAMPLE = """        const slideData = [
            // Slide 1
            {
                title: '1 枚目',
                duration: 10,
                narration: 'ひとつめ',
                render: function() { return `duration: 99,`; }
            },
            // Slide 2
            {
                title: '2 枚目',
                duration: 7,
                narration: 'ふたつめ',
            },
        ];
"""

written, changed, found = md.apply_durations(SAMPLE, {1: 12, 2: 7})
assert found == 2, found
assert changed == [(1, 10, 12)], changed
assert 'duration: 12,\n                narration:' in written
assert 'duration: 7,\n                narration:' in written
assert 'return `duration: 99,`' in written, 'render の中まで書き換えている'

written, changed, found = md.apply_durations(SAMPLE, {})
assert changed == [] and written == SAMPLE


# RULES が player.html の prepareSpeechText() と一語一句そろっているか。
# 片方だけ直すと測った秒数が実際とずれる（TODO-052）。
html = (pathlib.Path(__file__).resolve().parent.parent
        / 'player.html').read_text(encoding='utf-8')
chain = html[html.index('function prepareSpeechText'):]
chain = chain[:chain.index('\n        }')]
found = [(pat.replace(r'\/', '/'), rep.replace('$1', r'\1'), 'i' in flags)
         for pat, flags, rep
         in re.findall(r"\.replace\(/(.+)/([gi]+), '(.*)'\)", chain)]
mine = [(pat, rep, bool(flags & re.I)) for pat, rep, flags in md.RULES]
assert found == mine, [
    (a, b) for a, b in zip(found + [None] * len(mine), mine + [None] * len(found))
    if a != b]

print('OK')
