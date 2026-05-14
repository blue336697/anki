"""Build APKG for 栈、队列与堆 (Stack, Queue & Heap). 16 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301100, '算法::栈队列堆::原理通识')
add_basic(d0, '单调栈核心思想',
    '单调栈：栈内元素保持单调递增或递减顺序。<br>'
    '递增栈（栈底→栈顶递增）：找下一个更大元素，当新元素 &gt; 栈顶时弹出栈顶并记录结果。<br>'
    '递减栈（栈底→栈顶递减）：找下一个更小元素，当新元素 &lt; 栈顶时弹出栈顶。<br>'
    '核心操作：while(!stack.isEmpty() && nums[stack.peek()] &lt; nums[i]) stack.pop()<br>'
    '应用：每日温度、下一个更大元素 I/II、滑动窗口最大值、移掉K位数字、去除重复字母')
add_basic(d0, '堆/优先队列核心思想',
    '优先队列（PriorityQueue）：基于堆的数据结构，自动维护最值。<br>'
    '小根堆：堆顶最小，new PriorityQueue&lt;&gt;((a,b)-&gt;a.val-b.val)<br>'
    '大根堆：堆顶最大，new PriorityQueue&lt;&gt;((a,b)-&gt;b.val-a.val)<br>'
    '核心操作：offer(E), poll(), peek()<br>'
    '应用：合并K个排序链表、前K个高频元素、数据流中位数')
add_basic(d0, '栈的核心应用场景',
    '1. 括号匹配：左括号入栈，右括号与栈顶匹配后弹出<br>'
    '2. 表达式求值：数字栈+操作符栈，按优先级计算<br>'
    '3. 路径简化：split后遍历，".."弹栈，"."和空跳过<br>'
    '4. 双栈实现队列：push进栈A，pop/peek时A倒入B<br>'
    '5. 最小栈：辅助栈同步维护当前最小值')
add_cloze(d0, '单调递增栈模板（找下一个更大元素）',
    'Stack&lt;Integer&gt; stack = new Stack&lt;&gt;();<br>'
    + 'for(i=0; i&lt;n; i++){<br>'
    + '&nbsp;&nbsp;while(!stack.isEmpty() && nums[stack.peek()] {{c1::&lt;}} nums[i])<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;res[stack.pop()] = {{c2::nums[i]}};<br>'
    + '&nbsp;&nbsp;{{c3::stack.push(i)}};<br>}<br>'
    + '// 栈存索引，栈底→栈顶元素递增。nums[i]&gt;栈顶时，nums[i]就是栈顶元素的"下一个更大"')

# ============================================================
# 1. 有效的括号
# ============================================================
p = '有效的括号'
d = make_deck(1747301101, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个只包括 (、)、[、]、{、} 的字符串 s，判断字符串是否有效。<br>'
    '有效条件：1. 左括号必须用相同类型的右括号闭合；2. 左括号必须以正确的顺序闭合。')
add_cloze(d, make_front(p, '策略'),
    '栈解法：遍历字符串，左括号{{c1::入栈}}，右括号与{{c2::栈顶}}匹配。<br>'
    '优化技巧：遇到左括号时直接{{c3::push对应的右括号}}，匹配时只需判断 ch==stack.pop() 即可。<br>'
    '最终栈为空 → {{c4::完全匹配}}，返回true。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(n)}} — 最坏全部字符入栈')
add_basic(d, make_front(p, '题解(技巧版)'),
    '左括号push对应右括号，右括号直接pop比较。无需Map查表。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isValid(String s) {\n'
        '        if (s == null)\n'
        '            return false;\n'
        '        int len = s.length();\n'
        '        Deque&lt;Character&gt; stack = new LinkedList&lt;&gt;();\n'
        '        for (char ch : s.toCharArray()) {\n'
        '            if (ch == \'(\')\n'
        '                stack.push(\')\');\n'
        '            else if (ch == \'[\')\n'
        '                stack.push(\']\');\n'
        '            else if (ch == \'{\')\n'
        '                stack.push(\'}\');\n'
        '            else if (stack.isEmpty() || ch != stack.pop())\n'
        '                return false;\n'
        '        }\n'
        '        return stack.isEmpty();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '两种写法：<br>1. Map存括号映射（通用但稍冗长）<br>'
    + '2. 左括号直接push对应的右括号（巧妙：匹配时只需 ch==stack.pop()）<br>'
    + '边界优化：奇数长度直接返回false，因为括号不可能配对成功。')

# ============================================================
# 2. 合并K个排序链表
# ============================================================
p = '合并K个排序链表'
d = make_deck(1747301102, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个链表数组，每个链表都已经按升序排列。'
    '将所有链表合并到一个升序链表中，返回合并后的链表。')
add_cloze(d, make_front(p, '策略'),
    '小根堆解法：将所有链表的{{c1::头结点}}加入PriorityQueue。<br>'
    '每次poll出{{c2::最小}}节点接到结果链表尾部，然后将该节点的{{c3::next}}（若不为空）加入堆中。<br>'
    '重复直到堆为空。比较器：(a,b)-&gt;{{c4::a.val-b.val}}（升序=小根堆）。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(N log k)}} — N为总节点数，k为链表数，每次堆操作O(log k)<br>'
    + '空间：{{c2::O(k)}} — 堆中最多k个节点')
add_basic(d, make_front(p, '题解(小根堆)'),
    '比较器 (v1,v2)-&gt;v1.val-v2.val 建立小根堆。每次弹出最小节点后将其next入堆。<br>'
    + code(
        'class Solution {\n'
        '    public ListNode mergeKLists(ListNode[] lists) {\n'
        '        Queue&lt;ListNode&gt; pq = new PriorityQueue&lt;&gt;((v1, v2) -&gt; v1.val - v2.val);\n'
        '        for (ListNode node : lists) {\n'
        '            if (node != null) {\n'
        '                pq.offer(node);\n'
        '            }\n'
        '        }\n'
        '        ListNode dummyHead = new ListNode(0);\n'
        '        ListNode tail = dummyHead;\n'
        '        while (!pq.isEmpty()) {\n'
        '            ListNode minNode = pq.poll();\n'
        '            tail.next = minNode;\n'
        '            tail = minNode;\n'
        '            if (minNode.next != null) {\n'
        '                pq.offer(minNode.next);\n'
        '            }\n'
        '        }\n'
        '        return dummyHead.next;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '两种主要方法：<br>1. 小根堆：PriorityQueue，每次取最小值，O(N log k)<br>'
    + '2. 分治法两两合并：递归拆分成两半再合并，O(N log k)，无需额外堆空间<br>'
    + '核心：始终取当前K个链表头部的最小值。堆方法更直观，分治法空间更优。')

# ============================================================
# 3. 用栈实现队列
# ============================================================
p = '用栈实现队列'
d = make_deck(1747301103, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '请你仅使用两个栈实现先入先出队列。实现 push、pop、peek、empty 操作。')
add_cloze(d, make_front(p, '策略'),
    '双栈法：栈A用于{{c1::push}}，栈B用于{{c2::pop/peek}}。<br>'
    '当pop/peek时，若B为空，则将A中所有元素{{c3::弹出并压入B}}（反转顺序）。<br>'
    '此时B的栈顶就是队首元素。关键：只在B为空时才从A倒入。')
add_cloze(d, make_front(p, '复杂度'),
    'push：{{c1::O(1)}}<br>'
    + 'pop/peek：均摊{{c2::O(1)}}，每个元素最多从A移到B一次<br>'
    + '空间：{{c3::O(n)}}')
add_basic(d, make_front(p, '题解(双栈)'),
    'peek时若B空则将A全部倒入B。pop复用peek后B.pop()。<br>'
    + code(
        'class MyQueue {\n'
        '    private Stack&lt;Integer&gt; A;\n'
        '    private Stack&lt;Integer&gt; B;\n'
        '\n'
        '    public MyQueue() {\n'
        '        A = new Stack&lt;&gt;();\n'
        '        B = new Stack&lt;&gt;();\n'
        '    }\n'
        '\n'
        '    public void push(int x) {\n'
        '        A.push(x);\n'
        '    }\n'
        '\n'
        '    public int pop() {\n'
        '        int peek = peek();\n'
        '        B.pop();\n'
        '        return peek;\n'
        '    }\n'
        '\n'
        '    public int peek() {\n'
        '        if (!B.isEmpty()) return B.peek();\n'
        '        if (A.isEmpty()) return -1;\n'
        '        while (!A.isEmpty()) {\n'
        '            B.push(A.pop());\n'
        '        }\n'
        '        return B.peek();\n'
        '    }\n'
        '\n'
        '    public boolean empty() {\n'
        '        return A.isEmpty() && B.isEmpty();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心：两个栈倒来倒去。push直接入A；pop/peek时将A倒入B反转顺序。<br>'
    + '均摊O(1)分析：每个元素最多从A移到B一次，整体均摊是O(1)。')

# ============================================================
# 4. 滑动窗口最大值
# ============================================================
p = '滑动窗口最大值'
d = make_deck(1747301104, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 nums 和一个大小为 k 的滑动窗口，窗口从数组最左侧移动到最右侧。'
    '每次只能看到窗口内的 k 个数字。返回每个窗口中的最大值。' + img('image.png'))
add_cloze(d, make_front(p, '策略'),
    '单调递减队列（Deque）：队列从队首到队尾{{c1::递减}}（队首最大）。<br>'
    '入队：新元素与队尾比较，若队尾{{c2::&lt;=}}新元素则弹出队尾，直到满足递减。<br>'
    '出队：队首元素下标{{c3::不在窗口内}}（&lt;= i-k）时从队首弹出。<br>'
    '队首始终是当前窗口的{{c4::最大值}}。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个元素入队出队各一次<br>空间：{{c2::O(k)}} — 队列最多k个元素')
add_basic(d, make_front(p, '题解(单调队列)'),
    '队列存下标。队尾维护递减：新元素&gt;=队尾时弹出。队首超出窗口左边界时弹出。<br>'
    + code(
        'class Solution {\n'
        '    public int[] maxSlidingWindow(int[] nums, int k) {\n'
        '        if (nums == null || nums.length &lt; 2)\n'
        '            return nums;\n'
        '        int[] res = new int[nums.length - k + 1];\n'
        '        Deque&lt;Integer&gt; window = new LinkedList&lt;&gt;();\n'
        '        for (int i = 0; i &lt; nums.length; i++) {\n'
        '            while (!window.isEmpty() && nums[window.peekLast()] &lt;= nums[i])\n'
        '                window.pollLast();\n'
        '            window.addLast(i);\n'
        '            if (window.peek() &lt;= i - k)\n'
        '                window.poll();\n'
        '            if (i + 1 &gt;= k)\n'
        '                res[i - k + 1] = nums[window.peek()];\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '单调递减队列是本题的核心数据结构。<br>'
    + '队列中存的是数组下标而非数值，便于判断窗口边界。<br>'
    + '队首是最大值，队尾维护递减约束。每个元素至多入队出队一次 = O(n)。<br>'
    + '与单调栈的区别：双端队列可以同时从两端操作。')

# ============================================================
# 5. 最长有效括号
# ============================================================
p = '最长有效括号'
d = make_deck(1747301105, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个只包含 ( 和 ) 的字符串，找出最长有效（格式正确且连续）括号子串的长度。'
    + img('image 1.png'))
add_cloze(d, make_front(p, '策略'),
    '栈存下标法：栈底始终保持{{c1::最后一个未匹配的右括号下标}}（初始为-1）。<br>'
    '遇到 ( ：将其{{c2::下标入栈}}。<br>'
    '遇到 ) ：先{{c3::pop()}}，若栈为空则push当前下标（新的分割点），否则计算长度={{c4::i - stack.peek()}}。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(n)}} — 栈空间')
add_basic(d, make_front(p, '题解(栈存下标)'),
    '栈底始终是最后一个无法匹配的)位置。遇到)时弹栈后计算 i-stack.peek()。<br>'
    + code(
        'class Solution {\n'
        '    public int longestValidParentheses(String s) {\n'
        '        if (s == "")\n'
        '            return 0;\n'
        '        int len = s.length();\n'
        '        Deque&lt;Integer&gt; stack = new LinkedList&lt;&gt;();\n'
        '        stack.push(-1);\n'
        '        int res = 0;\n'
        '        for (int i = 0; i &lt; len; i++) {\n'
        '            if (s.charAt(i) == \'(\')\n'
        '                stack.push(i);\n'
        '            else {\n'
        '                stack.pop();\n'
        '                if (stack.isEmpty())\n'
        '                    stack.push(i);\n'
        '                else\n'
        '                    res = Math.max(res, i - stack.peek());\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '栈底存的是"最后一个未被匹配的右括号的索引"，作为有效子串的起始边界。<br>'
    + '初始化push(-1)是核心技巧：将-1视为虚拟的"未匹配右括号"，处理从头开始的有效子串。<br>'
    + '每次匹配成功时，i - stack.peek() 就是当前有效子串长度。')

# ============================================================
# 6. 最小栈
# ============================================================
p = '最小栈'
d = make_deck(1747301106, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '设计一个支持 push、pop、top 操作，并能在常数时间内检索到最小元素的栈。'
    + img('image 2.png'))
add_cloze(d, make_front(p, '策略'),
    '辅助栈法：维护两个栈——{{c1::数据栈 xStack}} 和 {{c2::最小值栈 minStack}}。<br>'
    'push时：数据栈直接push；minStack push{{c3::min(minStack.peek(), x)}}。<br>'
    'pop时：两个栈{{c4::同时pop}}。getMin() 返回 minStack.peek()。')
add_cloze(d, make_front(p, '复杂度'),
    '所有操作：时间{{c1::O(1)}}<br>空间：{{c2::O(n)}} — 两个栈')
add_basic(d, make_front(p, '题解(辅助栈)'),
    'minStack与xStack同步push/pop，minStack栈顶始终是当前所有元素的最小值。<br>'
    + code(
        'class MinStack {\n'
        '    Deque&lt;Integer&gt; xStack;\n'
        '    Deque&lt;Integer&gt; minStack;\n'
        '\n'
        '    public MinStack() {\n'
        '        xStack = new LinkedList&lt;Integer&gt;();\n'
        '        minStack = new LinkedList&lt;Integer&gt;();\n'
        '        minStack.push(Integer.MAX_VALUE);\n'
        '    }\n'
        '\n'
        '    public void push(int x) {\n'
        '        xStack.push(x);\n'
        '        minStack.push(Math.min(minStack.peek(), x));\n'
        '    }\n'
        '\n'
        '    public void pop() {\n'
        '        xStack.pop();\n'
        '        minStack.pop();\n'
        '    }\n'
        '\n'
        '    public int top() {\n'
        '        return xStack.peek();\n'
        '    }\n'
        '\n'
        '    public int getMin() {\n'
        '        return minStack.peek();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心：用辅助栈同步维护每个状态下的最小值。<br>'
    + '初始化push Integer.MAX_VALUE 确保第一次比较不出错。<br>'
    + '可优化：只在minStack中push<=当前min的值来节省空间，但pop时需要额外判断。')

# ============================================================
# 7. 基本计算器 II
# ============================================================
p = '基本计算器 II'
d = make_deck(1747301107, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '实现一个基本计算器来计算简单的字符串表达式。支持 +、-、*、/、^、%、(、)。'
    '整数除法仅保留整数部分。')
add_cloze(d, make_front(p, '策略'),
    '双栈法：{{c1::数字栈 nums}} + {{c2::操作符栈 ops}}。<br>'
    '遇到数字：取出完整数字入nums。<br>'
    '遇到 (：直接入ops。<br>'
    '遇到 )：不断计算直到遇到 ( 并弹出。<br>'
    '遇到运算符：将栈内{{c3::优先级高于或等于}}当前运算符的先算掉，再入栈。<br>'
    '最终将栈内剩余运算符全部计算。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个字符处理一次<br>空间：{{c2::O(n)}} — 两个栈')
add_basic(d, make_front(p, '题解(核心逻辑)'),
    '优先级比较是核心：&gt;= 确保同优先级的从左到右计算。前置补0处理一元运算符。<br>'
    + code(
        'class Solution {\n'
        '    Map&lt;Character, Integer&gt; map = new HashMap&lt;&gt;() {{\n'
        '        put(\'-\', 1);\n'
        '        put(\'+\', 1);\n'
        '        put(\'*\', 2);\n'
        '        put(\'/\', 2);\n'
        '        put(\'%\', 2);\n'
        '        put(\'^\', 3);\n'
        '    }};\n'
        '\n'
        '    public int calculate(String s) {\n'
        '        s = s.replaceAll(" ", "");\n'
        '        char[] cs = s.toCharArray();\n'
        '        int n = s.length();\n'
        '        Deque&lt;Integer&gt; nums = new ArrayDeque&lt;&gt;();\n'
        '        nums.addLast(0);\n'
        '        Deque&lt;Character&gt; ops = new ArrayDeque&lt;&gt;();\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            char c = cs[i];\n'
        '            if (c == \'(\') {\n'
        '                ops.addLast(c);\n'
        '            } else if (c == \')\') {\n'
        '                while (!ops.isEmpty()) {\n'
        '                    if (ops.peekLast() != \'(\') {\n'
        '                        calc(nums, ops);\n'
        '                    } else {\n'
        '                        ops.pollLast();\n'
        '                        break;\n'
        '                    }\n'
        '                }\n'
        '            } else {\n'
        '                if (isNumber(c)) {\n'
        '                    int u = 0;\n'
        '                    int j = i;\n'
        '                    while (j &lt; n && isNumber(cs[j]))\n'
        '                        u = u * 10 + (cs[j++] - \'0\');\n'
        '                    nums.addLast(u);\n'
        '                    i = j - 1;\n'
        '                } else {\n'
        '                    if (i &gt; 0 && (cs[i - 1] == \'(\' || cs[i - 1] == \'+\' || cs[i - 1] == \'-\')) {\n'
        '                        nums.addLast(0);\n'
        '                    }\n'
        '                    while (!ops.isEmpty() && ops.peekLast() != \'(\') {\n'
        '                        char prev = ops.peekLast();\n'
        '                        if (map.get(prev) &gt;= map.get(c)) {\n'
        '                            calc(nums, ops);\n'
        '                        } else {\n'
        '                            break;\n'
        '                        }\n'
        '                    }\n'
        '                    ops.addLast(c);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        while (!ops.isEmpty()) calc(nums, ops);\n'
        '        return nums.peekLast();\n'
        '    }\n'
        '\n'
        '    void calc(Deque&lt;Integer&gt; nums, Deque&lt;Character&gt; ops) {\n'
        '        if (nums.isEmpty() || nums.size() &lt; 2) return;\n'
        '        if (ops.isEmpty()) return;\n'
        '        int b = nums.pollLast(), a = nums.pollLast();\n'
        '        char op = ops.pollLast();\n'
        '        int ans = 0;\n'
        '        if (op == \'+\') ans = a + b;\n'
        '        else if (op == \'-\') ans = a - b;\n'
        '        else if (op == \'*\') ans = a * b;\n'
        '        else if (op == \'/\') ans = a / b;\n'
        '        else if (op == \'^\') ans = (int)Math.pow(a, b);\n'
        '        else if (op == \'%\') ans = a % b;\n'
        '        nums.addLast(ans);\n'
        '    }\n'
        '\n'
        '    boolean isNumber(char c) {\n'
        '        return Character.isDigit(c);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '双栈法处理表达式求值是经典模式。<br>'
    + '核心要点：1. 运算符优先级映射  2. 栈内优先级>=当前时立即计算  3. 括号内的独立计算<br>'
    + '前置补0技巧：将 (- 变为 (0-，(+ 变为 (0+)，统一处理负数情况。<br>'
    + 'calc函数：弹出两个数字和一个操作符，计算结果压回nums。')

# ============================================================
# 8. 每日温度
# ============================================================
p = '每日温度'
d = make_deck(1747301108, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 temperatures，表示每天的温度。'
    '返回一个数组 answer，其中 answer[i] 表示对于第i天，下一个更高温度出现在几天后。'
    '如果之后都不会升高，answer[i] = 0。')
add_cloze(d, make_front(p, '策略'),
    '单调递减栈：栈内存储{{c1::下标}}，对应温度从栈底到栈顶{{c2::递减}}。<br>'
    '遍历时，若当前温度 &gt; 栈顶温度，说明找到了{{c3::更高温度}}。<br>'
    '此时弹出栈顶，结果 = {{c4::i - stack.pop()}}（天数差）。<br>'
    '处理完后将当前下标入栈。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个元素最多入栈出栈一次<br>空间：{{c2::O(n)}} — 栈空间')
add_basic(d, make_front(p, '题解(单调栈)'),
    '栈内温度递减，遇到更高温度时弹出并计算天数差。默认值为0（数组初始化）。<br>'
    + code(
        'class Solution {\n'
        '    public int[] dailyTemperatures(int[] temperatures) {\n'
        '        Stack&lt;Integer&gt; stack = new Stack&lt;&gt;();\n'
        '        int[] res = new int[temperatures.length];\n'
        '        for (int i = 0; i &lt; res.length; i++) {\n'
        '            while (!stack.isEmpty() && temperatures[stack.peek()] &lt; temperatures[i]) {\n'
        '                int temp = stack.pop();\n'
        '                res[temp] = i - temp;\n'
        '            }\n'
        '            stack.push(i);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '单调递减栈的经典应用。<br>'
    + '核心：栈中存的是下标，栈内对应温度严格递减，当前元素大于栈顶时即为栈顶元素的下一个更高温度。<br>'
    + '数组默认初始化为0，未找到更高温度的元素自然保持0。')

# ============================================================
# 9. 移掉K位数字
# ============================================================
p = '移掉K位数字'
d = make_deck(1747301109, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个以字符串表示的非负整数 num，移除这个数中的 k 位数字，使得剩下的数字最小。'
    + img('image 3.png') + img('image 4.png') + img('image 5.png') + img('image 6.png') + img('image 7.png'))
add_cloze(d, make_front(p, '策略'),
    '单调递增栈（贪心）：维护数字{{c1::递增}}序列，使高位尽可能小。<br>'
    '遍历时，当栈顶 &gt; 当前数字且还有移除名额(k&gt;0)时，{{c2::弹出栈顶}}，k--。<br>'
    '关键处理：<br>'
    '1. 当前字符为0且栈为空时{{c3::跳过}}（去除前导零）<br>'
    '2. 遍历完若k仍有剩余，从{{c4::末尾}}移除剩余k位')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个字符最多入栈出栈一次<br>空间：{{c2::O(n)}} — StringBuilder')
add_basic(d, make_front(p, '题解(单调栈)'),
    '贪心+单调栈：当前字符小于栈顶时移除栈顶。遍历完若k&gt;0从末尾移除。<br>'
    + code(
        'class solution {\n'
        '    public String removeKdigits(String num, int k) {\n'
        '        if (num.length() == k)\n'
        '            return "0";\n'
        '        StringBuilder stack = new StringBuilder();\n'
        '        for (int i = 0; i &lt; num.length(); i++) {\n'
        '            char ch = num.charAt(i);\n'
        '            while (k &gt; 0 && stack.length() != 0\n'
        '                && stack.charAt(stack.length() - 1) &gt; ch) {\n'
        '                stack.setLength(stack.length() - 1);\n'
        '                k--;\n'
        '            }\n'
        '            if (ch == \'0\' && stack.length() == 0)\n'
        '                continue;\n'
        '            stack.append(ch);\n'
        '        }\n'
        '        String res = stack.substring(0, stack.length() - k &lt; 1 ? 0 : stack.length() - k).toString();\n'
        '        return res.length() == 0 ? "0" : res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心贪心思想：高位数字越小，整体数字越小。<br>'
    + '维护递增栈就是保证越靠前的数字越小。<br>'
    + '边界处理：k有剩余说明数字本身已经递增，从末尾移除；结果为空返回"0"；去除前导零。')

# ============================================================
# 10. 用两个栈实现队列
# ============================================================
p = '用两个栈实现队列'
d = make_deck(1747301110, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '用两个栈实现一个队列。实现 appendTail 和 deleteHead 两个功能。')
add_cloze(d, make_front(p, '策略'),
    '栈01用于{{c1::入队}}，栈02用于{{c2::出队}}。<br>'
    'deleteHead时：若栈02非空，直接{{c3::pop}}；若栈02为空，将栈01全部{{c4::倒入栈02}}再pop。<br>'
    '两栈全空时返回-1。')
add_cloze(d, make_front(p, '复杂度'),
    'appendTail：{{c1::O(1)}}<br>deleteHead：均摊{{c2::O(1)}}<br>空间：{{c3::O(n)}}')
add_basic(d, make_front(p, '题解'),
    '与LeetCode 232 用栈实现队列思路一致：入队栈+出队栈。<br>'
    + code(
        'class CQueue {\n'
        '    Deque&lt;Integer&gt; stack01;\n'
        '    Deque&lt;Integer&gt; stack02;\n'
        '\n'
        '    public CQueue() {\n'
        '        stack01 = new LinkedList&lt;&gt;();\n'
        '        stack02 = new LinkedList&lt;&gt;();\n'
        '    }\n'
        '\n'
        '    public void appendTail(int value) {\n'
        '        stack01.add(value);\n'
        '    }\n'
        '\n'
        '    public int deleteHead() {\n'
        '        if (stack02.isEmpty()) {\n'
        '            if (stack01.isEmpty())\n'
        '                return -1;\n'
        '            while (!stack01.isEmpty())\n'
        '                stack02.add(stack01.pop());\n'
        '            return stack02.pop();\n'
        '        } else\n'
        '            return stack02.pop();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '与 LeetCode 232 本质相同。<br>'
    + '剑指Offer版用了Deque而非Stack，其余逻辑一致。<br>'
    + '核心：只在deleteHead且栈02为空时才从栈01倒数据，保证均摊O(1)。')

# ============================================================
# 11. 有效的括号字符串
# ============================================================
p = '有效的括号字符串'
d = make_deck(1747301111, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个只包含三种字符的字符串：(、)、*，判断是否为有效字符串。<br>'
    '* 可以被视为 ) 或 ( 或空字符串。')
add_cloze(d, make_front(p, '策略(双栈法)'),
    '双栈法：left栈存{{c1::( }}下标，star栈存{{c2::* }}下标。<br>'
    '遇到 ) ：优先用{{c3::left栈弹栈}}匹配，否则用star栈弹栈，都为空则false。<br>'
    '遍历完后处理多余 ( ：比较下标，star必须在left{{c4::后面}}才能匹配（*变)）。')
add_cloze(d, make_front(p, '复杂度'),
    '双栈法：时间{{c1::O(n)}}，空间{{c2::O(n)}}<br>'
    + '上下界法：时间{{c3::O(n)}}，空间{{c4::O(1)}}')
add_basic(d, make_front(p, '题解(双栈)'),
    '注意最后while：比较*和(的位置，*必须在左括号后面才能充当)。<br>'
    + code(
        'class Solution {\n'
        '    public boolean checkValidString(String s) {\n'
        '        Stack&lt;Integer&gt; left = new Stack&lt;&gt;();\n'
        '        Stack&lt;Integer&gt; star = new Stack&lt;&gt;();\n'
        '        for (int i = 0; i &lt; s.length(); i++) {\n'
        '            char ch = s.charAt(i);\n'
        '            if (ch == \'(\')\n'
        '                left.push(i);\n'
        '            else if (ch == \'*\')\n'
        '                star.push(i);\n'
        '            else {\n'
        '                if (!left.isEmpty()) {\n'
        '                    left.pop();\n'
        '                } else if (!star.isEmpty())\n'
        '                    star.pop();\n'
        '                else\n'
        '                    return false;\n'
        '            }\n'
        '        }\n'
        '        while (!left.isEmpty()) {\n'
        '            if (star.isEmpty())\n'
        '                return false;\n'
        '            int indexLeft = left.pop();\n'
        '            int indexStar = star.pop();\n'
        '            if (indexStar &lt; indexLeft)\n'
        '                return false;\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(上下界法)'),
    '*可以是(、)或空，所以左括号数量在一个范围内。l=0表示可以匹配完。<br>'
    + code(
        'class Solution {\n'
        '    public boolean checkValidString(String s) {\n'
        '        int l = 0, r = 0;\n'
        '        for (char c : s.toCharArray()) {\n'
        '            if (c == \'(\') {\n'
        '                l++; r++;\n'
        '            } else if (c == \')\') {\n'
        '                l--; r--;\n'
        '            } else {\n'
        '                l--; r++;\n'
        '            }\n'
        '            l = Math.max(l, 0);\n'
        '            if (l &gt; r) return false;\n'
        '        }\n'
        '        return l == 0;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '两种解法：<br>1. 双栈法（通用）：记录下标位置，最后验证*是否在(后面<br>'
    + '2. 上下界法（巧妙）：维护左括号可能的数量范围[l, r]，O(1)空间<br>'
    + 'l是左括号最少数量，r是左括号最多数量，最终需要l==0。')

# ============================================================
# 12. 去除重复字母
# ============================================================
p = '去除重复字母'
d = make_deck(1747301112, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个字符串 s，请你去除字符串中重复的字母，使得每个字母只出现一次。'
    '需保证返回结果的字典序最小（要求不能打乱其他字符的相对位置）。')
add_cloze(d, make_front(p, '策略'),
    '单调递增栈 + 贪心：维护{{c1::字典序递增}}的字符序列。<br>'
    '遍历时，若当前字符已在栈中则{{c2::跳过}}。<br>'
    '否则：当栈非空、栈顶 &gt; 当前字符、且栈顶字符{{c3::在后面还会出现}}时，弹出栈顶。<br>'
    '最后将当前字符入栈。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个字符最多入栈出栈一次，contains操作O(26)<br>空间：{{c2::O(1)}} — 最多26个字符')
add_basic(d, make_front(p, '题解(单调栈)'),
    's.indexOf(stack.peek(),i)!=-1 表示栈顶字符在后面还会出现，可安全弹出。<br>'
    + code(
        'class Solution {\n'
        '    public String removeDuplicateLetters(String s) {\n'
        '        if (s == null)\n'
        '            return "";\n'
        '        Deque&lt;Character&gt; stack = new LinkedList&lt;&gt;();\n'
        '        for (int i = 0; i &lt; s.length(); i++) {\n'
        '            char ch = s.charAt(i);\n'
        '            if (stack.contains(ch))\n'
        '                continue;\n'
        '            while (!stack.isEmpty() && stack.peek() &gt; ch &&\n'
        '                    s.indexOf(stack.peek(), i) != -1) {\n'
        '                stack.pop();\n'
        '            }\n'
        '            stack.push(ch);\n'
        '        }\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        int len = stack.size();\n'
        '        for (int i = 0; i &lt; len; i++) {\n'
        '            sb.append(stack.pollLast());\n'
        '        }\n'
        '        return sb.toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '与"移掉K位数字"类似，都是维护递增序列的贪心。<br>'
    + '核心区别：1. 已存在的字符跳过  2. 弹出条件需确认栈顶字符后续还会出现<br>'
    + '字典序最小 = 保证高位字符尽可能小。三个条件缺一不可：栈非空、栈顶更大、栈顶字符后续还有。')

# ============================================================
# 13. 简化路径
# ============================================================
p = '简化路径'
d = make_deck(1747301113, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个 Unix 风格的绝对路径 path，请将其转化为简化的规范路径。<br>'
    '规则：多个连续斜杠用一个斜杠替代；. 表示当前目录；.. 表示上一级目录。')
add_cloze(d, make_front(p, '策略'),
    '栈解法：用 / 分割路径，遍历每个部分：<br>'
    '遇到 "" 或 "." → {{c1::跳过}}<br>'
    '遇到 ".." → 若栈非空则{{c2::pop()}}（返回上级）<br>'
    '其他 → {{c3::push入栈}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — split + 遍历<br>空间：{{c2::O(n)}} — 栈空间')
add_basic(d, make_front(p, '题解(栈)'),
    'split后过滤空和.，..向上弹栈。注意最后结果为空则返回根目录"/"。<br>'
    + code(
        'class Solution {\n'
        '    public String simplifyPath(String path) {\n'
        '        if (path == null)\n'
        '            return null;\n'
        '        String[] s = path.split("/");\n'
        '        Stack&lt;String&gt; stack = new Stack&lt;&gt;();\n'
        '        for (String item : s) {\n'
        '            if (item.equals("") || item.equals("."))\n'
        '                continue;\n'
        '            if (item.equals("..")) {\n'
        '                if (!stack.isEmpty())\n'
        '                    stack.pop();\n'
        '            } else {\n'
        '                stack.push(item);\n'
        '            }\n'
        '        }\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        while (!stack.isEmpty()) {\n'
        '            sb.append("/");\n'
        '            sb.append(stack.pop());\n'
        '        }\n'
        '        return sb.length() == 0 ? "/" : sb.toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '本质是目录层级模拟：.忽略，..回退，其他进入。<br>'
    + '注意最后拼接顺序：栈是后进先出，pop顺序与push顺序相反。<br>'
    + '严谨的做法应用pollLast从栈底取，或使用LinkedList+addLast/pollLast模拟队列。')

# ============================================================
# 14. 下一个更大元素 II
# ============================================================
p = '下一个更大元素 II'
d = make_deck(1747301114, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个循环数组 nums，返回数组中每个元素的下一个更大的元素。<br>'
    '如果不存在则输出 -1。循环数组：数组的最后一个元素的下一个元素是数组的第一个元素。'
    + img('image 8.png'))
add_cloze(d, make_front(p, '策略'),
    '单调递增栈 + 循环数组：遍历{{c1::2*n}}次（模拟循环）。<br>'
    '用 {{c2::i % n}} 访问数组元素，实现循环遍历。<br>'
    '栈内存储下标，栈底→栈顶对应元素{{c3::递减}}。<br>'
    '当 i &lt; n 时才将下标入栈（避免重复入栈）。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 遍历2n次，每个元素入栈出栈各一次<br>空间：{{c2::O(n)}} — 栈空间')
add_basic(d, make_front(p, '题解(单调栈+循环)'),
    '核心：遍历2n次模拟循环，i%n下标。i&lt;n时才入栈防止重复。<br>'
    + code(
        'class Solution {\n'
        '    public int[] nextGreaterElements(int[] nums) {\n'
        '        int n = nums.length;\n'
        '        int[] res = new int[n];\n'
        '        Arrays.fill(res, -1);\n'
        '        Stack&lt;Integer&gt; stack = new Stack&lt;&gt;();\n'
        '        for (int i = 0; i &lt; n * 2; i++) {\n'
        '            while (!stack.isEmpty() && nums[i % n] &gt; nums[stack.peek()])\n'
        '                res[stack.pop()] = nums[i % n];\n'
        '            if (i &lt; n)\n'
        '                stack.push(i % n);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '循环数组的处理技巧：遍历2n次，用 i%n 访问。<br>'
    + '第一遍 (0~n-1)：正常入栈处理<br>'
    + '第二遍 (n~2n-1)：只处理栈中剩余元素，不入栈（因为都已入过）<br>'
    + '用 Arrays.fill(res, -1) 初始化，未找到的就保持 -1。')

# ============================================================
# 15. 下一个更大元素 III
# ============================================================
p = '下一个更大元素 III'
d = make_deck(1747301115, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个32位正整数 n，找出符合32位整数范围的下一个更大的元素。<br>'
    '如果不存在这样的整数，返回 -1。本质是求下一个排列。')
add_cloze(d, make_front(p, '策略'),
    '下一个排列算法：<br>'
    '1. 从右向左找第一个{{c1::升序对}} (chars[i] &gt; chars[i-1])<br>'
    '2. 将 i-1 之后的子数组{{c2::排序}}（升序）<br>'
    '3. 在排序后的子数组中找第一个{{c3::大于}} chars[i-1] 的数并交换<br>'
    '4. 检查结果是否超出{{c4::Integer.MAX_VALUE}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n log n)}} — 主要是排序开销<br>空间：{{c2::O(n)}} — 字符数组')
add_basic(d, make_front(p, '题解(下一个排列)'),
    '从右找第一个升序对，排序后半段，找&gt;分界点的最小数交换。<br>'
    + code(
        'class Solution {\n'
        '    public int nextGreaterElement(int n) {\n'
        '        char[] chars = String.valueOf(n).toCharArray();\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        int len = chars.length;\n'
        '        for (int i = len - 1; i &gt; 0; i--) {\n'
        '            if (chars[i] &gt; chars[i - 1]) {\n'
        '                Arrays.sort(chars, i, len);\n'
        '                for (int j = i; j &lt; len; j++) {\n'
        '                    if (chars[j] &gt; chars[i - 1]) {\n'
        '                        char temp = chars[j];\n'
        '                        chars[j] = chars[i - 1];\n'
        '                        chars[i - 1] = temp;\n'
        '                        for (int k = 0; k &lt; len; k++) {\n'
        '                            sb.append(chars[k]);\n'
        '                        }\n'
        '                        long res = Long.parseLong(sb.toString());\n'
        '                        if (res &gt; Integer.MAX_VALUE)\n'
        '                            return -1;\n'
        '                        else\n'
        '                            return (int)res;\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return -1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '本质是"下一个排列"问题，与单调栈关系不大。<br>'
    + '核心：从右找到第一个升序对，这是可以变大的位置。<br>'
    + '将后半段排序后，选其中刚好大于分界点的数与分界点交换。<br>'
    + '注意：结果可能超出int范围，需用long检查并返回-1。')

# ============================================================
# 16. 栈的压入、弹出序列
# ============================================================
p = '栈的压入、弹出序列'
d = make_deck(1747301116, f'算法::栈队列堆::{p}')
add_basic(d, make_front(p, '题干'),
    '输入两个整数序列 pushed 和 popped，判断 popped 是否为 pushed 的合法弹出序列。')
add_cloze(d, make_front(p, '策略'),
    '模拟法：按照 pushed 顺序依次{{c1::入栈}}。<br>'
    '每次入栈后，循环判断栈顶是否等于 popped 的当前元素，相等则{{c2::弹出}}并移动 popped 指针。<br>'
    '最终栈为空 → {{c3::合法}}弹出序列。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个元素最多入栈出栈一次<br>空间：{{c2::O(n)}} — 栈空间')
add_basic(d, make_front(p, '题解(模拟)'),
    '模拟入栈出栈过程：按pushed入栈，能匹配popped就弹出。最终栈空则合法。<br>'
    + code(
        'class Solution {\n'
        '    public boolean validateStackSequences(int[] pushed, int[] popped) {\n'
        '        Deque&lt;Integer&gt; stack = new LinkedList&lt;&gt;();\n'
        '        int i = 0;\n'
        '        for (int num : pushed) {\n'
        '            stack.push(num);\n'
        '            while (!stack.isEmpty() && stack.peek() == popped[i]) {\n'
        '                stack.pop();\n'
        '                i++;\n'
        '            }\n'
        '        }\n'
        '        return stack.isEmpty();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '最简单直接的栈模拟题。<br>'
    + '核心思想：按 pushed 顺序入栈，每次入栈后尝试尽可能多地弹出（匹配popped）。<br>'
    + '遍历完pushed后，若栈为空则说明弹出序列合法。')

if __name__ == '__main__':
    print(build('../../牌组/算法/栈队列堆.apkg'))
