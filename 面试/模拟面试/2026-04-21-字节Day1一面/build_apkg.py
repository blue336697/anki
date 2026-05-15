from pathlib import Path
import sys

TOPIC = '2026-04-21-字节Day1一面'
BASE = Path(__file__).resolve().parent
SKILL_DIR = Path('/Users/haojie.liu/.hermes/skills/productivity/interview-anki-card-patterns')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))

from apkg_builder import make_deck, add_basic, build

category_files = [
    '项目表达-自我介绍与Ownership.md',
    '项目深挖-发票流水规则平台.md',
    '系统设计-指标口径与降级治理.md',
    'AI协同开发-工具治理.md',
]

deck = make_deck(1778800421, f'面试::模拟面试::{TOPIC}')
card_count = 0
for fname in category_files:
    text = (BASE / fname).read_text(encoding='utf-8')
    if '```tsv' not in text:
        continue
    tsv = text.split('```tsv', 1)[1].split('```', 1)[0].strip()
    for line in tsv.splitlines():
        parts = line.split('\t')
        if len(parts) != 5:
            continue
        front, back, tags, source, difficulty = parts
        back = back + f'<br><br><hr><small>Tags: {tags}<br>Source: {source}<br>Difficulty: {difficulty}</small>'
        add_basic(deck, front, back)
        card_count += 1

deck_dir = Path('/Users/haojie.liu/personalProjects/anki/牌组/面试/模拟面试')
deck_dir.mkdir(parents=True, exist_ok=True)
out = deck_dir / f'{TOPIC}.apkg'
summary = build(str(out))
print(summary)
print(f'cards={card_count}')
