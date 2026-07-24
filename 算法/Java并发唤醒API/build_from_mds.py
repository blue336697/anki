"""
build_from_mds.py — Generate Java并发唤醒API APKG from problems/*.md files.
"""
import html
import re
import sys
import urllib.parse
from pathlib import Path

TOPIC_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOPIC_DIR.parent.parent
SKILL_DIR = REPO_ROOT / '.agents' / 'skills' / 'anki-apkg-generator'

sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_deck, add_basic, add_cloze, img, code, build, make_front

TOPIC_NAME = 'Java并发唤醒API'
TEMPLATE_DECK_ID = 1747302600
START_DECK_ID = 1747302601
PROBLEMS_DIR = TOPIC_DIR / 'problems'
OUTPUT_PATH = REPO_ROOT / '牌组' / '算法' / f'{TOPIC_NAME}.apkg'


def parse_md(md_path: Path) -> dict:
    text = md_path.read_text(encoding='utf-8')
    title_match = re.search(r'^# (.+)$', text, re.MULTILINE)
    if not title_match:
        raise ValueError(f'No title in {md_path}')
    heads = list(re.finditer(r'^## (.+)$', text, re.MULTILINE))
    sections = {}
    for i, head in enumerate(heads):
        name = head.group(1).strip()
        start = head.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        sections[name] = text[start:end].strip()
    return {'title': title_match.group(1).strip(), 'sections': sections}


def normalize_cloze(text: str) -> str:
    return re.sub(r'\{\{c\d+::', '{{c1::', text)


def process_basic_text(text: str) -> str:
    escaped = html.escape(html.unescape(text))
    return escaped.replace('&lt;br&gt;', '<br>').replace('\n', '<br>')


def parse_cloze(content: str) -> tuple[str, str]:
    lines: list[str] = []
    hints: list[str] = []
    for line in content.splitlines():
        if line.startswith('> '):
            hints.append(line[2:].strip())
        elif line.strip():
            lines.append(line)
    cloze_text = process_basic_text(normalize_cloze('\n'.join(lines)))
    return cloze_text, process_basic_text('\n'.join(hints)) if hints else ''


def add_solution(deck, title: str, sec_name: str, content: str) -> None:
    parts: list[str] = []
    code_match = re.search(r'```(?:java)?\n(.*?)```', content, re.DOTALL)
    if code_match:
        desc = content[:code_match.start()].strip()
        if desc:
            parts.append(process_basic_text(desc))
        parts.append(code(html.unescape(code_match.group(1).strip())))
    elif content.strip():
        parts.append(process_basic_text(content.strip()))
    if parts:
        add_basic(deck, make_front(title, sec_name), '<br>'.join(parts))


def build_apkg() -> str:
    # Principle deck
    d0 = make_deck(TEMPLATE_DECK_ID, f'算法::{TOPIC_NAME}::总览')
    add_basic(d0, 'Java 并发唤醒 API 全景',
        '<b>Java 并发唤醒机制</b>分三组：<br><br>'
        '<b>1. 基础原语</b>：Object.wait/notify（需synchronized锁）<br>'
        '<b>2. JUC 中层</b>：LockSupport.park/unpark（无锁）、Lock/Condition（多条件队列）<br>'
        '<b>3. 高层工具</b>：Semaphore、CountDownLatch、CyclicBarrier、BlockingQueue<br><br>'
        '<b>经典例题</b>：交替打印 1-100，四种解法对比。')
    add_cloze(d0,
        'API 选型速查：<br>'
        '面试 → {{c1::synchronized + wait/notify}}<br>'
        '轻量精确唤醒 → {{c1::LockSupport.park/unpark}}<br>'
        '多条件队列 → {{c1::Lock + Condition}}<br>'
        '控制并发数 → {{c1::Semaphore}}',
        '各场景API速查')
    add_cloze(d0,
        '关键记忆点：<br>'
        '{{c1::wait() 释放锁，sleep() 不释放锁}}<br>'
        '{{c1::wait/notify 必须在 synchronized 块内}}<br>'
        '{{c1::unpark 可以先于 park 调用（许可证机制）}}<br>'
        '{{c1::park() 被 interrupt 后不抛异常，需手动检查}}',
        '核心区别')

    # Build problem decks
    deck_id = START_DECK_ID
    total_cards = 0
    total_problems = 0
    md_files = sorted(PROBLEMS_DIR.glob('*.md'))
    for md_path in md_files:
        data = parse_md(md_path)
        title = data['title']
        deck = make_deck(deck_id, f'算法::{TOPIC_NAME}::{title}')
        deck_id += 1
        for sec_name, sec_content in data['sections'].items():
            if not sec_content.strip():
                continue
            if '{{c' in sec_content:
                cloze_text, hint = parse_cloze(sec_content)
                add_cloze(deck, make_front(title, sec_name) + '<br>' + cloze_text, hint)
            elif '```java' in sec_content or '```' in sec_content:
                add_solution(deck, title, sec_name, sec_content)
            else:
                add_basic(deck, make_front(title, sec_name), process_basic_text(sec_content))
        total_problems += 1
        total_cards += len(deck.notes)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build(str(OUTPUT_PATH))
    print(f'\n{total_problems} topics, {total_cards} cards -> {OUTPUT_PATH}')
    return result


if __name__ == '__main__':
    build_apkg()
