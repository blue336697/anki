"""
_split_to_mds.py — Split monolithic md + build_binary_tree.py into individual problem mds.
Uses a recording shim to capture card data by executing build_binary_tree.py.
"""
import html as _html
import re
import sys
import types
from pathlib import Path

TOPIC_DIR = Path(r'D:\anki\算法\二叉树操作（递归 层序遍历）')
MD_PATH = TOPIC_DIR / '二叉树操作（递归 层序遍历） 259444514a3180218ebcc22a1a2f15dd.md'
BUILD_PATH = TOPIC_DIR / 'build_binary_tree.py'
PROBLEMS_DIR = TOPIC_DIR / 'problems'


# ============================================================
# Recording shim
# ============================================================

_record: dict[str, dict] = {}
_current_p: list[str | None] = [None]


def _record_make_deck(deck_id: int, name: str):
    parts = name.split('::')
    _current_p[0] = parts[-1] if len(parts) > 2 else name
    _record[_current_p[0]] = {'deck_id': deck_id, 'cards': []}
    return type('_D', (), {'add_note': lambda s, n: None})()


def _record_add_basic(deck, front: str, back: str) -> None:
    p = _current_p[0]
    if not p:
        return
    if ' | ' in front:
        _, category = front.split(' | ', 1)
    else:
        category = front
    _record[p]['cards'].append({
        'type': 'basic', 'category': category, 'content': back,
    })


def _record_add_cloze(deck, text: str, extra: str = '') -> None:
    p = _current_p[0]
    if not p:
        return
    if ' | ' in text:
        _, rest = text.split(' | ', 1)
        if '<br>' in rest:
            category, cloze = rest.split('<br>', 1)
        else:
            category, cloze = rest, ''
    else:
        category = text
        cloze = ''
    _record[p]['cards'].append({
        'type': 'cloze', 'category': category, 'text': cloze, 'hint': extra,
    })


def _record_make_front(problem: str, category: str) -> str:
    return f'{problem} | {category}'


def _record_img(name: str) -> str:
    return f'<br><img src="{name}">'


def _record_code(java: str) -> str:
    return f'<pre><code class="language-java">{_html.escape(java)}</code></pre>'


def _record_build(output_path: str) -> str:
    return ''


_a = types.ModuleType('apkg_builder')
_a.make_deck = _record_make_deck
_a.add_basic = _record_add_basic
_a.add_cloze = _record_add_cloze
_a.make_front = _record_make_front
_a.img = _record_img
_a.code = _record_code
_a.build = _record_build
_a.BASIC_MODEL = None
_a.CLOZE_MODEL = None
_a.HLJS_HEAD = ''

_g = types.ModuleType('genanki')
_g.Model = lambda *a, **kw: None
_g.Deck = lambda *a, **kw: None
_g.Note = lambda *a, **kw: None
_g.Package = lambda *a: type('_P', (), {'write_to_file': lambda s, p: None})()


def capture_build_data() -> dict[str, dict]:
    """Execute build_binary_tree.py with recording shim."""
    sys.modules['apkg_builder'] = _a
    sys.modules['genanki'] = _g
    exec(BUILD_PATH.read_text(encoding='utf-8'), {'__name__': '__main__'})
    return _record


# ============================================================
# Source MD parsing
# ============================================================

def parse_source_md() -> dict[str, str]:
    """Parse source md: {cleaned_heading: body}."""
    content = MD_PATH.read_text(encoding='utf-8')
    lines = content.split('\n')

    problems: dict[str, str] = {}
    heading_pat = re.compile(r'^###\s+(.+)$')
    seen: set[str] = set()

    i = 0
    while i < len(lines):
        m = heading_pat.match(lines[i])
        if m and i == 0:
            i += 1
            continue
        if m:
            raw = m.group(1)
            name = raw.replace('**', '').strip()
            if name in seen:
                i += 1
                continue
            seen.add(name)

            j = i + 1
            while j < len(lines) and not heading_pat.match(lines[j]):
                j += 1

            body = '\n'.join(lines[i + 1:j]).strip()
            problems[name] = body
            i = j
        else:
            i += 1

    return problems


# ============================================================
# MD writing helpers
# ============================================================

def extract_java_code_from_html(html_content: str) -> str | None:
    """Extract Java code from a code()-wrapped HTML string."""
    m = re.search(
        r'<pre><code class="language-java">(.*?)</code></pre>',
        html_content, re.DOTALL
    )
    if not m:
        return None
    code_text = m.group(1)
    code_text = _html.unescape(code_text)
    return code_text.strip()


def _extract_code_from_body(body: str) -> str | None:
    """Extract Java code from source md body."""
    m = re.search(r'```(?:java)?\n(.*?)```', body, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def clean_body_for_tigan(body: str) -> str:
    """Remove code blocks and orphan headings from body."""
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    lines = body.split('\n')
    result: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith('**') and s.endswith('**') and len(s) < 50:
            continue
        result.append(line)
    body = '\n'.join(result)
    body = re.sub(r'\n{4,}', '\n\n\n', body)
    return body.strip()


def infer_strategy(name: str) -> str:
    """Infer traversal strategy from problem name."""
    n = name
    if '前序' in n or '先序' in n or 'preorder' in n.lower():
        return '前序遍历：根→左→右。递归或迭代(栈：根入栈→弹出入右左)实现。'
    if '中序' in n or 'inorder' in n.lower():
        return '中序遍历：左→根→右。递归或迭代(栈)实现。BST的中序结果严格递增。'
    if '后序' in n or 'postorder' in n.lower():
        return '后序遍历：左→右→根。递归或迭代(栈+prev指针)实现。自底向上汇总子树结果。'
    if '层序' in n or '层次' in n or 'level' in n.lower() or '从顶' in n or '从上' in n:
        return '层序遍历(BFS)：队列存储，每层按size循环处理。'
    if '锯齿' in n or 'zigzag' in n.lower():
        return '层序遍历 + 方向标志位：每层遍历后根据标志位决定是否反转当前层结果。'
    if '最大深度' in n or '最小深度' in n:
        return '自底向上递归：depth = max/min(left, right) + 1。BFS也可用于最小深度：首次遇到叶子返回深度。'
    if '直径' in n:
        return '自底向上：每个节点计算 leftDepth + rightDepth 更新全局max，返回 max(left,right)+1。'
    if '对称' in n or '镜像' in n:
        return '递归比较两棵子树是否为镜像（p.left vs q.right 且 p.right vs q.left）。BFS队列也可。'
    if '翻转' in n or '反转' in n:
        return '前序或后序：交换左右子树后递归翻转。层序也可。'
    if '路径' in n and ('和' in n or '总和' in n):
        return 'DFS回溯：到达叶子节点时检查 sum==targetSum。路径总和III用前缀和+HashMap优化。'
    if '路径' in n and '最大' in n:
        return '自底向上：每个节点返回以该节点为起点的最大路径和贡献（max(0, left), max(0, right)），更新全局max。'
    if '公共祖先' in n or 'LCA' in n.upper():
        return '递归：若root是p或q返回root。分别在左右子树查找，两边都找到则root是LCA。'
    if '验证' in n or '合法' in n or 'BST' in n.upper():
        return '中序遍历检查是否严格递增。或递归：传递(lo, hi)区间约束每个节点值。'
    if '恢复' in n or '纠正' in n:
        return '中序遍历：找到两个错位的节点并交换值。相邻错位和不相邻错位分开处理。'
    if '序列化' in n:
        return '前序DFS序列化（用特殊标记null），反序列化时按相同顺序重建。可用队列优化。'
    if '构造' in n or '重建' in n or '从中序' in n or '前序中序' in n or '中序后序' in n:
        return '前序/后序找根，中序分左右子树，递归构造。核心：HashMap存储inorder中val→index映射O(1)查找。'
    if '完全' in n:
        return 'BFS层序遍历，检查是否出现过null节点后又出现非null节点。'
    if '平衡' in n:
        return '自底向上递归：返回子树高度，若左右高度差>1则标记为不平衡（返回-1）。'
    if 'BST' in n or '二叉搜索树' in n or '二叉查找树' in n:
        return '利用BST性质：左<根<右。中序遍历得到有序序列。插入、删除、查找都是O(h)。'
    if '叶子' in n:
        return 'DFS遍历，在叶子节点收集结果。'
    if '节点个数' in n or '节点数' in n or '完全二叉树' in n:
        return '递归计数。完全二叉树利用性质：最左深度==最右深度→满二叉树公式2^h-1，否则递归计算。'
    if '右视图' in n or '左视图' in n:
        return 'BFS层序遍历，每层取第一个（左视图）或最后一个（右视图）节点的值。'
    if '展开' in n and '链表' in n:
        return '后序遍历：先将左右子树分别展开，然后右指针指向左子树末尾接右子树。或Morris遍历。'
    if '填充' in n and 'next' in n:
        return '层序BFS：每层从左到右连接next指针。优化：利用已建立的next指针，O(1)空间。'
    if '打家劫舍' in n:
        return '树形DP：每个节点返回两个值 [偷当前节点的收益, 不偷当前节点的收益]。自底向上。'
    return '递归三部曲：1.终止条件 2.处理当前节点逻辑 3.递归调用左右子树。'


def infer_tip(name: str, java_code: str | None) -> str:
    """Infer key technique from problem context and code patterns."""
    tips: list[str] = []
    if java_code:
        if 'Queue' in java_code or 'Deque' in java_code:
            tips.append('BFS层序遍历：队列+每层size循环')
        if 'Stack' in java_code:
            tips.append('栈模拟递归：前序直接入栈，中序先左后根，后序用prev标记')
        if 'HashMap' in java_code or 'Map<' in java_code:
            tips.append('HashMap存储中序val→index映射，O(1)定位根节点位置')
        if 'prev' in java_code.lower() or 'pre' in java_code.lower():
            tips.append('prev指针记录前驱节点，用于中序遍历线索化或节点交换')
        if 'return Math.max' in java_code or 'Math.max' in java_code:
            tips.append('自底向上递归：先计算子树结果，再汇总返回当前层')
        if 'return Math.min' in java_code:
            tips.append('自底向上递归：取左右子树的最小值+1向上传递')
        if 'long' in java_code.lower():
            tips.append('使用long类型防止int溢出')
        if 'Integer.MAX_VALUE' in java_code or 'Integer.MIN_VALUE' in java_code:
            tips.append('极值初始化：用Integer.MAX_VALUE/MIN_VALUE作为哨兵')
        if 'List<List<Integer>>' in java_code:
            tips.append('List<List<Integer>>收集每层结果，new ArrayList<>()创建临时列表')
        if 'backtrack' in java_code.lower() or 'remove(' in java_code:
            tips.append('DFS+回溯：递归后撤销选择（path.removeLast()）')
    if not tips:
        tips.append('递归三部曲：1.终止条件 2.处理当前层逻辑 3.递归调用左右子树')
    return '；'.join(tips)


# ============================================================
# Main
# ============================================================

def write_problem_md(name: str, md_body: str, cards: list[dict]) -> None:
    """Write individual problem md with standard ## sections."""
    lines = [f'# {name}', '']

    # 题干 — from source md body (code blocks removed)
    tigan_body = clean_body_for_tigan(md_body)
    lines.append('## 题干')
    if tigan_body:
        lines.append(tigan_body)
    lines.append('')

    card_map: dict[str, dict] = {}
    for card in cards:
        cat = card.get('category', '')
        card_map[cat] = card

    # 遍历策略
    strategy = card_map.get('遍历/递归策略', {})
    lines.append('## 遍历策略')
    s_content = strategy.get('content', '')
    if s_content and not s_content.startswith('请描述') and len(s_content) > 10:
        lines.append(s_content)
    else:
        lines.append(infer_strategy(name))
    lines.append('')

    # 复杂度
    comp = card_map.get('复杂度', {})
    lines.append('## 复杂度')
    c_text = comp.get('text', '')
    if c_text:
        lines.append(c_text)
    lines.append('')

    # 题解
    sol = card_map.get('题解(BFS/DFS)', {})
    lines.append('## 题解(BFS/DFS)')
    sol_content = sol.get('content', '')
    java_code = extract_java_code_from_html(sol_content)
    if not java_code:
        java_code = _extract_code_from_body(md_body)
    if java_code:
        desc = ''
        if '<pre>' in sol_content:
            desc = sol_content[:sol_content.find('<pre>')].strip()
            # Remove HTML tags from description
            desc = re.sub(r'<[^>]+>', '', desc)
        if desc:
            lines.append(desc)
            lines.append('')
        lines.append('```java')
        lines.append(java_code)
        lines.append('```')
    elif sol_content.strip():
        lines.append(sol_content)
    lines.append('')

    # 关键技巧
    tip = card_map.get('关键技巧', {})
    lines.append('## 关键技巧')
    t_content = tip.get('content', '')
    if t_content and not t_content.startswith('请总') and len(t_content) > 5:
        lines.append(t_content)
    else:
        lines.append(infer_tip(name, java_code))
    lines.append('')

    PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = name.replace('/', '_').replace('\\', '_')
    (PROBLEMS_DIR / f'{safe_name}.md').write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    print('Capturing card data from build_binary_tree.py...')
    build_data = capture_build_data()
    # Remove template deck
    build_data.pop('原理通识', None)
    print(f'  Found {len(build_data)} problems in build script')

    print('Parsing source markdown...')
    md_data = parse_source_md()
    print(f'  Found {len(md_data)} problems in source md')

    written = 0
    for p_name, bdata in build_data.items():
        mdata = md_data.get(p_name)
        if not mdata:
            for mname in md_data:
                if p_name in mname or mname in p_name:
                    mdata = md_data[mname]
                    break
        if not mdata:
            print(f'  WARNING: No source md data for "{p_name}"')
            mdata = ''

        write_problem_md(p_name, mdata, bdata['cards'])
        written += 1

    print(f'\nDone: {written} md files -> {PROBLEMS_DIR}')


if __name__ == '__main__':
    main()
