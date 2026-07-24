"""Build design-pattern and DDD cards from knowledge/**/*.md."""
import html
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPIC = Path(__file__).resolve().parent
SOURCE = TOPIC / "knowledge"
OUTPUT = ROOT / "牌组" / "八股文" / "设计模式" / "设计模式与DDD八股文.apkg"
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "anki-apkg-generator" / "scripts"))
from apkg_builder import add_basic, build, code, make_deck  # noqa: E402

CODE_RE = re.compile(r"```(?:java)?\n(.*?)```", re.S)
CATEGORIES = {
    "设计原则": "八股文::设计模式与DDD::设计原则",
    "创建型": "八股文::设计模式与DDD::创建型",
    "结构型": "八股文::设计模式与DDD::结构型",
    "行为型": "八股文::设计模式与DDD::行为型",
    "DDD战略设计": "八股文::设计模式与DDD::DDD战略设计",
    "DDD战术设计": "八股文::设计模式与DDD::DDD战术设计",
    "DDD工程落地": "八股文::设计模式与DDD::DDD工程落地",
}


def deck_id(name):
    return 3_700_000_000 + sum((i + 1) * ord(c) for i, c in enumerate(name)) % 100_000_000


def split(text):
    text = text.replace("\r\n", "\n")
    title = re.search(r"^#\s+(.+)$", text, re.M)
    marks = list(re.finditer(r"^##\s+(.+)$", text, re.M))
    return (title.group(1).strip() if title else "未命名"), [
        (m.group(1).strip(), text[m.end() : marks[i + 1].start() if i + 1 < len(marks) else len(text)].strip())
        for i, m in enumerate(marks)
    ]


def text_html(text):
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        escaped = html.escape(line)
        escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
        out.append(("• " + escaped[2:] if line.startswith("- ") else escaped) + "<br>")
    return "".join(out)


def render(body):
    out, pos = [], 0
    for match in CODE_RE.finditer(body):
        out.append(text_html(body[pos : match.start()]))
        out.append(code(html.unescape(match.group(1).strip("\n"))))
        pos = match.end()
    out.append(text_html(body[pos:]))
    return "".join(out)


def qa(body):
    q = re.search(r"^Q:\s*(.+)$", body, re.M)
    a = re.search(r"^A:\s*$", body, re.M)
    return (q.group(1).strip(), render(body[a.end() :].strip())) if q and a else ("如何理解？", render(body))


def validate(path, title, sections):
    errors = []
    if title == "未命名" or len(sections) < 5:
        errors.append("missing title or fewer than 5 cards")
    if not CODE_RE.search(path.read_text(encoding="utf-8")):
        errors.append("topic has no Java example")
    for heading, body in sections:
        qs = len(re.findall(r"^Q:\s*.+$", body, re.M))
        ans = list(re.finditer(r"^A:\s*$", body, re.M))
        if qs != 1 or len(ans) != 1:
            errors.append(f"{heading}: Q={qs}, A={len(ans)}")
        elif len(body[ans[0].end() :].strip()) < 90:
            errors.append(f"{heading}: shallow answer")
    return errors


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    previous = Path.cwd()
    os.chdir(TOPIC)
    errors, ids, file_count, card_count = [], {}, 0, 0
    try:
        for category in sorted(SOURCE.iterdir()):
            if not category.is_dir():
                continue
            parent = CATEGORIES.get(category.name)
            if not parent:
                errors.append(f"unknown category {category.name}")
                continue
            for topic in sorted(category.iterdir()):
                if not topic.is_dir():
                    continue
                for path in sorted(topic.glob("*.md")):
                    title, sections = split(path.read_text(encoding="utf-8"))
                    errors.extend(f"{path.relative_to(TOPIC)}: {e}" for e in validate(path, title, sections))
                    name = f"{parent}::{title}"
                    did = deck_id(name)
                    if did in ids and ids[did] != name:
                        errors.append(f"deck id collision: {ids[did]} / {name}")
                    ids[did] = name
                    deck = make_deck(did, name)
                    for heading, body in sections:
                        question, answer = qa(body)
                        add_basic(deck, f"{title} | {heading}<br><br>{html.escape(question)}", answer)
                        card_count += 1
                    file_count += 1
        if errors:
            print("Source validation failed:")
            print("\n".join(f"  - {e}" for e in errors))
            raise SystemExit(1)
        print(build(str(OUTPUT)))
        print(f"Knowledge files: {file_count}, cards: {card_count}")
    finally:
        os.chdir(previous)


if __name__ == "__main__":
    main()
