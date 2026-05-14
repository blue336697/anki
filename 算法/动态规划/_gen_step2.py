"""
Step 2: Parse updated md for complexity, replace cards in build_dp.py.
Run: python _gen_step2.py
"""
import re
from pathlib import Path

TOPIC_DIR = Path(r'D:\anki\算法\动态规划')
MD_PATH = TOPIC_DIR / '动态规划 255444514a3180be947eea7331a4aaa6.md'
BUILD_PATH = TOPIC_DIR / 'build_dp.py'


def extract_complexity_from_md() -> dict[str, str]:
    """Parse updated md, return {problem_name: complexity_html}."""
    content = MD_PATH.read_text(encoding='utf-8')
    heading_pat = re.compile(r'^###\s+(?:\*\*)?(.+?)(?:\*\*)?$')
    result: dict[str, str] = {}

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        m = heading_pat.match(lines[i])
        if m:
            name = m.group(1).strip()
            j = i + 1
            while j < len(lines) and not heading_pat.match(lines[j]):
                j += 1
            section = '\n'.join(lines[i:j])
            comp_match = re.search(r'\*\*复杂度分析\*\*(.*?)$', section, re.DOTALL)
            if comp_match:
                raw = comp_match.group(1).strip()
                # Convert markdown to HTML for genanki cards
                html = raw
                html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
                html = html.replace('\n', '<br>')
                html = html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                # Restore <b> and <br> tags we just created
                html = html.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
                html = html.replace('&lt;br&gt;', '<br>')
                result[name] = html
            i = j
        else:
            i += 1
    return result


def fix_build_script(comp_map: dict[str, str]) -> None:
    """Replace complexity cards and fix code() in build_dp.py."""
    content = BUILD_PATH.read_text(encoding='utf-8')

    # Fix 1: code() uses html.escape()
    old_fn = (
        'def code(java: str) -> str:\n'
        '    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""\n'
        "    return f'<pre><code class=\"language-java\">{java}</code></pre>'"
    )
    new_fn = (
        'def code(java: str) -> str:\n'
        '    """Wrap Java code for highlight.js with HTML escaping."""\n'
        '    import html as _html\n'
        "    return f'<pre><code class=\"language-java\">{_html.escape(java)}</code></pre>'"
    )
    if old_fn in content:
        content = content.replace(old_fn, new_fn)
        print('Fixed: code() now uses html.escape()')

    # Name mapping: p= value → md heading name
    name_map: dict[str, str] = {}
    # Build reverse map: for each comp_map key, find matching p value
    for p_val in re.findall(r"^p = '(.+?)'$", content, re.MULTILINE):
        # Try exact match first
        if p_val in comp_map:
            name_map[p_val] = p_val
            continue
        # Try fuzzy match
        for md_name in comp_map:
            if p_val in md_name or md_name in p_val:
                name_map[p_val] = md_name
                break

    # Also add known mismatches
    name_map['最大子数组和(返回位置)'] = '返回最大子数组的起始位置和结束位置'
    name_map['连续子数组的最大和(精简)'] = '连续子数组的最大和'

    # Fix 2: Replace complexity cards
    fixed = 0
    for p_val, md_name in name_map.items():
        if md_name not in comp_map:
            continue

        new_html = comp_map[md_name]

        # Find the complexity card for this p value
        p_pos = content.find(f"p = '{p_val}'")
        if p_pos == -1:
            continue

        # Find add_cloze(d, make_front(p, '复杂度'), after p_pos
        search_start = p_pos
        comp_start_str = "add_cloze(d, make_front(p, '复杂度'),"
        comp_pos = content.find(comp_start_str, search_start)
        if comp_pos == -1:
            continue

        # Find the matching closing ) — it's at end of the LAST string line
        end_pos = content.find('\n', comp_pos + len(comp_start_str))
        if end_pos == -1:
            continue

        # Find end of the card: find line that ends with ')'
        card_end = content.find('\n', end_pos + 1)
        if card_end == -1:
            card_end = len(content)

        # Scan forward to find the ) at end of a line
        scan = end_pos + 1
        while scan < card_end:
            next_nl = content.find('\n', scan)
            if next_nl == -1:
                next_nl = card_end
            line = content[scan:next_nl].strip()
            if line.endswith(')'):
                card_end = next_nl
                break
            scan = next_nl + 1

        old_card = content[comp_pos:card_end]
        new_card = (
            f"add_basic(d, make_front(p, '复杂度'),\n"
            f"    '{new_html}')"
        )

        if old_card in content:
            content = content.replace(old_card, new_card)
            fixed += 1

    BUILD_PATH.write_text(content, encoding='utf-8')
    print(f'Replaced {fixed} complexity cards → {BUILD_PATH.name}')


if __name__ == '__main__':
    comp_map = extract_complexity_from_md()
    print(f'Extracted {len(comp_map)} complexity sections from md')
    fix_build_script(comp_map)
