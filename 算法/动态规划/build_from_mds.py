"""
build_from_mds.py — Read individual problem md files and generate APKG.
Each md follows the standard template with ## sections.
Run: python build_from_mds.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, r'D:\anki\.claude\skills\anki-apkg-generator\scripts')
from apkg_builder import make_deck, add_basic, add_cloze, img, build, make_front, code

TOPIC_DIR = Path(r'D:\anki\算法\动态规划')
PROBLEMS_DIR = TOPIC_DIR / 'problems'
OUTPUT_PATH = TOPIC_DIR.parent.parent / '牌组' / '动态规划.apkg'


def parse_md(md_path: Path) -> dict:
    """Parse a problem md file into {title, sections: {name: content}}."""
    text = md_path.read_text(encoding='utf-8')

    title_match = re.search(r'^# (.+)$', text, re.MULTILINE)
    if not title_match:
        raise ValueError(f"No title in {md_path}")
    title = title_match.group(1).strip()

    sections: dict[str, str] = {}
    section_heads = list(re.finditer(r'^## (.+)$', text, re.MULTILINE))
    for i, m in enumerate(section_heads):
        name = m.group(1).strip()
        start = m.end()
        end = section_heads[i + 1].start() if i + 1 < len(section_heads) else len(text)
        sections[name] = text[start:end].strip()

    return {'title': title, 'sections': sections}


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
            code_blocks.append(code(inner))
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
    # Template deck
    d0 = make_deck(1747300100, '算法::动态规划::算法模板')
    add_cloze(d0,
        '状态转移核心模式：dp[i] = {{c1::max/min}}( {{c2::dp[i-1]}}, {{c3::dp[i-2] + ...}} )',
        '最值型 DP：分类讨论"选或不选"取最优')
    add_cloze(d0,
        '降维关键：倒序防 {{c1::重复使用}}，正序允许 {{c2::无限次使用}}',
        '0-1 背包倒序，完全背包正序')

    md_files = sorted(PROBLEMS_DIR.glob('*.md'))
    # Skip template/empty decks (not real problems)
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
        sections = data['sections']

        d = make_deck(deck_id, f'算法::动态规划::{title}')
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
        java_code = code_match.group(1).strip()
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
