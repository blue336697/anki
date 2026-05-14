"""
Build APKG for 链表 (Linked List). 17 problems, full-code solutions.
"""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# ============================================================
# Deck 0: 链表 原理通识 (deck_id: 1747300500)
# ============================================================

d0 = make_deck(1747300500, '算法::链表::原理通识')

add_basic(d0, '链表::原理通识 | 概述',
    '链表操作核心技巧：<br>'
    '1. 哑节点 (dummy node) — 简化头节点的删除/插入操作<br>'
    '2. 快慢指针 — 找中点、环检测<br>'
    '3. 链表反转 — 双指针迭代 / 递归<br>'
    '4. 递归 — 利用递归栈处理倒序问题')

add_basic(d0, '链表::原理通识 | 哑节点(dummy)何时使用？',
    '1. 需要删除节点时（可能删除头节点）<br>'
    '2. 合并两个链表时<br>'
    '3. 需要返回新链表头时<br>'
    '<br>核心：<code>ListNode dummy = new ListNode(0);</code><br>'
    '<code>dummy.next = head;</code><br>'
    '最后返回 <code>dummy.next</code>')

add_basic(d0, '链表::原理通识 | 快慢指针模式',
    '快指针走两步，慢指针走一步：<br>'
    '1. 找中点：<code>while(fast.next!=null && fast.next.next!=null)</code><br>'
    '2. 环检测：<code>while(fast!=null && fast.next!=null)</code><br>'
    '3. 倒数第k个：快指针先走k步，再和慢指针同步走')

add_cloze(d0, '链表反转—双指针迭代核心：<br>'
    '<code>while(cur != null) {<br>'
    '  tail = cur.next;<br>'
    '  cur.next = {{c1::pre}};<br>'
    '  pre = {{c2::cur}};<br>'
    '  cur = {{c3::tail}};<br>'
    '}<br>return {{c4::pre}};</code>',
    '最后返回pre而非cur，因为cur最终为null')

add_cloze(d0, '链表反转—递归核心：<br>'
    '<code>ListNode cur = reverseList({{c1::head.next}});<br>'
    'head.next.next = {{c2::head}};<br>'
    'head.next = {{c3::null}};<br>'
    'return cur;</code>',
    'cur始终是反转后的新头节点（原尾节点）')

add_basic(d0, '链表::原理通识 | 链表递归思路',
    '1. 终止条件：head==null 或 head.next==null<br>'
    '2. 递：递归调用处理子链表<br>'
    '3. 归：拿到子链表结果后处理当前节点<br>'
    '4. 宏观视角：假设子问题已解决，只关注当前层逻辑')

add_basic(d0, '链表::原理通识 | 常见错误',
    '1. 忘记设 <code>curNode.next = null</code> 导致成环<br>'
    '2. 反转后返回 cur 而非 pre<br>'
    '3. 遍历时用 <code>cur.next != null</code> 会漏掉最后一个节点<br>'
    '4. 修改 <code>head.next</code> 前未保存原引用')


# ============================================================
# 1. 反转链表 (deck_id: 1747300501)
# ============================================================

p = '反转链表'
d = make_deck(1747300501, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '反转一个单链表。'
    + img('34457_k3RMIiHpYvey41CJ.png'))

add_basic(d, make_front(p, '关键技巧'),
    '双指针迭代：pre/cur/tail 三指针<br>'
    '1. 保存 cur.next 到 tail<br>'
    '2. cur.next 指向 pre<br>'
    '3. pre 和 cur 各前进一步<br>'
    '4. 最后返回 pre（原尾节点，现头节点）<br>'
    '<br>递归：<code>head.next.next = head; head.next = null;</code><br>'
    '头插法（不创建新节点）：循环将 head.next 摘下插到头部'
    + img('image.png'))

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 遍历一次<br>'
    '空间：O(1) — 迭代；O(n) — 递归栈')

add_basic(d, make_front(p, '题解(迭代-双指针)'),
    'pre/cur/next 三指针迭代反转。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode reverse(ListNode head) {\n'
        '        if (head == null || head.next == null) {\n'
        '            return head;\n'
        '        }\n'
        '        ListNode preNode = null;\n'
        '        ListNode curNode = head;\n'
        '        ListNode nextNode = null;\n'
        '        while (curNode != null) {\n'
        '            nextNode = curNode.next;\n'
        '            curNode.next = preNode;\n'
        '            preNode = curNode;\n'
        '            curNode = nextNode;\n'
        '        }\n'
        '        return preNode;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(递归)'),
    '递归到最后一个节点，回溯时反转指向。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode reverseList(ListNode head) {\n'
        '        if (head == null || head.next == null)\n'
        '            return head;\n'
        '        ListNode cur = reverseList(head.next);\n'
        '        head.next.next = head;\n'
        '        head.next = null;\n'
        '        return cur;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(头插法)'),
    '不创建新节点，循环将 head.next 摘下插入到头部。<br>'
    + code(
        'public ListNode reverseList(ListNode head) {\n'
        '    if (head == null || head.next == null)\n'
        '        return head;\n'
        '    ListNode cur = head;\n'
        '    while (head.next != null) {\n'
        '        ListNode tail = head.next.next;\n'
        '        head.next.next = cur;\n'
        '        cur = head.next;\n'
        '        head.next = tail;\n'
        '    }\n'
        '    return cur;\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 反转链表II 的区别：II 只反转指定区间 [m,n]<br>'
    '与 K个一组翻转链表 的区别：K个一组是分段反转<br>'
    '与 重排链表 的区别：重排需要先找中点，只反转后半部分')


# ============================================================
# 2. 反转链表 II (deck_id: 1747300502)
# ============================================================

p = '反转链表 II'
d = make_deck(1747300502, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '反转从位置 m 到 n 的链表。1 &lt;= m &lt;= n &lt;= 链表长度。'
    + img('image 1.png'))

add_basic(d, make_front(p, '关键技巧'),
    '1. dummy节点：防止 m=1 时头节点丢失<br>'
    '2. 找到第 m-1 个节点（反转区间的前驱）<br>'
    '3. 对 [m, n] 区间执行标准链表反转<br>'
    '4. 重新连接：区间前驱.next = 反转后头；区间原头.next = 原 n.next')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 最坏遍历到 n<br>'
    '空间：O(1) — 原地反转')

add_basic(d, make_front(p, '题解'),
    'dummy节点找到前驱，反转[m,n]区间后重新连接。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode reverseBetween(ListNode head, int m, int n) {\n'
        '        ListNode res = new ListNode(0);\n'
        '        res.next = head;\n'
        '        ListNode node = res;\n'
        '        // find the node before the reversal segment\n'
        '        for (int i = 1; i &lt; m; i++) {\n'
        '            node = node.next;\n'
        '        }\n'
        '        ListNode nextHead = node.next;\n'
        '        ListNode next = null;\n'
        '        ListNode pre = null;\n'
        '        // reverse from m to n\n'
        '        for (int i = m; i &lt;= n; i++) {\n'
        '            next = nextHead.next;\n'
        '            nextHead.next = pre;\n'
        '            pre = nextHead;\n'
        '            nextHead = next;\n'
        '        }\n'
        '        // reconnect\n'
        '        node.next.next = next;\n'
        '        node.next = pre;\n'
        '        return res.next;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 反转链表 的区别：全反转无需找前驱、无需重连<br>'
    '与 K个一组 的区别：K个一组分段多次反转，II 只反转一段')


# ============================================================
# 3. 合并两个有序链表 (deck_id: 1747300503)
# ============================================================

p = '合并两个有序链表'
d = make_deck(1747300503, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '将两个升序链表合并为一个新的升序链表并返回。新链表由原链表的节点组成。')

add_basic(d, make_front(p, '关键技巧'),
    '迭代：<br>'
    '1. dummy节点连接合并后链表<br>'
    '2. 比较 cur1.val 和 cur2.val，取较小者接到 dummy 后<br>'
    '3. 剩余节点直接拼接<br>'
    '<br>递归：<br>'
    'if list1.val &lt; list2.val: list1.next = merge(list1.next, list2)<br>'
    'else: list2.next = merge(list1, list2.next)')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(m+n) — 两个链表长度之和<br>'
    '空间：O(1) — 迭代；O(m+n) — 递归栈')

add_basic(d, make_front(p, '题解(迭代)'),
    'dummy节点 + 双指针比较，取较小者接入结果链。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode mergeTwoLists(ListNode list1, ListNode list2) {\n'
        '        if (list1 == null && list2 == null)\n'
        '            return null;\n'
        '        ListNode dummy = new ListNode(0);\n'
        '        ListNode res = dummy;\n'
        '        ListNode cur1 = list1;\n'
        '        ListNode cur2 = list2;\n'
        '        while (cur1 != null && cur2 != null) {\n'
        '            if (cur1.val &lt; cur2.val) {\n'
        '                dummy.next = cur1;\n'
        '                cur1 = cur1.next;\n'
        '            } else {\n'
        '                dummy.next = cur2;\n'
        '                cur2 = cur2.next;\n'
        '            }\n'
        '            dummy = dummy.next;\n'
        '        }\n'
        '        dummy.next = cur1 == null ? cur2 : cur1;\n'
        '        return res.next;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(递归)'),
    '递归比较头节点，较小者的next指向子问题结果。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode mergeTwoLists(ListNode list1, ListNode list2) {\n'
        '        if (list1 == null) {\n'
        '            return list2;\n'
        '        }\n'
        '        if (list2 == null) {\n'
        '            return list1;\n'
        '        }\n'
        '        if (list1.val &lt; list2.val) {\n'
        '            list1.next = mergeTwoLists(list1.next, list2);\n'
        '            return list1;\n'
        '        }\n'
        '        list2.next = mergeTwoLists(list1, list2.next);\n'
        '        return list2;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 分隔链表 的区别：分隔是按值x分成大小两组，不要求有序<br>'
    '本题是两个已有序链表的合并（归并排序的merge步骤）')


# ============================================================
# 4. K 个一组翻转链表 (deck_id: 1747300504)
# ============================================================

p = 'K 个一组翻转链表'
d = make_deck(1747300504, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个链表，每 k 个节点一组进行翻转，返回修改后的链表。<br>'
    '如果节点总数不是 k 的整数倍，保持最后剩余节点原有顺序。'
    + img('34457_XsCvOoSeE4HnyUtb.png'))

add_basic(d, make_front(p, '关键技巧'),
    '1. dummy节点 — 防止头节点被反转<br>'
    '2. pre 指向每段反转区间的前驱<br>'
    '3. cur 找每段末尾（走k步），不足k个则break<br>'
    '4. 保存断开后的 next，反转区间，重新连接<br>'
    '5. 更新 pre 和 cur 为反转后末尾（即原区间头 start）')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 每个节点访问两次（找尾+反转）<br>'
    '空间：O(1) — 原地操作')

add_basic(d, make_front(p, '题解'),
    '找到k个节点→断开→反转→重连→更新pre/cur。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode reverseKGroup(ListNode head, int k) {\n'
        '        if (head == null || head.next == null) {\n'
        '            return head;\n'
        '        }\n'
        '        ListNode dummy = new ListNode(0);\n'
        '        dummy.next = head;\n'
        '        ListNode pre = dummy;\n'
        '        ListNode cur = dummy;\n'
        '        while (cur.next != null) {\n'
        '            for (int i = 0; i &lt; k && cur != null; i++) {\n'
        '                cur = cur.next;\n'
        '            }\n'
        '            if (cur == null) {\n'
        '                break;\n'
        '            }\n'
        '            ListNode next = cur.next;\n'
        '            cur.next = null;\n'
        '            ListNode start = pre.next;\n'
        '            pre.next = reverse(start);\n'
        '            start.next = next;\n'
        '            pre = start;\n'
        '            cur = start;\n'
        '        }\n'
        '        return dummy.next;\n'
        '    }\n'
        '\n'
        '    public ListNode reverse(ListNode head) {\n'
        '        if (head == null || head.next == null) {\n'
        '            return head;\n'
        '        }\n'
        '        ListNode pre = null;\n'
        '        ListNode cur = head;\n'
        '        ListNode tail = null;\n'
        '        while (cur != null) {\n'
        '            tail = cur.next;\n'
        '            cur.next = pre;\n'
        '            pre = cur;\n'
        '            cur = tail;\n'
        '        }\n'
        '        return pre;\n'
        '    }\n'
        '}'
    ))


# ============================================================
# 5. 重排链表 (deck_id: 1747300505)
# ============================================================

p = '重排链表'
d = make_deck(1747300505, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定 L0-&gt;L1-&gt;...-&gt;Ln-1-&gt;Ln，重排为 L0-&gt;Ln-&gt;L1-&gt;Ln-1-&gt;L2-&gt;...</br>'
    + img('image 2.png')
    + img('image 3.png'))

add_basic(d, make_front(p, '关键技巧'),
    '方法一（最优O(1)空间）：<br>'
    '1. 快慢指针找中点<br>'
    '2. 反转后半部分链表<br>'
    '3. 交替合并前后两部分<br>'
    '<br>方法二（暴力O(n)空间）：ArrayList存所有节点后双指针重排<br>'
    '<br>方法三：递归（类似暴力，用递归找尾节点）'
    + img('image 4.png'))

add_basic(d, make_front(p, '复杂度'),
    '方法一（中点+反转+合并）：<br>'
    '时间：O(n)<br>'
    '空间：O(1)<br>'
    '<br>方法二（ArrayList）：<br>'
    '时间：O(n)<br>'
    '空间：O(n)')

add_basic(d, make_front(p, '题解(中点+反转+合并)'),
    '三步走：找中点、反转后半、交替合并。O(1)空间最优解。<br>'
    + code(
        'class Solution {\n'
        '    public void reorderList(ListNode head) {\n'
        '        if (head == null || head.next == null || head.next.next == null) {\n'
        '            return;\n'
        '        }\n'
        '        // 1. find middle\n'
        '        ListNode slow = head;\n'
        '        ListNode fast = head;\n'
        '        while (fast.next != null && fast.next.next != null) {\n'
        '            slow = slow.next;\n'
        '            fast = fast.next.next;\n'
        '        }\n'
        '        ListNode newHead = slow.next;\n'
        '        slow.next = null;\n'
        '        // 2. reverse second half\n'
        '        newHead = reverseList(newHead);\n'
        '        // 3. interleave merge\n'
        '        while (newHead != null) {\n'
        '            ListNode temp = newHead.next;\n'
        '            newHead.next = head.next;\n'
        '            head.next = newHead;\n'
        '            head = newHead.next;\n'
        '            newHead = temp;\n'
        '        }\n'
        '    }\n'
        '\n'
        '    private ListNode reverseList(ListNode head) {\n'
        '        if (head == null) {\n'
        '            return null;\n'
        '        }\n'
        '        ListNode tail = head;\n'
        '        head = head.next;\n'
        '        tail.next = null;\n'
        '        while (head != null) {\n'
        '            ListNode temp = head.next;\n'
        '            head.next = tail;\n'
        '            tail = head;\n'
        '            head = temp;\n'
        '        }\n'
        '        return tail;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(暴力-ArrayList)'),
    '将所有节点存入ArrayList，双指针从两端向中间重连。<br>'
    + code(
        'class Solution {\n'
        '    public void reorderList(ListNode head) {\n'
        '        if (head == null)\n'
        '            return;\n'
        '        List&lt;ListNode&gt; list = new ArrayList&lt;&gt;();\n'
        '        while (head != null) {\n'
        '            list.add(head);\n'
        '            head = head.next;\n'
        '        }\n'
        '        int left = 0, right = list.size() - 1;\n'
        '        while (left &lt; right) {\n'
        '            list.get(left).next = list.get(right);\n'
        '            left++;\n'
        '            if (left == right)\n'
        '                break;\n'
        '            list.get(right).next = list.get(left);\n'
        '            right--;\n'
        '        }\n'
        '        list.get(left).next = null;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(递归)'),
    '递归找尾节点并重连，类似暴力但用递归替代尾节点查找。<br>'
    + code(
        'class Solution {\n'
        '    public void reorderList(ListNode head) {\n'
        '        if (head == null || head.next == null || head.next.next == null) {\n'
        '            return;\n'
        '        }\n'
        '        int len = 0;\n'
        '        ListNode h = head;\n'
        '        while (h != null) {\n'
        '            len++;\n'
        '            h = h.next;\n'
        '        }\n'
        '        reorderListHelper(head, len);\n'
        '    }\n'
        '\n'
        '    private ListNode reorderListHelper(ListNode head, int len) {\n'
        '        if (len == 1) {\n'
        '            ListNode outTail = head.next;\n'
        '            head.next = null;\n'
        '            return outTail;\n'
        '        }\n'
        '        if (len == 2) {\n'
        '            ListNode outTail = head.next.next;\n'
        '            head.next.next = null;\n'
        '            return outTail;\n'
        '        }\n'
        '        ListNode tail = reorderListHelper(head.next, len - 2);\n'
        '        ListNode subHead = head.next;\n'
        '        head.next = tail;\n'
        '        ListNode outTail = tail.next;\n'
        '        tail.next = subHead;\n'
        '        return outTail;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 奇偶链表 相似：都是交替取节点重排<br>'
    '但奇偶链表不反转，本题需要先反转后半部分<br>'
    '与 回文链表 相似：都用到找中点+反转后半部分')


# ============================================================
# 6. 删除排序链表中的重复元素 (deck_id: 1747300506)
# ============================================================

p = '删除排序链表中的重复元素'
d = make_deck(1747300506, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '删除排序链表中所有重复元素，使每个元素只出现一次。')

add_basic(d, make_front(p, '关键技巧'),
    '简单遍历：<br>'
    '1. cur从头开始<br>'
    '2. 如果 cur.val == cur.next.val，跳过 cur.next<br>'
    '3. 否则 cur 后移<br>'
    '注意：保留第一个出现的重复元素')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 一次遍历<br>'
    '空间：O(1) — 原地修改')

add_basic(d, make_front(p, '题解'),
    '遍历链表，相等则跳过重复节点(cur.next = cur.next.next)，不等则后移。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode deleteDuplicates(ListNode head) {\n'
        '        if (head == null) {\n'
        '            return head;\n'
        '        }\n'
        '        ListNode cur = head;\n'
        '        while (cur.next != null) {\n'
        '            if (cur.val == cur.next.val) {\n'
        '                cur.next = cur.next.next;\n'
        '            } else {\n'
        '                cur = cur.next;\n'
        '            }\n'
        '        }\n'
        '        return head;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 删除重复元素II 的区别：<br>'
    '本题保留一个重复元素的拷贝，II 全部删除重复元素<br>'
    '本题无需dummy节点（头节点不会被删除）')


# ============================================================
# 7. 删除排序链表中的重复元素 II (deck_id: 1747300507)
# ============================================================

p = '删除排序链表中的重复元素 II'
d = make_deck(1747300507, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '删除排序链表中所有含有重复数字的节点，只保留原始链表中没有重复出现的数字。')

add_basic(d, make_front(p, '关键技巧'),
    '1. dummy节点 — 头节点可能被删除<br>'
    '2. pre 指向已确认不重复的最后一个节点<br>'
    '3. cur 遍历跳过所有值相等的节点，找到右边界<br>'
    '4. 若 pre.next == cur，说明cur没有重复，pre后移<br>'
    '5. 否则 pre.next = cur.next（跳过cur这一段重复的）')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 一次遍历<br>'
    '空间：O(1) — 原地修改')

add_basic(d, make_front(p, '题解(迭代)'),
    'dummy + pre/cur双指针，pre.next==cur说明无重复则pre后移，否则跳过重复区间。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode deleteDuplicates(ListNode head) {\n'
        '        if (head == null)\n'
        '            return null;\n'
        '        ListNode dummy = new ListNode(0);\n'
        '        dummy.next = head;\n'
        '        ListNode pre = dummy;\n'
        '        ListNode cur = head;\n'
        '        while (cur != null) {\n'
        '            while (cur.next != null && cur.val == cur.next.val)\n'
        '                cur = cur.next;\n'
        '            if (pre.next == cur)\n'
        '                pre = cur;\n'
        '            else\n'
        '                pre.next = cur.next;\n'
        '            cur = cur.next;\n'
        '        }\n'
        '        return dummy.next;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(递归)'),
    '递归：遇到重复则跳过全部重复节点，递归处理后续。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode deleteDuplicates(ListNode head) {\n'
        '        if (head == null || head.next == null)\n'
        '            return head;\n'
        '        if (head.val != head.next.val) {\n'
        '            head.next = deleteDuplicates(head.next);\n'
        '        } else {\n'
        '            ListNode temp = head.next.next;\n'
        '            while (temp != null && temp.val == head.val)\n'
        '                temp = temp.next;\n'
        '            return deleteDuplicates(temp);\n'
        '        }\n'
        '        return head;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 删除重复元素 的区别：本题全部删除重复元素，前者保留一个<br>'
    '本题必须用 dummy（头节点可能被删），前者不需要')


# ============================================================
# 8. 两两交换链表中的节点 (deck_id: 1747300508)
# ============================================================

p = '两两交换链表中的节点'
d = make_deck(1747300508, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个链表，两两交换其中相邻的节点，并返回交换后的链表。')

add_basic(d, make_front(p, '关键技巧'),
    '递归三步骤：<br>'
    '1. 终止条件：head==null 或 head.next==null（单节点无法交换）<br>'
    '2. 记录第二个节点 tail = head.next<br>'
    '3. head.next = swapPairs(tail.next) — 递归处理后续<br>'
    '4. tail.next = head — 当前层交换<br>'
    '5. 返回 tail（新头）')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 每两个节点处理一次<br>'
    '空间：O(n) — 递归栈深度 n/2')

add_basic(d, make_front(p, '题解(递归)'),
    '先递归处理后续，再交换当前层两个节点。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode swapPairs(ListNode head) {\n'
        '        if (head == null || head.next == null)\n'
        '            return head;\n'
        '        ListNode tail = head.next;\n'
        '        head.next = swapPairs(tail.next);\n'
        '        tail.next = head;\n'
        '        return tail;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 K个一组 的区别：K个一组泛化为任意k（k=2退化成本题）<br>'
    '本题递归更简洁，K个一组通常用迭代')


# ============================================================
# 9. 旋转链表 (deck_id: 1747300509)
# ============================================================

p = '旋转链表'
d = make_deck(1747300509, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个链表，将链表每个节点向右移动 k 个位置。'
    + img('image 5.png')
    + img('image 6.png'))

add_basic(d, make_front(p, '关键技巧'),
    '1. 先遍历求出链表长度 count<br>'
    '2. k %= count — 消除重复移动<br>'
    '3. 闭合为环：tail.next = head<br>'
    '4. 找到断开位置：第 count - k 个节点<br>'
    '5. 新头 = 断开点的next；断开点.next = null')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 遍历两次（求长度+找断开点）<br>'
    '空间：O(1)')

add_basic(d, make_front(p, '题解'),
    '闭合为环→找新断开点→断开返回新头。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode rotateRight(ListNode head, int k) {\n'
        '        if (head == null || k == 0)\n'
        '            return head;\n'
        '        ListNode tail = head;\n'
        '        int count = 1;\n'
        '        while (tail.next != null) {\n'
        '            tail = tail.next;\n'
        '            count++;\n'
        '        }\n'
        '        k %= count;\n'
        '        ListNode p = head;\n'
        '        for (int i = 0; i &lt; count - k - 1; i++) {\n'
        '            p = p.next;\n'
        '        }\n'
        '        tail.next = head;\n'
        '        head = p.next;\n'
        '        p.next = null;\n'
        '        return head;\n'
        '    }\n'
        '}'
    ))


# ============================================================
# 10. 奇偶链表 (deck_id: 1747300510)
# ============================================================

p = '奇偶链表'
d = make_deck(1747300510, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个单链表，将所有奇数节点和偶数节点分别排在一起。<br>'
    '奇数节点指索引为奇数的节点，偶数节点指索引为偶数的节点。<br>'
    '保持奇数节点和偶数节点的相对顺序。'
    + img('image 7.png'))

add_basic(d, make_front(p, '关键技巧'),
    '1. 分离奇数链表和偶数链表<br>'
    '2. odd指针串联所有奇数索引节点<br>'
    '3. even指针串联所有偶数索引节点<br>'
    '4. evenHead = head.next（偶数链表头保存起来用于拼接）<br>'
    '5. odd.next = evenHead 拼接两链表')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 一次遍历<br>'
    '空间：O(1)')

add_basic(d, make_front(p, '题解'),
    'odd串奇数位，even串偶数位，最后odd尾连even头。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode oddEvenList(ListNode head) {\n'
        '        if (head == null)\n'
        '            return head;\n'
        '        ListNode dummy = head;\n'
        '        ListNode evenHead = head.next;\n'
        '        ListNode even = evenHead;\n'
        '        while (even != null && even.next != null) {\n'
        '            dummy.next = even.next;\n'
        '            dummy = dummy.next;\n'
        '            even.next = dummy.next;\n'
        '            even = even.next;\n'
        '        }\n'
        '        dummy.next = evenHead;\n'
        '        return head;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 排序奇升偶降链表 的关系：<br>'
    '本题 = 奇偶分离；后者 = 奇偶分离 + 反转偶数链表 + 合并两个有序链表')


# ============================================================
# 11. 排序奇升偶降链表 (deck_id: 1747300511)
# ============================================================

p = '排序奇升偶降链表'
d = make_deck(1747300511, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个奇数位升序、偶数位降序的链表，将其重新排序为全升序。<br>'
    '输入: 1-&gt;8-&gt;3-&gt;6-&gt;5-&gt;4-&gt;7-&gt;2-&gt;NULL<br>'
    '输出: 1-&gt;2-&gt;3-&gt;4-&gt;5-&gt;6-&gt;7-&gt;8-&gt;NULL')

add_basic(d, make_front(p, '关键技巧'),
    '组合题 = 奇偶链表 + 反转链表 + 合并两个有序链表<br>'
    '1. 分离奇数链表（升序）和偶数链表（降序）<br>'
    '2. 反转偶数链表（降序→升序）<br>'
    '3. 合并两个升序链表（同 合并两个有序链表）')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 三次遍历（分离+反转+合并）<br>'
    '空间：O(1)')

add_basic(d, make_front(p, '题解'),
    '三步组合：分离奇偶、反转偶数、合并有序。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode oddEvenList(ListNode head) {\n'
        '        if (head == null)\n'
        '            return head;\n'
        '        ListNode dummy = head;\n'
        '        ListNode evenHead = head.next;\n'
        '        ListNode even = evenHead;\n'
        '        while (even != null && even.next != null) {\n'
        '            dummy.next = even.next;\n'
        '            dummy = dummy.next;\n'
        '            even.next = dummy.next;\n'
        '            even = even.next;\n'
        '        }\n'
        '        evenHead = reverse(evenHead);\n'
        '        head = mergeTwoLists(evenHead, head);\n'
        '        return head;\n'
        '    }\n'
        '\n'
        '    public ListNode reverse(ListNode node) {\n'
        '        ListNode pre = null;\n'
        '        ListNode cur = node;\n'
        '        ListNode tail = null;\n'
        '        while (cur != null) {\n'
        '            tail = cur.next;\n'
        '            cur.next = pre;\n'
        '            pre = cur;\n'
        '            cur = tail;\n'
        '        }\n'
        '        return pre;\n'
        '    }\n'
        '\n'
        '    public ListNode mergeTwoLists(ListNode l1, ListNode l2) {\n'
        '        ListNode res = new ListNode(-1);\n'
        '        ListNode preNode = res;\n'
        '        if (l1 == null && l2 == null)\n'
        '            return null;\n'
        '        ListNode temp01 = l1;\n'
        '        ListNode temp02 = l2;\n'
        '        while (temp01 != null && temp02 != null) {\n'
        '            if (temp01.val &lt; temp02.val) {\n'
        '                preNode.next = temp01;\n'
        '                temp01 = temp01.next;\n'
        '            } else {\n'
        '                preNode.next = temp02;\n'
        '                temp02 = temp02.next;\n'
        '            }\n'
        '            preNode = preNode.next;\n'
        '        }\n'
        '        preNode.next = temp01 == null ? temp02 : temp01;\n'
        '        return res.next;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 奇偶链表 的区别：后者只分离不反转不合并<br>'
    '本题集成了三个子问题的解法，是经典的综合题')


# ============================================================
# 12. 分隔链表 (deck_id: 1747300512)
# ============================================================

p = '分隔链表'
d = make_deck(1747300512, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个链表和一个特定值 x，对链表进行分隔，使得所有小于 x 的节点都在大于或等于 x 的节点之前，且保持原有相对顺序。')

add_basic(d, make_front(p, '关键技巧'),
    '1. 创建两个dummy链表：small（存 &lt;x）和 large（存 &gt;=x）<br>'
    '2. 遍历原链表，根据val分配节点到small或large<br>'
    '3. 关键：每次连接后设 curNode.next = null，避免成环<br>'
    '4. smallTail.next = largeHead.next 拼接<br>'
    '5. 返回 smallHead.next')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 一次遍历<br>'
    '空间：O(1) — 原地重连（仅用了两个dummy节点）')

add_basic(d, make_front(p, '题解'),
    '两个dummy分别存大小节点，每次连接后置null防止成环。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode partition(ListNode head, int x) {\n'
        '        ListNode dummy01 = new ListNode(0);\n'
        '        ListNode curNodeDummy01 = dummy01;\n'
        '        ListNode dummy02 = new ListNode(0);\n'
        '        ListNode curNodeDummy02 = dummy02;\n'
        '        while (head != null) {\n'
        '            if (head.val &lt; x) {\n'
        '                curNodeDummy01.next = head;\n'
        '                head = head.next;\n'
        '                curNodeDummy01 = curNodeDummy01.next;\n'
        '                curNodeDummy01.next = null;\n'
        '            } else {\n'
        '                curNodeDummy02.next = head;\n'
        '                head = head.next;\n'
        '                curNodeDummy02 = curNodeDummy02.next;\n'
        '                curNodeDummy02.next = null;\n'
        '            }\n'
        '        }\n'
        '        curNodeDummy01.next = dummy02.next;\n'
        '        return dummy01.next;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 合并两个有序链表 的区别：<br>'
    '本题按值x分成两组保持相对顺序，无需排序<br>'
    '合并两个有序链表是将已排序的两链合并为一个')


# ============================================================
# 13. 链表求和 (deck_id: 1747300513)
# ============================================================

p = '链表求和'
d = make_deck(1747300513, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定两个用链表表示的非负整数，每个节点只存一位数字，数字按逆序存储。<br>'
    '求两数之和，以相同链表形式返回。')

add_basic(d, make_front(p, '关键技巧'),
    '1. 逆序存储（个位在头）：直接从头遍历相加<br>'
    '2. 进位 carry = sum / 10<br>'
    '3. 短链表补0处理<br>'
    '4. 最后如果进位为1，需额外添加节点')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(max(m,n)) — 遍历较长链表长度<br>'
    '空间：O(max(m,n)) — 结果链表')

add_basic(d, make_front(p, '题解'),
    '逐位相加+进位，短链表补0，最后额外处理进位。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {\n'
        '        if (l1 == null || l2 == null)\n'
        '            return null;\n'
        '        ListNode res = new ListNode(0);\n'
        '        ListNode cur = res;\n'
        '        int one = 0;\n'
        '        while (l1 != null || l2 != null) {\n'
        '            int num1 = l1 != null ? l1.val : 0;\n'
        '            int num2 = l2 != null ? l2.val : 0;\n'
        '            cur.next = new ListNode((num1 + num2 + one) % 10);\n'
        '            one = (num1 + num2 + one) / 10;\n'
        '            l1 = l1.next;\n'
        '            l2 = l2.next;\n'
        '            cur = cur.next;\n'
        '        }\n'
        '        if (one == 1)\n'
        '            cur.next = new ListNode(1);\n'
        '        return res.next;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 两数相加II 的区别：<br>'
    '本题数字逆序存储，可直接从低位加<br>'
    'II 是正向存储，需要先反转再相加再反转回来')


# ============================================================
# 14. 两数相加 (deck_id: 1747300514)
# ============================================================

p = '两数相加'
d = make_deck(1747300514, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定两个非空的链表，代表两个非负整数。它们每位数字都是按逆序存储。<br>'
    '将两数相加，以相同链表形式返回和。<br>'
    '(2-&gt;4-&gt;3) 代表 342。'
    + img('image 8.png')
    + img('image 9.png'))

add_basic(d, make_front(p, '关键技巧'),
    '1. dummy节点 + cur指针构建结果链<br>'
    '2. carry 标志位进位<br>'
    '3. 三条件循环：l1!=null || l2!=null || carry!=0<br>'
    '4. 每次取 l1/l2 的 val（null 则取 0），加 carry<br>'
    '5. carry = sum / 10，新节点 = sum % 10')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(max(m,n))<br>'
    '空间：O(max(m,n)) — 结果链表')

add_basic(d, make_front(p, '题解'),
    '逐位相加+进位标志，空位补0，三条件循环确保最后进位也被处理。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {\n'
        '        ListNode prev = new ListNode(0);\n'
        '        int carry = 0;\n'
        '        ListNode cur = prev;\n'
        '        while (l1 != null || l2 != null) {\n'
        '            int x = l1 != null ? l1.val : 0;\n'
        '            int y = l2 != null ? l2.val : 0;\n'
        '            int sum = x + y + carry;\n'
        '            carry = sum / 10;\n'
        '            sum = sum % 10;\n'
        '            cur.next = new ListNode(sum);\n'
        '            cur = cur.next;\n'
        '            if (l1 != null) {\n'
        '                l1 = l1.next;\n'
        '            }\n'
        '            if (l2 != null) {\n'
        '                l2 = l2.next;\n'
        '            }\n'
        '        }\n'
        '        if (carry == 1) {\n'
        '            cur.next = new ListNode(carry);\n'
        '        }\n'
        '        return prev.next;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 链表求和 是同一道题的不同表述，解法相同<br>'
    '与 两数相加II 的区别：II是正向存储需先反转')


# ============================================================
# 15. 两数相加 II (deck_id: 1747300515)
# ============================================================

p = '两数相加 II'
d = make_deck(1747300515, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定两个非空链表代表两个非负整数，最高位在链表头。<br>'
    '求两数之和，以相同链表形式返回。（正序存储）')

add_basic(d, make_front(p, '关键技巧'),
    '正向存储 → 先反转再加再反转：<br>'
    '1. l1 = reverse(l1)<br>'
    '2. l2 = reverse(l2)<br>'
    '3. 调用 两数相加 逻辑相加<br>'
    '4. return reverse(结果)<br>'
    '<br>或用栈：两个栈分别存l1、l2的值，然后逐个弹出相加')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(m+n) — 两次反转+一次相加<br>'
    '空间：O(m+n) — 结果链表（或O(m+n)用栈）')

add_basic(d, make_front(p, '题解'),
    '正序存储→先反转两个链表→低位相加→再反转结果回来。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {\n'
        '        ListNode prev = new ListNode(0);\n'
        '        int carry = 0;\n'
        '        ListNode cur = prev;\n'
        '        l1 = reverse(l1);\n'
        '        l2 = reverse(l2);\n'
        '        while (l1 != null || l2 != null) {\n'
        '            int x = l1 != null ? l1.val : 0;\n'
        '            int y = l2 != null ? l2.val : 0;\n'
        '            int sum = x + y + carry;\n'
        '            carry = sum / 10;\n'
        '            sum = sum % 10;\n'
        '            cur.next = new ListNode(sum);\n'
        '            cur = cur.next;\n'
        '            if (l1 != null) {\n'
        '                l1 = l1.next;\n'
        '            }\n'
        '            if (l2 != null) {\n'
        '                l2 = l2.next;\n'
        '            }\n'
        '        }\n'
        '        if (carry == 1) {\n'
        '            cur.next = new ListNode(carry);\n'
        '        }\n'
        '        return reverse(prev.next);\n'
        '    }\n'
        '\n'
        '    public ListNode reverse(ListNode node) {\n'
        '        ListNode pre = null;\n'
        '        ListNode cur = node;\n'
        '        ListNode tail = null;\n'
        '        while (cur != null) {\n'
        '            tail = cur.next;\n'
        '            cur.next = pre;\n'
        '            pre = cur;\n'
        '            cur = tail;\n'
        '        }\n'
        '        return pre;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 两数相加 的核心区别：本题数字正序存储（高位在头），需先反转<br>'
    '与 链表求和 的关系：链表求和=两数相加（逆序存储）')


# ============================================================
# 16. 删除链表中的节点 (deck_id: 1747300516)
# ============================================================

p = '删除链表中的节点'
d = make_deck(1747300516, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '给定单向链表的头指针和一个要删除的节点的值，定义一个函数删除该节点。<br>'
    '返回删除后的链表的头节点。'
    + img('image 10.png'))

add_basic(d, make_front(p, '关键技巧'),
    '1. 特判：head.val == val → return head.next<br>'
    '2. pre 记录前驱节点，temp 遍历<br>'
    '3. 找到目标节点后：pre.next = temp.next<br>'
    '4. 断开连接：temp.next = null')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 最坏遍历到末尾<br>'
    '空间：O(1)')

add_basic(d, make_front(p, '题解'),
    'pre记录前驱，找到目标后跳过该节点并断开。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode deleteNode(ListNode head, int val) {\n'
        '        if (head == null)\n'
        '            return null;\n'
        '        if (head.val == val)\n'
        '            return head.next;\n'
        '        ListNode temp = head;\n'
        '        ListNode pre = head;\n'
        '        while (temp != null) {\n'
        '            if (temp.val != val) {\n'
        '                pre = temp;\n'
        '                temp = temp.next;\n'
        '            } else\n'
        '                break;\n'
        '        }\n'
        '        pre.next = temp.next;\n'
        '        temp.next = null;\n'
        '        return head;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 删除排序链表中的重复元素 的区别：<br>'
    '本题删除指定值节点，后者按相邻相等删除<br>'
    '与 从尾到头打印链表：两者都是基础链表操作')


# ============================================================
# 17. 从尾到头打印链表 (deck_id: 1747300517)
# ============================================================

p = '从尾到头打印链表'
d = make_deck(1747300517, f'算法::链表::{p}')

add_basic(d, make_front(p, '题干'),
    '输入一个链表的头节点，从尾到头反过来返回每个节点的值（用数组返回）。')

add_basic(d, make_front(p, '关键技巧'),
    '方法一（栈）：<br>'
    '1. 遍历链表，节点值依次入栈<br>'
    '2. 栈中元素依次弹出填入数组<br>'
    '<br>方法二（递归）：<br>'
    '1. 递归到链表末尾<br>'
    '2. 回溯时将值加入结果列表<br>'
    '<br>注意：<code>stack.size()</code> 会随出栈变小，需先记录长度')

add_basic(d, make_front(p, '复杂度'),
    '时间：O(n) — 遍历+出栈<br>'
    '空间：O(n) — 栈中存所有元素')

add_basic(d, make_front(p, '题解(栈)'),
    '栈存放所有节点值，再依次弹出到数组。关键：需先保存栈大小。<br>'
    + code(
        'class Solution {\n'
        '    public int[] reversePrint(ListNode head) {\n'
        '        Deque&lt;Integer&gt; stack = new LinkedList&lt;&gt;();\n'
        '        ListNode curNode = head;\n'
        '        while (curNode != null) {\n'
        '            stack.push(curNode.val);\n'
        '            curNode = curNode.next;\n'
        '        }\n'
        '        int[] res = new int[stack.size()];\n'
        '        int length = stack.size();\n'
        '        for (int i = 0; i &lt; length; i++) {\n'
        '            res[i] = stack.pop();\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '对比'),
    '与 反转链表 的区别：<br>'
    '反转链表是原地修改链表结构<br>'
    '本题不修改链表，只按逆序输出节点值')


# ============================================================
# Export
# ============================================================

if __name__ == '__main__':
    print(build('../../牌组/链表.apkg'))
