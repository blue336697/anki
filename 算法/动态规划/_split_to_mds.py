"""
_split_to_mds.py — Split monolithic md + build_dp.py into individual problem mds.
Uses a recording shim to capture card data by actually executing build_dp.py.
Run: python _split_to_mds.py
"""
import html as _html
import re
import sys
import types
from pathlib import Path

TOPIC_DIR = Path(r'D:\anki\算法\动态规划')
MD_PATH = TOPIC_DIR / '动态规划 255444514a3180be947eea7331a4aaa6.md'
BUILD_PATH = TOPIC_DIR / 'build_dp.py'
PROBLEMS_DIR = TOPIC_DIR / 'problems'


# ============================================================
# Recording shim — captures card data when build_dp.py runs
# ============================================================

_record: dict[str, dict] = {}
_current_p: list[str | None] = [None]


def _record_make_deck(deck_id: int, name: str):
    parts = name.split('::')
    _current_p[0] = parts[-1] if len(parts) > 2 else name
    _record[_current_p[0]] = {'deck_id': deck_id, 'cards': []}
    return type('_D', (), {'add_note': lambda s, n: None})()


def _record_add_basic(deck, front: str, back: str) -> None:
    p = _current_p[0]
    if not p:
        return
    if ' | ' in front:
        _, category = front.split(' | ', 1)
    else:
        category = front
    _record[p]['cards'].append({
        'type': 'basic', 'category': category, 'content': back,
    })


def _record_add_cloze(deck, text: str, extra: str = '') -> None:
    p = _current_p[0]
    if not p:
        return
    if ' | ' in text:
        _, rest = text.split(' | ', 1)
        if '<br>' in rest:
            category, cloze = rest.split('<br>', 1)
        else:
            category, cloze = rest, ''
    else:
        category = text
        cloze = ''
    _record[p]['cards'].append({
        'type': 'cloze', 'category': category, 'text': cloze, 'hint': extra,
    })


def _record_make_front(problem: str, category: str) -> str:
    return f'{problem} | {category}'


def _record_img(name: str) -> str:
    return f'<br><img src="{name}">'


def _record_code(java: str) -> str:
    return f'<pre><code class="language-java">{_html.escape(java)}</code></pre>'


def _record_build(output_path: str) -> str:
    return ''


# Build fake modules
_apkg = types.ModuleType('apkg_builder')
_apkg.make_deck = _record_make_deck
_apkg.add_basic = _record_add_basic
_apkg.add_cloze = _record_add_cloze
_apkg.make_front = _record_make_front
_apkg.img = _record_img
_apkg.code = _record_code
_apkg.build = _record_build
_apkg.BASIC_MODEL = None
_apkg.CLOZE_MODEL = None
_apkg.HLJS_HEAD = ''

_genanki = types.ModuleType('genanki')
_genanki.Model = lambda *a, **kw: None
_genanki.Deck = lambda *a, **kw: None
_genanki.Note = lambda *a, **kw: None
_genanki.Package = lambda *a: type('_P', (), {'write_to_file': lambda s, p: None})()


def capture_build_data() -> dict[str, dict]:
    """Execute build_dp.py with recording shim, return captured data."""
    # Build path needs to be absolute for exec
    sys.modules['apkg_builder'] = _apkg
    sys.modules['genanki'] = _genanki

    exec(BUILD_PATH.read_text(encoding='utf-8'), {'__name__': '__main__'})

    return _record


# ============================================================
# Source MD parsing
# ============================================================

def clean_heading(text: str) -> str:
    return text.replace('**', '').strip()


def parse_source_md() -> dict[str, dict]:
    """Parse source markdown: {cleaned_heading: {body, complexity}}."""
    content = MD_PATH.read_text(encoding='utf-8')
    lines = content.split('\n')

    problems: dict[str, dict] = {}
    heading_pat = re.compile(r'^###\s+(.+)$')
    seen: set[str] = set()

    i = 0
    while i < len(lines):
        m = heading_pat.match(lines[i])
        if m and i == 0:
            i += 1
            continue
        if m:
            raw = m.group(1)
            name = clean_heading(raw)
            if name in seen:
                i += 1
                continue
            seen.add(name)

            j = i + 1
            while j < len(lines) and not heading_pat.match(lines[j]):
                j += 1

            body = '\n'.join(lines[i + 1:j]).strip()
            comp_match = re.search(r'\*\*复杂度分析\*\*(.*?)$', body, re.DOTALL)
            complexity = ''
            if comp_match:
                raw_comp = comp_match.group(1).strip()
                html = raw_comp
                html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
                html = html.replace('\n', '<br>')
                body = body[:comp_match.start()].strip()
                complexity = html

            problems[name] = {'body': body, 'complexity': complexity}
            i = j
        else:
            i += 1

    return problems


def write_problem_md(name: str, md_data: dict, cards: list[dict]) -> None:
    """Write individual problem md with standard ## sections."""
    lines = [f'# {name}', '']

    # 题干
    lines.append('## 题干')
    lines.append(md_data.get('body', ''))
    lines.append('')

    # 五部曲: map full category names to short section headers
    step_map = {
        '定义状态(1/5)': '定义状态', '转移方程(2/5)': '转移方程',
        '初始化(3/5)': '初始化', '计算顺序(4/5)': '计算顺序',
        '返回结果(5/5)': '返回结果',
    }

    for full_step, short_step in step_map.items():
        for card in cards:
            if card.get('category') == full_step:
                lines.append(f'## {short_step}')
                if card['type'] == 'cloze':
                    lines.append(card.get('text', ''))
                    if card.get('hint'):
                        lines.append(f'> {card["hint"]}')
                else:
                    lines.append(card.get('content', ''))
                lines.append('')
                break

    # 复杂度
    comp = md_data.get('complexity', '')
    if comp:
        lines.append('## 复杂度')
        lines.append(comp)
        lines.append('')

    # 题解 — extract clean Java code
    for card in cards:
        cat = card.get('category', '')
        if cat.startswith('题解'):
            lines.append(f'## {cat}')
            content = card.get('content', '')
            code_match = re.search(
                r'<pre><code class="language-java">(.*?)</code></pre>',
                content, re.DOTALL
            )
            if code_match:
                java_code = code_match.group(1)
                java_code = _html.unescape(java_code)
                # Strip leading description text (before the code block)
                desc = content[:code_match.start()].strip()
                if desc:
                    desc = re.sub(r'<br>$', '', desc).strip()
                    lines.append(desc)
                lines.append('```java')
                lines.append(java_code)
                lines.append('```')
            else:
                lines.append(content)
            lines.append('')

    PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = name.replace('/', '_').replace('\\', '_')
    (PROBLEMS_DIR / f'{safe_name}.md').write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    print('Capturing card data from build_dp.py...')
    build_data = capture_build_data()
    print(f'  Found {len(build_data)} problems')

    print('Parsing source markdown...')
    md_data = parse_source_md()
    print(f'  Found {len(md_data)} problems')

    name_map = {
        '最大子数组和(返回位置)': '返回最大子数组的起始位置和结束位置',
        '连续子数组的最大和(精简)': '连续子数组的最大和',
    }

    for p_val in build_data:
        print(f'  Processing: {p_val} ({len(build_data[p_val]["cards"])} cards)')

    written = 0
    for p_val, bdata in build_data.items():
        md_name = name_map.get(p_val, p_val)
        mdata = md_data.get(md_name)
        if not mdata:
            for mname in md_data:
                if p_val in mname or mname in p_val or md_name in mname:
                    mdata = md_data[mname]
                    break
        if not mdata:
            print(f'  WARNING: No source md data for {p_val}')
            mdata = {'body': '', 'complexity': ''}

        write_problem_md(p_val, mdata, bdata['cards'])
        written += 1

    print(f'\nDone: {written} md files -> {PROBLEMS_DIR}')


if __name__ == '__main__':
    main()
