#!/usr/bin/env python3
"""Copy source lecture-note images to knowledge directories, renaming to avoid collisions."""
import os, shutil
from pathlib import Path
from collections import defaultdict

JAVA_DIR = Path("/Users/haojie.liu/personalProjects/anki/八股文/Java")
KNOWLEDGE_DIR = JAVA_DIR / "knowledge"
MAP_FILE = "/tmp/java_image_map.txt"

def main():
    with open(MAP_FILE) as f:
        lines = [l.strip().split("|") for l in f if l.strip()]

    copied = defaultdict(list)
    skipped = []

    for src_dir_str, img_name, target in lines:
        src_dir = Path(src_dir_str)
        src_path = src_dir / img_name

        if not src_path.exists():
            skipped.append((src_dir_str, img_name, "file not found"))
            continue

        target_dir = KNOWLEDGE_DIR / target
        target_dir.mkdir(parents=True, exist_ok=True)

        dest_name = img_name
        dest_path = target_dir / dest_name
        if dest_path.exists():
            dest_name = f"{src_dir.name}_{img_name}"
            dest_path = target_dir / dest_name

        shutil.copy2(src_path, dest_path)
        copied[target].append(dest_name)

    total = len(lines)
    ok = sum(len(v) for v in copied.values())
    print(f"Total mappings: {total}")
    print(f"Copied: {ok}")
    print(f"Skipped (missing source): {len(skipped)}")

    print(f"\n--- Per-target summary ---")
    for target in sorted(copied.keys()):
        names = copied[target]
        print(f"  {target}: {len(names)} images")

    if skipped:
        print(f"\n--- Skipped items ---")
        for src_dir, img_name, reason in skipped[:20]:
            print(f"  {src_dir} / {img_name} ({reason})")
        if len(skipped) > 20:
            print(f"  ... and {len(skipped)-20} more")

if __name__ == "__main__":
    main()
