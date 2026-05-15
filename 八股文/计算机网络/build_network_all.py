"""Build APKG from computer-network knowledge notes."""

import html
import os
import re
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPIC_DIR = Path(__file__).resolve().parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "anki-apkg-generator"
KNOWLEDGE_ROOT = TOPIC_DIR / "knowledge"
OUTPUT_PATH = REPO_ROOT / "牌组" / "八股文" / "计算机网络" / "计算机网络八股文.apkg"

sys.path.insert(0, str(SKILL_DIR / "scripts"))
from apkg_builder import add_basic, build, code, img, make_deck  # noqa: E402

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.S)


def deck_id_for(name: str) -> int:
    return 2_900_000_000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name)) % 100_000_000


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    text = text.replace("\r\n", "\n")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    title = title_match.group(1).strip() if title_match else "未命名"
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    sections: list[tuple[str, str]] = []
    if matches:
        header_end = matches[0].start()
        header = text[:header_end].strip()
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if i == 0 and header:
            body = header + "\n" + body
        sections.append((match.group(1).strip(), body))
    return title, sections


def inline_markup(line: str) -> str:
    escaped = html.escape(line)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def text_to_html(text: str, base_dir: Optional[Path] = None) -> str:
    rendered: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        image_match = IMAGE_RE.search(line)
        if image_match:
            img_path = image_match.group(1)
            if base_dir and not img_path.startswith(("http://", "https://", "/")):
                img_path = str(base_dir / img_path)
            rendered.append(img(img_path))
            continue
        if line.startswith("- "):
            rendered.append("• " + inline_markup(line[2:]) + "<br>")
        elif re.match(r"^\d+\.\s+", line):
            rendered.append(inline_markup(line) + "<br>")
        else:
            rendered.append(inline_markup(line) + "<br>")
    return "".join(rendered)


def mdish_to_html(body: str, base_dir: Optional[Path] = None) -> str:
    parts: list[str] = []
    pos = 0
    for match in CODE_RE.finditer(body):
        before = body[pos : match.start()]
        parts.append(text_to_html(before, base_dir))
        lang = (match.group(1) or "").lower()
        raw = html.unescape(match.group(2).strip("\n"))
        if lang in {"c", "cpp", "java", ""}:
            parts.append(code(raw))
        else:
            parts.append(f"<pre><code>{html.escape(raw)}</code></pre>")
        pos = match.end()
    parts.append(text_to_html(body[pos:], base_dir))
    return "".join(part for part in parts if part)


def parse_qa(body: str, base_dir: Optional[Path] = None) -> tuple[str, str]:
    q_match = re.search(r"^Q:\s*(.+?)\s*$", body, re.M)
    a_match = re.search(r"^A:\s*$", body, re.M)
    if not q_match or not a_match:
        return "这个知识点要怎么理解？", mdish_to_html(body)
    question = q_match.group(1).strip()
    answer = body[a_match.end():].strip()
    preamble = body[:q_match.start()].strip()
    if preamble:
        answer = preamble + "\n" + answer
    return question, mdish_to_html(answer, base_dir)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    old_cwd = Path.cwd()
    os.chdir(TOPIC_DIR)

    total_cards = 0
    total_files = 0

    try:
        for category_dir in sorted(KNOWLEDGE_ROOT.iterdir()):
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for topic_dir in sorted(category_dir.iterdir()):
                if not topic_dir.is_dir() or topic_dir.name.startswith("."):
                    continue
                for md_path in sorted(topic_dir.glob("*.md")):
                    raw = md_path.read_text(encoding="utf-8")
                    title, sections = split_sections(raw)
                    deck_name = f"八股文::计算机网络::{category_dir.name}::{title}"
                    deck = make_deck(deck_id_for(deck_name), deck_name)
                    for section_title, body in sections:
                        question, answer_html = parse_qa(body, md_path.parent)
                        front = f"{title} | {section_title}<br><br>{html.escape(question)}"
                        add_basic(deck, front, answer_html)
                        total_cards += 1
                    total_files += 1

        result = build(str(OUTPUT_PATH))
        print(result)
        print(f"Knowledge files: {total_files}, cards: {total_cards}")
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    main()
