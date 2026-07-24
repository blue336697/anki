"""Parse canonical MySQL Markdown notes into JSON for Anki synchronization."""

from __future__ import annotations

import argparse
import html
import json
import sys

from build_mysql_all import (
    KNOWLEDGE_ROOT,
    parse_qa,
    split_sections,
    tag_name,
)


def collect_notes() -> list[dict]:
    decks: list[dict] = []
    for category_dir in sorted(KNOWLEDGE_ROOT.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        for topic_dir in sorted(category_dir.iterdir()):
            if not topic_dir.is_dir() or topic_dir.name.startswith("."):
                continue
            for md_path in sorted(topic_dir.glob("*.md")):
                title, sections = split_sections(md_path.read_text(encoding="utf-8"))
                notes: list[dict] = []
                for section_title, body in sections:
                    question, answer_html = parse_qa(body, md_path.parent)
                    notes.append(
                        {
                            "fields": {
                                "Front": (
                                    f"{html.escape(title)} | {html.escape(section_title)}"
                                    f"<br><br>{html.escape(question)}"
                                ),
                                "Back": answer_html,
                            },
                            "tags": [
                                "八股文",
                                "MySQL",
                                "追问链",
                                "源码机制级",
                                "MySQL-8.4",
                                tag_name(category_dir.name),
                                tag_name(title),
                            ],
                        }
                    )
                decks.append(
                    {
                        "deck_name": (
                            f"八股文::MySQL::{category_dir.name}::{title}"
                        ),
                        "notes": notes,
                    }
                )
    return decks


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int)
    args = parser.parse_args()
    all_decks = collect_notes()
    end = None if args.count is None else args.start + args.count
    decks = all_decks[args.start:end]
    if args.summary:
        print(
            json.dumps(
                {
                    "all_decks": len(all_decks),
                    "selected_decks": len(decks),
                    "selected_notes": sum(len(deck["notes"]) for deck in decks),
                },
                ensure_ascii=False,
            )
        )
    else:
        print(json.dumps(decks, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
