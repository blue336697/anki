"""Standalone: 从中序与后序遍历构造二叉树 — HashMap优化解法 单卡 APKG."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / '.claude' / 'skills' / 'anki-apkg-generator'
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, code, build

p = '从中序与后序遍历序列构造二叉树'
d = make_deck(1747300800, f'算法::二叉树::{p}::HashMap优化')

add_basic(d, make_front(p, '题干-HashMap优化'),
    '给定中序和后序遍历结果重建二叉树。<br>'
    '原解：每次递归线性查找root在中序的位置→O(n²)最坏。<br>'
    'HashMap优化：<b>预存inorder值→下标映射</b>，O(1)定位；<br>'
    '用<b>下标区间</b>代替Arrays.copyOfRange避免O(n)数组拷贝。<br>'
    '整体时间从O(n²)降至<b>O(n)</b>。')

add_cloze(d, make_front(p, 'HashMap优化-复杂度'),
    'HashMap优化后：<br>'
    '时间：{{c1::O(n)}}（每个节点构造一次，HashMap定位O(1)）<br>'
    '空间：{{c1::O(n)}}（HashMap存n个下标 + 递归栈O(h)）')

add_basic(d, make_front(p, '题解(HashMap优化)'),
    'HashMap + 下标区间，O(n)时间，无数组拷贝<br>'
    + code(
        'class Solution {\n'
        '    HashMap<Integer, Integer> memo = new HashMap<>(); // 值→中序下标\n'
        '    int[] post;\n'
        '\n'
        '    public TreeNode buildTree(int[] inorder, int[] postorder) {\n'
        '        // 预存中序序列的值→下标映射，O(1)定位根节点\n'
        '        for (int i = 0; i < inorder.length; i++)\n'
        '            memo.put(inorder[i], i);\n'
        '        post = postorder;\n'
        '        // 递归建树：传入中序区间[is, ie]和后序区间[ps, pe]\n'
        '        return buildTree(0, inorder.length - 1, 0, post.length - 1);\n'
        '    }\n'
        '\n'
        '    public TreeNode buildTree(int is, int ie, int ps, int pe) {\n'
        '        if (ie < is || pe < ps) // 区间无效，递归终止\n'
        '            return null;\n'
        '\n'
        '        int rootVal = post[pe];           // 后序末尾是根\n'
        '        int ri = memo.get(rootVal);       // HashMap O(1)定位根在中序的位置\n'
        '\n'
        '        TreeNode node = new TreeNode(rootVal);\n'
        '        int leftSize = ri - is;            // 左子树节点数量\n'
        '        // 左子树：中序[is, ri-1]，后序[ps, ps+leftSize-1]\n'
        '        node.left = buildTree(is, ri - 1, ps, ps + leftSize - 1);\n'
        '        // 右子树：中序[ri+1, ie]，后序[ps+leftSize, pe-1]\n'
        '        node.right = buildTree(ri + 1, ie, ps + leftSize, pe - 1);\n'
        '        return node;\n'
        '    }\n'
        '}\n'
    ))

add_basic(d, make_front(p, 'HashMap优化-核心要点'),
    '<b>1. 为什么要HashMap？</b><br>'
    '原解每层递归用for循环在中序数组中找root位置→O(n)，n层递归→O(n²)<br>'
    'HashMap预存inorder[i]→i映射，每次定位O(1)→整体O(n)<br><br>'
    '<b>2. 为什么要用下标区间？</b><br>'
    '原解用Arrays.copyOfRange每次复制子数组→O(n)时间+O(n)空间<br>'
    '用下标[is,ie][ps,pe]直接在原数组上操作→O(1)时间，无额外空间<br><br>'
    '<b>3. 下标计算（提取leftSize变量）：</b><br>'
    '<code>int leftSize = ri - is;</code>  // 左子树节点数量<br>'
    '左子树中序：[is, ri-1]，后序：[ps, ps+leftSize-1]<br>'
    '右子树中序：[ri+1, ie]，后序：[ps+leftSize, pe-1]<br>'
    '提取变量后区间公式一目了然，无需心算 ri-is<br><br>'
    '<b>4. 对比记忆：</b><br>'
    '前序+中序建树：前序<b>开头</b>是根，HashMap同样适用<br>'
    '后序+中序建树：后序<b>末尾</b>是根，其余逻辑完全对称')

OUTPUT = REPO_ROOT / '牌组' / '算法' / '从中序后序构造二叉树_HashMap优化.apkg'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
result = build(str(OUTPUT))
print(result)
print(f'输出: {OUTPUT}')
