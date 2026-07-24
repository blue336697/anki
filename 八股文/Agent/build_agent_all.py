"""Build one APKG from all Agent/LLM interview knowledge notes."""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPIC_DIR = Path(__file__).resolve().parent
SKILL_DIRS = [
    REPO_ROOT / ".agents" / "skills" / "anki-apkg-generator",
    REPO_ROOT / ".claude" / "skills" / "anki-apkg-generator",
    REPO_ROOT / ".Codex" / "skills" / "anki-apkg-generator",
]
SKILL_DIR = next((path for path in SKILL_DIRS if (path / "scripts" / "apkg_builder.py").exists()), None)
if SKILL_DIR is None:
    raise RuntimeError("Cannot find anki-apkg-generator/scripts/apkg_builder.py")

KNOWLEDGE_ROOT = TOPIC_DIR / "knowledge" / "NootCode LLM"
OUTPUT_PATH = REPO_ROOT / "牌组" / "八股文" / "Agent" / "NootCode LLM Agent八股文.apkg"
MODULE_ORDER = ["LLM 基础", "LLM 上下文工程", "RAG", "Agent 架构设计"]

sys.path.insert(0, str(SKILL_DIR / "scripts"))
from apkg_builder import add_basic, build, code, img, make_deck  # noqa: E402

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.S)


def deck_id_for(name: str) -> int:
    return 4_700_000_000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name)) % 100_000_000


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    text = text.replace("\r\n", "\n")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    title = title_match.group(1).strip() if title_match else "未命名"
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


def text_to_html(text: str, base_dir: Path) -> str:
    rendered: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            rendered.append("</ul>")
            in_list = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            close_list()
            continue

        image_match = IMAGE_RE.search(line)
        if image_match:
            close_list()
            image_path = image_match.group(1)
            if not image_path.startswith(("http://", "https://", "/")):
                image_path = str(base_dir / image_path)
            rendered.append(img(image_path))
            continue

        if line.startswith("- "):
            if not in_list:
                rendered.append("<ul>")
                in_list = True
            rendered.append("<li>" + inline_markup(line[2:]) + "</li>")
            continue

        close_list()
        if re.match(r"^\d+\.\s+", line):
            rendered.append(inline_markup(line) + "<br>")
        else:
            rendered.append(inline_markup(line) + "<br>")

    close_list()
    return "".join(rendered)


def mdish_to_html(body: str, base_dir: Path) -> str:
    parts: list[str] = []
    pos = 0
    for match in CODE_RE.finditer(body):
        before = body[pos : match.start()]
        parts.append(text_to_html(before, base_dir))
        raw = html.unescape(match.group(2).strip("\n"))
        parts.append(code(raw))
        pos = match.end()
    parts.append(text_to_html(body[pos:], base_dir))
    return "".join(part for part in parts if part)


def parse_qa(body: str, base_dir: Path) -> tuple[str, str]:
    q_match = re.search(r"^Q:\s*(.+?)\s*$", body, re.M)
    a_match = re.search(r"^A:\s*$", body, re.M)
    if not q_match or not a_match:
        return "这个知识点要怎么理解？", mdish_to_html(body, base_dir)
    question = q_match.group(1).strip()
    answer = body[a_match.end() :].strip()
    return question, mdish_to_html(answer, base_dir)


def iter_md_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for module in MODULE_ORDER:
        module_dir = KNOWLEDGE_ROOT / module
        if not module_dir.exists():
            raise RuntimeError(f"Missing module directory: {module_dir}")
        for md_path in sorted(module_dir.glob("*/*.md")):
            files.append((module, md_path))
    return files


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    old_cwd = Path.cwd()
    os.chdir(TOPIC_DIR)

    total_cards = 0
    total_files = 0

    try:
        for module, md_path in iter_md_files():
            raw = md_path.read_text(encoding="utf-8")
            title, sections = split_sections(raw)
            deck_name = f"八股文::Agent::NootCode LLM::{module}::{title}"
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
