import re
from pathlib import Path

problems_dir = Path(r"D:\anki\算法\二叉树操作（递归 层序遍历）\problems")
total = 0
empty_tigan = []
empty_complexity = []
code_in_tigan = []

for md_path in sorted(problems_dir.glob("*.md")):
    text = md_path.read_text(encoding="utf-8")
    total += 1

    sections = {}
    section_heads = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
    for i, m in enumerate(section_heads):
        name = m.group(1).strip()
        start = m.end()
        end = section_heads[i + 1].start() if i + 1 < len(section_heads) else len(text)
        sections[name] = text[start:end].strip()

    tigan = sections.get("题干", "")
    if len(tigan.strip()) < 10:
        empty_tigan.append(md_path.name)

    if "```" in tigan:
        code_in_tigan.append(md_path.name)

    complexity = sections.get("复杂度", "")
    if len(complexity.strip()) < 10:
        empty_complexity.append(md_path.name)

print(f"Total: {total}")
print(f"\nEmpty 题干 (<10 chars): {len(empty_tigan)}")
for name in empty_tigan[:15]:
    print(f"  {name}")
if len(empty_tigan) > 15:
    print(f"  ... and {len(empty_tigan)-15} more")

print(f"\nCode in 题干: {len(code_in_tigan)}")
for name in code_in_tigan:
    print(f"  {name}")

print(f"\nEmpty 复杂度 (<10 chars): {len(empty_complexity)}")
for name in empty_complexity[:15]:
    print(f"  {name}")
if len(empty_complexity) > 15:
    print(f"  ... and {len(empty_complexity)-15} more")
