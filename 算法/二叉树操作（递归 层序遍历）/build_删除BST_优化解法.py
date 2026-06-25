"""Build APKG for 删除二叉搜索树中的节点 优化解法 — 2 cards.
Card 1: 交换值 + 递归删后继
Card 2: 删除后自适应AVL自平衡
"""
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
# Card 1: 交换值 + 递归删后继
# ═══════════════════════════════════════════════════════════════
p1 = '删除二叉搜索树中的节点'
d1 = make_deck(1747300801, f'算法::二叉树::{p1}')

add_basic(d1, make_front(p1, '题干'),
    '给定二叉搜索树根节点和key，删除值为key的节点，保持BST性质。<br>'
    '本解法：交换值+递归删后继，比移动子树更简洁。')

add_cloze(d1, make_front(p1, '交换值递归删后继-核心思路'),
    '删除分三种情况：<br>'
    '1. 无左子 → 返回 {{c1::右子}}<br>'
    '2. 无右子 → 返回 {{c2::左子}}<br>'
    '3. 双子都存在 → 找 {{c3::右子树最左节点（后继）}}，将后继值赋给当前节点，再递归删除后继<br>'
    '与移动子树法的区别：不修改指针结构，仅 {{c4::交换值}}')

add_cloze(d1, make_front(p1, '复杂度'),
    '时间：{{c1::O(h)}} — 查找 successor 沿右子树左侧走到底，最多 O(h)<br>'
    '空间：{{c2::O(h)}} — 递归调用栈深度，平衡树 O(log n)，退化树 O(n)')

add_basic(d1, make_front(p1, '题解(交换值递归删后继)'),
    '找后继（右子树最小节点）→ 交换值 → 递归删后继<br>'
    + code(
        'class Solution {\n'
        '    public TreeNode deleteNode(TreeNode root, int key) {\n'
        '        if (root == null) {\n'
        '            return null;\n'
        '        }\n'
        '        if (key < root.val) {\n'
        '            root.left = deleteNode(root.left, key);\n'
        '        } else if (key > root.val) {\n'
        '            root.right = deleteNode(root.right, key);\n'
        '        } else {\n'
        '            // 找到待删除节点\n'
        '            if (root.left == null) {\n'
        '                return root.right;  // 无左子，右子直接顶替\n'
        '            }\n'
        '            if (root.right == null) {\n'
        '                return root.left;   // 无右子，左子直接顶替\n'
        '            }\n'
        '            // 左右子树都存在：找后继（右子树最小节点）\n'
        '            TreeNode successor = root.right;\n'
        '            while (successor.left != null) {\n'
        '                successor = successor.left;\n'
        '            }\n'
        '            // 后继值赋给当前节点，递归删除后继\n'
        '            root.val = successor.val;\n'
        '            root.right = deleteNode(root.right, successor.val);\n'
        '        }\n'
        '        return root;\n'
        '    }\n'
        '}\n'
    ))

add_basic(d1, make_front(p1, '关键技巧'),
    '交换值法的优势：代码简洁，不手动移动子树指针<br>'
    '后继一定没有左孩子，递归删它只会走情况1或2，最多递归一层<br>'
    '对比移动子树法：需要手动将左子树嫁接到后继的左孩子')

# ═══════════════════════════════════════════════════════════════
# Card 2: 删除后自适应AVL自平衡
# ═══════════════════════════════════════════════════════════════
p2 = '删除二叉搜索树中的节点'
d2 = make_deck(1747300802, f'算法::二叉树::{p2}')

add_basic(d2, make_front(p2, '题干'),
    '在BST删除的基础上，删除后自底向上检查AVL平衡因子，'
    '通过旋转操作恢复平衡，确保树高始终为O(log n)。')

add_cloze(d2, make_front(p2, 'AVL自平衡-核心思路'),
    '删除后从被删位置向上回溯，计算 balance = {{c1::height(left) - height(right)}}<br>'
    '若 |balance| > 1，分四种情况旋转：<br>'
    'LL：左子树的左子树过高 → {{c2::右旋}}<br>'
    'RR：右子树的右子树过高 → {{c3::左旋}}<br>'
    'LR：左子树的右子树过高 → 先{{c4::左旋左子}}再{{c5::右旋}}<br>'
    'RL：右子树的左子树过高 → 先{{c6::右旋右子}}再{{c7::左旋}}')

add_cloze(d2, make_front(p2, 'AVL自平衡-复杂度'),
    '时间：{{c1::O(log n)}} — 平衡树高 O(log n)，查找+回溯均沿一条路径<br>'
    '空间：{{c2::O(log n)}} — 递归调用栈深度<br>'
    '注意：height() 每次都遍历子树为 O(n)，生产中应在节点存高度字段')

add_basic(d2, make_front(p2, '题解(AVL自平衡删除)'),
    'BST删除 + 自底向上检查平衡因子 + 四种旋转恢复平衡<br>'
    + code(
        'class Solution {\n'
        '    public TreeNode deleteNode(TreeNode root, int key) {\n'
        '        if (root == null) {\n'
        '            return null;\n'
        '        }\n'
        '        if (key < root.val) {\n'
        '            root.left = deleteNode(root.left, key);\n'
        '        } else if (key > root.val) {\n'
        '            root.right = deleteNode(root.right, key);\n'
        '        } else {\n'
        '            if (root.left == null) {\n'
        '                return root.right;\n'
        '            }\n'
        '            if (root.right == null) {\n'
        '                return root.left;\n'
        '            }\n'
        '            // 找后继，交换值后递归删除后继\n'
        '            TreeNode successor = root.right;\n'
        '            while (successor.left != null) {\n'
        '                successor = successor.left;\n'
        '            }\n'
        '            root.val = successor.val;\n'
        '            root.right = deleteNode(root.right, successor.val);\n'
        '        }\n'
        '\n'
        '        // AVL自平衡\n'
        '        int balance = height(root.left) - height(root.right);\n'
        '\n'
        '        // LL：左子树的左子树过高 → 右旋\n'
        '        if (balance > 1 && height(root.left.left) >= height(root.left.right)) {\n'
        '            return rotateRight(root);\n'
        '        }\n'
        '        // LR：左子树的右子树过高 → 先左旋左子，再右旋\n'
        '        if (balance > 1 && height(root.left.right) > height(root.left.left)) {\n'
        '            root.left = rotateLeft(root.left);\n'
        '            return rotateRight(root);\n'
        '        }\n'
        '        // RR：右子树的右子树过高 → 左旋\n'
        '        if (balance < -1 && height(root.right.right) >= height(root.right.left)) {\n'
        '            return rotateLeft(root);\n'
        '        }\n'
        '        // RL：右子树的左子树过高 → 先右旋右子，再左旋\n'
        '        if (balance < -1 && height(root.right.left) > height(root.right.right)) {\n'
        '            root.right = rotateRight(root.right);\n'
        '            return rotateLeft(root);\n'
        '        }\n'
        '\n'
        '        return root;\n'
        '    }\n'
        '\n'
        '    private int height(TreeNode node) {\n'
        '        if (node == null) {\n'
        '            return 0;\n'
        '        }\n'
        '        return Math.max(height(node.left), height(node.right)) + 1;\n'
        '    }\n'
        '\n'
        '    // 右旋（LL情况）：y的左子x成为新根\n'
        '    private TreeNode rotateRight(TreeNode y) {\n'
        '        TreeNode x = y.left;\n'
        '        TreeNode T2 = x.right;\n'
        '        x.right = y;\n'
        '        y.left = T2;\n'
        '        return x;\n'
        '    }\n'
        '\n'
        '    // 左旋（RR情况）：x的右子y成为新根\n'
        '    private TreeNode rotateLeft(TreeNode x) {\n'
        '        TreeNode y = x.right;\n'
        '        TreeNode T2 = y.left;\n'
        '        y.left = x;\n'
        '        x.right = T2;\n'
        '        return y;\n'
        '    }\n'
        '}\n'
    ))

add_basic(d2, make_front(p2, '关键技巧'),
    'AVL核心：height(left)-height(right) 的绝对值 ≤ 1<br>'
    '四种旋转：LL(右旋) / RR(左旋) / LR(左旋左子+右旋) / RL(右旋右子+左旋)<br>'
    '面试优化点：height() O(n) 可改为节点存高度字段 O(1)<br>'
    '旋转本质：不改变中序遍历顺序，仅调整树的高度结构')

# ═══════════════════════════════════════════════════════════════
# Build APKG
# ═══════════════════════════════════════════════════════════════
OUTPUT_DIR = Path(r'D:\claudeProjects\anki\牌组\算法')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
build(str(OUTPUT_DIR / '二叉树_删除BST节点_优化解法.apkg'))
print('Done: 二叉树_删除BST节点_优化解法.apkg')
