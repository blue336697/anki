"""Standalone: 最小花费爬楼梯 — read md, all section cards."""
import html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / '.claude' / 'skills' / 'anki-apkg-generator'
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_deck, add_basic, add_cloze, code, build, make_front

MD_PATH = Path(__file__).resolve().parent / 'problems' / '使用最小花费爬楼梯.md'


def parse_md(md_path: Path) -> dict:
    text = md_path.read_text(encoding='utf-8')
    title_match = re.search(r'^# (.+)$', text, re.MULTILINE)
    heads = list(re.finditer(r'^## (.+)$', text, re.MULTILINE))
    sections: dict[str, str] = {}
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
    return process_basic_text(normalize_cloze('\n'.join(lines))), \
           process_basic_text('\n'.join(hints)) if hints else ''


def add_solution(deck, title: str, sec_name: str, content: str) -> None:
    parts: list[str] = []
    code_match = re.search(r'```(?:java)?\n(.*?)```', content, re.DOTALL)
    if code_match:
        desc = content[:code_match.start()].strip()
        if desc:
            parts.append(process_basic_text(desc))
        parts.append(code(html.unescape(code_match.group(1).strip())))
    if parts:
        add_basic(deck, make_front(title, sec_name), '<br>'.join(parts))


data = parse_md(MD_PATH)
title = data['title']
d = make_deck(1747300192, f'算法::动态规划::{title}')

for sec_name, sec_content in data['sections'].items():
    if not sec_content.strip():
        continue
    if sec_name == '题干':
        add_basic(d, make_front(title, '题干'), process_basic_text(sec_content))
    elif sec_name.startswith('题解'):
        add_solution(d, title, sec_name, sec_content)
    elif '{{c' in sec_content:
        cloze_text, hint = parse_cloze(sec_content)
        add_cloze(d, make_front(title, sec_name) + '<br>' + cloze_text, hint)
    else:
        add_basic(d, make_front(title, sec_name), process_basic_text(sec_content))

total = len(d.notes)
OUTPUT = REPO_ROOT / '牌组' / '算法' / '使用最小花费爬楼梯_修复.apkg'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
print(f'{total} cards -> {build(str(OUTPUT))}')
