"""
build_from_mds.py — Read individual problem md files and generate APKG.
Run from this topic directory: python3 build_from_mds.py
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

TOPIC_NAME = '贪心算法'
TEMPLATE_DECK_ID = 1747300900
START_DECK_ID = 1747300901
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
    code_blocks = []
    inline_codes = []
    images = []

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


def parse_cloze(content: str) -> tuple:
    lines = []
    hints = []
    for line in content.splitlines():
        if line.startswith('> '):
            hints.append(line[2:].strip())
        elif line.strip():
            lines.append(line)
    cloze_text = process_basic_text(normalize_cloze('\n'.join(lines)))
    return cloze_text, process_basic_text('\n'.join(hints)) if hints else ''


def add_solution(deck, title: str, sec_name: str, content: str) -> None:
    parts = []
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
            if sec_name == '题干':
                add_basic(deck, make_front(title, '题干'), process_body_with_images(sec_content))
            elif sec_name.startswith('题解'):
                add_solution(deck, title, sec_name, sec_content)
            elif '{{c' in sec_content:
                cloze_text, hint = parse_cloze(sec_content)
                add_cloze(deck, make_front(title, sec_name) + '<br>' + cloze_text, hint)
            else:
                add_basic(deck, make_front(title, sec_name), process_basic_text(sec_content))
        total_problems += 1
        total_cards += len(deck.notes)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build(str(OUTPUT_PATH))
    print(f'\n{total_problems} problems, {total_cards} cards -> {OUTPUT_PATH}')
    return result


if __name__ == '__main__':
    build_apkg()
