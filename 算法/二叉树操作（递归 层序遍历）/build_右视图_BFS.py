"""Build APKG for 二叉树的右视图 BFS解法 — 1 card."""
import html
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\claudeProjects\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    escaped = html.escape(java)
    return f'<pre><code class="language-java">{escaped}</code></pre>'


# ═══════════════════════════════════════════════════════════════
# Card: 二叉树的右视图 (BFS)
# ═══════════════════════════════════════════════════════════════
p = '二叉树的右视图'
d = make_deck(1747300800, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '给定二叉树根节点，返回从右侧观察这棵树时从上到下能看到的节点值。每层只保留最右侧节点。')

add_cloze(d, make_front(p, 'BFS核心思路'),
    'BFS层序遍历，每层用 {{c1::size}} 控制遍历节点数<br>'
    '当 {{c2::i == size - 1}} 时（即当前层最后一个节点），将其值加入结果列表<br>'
    '本质：BFS天然按层处理，每层最右节点 = 右视图看到的节点')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个节点入队出队一次<br>'
    '空间：{{c2::O(w)}} — 队列最多存最大层宽 w 个节点，最坏 O(n)')

add_basic(d, make_front(p, '题解(BFS右视图)'),
    'BFS层序遍历：每层遍历size个节点，i==size-1时为该层最右节点，加入结果<br>'
    + code(
        'class Solution {\n'
        '    public List<Integer> rightSideView(TreeNode root) {\n'
        '        List<Integer> res = new ArrayList<>();\n'
        '        if (root == null) {\n'
        '            return res;\n'
        '        }\n'
        '        Queue<TreeNode> queue = new LinkedList<>();\n'
        '        queue.offer(root);\n'
        '        while (!queue.isEmpty()) {\n'
        '            int size = queue.size();\n'
        '            for (int i = 0; i < size; i++) {\n'
        '                TreeNode node = queue.poll();\n'
        '                if (node.left != null) {\n'
        '                    queue.offer(node.left);\n'
        '                }\n'
        '                if (node.right != null) {\n'
        '                    queue.offer(node.right);\n'
        '                }\n'
        '                // 当前层最后一个节点即为右视图看到的节点\n'
        '                if (i == size - 1) {\n'
        '                    res.add(node.val);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'BFS右视图：层序遍历中 i == size - 1 时记录节点<br>'
    '对比DFS右视图：根→右→左优先遍历，depth==list.size()时记录<br>'
    '两种方法时间复杂度相同，BFS更直观无需维护深度参数')

# ═══════════════════════════════════════════════════════════════
# Build APKG
# ═══════════════════════════════════════════════════════════════
OUTPUT_DIR = Path(r'D:\claudeProjects\anki\牌组\算法')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
build(str(OUTPUT_DIR / '二叉树_右视图_BFS.apkg'))
print('Done: 二叉树_右视图_BFS.apkg')
