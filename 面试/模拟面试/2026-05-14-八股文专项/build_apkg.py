from pathlib import Path
import sys

TOPIC = '2026-05-14-八股文专项'
BASE = Path(__file__).resolve().parent
SKILL_DIR = Path('/Users/haojie.liu/.hermes/skills/productivity/interview-anki-card-patterns')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))

from apkg_builder import make_deck, add_basic, build

category_files = [
    '分布式一致性-发券幂等与重试.md',
    '消息队列-重复消费乱序与补偿.md',
    '系统设计-优惠券库存防超发.md',
    '业务状态机-订单库存发券.md',
    '面试表达-八股场景化回答.md'
]

deck = make_deck(1778800514, f'面试::模拟面试::{TOPIC}')
card_count = 0
for fname in category_files:
    text = (BASE / fname).read_text(encoding='utf-8')
    if '```tsv' not in text:
        continue
    tsv = text.split('```tsv', 1)[1].split('```', 1)[0].strip()
    for line in tsv.splitlines():
        parts = line.split('	')
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
