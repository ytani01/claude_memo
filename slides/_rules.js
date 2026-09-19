// 全デッキ共通の読みの置換表（TODO-054）。
// デッキだけの語は slides/<名前>.js の deckConfig.rules に書く。
// 当てる順はデッキ側が先、ここが後（デッキ側で読みを上書きできる）。
// tools/measure-duration.py もこのファイルを読む。
const SPEECH_RULES = [
    [/TODO\.md/gi, 'トゥードゥー ドット エムディー'],
    [/TODO-([0-9]+)/gi, 'トゥードゥー $1'],
    [/TODO/gi, 'トゥードゥー'],
    [/CLAUDE\.md/gi, 'クロード ドット エムディー'],
    [/Claude Code/gi, 'クロード コード'],
    [/Claude/gi, 'クロード'],
    [/考え方/g, 'かんがえかた'],
    [/使い方/g, 'つかいかた'],
    [/measure-duration\.py/gi, 'メジャー デュレーション ドット パイ'],
    [/player\.html/gi, 'プレイヤー ドット エイチティーエムエル'],
    [/User\.md/gi, 'ユーザー ドット エムディー'],
    [/slideData/gi, 'スライドデータ'],
    [/\bslides\b/gi, 'スライズ'],
    [/deckConfig/gi, 'デッキ コンフィグ'],
    [/\bdeck\b/gi, 'デッキ'],
    [/\bduration\b/gi, 'デュレーション'],
    [/\bclamp\b/gi, 'クランプ'],
    [/\bcqw\b/gi, 'シーキューダブリュー'],
    [/px\b/gi, 'ピクセル'],
    [/\brem\b/gi, 'レム'],
    [/Tailwind/gi, 'テイルウィンド'],
    [/HTML/gi, 'エイチティーエムエル'],
    [/\bPython\b/gi, 'パイソン'],
    [/\buser\b/gi, 'ユーザー'],
];
