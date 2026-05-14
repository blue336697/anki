"""Generate escaped Java code strings for build_hard.py cards."""
import re

with open(r'D:\anki\算法\力扣困难\Difficult 224444514a31807ea5d8e30a31a47260.md', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'```java\n(.*?)```'
java_blocks = list(re.finditer(pattern, content, re.DOTALL))

for i, m in enumerate(java_blocks):
    code_text = m.group(1)
    pos = m.start()
    prev_text = content[:pos]

    headings = list(re.finditer(r'^### (.+)$', prev_text, re.MULTILINE))
    problem = headings[-1].group(1).strip() if headings else 'UNKNOWN'

    sub_match = re.search(r'\*\*(.+?)\*\*\s*$', prev_text[prev_text.rfind('###'):], re.MULTILINE)
    sub = sub_match.group(1).strip() if sub_match else None

    escaped = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    print(f'# BLOCK {i+1}: {problem}' + (f' / {sub}' if sub else ''))
    print(f'# Lines: {len(code_text.strip().splitlines())}')
    print('_' * 60)

    for line in escaped.strip().split('\n'):
        print(repr(line))
    print()
    print('=' * 60)
    print()
