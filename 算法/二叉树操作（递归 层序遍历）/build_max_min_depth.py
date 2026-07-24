"""Build APKG for 二叉树最大/最小深度 — DFS & BFS solutions."""
import html
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\claudeProjects\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    escaped = html.escape(java)
    return f'<pre><code class="language-java">{escaped}</code></pre>'


# ═══════════════════════════════════════════════════════════════
# Card 1: 二叉树的最大深度 (DFS)
# ═══════════════════════════════════════════════════════════════
p1 = '二叉树的最大深度'
d1 = make_deck(1747300610, f'算法::二叉树::{p1}')

add_basic(d1, make_front(p1, '题干'),
    '给定二叉树根节点，返回根节点到最远叶子节点路径上的节点数。')

add_cloze(d1, make_front(p1, '核心思路（DFS自底向上）'),
    '空节点深度为{{c1::0}}<br>'
    '当前深度 = {{c2::max(左子树深度, 右子树深度) + 1}}<br>'
    '自底向上：先递归到底，再逐层向上汇总')

add_cloze(d1, make_front(p1, '复杂度'),
    '时间：{{c1::O(n)}} — 每个节点访问一次<br>'
    '空间：{{c2::O(h)}} — 递归调用栈深度为树高，平衡树 O(log n)，退化树 O(n)')

add_basic(d1, make_front(p1, '题解(DFS)'),
    'DFS 递归：自底向上，空节点返回0，当前层取左右子树最大深度+1<br>'
    + code(
        'class Solution {\n'
        '    public int maxDepth(TreeNode root) {\n'
        '        if (root == null) {\n'
        '            return 0;\n'
        '        }\n'
        '        int leftDepth = maxDepth(root.left);\n'
        '        int rightDepth = maxDepth(root.right);\n'
        '        return Math.max(leftDepth, rightDepth) + 1;\n'
        '    }\n'
        '}\n'
    ))

add_basic(d1, make_front(p1, '关键技巧'),
    'DFS 最大深度 = max(左深度, 右深度) + 1<br>'
    '空节点贡献深度0，终止条件为 root == null<br>'
    'BFS 也可做：层序遍历，每层计数+1')

# ═══════════════════════════════════════════════════════════════
# Card 2: 二叉树的最小深度 (BFS)
# ═══════════════════════════════════════════════════════════════
p2 = '二叉树的最小深度'
d2 = make_deck(1747300611, f'算法::二叉树::{p2}')

add_basic(d2, make_front(p2, '题干'),
    '给定二叉树根节点，返回根节点到最近叶子节点路径上的节点数。<br>'
    '注意：只有左右孩子都为 null 的节点才是叶子节点。')

add_cloze(d2, make_front(p2, '核心思路（BFS层序遍历）'),
    'BFS 逐层扫描，{{c1::第一个遇到的叶子节点}}即为最小深度<br>'
    '关键：叶子节点定义为 {{c2::左右孩子都为 null}}<br>'
    'DFS 也能做，但需特判单子树情况，不能用 min(左,右)+1 直接用')

add_cloze(d2, make_front(p2, '复杂度'),
    '时间：{{c1::O(n)}} — 最坏访问所有节点；BFS 遇叶子可提前结束<br>'
    '空间：{{c2::O(w)}} — 队列最大宽度，最坏 O(n)')

add_basic(d2, make_front(p2, '题解(BFS)'),
    'BFS 层序遍历：每层遍历时检查叶子节点，首次遇到立即返回当前深度<br>'
    + code(
        'class Solution {\n'
        '    public int minDepth(TreeNode root) {\n'
        '        if (root == null) {\n'
        '            return 0;\n'
        '        }\n'
        '        Queue<TreeNode> queue = new LinkedList<>();\n'
        '        queue.add(root);\n'
        '        int depth = 1;\n'
        '        while (!queue.isEmpty()) {\n'
        '            int size = queue.size();\n'
        '            for (int i = 0; i < size; i++) {\n'
        '                TreeNode node = queue.poll();\n'
        '                // 叶子节点：最早遇到即最小深度\n'
        '                if (node.left == null && node.right == null) {\n'
        '                    return depth;\n'
        '                }\n'
        '                if (node.left != null) {\n'
        '                    queue.add(node.left);\n'
        '                }\n'
        '                if (node.right != null) {\n'
        '                    queue.add(node.right);\n'
        '                }\n'
        '            }\n'
        '            depth++;\n'
        '        }\n'
        '        return depth;\n'
        '    }\n'
        '}\n'
    ))

add_basic(d2, make_front(p2, '关键技巧'),
    'BFS 最小深度：层序遍历，遇首个叶子直接返回 depth<br>'
    'BFS 天然适合"最短路径"场景，DFS 需要处理单子树退化情况<br>'
    'DFS 版核心：单侧为空时返回另一侧+1，两侧都非空取 min+1')

# ═══════════════════════════════════════════════════════════════
# Build APKG
# ═══════════════════════════════════════════════════════════════
build('二叉树_最大最小深度.apkg')
print('Done: 二叉树_最大最小深度.apkg')
