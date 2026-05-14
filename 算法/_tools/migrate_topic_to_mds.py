"""
Migrate a legacy topic build_*.py into problems/*.md + build_from_mds.py.

Usage:
    python3 算法/_tools/migrate_topic_to_mds.py 算法/回溯法（递归枚举\ 剪枝）/build_backtracking.py

The script executes the legacy build file with a mocked apkg_builder module,
captures cards, writes one md per problem deck, and creates a local
build_from_mds.py that can rebuild the APKG from those md files.
"""
from __future__ import annotations

import html
import re
import sys
import types
import urllib.parse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "anki-apkg-generator"


def md_filename(name: str) -> str:
    safe = name.replace("/", "／").replace(":", "：").strip()
    return f"{safe}.md"


def normalize_cloze(text: str) -> str:
    return re.sub(r"\{\{c\d+::", "{{c1::", text)


def html_to_mdish(text: str) -> str:
    """Convert legacy card HTML into markdown-ish text for problem md files."""
    text = text or ""
    text = text.replace("\r\n", "\n")
    code_blocks: list[str] = []

    def code_repl(match: re.Match) -> str:
        body = html.unescape(match.group(1)).strip()
        code_blocks.append(f"\n```java\n{body}\n```\n")
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    text = re.sub(
        r"<pre><code(?:\s+class=\"language-java\")?>(.*?)</code></pre>",
        code_repl,
        text,
        flags=re.DOTALL,
    )

    def img_repl(match: re.Match) -> str:
        src = html.unescape(match.group(1)).strip()
        encoded = urllib.parse.quote(src, safe="/.%")
        return f"\n![{src}]({encoded})\n"

    text = re.sub(r"<br><img\s+src=\"([^\"]+)\"[^>]*>", img_repl, text)
    text = re.sub(r"<img\s+src=\"([^\"]+)\"[^>]*>", img_repl, text)
    text = text.replace("<br>", "\n")
    text = re.sub(r"</?b>", "**", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    for i, value in enumerate(code_blocks):
        text = text.replace(f"\x00CODE{i}\x00", value)
    text = normalize_cloze(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class Recorder:
    def __init__(self) -> None:
        self.decks: list[dict] = []
        self.current: dict | None = None

    def make_deck(self, deck_id: int, name: str):
        deck = {"deck_id": deck_id, "name": name, "cards": []}
        self.decks.append(deck)
        self.current = deck
        return type("_Deck", (), {"add_note": lambda s, n: None})()

    def make_front(self, problem: str, category: str) -> str:
        return f"{problem} | {category}"

    def add_basic(self, deck, front: str, back: str) -> None:
        if self.current is None:
            return
        category = front.split(" | ", 1)[1] if " | " in front else front
        self.current["cards"].append(
            {"type": "basic", "category": category, "content": html_to_mdish(back)}
        )

    def add_cloze(self, deck, text: str, extra: str = "") -> None:
        if self.current is None:
            return
        rest = text
        if " | " in text:
            rest = text.split(" | ", 1)[1]
        if "<br>" in rest:
            category, body = rest.split("<br>", 1)
        else:
            category, body = rest, ""
        # Some legacy scripts call add_cloze(deck, make_front(...), cloze_body).
        # In that style the third argument is the actual cloze text, not a hint.
        if not body.strip() and "{{c" in extra:
            body = extra
            extra = ""
        self.current["cards"].append(
            {
                "type": "cloze",
                "category": category.strip(),
                "content": html_to_mdish(body),
                "hint": html_to_mdish(extra),
            }
        )

    def img(self, name: str) -> str:
        return f'<br><img src="{name}" style="max-width:100%;margin-top:12px">'

    def code(self, java: str) -> str:
        return f'<pre><code class="language-java">{html.escape(html.unescape(java))}</code></pre>'

    def build(self, output_path: str) -> str:
        return ""


def capture(build_path: Path) -> list[dict]:
    recorder = Recorder()

    apkg = types.ModuleType("apkg_builder")
    apkg.make_deck = recorder.make_deck
    apkg.make_front = recorder.make_front
    apkg.add_basic = recorder.add_basic
    apkg.add_cloze = recorder.add_cloze
    apkg.img = recorder.img
    apkg.code = recorder.code
    apkg.build = recorder.build
    apkg.BASIC_MODEL = None
    apkg.CLOZE_MODEL = None
    apkg.HLJS_HEAD = ""

    genanki = types.ModuleType("genanki")
    genanki.Model = lambda *a, **kw: None
    genanki.Deck = lambda *a, **kw: None
    genanki.Note = lambda *a, **kw: None
    genanki.Package = lambda *a, **kw: type("_Pkg", (), {"write_to_file": lambda s, p: None})()

    old_modules = {name: sys.modules.get(name) for name in ("apkg_builder", "genanki")}
    sys.modules["apkg_builder"] = apkg
    sys.modules["genanki"] = genanki
    old_cwd = Path.cwd()
    sys.path.insert(0, str(build_path.parent))
    try:
        source = build_path.read_text(encoding="utf-8")
        exec(compile(source, str(build_path), "exec"), {"__name__": "__main__", "__file__": str(build_path)})
    finally:
        sys.path = [p for p in sys.path if p != str(build_path.parent)]
        for name, old in old_modules.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
        try:
            import os

            os.chdir(old_cwd)
        except Exception:
            pass
    return recorder.decks


def problem_name(deck_name: str) -> str:
    parts = deck_name.split("::")
    return parts[-1].strip()


def topic_name(decks: list[dict], topic_dir: Path) -> str:
    for deck in decks:
        parts = deck["name"].split("::")
        if len(parts) >= 2 and parts[0] == "算法":
            return parts[1]
    return topic_dir.name


def is_principles(deck: dict) -> bool:
    name = problem_name(deck["name"])
    return name in {"原理通识", "算法模板"} or "原理" in name or "模板" in name


SECTION_ORDER = [
    "题干",
    "回溯-选择列表",
    "回溯-终止+剪枝",
    "定义状态",
    "转移方程",
    "初始化",
    "遍历策略",
    "窗口定义",
    "指针策略",
    "核心思路",
    "复杂度",
    "关键技巧",
]


def write_problem_md(deck: dict, out_dir: Path) -> None:
    name = problem_name(deck["name"])
    grouped: dict[str, list[dict]] = {}
    for card in deck["cards"]:
        grouped.setdefault(card["category"], []).append(card)

    categories = list(grouped)
    ordered = [c for c in SECTION_ORDER if c in grouped]
    ordered += [c for c in categories if c.startswith("题解")]
    ordered += [c for c in categories if c not in ordered]

    lines = [f"# {name}", ""]
    for category in ordered:
        cards = grouped[category]
        for idx, card in enumerate(cards, start=1):
            section = category if len(cards) == 1 else f"{category}({idx})"
            lines.append(f"## {section}")
            content = card.get("content", "").strip()
            if card["type"] == "cloze":
                content = normalize_cloze(content)
                lines.append(content)
                hint = card.get("hint", "").strip()
                if hint:
                    lines.append(f"> {hint}")
            else:
                lines.append(content)
            lines.append("")

    out_path = out_dir / md_filename(name)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


BUILD_FROM_MDS = r'''"""
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

TOPIC_NAME = __TOPIC_NAME__
TEMPLATE_DECK_ID = __TEMPLATE_DECK_ID__
START_DECK_ID = __START_DECK_ID__
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
'''


def write_build_from_mds(topic_dir: Path, topic: str, decks: list[dict]) -> None:
    problem_decks = [deck for deck in decks if not is_principles(deck)]
    first_id = min((deck["deck_id"] for deck in problem_decks), default=1747300001)
    template_id = min((deck["deck_id"] for deck in decks), default=first_id - 1)
    text = BUILD_FROM_MDS
    text = text.replace("__TOPIC_NAME__", repr(topic))
    text = text.replace("__TEMPLATE_DECK_ID__", str(template_id))
    text = text.replace("__START_DECK_ID__", str(first_id))
    (topic_dir / "build_from_mds.py").write_text(text, encoding="utf-8")


def migrate(build_path: Path) -> None:
    decks = capture(build_path)
    topic_dir = build_path.parent
    topic = topic_name(decks, topic_dir)
    problems_dir = topic_dir / "problems"
    problems_dir.mkdir(exist_ok=True)
    for old in problems_dir.glob("*.md"):
        old.unlink()

    problem_decks = [deck for deck in decks if not is_principles(deck)]
    for deck in problem_decks:
        write_problem_md(deck, problems_dir)
    write_build_from_mds(topic_dir, topic, decks)
    print(f"{topic_dir}: wrote {len(problem_decks)} problem md files for topic {topic}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: migrate_topic_to_mds.py <build_*.py> [...]")
    for arg in sys.argv[1:]:
        migrate(Path(arg).resolve())


if __name__ == "__main__":
    main()
