"""Build the unified computer-network APKG from knowledge/**/*.md."""
import html
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPIC_DIR = Path(__file__).resolve().parent
KNOWLEDGE_ROOT = TOPIC_DIR / "knowledge"
OUTPUT_PATH = REPO_ROOT / "牌组" / "八股文" / "计算机网络" / "计算机网络八股文.apkg"
sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "anki-apkg-generator" / "scripts"))
from apkg_builder import add_basic, build, code, img, make_deck  # noqa: E402

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CODE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.S)
CATEGORY_MAP = {
    "网络基础": "八股文::计算机网络::网络基础",
    "二层与局域网": "八股文::计算机网络::二层与局域网",
    "网络层": "八股文::计算机网络::网络层",
    "传输层": "八股文::计算机网络::传输层",
    "网络编程": "八股文::计算机网络::网络编程",
    "应用层": "八股文::计算机网络::应用层",
    "代理与排障": "八股文::计算机网络::代理与排障",
}


def deck_id_for(name: str) -> int:
    return 2_900_000_000 + sum((i + 1) * ord(c) for i, c in enumerate(name)) % 100_000_000


def split_sections(text: str):
    text = text.replace("\r\n", "\n")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    title = title_match.group(1).strip() if title_match else "未命名"
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    header = text[: matches[0].start()].strip() if matches else ""
    sections = []
    for i, match in enumerate(matches):
        body = text[match.end() : matches[i + 1].start() if i + 1 < len(matches) else len(text)].strip()
        sections.append((match.group(1).strip(), (header + "\n" + body).strip() if i == 0 and header else body))
    return title, sections


def inline(line: str) -> str:
    escaped = html.escape(line)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def text_html(text: str, base: Path) -> str:
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = IMAGE_RE.search(line)
        if match:
            path = match.group(1)
            out.append(img(str(base / path)) if not path.startswith(("http://", "https://", "/")) else img(path))
        elif line.startswith("- "):
            out.append("• " + inline(line[2:]) + "<br>")
        else:
            out.append(inline(line) + "<br>")
    return "".join(out)


def render(body: str, base: Path) -> str:
    out, pos = [], 0
    for match in CODE_RE.finditer(body):
        out.append(text_html(body[pos : match.start()], base))
        out.append(code(html.unescape(match.group(2).strip("\n"))))
        pos = match.end()
    out.append(text_html(body[pos:], base))
    return "".join(out)


def parse_qa(body: str, base: Path):
    q = re.search(r"^Q:\s*(.+?)\s*$", body, re.M)
    a = re.search(r"^A:\s*$", body, re.M)
    if not q or not a:
        return "这个知识点要怎么理解？", render(body, base)
    answer = body[a.end() :].strip()
    preamble = body[: q.start()].strip()
    return q.group(1).strip(), render((preamble + "\n" + answer).strip(), base)


def validate(path: Path, title: str, sections):
    errors = []
    if title == "未命名":
        errors.append("missing H1")
    if len(sections) < 6:
        errors.append(f"only {len(sections)} cards")
    for heading, body in sections:
        qs = len(re.findall(r"^Q:\s*.+$", body, re.M))
        ans = list(re.finditer(r"^A:\s*$", body, re.M))
        if qs != 1 or len(ans) != 1:
            errors.append(f"{heading}: Q={qs}, A={len(ans)}")
        elif len(body[ans[0].end() :].strip()) < 100:
            errors.append(f"{heading}: shallow answer")
    for match in IMAGE_RE.finditer(path.read_text(encoding="utf-8")):
        target = match.group(1)
        if not target.startswith(("http://", "https://", "/")) and not (path.parent / target).exists():
            errors.append(f"missing image: {target}")
    return errors


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    old_cwd = Path.cwd()
    os.chdir(TOPIC_DIR)
    errors, used, total_files, total_cards = [], {}, 0, 0
    try:
        for category in sorted(KNOWLEDGE_ROOT.iterdir()):
            if not category.is_dir() or category.name.startswith("."):
                continue
            parent = CATEGORY_MAP.get(category.name)
            if not parent:
                errors.append(f"unknown category: {category.name}")
                continue
            for topic in sorted(category.iterdir()):
                if not topic.is_dir() or topic.name.startswith("."):
                    continue
                mds = sorted(topic.glob("*.md"))
                if not mds:
                    errors.append(f"empty topic: {topic}")
                for path in mds:
                    title, sections = split_sections(path.read_text(encoding="utf-8"))
                    errors.extend(f"{path.relative_to(TOPIC_DIR)}: {e}" for e in validate(path, title, sections))
                    name = f"{parent}::{title}"
                    did = deck_id_for(name)
                    if did in used and used[did] != name:
                        errors.append(f"deck id collision: {used[did]} / {name}")
                    used[did] = name
                    deck = make_deck(did, name)
                    for heading, body in sections:
                        question, answer = parse_qa(body, path.parent)
                        add_basic(deck, f"{title} | {heading}<br><br>{html.escape(question)}", answer)
                        total_cards += 1
                    total_files += 1
        if errors:
            print("Source validation failed:")
            print("\n".join(f"  - {e}" for e in errors))
            raise SystemExit(1)
        print(build(str(OUTPUT_PATH)))
        print(f"Knowledge files: {total_files}, cards: {total_cards}")
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    main()
