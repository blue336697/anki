"""Build APKG from computer-architecture knowledge notes."""

import html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPIC_DIR = Path(__file__).resolve().parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "anki-apkg-generator"
KNOWLEDGE_ROOT = TOPIC_DIR / "knowledge"
OUTPUT_PATH = REPO_ROOT / "牌组" / "八股文" / "计算机组成原理" / "计算机组成原理八股文.apkg"

sys.path.insert(0, str(SKILL_DIR / "scripts"))
import apkg_builder as anki  # noqa: E402

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.S)
IMG_MARKER_RE = re.compile(r"\[\[img:([A-Za-z0-9_.-]+)\]\]")


def deck_id_for(name: str) -> int:
    return 3_900_000_000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name)) % 90_000_000


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


def register_media(name: str) -> str:
    media_path = TOPIC_DIR / "diagrams" / name
    if not media_path.exists():
        raise FileNotFoundError(f"Missing diagram media: {media_path}")
    anki._images.add(str(media_path))
    return f'<br><img src="{name}" style="max-width:100%;height:auto;margin-top:12px">'


def render_markers(text: str) -> str:
    return IMG_MARKER_RE.sub(lambda m: register_media(m.group(1)), text)


def text_to_html(text: str, base_dir: Path) -> str:
    rendered: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        marker_rendered = render_markers(line)
        if marker_rendered != line:
            rendered.append(marker_rendered)
            continue
        image_match = IMAGE_RE.search(line)
        if image_match:
            img_path = image_match.group(1)
            if not img_path.startswith(("http://", "https://", "/")):
                img_path = str(base_dir / img_path)
            rendered.append(anki.img(img_path))
            continue
        if line.startswith("- "):
            rendered.append("• " + inline_markup(line[2:]) + "<br>")
        elif re.match(r"^\d+\.\s+", line):
            rendered.append(inline_markup(line) + "<br>")
        else:
            rendered.append(inline_markup(line) + "<br>")
    return "".join(rendered)


def mdish_to_html(body: str, base_dir: Path) -> str:
    parts: list[str] = []
    pos = 0
    for match in CODE_RE.finditer(body):
        before = body[pos : match.start()]
        parts.append(text_to_html(before, base_dir))
        raw = html.unescape(match.group(2).strip("\n"))
        parts.append(anki.code(raw))
        pos = match.end()
    parts.append(text_to_html(body[pos:], base_dir))
    return "".join(part for part in parts if part)


def parse_qa(body: str, base_dir: Path) -> tuple[str, str]:
    q_match = re.search(r"^Q:\s*(.+?)\s*$", body, re.M)
    a_match = re.search(r"^A:\s*$", body, re.M)
    if not q_match or not a_match:
        return "这个知识点要怎么理解？", mdish_to_html(body, base_dir)
    question = q_match.group(1).strip()
    answer = body[a_match.end():].strip()
    return question, mdish_to_html(answer, base_dir)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    total_cards = 0
    total_files = 0

    for category_dir in sorted(KNOWLEDGE_ROOT.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        for topic_dir in sorted(category_dir.iterdir()):
            if not topic_dir.is_dir() or topic_dir.name.startswith("."):
                continue
            for md_path in sorted(topic_dir.glob("*.md")):
                raw = md_path.read_text(encoding="utf-8")
                title, sections = split_sections(raw)
                deck_name = f"八股文::计算机组成原理::{category_dir.name}::{title}"
                deck = anki.make_deck(deck_id_for(deck_name), deck_name)
                for section_title, body in sections:
                    question, answer_html = parse_qa(body, md_path.parent)
                    front = f"{title} | {section_title}<br><br>{html.escape(question)}"
                    anki.add_basic(deck, front, answer_html)
                    total_cards += 1
                total_files += 1

    result = anki.build(str(OUTPUT_PATH))
    print(result)
    print(f"Knowledge files: {total_files}, cards: {total_cards}")


if __name__ == "__main__":
    main()
