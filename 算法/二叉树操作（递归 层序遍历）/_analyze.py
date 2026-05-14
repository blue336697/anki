"""Quick analysis of build_binary_tree.py."""
import re
from pathlib import Path

text = Path(r'D:\anki\算法\二叉树操作（递归 层序遍历）\build_binary_tree.py').read_text(encoding='utf-8')

problems = re.findall(r"^p = '([^']+)'$", text, re.MULTILINE)
print(f'Problems: {len(problems)}')
for p in problems[:5]:
    print(f'  {p}')
print('  ...')
for p in problems[-3:]:
    print(f'  {p}')

basics = len(re.findall(r'add_basic\(', text))
clozes = len(re.findall(r'add_cloze\(', text))
print(f'Cards: {basics} basic + {clozes} cloze = {basics + clozes} total')

placeholders = re.findall(r'请描述[^"]*', text)
print(f'"请描述" placeholders: {len(placeholders)}')

tigan_basic_issues = 0
for m in re.finditer(r"add_basic\(d, make_front\(p, '题干'\),\s*'([^']*)'\)", text):
    if len(m.group(1)) < 20:
        tigan_basic_issues += 1
print(f'Skeletal 题干 (<20 chars): {tigan_basic_issues}')

comp_matches = re.findall(r"add_cloze\(d, make_front\(p, '复杂度'\),\s*'([^']*)'\)", text)
no_deriv = sum(1 for m in comp_matches if 'O(' in m and len(m) < 60)
print(f'复杂度 without derivation: {no_deriv}/{len(comp_matches)}')
