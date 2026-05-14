"""Build APKG for 力扣简单 (LeetCode Easy). 24 problems, 3-5 cards each."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# ============================================================
# 1. 用队列实现栈
# ============================================================
p = '用队列实现栈'
d = make_deck(1747302001, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '请你仅使用两个队列实现一个后入先出（LIFO）的栈，并支持普通栈的全部四种操作'
    '（push、top、pop 和 empty）。实现 MyStack 类。')
add_cloze(d, make_front(p, '复杂度'),
    'push：{{c1::O(1)}}<br>pop：{{c2::O(1)}}<br>'
    'top：{{c3::O(1)}}<br>空间：{{c4::O(n)}} — 均使用 Deque 双端队列实现')
add_basic(d, make_front(p, '题解(Deque)'),
    'Deque 双端队列的 push/pop/peek 均在队首操作，天然实现了栈的后入先出。<br>'
    + code(
        'class MyStack {\n'
        '    Deque&lt;Integer&gt; stack1;\n'
        '\n'
        '    public MyStack() {\n'
        '        stack1 = new LinkedList&lt;&gt;();\n'
        '    }\n'
        '\n'
        '    public void push(int x) {\n'
        '        stack1.push(x);\n'
        '    }\n'
        '\n'
        '    public int pop() {\n'
        '        return stack1.pop();\n'
        '    }\n'
        '\n'
        '    public int top() {\n'
        '        return stack1.peek();\n'
        '    }\n'
        '\n'
        '    public boolean empty() {\n'
        '        if (stack1.size() == 0) {\n'
        '            return true;\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 2. 圆圈中最后剩下的数字
# ============================================================
p = '圆圈中最后剩下的数字'
d = make_deck(1747302002, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '0,1,...,n-1 这 n 个数字排成一个圆圈，从数字 0 开始，每次从这个圆圈里删除第 m 个数字。'
    '求出这个圆圈里剩下的最后一个数字。' + img('image.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 递归 n 层<br>空间：{{c2::O(n)}} — 递归调用栈深度')
add_basic(d, make_front(p, '题解(递归)'),
    '约瑟夫环递推公式：f(n,m) = (f(n-1,m) + m) % n，base case f(1)=0。<br>'
    + code(
        'class Solution {\n'
        '    public int lastRemaining(int n, int m) {\n'
        '        return f(n, m);\n'
        '    }\n'
        '\n'
        '    public int f(int n, int m) {\n'
        '        if (n == 1) {\n'
        '            return 0;\n'
        '        }\n'
        '        int x = f(n - 1, m);\n'
        '        return (m + x) % n;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '约瑟夫环递推公式：f(n,m) = (f(n-1,m) + m) % n<br>'
    '理解：每次删除后，从下一位置重新编号，旧编号 = (新编号 + m) % 当前人数。<br>'
    '从 n=1 的 base case 倒推回 n 即可。')

# ============================================================
# 3. 调整数组顺序使奇数位于偶数前面
# ============================================================
p = '调整数组顺序使奇数位于偶数前面'
d = make_deck(1747302003, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '输入一个整数数组，实现一个函数来调整该数组中数字的顺序，'
    '使得所有奇数在数组的前半部分，所有偶数在数组的后半部分。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 双指针一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(双指针)'),
    '左指针找偶数，右指针找奇数，找到后交换。类似快速排序的 partition 过程。<br>'
    + code(
        'class Solution {\n'
        '    public int[] exchange(int[] nums) {\n'
        '        int temp = 0;\n'
        '        int left = 0;\n'
        '        int right = nums.length - 1;\n'
        '        while (left &lt; right) {\n'
        '            if (nums[left] % 2 != 0) {\n'
        '                left++;\n'
        '                continue;\n'
        '            }\n'
        '            if (nums[right] % 2 == 0) {\n'
        '                right--;\n'
        '                continue;\n'
        '            }\n'
        '            temp = nums[left];\n'
        '            nums[left] = nums[right];\n'
        '            nums[right] = temp;\n'
        '        }\n'
        '        return nums;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '双指针相向而行：左边跳过奇数找偶数，右边跳过偶数找奇数，交换后继续。<br>'
    '类似快速排序的 partition 过程。关键在于指针移动时机：只有当前满足条件才移动。')

# ============================================================
# 4. 扑克牌中的顺子
# ============================================================
p = '扑克牌中的顺子'
d = make_deck(1747302004, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '从若干副扑克牌中随机抽 5 张牌，判断是不是一个顺子。'
    'A=1, J=11, Q=12, K=13，大小王(0)可以看成任意数字。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n log n)}} — 排序开销（n=5 可视为 O(1)）<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(排序+计数)'),
    '排序后统计大小王数量，然后检查相邻牌差值，用大小王填补 gap。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isStraight(int[] nums) {\n'
        '        int n = nums.length;\n'
        '        int i = 0, j = 1, zeroNum = 0;\n'
        '        Arrays.sort(nums);\n'
        '\n'
        '        while (zeroNum &lt; n) {\n'
        '            if (nums[zeroNum] == 0)\n'
        '                zeroNum++;\n'
        '            else\n'
        '                break;\n'
        '        }\n'
        '        i = zeroNum; j = zeroNum + 1;\n'
        '        while (j &lt; n) {\n'
        '            int difference = nums[j] - nums[i];\n'
        '            if (difference == 1) {\n'
        '                i++; j++;\n'
        '            } else if (difference - zeroNum &gt;= 2)\n'
        '                return false;\n'
        '            else if (difference == 0)\n'
        '                return false;\n'
        '            else if (difference == zeroNum + 1) {\n'
        '                i++; j++;\n'
        '                zeroNum = 0;\n'
        '            } else\n'
        '                return true;\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '顺子条件：除了大小王(0)外，无重复牌 + max-min &lt; 5。<br>'
    '更简洁：排序后，统计 0 的个数，然后遍历非 0 部分，'
    '相邻差值 diff-1 就是需要的大小王数量。<br>'
    '只要 0 够用（zeroNum &gt;= 需要的填补量）就是顺子。')

# ============================================================
# 5. 重复的子字符串
# ============================================================
p = '重复的子字符串'
d = make_deck(1747302005, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非空的字符串 s，检查是否可以通过由它的一个子串重复多次构成。'
    + img('image 1.png'))
add_cloze(d, make_front(p, '复杂度'),
    '拼接法：时间 {{c1::O(n)}}（contains 实现相关），空间 {{c2::O(n)}}<br>'
    'KMP：时间 {{c3::O(n)}}，空间 {{c4::O(n)}}')
add_basic(d, make_front(p, '题解(拼接法)'),
    '将 s 拼接自身，去掉首尾字符，若新串中仍包含 s，则 s 可由子串重复构成。<br>'
    + code(
        'class Solution {\n'
        '    public boolean repeatedSubstringPattern(String s) {\n'
        '        String str = s + s;\n'
        '        return str.substring(1, str.length() - 1).contains(s);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(KMP)'),
    '构造 next 数组，若 len 能被 (len - next[len-1]) 整除则存在循环节。<br>'
    + code(
        'class Solution {\n'
        '    public boolean repeatedSubstringPattern(String s) {\n'
        '        if (s.equals("")) return false;\n'
        '\n'
        '        int len = s.length();\n'
        '        int[] next = new int[len];\n'
        '\n'
        '        for (int i = 1, j = 0; i &lt; len; i++) {\n'
        '            while (j &gt; 0 && s.charAt(i) != s.charAt(j))\n'
        '                j = next[j - 1];\n'
        '            if (s.charAt(i) == s.charAt(j)) j++;\n'
        '            next[i] = j;\n'
        '        }\n'
        '\n'
        '        if (next[len - 1] &gt; 0\n'
        '                && len % (len - next[len - 1]) == 0) {\n'
        '            return true;\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 6. Excel表列名称
# ============================================================
p = 'Excel表列名称'
d = make_deck(1747302006, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个整数 columnNumber，返回它在 Excel 表中相对应的列名称。'
    'A→1, B→2, ..., Z→26, AA→27, AB→28...' + img('image 2.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 每次除以 26（底数为 26）<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解'),
    '关键：先 cn-- 再取模。因为 A 对应 1 而非 0，需要将 1-indexed 转为 0-indexed。<br>'
    + code(
        'class Solution {\n'
        '    public String convertToTitle(int cn) {\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        while (cn &gt; 0) {\n'
        '            cn--;\n'
        "            sb.append((char)(cn % 26 + 'A'));\n"
        '            cn /= 26;\n'
        '        }\n'
        '        sb.reverse();\n'
        '        return sb.toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心陷阱：Excel 列号是 1-indexed（A=1），但取模运算需要 0-indexed。<br>'
    '所以每次循环先 cn--，这样 A→0, B→1, ..., Z→25。<br>'
    '最后需要 reverse 因为先算出来的是低位。')

# ============================================================
# 7. 删除字符串中的所有相邻重复项
# ============================================================
p = '删除字符串中的所有相邻重复项'
d = make_deck(1747302007, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给出由小写字母组成的字符串 S，重复项删除操作会选择两个相邻且相同的字母并删除它们。'
    '反复执行删除操作，直到无法继续删除。返回最终字符串。'
    + img('34457_xmKgrAtYScw8L302.png'))
add_cloze(d, make_front(p, '复杂度'),
    '栈法：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    '原地数组：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(栈)'),
    '当前字符与栈顶相同则弹出(消除一对)，否则入栈。最后栈中剩余字符逆序拼接。<br>'
    + code(
        'class Solution {\n'
        '    public String removeDuplicates(String s) {\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        Stack&lt;Character&gt; stack = new Stack();\n'
        '        int i = 0;\n'
        '        while (i &lt; s.length()) {\n'
        '            char ch = s.charAt(i);\n'
        '            if (stack.isEmpty() || ch != stack.peek()) {\n'
        '                stack.push(s.charAt(i));\n'
        '                i++;\n'
        '            } else {\n'
        '                stack.pop();\n'
        '                i++;\n'
        '            }\n'
        '        }\n'
        '        while (!stack.isEmpty())\n'
        '            sb.append(stack.pop());\n'
        '        return sb.reverse().toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(原地数组)'),
    '用 char[] 自身当栈，index 指针模拟栈顶。匹配则 index--，不匹配则覆盖写入。<br>'
    + code(
        'class Solution {\n'
        '    public String removeDuplicates(String s) {\n'
        '        int index = -1;\n'
        '        char[] chs = s.toCharArray();\n'
        '        for (int i = 0; i &lt; chs.length; i++) {\n'
        '            if (index &gt;= 0 && chs[index] == chs[i])\n'
        '                index--;\n'
        '            else {\n'
        '                index++;\n'
        '                chs[index] = chs[i];\n'
        '            }\n'
        '        }\n'
        '        return String.copyValueOf(chs, 0, index + 1);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '原地数组优化：用 index 指针模拟栈，char[] 数组自身当栈。<br>'
    'index=-1 代表空栈，匹配则 index--，不匹配则 chs[++index]=chs[i]。<br>'
    '最终 new String(chs, 0, index+1) 即为结果，空间 O(1)。')

# ============================================================
# 8. 数组中重复的数字
# ============================================================
p = '数组中重复的数字'
d = make_deck(1747302008, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '在一个长度为 n 的数组 nums 里的所有数字都在 0 ~ n-1 的范围内。'
    '找出数组中任意一个重复的数字。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个元素最多交换两次<br>空间：{{c2::O(1)}} — 原地交换')
add_basic(d, make_front(p, '题解(原地Hash)'),
    '将每个数字放到其值对应的索引位置，若目标位置已有相同值则找到重复。<br>'
    + code(
        'class Solution {\n'
        '    public int findRepeatNumber(int[] nums) {\n'
        '        int temp = -1;\n'
        '        for (int i = 0; i &lt; nums.length;) {\n'
        '            if (nums[i] == i) {\n'
        '                i++;\n'
        '                continue;\n'
        '            }\n'
        '            if (nums[nums[i]] != nums[i]) {\n'
        '                temp = nums[nums[i]];\n'
        '                nums[nums[i]] = nums[i];\n'
        '                nums[i] = temp;\n'
        '            } else\n'
        '                return nums[i];\n'
        '        }\n'
        '        return -1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '原地哈希核心：数字范围 0~n-1，每个数字的值 = 它应该在的索引。<br>'
    '若 nums[i]==i 说明归位，i++ 继续；否则与 nums[nums[i]] 交换。<br>'
    '交换时发现 nums[nums[i]] == nums[i] 说明重复。每个数最多被交换 2 次。')

# ============================================================
# 9. 旋转数组的最小数字
# ============================================================
p = '旋转数组的最小数字'
d = make_deck(1747302009, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '把一个数组最开始的若干个元素搬到数组的末尾，称之为数组的旋转。'
    '输入一个递增排序的数组的一个旋转，输出旋转数组的最小元素。'
    + img('image 3.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解'),
    '旋转数组中第一次出现「前 &gt; 后」的位置，后一个元素即最小值。<br>'
    + code(
        'class Solution {\n'
        '    public int minArray(int[] numbers) {\n'
        '        for (int i = 0; i &lt; numbers.length - 1; i++) {\n'
        '            if (numbers[i] &gt; numbers[i + 1])\n'
        '                return numbers[i + 1];\n'
        '        }\n'
        '        return numbers[0];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '旋转后的数组分为两个递增段，第二段的第一个元素就是最小值。<br>'
    '即找到第一个 numbers[i] &gt; numbers[i+1] 的位置，numbers[i+1] 为结果。<br>'
    '若整个数组仍是递增的（旋转了 0 个或 n 个），则 numbers[0] 是最小值。')

# ============================================================
# 10. 位1的个数
# ============================================================
p = '位1的个数'
d = make_deck(1747302010, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '编写一个函数，输入是一个无符号整数（以二进制串的形式），'
    '返回其二进制表达式中数字位数为 1 的个数（汉明重量）。')
add_cloze(d, make_front(p, '复杂度'),
    'n & (n-1) 法：时间 {{c1::O(k)}}（k=1的个数），空间 {{c2::O(1)}}<br>'
    '逐位检查：时间 {{c3::O(32)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(n & (n-1))'),
    'n & (n-1) 会将 n 的最低位的 1 变成 0，每次循环消除一个 1。<br>'
    + code(
        'public class Solution {\n'
        '    public int hammingWeight(int n) {\n'
        '        int res = 0;\n'
        '        while (n != 0) {\n'
        '            n &amp;= n - 1;\n'
        '            res++;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '三种方法：<br>'
    '1. n & (n-1)：每次消除最低位 1，循环次数=1的个数，最优<br>'
    '2. 逐位右移：while(n!=0) { count += n&1; n &gt;&gt;&gt;= 1; }，固定 32 次<br>'
    '3. 分治累加：两两分组统计 → 4位 → 8位 → 乘 0x01010101 汇总，O(1)')

# ============================================================
# 11. 在排序数组中查找数字 I
# ============================================================
p = '在排序数组中查找数字 I'
d = make_deck(1747302011, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '统计一个数字在排序数组中出现的次数。' + img('image 4.png'))
add_cloze(d, make_front(p, '复杂度'),
    '遍历法：时间 {{c1::O(n)}}，空间 {{c2::O(1)}}<br>'
    '二分法：时间 {{c3::O(log n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(遍历)'),
    '遍历统计 target 出现次数，简单直接。<br>'
    + code(
        'class Solution {\n'
        '    public int search(int[] nums, int target) {\n'
        '        if (nums.length == 0\n'
        '            || target &lt; nums[0]\n'
        '            || target &gt; nums[nums.length - 1])\n'
        '            return 0;\n'
        '        int temp = 0;\n'
        '        for (int i = 0; i &lt;= nums.length - 1; i++) {\n'
        '            if (target == nums[i])\n'
        '                temp++;\n'
        '        }\n'
        '        if (temp == 0)\n'
        '            return 0;\n'
        '        return temp;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(二分)'),
    '二分查找 target 的第一个位置和 target+1 的第一个位置，差值即出现次数。<br>'
    + '核心：寻找 &gt;= target 的左边界，count = search(target+1) - search(target)。')

# ============================================================
# 12. 两数之和 II - 输入有序数组
# ============================================================
p = '两数之和 II - 输入有序数组'
d = make_deck(1747302012, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个下标从 1 开始的整数数组 numbers，该数组已按非递减顺序排列。'
    '找出两个数之和等于目标数 target，返回两个数的下标（1-indexed）。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 双指针一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(双指针)'),
    '左指针在开头，右指针在末尾，和太大则右指针左移，和太小则左指针右移。<br>'
    + code(
        'class Solution {\n'
        '    public int[] twoSum(int[] numbers, int target) {\n'
        '        int len = numbers.length;\n'
        '        int i = 0, j = len - 1;\n'
        '        while (i &lt; j) {\n'
        '            int sum = numbers[i] + numbers[j];\n'
        '            if (sum &gt; target)\n'
        '                j--;\n'
        '            else if (sum &lt; target)\n'
        '                i++;\n'
        '            else\n'
        '                return new int[]{i + 1, j + 1};\n'
        '        }\n'
        '        return new int[]{-1, -1};\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '利用数组有序性：如果 sum &gt; target，则任何与 j 的组合都会更大，所以 j 左移。<br>'
    '如果 sum &lt; target，则任何与 i 的组合都会更小，所以 i 右移。<br>'
    '这本质上是在二维矩阵中搜索，双指针每次排除一行或一列。')

# ============================================================
# 13. 缺失数字
# ============================================================
p = '缺失数字'
d = make_deck(1747302013, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个包含 [0, n] 中 n 个数的数组 nums，找出 [0, n] 中没有出现在数组中的那个数。')
add_cloze(d, make_front(p, '复杂度'),
    '数学法：时间 {{c1::O(n)}}，空间 {{c2::O(1)}}<br>'
    '异或法：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(异或)'),
    '先对 0~n 全部异或，再异或数组中所有数，成对的消掉，剩下就是缺失的。<br>'
    + code(
        'class Solution {\n'
        '    public int missingNumber(int[] nums) {\n'
        '        int n = nums.length;\n'
        '        int ans = 0;\n'
        '        for (int i = 0; i &lt;= n; i++) ans ^= i;\n'
        '        for (int i : nums) ans ^= i;\n'
        '        return ans;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(数学法)'),
    '0~n 的等差数列和减去数组元素和，差值即缺失数。<br>'
    + code(
        'class Solution {\n'
        '    public int missingNumber(int[] nums) {\n'
        '        int n = nums.length;\n'
        '        int cur = 0, sum = n * (n + 1) / 2;\n'
        '        for (int i : nums) cur += i;\n'
        '        return sum - cur;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '多种解法：<br>'
    '1. 数学法：sum(0..n) - sum(nums) = 缺失数，注意防溢出用 long<br>'
    '2. 异或法：x ^ x = 0，将 0~n 和数组所有元素异或，剩下的即缺失数<br>'
    '3. 原地哈希：将数字放到对应索引，第一个不匹配的位置即缺失数')

# ============================================================
# 14. 有序数组的平方
# ============================================================
p = '有序数组的平方'
d = make_deck(1747302014, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个按非递减顺序排序的整数数组 nums，返回每个数字的平方组成的新数组，'
    '要求也按非递减顺序排序。' + img('image 5.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 双指针一次遍历<br>空间：{{c2::O(n)}} — 结果数组')
add_basic(d, make_front(p, '题解(双指针)'),
    '平方后最大值一定在数组两端，从后往前填充结果数组。<br>'
    + code(
        'class Solution {\n'
        '    public int[] sortedSquares(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        int left = 0, right = len - 1;\n'
        '\n'
        '        int[] arrPow = new int[len];\n'
        '        int write = len - 1;\n'
        '\n'
        '        while (left &lt;= right) {\n'
        '            if (nums[left] * nums[left]\n'
        '                    &gt; nums[right] * nums[right]) {\n'
        '                arrPow[write] = nums[left] * nums[left];\n'
        '                left++;\n'
        '            } else {\n'
        '                arrPow[write] = nums[right] * nums[right];\n'
        '                right--;\n'
        '            }\n'
        '            write--;\n'
        '        }\n'
        '        return arrPow;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '关键洞察：原数组可能有负数，平方后最大值一定出现在数组的两端。<br>'
    '双指针从两端向中间移动，每次选择平方值较大的填入结果数组末尾。<br>'
    '从后往前填充避免了结果数组的元素移动。')

# ============================================================
# 15. 阶乘后的零
# ============================================================
p = '阶乘后的零'
d = make_deck(1747302015, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数 n，返回 n! 结果尾数中零的数量。' + img('image 6.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 每次除以 5（底数为 5）<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解'),
    '尾零数量 = min(因子2的个数, 因子5的个数) = 因子5的个数（因为2总是更多）。<br>'
    + code(
        'class Solution {\n'
        '    public int trailingZeroes(int n) {\n'
        '        int count = 0;\n'
        '        while (n &gt; 0) {\n'
        '            count += n / 5;\n'
        '            n = n / 5;\n'
        '        }\n'
        '        return count;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心：每个尾零由一对因子 2×5 产生，而 2 的因子数量远多于 5。<br>'
    '所以只需统计 1~n 中因子 5 的总数 = n/5 + n/25 + n/125 + ...<br>'
    '循环 n/=5 累加等价于这个级数求和。')

# ============================================================
# 16. Excel表列序号
# ============================================================
p = 'Excel表列序号'
d = make_deck(1747302016, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个字符串 columnTitle，表示 Excel 表格中的列名称。返回该列名称对应的列序号。'
    'A→1, B→2, ..., Z→26, AA→27...')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 遍历字符串<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解'),
    '26 进制转 10 进制，注意 1-indexed（A=1, Z=26），每次 res = res * 26 + (ch - A + 1)。<br>'
    + code(
        'class Solution {\n'
        '    public int titleToNumber(String s) {\n'
        '        int len = s.length();\n'
        '        int res = 0;\n'
        '        for (int i = 0; i &lt; len; i++) {\n'
        "            res = res * 26 + (s.charAt(i) - 'A' + 1);\n"
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '26 进制转 10 进制，注意 1-indexed（A=1, Z=26）。<br>'
    '与「Excel表列名称」互为逆运算，那题需要先 cn--，这题需要 +1。<br>'
    "遍历方式：res = res * 26 + (ch - 'A' + 1)。")

# ============================================================
# 17. 搜索插入位置
# ============================================================
p = '搜索插入位置'
d = make_deck(1747302017, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个排序数组和一个目标值，在数组中找到目标值并返回其索引。'
    '如果目标值不存在于数组中，返回它将会被按顺序插入的位置。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 二分查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(二分)'),
    '寻找第一个 &gt;= target 的索引。res 初始化为 nums.length，覆盖 target 大于所有元素的情况。<br>'
    + code(
        'class Solution {\n'
        '    public int searchInsert(int[] nums, int target) {\n'
        '        int left = 0, right = nums.length - 1;\n'
        '        int res = nums.length;\n'
        '        while (left &lt;= right) {\n'
        '            int mid = (left + right) / 2;\n'
        '            if (nums[mid] &gt;= target) {\n'
        '                res = mid;\n'
        '                right = mid - 1;\n'
        '            } else\n'
        '                left = mid + 1;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '二分查找变体：找第一个 &gt;= target 的位置。<br>'
    '当 nums[mid]==target 时不直接返回，继续向左搜索更左边界。<br>'
    'res 初始化为 nums.length，覆盖 target 大于所有元素的情况。')

# ============================================================
# 18. 翻转单词顺序
# ============================================================
p = '翻转单词顺序'
d = make_deck(1747302018, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '输入一个英文句子，翻转句子中单词的顺序，但单词内字符的顺序不变。'
    '标点符号和普通字母一样处理。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 拆分 + 遍历<br>空间：{{c2::O(n)}} — 字符串数组')
add_basic(d, make_front(p, '题解'),
    '按空格 split，倒序遍历数组，跳过空串（连续空格产生），单词间补一个空格。<br>'
    + code(
        'class Solution {\n'
        '    public String reverseWords(String s) {\n'
        '        String[] strArr = s.split(" ");\n'
        '        String str = "";\n'
        '        for (int i = strArr.length - 1; i &gt;= 0; i--) {\n'
        '            if (strArr[i].equals(""))\n'
        '                continue;\n'
        '            if (i == strArr.length - 1) {\n'
        '                str = str + strArr[i];\n'
        '                continue;\n'
        '            } else if (i == 0) {\n'
        '                str = str + " " + strArr[i];\n'
        '                break;\n'
        '            }\n'
        '            str = str + " " + strArr[i];\n'
        '        }\n'
        '        return str;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 19. 0～n-1中缺失的数字
# ============================================================
p = '0～n-1中缺失的数字'
d = make_deck(1747302019, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '一个长度为 n-1 的递增排序数组中的所有数字都是唯一的，'
    '并且每个数字都在范围 0~n-1 之内。找出缺失的数字。'
    + img('image 7.png'))
add_cloze(d, make_front(p, '复杂度'),
    '遍历法：时间 {{c1::O(n)}}，空间 {{c2::O(1)}}<br>'
    '二分法：时间 {{c3::O(log n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(遍历)'),
    '遍历找第一个 nums[i] != i 的位置，i 即为缺失数字。<br>'
    + code(
        'class Solution {\n'
        '    public int missingNumber(int[] nums) {\n'
        '        if (nums[0] != 0)\n'
        '            return 0;\n'
        '        if (nums.length == 1 && nums[0] == 0)\n'
        '            return nums[0] + 1;\n'
        '        for (int i = 0; i &lt; nums.length - 1; i++) {\n'
        '            if (nums[i + 1] - nums[i] != 1) {\n'
        '                return nums[i] + 1;\n'
        '            }\n'
        '        }\n'
        '        return nums[nums.length - 1] + 1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(二分)'),
    '在缺失数字之前，nums[i]==i；之后，nums[i]==i+1。二分找第一个不匹配的位置。<br>'
    + '二分查找：若 nums[mid]==mid 则缺失在右侧(left=mid+1)，否则在左侧(right=mid-1)。最终 left 即缺失数字。')
add_basic(d, make_front(p, '关键技巧'),
    '多种解法：遍历找第一个 nums[i]!=i 的位置；<br>'
    '二分查找：在缺失数字之前 nums[i]==i，之后 nums[i]==i+1，找第一个不匹配的位置。')

# ============================================================
# 20. 替换空格
# ============================================================
p = '替换空格'
d = make_deck(1747302020, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '请实现一个函数，把字符串 s 中的每个空格替换成 "%20"。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 遍历字符串<br>空间：{{c2::O(n)}} — StringBuilder')
add_basic(d, make_front(p, '题解'),
    '遍历每个字符，空格替换为 %20，其他字符直接追加。或直接用 s.replace()。<br>'
    + code(
        'class Solution {\n'
        '    public String replaceSpace(String s) {\n'
        '        return s.replace(" ", "%20");\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '最简单：s.replace(" ", "%20")。<br>'
    '面试可写遍历版本：遍历 char 数组，遇空格 append("%20")，否则 append(c)。')

# ============================================================
# 21. 下一个更大元素 I
# ============================================================
p = '下一个更大元素 I'
d = make_deck(1747302021, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    'nums1 是 nums2 的子集。对于 nums1 中的每个元素，找出在 nums2 中该元素右侧第一个比它大的元素。'
    '不存在则返回 -1。')
add_cloze(d, make_front(p, '复杂度'),
    '暴力法：时间 {{c1::O(n*m)}}，空间 {{c2::O(1)}}<br>'
    '单调栈：时间 {{c3::O(n+m)}}，空间 {{c4::O(n)}}')
add_basic(d, make_front(p, '题解(暴力)'),
    '先在 nums2 中找到等于 nums1[i] 的元素，再向右找第一个更大的值。<br>'
    + code(
        'class Solution {\n'
        '    public int[] nextGreaterElement(int[] nums1, int[] nums2) {\n'
        '\n'
        '        for (int i = 0; i &lt; nums1.length; i++)\n'
        '            for (int j = 0; j &lt; nums2.length; j++) {\n'
        '                int temp = nums1[i];\n'
        '                if (temp != nums2[j])\n'
        '                    continue;\n'
        '                else {\n'
        '                    int change = findBigger(nums2, j);\n'
        '                    nums1[i] = change;\n'
        '                    break;\n'
        '                }\n'
        '            }\n'
        '        return nums1;\n'
        '    }\n'
        '\n'
        '    public int findBigger(int[] nums2, int index) {\n'
        '        for (int i = index + 1; i &lt; nums2.length; i++) {\n'
        '            if (nums2[index] &lt; nums2[i])\n'
        '                return nums2[i];\n'
        '            else\n'
        '                continue;\n'
        '        }\n'
        '        return -1;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '优化：单调栈预处理 nums2 中每个元素的「下一个更大元素」，存入 HashMap。<br>'
    '单调递减栈：遇到比栈顶大的元素时，栈顶出栈并记录结果，新元素入栈。<br>'
    '预处理后 nums1 的查询变成 O(1) HashMap 查找。')

# ============================================================
# 22. 左旋转字符串
# ============================================================
p = '左旋转字符串'
d = make_deck(1747302022, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '字符串的左旋转操作是把字符串前面的若干个字符转移到字符串的尾部。'
    '实现一个函数，输入字符串 s 和数字 n，返回左旋转 n 位后的结果。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 遍历字符串<br>空间：{{c2::O(n)}} — 新字符串')
add_basic(d, make_front(p, '题解(取余遍历)'),
    '用取余方式区分前后两部分，一次遍历完成拼接，避免两次 substring。<br>'
    + code(
        'class Solution {\n'
        '    public String reverseLeftWords(String s, int n) {\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        for (int i = n; i &lt; n + s.length(); i++) {\n'
        '            sb.append(s.charAt(i % s.length()));\n'
        '        }\n'
        '        return sb.toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(substring)'),
    'substring 直接拼接：s.substring(n) + s.substring(0, n)。最简洁直观。<br>'
    + code(
        'class Solution {\n'
        '    public String reverseLeftWords(String s, int n) {\n'
        '        return s.substring(n, s.length()) + s.substring(0, n);\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 23. 排列硬币
# ============================================================
p = '排列硬币'
d = make_deck(1747302023, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '你总共有 n 枚硬币，需要将它们摆成一个阶梯形状，第 k 行恰好有 k 枚硬币。'
    '返回可形成完整阶梯行的总行数。')
add_cloze(d, make_front(p, '复杂度'),
    '二分法：时间 {{c1::O(log n)}}，空间 {{c2::O(1)}}')
add_basic(d, make_front(p, '题解(二分查找)'),
    '前 k 行硬币总数 = k*(k+1)/2，二分查找满足 S_mid &lt;= n 的最大 mid。<br>'
    + code(
        'class Solution {\n'
        '    public int arrangeCoins(int n) {\n'
        '        long left = 0, right = 10000000;\n'
        '        long res = 0;\n'
        '        while (left &lt;= right) {\n'
        '            long mid = (left + right) / 2;\n'
        '            if (mid + (mid * (mid - 1)) / 2 &lt;= n) {\n'
        '                res = mid;\n'
        '                left = mid + 1;\n'
        '            } else\n'
        '                right = mid - 1;\n'
        '        }\n'
        '        return (int)res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '等差数列前 k 项和：Sk = k*(k+1)/2。<br>'
    '二分查找「小于等于 target 的最大行数」，找到满足 S_mid &lt;= n 的最大 mid。<br>'
    '注意用 long 防止 mid*(mid+1)/2 溢出。')

# ============================================================
# 24. 有效的完全平方数
# ============================================================
p = '有效的完全平方数'
d = make_deck(1747302024, f'算法::力扣简单::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个正整数 num，编写一个函数判断是否为完全平方数。不可使用任何内置库函数。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 二分查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(二分)'),
    '二分查找小于等于 num 的最大平方根，验证平方是否等于 num。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isPerfectSquare(int num) {\n'
        '        long left = 0, right = 10000000;\n'
        '        long res = 0;\n'
        '        while (left &lt;= right) {\n'
        '            long mid = (left + right) / 2;\n'
        '            if (mid * mid &lt;= num) {\n'
        '                res = mid;\n'
        '                left = mid + 1;\n'
        '            } else\n'
        '                right = mid - 1;\n'
        '        }\n'
        '        return res * res == num;\n'
        '    }\n'
        '}'
    ))

if __name__ == '__main__':
    print(build('../../牌组/算法/力扣简单.apkg'))
