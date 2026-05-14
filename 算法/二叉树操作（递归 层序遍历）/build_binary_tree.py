"""Build APKG for 二叉树 (Binary Tree). 50 problems, full-code Java solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# ═══════════════════════════════════════════════════════════════
# Principles Deck
# ═══════════════════════════════════════════════════════════════
pd = make_deck(1747300600, '算法::二叉树::原理通识')
add_basic(pd, '二叉树遍历框架',
    '前序：根→左→右 | 中序：左→根→右 | 后序：左→右→根<br>'
    '层序：BFS队列，每层size控制<br>'
    '递归三部曲：终止条件→处理当前层→递归子树')
add_cloze(pd, '二叉树递归与迭代',
    '递归：隐式使用系统栈，代码简洁<br>'
    '迭代：显式使用{{c1::Stack}}模拟递归<br>'
    '层序遍历：使用{{c2::Queue}}，for循环按层处理<br>'
    'Morris遍历：{{c3::O(1)}}空间，利用叶子节点空闲指针')
add_basic(pd, '二叉树常用技巧',
    '递归三部曲：1.终止条件 2.处理逻辑 3.递归左右子树<br>'
    '自顶向下：传递状态参数（如前缀和、深度）<br>'
    '自底向上：汇总子树结果返回<br>'
    '双递归：主递归遍历节点+辅助递归计算当前节点<br>'
    'BFS层序：队列+每层size遍历')

# ════════════════════════════════════════════════════════════
# Problem 1: 二叉树的层序遍历
# ════════════════════════════════════════════════════════════
p = '二叉树的层序遍历'
d = make_deck(1747300601, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    'BFS')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的层序遍历的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    'BFS<br>'
    + code(
            'class Solution {\n'
            '    public List&lt;List&lt;Integer&gt;&gt; levelOrder(TreeNode root) {\n'
            '        List&lt;List&lt;Integer&gt;&gt; returnList = new ArrayList&lt;&gt;();\n'
            '        if(root==null)\n'
            '            return returnList;\n'
            '        TreeNode temp;\n'
            '        Deque&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        queue.add(root);    //根结点入队\n'
            '        while(queue.size()!=0){\n'
            '            List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '            int size = queue.size();\n'
            '            for(int i = 0; i &lt; size; i++){\n'
            '                temp = queue.poll();\n'
            '                list.add(temp.val);\n'
            '                if(temp.left != null)\n'
            '                    queue.add(temp.left);\n'
            '                if(temp.right != null)\n'
            '                    queue.add(temp.right);   \n'
            '            }\n'
            '            returnList.add(list);\n'
            '\n'
            '        }\n'
            '        return returnList;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的层序遍历的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 2: 二叉树的层次遍历 II
# ════════════════════════════════════════════════════════════
p = '二叉树的层次遍历 II'
d = make_deck(1747300602, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '没啥好说的层次遍历就完事了')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的层次遍历 II的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '没啥好说的层次遍历就完事了<br>'
    + code(
            'public class Solution {\n'
            '    public List&lt;List&lt;Integer&gt;&gt; levelOrderBottom(TreeNode root) {\n'
            '        List&lt;List&lt;Integer&gt;&gt; ans = new LinkedList&lt;&gt;();\n'
            '        if (root == null)\n'
            '            return ans;\n'
            '        //设置队列\n'
            '        Queue&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        //根结点入队\n'
            '        queue.offer(root);\n'
            '        while (!queue.isEmpty()) {\n'
            '            int len = queue.size();\n'
            '            List&lt;Integer&gt; tempList = new LinkedList&lt;&gt;();\n'
            '            //广度优先遍历，以队列的长度为次数将本层的所有结点全部入队\n'
            '            for (int i = 0; i &lt; len; i++) {\n'
            '                TreeNode node = queue.poll();\n'
            '                tempList.add(node.val);\n'
            '                if (node.left != null)\n'
            '                    queue.offer(node.left);\n'
            '                if (node.right != null)\n'
            '                    queue.offer(node.right);\n'
            '            }\n'
            '            //ans.add(tempList);\n'
            '            ans.add(0, tempList); //这里写成这样就不要最后反转了，改为头插\n'
            '        }\n'
            '        //Collections.reverse(ans);\n'
            '        return ans;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的层次遍历 II的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 3: 二叉树的锯齿形层次遍历
# ════════════════════════════════════════════════════════════
p = '二叉树的锯齿形层次遍历'
d = make_deck(1747300603, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '这道题的思路就是顺序遍历每层的结点，设置一个标志位，每循环遍历一层就将标志位取反，判断是否进行反转，也就是说每隔一层进行一次反转')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的锯齿形层次遍历的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '这道题的思路就是顺序遍历每层的结点，设置一个标志位，每循环遍历一层就将标志位取反，判断是否进行反转，也就是说每隔一层进行一次反转<br>'
    + code(
            'public class Solution {\n'
            '    public List&lt;List&lt;Integer&gt;&gt; zigzagLevelOrder(TreeNode root) {\n'
            '        List&lt;List&lt;Integer&gt;&gt; ans = new LinkedList&lt;&gt;();\n'
            '        if (root == null)\n'
            '            return ans;\n'
            '        //设置队列\n'
            '        Queue&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        //设置标志位\n'
            '        boolean reverse = false;\n'
            '        //根结点入队\n'
            '        queue.offer(root);\n'
            '        while (!queue.isEmpty()) {\n'
            '            int len = queue.size();\n'
            '            List&lt;Integer&gt; tempList = new LinkedList&lt;&gt;();\n'
            '            //广度优先遍历，以队列的长度为次数将本层的所有结点全部入队\n'
            '            for (int i = 0; i &lt; len; i++) {\n'
            '                TreeNode node = queue.poll();\n'
            '                tempList.add(node.val);\n'
            '                if (node.left != null)\n'
            '                    queue.offer(node.left);\n'
            '                if (node.right != null)\n'
            '                    queue.offer(node.right);\n'
            '            }\n'
            '            //标志位判断，每隔一层进行反转\n'
            '            if (reverse) {\n'
            '                Collections.reverse(tempList);\n'
            '            }\n'
            '            reverse = !reverse;\n'
            '            ans.add(tempList);\n'
            '        }\n'
            '        return ans;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的锯齿形层次遍历的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 4: 从上到下打印二叉树 II
# ════════════════════════════════════════════════════════════
p = '从上到下打印二叉树 II'
d = make_deck(1747300604, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：从上到下打印二叉树 II。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述从上到下打印二叉树 II的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    List&lt;List&lt;Integer&gt;&gt; list = new ArrayList&lt;&gt;();\n'
            '    Queue&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '    public List&lt;List&lt;Integer&gt;&gt; levelOrder(TreeNode root) {\n'
            '        //levelTraversal(0, root);\n'
            '        levelTraversal(root);\n'
            '        return list;\n'
            '    }\n'
            '\n'
            '    //递归\n'
            '    public void levelTraversal(int depth, TreeNode node){\n'
            '        //list.add(new ArrayList&lt;Integer&gt;().add(node.val));\n'
            '        if(node == null)\n'
            '            return;\n'
            '        if(depth == list.size()){\n'
            '            list.add(new ArrayList&lt;&gt;());\n'
            '        }\n'
            '        //这句代码就是分层的关键，将层数和大list大索引相关联\n'
            '        list.get(depth).add(node.val);\n'
            '        levelTraversal(depth + 1, node.left);\n'
            '        levelTraversal(depth + 1, node.right);\n'
            '\n'
            '    }\n'
            '\n'
            '    //非递归方法\n'
            '    public void levelTraversal(TreeNode root){\n'
            '        if(root != null)\n'
            '            queue.add(root);\n'
            '        while(!queue.isEmpty()){\n'
            '            List&lt;Integer&gt; temp = new ArrayList&lt;&gt;();\n'
            '            //这句就是分层的关键，以队列中的节点数为分层的区别，例如第一次进入这个方法时队列初始化完成以后的长度是1，那么就为根结点的层数，当进入第二次循环的时候根结点出列的他的左孩子和右孩子进入队列，长度变为2即为第二层，如果第二层的两个结点都有左右孩子那么队列会进入四个结点，长度变为4即为第三层\n'
            '            for(int i = queue.size();i&gt;0;i--){\n'
            '                TreeNode node = queue.poll();\n'
            '                temp.add(node.val);\n'
            '                if(node.left != null)\n'
            '                    queue.add(node.left);\n'
            '                if(node.right != null)\n'
            '                    queue.add(node.right);\n'
            '\n'
            '            }\n'
            '            list.add(temp);\n'
            '        }\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结从上到下打印二叉树 II的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 5: 从上到下打印二叉树 III
# ════════════════════════════════════════════════════════════
p = '从上到下打印二叉树 III'
d = make_deck(1747300605, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '跟【二叉树的锯齿形层次遍历】一个样子，设置标志位')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述从上到下打印二叉树 III的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '跟【二叉树的锯齿形层次遍历】一个样子，设置标志位<br>'
    + code(
            'class Solution {\n'
            '    public List&lt;List&lt;Integer&gt;&gt; levelOrder(TreeNode root) {\n'
            '        List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
            '        if(root == null)\n'
            '            return res;\n'
            '        List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '        Queue&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        queue.add(root);\n'
            '        //由于我们需要Z形遍历，其实就是跟103题一样，设置一个反转标志位即可\n'
            '        boolean reverse = false;    //默认第一层不反转\n'
            '        while(!queue.isEmpty()){\n'
            '            int len = queue.size();\n'
            '            //我们每次需要在一个while循环中处理完一层，那么需要嵌套for循环来\n'
            '            for(int i = 0; i &lt; len; i++){\n'
            '                TreeNode temp = queue.poll();\n'
            '                list.add(temp.val);\n'
            '                if(temp.left != null)\n'
            '                    queue.add(temp.left);\n'
            '                if(temp.right != null)\n'
            '                    queue.add(temp.right);\n'
            '            }\n'
            '            if(reverse)\n'
            '                Collections.reverse(list);\n'
            '            reverse = !reverse;\n'
            '            res.add(new ArrayList&lt;&gt;(list));\n'
            '            list.clear();\n'
            '        }\n'
            '        return res;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结从上到下打印二叉树 III的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 6: 二叉树的右视图
# ════════════════════════════════════════════════════════════
p = '二叉树的右视图'
d = make_deck(1747300606, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '两种方式：DFS和BFS<br>DFS:<br>BFS:' + img('image.png') + img('image 1.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的右视图的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '两种方式：DFS和BFS<br>DFS:<br>BFS:<br>'
    + code(
            'class Solution {\n'
            '    //站在右侧向左看，如果是[1,3]那么返回的也是[1,3]，因为站在有吃的看3的时候右子树是没有任何结点的，即使3是左子树的结点\n'
            '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '    public List&lt;Integer&gt; rightSideView(TreeNode root) {\n'
            '        dfs(root, 0);\n'
            '        return list;\n'
            '    }\n'
            '\n'
            '    public void dfs(TreeNode root, int depth){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        // 先访问 当前节点，再递归地访问 右子树 和 左子树。\n'
            '\n'
            '        // 如果当前节点所在深度还没有出现在res里，说明在该深度下当前节点是第一个被访问的节点，因此将当前节点加入res中。\n'
            '        if(depth == list.size())\n'
            '            list.add(root.val);\n'
            '\n'
            '        depth++;\n'
            '        dfs(root.right, depth);\n'
            '        dfs(root.left, depth);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的右视图的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    public List&lt;Integer&gt; rightSideView(TreeNode root) {\n'
            '        List&lt;Integer&gt; res = new ArrayList&lt;&gt;();\n'
            '        if (root == null) {\n'
            '            return res;\n'
            '        }\n'
            '        Queue&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        queue.offer(root);\n'
            '        while (!queue.isEmpty()) {\n'
            '            int size = queue.size();\n'
            '            for (int i = 0; i &lt; size; i++) {\n'
            '                TreeNode node = queue.poll();\n'
            '                if (node.left != null) {\n'
            '                    queue.offer(node.left);\n'
            '                }\n'
            '                if (node.right != null) {\n'
            '                    queue.offer(node.right);\n'
            '                }\n'
            '                if (i == size - 1) {  //将当前层的最后一个节点放入结果列表\n'
            '                    res.add(node.val);\n'
            '                }\n'
            '            }\n'
            '        }\n'
            '        return res;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 7: 二叉树的前序遍历
# ════════════════════════════════════════════════════════════
p = '二叉树的前序遍历'
d = make_deck(1747300607, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树的前序遍历。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的前序遍历的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '\n'
            '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '    public List&lt;Integer&gt; preorderTraversal(TreeNode root) {\n'
            '        inOrder(root);\n'
            '        return list;\n'
            '    }\n'
            '\n'
            '    //先根，在左，在右\n'
            '    public void inOrder(TreeNode root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        list.add(root.val);\n'
            '        if(root.left!=null)\n'
            '            inOrder(root.left);\n'
            '\n'
            '        if(root.right!=null)\n'
            '            inOrder(root.right);\n'
            '\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的前序遍历的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 8: 二叉树的中序遍历
# ════════════════════════════════════════════════════════════
p = '二叉树的中序遍历'
d = make_deck(1747300608, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树的中序遍历。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的中序遍历的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            '\n'
            'class Solution {\n'
            '//先左，在根，在右\n'
            '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '    public List&lt;Integer&gt; inorderTraversal(TreeNode root) {\n'
            '        inOrder(root);\n'
            '        return list;\n'
            '    }\n'
            '\n'
            '    public void inOrder(TreeNode root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        if(root.left!=null)\n'
            '            inOrder(root.left);\n'
            '        list.add(root.val);\n'
            '        if(root.right!=null)\n'
            '            inOrder(root.right);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的中序遍历的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 9: 二叉树的后序遍历
# ════════════════════════════════════════════════════════════
p = '二叉树的后序遍历'
d = make_deck(1747300609, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树的后序遍历。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的后序遍历的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '    public List&lt;Integer&gt; postorderTraversal(TreeNode root) {\n'
            '        inOrder(root);\n'
            '        return list;\n'
            '    }\n'
            '\n'
            '    //先左，后右，在根\n'
            '    public void inOrder(TreeNode root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        if(root.left != null)\n'
            '            inOrder(root.left);\n'
            '        if(root.right != null)\n'
            '            inOrder(root.right);\n'
            '        list.add(root.val);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的后序遍历的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 10: 二叉树的最大深度
# ════════════════════════════════════════════════════════════
p = '二叉树的最大深度'
d = make_deck(1747300610, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    'BFS<br>DFS')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的最大深度的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    'BFS<br>DFS<br>'
    + code(
            'class Solution {\n'
            '    public int maxDepth(TreeNode root) {\n'
            '        List&lt;List&lt;Integer&gt;&gt; list = getDepth(root);\n'
            '        return list.size();\n'
            '    }\n'
            '\n'
            '    public List&lt;List&lt;Integer&gt;&gt; getDepth(TreeNode root){\n'
            '        List&lt;List&lt;Integer&gt;&gt; returnList = new ArrayList&lt;&gt;();\n'
            '        if(root==null)\n'
            '            return returnList;\n'
            '        TreeNode p;\n'
            '        Deque&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        queue.add(root);    //根结点入队\n'
            '        while(queue.size()!=0){\n'
            '            List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '            int size = queue.size();\n'
            '            for(int i=0;i&lt;size;i++){\n'
            '                p = queue.poll();\n'
            '                list.add(p.val);\n'
            '                if(p.left!=null)\n'
            '                    queue.add(p.left);\n'
            '                if(p.right!=null)\n'
            '                    queue.add(p.right);   \n'
            '            }\n'
            '            returnList.add(list);\n'
            '\n'
            '        }\n'
            '        return returnList;\n'
            '    }\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的最大深度的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'public int maxDepth(TreeNode root) {\n'
            '        if (root == null) {\n'
            '            return 0;\n'
            '        } else {\n'
            '            int leftHeight = maxDepth(root.left);\n'
            '            int rightHeight = maxDepth(root.right);\n'
            '            return Math.max(leftHeight, rightHeight) + 1;\n'
            '        }\n'
            '    }  \n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 11: 二叉树的最小深度
# ════════════════════════════════════════════════════════════
p = '二叉树的最小深度'
d = make_deck(1747300611, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    'DFS<br>BFS')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的最小深度的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    'DFS<br>BFS<br>'
    + code(
            'class Solution {\n'
            '    //1.递归条件（就是会出现的各种情况）\n'
            '    //2.只在意本层的逻辑\n'
            '    //3.需要返回什么，（根据条件你需要返回什么）\n'
            '    /*叶子节点的定义是左孩子和右孩子都为 null 时叫做叶子节点\n'
            '    当 root 节点左右孩子都为空时，返回 1\n'
            '    当 root 节点左右孩子有一个为空时，返回不为空的孩子节点的深度\n'
            '    当 root 节点左右孩子都不为空时，返回左右孩子较小深度的节点值\n'
            '    */\n'
            '    public int minDepth(TreeNode root) {\n'
            '        //根节点位0，树为空\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        //左右子树都为空，返回自身的长度\n'
            '        if(root.left == null &amp;&amp; root.right == null)\n'
            '            return 1;\n'
            '        //当左子树为空，返回右子树+自身的长度\n'
            '        if(root.left == null)\n'
            '            return minDepth(root.right) + 1;\n'
            '        //与上面同理\n'
            '        if(root.right == null)\n'
            '            return minDepth(root.left) + 1;\n'
            '        //左右子树都不为空，那就看谁小\n'
            '        return Math.min(minDepth(root.left), minDepth(root.right)) + 1;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的最小深度的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    public int minDepth(TreeNode root) {\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        Queue&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        queue.add(root);\n'
            '        int res = 1;    //如果根节点不为空那么初始树高就是1\n'
            '        while(!queue.isEmpty()){\n'
            '            int len = queue.size();\n'
            '            //这里加个for循环的原因就是遍历本层节点，如果本层的任意节点出现了\n'
            '            //没有左右子树的情况则立即返回\n'
            '            //你不遍历本层节点，直接在while中操作res，会出现你先写的左边还是右边\n'
            '            //加入队列，那就按谁的来\n'
            '            for(int i = 0; i &lt; len; i++){\n'
            '                TreeNode temp = queue.poll();\n'
            '                if(temp.left == null &amp;&amp; temp.right == null)\n'
            '                    return res;    \n'
            '                if(temp.left != null)\n'
            '                    queue.add(temp.left);\n'
            '                if(temp.right != null)\n'
            '                    queue.add(temp.right);\n'
            '            }\n'
            '            res++;//都没有上面所说的那个情况出现，树深加1\n'
            '        }\n'
            '        return res;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 12: 二叉树最大宽度
# ════════════════════════════════════════════════════════════
p = '二叉树最大宽度'
d = make_deck(1747300612, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树最大宽度。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树最大宽度的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            '/**\n'
            '  * 二叉树的最大宽度\n'
            '  * 优先队列，进行层序遍历，记录每个节点在满二叉树中的序号\n'
            '  * 在满二叉树中，当前节点的序号为k，\n'
            '  * 那么其左孩子和右孩子的序号分别为2k、2k+1\n'
            '  */\n'
            'class Solution {\n'
            '    public int widthOfBinaryTree(TreeNode root) {\n'
            '        Deque&lt;Node&gt; pq = new LinkedList&lt;&gt;();\n'
            '        //将根节点放入\n'
            '        pq.offer(new Node(root, 1));\n'
            '        long ans = 0;\n'
            '        //while循环过每一层\n'
            '        while (!pq.isEmpty()) {\n'
            '            int size = pq.size();\n'
            '            // 注意：right可能会越界，这里使用long\n'
            '            long left = pq.peek().index, right = pq.peek().index; \n'
            '            //每轮for循环就是对当前层的每个节点的标记  \n'
            '            for (int k = 0; k &lt; size; k++) {\n'
            '                Node node = pq.poll();\n'
            '                //左边界\n'
            '                left = Math.min(left, node.index);\n'
            '                //右边界\n'
            '                right = Math.max(right, node.index);\n'
            '                ans = Math.max(ans, right - left + 1);\n'
            '                if (node.treeNode.left != null) pq.offer(new Node(node.treeNode.left, 2 * node.index));\n'
            '                if (node.treeNode.right != null) pq.offer(new Node(node.treeNode.right, 2 * node.index + 1));\n'
            '            }\n'
            '        }\n'
            '        return (int) ans;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树最大宽度的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 13: 二叉树的直径
# ════════════════════════════════════════════════════════════
p = '二叉树的直径'
d = make_deck(1747300613, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树的直径。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的直径的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    int ans;\n'
            '    public int diameterOfBinaryTree(TreeNode root) {\n'
            '        ans = 1;\n'
            '        depth(root);\n'
            '        return ans - 1;\n'
            '    }\n'
            '    public int depth(TreeNode node) {\n'
            '        if (node == null) {\n'
            '            return 0; // 访问到空节点了，返回0\n'
            '        }\n'
            '        int L = depth(node.left); // 左儿子为根的子树的深度\n'
            '        int R = depth(node.right); // 右儿子为根的子树的深度\n'
            '        ans = Math.max(ans, L+R+1); // 计算d_node即L+R+1 并更新ans\n'
            '        return Math.max(L, R) + 1; // 返回该节点为根的子树的深度\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的直径的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 14: 对称二叉树
# ════════════════════════════════════════════════════════════
p = '对称二叉树'
d = make_deck(1747300614, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '使用dfs的方式<br>使用队列的方式' + img('image 2.png') + img('image 3.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述对称二叉树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '使用dfs的方式<br>使用队列的方式<br>'
    + code(
            'public boolean isSymmetric(TreeNode root) {\n'
            '        if(root == null)\n'
            '            return true;\n'
            '        //递归入口\n'
            '        return dfs(root.left, root.right);\n'
            '    }\n'
            '\n'
            '    public boolean dfs(TreeNode left, TreeNode right){\n'
            '        //递归出口\n'
            '        if(left == null &amp;&amp; right == null)\n'
            '            return true;\n'
            '        //递归出口\n'
            '        if(left == null || right == null)\n'
            '            return false;\n'
            '        //递归出口\n'
            '        if(left.val != right.val)\n'
            '            return false;\n'
            '\n'
            '        //左树的左孩子跟右树的右孩子比较，左树的右孩子跟右树的左孩子比较\n'
            '        return dfs(left.left, right.right) &amp;&amp; dfs(left.right, right.left);\n'
            '    }\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结对称二叉树的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    public boolean isSymmetric(TreeNode root) {\n'
            '        if(root==null || (root.left==null &amp;&amp; root.right==null)) {\n'
            '            return true;\n'
            '        }\n'
            '        //用队列保存节点\n'
            '        LinkedList&lt;TreeNode&gt; queue = new LinkedList&lt;TreeNode&gt;();\n'
            '        //将根节点的左右孩子放到队列中\n'
            '        queue.add(root.left);\n'
            '        queue.add(root.right);\n'
            '        while(queue.size()&gt;0) {\n'
            '            //从队列中取出两个节点，再比较这两个节点\n'
            '            TreeNode left = queue.removeFirst();\n'
            '            TreeNode right = queue.removeFirst();\n'
            '            //如果两个节点都为空就继续循环，两者有一个为空就返回false\n'
            '            if(left==null &amp;&amp; right==null) {\n'
            '                continue;\n'
            '            }\n'
            '            if(left==null || right==null) {\n'
            '                return false;\n'
            '            }\n'
            '            if(left.val!=right.val) {\n'
            '                return false;\n'
            '            }\n'
            '            //将左节点的左孩子， 右节点的右孩子放入队列\n'
            '            queue.add(left.left);\n'
            '            queue.add(right.right);\n'
            '            //将左节点的右孩子，右节点的左孩子放入队列\n'
            '            queue.add(left.right);\n'
            '            queue.add(right.left);\n'
            '        }\n'
            '\n'
            '        return true;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 15: 相同的树
# ════════════════════════════════════════════════════════════
p = '相同的树'
d = make_deck(1747300615, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：相同的树。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述相同的树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '\n'
            '    boolean isSameTree(TreeNode root1, TreeNode root2) {\n'
            '    // 都为空的话，显然相同\n'
            '    if (root1 == null &amp;&amp; root2 == null) return true;\n'
            '    // 一个为空，一个非空，显然不同\n'
            '    if (root1 == null || root2 == null) return false;\n'
            '    // 两个都非空，但 val 不一样也不行\n'
            '    if (root1.val != root2.val) return false;\n'
            '\n'
            '    // root1 和 root2 该比的都比完了\n'
            '    return isSameTree(root1.left, root2.left)\n'
            '        &amp;&amp; isSameTree(root1.right, root2.right);\n'
            '	}\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结相同的树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 16: 平衡二叉树
# ════════════════════════════════════════════════════════════
p = '平衡二叉树'
d = make_deck(1747300616, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：平衡二叉树。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述平衡二叉树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    public boolean isBalanced(TreeNode root) {\n'
            '        //如果最后返回的个非负则是一颗平衡二叉树\n'
            '        return depth(TreeNode root) != -1;\n'
            '\n'
            '    }\n'
            '\n'
            '    //自底向上，可以避免很多重复的递归，本质上是一个先序遍历\n'
            '    public int depth(TreeNode root){\n'
            '        //根结点为空则返回0\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        //将左边子树的深度记录\n'
            '        int i = depth(root.left);\n'
            '        //不满足是平衡二叉树，则返回-1\n'
            '        if(i == -1)\n'
            '            return -1;\n'
            '        //与上面同理\n'
            '        int j = depth(root.right);\n'
            '        if(j == -1)\n'
            '            return -1;\n'
            '\n'
            '        return Math.abs(i - j) &lt; 2 ? Math.max(i, j) : -1; \n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结平衡二叉树的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            '//自顶向下，也就是暴力解法，分为两个递归：判断该树是否为平衡二叉树\n'
            '//另一个记录二叉树的树深\n'
            'class Solution {\n'
            '    public boolean isBalanced(TreeNode root) {\n'
            '        if(root == null)\n'
            '            return true;\n'
            '        return Math.abs(depth(root.left) - depth(root.right)) &lt;= 1 &amp;&amp; isBalanced(root.left) &amp;&amp; isBalanced(root.right);\n'
            '    }\n'
            '\n'
            '    public int depth(TreeNode root){\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        return Math.max(depth(root.left), depth(root.right)) + 1;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 17: 二叉树的最近公共祖先
# ════════════════════════════════════════════════════════════
p = '二叉树的最近公共祖先'
d = make_deck(1747300617, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树的最近公共祖先。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的最近公共祖先的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n'
            '        //开始先序遍历 先根，在左，在右\n'
            '        //根据题意，当p，q某一个是root时，该点就是最近公共祖先\n'
            '        if(root == null || root == p || root == q)\n'
            '            return root;\n'
            '\n'
            '        TreeNode left = lowestCommonAncestor(root.left, p, q);\n'
            '        TreeNode right = lowestCommonAncestor(root.right, p, q);\n'
            '        //第一种情况：当一直遍历到最后一层，未遍历到p和q，则公共祖先为root\n'
            '        if(left == null &amp;&amp; right == null)\n'
            '            return null;\n'
            '        //第二种情况：遍历到右子树有q，左子树的p可能在右子树，\n'
            '        if(left == null)\n'
            '            return right;\n'
            '        //第三种情况：与第二种相反\n'
            '        if(right == null)\n'
            '            return left;\n'
            '\n'
            '        //此时其实p和q分别在左右子树都已经找到了，有一个隐含条件\n'
            '        //if(left != null and right != null)\n'
            '        return root;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的最近公共祖先的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 18: 二叉搜索树的最近公共祖先
# ════════════════════════════════════════════════════════════
p = '二叉搜索树的最近公共祖先'
d = make_deck(1747300618, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉搜索树的最近公共祖先。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉搜索树的最近公共祖先的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n'
            '        if(root == null)\n'
            '            return null;\n'
            '        //这里些许有点问题，直接一个while循环跳出来返回root就行了，没必要判断这两个结点是否分别为根结点左子树和右子树上的结点\n'
            '        if((p.val &gt; root.val &amp;&amp; q.val &lt; root.val) || (q.val &gt; root.val &amp;&amp; p.val &lt; root.val)){\n'
            '            return root;\n'
            '        }else if(p.val &gt; root.val &amp;&amp; q.val &gt; root.val){\n'
            '\n'
            '        }else if(p.val &lt; root.val &amp;&amp; q.val &lt; root.val){\n'
            '\n'
            '        }\n'
            '    }\n'
            '}\n'
            '\n'
            'class Solution {\n'
            '    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n'
            '        while(root != null) {\n'
            '            if(root.val &lt; p.val &amp;&amp; root.val &lt; q.val) // p,q 都在 root 的右子树中\n'
            '                root = root.right; // 遍历至右子节点\n'
            '            //一直判断，直到不满足这个条件这个公共最近的祖先结点\n'
            '            else if(root.val &gt; p.val &amp;&amp; root.val &gt; q.val) // p,q 都在 root 的左子树中\n'
            '                root = root.left; // 遍历至左子节点\n'
            '            else break;\n'
            '        }\n'
            '        //如果上面的两个判断都不满足那自然而然这两个结点就是分别居于左子树和右子树上面\n'
            '        return root;\n'
            '    }\n'
            '    \n'
            '\n'
            '    //采用递归的方法\n'
            '    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n'
            '        if(root == null)\n'
            '            return null;\n'
            '        //如果全在左子树\n'
            '        if(root.val &lt; p.val &amp;&amp; root.val &lt; q.val)\n'
            '            return lowestCommonAncestor(root.right, p, q);\n'
            '        if(root.val &gt; p.val &amp;&amp; root.val &gt; q.val)\n'
            '            return lowestCommonAncestor(root.left, p, q); \n'
            '\n'
            '        return root;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉搜索树的最近公共祖先的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 19: 二叉搜索树的第k大节点
# ════════════════════════════════════════════════════════════
p = '二叉搜索树的第k大节点'
d = make_deck(1747300619, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉搜索树的第k大节点。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉搜索树的第k大节点的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            '\n'
            'class Solution {\n'
            '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '    public int kthLargest(TreeNode root, int k) {\n'
            '        inOrder(root);\n'
            '        return list.get(list.size() - k);\n'
            '    }\n'
            '\n'
            '    public void inOrder(TreeNode root){\n'
            '        if(root.left != null)\n'
            '            inOrder(root.left);\n'
            '        list.add(root.val);\n'
            '        if(root.right != null)\n'
            '            inOrder(root.right);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉搜索树的第k大节点的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 20: 二叉搜索树中第K小的元素
# ════════════════════════════════════════════════════════════
p = '二叉搜索树中第K小的元素'
d = make_deck(1747300620, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '利用大根堆（优先队列），但是时间复杂度并不算优秀<br>使用API的排序，这个仅作为观赏，面试写出来直接say goodbye<br>利用二叉搜索树的特性直接中序遍历，省去了排序的过程，时间复杂度最优' + img('image 8.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉搜索树中第K小的元素的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '利用大根堆（优先队列），但是时间复杂度并不算优秀<br>使用API的排序，这个仅作为观赏，面试写出来直接say goodbye<br>利用二叉搜索树的特性直接中序遍历，省去了排序的过程，时间复杂度最优<br>'
    + code(
            '	public int kthSmallest(TreeNode root, int k) {\n'
            '        //这里就是使用权重的队列来模拟大根堆的创建过程\n'
            '        //重写里面的compareTo方法使之降序排列，与树的层次遍历结合，一层一层的检查大根堆\n'
            '        PriorityQueue&lt;Integer&gt; q = new PriorityQueue&lt;&gt;((a,b)-&gt;b-a);\n'
            '        Deque&lt;TreeNode&gt; d = new ArrayDeque&lt;&gt;();\n'
            '        d.addLast(root);\n'
            '        while (!d.isEmpty()) {\n'
            '            TreeNode node = d.pollFirst();\n'
            '            //如果此时大根堆的长度还不足k，那么就证明还未建立完成，继续增加新的节点\n'
            '            //即建立一个容量为k的堆\n'
            '            if (q.size() &lt; k) {\n'
            '                q.add(node.val);\n'
            '                //如果大根堆满了则要比较当前节点值，跟队列中的值\n'
            '                //如果队首的值大于当前节点值\n'
            '            } else if (q.peek() &gt; node.val) {\n'
            '                //当进行出队操作后，剩余的元素来进行大根堆的重构，时刻保证了大根堆\n'
            '                //对容量为k的大根堆，我们时刻保证个规则，大的出，当全部遍历完\n'
            '                //剩余的刚好就是我们需要的\n'
            '                q.poll();   //将根节点出队\n'
            '                q.add(node.val);\n'
            '            }\n'
            '\n'
            '            //也就是说上面的全部操作，就是在优化k个范围内的大根堆，我们找第k个最小的元素\n'
            '            //那在大根堆中就是k个容量的根节点就是所求的值\n'
            '\n'
            '            if (node.left != null) d.addLast(node.left);\n'
            '            if (node.right != null) d.addLast(node.right);\n'
            '        }\n'
            '        return q.peek();\n'
            '    }\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉搜索树中第K小的元素的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '    //利用二叉搜索树的特效，二叉搜索树的中序遍历就是排好序的\n'
            '    public int kthSmallest(TreeNode root, int k) {\n'
            '        inOrder(root);\n'
            '        return list.get(k - 1);\n'
            '    }\n'
            '\n'
            '    public void inOrder(TreeNode root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        inOrder(root.left);\n'
            '        list.add(root.val);\n'
            '        inOrder(root.right);\n'
            '    }\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 21: 将二叉搜索树转化为排序的双向链表
# ════════════════════════════════════════════════════════════
p = '将二叉搜索树转化为排序的双向链表'
d = make_deck(1747300621, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：将二叉搜索树转化为排序的双向链表。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述将二叉搜索树转化为排序的双向链表的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            '//约定左子树就是前序，右子树就是后序节点\n'
            'class Solution {\n'
            '    //pre节点代表当前节点的父节点，全部递归结束指向最后一个节点\n'
            '    Node pre, head;\n'
            '    public Node treeToDoublyList(Node root) {\n'
            '        if(root == null)\n'
            '            return null;\n'
            '        dfs(root);\n'
            '        pre.right = head;\n'
            '        head.left = pre;\n'
            '        return head;\n'
            '    }\n'
            '\n'
            '    public void dfs(Node root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        dfs(root.left);\n'
            '        if(pre != null)\n'
            '            pre.right = root;\n'
            '        else    //如果为空说明是头节点，最小的节点，遍历到了最底层\n'
            '            head = root;\n'
            '        root.left = pre;\n'
            '        //保存当前节点，就是下一个节点的父节点\n'
            '        pre = root;\n'
            '        dfs(root.right);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结将二叉搜索树转化为排序的双向链表的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 22: 二叉搜索树与双向链表
# ════════════════════════════════════════════════════════════
p = '二叉搜索树与双向链表'
d = make_deck(1747300622, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '我们用两个队列，一个正序一个反序，先正序出队连接left，后反序出队连接right<br>利用中序遍历一边遍历一边连接')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉搜索树与双向链表的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '我们用两个队列，一个正序一个反序，先正序出队连接left，后反序出队连接right<br>利用中序遍历一边遍历一边连接<br>'
    + code(
            'class Solution {\n'
            '\n'
            '    Deque&lt;Node&gt; queue01 = new ArrayDeque&lt;&gt;();\n'
            '    Deque&lt;Node&gt; queue02 = new ArrayDeque&lt;&gt;();\n'
            '    public Node treeToDoublyList(Node root) {\n'
            '        inOrder(root);\n'
            '        while(!queue01.isEmpty()){\n'
            '            Node temp = queue01.poll();\n'
            '            //当为空的时候，就要将最后一个结点指向第一个结点\n'
            '            if(queue01.isEmpty())\n'
            '                temp.left = queue02.peekLast();\n'
            '            else\n'
            '                temp.left = queue01.peek();\n'
            '            queue02.addFirst(temp);\n'
            '        }\n'
            '        Node tail = queue02.peek();\n'
            '        Node head = queue02.peekLast();\n'
            '        while(!queue02.isEmpty()){\n'
            '            Node temp = queue02.poll();\n'
            '            if(queue02.isEmpty())\n'
            '                temp.right = tail;\n'
            '            else\n'
            '                temp.right = queue02.peek();\n'
            '        }\n'
            '\n'
            '        return head;\n'
            '    }\n'
            '\n'
            '    public void inOrder(Node root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        treeToDoublyList(root.left);\n'
            '        queue01.add(root);\n'
            '        treeToDoublyList(root.right);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉搜索树与双向链表的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {    \n'
            '    Node pre, head;\n'
            '    public Node treeToDoublyList(Node root) {\n'
            '        if(root == null) return null;\n'
            '        inOrder(root);\n'
            '        //然后将head的前继节点设置成尾\n'
            '        head.left = pre;\n'
            '        //将尾的后继节点指向头\n'
            '        pre.right = head;\n'
            '        return head;\n'
            '    }\n'
            '\n'
            '    //利用中序遍历，一边遍历一边连接\n'
            '    public void inOrder(Node cur) {\n'
            '        if(cur == null) return;\n'
            '        dfs(cur.left);\n'
            '        //如果pre节点不为空，证明当前节点不是头节点，则把pre节点的后继\n'
            '        //节点指向当前节点\n'
            '        if(pre != null) \n'
            '            pre.right = cur;\n'
            '        //为空就说明是头结点，那么就把cur赋值给head\n'
            '        else \n'
            '            head = cur;\n'
            '        //然后当前前继结点设置为pre，当cur是头结点时，pre是null\n'
            '        //也就是说整个中序遍历后我们应该将头跟尾连接\n'
            '        cur.left = pre;\n'
            '        //然后把pre设置成cur，即向前递归，处理下一个结点\n'
            '        pre = cur;\n'
            '        dfs(cur.right);\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 23: 二叉搜索树的后序遍历序列
# ════════════════════════════════════════════════════════════
p = '二叉搜索树的后序遍历序列'
d = make_deck(1747300623, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '递归，就是利用后序遍历的序列性质<br>模拟构造一个二叉搜索树')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉搜索树的后序遍历序列的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '递归，就是利用后序遍历的序列性质<br>模拟构造一个二叉搜索树<br>'
    + code(
            'class Solution {\n'
            '    //后序遍历的规律是先左 后右 在根，那么对于后序的序列来说，最后一个值就是根节点\n'
            '    //然后我们遍历数组直到遇到比根节点的值大的，标记为m，哪就是根节点的右子树\n'
            '    //即i到m-1为左、m到j-1为右子树，直接递归进去继续判断\n'
            '    public boolean verifyPostorder(int[] postorder) {\n'
            '        return check(postorder, 0, postorder.length - 1);\n'
            '\n'
            '    }\n'
            '    public boolean check(int[] post, int i, int j){\n'
            '        if(i &gt;= j)  //如果右子树都超过左子树了，那么肯定遍历完了\n'
            '            return true;\n'
            '        int cur = i;\n'
            '        while(post[cur] &lt; post[j])  //cur代表比根节点大的节点\n'
            '            cur++;\n'
            '        int mid = cur;  //标记为mid，以这个为中点，左为左子树，右为右子树\n'
            '        //mid后面的值应该都大于根节点，如果遇到小的了那么此时就是跳出，去判断\n'
            '        //树是否为搜索树了\n'
            '        while(post[cur] &gt; post[j])\n'
            '            cur++;\n'
            '        //需满足三个条件，需要遍历完，然后左子树满足，右子树也满足\n'
            '        return cur == j &amp;&amp; check(post, i, mid - 1) &amp;&amp; check(post, mid, j - 1);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉搜索树的后序遍历序列的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    int end;//判断是否完全遍历\n'
            '    public boolean verifyPostorder(int[] postorder) {\n'
            '        if (postorder == null || postorder.length == 1) \n'
            '            return true;\n'
            '        //设置根节点\n'
            '        end = postorder.length - 1;\n'
            '        //然后开始构建二叉树\n'
            '        build(postorder, Integer.MIN_VALUE, Integer.MAX_VALUE);\n'
            '        return end &lt; 0;//如果完全遍历，则end &lt; 0;\n'
            '    }\n'
            '    private void build(int[] postorder, int min, int max) {\n'
            '        if (end &lt; 0) return ;//空了，返回\n'
            '        int rootV = postorder[end];\n'
            '        if (rootV &gt;= max || rootV &lt;= min) return ;\n'
            '        //符合节点要求，节点数量减一\n'
            '        end--;\n'
            '        //对于右子树来说，最最小值就是根节点的值，因为右子树的值都比根节点\n'
            '        //要大\n'
            '        build(postorder, rootV, max);//右子树\n'
            '        //对于左子树号右子树相反\n'
            '        build(postorder, min, rootV);//左子树\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 24: 删除二叉搜索树中的节点
# ════════════════════════════════════════════════════════════
p = '删除二叉搜索树中的节点'
d = make_deck(1747300624, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '这个代码会让树高变高，从而破坏二叉搜索树的效率，面试中会要求优化成AVL（二叉查找树，即两个子树的高度差不能超过1）这样效率就不会收到影响<br>> 如果删除这个节点可以清楚的看到树的高度变了' + img('image 9.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述删除二叉搜索树中的节点的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '这个代码会让树高变高，从而破坏二叉搜索树的效率，面试中会要求优化成AVL（二叉查找树，即两个子树的高度差不能超过1）这样效率就不会收到影响<br>> 如果删除这个节点可以清楚的看到树的高度变了<br>'
    + code(
            'class Solution {\n'
            '    public TreeNode deleteNode(TreeNode root, int key) {\n'
            '                if (root == null)return null;\n'
            '\n'
            '        if (key &gt; root.val)\n'
            '            root.right = deleteNode(root.right, key); // 去右子树删除\n'
            '\n'
            '        else if(key &lt; root.val)    \n'
            '            root.left = deleteNode(root.left, key);  // 去左子树删除\n'
            '\n'
            '        else  {  // 当前节点就是要删除的节点\n'
            '\n'
            '            if (root.left == null)   return root.right;      // 情况1，欲删除节点无左子\n'
            '            else if (root.right == null)  return root.left;  // 情况2，欲删除节点无右子\n'
            '            else if (root.left!=null &amp;&amp; root.right !=null){  // 情况3，欲删除节点左右子都有 \n'
            '                TreeNode node = root.right;   \n'
            '                while (node.left != null)      // 寻找欲删除节点右子树的最左节点\n'
            '                    node = node.left;\n'
            '\n'
            '                //这样待删除节点的左子树，可以全部移植到我们找到的待删除节点的右子树的\n'
            '                //最左节点的左孩子\n'
            '                //node保存的就是待删除节点右子树的最左节点\n'
            '                node.left = root.left;     // 将欲删除节点的左子树成为其右子树的最左节点的左子树\n'
            '                root = root.right;         // 欲删除节点的右子顶替其位置，节点被删除\n'
            '            }\n'
            '        }\n'
            '        return root;    \n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结删除二叉搜索树中的节点的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 25: 将有序数组转换为二叉搜索树
# ════════════════════════════════════════════════════════════
p = '将有序数组转换为二叉搜索树'
d = make_deck(1747300625, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '就是利用折半的特效两边分别建立二叉树')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述将有序数组转换为二叉搜索树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '就是利用折半的特效两边分别建立二叉树<br>'
    + code(
            'class Solution {\n'
            '    public TreeNode sortedArrayToBST(int[] nums) {\n'
            '        return buildTree(nums, 0, nums.length - 1);\n'
            '    }\n'
            '\n'
            '    public TreeNode buildTree(int[] nums, int left, int right){\n'
            '        if(left &gt; right);\n'
            '            return null;\n'
            '        int mid = left + (right - left) / 2;\n'
            '        //由于数组是升序的其谁做根节点都无所谓\n'
            '        TreeNode root = new TreeNode(nums[mid]);\n'
            '        //构建其左子树和右子树\n'
            '        root.left = buildTree(nums, left, mid - 1);\n'
            '        root.right = buildTree(nums, mid + 1, right);\n'
            '        return root\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结将有序数组转换为二叉搜索树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 26: 验证二叉搜索树
# ════════════════════════════════════════════════════════════
p = '验证二叉搜索树'
d = make_deck(1747300626, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '递归+中序遍历')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述验证二叉搜索树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '递归+中序遍历<br>'
    + code(
            'class Solution {\n'
            '    public boolean isValidBST(TreeNode root) {\n'
            '\n'
            '        return inOrder(root);\n'
            '    }\n'
            '\n'
            '    long preTemp = Long.MIN_VALUE;\n'
            '    //使用中序遍历来比较当前遍历结点与前一个遍历结点的值，中序遍历的当前结点肯定是比前一个结点大的\n'
            '    public boolean inOrder(TreeNode root){\n'
            '        if(root == null)\n'
            '            return true;\n'
            '        if(!inOrder(root.left))\n'
            '            return false;\n'
            '        //关键就是用一个变量保存前一个结点的值\n'
            '        if(preTemp &gt;= root.val)\n'
            '            return false;\n'
            '        preTemp = root.val;\n'
            '\n'
            '        //如果在添加if语句来判断的话，就缺少总体的返回语句来，所以这样处理\n'
            '        return inOrder(root.right);\n'
            '\n'
            '    }\n'
            '\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结验证二叉搜索树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 27: 翻转二叉树
# ════════════════════════════════════════════════════════════
p = '翻转二叉树'
d = make_deck(1747300627, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '深度优先遍历<br>广度优先遍历')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述翻转二叉树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '深度优先遍历<br>广度优先遍历<br>'
    + code(
            'class Solution {\n'
            '\n'
            '    //自己的空间复杂度跟下面优化的虽然是一个量级但是更省一些\n'
            '    public TreeNode invertTree(TreeNode root) {\n'
            '        reverse(root);\n'
            '        return root;\n'
            '    }\n'
            '\n'
            '    public void reverse(TreeNode root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        if(root.right != null &amp;&amp; root.left != null){\n'
            '            TreeNode temp = root.left;\n'
            '            root.left = root.right;\n'
            '            root.right = temp;\n'
            '        }else if(root.left == null &amp;&amp; root.right != null){\n'
            '            root.left = root.right;\n'
            '            root.right = null;\n'
            '        }else if(root.right == null &amp;&amp; root.left != null){\n'
            '            root.right = root.left;\n'
            '            root.left = null;\n'
            '        }else\n'
            '            return;\n'
            '        reverse(root.left);\n'
            '        reverse(root.right);\n'
            '    }\n'
            '\n'
            '    //过程更简洁，缺少判断每次都创建temp空间复杂度较高\n'
            '    public TreeNode invertTree(TreeNode root) {\n'
            '        if(root == null)\n'
            '            return root;\n'
            '\n'
            '        TreeNode temp = root.left;\n'
            '        root.left = root.right;\n'
            '        root.right = temp;\n'
            '\n'
            '        invertTree(root.left);\n'
            '        invertTree(root.right);\n'
            '\n'
            '        return root;\n'
            '    }\n'
            '\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结翻转二叉树的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    //广度优先遍历\n'
            '    public TreeNode invertTree(TreeNode root) {\n'
            '        if(root==null) {\n'
            '            return null;\n'
            '        }\n'
            '        //将二叉树中的节点逐层放入队列中，再迭代处理队列中的元素\n'
            '        LinkedList&lt;TreeNode&gt; queue = new LinkedList&lt;TreeNode&gt;();\n'
            '        queue.add(root);\n'
            '        while(!queue.isEmpty()) {\n'
            '            //每次都从队列中拿一个节点，并交换这个节点的左右子树\n'
            '            TreeNode tmp = queue.poll();\n'
            '            TreeNode left = tmp.left;\n'
            '            tmp.left = tmp.right;\n'
            '            tmp.right = left;\n'
            '            //如果当前节点的左子树不为空，则放入队列等待后续处理\n'
            '            if(tmp.left!=null) {\n'
            '                queue.add(tmp.left);\n'
            '            }\n'
            '            //如果当前节点的右子树不为空，则放入队列等待后续处理\n'
            '            if(tmp.right!=null) {\n'
            '                queue.add(tmp.right);\n'
            '            }\n'
            '\n'
            '        }\n'
            '        //返回处理完的根节点\n'
            '        return root;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 28: 二叉树的镜像
# ════════════════════════════════════════════════════════════
p = '二叉树的镜像'
d = make_deck(1747300628, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树的镜像。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的镜像的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    public TreeNode mirrorTree(TreeNode root) {\n'
            '        //这里记住一定要将置换结点设置为TreeNode，这样就可以把父结点以下的所有孩子结点统一进行置换\n'
            '        TreeNode temp = null;\n'
            '        if(root == null)\n'
            '            return null;\n'
            '        if(root.left != null &amp;&amp; root.right != null){\n'
            '            temp = root.left;\n'
            '            root.left = root.right;\n'
            '            root.right = temp;\n'
            '            mirrorTree(root.left);\n'
            '            mirrorTree(root.right);\n'
            '        }else if(root.left != null &amp;&amp; root.right == null){\n'
            '            root.right = root.left;\n'
            '            root.left = null;\n'
            '            //这里记住左孩子已经被我们置空了，所以要传进去更改玩的右孩子\n'
            '            mirrorTree(root.right);\n'
            '        }else{\n'
            '            root.left = root.right;\n'
            '            root.right = null;\n'
            '            //与上面的同理\n'
            '            mirrorTree(root.left);\n'
            '        }\n'
            '\n'
            '        return root;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的镜像的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 29: 路径总和
# ════════════════════════════════════════════════════════════
p = '路径总和'
d = make_deck(1747300629, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：路径总和。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述路径总和的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    public boolean hasPathSum(TreeNode root, int sum) {\n'
            '        if (root == null) {\n'
            '            return false;\n'
            '        }\n'
            '        if (root.left == null &amp;&amp; root.right == null) {\n'
            '            return sum == root.val;\n'
            '        }\n'
            '        //这个递归的过程就是先找到所有的叶子结点，然后以叶子结点为起始点逐层回溯到根结点判断，\n'
            '        //如果每一层的sum值（传入的sum是每一层开始递归减去当时所在的结点值后的结果，\n'
            '        //那么如果这个值是与下一层相等的就是满足当前层的条件）和当前结点的val是相等的那么返回父结点继续做判断\n'
            '        return hasPathSum(root.left, sum - root.val) || hasPathSum(root.right, sum - root.val);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结路径总和的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 30: 路径总和 II
# ════════════════════════════════════════════════════════════
p = '路径总和 II'
d = make_deck(1747300630, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：路径总和 II。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述路径总和 II的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            '//这道题有三个注意的点\n'
            'class Solution {\n'
            '    //dfs\n'
            '    List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
            '    public List&lt;List&lt;Integer&gt;&gt; pathSum(TreeNode root, int targetSum) {\n'
            '        List&lt;Integer&gt; path = new ArrayList&lt;&gt;();\n'
            '        dfs(root, targetSum, path);\n'
            '        return res;\n'
            '    }\n'
            '\n'
            '    public void dfs(TreeNode root, int sum, List&lt;Integer&gt; path) {\n'
            '        if(root == null) return;\n'
            '        sum = sum - root.val;\n'
            '        path.add(root.val);\n'
            '        if(root.left == null &amp;&amp; root.right == null &amp;&amp; sum == 0) {\n'
            '            //1.不能在这里直接res.add（path），应该重新new一个将当前满足路径的元素集合传入res，如果一直用path直接穿入，会有数据冗余\n'
            '            res.add(new ArrayList&lt;&gt;(path));\n'
            '            //2.不能满足条件后即这个if满足后直接返回，因为会缺少一次回溯，会不能将path的重复元素删除，所以我们需要在进行一次回溯会删除\n'
            '        }\n'
            '        dfs(root.left, sum, path);\n'
            '        dfs(root.right, sum, path);\n'
            '        //3.需要进行回溯，对每次path满足条件或不满足条件的进行筛选\n'
            '        path.remove(path.size() - 1);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结路径总和 II的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 31: 路径总和 III
# ════════════════════════════════════════════════════════════
p = '路径总和 III'
d = make_deck(1747300631, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '与第二种的区别就是不从当前根节点触发，每个节点作为根节点都可以<br>双递归，时间复杂度很大<br>前缀和+回溯，其实这种一眼就可以使用前缀和' + img('image 12.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述路径总和 III的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '与第二种的区别就是不从当前根节点触发，每个节点作为根节点都可以<br>双递归，时间复杂度很大<br>前缀和+回溯，其实这种一眼就可以使用前缀和<br>'
    + code(
            'class Solution {\n'
            '    int pathSumRes;\n'
            '    public int pathSum(TreeNode root, long targetSum) {\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        //这道题说了不要求从根节点出发，每个节点作为根节点都可以往下进行，符合条件就能增加路径数\n'
            '        dfs(root, targetSum);\n'
            '        //所以我们还要在主函数的递归中，去递归当前根节点的左右孩子作为根节点时能否符合条件\n'
            '        pathSum(root.left, targetSum);\n'
            '        pathSum(root.right, targetSum);\n'
            '        return pathSumRes;\n'
            '    }\n'
            '\n'
            '    public void dfs(TreeNode root, long sum){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        sum -= root.val;\n'
            '        if(sum == 0)\n'
            '            pathSumRes++;\n'
            '        dfs(root.left, sum);\n'
            '        dfs(root.right, sum);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结路径总和 III的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    public int pathSum(TreeNode root, int sum) {\n'
            '        // key是前缀和, value是大小为key的前缀和出现的次数\n'
            '        Map&lt;Integer, Integer&gt; prefixSumCount = new HashMap&lt;&gt;();\n'
            '        // 前缀和为0的一条路径\n'
            '        prefixSumCount.put(0, 1);\n'
            '        // 前缀和的递归回溯思路\n'
            '        return recursionPathSum(root, prefixSumCount, sum, 0);\n'
            '    }\n'
            '\n'
            '    /**\n'
            '     * 前缀和的递归回溯思路\n'
            '     * 从当前节点反推到根节点(反推比较好理解，正向其实也只有一条)，有且仅有一条路径，因为这是一棵树\n'
            '     * 如果此前有和为currSum-target,而当前的和又为currSum,两者的差就肯定为target了\n'
            '     * 所以前缀和对于当前路径来说是唯一的，当前记录的前缀和，在回溯结束，回到本层时去除，保证其不影响其他分支的结果\n'
            '     * @param node 树节点\n'
            '     * @param prefixSumCount 前缀和Map\n'
            '     * @param target 目标值\n'
            '     * @param currSum 当前路径和\n'
            '     * @return 满足题意的解\n'
            '     */\n'
            '    private int recursionPathSum(TreeNode node, Map&lt;Integer, Integer&gt; prefixSumCount, int target, int currSum) {\n'
            '        // 1.递归终止条件\n'
            '        if (node == null) {\n'
            '            return 0;\n'
            '        }\n'
            '        // 2.本层要做的事情\n'
            '        int res = 0;\n'
            '        // 当前路径上的和，这一步就是在构建前缀和\n'
            '        currSum += node.val;\n'
            '\n'
            '        //---核心代码\n'
            '        // 看看root到当前节点这条路上是否存在节点前缀和加target为currSum的路径\n'
            '        // 当前节点-&gt;root节点反推，有且仅有一条路径，如果此前有和为currSum-target,而当前的和又为currSum,两者的差就肯定为target了\n'
            '        // currSum-target相当于找路径的起点，起点的sum+target=currSum，当前点到起点的距离就是target\n'
            '        res += prefixSumCount.getOrDefault(currSum - target, 0);\n'
            '        // 更新路径上当前节点前缀和的个数\n'
            '        prefixSumCount.put(currSum, prefixSumCount.getOrDefault(currSum, 0) + 1);\n'
            '        //---核心代码\n'
            '\n'
            '        // 3.进入下一层\n'
            '        res += recursionPathSum(node.left, prefixSumCount, target, currSum);\n'
            '        res += recursionPathSum(node.right, prefixSumCount, target, currSum);\n'
            '\n'
            '        // 4.回到本层，恢复状态，去除当前节点的前缀和数量\n'
            '        prefixSumCount.put(currSum, prefixSumCount.get(currSum) - 1);\n'
            '        return res;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 32: 求根到叶子节点数字之和
# ════════════════════════════════════════════════════════════
p = '求根到叶子节点数字之和'
d = make_deck(1747300632, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '- 递归的入口<br>> 就是根结点以及0，这个0就很好的解决了我们递归的方向以及递归返回的方向，我们即需要递归入口的高位，还需要递归一层一层回来以后的总和<br>- 递归终止条件，递归出口' + img('image 13.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述求根到叶子节点数字之和的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '- 递归的入口<br>> 就是根结点以及0，这个0就很好的解决了我们递归的方向以及递归返回的方向，我们即需要递归入口的高位，还需要递归一层一层回来以后的总和<br>- 递归终止条件，递归出口<br>'
    + code(
            'class Solution {\n'
            '    //这种分路径的寻找值的不用想 深度优先遍历\n'
            '    public int sumNumbers(TreeNode root) {\n'
            '        return dfs(root,0);\n'
            '    }\n'
            '\n'
            '    public int dfs(TreeNode root, int i){\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        int temp = i * 10 + root.val;\n'
            '        if(root.left == null &amp;&amp; root.right == null)\n'
            '            return temp;\n'
            '        return dfs(root.left, temp) + dfs(root.right, temp);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结求根到叶子节点数字之和的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 33: 二叉树中的最大路径和
# ════════════════════════════════════════════════════════════
p = '二叉树中的最大路径和'
d = make_deck(1747300633, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '递归+dfs' + img('2a3b13d5-004a-4e2a-9107-c95c497b6565.png') + img('image 14.png') + img('image 15.png') + img('image 16.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树中的最大路径和的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '递归+dfs<br>'
    + code(
            'class Solution {\n'
            '    int result = Integer.MIN_VALUE;\n'
            '    public int maxPathSum(TreeNode root) {\n'
            '        dfs(root);\n'
            '        return result;\n'
            '    }\n'
            '\n'
            '    // 函数功能：返回当前节点能为父亲提供的贡献，需要结合上面的图来看！\n'
            '    private int dfs(TreeNode root) {\n'
            '        // 如果当前节点为叶子节点，那么对父亲贡献为 0\n'
            '        if(root == null) return 0;\n'
            '        // 如果不是叶子节点，计算当前节点的左右孩子对自身的贡献left和right\n'
            '        int left = dfs(root.left);\n'
            '        int right = dfs(root.right);\n'
            '        // 更新最大值，就是当前节点的val 加上左右节点的贡献。\n'
            '        result = Math.max(result, root.val + left + right);\n'
            '        // 计算当前节点能为父亲提供的最大贡献，必须是把 val 加上！\n'
            '        int max = Math.max(root.val + left, root.val + right);\n'
            '        // 如果贡献小于0的话，直接返回0即可！\n'
            '        return max &lt; 0 ? 0 : max;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树中的最大路径和的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 34: 二叉树的所有路径
# ════════════════════════════════════════════════════════════
p = '二叉树的所有路径'
d = make_deck(1747300634, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '递归就完事了')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的所有路径的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '递归就完事了<br>'
    + code(
            'class Solution {\n'
            '    List&lt;String&gt; res;\n'
            '    public List&lt;String&gt; binaryTreePaths(TreeNode root) {\n'
            '        res = new ArrayList&lt;&gt;();\n'
            '        if(root == null)\n'
            '            return null;\n'
            '        dfs(root, "");\n'
            '        return res;\n'
            '\n'
            '    }\n'
            '\n'
            '    public void dfs(TreeNode root, String curRoad){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        //自己这里自动的拆包装包最好现式的自己转换，提高效率\n'
            '        curRoad += Integer.valueOf(root.val);\n'
            '        if(root.left == null &amp;&amp; root.right == null){\n'
            '            res.add(curRoad);\n'
            '            return;\n'
            '        }\n'
            '        curRoad += "-&gt;";\n'
            '        dfs(root.left, curRoad);\n'
            '        dfs(root.right, curRoad);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的所有路径的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 35: 二叉树中和为某一值的路径
# ════════════════════════════════════════════════════════════
p = '二叉树中和为某一值的路径'
d = make_deck(1747300635, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    'DFS+回溯+递归')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树中和为某一值的路径的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    'DFS+回溯+递归<br>'
    + code(
            'class Solution {\n'
            '    List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
            '    public List&lt;List&lt;Integer&gt;&gt; pathSum(TreeNode root, int target) {\n'
            '        dfs(root, target);\n'
            '        return res;\n'
            '    }\n'
            '\n'
            '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '    public void dfs(TreeNode cur, int target){\n'
            '        //不满足则返回回溯，注意存在负数的情况 cur.val &gt; target的条件需要丢弃\n'
            '        if(cur == null)\n'
            '            return;\n'
            '        target -= cur.val;\n'
            '        list.add(cur.val);\n'
            '        //叶子节点并且满足target=0才能加入哦，中途半道满足target但不满足叶子的\n'
            '        //情况需要考虑到\n'
            '        if(target == 0 &amp;&amp; cur.left == null &amp;&amp; cur.right == null){\n'
            '            res.add(new ArrayList&lt;&gt;(list));\n'
            '        }\n'
            '        dfs(cur.left, target);\n'
            '        dfs(cur.right, target);\n'
            '        //这里就是回溯到基础，丢弃节点\n'
            '        list.remove(list.size() - 1);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树中和为某一值的路径的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 36: 二叉树的完全性检验
# ════════════════════════════════════════════════════════════
p = '二叉树的完全性检验'
d = make_deck(1747300636, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '创建节点辅助类<br>完全二叉树就是最下面两层的节点度数可以小于2，并且最下面一层的叶子结点都依次排序在该层的最左侧的位置上')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的完全性检验的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '创建节点辅助类<br>完全二叉树就是最下面两层的节点度数可以小于2，并且最下面一层的叶子结点都依次排序在该层的最左侧的位置上<br>'
    + code(
            '//这个方法就是用了二叉树的性质，当根节点的序号为i，那么左孩子为2i\n'
            '//右孩子为2i+1，那么当全部节点进去list，如果为完全二叉树，此时的size应该\n'
            '//等于最后一个节点的序号\n'
            'class Solution {\n'
            '    public boolean isCompleteTree(TreeNode root) {\n'
            '        List&lt;ANode&gt; nodes = new ArrayList();\n'
            '        nodes.add(new ANode(root, 1));\n'
            '        int i = 0;\n'
            '        while (i &lt; nodes.size()) {\n'
            '            ANode anode = nodes.get(i++);\n'
            '            if (anode.node != null) {\n'
            '                nodes.add(new ANode(anode.node.left, anode.code * 2));\n'
            '                nodes.add(new ANode(anode.node.right, anode.code * 2 + 1));\n'
            '            }\n'
            '        }\n'
            '        //这里减一是因为i++，所以i-1才是最后一个\n'
            '        return nodes.get(i-1).code == nodes.size();\n'
            '    }\n'
            '}\n'
            '\n'
            'class ANode {  // Annotated Node\n'
            '    TreeNode node;\n'
            '    int code;\n'
            '    ANode(TreeNode node, int code) {\n'
            '        this.node = node;\n'
            '        this.code = code;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的完全性检验的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 37: 完全二叉树的节点个数
# ════════════════════════════════════════════════════════════
p = '完全二叉树的节点个数'
d = make_deck(1747300637, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '这里就是利用二叉树的性质和完全二叉树的性质，下面求节点数量也可以用位运算；求完全二叉树的高度也可以直接利用性质，左子树一条道求到底<br>朴实无华的递归' + img('image 17.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述完全二叉树的节点个数的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '这里就是利用二叉树的性质和完全二叉树的性质，下面求节点数量也可以用位运算；求完全二叉树的高度也可以直接利用性质，左子树一条道求到底<br>朴实无华的递归<br>'
    + code(
            'class Solution {\n'
            '    public int countNodes(TreeNode root) {\n'
            '        int height = getHeight(root);\n'
            '        if(height &lt; 1)\n'
            '            return 0;\n'
            '        int left = getHeight(root.left);    //得到左子树的高度\n'
            '        int right = getHeight(root.right);  //得到右子树的高度\n'
            '        //根据完全二叉树的性质，如果两个子树的高度相等那么左子树的最下面的节点肯定是满的，右边\n'
            '        //就要一层一层去求了，没减1，也是加上了root\n'
            '        if(left == right){\n'
            '            return countNodes(root.right) + (int)Math.pow(2, left);\n'
            '        }else{  //如果不满足说明最下面一层的节点数不是满的\n'
            '            //那么对于倒数第二层的右子树是满的，知道高度值求右子树的节点树，没有减一加上了root节点\n'
            '            //对于左子树就是一层一层去求\n'
            '            return countNodes(root.left) + (int)Math.pow(2, right);\n'
            '        }\n'
            '    }\n'
            '\n'
            '    public int getHeight(TreeNode root){\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        int left = getHeight(root.left);\n'
            '        int right = getHeight(root.right);\n'
            '        return Math.max(left , right) + 1;\n'
            '\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结完全二叉树的节点个数的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    public int countNodes(TreeNode root) {\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        return countNodes(root.left) + countNodes(root.right) + 1;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 38: 从前序与中序遍历序列构造二叉树
# ════════════════════════════════════════════════════════════
p = '从前序与中序遍历序列构造二叉树'
d = make_deck(1747300638, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '分治算法：只能应对节点值不重复的二叉树<br>注意在传下一个层次的数组时已经构建了根节点的数值就不需要传入了<br>- 前序：[3,9,20,15,7]' + img('image 18.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述从前序与中序遍历序列构造二叉树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '分治算法：只能应对节点值不重复的二叉树<br>注意在传下一个层次的数组时已经构建了根节点的数值就不需要传入了<br>- 前序：[3,9,20,15,7]<br>'
    + code(
            'class Solution {\n'
            '    private Map&lt;Integer,Integer&gt; map;\n'
            '    //这里可以将前序序列储存起来，因为递归中只是用了前序序列\n'
            '    private int[] tempPre;\n'
            '    public TreeNode buildTree(int[] preorder, int[] inorder) {       \n'
            '        int n = preorder.length;//记录边界\n'
            '        map = new HashMap&lt;&gt;();\n'
            '        for(int i = 0; i &lt; n; i++){\n'
            '            //这里就是用map来定位中序遍历的根结点位置，以此来确定左子树和右子树的结点数量\n'
            '            map.put(inorder[i], i); \n'
            '        }\n'
            '        tempPre  = preorder;\n'
            '        return myBuild(0, n - 1, 0, n - 1);\n'
            '\n'
            '    }\n'
            '\n'
            '    //四个索引分别为\n'
            '    //当前根的左边界\n'
            '    //当前根的右边界\n'
            '    //递归树的左边界，即数组左边界\n'
            '    //递归树的右边界，即数组右边界\n'
            '    private TreeNode myBuild(int preLeft, \n'
            '                            int preRight, \n'
            '                            int inLeft, \n'
            '                            int inRight){\n'
            '        if(preLeft &gt; preRight)\n'
            '            return null;    //如果满足此条件就是说明此树为空\n'
            '\n'
            '        int preRoot = preLeft;  //先得到根结点的值，因为前序遍历的左边界就是根节点\n'
            '        //创建根结点\n'
            '        TreeNode root = new TreeNode(tempPre[preRoot]);\n'
            '        //呼应我们主方法的map定位根结点的位置，map的key是每个节点值，value是在中序遍历的数组中的索引下标，\n'
            '        //即我们就找到了中序遍历中的根结点索引位置\n'
            '        int inRoot = map.get(tempPre[preRoot]);  \n'
            '\n'
            '        //左子树结点个数=中序遍历根节点位置-中序遍历根节点左子树的节点位置，上图就是1-0即为1\n'
            '        int size_left_subtree = inRoot - inLeft;\n'
            '\n'
            '        //左右子树遍历完成以后跟根结点连接起来就可以了\n'
            '        //开始左递归遍历左子树\n'
            '        //先序遍历中「从 左边界+1 开始到 左子树节点数量」个元素就对应了\n'
            '        //中序遍历中「从 左边界 开始到 根节点定位-1」的元素        \n'
            '        root.left = myBuild(preLeft + 1, preLeft + size_left_subtree, inLeft, inRoot - 1);\n'
            '\n'
            '        //开始右递归遍历右子树\n'
            '\n'
            '        // 先序遍历中「从 左边界+1+左子树节点数目 开始到 右边界」的元素就对应了\n'
            '        //中序遍历中「从 根节点定位+1 到 右边界」的元素\n'
            '        root.right = myBuild(preLeft + size_left_subtree + 1, preRight, inRoot + 1,inRight);\n'
            '\n'
            '        return root;\n'
            '\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结从前序与中序遍历序列构造二叉树的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    public TreeNode buildTree(int[] preorder, int[] inorder) {\n'
            '        //记录结点数量\n'
            '        int p_len = preorder.length;\n'
            '        int i_len = inorder.length;\n'
            '        if(p_len &lt;= 0 || i_len &lt;= 0)\n'
            '            return null;\n'
            '        //根结点的值\n'
            '        int rootVal = preorder[0];\n'
            '        TreeNode root = new TreeNode(rootVal);\n'
            '        //记录分界点\n'
            '        int k = 0;\n'
            '        for(int i = 0; i &lt; i_len; i++){\n'
            '            if(inorder[i] == rootVal){\n'
            '                k = i;\n'
            '                break;\n'
            '            }\n'
            '        }\n'
            '        //开始递归的去构建左子树和右子树\n'
            '        //都是左闭右开\n'
            '        root.left = buildTree(Arrays.copyOfRange(preorder, 1, k + 1), \n'
            '                            Arrays.copyOfRange(inorder, 0, k));\n'
            '\n'
            '        root.right = buildTree(Arrays.copyOfRange(preorder, k + 1, p_len), \n'
            '                            Arrays.copyOfRange(inorder, k + 1, i_len));\n'
            '\n'
            '        return root;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 39: 从中序与后序遍历序列构造二叉树
# ════════════════════════════════════════════════════════════
p = '从中序与后序遍历序列构造二叉树'
d = make_deck(1747300639, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '可以优化成hash寻找根节点位置<br>hash优化，空间复杂度和时间都上升了一个层级')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述从中序与后序遍历序列构造二叉树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '可以优化成hash寻找根节点位置<br>hash优化，空间复杂度和时间都上升了一个层级<br>'
    + code(
            'class Solution {\n'
            '    //递归每一层代表这一层的根节点以及构建其左右子树的过程\n'
            '    public TreeNode buildTree(int[] inorder, int[] postorder) {\n'
            '        //记录结点数量\n'
            '        int i_len = inorder.length, p_len = postorder.length;\n'
            '        if(i_len &lt;= 0 || p_len &lt;= 0)  //结点值小于0返回null\n'
            '            return null;\n'
            '        //定义返回结点根节点root\n'
            '        TreeNode root;\n'
            '        //根节点值\n'
            '        int rootVal = postorder[p_len - 1];\n'
            '        //创建二叉树的根节点\n'
            '        root = new TreeNode(rootVal);\n'
            '        int k = 0;  //遍历中序序列，确定根节点在中序序列的位置，从而确定左右子树\n'
            '        //可以优化这里，将顺序遍历，优化成hash\n'
            '        for(int i = 0; i &lt; i_len; i++){\n'
            '            if(inorder[i] == rootVal){\n'
            '                k = i;\n'
            '                break;\n'
            '            }\n'
            '        }\n'
            '        //分割左右子树，分别创建左右子树的中序、后序序列\n'
            '        root.left = buildTree(Arrays.copyOfRange(inorder, 0, k), \n'
            '                        Arrays.copyOfRange(postorder, 0, k));\n'
            '        root.right = buildTree(Arrays.copyOfRange(inorder, k + 1, i_len),\n'
            '                        Arrays.copyOfRange(postorder, k, p_len - 1));\n'
            '\n'
            '        return root;   \n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结从中序与后序遍历序列构造二叉树的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '\n'
            '    HashMap&lt;Integer,Integer&gt; memo = new HashMap&lt;&gt;();\n'
            '    int[] post;\n'
            '\n'
            '    public TreeNode buildTree(int[] inorder, int[] postorder) {\n'
            '        for(int i = 0;i &lt; inorder.length; i++) \n'
            '	        memo.put(inorder[i], i);\n'
            '        post = postorder;\n'
            '        TreeNode root = buildTree(0, inorder.length - 1, 0, post.length - 1);\n'
            '        return root;\n'
            '    }\n'
            '\n'
            '    public TreeNode buildTree(int is, int ie, int ps, int pe) {\n'
            '        if(ie &lt; is || pe &lt; ps) \n'
            '	        return null;\n'
            '\n'
            '        int root = post[pe];\n'
            '        int ri = memo.get(root);\n'
            '\n'
            '        TreeNode node = new TreeNode(root);\n'
            '        node.left = buildTree(is, ri - 1, ps, ps + ri - is - 1);\n'
            '        node.right = buildTree(ri + 1, ie, ps + ri - is, pe - 1);\n'
            '        return node;\n'
            '    }\n'
            '}\n'
    ))

# ════════════════════════════════════════════════════════════
# Problem 40: 重建二叉树
# ════════════════════════════════════════════════════════════
p = '重建二叉树'
d = make_deck(1747300640, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '注意：本文方法只适用于 “无重复节点值” 的二叉树。PythonJavaC++')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述重建二叉树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '注意：本文方法只适用于 “无重复节点值” 的二叉树。PythonJavaC++<br>'
    + code(
            'class Solution {\n'
            '    int[] preorder;\n'
            '    HashMap&lt;Integer, Integer&gt; hmap = new HashMap&lt;&gt;();\n'
            '    public TreeNode deduceTree(int[] preorder, int[] inorder) {\n'
            '        this.preorder = preorder;\n'
            '        for(int i = 0; i &lt; inorder.length; i++)\n'
            '            hmap.put(inorder[i], i);\n'
            '        return recur(0, 0, inorder.length - 1);\n'
            '    }\n'
            '    TreeNode recur(int root, int left, int right) {\n'
            '        if(left &gt; right) return null;                          // 递归终止\n'
            '        TreeNode node = new TreeNode(preorder[root]);          // 建立根节点\n'
            '        int i = hmap.get(preorder[root]);                      // 划分根节点、左子树、右子树\n'
            '        node.left = recur(root + 1, left, i - 1);              // 开启左子树递归\n'
            '        node.right = recur(root + i - left + 1, i + 1, right); // 开启右子树递归\n'
            '        return node;                                           // 回溯返回根节点\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结重建二叉树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 41: 合并二叉树
# ════════════════════════════════════════════════════════════
p = '合并二叉树'
d = make_deck(1747300641, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：合并二叉树。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述合并二叉树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '    public TreeNode mergeTrees(TreeNode root1, TreeNode root2) {\n'
            '        if(root1 == null &amp;&amp; root2 == null)\n'
            '            return null;\n'
            '        //两者都不为空进行前序遍历，开始相加\n'
            '        if(root1 != null &amp;&amp; root2 != null){\n'
            '            root1.val += root2.val;\n'
            '            root1.left = mergeTrees(root1.left, root2.left);\n'
            '            root1.right = mergeTrees(root1.right, root2.right);\n'
            '            return root1;\n'
            '        }else{\n'
            '            //两者有一方不为空，返回不为空的\n'
            '            return root1 == null ? root2 : root1;\n'
            '        } \n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结合并二叉树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 42: 树的子结构
# ════════════════════════════════════════════════════════════
p = '树的子结构'
d = make_deck(1747300642, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    'DFS')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述树的子结构的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    'DFS<br>'
    + code(
            'class Solution {\n'
            '    public boolean isSubStructure(TreeNode A, TreeNode B) {\n'
            '        if(A == null || B == null)\n'
            '            return false;\n'
            '        //从父的根节点就开始比较，如果不是就开始比左子树或右子树只要有一个满足就返回\n'
            '        return dfs(A, B) || isSubStructure(A.left, B) || isSubStructure(A.right, B);\n'
            '    }\n'
            '\n'
            '    public boolean dfs(TreeNode parent, TreeNode child){\n'
            '        if(child == null)   //如果孩子提前比没了就证明是子树\n'
            '            return true;\n'
            '        if(parent == null)  //如果父树提前比完了就证明不是子树，因为父树的节点数量大于子树\n'
            '            return false;\n'
            '        return parent.val == child.val &amp;&amp; dfs(parent.left, child.left)\n'
            '                    &amp;&amp; dfs(parent.right, child.right);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结树的子结构的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 43: 另一个树的子树
# ════════════════════════════════════════════════════════════
p = '另一个树的子树'
d = make_deck(1747300643, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：另一个树的子树。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述另一个树的子树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            '\n'
            'class Solution {\n'
            '    public boolean isSubtree(TreeNode root, TreeNode subRoot) {\n'
            '        //对于子树题目明确不为空，那么就对root判空就好\n'
            '        if(root == null)\n'
            '            return false;\n'
            '        //先看最基本未递归的是否相等，然后开始递归看左子树和右子树\n'
            '        return isSameTree(root, subRoot) || isSubtree(root.left, subRoot)\n'
            '                || isSubtree(root.right, subRoot);\n'
            '    }\n'
            '\n'
            '    //传进两个节点依次比较以这两个节点为根节点的子树\n'
            '    public boolean isSameTree(TreeNode root1, TreeNode root2) {\n'
            '        // 都为空的话，显然相同\n'
            '        if (root1 == null &amp;&amp; root2 == null) return true;\n'
            '        // 一个为空，一个非空，显然不同\n'
            '        if (root1 == null || root2 == null) return false;\n'
            '        // 两个都非空，但 val 不一样也不行\n'
            '        if (root1.val != root2.val) return false;\n'
            '\n'
            '        // root1 和 root2 该比的都比完了\n'
            '        return isSameTree(root1.left, root2.left)\n'
            '            &amp;&amp; isSameTree(root1.right, root2.right);\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结另一个树的子树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 44: 二叉树展开为链表
# ════════════════════════════════════════════════════════════
p = '二叉树展开为链表'
d = make_deck(1747300644, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：二叉树展开为链表。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树展开为链表的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            '\n'
            'class Solution {\n'
            '\n'
            '    //这个方法我采用前序遍历的逆序，注意是先右 左 根的，并不是\n'
            '    //后序遍历哦，见题目展开后的链表顺序就是原树的前序遍历，但如果\n'
            '    //我们直接用前序会让右子树的节点丢失，所以采用前序的逆序，\n'
            '    //自底向上的方法 6 5 4 3 2 1  6《- 5 4 3 2 1\n'
            '    TreeNode pre;\n'
            '    public void flatten(TreeNode root) {\n'
            '\n'
            '        if(root == null)\n'
            '            return;\n'
            '        flatten(root.right);\n'
            '        flatten(root.left);\n'
            '        root.right = pre;\n'
            '        root.left = null;\n'
            '        pre = root;\n'
            '    }\n'
            '\n'
            '    //第二种方法，我们采用，将左子树直接转移到右子树，然后让右子树\n'
            '    //用一个临时节点保存，再加入到左子树移动后的树，然后继续移动到\n'
            '    //有左子树的根节点\n'
            '    /*\n'
            '    1\n'
            '   / \\n'
            '  2   5\n'
            ' / \   \\n'
            '3   4   6\n'
            '\n'
            '//将 1 的左子树插入到右子树的地方\n'
            '    1\n'
            '     \\n'
            '      2         5\n'
            '     / \         \\n'
            '    3   4         6        \n'
            '//将原来的右子树接到左子树的最右边节点\n'
            '    1\n'
            '     \\n'
            '      2          \n'
            '     / \          \n'
            '    3   4  \n'
            '         \\n'
            '          5\n'
            '           \\n'
            '            6\n'
            '\n'
            ' //将 2 的左子树插入到右子树的地方\n'
            '    1\n'
            '     \\n'
            '      2          \n'
            '       \          \n'
            '        3       4  \n'
            '                 \\n'
            '                  5\n'
            '                   \\n'
            '                    6   \n'
            '\n'
            ' //将原来的右子树接到左子树的最右边节点\n'
            '    1\n'
            '     \\n'
            '      2          \n'
            '       \          \n'
            '        3      \n'
            '         \\n'
            '          4  \n'
            '           \\n'
            '            5\n'
            '             \\n'
            '              6         \n'
            '\n'
            '  ......*/\n'
            '    public void flatten(TreeNode root) {\n'
            '        while(root != null){\n'
            '            if(root.left == null)\n'
            '                root = root.right;\n'
            '            else{\n'
            '                //找到左子树的最右节点\n'
            '                TreeNode pre = root.left;\n'
            '                while(pre.right != null){\n'
            '                    pre = pre.right;\n'
            '                }\n'
            '                //将最右节点的右节点，设置为根节点的右子树\n'
            '                pre.right = root.right;\n'
            '                //将整个左子树移动到右子树那边\n'
            '                root.right = root.left;\n'
            '                //左子树置为空\n'
            '                root.left = null;\n'
            '                //遍历下一个有左子树的\n'
            '                root = root.right;\n'
            '            }\n'
            '        }\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树展开为链表的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 45: 二叉树中所有距离为 K 的结点
# ════════════════════════════════════════════════════════════
p = '二叉树中所有距离为 K 的结点'
d = make_deck(1747300645, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '树转图（领接表）+BFS')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树中所有距离为 K 的结点的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '树转图（领接表）+BFS<br>'
    + code(
            'class Solution {\n'
            '    Map&lt;Integer, List&lt;Integer&gt;&gt; map;\n'
            '    List&lt;Integer&gt; res;\n'
            '    Set&lt;Integer&gt; visit;\n'
            '    public List&lt;Integer&gt; distanceK(TreeNode root, TreeNode target, int k) {\n'
            '        if(root == null)\n'
            '            return new ArrayList();\n'
            '        res = new ArrayList&lt;&gt;();\n'
            '        //使用map存放领接表，key是节点，value是相邻的点\n'
            '        //之所以使用领接表不用矩阵，对于本体的树转化为图其实属于稀疏图，为了节约内存\n'
            '        map = new HashMap&lt;&gt;();\n'
            '        //我们使用BFS的方式去遍历图，以target向外扩散k次就是目标的所有节点了\n'
            '        dfs(root);\n'
            '        //我们用一个集合标记去过的节点\n'
            '        visit = new HashSet&lt;&gt;();\n'
            '        Deque&lt;Integer&gt; queue = new LinkedList&lt;&gt;();\n'
            '        queue.add(target.val);\n'
            '        visit.add(target.val);\n'
            '        int size = 0;\n'
            '        while(!queue.isEmpty() &amp;&amp; k &gt;= 0){\n'
            '            size = queue.size();\n'
            '            for(int i = 0; i &lt; size; i++){\n'
            '                int temp = queue.poll();\n'
            '                if(k == 0){ //到达目标距离的所有节点，循环队列里面节点次数最后返回即可\n'
            '                    res.add(temp);\n'
            '                    continue;\n'
            '                }\n'
            '                //得到当前节点的相邻节点\n'
            '                List&lt;Integer&gt; nodes = map.get(temp);\n'
            '                if(nodes == null)   continue;\n'
            '                for(int node : nodes){\n'
            '                    //防止重复遍历，如果没有访问过加入队列和访问集合\n'
            '                    if(!visit.contains(node)){\n'
            '                        queue.add(node);\n'
            '                        visit.add(node);\n'
            '                    }\n'
            '                }\n'
            '\n'
            '            }\n'
            '            k--;\n'
            '        }\n'
            '        return res;\n'
            '\n'
            '    }\n'
            '    //构建图的边关系：通过dfs遍历每个节点，每个节点将左右孩子分别添加进去，注意是无向图，双向的\n'
            '    public void dfs(TreeNode root){\n'
            '        if(root == null)\n'
            '            return;\n'
            '        if(root.left != null){\n'
            '            add(root.val, root.left.val);\n'
            '            add(root.left.val, root.val);\n'
            '            dfs(root.left);\n'
            '        }\n'
            '        if(root.right != null){\n'
            '            add(root.val, root.right.val);\n'
            '            add(root.right.val, root.val);\n'
            '            dfs(root.right);\n'
            '        }\n'
            '    }\n'
            '    //添加具体的边关系\n'
            '    public void add(int a, int b){\n'
            '        if(map.get(a) == null){\n'
            '            List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
            '            list.add(b);\n'
            '            map.put(a, list);\n'
            '        }else{\n'
            '            List&lt;Integer&gt; list = map.get(a);\n'
            '            list.add(b);\n'
            '            map.put(a, list);\n'
            '        }\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树中所有距离为 K 的结点的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 46: 二叉树的序列化与反序列化
# ════════════════════════════════════════════════════════════
p = '二叉树的序列化与反序列化'
d = make_deck(1747300646, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '层次遍历')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的序列化与反序列化的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '层次遍历<br>'
    + code(
            '/**\n'
            ' * Definition for a binary tree node.\n'
            ' * public class TreeNode {\n'
            ' *     int val;\n'
            ' *     TreeNode left;\n'
            ' *     TreeNode right;\n'
            ' *     TreeNode(int x) { val = x; }\n'
            ' * }\n'
            ' */\n'
            'public class Codec {\n'
            '\n'
            '    StringBuilder s = new StringBuilder();\n'
            '    // Encodes a tree to a single string.\n'
            '    public String serialize(TreeNode root) {\n'
            '        if(root == null)\n'
            '            return "";\n'
            '        //我们使用层次遍历\n'
            '        Deque&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        //根结点入队\n'
            '        queue.offerLast(root);\n'
            '        TreeNode temp;\n'
            '        while(queue.size() != 0){\n'
            '            temp = queue.removeFirst();\n'
            '            //我们需要用null来占位，不然使用层次遍历恢复不了\n'
            '            if(temp == null)\n'
            '                s.append("null,");\n'
            '            else{\n'
            '                s.append(temp.val + ",");\n'
            '                queue.offerLast(temp.left);\n'
            '                queue.offerLast(temp.right);\n'
            '            }\n'
            '        }\n'
            '        return s.toString();\n'
            '    }\n'
            '\n'
            '    // 这里反序列化使用了两个队列\n'
            '    public TreeNode deserialize(String data) {\n'
            '        if(data == null || data == "")\n'
            '            return null;\n'
            '        //存放数字和null队列\n'
            '        Queue&lt;String&gt; nodes = new ArrayDeque(Arrays.asList(data.split(",")));\n'
            '        //设置根节点\n'
            '        TreeNode root = new TreeNode(Integer.parseInt(nodes.poll()));\n'
            '        //存放各个结点的辅助队列\n'
            '        Queue&lt;TreeNode&gt; queue = new ArrayDeque&lt;&gt;();\n'
            '        //将根节点入队\n'
            '        queue.offer(root);\n'
            '        while(!queue.isEmpty()){\n'
            '            //开始循环遍历建立二叉树（一定要把空值在序列化的时候标记上）\n'
            '            TreeNode node = queue.poll();\n'
            '\n'
            '            String left = nodes.poll();\n'
            '            String right = nodes.poll();\n'
            '            if(!left.equals("null")){\n'
            '                node.left = new TreeNode(Integer.parseInt(left));\n'
            '                queue.add(node.left);\n'
            '            }\n'
            '\n'
            '            if(!right.equals("null")){\n'
            '                node.right = new TreeNode(Integer.parseInt(right));\n'
            '                queue.add(node.right);\n'
            '            }\n'
            '\n'
            '        }\n'
            '        return root;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的序列化与反序列化的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 47: 不同的二叉搜索树
# ════════════════════════════════════════════════════════════
p = '不同的二叉搜索树'
d = make_deck(1747300647, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '动态规划' + img('image 19.png'))

add_basic(d, make_front(p, '遍历/递归策略'), '请描述不同的二叉搜索树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '动态规划<br>'
    + code(
            'class Solution {\n'
            '    //根据构造搜索二叉树的性质，可知根据不同的输入序列会输出不同的二叉树\n'
            '    //二叉搜索树的性质是中序遍历递增\n'
            '    //比如序列【3 1 2】就是例子中最后一个二叉树\n'
            '     public int numTrees(int n) {\n'
            '         //dp状态时，n个节点时的不同二叉搜索树的个数\n'
            '        int[] dp = new int[n+1];\n'
            '        //初始化状态：没有值和第一个值的序列都为1个树\n'
            '        dp[0] = 1;\n'
            '        dp[1] = 1;\n'
            '        //从两个节点的地方开始\n'
            '        /*\n'
            '        G(n)=f(1)+f(2)+f(3)+f(4)+...+f(n)\n'
            '\n'
            '        当 i 为根节点时，其左子树节点个数为 i-1 个，右子树节点为 n-i，则\n'
            '\n'
            '        f(i)=G(i−1)∗G(n−i)\n'
            '        综合两个公式可以得到 卡特兰数 公式\n'
            '\n'
            '        G(n)=G(0)∗G(n−1)+G(1)∗G(n−2)+...+G(n−1)∗G(0)\n'
            '        dp[2] = dp[0] * dp[1] + dp[1] * dp[0]\n'
            '         */\n'
            '        for(int i = 2; i &lt; n + 1; i++)\n'
            '            for(int j = 1; j &lt; i + 1; j++) \n'
            '                dp[i] += dp[j-1] * dp[i-j];\n'
            '\n'
            '        return dp[n];\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结不同的二叉搜索树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 48: 打家劫舍 III
# ════════════════════════════════════════════════════════════
p = '打家劫舍 III'
d = make_deck(1747300648, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    '终极方法<br>> 每个节点可选择偷或者不偷两种状态，根据题目意思，相连节点不能一起偷<br>- 当前节点选择偷时，那么两个孩子节点就不能选择偷了')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述打家劫舍 III的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '终极方法<br>> 每个节点可选择偷或者不偷两种状态，根据题目意思，相连节点不能一起偷<br>- 当前节点选择偷时，那么两个孩子节点就不能选择偷了<br>'
    + code(
            'public int rob(TreeNode root) {\n'
            '    int[] result = robErgodic(root);\n'
            '    return Math.max(result[0], result[1]);\n'
            '}\n'
            '\n'
            'public int[] robErgodic(TreeNode root) {\n'
            '    if (root == null) \n'
            '        return new int[2];\n'
            '    int[] result = new int[2];\n'
            '\n'
            '    int[] left = robErgodic(root.left);\n'
            '    int[] right = robErgodic(root.right);\n'
            '\n'
            '    result[0] = Math.max(left[0], left[1]) + Math.max(right[0], right[1]);\n'
            '    result[1] = left[0] + right[0] + root.val;\n'
            '\n'
            '    return result;\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结打家劫舍 III的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 49: 相同的树
# ════════════════════════════════════════════════════════════
p = '相同的树'
d = make_deck(1747300649, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'), '二叉树问题：相同的树。')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述相同的树的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    '<br>'
    + code(
            'class Solution {\n'
            '\n'
            '    boolean isSameTree(TreeNode root1, TreeNode root2) {\n'
            '    // 都为空的话，显然相同\n'
            '    if (root1 == null &amp;&amp; root2 == null) return true;\n'
            '    // 一个为空，一个非空，显然不同\n'
            '    if (root1 == null || root2 == null) return false;\n'
            '    // 两个都非空，但 val 不一样也不行\n'
            '    if (root1.val != root2.val) return false;\n'
            '\n'
            '    // root1 和 root2 该比的都比完了\n'
            '    return isSameTree(root1.left, root2.left)\n'
            '        &amp;&amp; isSameTree(root1.right, root2.right);\n'
            '	}\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结相同的树的关键技巧。')

# ════════════════════════════════════════════════════════════
# Problem 50: 二叉树的最小深度
# ════════════════════════════════════════════════════════════
p = '二叉树的最小深度'
d = make_deck(1747300650, f'算法::二叉树::{p}')

add_basic(d, make_front(p, '题干'),
    'DFS<br>BFS')

add_basic(d, make_front(p, '遍历/递归策略'), '请描述二叉树的最小深度的遍历/递归策略。')

add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}}，空间：{{c2::O(n)}}')

add_basic(d, make_front(p, '题解(BFS/DFS)'),
    'DFS<br>BFS<br>'
    + code(
            'class Solution {\n'
            '    //1.递归条件（就是会出现的各种情况）\n'
            '    //2.只在意本层的逻辑\n'
            '    //3.需要返回什么，（根据条件你需要返回什么）\n'
            '    /*叶子节点的定义是左孩子和右孩子都为 null 时叫做叶子节点\n'
            '    当 root 节点左右孩子都为空时，返回 1\n'
            '    当 root 节点左右孩子有一个为空时，返回不为空的孩子节点的深度\n'
            '    当 root 节点左右孩子都不为空时，返回左右孩子较小深度的节点值\n'
            '    */\n'
            '    public int minDepth(TreeNode root) {\n'
            '        //根节点位0，树为空\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        //左右子树都为空，返回自身的长度\n'
            '        if(root.left == null &amp;&amp; root.right == null)\n'
            '            return 1;\n'
            '        //当左子树为空，返回右子树+自身的长度\n'
            '        if(root.left == null)\n'
            '            return minDepth(root.right) + 1;\n'
            '        //与上面同理\n'
            '        if(root.right == null)\n'
            '            return minDepth(root.left) + 1;\n'
            '        //左右子树都不为空，那就看谁小\n'
            '        return Math.min(minDepth(root.left), minDepth(root.right)) + 1;\n'
            '    }\n'
            '}\n'
    ))

add_basic(d, make_front(p, '关键技巧'), '请总结二叉树的最小深度的关键技巧。')
add_basic(d, make_front(p, f'题解(方法2)'),
    '替代解法<br>'
    + code(
            'class Solution {\n'
            '    public int minDepth(TreeNode root) {\n'
            '        if(root == null)\n'
            '            return 0;\n'
            '        Queue&lt;TreeNode&gt; queue = new LinkedList&lt;&gt;();\n'
            '        queue.add(root);\n'
            '        int res = 1;    //如果根节点不为空那么初始树高就是1\n'
            '        while(!queue.isEmpty()){\n'
            '            int len = queue.size();\n'
            '            //这里加个for循环的原因就是遍历本层节点，如果本层的任意节点出现了\n'
            '            //没有左右子树的情况则立即返回\n'
            '            //你不遍历本层节点，直接在while中操作res，会出现你先写的左边还是右边\n'
            '            //加入队列，那就按谁的来\n'
            '            for(int i = 0; i &lt; len; i++){\n'
            '                TreeNode temp = queue.poll();\n'
            '                if(temp.left == null &amp;&amp; temp.right == null)\n'
            '                    return res;    \n'
            '                if(temp.left != null)\n'
            '                    queue.add(temp.left);\n'
            '                if(temp.right != null)\n'
            '                    queue.add(temp.right);\n'
            '            }\n'
            '            res++;//都没有上面所说的那个情况出现，树深加1\n'
            '        }\n'
            '        return res;\n'
            '    }\n'
            '}\n'
    ))


if __name__ == '__main__':
    print(build('../../牌组/二叉树.apkg'))