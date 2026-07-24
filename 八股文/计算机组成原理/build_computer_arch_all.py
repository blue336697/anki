"""Build the unified computer-architecture APKG from knowledge/**/*.md."""

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
OUTPUT_PATH = REPO_ROOT / "牌组" / "八股文" / "计算机组成原理" / "计算机组成原理八股文.apkg"

sys.path.insert(0, str(SKILL_DIR / "scripts"))
from apkg_builder import add_basic, build, code, img, make_deck  # noqa: E402

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.S)

CATEGORY_MAP: dict[str, str] = {
    "体系结构基础": "八股文::计算机组成原理::体系结构基础",
    "程序表示": "八股文::计算机组成原理::程序表示",
    "CPU微架构": "八股文::计算机组成原理::CPU微架构",
    "存储系统": "八股文::计算机组成原理::存储系统",
    "IO系统": "八股文::计算机组成原理::IO系统",
    "并行计算": "八股文::计算机组成原理::并行计算",
    "性能分析": "八股文::计算机组成原理::性能分析",
}


def deck_id_for(name: str) -> int:
    return 3_900_000_000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name)) % 90_000_000


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    text = text.replace("\r\n", "\n")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    title = title_match.group(1).strip() if title_match else "未命名"
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    header = text[: matches[0].start()].strip() if matches else ""
    sections: list[tuple[str, str]] = []
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
            image_path = image_match.group(1)
            if base_dir and not image_path.startswith(("http://", "https://", "/")):
                image_path = str(base_dir / image_path)
            rendered.append(img(image_path))
        elif line.startswith("- "):
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
        parts.append(text_to_html(body[pos : match.start()], base_dir))
        raw = html.unescape(match.group(2).strip("\n"))
        parts.append(code(raw))
        pos = match.end()
    parts.append(text_to_html(body[pos:], base_dir))
    return "".join(part for part in parts if part)


def parse_qa(body: str, base_dir: Optional[Path] = None) -> tuple[str, str]:
    q_match = re.search(r"^Q:\s*(.+?)\s*$", body, re.M)
    a_match = re.search(r"^A:\s*$", body, re.M)
    if not q_match or not a_match:
        return "这个知识点要怎么理解？", mdish_to_html(body, base_dir)
    answer = body[a_match.end() :].strip()
    preamble = body[: q_match.start()].strip()
    if preamble:
        answer = preamble + "\n" + answer
    return q_match.group(1).strip(), mdish_to_html(answer, base_dir)


def validate_source(md_path: Path, title: str, sections: list[tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    if title == "未命名":
        errors.append("missing H1 title")
    if len(sections) < 6:
        errors.append(f"only {len(sections)} cards; expected at least 6")
    for section_title, body in sections:
        q_count = len(re.findall(r"^Q:\s*.+$", body, re.M))
        a_count = len(re.findall(r"^A:\s*$", body, re.M))
        if q_count != 1 or a_count != 1:
            errors.append(f"{section_title}: expected one Q/A pair, got Q={q_count}, A={a_count}")
        if a_count == 1:
            start = re.search(r"^A:\s*$", body, re.M)
            answer = body[start.end() :].strip() if start else ""
            if len(answer) < 100:
                errors.append(f"{section_title}: answer is too shallow ({len(answer)} chars)")
    for match in IMAGE_RE.finditer(md_path.read_text(encoding="utf-8")):
        image_path = match.group(1)
        if not image_path.startswith(("http://", "https://", "/")) and not (md_path.parent / image_path).exists():
            errors.append(f"missing image: {image_path}")
    return errors


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    old_cwd = Path.cwd()
    os.chdir(TOPIC_DIR)
    total_cards = 0
    total_files = 0
    errors: list[str] = []
    used_ids: dict[int, str] = {}
    try:
        for category_dir in sorted(KNOWLEDGE_ROOT.iterdir()):
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue
            parent_deck = CATEGORY_MAP.get(category_dir.name)
            if parent_deck is None:
                errors.append(f"unknown category: {category_dir.name}")
                continue
            for topic_dir in sorted(category_dir.iterdir()):
                if not topic_dir.is_dir() or topic_dir.name.startswith("."):
                    continue
                md_files = sorted(topic_dir.glob("*.md"))
                if not md_files:
                    errors.append(f"empty topic directory: {topic_dir.relative_to(TOPIC_DIR)}")
                for md_path in md_files:
                    title, sections = split_sections(md_path.read_text(encoding="utf-8"))
                    errors.extend(f"{md_path.relative_to(TOPIC_DIR)}: {e}" for e in validate_source(md_path, title, sections))
                    deck_name = f"{parent_deck}::{title}"
                    deck_id = deck_id_for(deck_name)
                    if deck_id in used_ids and used_ids[deck_id] != deck_name:
                        errors.append(f"deck id collision {deck_id}: {used_ids[deck_id]} vs {deck_name}")
                    used_ids[deck_id] = deck_name
                    deck = make_deck(deck_id, deck_name)
                    for section_title, body in sections:
                        question, answer_html = parse_qa(body, md_path.parent)
                        add_basic(deck, f"{title} | {section_title}<br><br>{html.escape(question)}", answer_html)
                        total_cards += 1
                    total_files += 1
        if errors:
            print("Source validation failed:")
            for error in errors:
                print(f"  - {error}")
            raise SystemExit(1)
        print(build(str(OUTPUT_PATH)))
        print(f"Knowledge files: {total_files}, cards: {total_cards}")
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    main()
