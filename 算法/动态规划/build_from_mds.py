"""
build_from_mds.py — Read individual problem md files and generate APKG.
Each md follows the standard template with ## sections.
Run: python build_from_mds.py
"""
import re
import sys
import html
from pathlib import Path

TOPIC_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOPIC_DIR.parent.parent
SKILL_DIR = REPO_ROOT / '.agents' / 'skills' / 'anki-apkg-generator'

sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_deck, add_basic, add_cloze, img, build, make_front, code

PROBLEMS_DIR = TOPIC_DIR / 'problems'
KNOWLEDGE_DIR = TOPIC_DIR / 'knowledge'
OUTPUT_PATH = REPO_ROOT / '牌组' / '算法' / '动态规划.apkg'


def parse_md(md_path: Path) -> dict:
    """Parse a problem md file, including an optional live-Anki deck alias."""
    text = md_path.read_text(encoding='utf-8')

    title_match = re.search(r'^# (.+)$', text, re.MULTILINE)
    if not title_match:
        raise ValueError(f"No title in {md_path}")
    title = title_match.group(1).strip()
    deck_match = re.search(r'^<!--\s*anki-deck:\s*(.+?)\s*-->$', text, re.MULTILINE)
    deck_title = deck_match.group(1).strip() if deck_match else title

    sections: dict[str, str] = {}
    section_heads = list(re.finditer(r'^## (.+)$', text, re.MULTILINE))
    for i, m in enumerate(section_heads):
        name = m.group(1).strip()
        start = m.end()
        end = section_heads[i + 1].start() if i + 1 < len(section_heads) else len(text)
        sections[name] = text[start:end].strip()

    return {'title': title, 'deck_title': deck_title, 'sections': sections}


def process_body_with_images(text: str) -> str:
    """Convert markdown body to HTML for Anki card display.
    Extracts code blocks -> code(), images -> img(), escapes the rest."""
    import html as _html_mod
    import urllib.parse

    # Phase 1: extract code blocks and replace with placeholders
    code_blocks: list[str] = []
    def stash_code(m: re.Match) -> str:
        lang = m.group(1) or ''
        inner = m.group(2)
        if 'java' in lang:
            code_blocks.append(code(html.unescape(inner)))
        else:
            code_blocks.append(f'<pre><code>{_html_mod.escape(inner)}</code></pre>')
        return f'\x00CODE{len(code_blocks) - 1}\x00'

    text = re.sub(r'```(\w*)\n(.*?)```', stash_code, text, flags=re.DOTALL)

    # Phase 2: handle inline code
    inline_codes: list[str] = []
    def stash_inline(m: re.Match) -> str:
        inline_codes.append(f'<code>{_html_mod.escape(m.group(1))}</code>')
        return f'\x00INLINE{len(inline_codes) - 1}\x00'

    text = re.sub(r'`([^`]+?)`', stash_inline, text)

    # Phase 3: handle images -> img() calls
    imgs: list[str] = []
    def stash_img(m: re.Match) -> str:
        path = m.group(1)
        decoded = urllib.parse.unquote(path)
        imgs.append(img(decoded))
        return f'\x00IMG{len(imgs) - 1}\x00'

    text = re.sub(r'!\[.*?\]\((.*?)\)', stash_img, text)

    # Phase 4: HTML-escape remaining text
    text = _html_mod.escape(text)

    # Phase 5: restore placeholders (reverse order)
    for i, h in enumerate(imgs):
        text = text.replace(f'\x00IMG{i}\x00', h)
    for i, h in enumerate(inline_codes):
        text = text.replace(f'\x00INLINE{i}\x00', h)
    for i, h in enumerate(code_blocks):
        text = text.replace(f'\x00CODE{i}\x00', h)

    # Convert newlines to <br>
    text = text.replace('\n', '<br>')
    return text


def build_apkg() -> str:
    """Read all problem mds and generate APKG."""
    # Principle cards are Markdown-backed too; Python must not hardcode content.
    for index, md_path in enumerate(sorted(KNOWLEDGE_DIR.glob('*.md'))):
        data = parse_md(md_path)
        d0 = make_deck(1747300100 + index, f"算法::动态规划::{data['deck_title']}")
        for sec_name, sec_content in data['sections'].items():
            text_match = re.search(
                r'^Text:\s*(.+?)(?=^Back Extra:|\Z)',
                sec_content,
                re.MULTILINE | re.DOTALL,
            )
            extra_match = re.search(
                r'^Back Extra:\s*(.*)$',
                sec_content,
                re.MULTILINE | re.DOTALL,
            )
            if not text_match:
                raise ValueError(f'Missing Text in {md_path} section {sec_name}')
            add_cloze(
                d0,
                text_match.group(1).strip(),
                extra_match.group(1).strip() if extra_match else '',
            )

    md_files = sorted(PROBLEMS_DIR.glob('*.md'))
    # Historical placeholder; principle cards now live under knowledge/.
    skip_files = {'原理通识.md'}
    md_files = [f for f in md_files if f.name not in skip_files]
    deck_id = 1747300101
    total_cards = 0
    total_problems = 0

    cloze_sections = {'定义状态', '转移方程', '初始化'}
    basic_sections = {'计算顺序', '返回结果'}

    for md_path in md_files:
        data = parse_md(md_path)
        title = data['title']
        deck_title = data['deck_title']
        sections = data['sections']

        d = make_deck(deck_id, f'算法::动态规划::{deck_title}')
        deck_id += 1

        for sec_name, sec_content in sections.items():
            if sec_name == '题干':
                html_body = process_body_with_images(sec_content)
                add_basic(d, make_front(title, '题干'), html_body)
            elif sec_name in cloze_sections:
                cloze_text, hint = _parse_cloze(sec_content)
                add_cloze(d,
                    make_front(title, sec_name) + '<br>' + cloze_text,
                    hint)
            elif sec_name in basic_sections:
                add_basic(d, make_front(title, sec_name), sec_content)
            elif sec_name == '复杂度':
                add_basic(d, make_front(title, '复杂度'), sec_content)
            elif sec_name.startswith('题解'):
                _add_solution(d, title, sec_name, sec_content)

        total_problems += 1
        total_cards += len(d.notes)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build(str(OUTPUT_PATH))
    print(f'\n{total_problems} problems, {total_cards} cards -> {OUTPUT_PATH}')
    return result


def _parse_cloze(content: str) -> tuple[str, str]:
    """Parse cloze text and optional > hint from section content."""
    lines = content.split('\n')
    cloze_lines = []
    hint = ''
    for line in lines:
        if line.startswith('> '):
            hint = line[2:].strip()
        elif line.strip():
            cloze_lines.append(line)
    return '<br>'.join(cloze_lines), hint


def _add_solution(d, title: str, sec_name: str, content: str) -> None:
    """Add 题解 card — extract description + Java code from section."""
    parts: list[str] = []
    code_match = re.search(r'```(?:java)?\n(.*?)```', content, re.DOTALL)
    if code_match:
        java_code = html.unescape(code_match.group(1).strip())
        desc = content[:code_match.start()].strip()
        if desc:
            parts.append(desc)
        parts.append(code(java_code))
    else:
        if content.strip():
            parts.append(content.strip())

    if parts:
        add_basic(d, make_front(title, sec_name), '<br>'.join(parts))


if __name__ == '__main__':
    build_apkg()
