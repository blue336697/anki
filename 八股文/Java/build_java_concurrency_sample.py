from __future__ import annotations

import html
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOPIC_DIR = Path(__file__).resolve().parent
SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "anki-apkg-generator"
KNOWLEDGE_DIR = TOPIC_DIR / "knowledge" / "Java多并发（二） cas & synchronized & volatile的内存语义"
OUTPUT_PATH = REPO_ROOT / "牌组" / "八股文" / "Java" / "Java并发样板.apkg"

sys.path.insert(0, str(SKILL_DIR / "scripts"))
from apkg_builder import add_basic, build, code, img, make_deck  # noqa: E402


IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.S)


def deck_id_for(name: str) -> int:
    return 2600000000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name)) % 100000000


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    title_match = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    title = title_match.group(1).strip() if title_match else "未命名知识点"
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    sections: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[start:end].strip()))
    return title, sections


def inline_markup(line: str) -> str:
    escaped = html.escape(line)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def mdish_to_html(body: str) -> str:
    parts: list[str] = []
    pos = 0
    for match in CODE_RE.finditer(body):
        before = body[pos:match.start()]
        parts.append(text_to_html(before))
        lang = (match.group(1) or "").lower()
        raw = html.unescape(match.group(2).strip("\n"))
        parts.append(code(raw) if lang in {"java", ""} else f"<pre><code>{html.escape(raw)}</code></pre>")
        pos = match.end()
    parts.append(text_to_html(body[pos:]))
    return "".join(part for part in parts if part)


def text_to_html(text: str) -> str:
    rendered: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        image_match = IMAGE_RE.search(line)
        if image_match:
            rendered.append(img(image_match.group(1)))
            continue
        if line.startswith("- "):
            rendered.append("• " + inline_markup(line[2:]) + "<br>")
        elif re.match(r"^\d+\.\s+", line):
            rendered.append(inline_markup(line) + "<br>")
        else:
            rendered.append(inline_markup(line) + "<br>")
    return "".join(rendered)


def parse_qa(body: str) -> tuple[str, str]:
    q_match = re.search(r"^Q:\s*(.+?)\s*$", body, re.M)
    a_match = re.search(r"^A:\s*$", body, re.M)
    if not q_match or not a_match:
        return "这个知识点要怎么理解？", mdish_to_html(body)
    question = q_match.group(1).strip()
    answer = body[a_match.end() :].strip()
    return question, mdish_to_html(answer)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    old_cwd = Path.cwd()
    try:
        # apkg_builder.img registers media relative to the current working directory.
        import os

        os.chdir(TOPIC_DIR)
        total_cards = 0
        for md_path in sorted(KNOWLEDGE_DIR.glob("*.md")):
            title, sections = split_sections(md_path.read_text(encoding="utf-8"))
            deck = make_deck(deck_id_for(title), f"八股文::Java::并发::{title}")
            for section_title, body in sections:
                question, answer = parse_qa(body)
                front = f"{title} | {section_title}<br><br>{html.escape(question)}"
                add_basic(deck, front, answer)
                total_cards += 1
        print(build(str(OUTPUT_PATH)))
        print(f"Knowledge files: {len(list(KNOWLEDGE_DIR.glob('*.md')))}, cards: {total_cards}")
    finally:
        import os

        os.chdir(old_cwd)


if __name__ == "__main__":
    main()
