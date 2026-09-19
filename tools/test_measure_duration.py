#!/usr/bin/env python3
"""apply_durations() の置換を確かめる。`tools/test_measure_duration.py` で実行。

ネットワークは要らない（測定そのものは Google TTS 任せなので見ない）。
"""
import importlib.util
import pathlib

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

print('OK')
