from pathlib import Path
import sys


TOPIC = '2025-真实面试复盘'
BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
SKILL_DIR = REPO / '.agents' / 'skills' / 'anki-apkg-generator'
sys.path.insert(0, str(SKILL_DIR / 'scripts'))

from apkg_builder import make_deck, add_basic, build  # noqa: E402


category_files = [
    '算法与代码输出专项.md',
    '项目深挖专项.md',
]


def iter_tsv_cards(text: str):
    if '```tsv' not in text:
        return
    tsv = text.split('```tsv', 1)[1].split('```', 1)[0].strip()
    for line_no, line in enumerate(tsv.splitlines(), 1):
        parts = line.split('\t')
        if len(parts) != 5:
            raise ValueError(f'Invalid TSV line {line_no}: expected 5 columns, got {len(parts)}')
        yield parts


deck = make_deck(1778800825, f'面试::真实面试::{TOPIC}')
card_count = 0

for fname in category_files:
    text = (BASE / fname).read_text(encoding='utf-8')
    for front, back, tags, source, difficulty in iter_tsv_cards(text):
        back = (
            back
            + f'<br><br><hr><small>Tags: {tags}<br>'
            + f'Source: {source}<br>Difficulty: {difficulty}</small>'
        )
        add_basic(deck, front, back)
        card_count += 1

deck_dir = REPO / '牌组' / '面试' / '2025年真实面试'
deck_dir.mkdir(parents=True, exist_ok=True)
out = deck_dir / f'{TOPIC}.apkg'
summary = build(str(out))
print(summary)
print(f'cards={card_count}')
