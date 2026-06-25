"""Build APKG for 树结构对比与旋转操作 — 含完整伪代码的面试卡片."""
import html as _html
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\claudeProjects\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, build


def pseudo(text: str) -> str:
    """Escape and wrap pseudocode in <pre> for display."""
    escaped = _html.escape(text)
    return f'<pre><code>{escaped}</code></pre>'


# ═══════════════════════════════════════════════════════════════
# Deck
# ═══════════════════════════════════════════════════════════════
d = make_deck(1747300900, '八股文::数据结构')

# ═══════════════════════════════════════════════════════════════
# Card 1: 五种树对比总表 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, '五种树结构对比总表',
    '<table style="border-collapse:collapse;">'
    '<tr><th>维度</th><th>BST</th><th>AVL</th><th>红黑树</th><th>B树</th><th>B+树</th></tr>'
    '<tr><td>平衡方式</td><td>无</td><td>严格|bf|≤1</td><td>黑高一致</td><td>叶同层</td><td>叶同层</td></tr>'
    '<tr><td>节点结构</td><td>val+left+right</td><td>+height</td><td>+color</td><td>keys[]+children[]</td><td>内:keys+ptrs / 叶:keys+data+next</td></tr>'
    '<tr><td>高度</td><td>n~1</td><td>~1.44log(n)</td><td>~2log(n)</td><td>log_m(n)</td><td>log_m(n)</td></tr>'
    '<tr><td>查找</td><td>O(n)</td><td>O(log n)</td><td>O(log n)</td><td>O(log n)</td><td>O(log n)</td></tr>'
    '<tr><td>插入</td><td>O(n)</td><td>O(log n)+旋转</td><td>变色+≤2转</td><td>O(log n)+分裂</td><td>O(log n)+分裂</td></tr>'
    '<tr><td>删除</td><td>O(n)</td><td>可能O(log n)转</td><td>变色+≤3转</td><td>O(log n)+合并/借位</td><td>O(log n)+合并/借位</td></tr>'
    '<tr><td>存储</td><td>内存</td><td>内存</td><td>内存</td><td>磁盘</td><td>磁盘</td></tr>'
    '<tr><td>实例</td><td>教学</td><td>查找密集</td><td>TreeMap, CFS, epoll</td><td>MongoDB</td><td>MySQL, PG</td></tr>'
    '</table>'
    '<br><b>核心规律</b>：内存用AVL(查多)或红黑树(写多)；磁盘用B/B+树。'
)

# ═══════════════════════════════════════════════════════════════
# Card 2: 左旋/右旋伪代码 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, '左旋/右旋伪代码',
    '<b>旋转前后中序遍历不变！AVL和红黑树的旋转操作完全一致。</b><br><br>'
    '<b>右旋（Right Rotate）— LL场景</b><br>'
    + pseudo(
        'ROTATE_RIGHT(y):\n'
        '    x  = y.left          // x 是 y 的左孩子\n'
        '    T2 = x.right         // 保存 x 的右子树（将被挂在 y 下）\n'
        '    x.right = y          // y 成为 x 的右孩子\n'
        '    y.left  = T2         // T2 成为 y 的左孩子\n'
        '    // AVL 需更新 y 和 x 的高度（红黑树不需要）\n'
        '    UPDATE_HEIGHT(y)\n'
        '    UPDATE_HEIGHT(x)\n'
        '    return x             // 返回新根\n'
    ) +
    '<br><b>左旋（Left Rotate）— RR场景</b><br>'
    + pseudo(
        'ROTATE_LEFT(x):\n'
        '    y  = x.right         // y 是 x 的右孩子\n'
        '    T2 = y.left          // 保存 y 的左子树（将被挂在 x 下）\n'
        '    y.left   = x         // x 成为 y 的左孩子\n'
        '    x.right  = T2        // T2 成为 x 的右孩子\n'
        '    // AVL 需更新 x 和 y 的高度（红黑树不需要）\n'
        '    UPDATE_HEIGHT(x)\n'
        '    UPDATE_HEIGHT(y)\n'
        '    return y             // 返回新根\n'
    ) +
    '<br><b>T2为什么挂得对？</b> T2中所有值在x和y之间，旋转后T2挂在x.right(左旋)或y.left(右旋)，BST性质不变。'
)

# ═══════════════════════════════════════════════════════════════
# Card 3: BST删除伪代码 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, 'BST删除 — 三种情况伪代码',
    '<b>后继一定没有左孩子，递归删它最多走一层。</b><br><br>'
    + pseudo(
        'DELETE_BST(root, key):\n'
        '    if root == null:\n'
        '        return null\n'
        '\n'
        '    if key < root.val:\n'
        '        root.left = DELETE_BST(root.left, key)\n'
        '    else if key > root.val:\n'
        '        root.right = DELETE_BST(root.right, key)\n'
        '    else:\n'
        '        // ===== 找到待删除节点 =====\n'
        '        // 情况1: 无左子 -&gt; 右子直接顶替\n'
        '        if root.left == null:\n'
        '            return root.right\n'
        '\n'
        '        // 情况2: 无右子 -&gt; 左子直接顶替\n'
        '        if root.right == null:\n'
        '            return root.left\n'
        '\n'
        '        // 情况3: 双子都存在\n'
        '        // 策略A: 找后继，交换值，递归删后继\n'
        '        successor = GET_MIN(root.right)   // 右子树最左节点\n'
        '        root.val = successor.val          // 交换值\n'
        '        root.right = DELETE_BST(root.right, successor.val)\n'
        '\n'
        '        // 策略B: 找前驱，交换值，递归删前驱\n'
        '        // predecessor = GET_MAX(root.left)\n'
        '        // root.val = predecessor.val\n'
        '        // root.left = DELETE_BST(root.left, predecessor.val)\n'
        '\n'
        '        // 策略C: 移动子树（左子树嫁接到后继的左孩子）\n'
        '        // node = root.right\n'
        '        // while node.left != null: node = node.left\n'
        '        // node.left = root.left\n'
        '        // root = root.right\n'
        '\n'
        '    return root\n'
        '\n'
        'GET_MIN(node):\n'
        '    while node.left != null:\n'
        '        node = node.left\n'
        '    return node\n'
    )
)

# ═══════════════════════════════════════════════════════════════
# Card 4: AVL四种旋转场景 (cloze)  — 填空内容必须在text参数（第一个）
# ═══════════════════════════════════════════════════════════════
add_cloze(d,
    'AVL四种旋转场景速查<br><br>'
    'balance = height({{c1::left}}) - height({{c1::right}})<br><br>'
    '<table style="border-collapse:collapse;font-size:16px">'
    '<tr><th>场景</th><th>条件</th><th>操作</th></tr>'
    '<tr><td>LL</td><td>bf &gt; 1 且 bf(left) &ge; 0</td><td>{{c1::右旋(root)}}</td></tr>'
    '<tr><td>RR</td><td>bf &lt; -1 且 bf(right) &le; 0</td><td>{{c1::左旋(root)}}</td></tr>'
    '<tr><td>LR</td><td>bf &gt; 1 且 bf(left) &lt; 0</td><td>先{{c1::左旋(root.left)}}再{{c1::右旋(root)}}</td></tr>'
    '<tr><td>RL</td><td>bf &lt; -1 且 bf(right) &gt; 0</td><td>先{{c1::右旋(root.right)}}再{{c1::左旋(root)}}</td></tr>'
    '</table><br>'
    '记忆法：第二个字母=突出方向，第一个字母=在哪边（LR=Left子树的{{c1::Right}}侧突出）'
)

# ═══════════════════════════════════════════════════════════════
# Card 5: AVL插入伪代码 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, 'AVL插入伪代码',
    '<b>插入后最多1次旋转即可恢复平衡。</b><br><br>'
    + pseudo(
        'HEIGHT(node):\n'
        '    if node == null: return 0\n'
        '    return max(HEIGHT(node.left), HEIGHT(node.right)) + 1\n'
        '\n'
        'BF(node) = HEIGHT(node.left) - HEIGHT(node.right)\n'
        '// BF 属于 {-1, 0, 1} 为平衡，超出需旋转\n'
        '\n'
        'INSERT_AVL(root, key):\n'
        '    // 1. 标准BST插入\n'
        '    if root == null:\n'
        '        return NEW_NODE(key)\n'
        '    if key < root.val:\n'
        '        root.left = INSERT_AVL(root.left, key)\n'
        '    else if key > root.val:\n'
        '        root.right = INSERT_AVL(root.right, key)\n'
        '    else:\n'
        '        return root   // 不允许重复key\n'
        '\n'
        '    // 2. 更新高度\n'
        '    UPDATE_HEIGHT(root)\n'
        '\n'
        '    // 3. 检查平衡并旋转\n'
        '    bf = BF(root)\n'
        '\n'
        '    // LL Case\n'
        '    if bf > 1 and key < root.left.val:\n'
        '        return ROTATE_RIGHT(root)\n'
        '\n'
        '    // RR Case\n'
        '    if bf < -1 and key > root.right.val:\n'
        '        return ROTATE_LEFT(root)\n'
        '\n'
        '    // LR Case\n'
        '    if bf > 1 and key > root.left.val:\n'
        '        root.left = ROTATE_LEFT(root.left)\n'
        '        return ROTATE_RIGHT(root)\n'
        '\n'
        '    // RL Case\n'
        '    if bf < -1 and key < root.right.val:\n'
        '        root.right = ROTATE_RIGHT(root.right)\n'
        '        return ROTATE_LEFT(root)\n'
        '\n'
        '    return root\n'
    )
)

# ═══════════════════════════════════════════════════════════════
# Card 6: AVL删除伪代码 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, 'AVL删除伪代码',
    '<b>与插入的区别：删除可能需向上回溯旋转O(log n)次，因为子树高度-1可能破坏更上层平衡。</b><br><br>'
    + pseudo(
        'DELETE_AVL(root, key):\n'
        '    // 1. 标准BST删除\n'
        '    if root == null: return null\n'
        '    if key < root.val:\n'
        '        root.left = DELETE_AVL(root.left, key)\n'
        '    else if key > root.val:\n'
        '        root.right = DELETE_AVL(root.right, key)\n'
        '    else:\n'
        '        if root.left == null or root.right == null:\n'
        '            temp = root.left if root.left else root.right\n'
        '            root = temp   // 单子或无子，直接顶替\n'
        '        else:\n'
        '            // 双子：找后继，交换值，递归删后继\n'
        '            successor = GET_MIN(root.right)\n'
        '            root.val = successor.val\n'
        '            root.right = DELETE_AVL(root.right, successor.val)\n'
        '\n'
        '    if root == null: return null\n'
        '\n'
        '    // 2. 更新高度\n'
        '    UPDATE_HEIGHT(root)\n'
        '\n'
        '    // 3. 检查平衡并旋转（删除时不能靠key判断，要看子树的BF）\n'
        '    bf = BF(root)\n'
        '\n'
        '    // LL Case\n'
        '    if bf > 1 and BF(root.left) >= 0:\n'
        '        return ROTATE_RIGHT(root)\n'
        '\n'
        '    // LR Case\n'
        '    if bf > 1 and BF(root.left) < 0:\n'
        '        root.left = ROTATE_LEFT(root.left)\n'
        '        return ROTATE_RIGHT(root)\n'
        '\n'
        '    // RR Case\n'
        '    if bf < -1 and BF(root.right) <= 0:\n'
        '        return ROTATE_LEFT(root)\n'
        '\n'
        '    // RL Case\n'
        '    if bf < -1 and BF(root.right) > 0:\n'
        '        root.right = ROTATE_RIGHT(root.right)\n'
        '        return ROTATE_LEFT(root)\n'
        '\n'
        '    return root\n'
    )
)

# ═══════════════════════════════════════════════════════════════
# Card 7: AVL插入 vs 删除区别 (cloze)
# ═══════════════════════════════════════════════════════════════
add_cloze(d,
    'AVL插入 vs 删除的关键区别<br><br>'
    '插入后最多旋转 {{c1::1}} 次即可恢复平衡<br>'
    '删除后可能需要旋转 {{c1::O(log n)}} 次，沿路径向上回溯<br><br>'
    '原因：插入时子树高度+1，转一次就恢复了；<br>'
    '删除时子树高度 {{c1::-1}}，可能破坏更上层的平衡<br><br>'
    '插入判断旋转用 {{c1::key值}} 比较（key &lt; root.left.val），<br>'
    '删除判断旋转用 {{c1::子树的BF}} ，因为key已经不在树里了'
)

# ═══════════════════════════════════════════════════════════════
# Card 8: 红黑树五条性质 (cloze)
# ═══════════════════════════════════════════════════════════════
add_cloze(d,
    '红黑树五条性质（必背）<br><br>'
    '1. 节点是 {{c1::红色}} 或 {{c1::黑色}}<br>'
    '2. 根节点是 {{c1::黑色}}<br>'
    '3. 叶子（NIL）是 {{c1::黑色}}<br>'
    '4. 红节点的两个孩子必须是 {{c1::黑色}}（不能 {{c1::连续两个红}}）<br>'
    '5. 任意节点到所有后代叶子的路径上，{{c1::黑色节点数量相同}}（黑高一致）'
)

# ═══════════════════════════════════════════════════════════════
# Card 9: 红黑树插入伪代码 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, '红黑树插入伪代码',
    '<b>新节点默认红色 → 父黑无事 → 父红则修复（变色为主，旋转兜底）。插入最多2次旋转。</b><br><br>'
    + pseudo(
        'INSERT_RBT(root, key):\n'
        '    // 1. 标准BST插入，新节点着红色\n'
        '    root = BST_INSERT(root, key)\n'
        '    root.color = RED\n'
        '\n'
        '    // 2. 修复红红冲突\n'
        '    root = FIX_INSERT(root, node)\n'
        '    root.color = BLACK              // 保证根始终黑\n'
        '    return root\n'
        '\n'
        'FIX_INSERT(root, node):\n'
        '    while node.parent != null and node.parent.color == RED:\n'
        '        if node.parent == node.parent.parent.left:  // 父是左孩子\n'
        '            uncle = node.parent.parent.right\n'
        '\n'
        '            // Case 1: 叔叔红色 → 变色上推（不旋转）\n'
        '            if uncle != null and uncle.color == RED:\n'
        '                node.parent.color = BLACK\n'
        '                uncle.color = BLACK\n'
        '                node.parent.parent.color = RED\n'
        '                node = node.parent.parent\n'
        '                continue\n'
        '\n'
        '            // Case 2: LR → 先左旋父节点，转为Case 3\n'
        '            if node == node.parent.right:\n'
        '                node = node.parent\n'
        '                ROTATE_LEFT(node)\n'
        '\n'
        '            // Case 3: LL → 父变黑、祖父变红、右旋祖父（终结）\n'
        '            node.parent.color = BLACK\n'
        '            node.parent.parent.color = RED\n'
        '            ROTATE_RIGHT(node.parent.parent)\n'
        '\n'
        '        else:   // 父是祖父的右孩子（镜像对称）\n'
        '            uncle = node.parent.parent.left\n'
        '            if uncle != null and uncle.color == RED:\n'
        '                node.parent.color = BLACK\n'
        '                uncle.color = BLACK\n'
        '                node.parent.parent.color = RED\n'
        '                node = node.parent.parent\n'
        '                continue\n'
        '            if node == node.parent.left:       // RL → 先右旋\n'
        '                node = node.parent\n'
        '                ROTATE_RIGHT(node)\n'
        '            node.parent.color = BLACK          // RR → 左旋终结\n'
        '            node.parent.parent.color = RED\n'
        '            ROTATE_LEFT(node.parent.parent)\n'
        '    return root\n'
    )
)

# ═══════════════════════════════════════════════════════════════
# Card 10: 红黑树删除伪代码 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, '红黑树删除伪代码',
    '<b>先BST删除 → 若删了黑色则从兄弟"借黑"修复。删除最多3次旋转。</b><br><br>'
    + pseudo(
        'DELETE_RBT(root, key):\n'
        '    // 1. BST删除：找到要物理删除的节点\n'
        '    node = FIND(root, key)\n'
        '    // 若双子都存在，找后继替换值，实际删的是后继\n'
        '    if node.left != null and node.right != null:\n'
        '        successor = GET_MIN(node.right)\n'
        '        node.val = successor.val\n'
        '        node = successor   // 后继最多一个子节点\n'
        '\n'
        '    // 2. 记录颜色和孩子\n'
        '    child = node.left if node.left != null else node.right\n'
        '    deletedColor = node.color\n'
        '\n'
        '    // 3. 用child顶替node\n'
        '    REPLACE(node, child)\n'
        '\n'
        '    // 4. 若删除的是黑色节点，需要修复双黑\n'
        '    if deletedColor == BLACK:\n'
        '        if child != null and child.color == RED:\n'
        '            child.color = BLACK    // 红孩子直接变黑补偿\n'
        '        else:\n'
        '            FIX_DELETE(root, child)   // 核心：兄弟借黑\n'
        '\n'
        'FIX_DELETE(root, node):    // node是"双黑"节点\n'
        '    while node != root and (node == null or node.color == BLACK):\n'
        '        if node == node.parent.left:\n'
        '            sibling = node.parent.right\n'
        '\n'
        '            // Case 1: 兄弟红色 → 父变红，兄变黑，左旋父\n'
        '            if sibling.color == RED:\n'
        '                sibling.color = BLACK\n'
        '                node.parent.color = RED\n'
        '                ROTATE_LEFT(node.parent)\n'
        '                sibling = node.parent.right\n'
        '\n'
        '            // Case 2: 兄弟黑+两侄都黑 → 兄弟变红，问题上推\n'
        '            if (sibling.left is null or sibling.left.color == BLACK)\n'
        '               and (sibling.right is null or sibling.right.color == BLACK):\n'
        '                sibling.color = RED\n'
        '                node = node.parent\n'
        '                continue\n'
        '\n'
        '            // Case 3: 兄弟黑+左侄红+右侄黑 → 右旋兄弟 → 转Case4\n'
        '            if sibling.right == null or sibling.right.color == BLACK:\n'
        '                sibling.left.color = BLACK\n'
        '                sibling.color = RED\n'
        '                ROTATE_RIGHT(sibling)\n'
        '                sibling = node.parent.right\n'
        '\n'
        '            // Case 4: 兄弟黑+右侄红 → 兄弟取父色，父黑，右侄黑，左旋父\n'
        '            sibling.color = node.parent.color\n'
        '            node.parent.color = BLACK\n'
        '            sibling.right.color = BLACK\n'
        '            ROTATE_LEFT(node.parent)\n'
        '            node = root   // 修复完成，跳出循环\n'
        '\n'
        '        else:   // node是右孩子（镜像对称）\n'
        '            ...\n'
        '\n'
        '    if node != null:\n'
        '        node.color = BLACK\n'
    )
)

# ═══════════════════════════════════════════════════════════════
# Card 11: 红黑树 vs AVL 对比 (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, '红黑树 vs AVL 工程选型',
    '<table style="border-collapse:collapse;">'
    '<tr><th>维度</th><th>AVL</th><th>红黑树</th></tr>'
    '<tr><td>平衡严格度</td><td>极严格(|bf|&le;1)</td><td>宽松(最长&le;2&times;最短)</td></tr>'
    '<tr><td>查找性能</td><td>略优(树更矮)</td><td>略差</td></tr>'
    '<tr><td>插入代价</td><td>每次维护高度+旋转</td><td>多数变色，少旋转</td></tr>'
    '<tr><td>删除代价</td><td>可能O(log n)次旋转</td><td>&le;3次旋转</td></tr>'
    '<tr><td>插入旋转上限</td><td>1次</td><td>2次</td></tr>'
    '<tr><td>删除旋转上限</td><td>O(log n)次</td><td>3次</td></tr>'
    '<tr><td>适合场景</td><td>查找远多于写</td><td>读写混合/写多</td></tr>'
    '<tr><td>Java实例</td><td>—</td><td>TreeMap, TreeSet, HashMap(JDK8+)</td></tr>'
    '</table>'
)

# ═══════════════════════════════════════════════════════════════
# Card 12: B树插入伪代码（分裂） (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, 'B树插入伪代码（分裂 Split）',
    '<b>m阶B树节点key数范围：[ceil(m/2)-1, m-1]。插入前保证沿途节点不满，满则先分裂再继续。</b><br><br>'
    + pseudo(
        'INSERT_BTREE(root, key):\n'
        '    // 1. 若根已满，先分裂根\n'
        '    if root.keyCount == m - 1:\n'
        '        newRoot = NEW_NODE()\n'
        '        newRoot.isLeaf = false\n'
        '        newRoot.children[0] = root\n'
        '        SPLIT_CHILD(newRoot, 0)      // 分裂旧根\n'
        '        root = newRoot\n'
        '\n'
        '    // 2. 从根开始递归插入（保证沿途不满）\n'
        '    INSERT_NONFULL(root, key)\n'
        '\n'
        'INSERT_NONFULL(node, key):\n'
        '    i = node.keyCount - 1\n'
        '    if node.isLeaf:\n'
        '        // 叶子节点：直接插入（已保证有空间）\n'
        '        while i >= 0 and key < node.keys[i]:\n'
        '            node.keys[i + 1] = node.keys[i]; i--\n'
        '        node.keys[i + 1] = key\n'
        '        node.keyCount++\n'
        '    else:\n'
        '        // 内节点：找到合适的子节点\n'
        '        while i >= 0 and key < node.keys[i]:\n'
        '            i--\n'
        '        i++   // i 现在是目标子节点的索引\n'
        '        // 如果子节点已满，先分裂\n'
        '        if node.children[i].keyCount == m - 1:\n'
        '            SPLIT_CHILD(node, i)\n'
        '            if key > node.keys[i]:\n'
        '                i++   // key 在分裂后的右半部分\n'
        '        INSERT_NONFULL(node.children[i], key)\n'
        '\n'
        'SPLIT_CHILD(parent, index):\n'
        '    // 将 children[index] 一分为二\n'
        '    fullChild = parent.children[index]\n'
        '    newChild  = NEW_NODE()\n'
        '    newChild.isLeaf = fullChild.isLeaf\n'
        '    t = ceil(m / 2)\n'
        '    midKey = fullChild.keys[t - 1]\n'
        '\n'
        '    // 右半部分 key 复制到 newChild\n'
        '    for j = 0 to t-2:\n'
        '        newChild.keys[j] = fullChild.keys[t + j]\n'
        '    newChild.keyCount = t - 1\n'
        '\n'
        '    // 如果不是叶子，子节点指针也要复制\n'
        '    if not fullChild.isLeaf:\n'
        '        for j = 0 to t-1:\n'
        '            newChild.children[j] = fullChild.children[t + j]\n'
        '\n'
        '    fullChild.keyCount = t - 1   // 左半保留 t-1 个 key\n'
        '\n'
        '    // 在 parent 中插入 midKey 和 newChild 指针\n'
        '    for j = parent.keyCount down to index:\n'
        '        parent.children[j + 1] = parent.children[j]\n'
        '    parent.children[index + 1] = newChild\n'
        '    for j = parent.keyCount - 1 down to index:\n'
        '        parent.keys[j + 1] = parent.keys[j]\n'
        '    parent.keys[index] = midKey\n'
        '    parent.keyCount++\n'
    )
)

# ═══════════════════════════════════════════════════════════════
# Card 13: B树删除伪代码（借位/合并） (basic)
# ═══════════════════════════════════════════════════════════════
add_basic(d, 'B树删除伪代码（借位/合并）',
    '<b>删除核心：保证节点key数 &ge; ceil(m/2)-1。下溢时优先借兄弟，借不到则合并。</b><br><br>'
    + pseudo(
        'DELETE_BTREE(node, key):\n'
        '    idx = FIND_KEY_INDEX(node, key)\n'
        '\n'
        '    if idx < node.keyCount and node.keys[idx] == key:\n'
        '        // ====== key在当前节点 ======\n'
        '        if node.isLeaf:\n'
        '            REMOVE_FROM_LEAF(node, idx)          // 叶子直接删\n'
        '        else:\n'
        '            DELETE_FROM_INTERNAL(node, idx)      // 内节点用前驱/后继替换\n'
        '    else:\n'
        '        // ====== key在子树 ======\n'
        '        if node.isLeaf: return   // 没找到\n'
        '        child = node.children[idx]\n'
        '        if child.keyCount == t - 1:   // 将下溢，先填充\n'
        '            FILL_CHILD(node, idx)\n'
        '        if idx > node.keyCount:\n'
        '            idx--  // 合并导致索引变化\n'
        '        DELETE_BTREE(node.children[idx], key)\n'
        '\n'
        'DELETE_FROM_INTERNAL(node, idx):\n'
        '    key = node.keys[idx]\n'
        '    // 策略A: 左子节点key >= t → 用前驱替换\n'
        '    if node.children[idx].keyCount >= t:\n'
        '        predecessor = GET_MAX(node.children[idx])\n'
        '        node.keys[idx] = predecessor\n'
        '        DELETE_BTREE(node.children[idx], predecessor)\n'
        '    // 策略B: 右子节点key >= t → 用后继替换\n'
        '    else if node.children[idx + 1].keyCount >= t:\n'
        '        successor = GET_MIN(node.children[idx + 1])\n'
        '        node.keys[idx] = successor\n'
        '        DELETE_BTREE(node.children[idx + 1], successor)\n'
        '    // 策略C: 左右都不够t → 合并后删\n'
        '    else:\n'
        '        MERGE_CHILDREN(node, idx)\n'
        '        DELETE_BTREE(node.children[idx], key)\n'
        '\n'
        'FILL_CHILD(node, idx):\n'
        '    // 让 children[idx] 的key数 >= t\n'
        '    if idx > 0 and node.children[idx - 1].keyCount >= t:\n'
        '        BORROW_FROM_LEFT(node, idx)    // 左兄弟借\n'
        '    else if idx < node.keyCount and node.children[idx + 1].keyCount >= t:\n'
        '        BORROW_FROM_RIGHT(node, idx)   // 右兄弟借\n'
        '    else:\n'
        '        if idx < node.keyCount:\n'
        '            MERGE_CHILDREN(node, idx)     // 与右兄弟合并\n'
        '        else:\n'
        '            MERGE_CHILDREN(node, idx - 1) // 与左兄弟合并\n'
        '\n'
        'BORROW_FROM_LEFT(node, idx):\n'
        '    child = node.children[idx]\n'
        '    leftSibling = node.children[idx - 1]\n'
        '    // child所有key右移一位\n'
        '    for i = child.keyCount - 1 down to 0:\n'
        '        child.keys[i + 1] = child.keys[i]\n'
        '    if not child.isLeaf:\n'
        '        for i = child.keyCount down to 0:\n'
        '            child.children[i + 1] = child.children[i]\n'
        '    // 父key下放，左兄弟尾key上升\n'
        '    child.keys[0] = node.keys[idx - 1]\n'
        '    node.keys[idx - 1] = leftSibling.keys[leftSibling.keyCount - 1]\n'
        '    if not child.isLeaf:\n'
        '        child.children[0] = leftSibling.children[leftSibling.keyCount]\n'
        '    child.keyCount++\n'
        '    leftSibling.keyCount--\n'
        '\n'
        'MERGE_CHILDREN(node, idx):\n'
        '    // 合并 children[idx] 和 children[idx+1]\n'
        '    left  = node.children[idx]\n'
        '    right = node.children[idx + 1]\n'
        '    // 父key下沉到left中间，right全部拷入\n'
        '    left.keys[left.keyCount] = node.keys[idx]\n'
        '    left.keyCount++\n'
        '    for i = 0 to right.keyCount - 1:\n'
        '        left.keys[left.keyCount + i] = right.keys[i]\n'
        '    if not left.isLeaf:\n'
        '        for i = 0 to right.keyCount:\n'
        '            left.children[left.keyCount + i] = right.children[i]\n'
        '    left.keyCount += right.keyCount\n'
        '    // 父节点删除idx处key和idx+1处child\n'
        '    for i = idx to node.keyCount - 2:\n'
        '        node.keys[i] = node.keys[i + 1]\n'
        '    for i = idx + 1 to node.keyCount - 1:\n'
        '        node.children[i] = node.children[i + 1]\n'
        '    node.keyCount--\n'
    )
)

# ═══════════════════════════════════════════════════════════════
# Card 14: B+树 vs B树差异 (cloze)
# ═══════════════════════════════════════════════════════════════
add_cloze(d,
    'B+树 vs B树关键差异<br><br>'
    '<b>结构差异：</b><br>'
    'B树每个节点存 {{c1::key+data}}<br>'
    'B+树内节点仅存 {{c1::key}}，数据全在 {{c1::叶子}}<br>'
    '叶子间有 {{c1::next链表}} 支持范围扫描<br><br>'
    '<b>分裂差异：</b><br>'
    'B树叶子分裂：左[t-1] | mid上升 | 右[t-1]<br>'
    'B+树叶子分裂：左[t] | mid上升 | 右[t] ← 叶子层 {{c1::保留}} mid<br><br>'
    '<b>删除差异：</b><br>'
    'B+树内节点key删除后可 {{c1::保留作为路标}}（不影响正确性）<br><br>'
    '<b>工程选择：</b><br>'
    '范围查询多 → {{c1::B+树}}（叶子链表O(1)跨页扫描）<br>'
    '等值查询 → B树可能在 {{c1::非叶层直接命中}}<br>'
    'MySQL InnoDB → {{c1::B+树}}，MongoDB → {{c1::B树}}<br>'
    'B+树扇出 {{c1::更高}} → 树更矮 → IO更少'
)

# ═══════════════════════════════════════════════════════════════
# Card 15: 工程实例速记 (cloze)
# ═══════════════════════════════════════════════════════════════
add_cloze(d,
    '工程实例速记：什么产品用什么树<br><br>'
    'Java TreeMap/TreeSet → {{c1::红黑树}}<br>'
    'Java HashMap(JDK8+)链表转树 → {{c1::红黑树}}<br>'
    'Linux CFS完全公平调度器 → {{c1::红黑树}}<br>'
    'Linux epoll事件管理 → {{c1::红黑树}}<br>'
    'MySQL InnoDB索引 → {{c1::B+树}}<br>'
    'PostgreSQL索引 → {{c1::B+树}}<br>'
    'MongoDB索引 → {{c1::B树}}<br>'
    '查找多写入少(内存) → {{c1::AVL}}<br>'
    '读写混合(内存) → {{c1::红黑树}}<br>'
    '磁盘存储+范围查询 → {{c1::B+树}}'
)

# ═══════════════════════════════════════════════════════════════
# Build
# ═══════════════════════════════════════════════════════════════
OUTPUT_DIR = Path(r'D:\claudeProjects\anki\牌组\八股文')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
build(str(OUTPUT_DIR / '数据结构_树结构对比与旋转操作.apkg'))
print('Done: 数据结构_树结构对比与旋转操作.apkg')
