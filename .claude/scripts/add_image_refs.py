#!/usr/bin/env python3
"""Add image references to knowledge files by matching source headings to knowledge card headers."""
import os, re
from pathlib import Path
from collections import defaultdict
from urllib.parse import unquote

JAVA_DIR = Path("/Users/haojie.liu/personalProjects/anki/八股文/Java")
KNOWLEDGE_DIR = JAVA_DIR / "knowledge"
MAP_FILE = "/tmp/java_image_map.txt"

def find_heading_before(lines, line_idx):
    for i in range(line_idx - 1, -1, -1):
        m = re.match(r'^#{1,4}\s+(.+)', lines[i].strip())
        if m:
            return m.group(1).strip()
    return None

def find_matching_card(knowledge_lines, source_heading):
    if not source_heading:
        return None
    cards = [(i, re.match(r'^##\s+(.+)', l.strip()).group(1))
             for i, l in enumerate(knowledge_lines)
             if re.match(r'^##\s+', l.strip())]
    if not cards:
        return None
    src = source_heading.lower()
    best = (0, None)
    for idx, name in cards:
        nl = name.lower()
        score = sum(1 for w in src.split() if len(w) > 1 and w in nl)
        if src in nl or nl in src:
            score += 5
        if score > best[0]:
            best = (score, idx)
    return best[1] if best[0] >= 2 else None

def main():
    with open(MAP_FILE) as f:
        mappings = [l.strip().split("|") for l in f if l.strip()]

    by_target = defaultdict(list)
    for src_dir_str, img_name, target in mappings:
        by_target[target].append((Path(src_dir_str), img_name))

    updated = 0
    for target, img_list in sorted(by_target.items()):
        target_dir = KNOWLEDGE_DIR / target
        md_files = list(target_dir.glob("*.md"))
        if not md_files:
            continue

        md_file = md_files[0]
        text = md_file.read_text(encoding='utf-8')
        lines = text.split('\n')

        if re.search(r'!\[.*?\]\(.*?\.(?:png|jpg|svg|gif)', text):
            continue

        existing = set(p.name for p in target_dir.glob("*.png"))
        refs = []
        seen = set()

        for src_dir, img_name in img_list:
            if img_name not in existing:
                continue
            src_mds = list(JAVA_DIR.glob(f"{src_dir.name}*.md"))
            if not src_mds:
                continue
            src_lines = src_mds[0].read_text(encoding='utf-8').split('\n')
            for i, line in enumerate(src_lines):
                m = re.search(r'!\[.*?\]\((.+)\)', line)
                if not m:
                    continue
                if os.path.basename(unquote(m.group(1))) == img_name:
                    h = find_heading_before(src_lines, i)
                    if h and h not in seen:
                        seen.add(h)
                        card_line = find_matching_card(lines, h)
                        if card_line is not None:
                            refs.append((card_line, f'\n![{h}]({img_name})\n'))

        if not refs:
            # Top-of-file fallback: 1-3 images
            pngs = [n for _, n in img_list if n in existing][:3]
            refs = [(0, f'\n![{n}]({n})\n') for n in pngs]

        new_lines = list(lines)
        for insert_after, ref_line in sorted(refs, key=lambda x: -x[0]):
            new_lines.insert(insert_after + 1, ref_line.strip())

        md_file.write_text('\n'.join(new_lines), encoding='utf-8')
        updated += 1
        print(f"  + {target}: {len(refs)} refs")

    print(f"\nFiles updated: {updated}")

if __name__ == "__main__":
    main()
