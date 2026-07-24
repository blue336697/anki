"""
build_from_mds.py — Generate Deque双端队列 APKG from problems/*.md files.
Run from this directory: python3 build_from_mds.py
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

TOPIC_NAME = 'Deque双端队列'
TEMPLATE_DECK_ID = 1747302500
START_DECK_ID = 1747302501
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


def process_body_with_images(text: str) -> str:
    code_blocks: list[str] = []
    inline_codes: list[str] = []
    images: list[str] = []

    def stash_code(match: re.Match) -> str:
        lang = match.group(1) or ''
        inner = html.unescape(match.group(2))
        if 'java' in lang:
            code_blocks.append(code(inner))
        else:
            code_blocks.append(f'<pre><code>{html.escape(inner)}</code></pre>')
        return f'\x00CODE{len(code_blocks) - 1}\x00'

    def stash_inline(match: re.Match) -> str:
        inline_codes.append(f'<code>{html.escape(match.group(1))}</code>')
        return f'\x00INLINE{len(inline_codes) - 1}\x00'

    def stash_image(match: re.Match) -> str:
        images.append(img(urllib.parse.unquote(match.group(1))))
        return f'\x00IMG{len(images) - 1}\x00'

    text = re.sub(r'```(\w*)\n(.*?)```', stash_code, text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+?)`', stash_inline, text)
    text = re.sub(r'!\[.*?\]\((.*?)\)', stash_image, text)
    text = html.escape(html.unescape(text))
    for i, value in enumerate(images):
        text = text.replace(f'\x00IMG{i}\x00', value)
    for i, value in enumerate(inline_codes):
        text = text.replace(f'\x00INLINE{i}\x00', value)
    for i, value in enumerate(code_blocks):
        text = text.replace(f'\x00CODE{i}\x00', value)
    return text.replace('\n', '<br>')


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
    add_basic(d0, 'Deque 双端队列全景',
        '<b>Deque</b>（Double Ended Queue）— Java 中最强大的线性集合接口。<br>'
        '<b>核心能力</b>：两端插入/删除，可当栈、可当队列、可做双端操作。<br>'
        '<b>首选实现</b>：ArrayDeque（比 Stack 快，比 LinkedList 快）<br><br>'
        '四大专题：<br>'
        '1. <b>基本概念与API</b> — 两大API族（add/remove/get vs offer/poll/peek）<br>'
        '2. <b>栈和队列模式</b> — 替代Stack、替代LinkedList队列<br>'
        '3. <b>单调队列</b> — 滑动窗口最大值的首选方案<br>'
        '4. <b>经典应用</b> — BFS、接雨水、回文检查、简化路径等')
    add_cloze(d0,
        'Deque 核心记忆：<br>'
        '{{c1::抛异常 → add/remove/get（失败抛 NoSuchElementException）}}',
        '两组API + 两种模式 = Deque 全部用法')
    add_cloze(d0,
        'Deque 核心记忆：<br>'
        '{{c1::返回特殊值 → offer/poll/peek（失败返回 null/false）}}',
        '')
    add_cloze(d0,
        'Deque 核心记忆：<br>'
        '{{c1::栈模式 → push/pop/peek = addFirst/removeFirst/peekFirst}}',
        '')
    add_cloze(d0,
        'Deque 核心记忆：<br>'
        '{{c1::队列模式 → offer/poll/peek = offerLast/pollFirst/peekFirst}}',
        '')
    add_cloze(d0,
        '永远记住：<br>'
        '{{c1::用 ArrayDeque，不用 Stack（性能差+设计烂）}}',
        'Java 官方推荐的最佳实践')
    add_cloze(d0,
        '永远记住：<br>'
        '{{c1::用 ArrayDeque，不用 LinkedList 当队列（内存+性能双重浪费）}}',
        '')

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
