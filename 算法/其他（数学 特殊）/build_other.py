"""Build APKG for 其他 (Other/Math). 11 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301900, '算法::其他::原理通识')
add_basic(d0, '位运算常用技巧',
    '1. n & 1：判断奇偶（最低位是否为1）<br>'
    '2. n & (n-1)：消除最低位的1，用于统计二进制中1的个数<br>'
    '3. n & 15 (n & 0xf)：取低4位，等价于 n % 16<br>'
    '4. n &gt;&gt;&gt;= 4：无符号右移4位，等价于 n /= 16（处理负数）<br>'
    '5. a ^ b：无进位加法结果（异或）<br>'
    '6. (a & b) &lt;&lt; 1：进位结果<br>'
    '7. n & (-n)：获取最低位的1（lowbit）')
add_cloze(d0, '数学模拟类问题模式',
    '1. 模拟除法：逐位{{c1::添0}}，用HashMap记录{{c2::余数首次出现位置}}检测循环<br>'
    '2. 快速幂：{{c3::折半指数}}，每次判断奇偶，累乘结果<br>'
    '3. 进制转换：用 {{c4::&amp;15 和 &gt;&gt;&gt;=4}} 处理十六进制<br>'
    '4. 数字序列定位：先确定{{c5::数字范围（位数）}}，再确定具体数字和数位')
add_basic(d0, '拒绝采样与随机化',
    '拒绝采样：通过构造更大范围的均匀分布，拒绝超出目标范围的部分，取模映射到目标范围。<br>'
    '核心公式：(rand7()-1)*7 + rand7() 将范围扩展到 [1,49]<br>'
    'Fisher-Yates洗牌：从前往后，每次随机选一个未处理元素与当前位置交换。<br>'
    'random.nextInt(n - i) 生成 [0, n-i) 范围的随机索引，保证等概率。')

# ============================================================
# 1. 移动零
# ============================================================
p = '移动零'
d = make_deck(1747301901, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个数组 nums，编写一个函数将所有 0 移动到数组的末尾，'
    '同时保持非零元素的相对顺序。<br>'
    '要求必须在原数组上操作，不能拷贝额外的数组。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 遍历两次数组（收集非零 + 补零）<br>空间：{{c2::O(1)}} — 原地操作')
add_basic(d, make_front(p, '题解(双指针)'),
    'index记录非零元素应放置的位置，第一遍收集非零，第二遍将index之后全部置零。<br>'
    + code(
        'public void moveZeroes(int[] nums) {\n'
        '    if (nums == null || nums.length &lt;= 1) {\n'
        '        return;\n'
        '    }\n'
        '    int index = 0;\n'
        '    for (int i = 0; i &lt; nums.length; i++) {\n'
        '        if (nums[i] != 0) {\n'
        '            nums[index] = nums[i];\n'
        '            index++;\n'
        '        }\n'
        '    }\n'
        '\n'
        '    for (int i = index; i &lt; nums.length; i++) {\n'
        '        nums[i] = 0;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '双指针思想：index 指针记录非零元素的写入位置，i 指针遍历数组。<br>'
    '第一遍：将非零元素按顺序收集到前面<br>'
    '第二遍：从 index 到末尾全部置零<br>'
    '非零元素的相对顺序自动保持，因为按原顺序依次写入。')

# ============================================================
# 2. 相交链表
# ============================================================
p = '相交链表'
d = make_deck(1747301902, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '给你两个单链表的头节点 headA 和 headB，找出并返回两个单链表相交的起始节点。'
    '如果两个链表不存在相交节点，返回 null。<br>'
    '要求：时间复杂度 O(n)，空间复杂度 O(1)。'
    + img('image.png') + img('image 1.png') + img('image 2.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n+m)}} — 两个指针各走最多 n+m 步<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(双指针)'),
    'A走完走B，B走完走A，两指针走过的路程相等，相遇点即交点。<br>'
    + code(
        'public class Solution {\n'
        '    public ListNode getIntersectionNode(ListNode headA, ListNode headB) {\n'
        '        ListNode A = headA, B = headB;\n'
        '        while (A != B) {\n'
        '            A = A != null ? A.next : headB;\n'
        '            B = B != null ? B.next : headA;\n'
        '        }\n'
        '        return A;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心思想：消除长度差。设 headA 长度为 a，headB 长度为 b，公共部分长度为 c。<br>'
    'A 走到头后切换到 headB，B 走到头后切换到 headA。<br>'
    'A 走过的总路程：a + (b-c)，B 走过的总路程：b + (a-c)，两者相等。<br>'
    '若两指针相遇，该节点即为交点；若最终都为 null，则无交点。')

# ============================================================
# 3. 用 Rand7() 实现 Rand10()
# ============================================================
p = '用 Rand7() 实现 Rand10()'
d = make_deck(1747301903, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '给定方法 rand7() 可生成 [1,7] 范围内的均匀随机整数，'
    '试写一个方法 rand10() 生成 [1,10] 范围内的均匀随机整数。'
    '不能使用系统的 Math.random() 方法。')
add_cloze(d, make_front(p, '复杂度'),
    '期望时间：{{c1::O(1)}} — 拒绝采样的期望拒绝次数为常数<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(拒绝采样)'),
    '将范围扩展到1~49，拒绝41~49并重新利用余数扩展，多级拒绝最小化浪费。<br>'
    + code(
        'class Solution extends SolBase {\n'
        '    public int rand10() {\n'
        '        while (true) {\n'
        '            int res = (super.rand7() - 1) * 7 + super.rand7();\n'
        '            if (res &lt;= 40)\n'
        '                return 1 + res % 10;\n'
        '            res = (res - 40 - 1) * 7 + super.rand7();\n'
        '            if (res &lt;= 60)\n'
        '                return 1 + res % 10;\n'
        '            res = (res - 60 - 1) * 7 + super.rand7();\n'
        '            if (res &lt;= 20)\n'
        '                return 1 + res % 10;\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '拒绝采样核心：<br>'
    '1. 范围扩展：(rand7()-1)*7 + rand7() 生成 [1,49] 的均匀分布<br>'
    '2. 拒绝策略：只取 &lt;=40 的结果映射到 [1,10]<br>'
    '3. 余数再利用：被拒绝的 41~49 减40后变为1~9，再乘以7扩大范围，继续拒绝采样<br>'
    '4. 每级都充分利用被拒绝的样本，减少总调用次数')

# ============================================================
# 4. Pow(x, n)
# ============================================================
p = 'Pow(x, n)'
d = make_deck(1747301904, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '实现 pow(x, n)，即计算 x 的 n 次幂函数（即 x^n）。'
    'n 可以是负数。'
    + img('image 3.png') + img('image 4.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 指数每次折半<br>空间：{{c2::O(1)}}（迭代）/ {{c3::O(log n)}}（递归）')
add_basic(d, make_front(p, '题解(快速幂-迭代)'),
    '指数每次折半，奇数轮累乘当前x，每轮x自乘，处理负数时取倒数。<br>'
    + code(
        'public double myPow(double x, int n) {\n'
        '    double res = 1.0;\n'
        '    for (int i = n; i != 0; i /= 2) {\n'
        '        if (i % 2 != 0) {\n'
        '            res *= x;\n'
        '        }\n'
        '        x *= x;\n'
        '    }\n'
        '    return n &lt; 0 ? 1 / res : res;\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(快速幂-递归)'),
    '位运算判断奇偶：(n & 1) == 0 即偶数，递归每次折半，负数时在外层乘1/x。<br>'
    + code(
        'public double myPow(double x, int n) {\n'
        '    if (n == 0) {\n'
        '        return 1.0;\n'
        '    } else if ((n & 1) == 0) {\n'
        '        return myPow(x * x, n / 2);\n'
        '    } else {\n'
        '        return (n &gt; 0 ? x : 1.0 / x) * myPow(x * x, n / 2);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '快速幂核心：指数折半。<br>'
    '迭代法：for(i=n; i!=0; i/=2)，奇数轮 res*=x，每轮 x*=x。<br>'
    '递归法：n为偶数时返回 myPow(x*x, n/2)，奇数时多乘一个 x（负数乘 1/x）。<br>'
    '时间复杂度 O(log n)，比暴力 O(n) 快得多。')

# ============================================================
# 5. 字典序的第K小数字
# ============================================================
p = '字典序的第K小数字'
d = make_deck(1747301905, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '给定整数 n 和 k，返回 [1, n] 中字典序第 k 小的数字。'
    '字典序即数字按照字符串顺序排序：1, 10, 100, 101, ... 11, 12, ... 2, 20...'
    + img('image 5.png') + img('image 6.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 在十叉树上逐层移动<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(十叉树遍历)'),
    '将问题建模为十叉树先序遍历，getCount统计以prefix为前缀的节点数，若k在子树内则深入，否则向右兄弟移动。<br>'
    + code(
        'class Solution {\n'
        '    public int findKthNumber(int n, int k) {\n'
        '        int prefix = 1;\n'
        '        int cur = 1;\n'
        '        while (cur &lt; k) {\n'
        '            int count = getCount(prefix, n);\n'
        '            if (cur + count &gt; k) {\n'
        '                prefix *= 10;\n'
        '                cur++;\n'
        '            } else {\n'
        '                prefix++;\n'
        '                cur += count;\n'
        '            }\n'
        '        }\n'
        '        return prefix;\n'
        '    }\n'
        '\n'
        '    public int getCount(int prefix, int n) {\n'
        '        int cur = prefix;\n'
        '        int next = prefix + 1;\n'
        '        int resCount = 0;\n'
        '        while (cur &lt;= n) {\n'
        '            resCount += Math.min(n + 1, next) - cur;\n'
        '            cur *= 10;\n'
        '            next *= 10;\n'
        '        }\n'
        '        return resCount;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '将问题建模为十叉树的先序遍历：<br>'
    'getCount(prefix, n)：统计以 prefix 为前缀且在 [1,n] 内的节点数量<br>'
    '每层：next = prefix+1，当前层节点数 = min(n+1, next) - cur<br>'
    '然后 cur *= 10, next *= 10 进入下一层<br>'
    '判断逻辑：cur + count &gt; k 则在子树内，prefix *= 10 深入；否则 prefix++ 跳到兄弟。')

# ============================================================
# 6. 打乱数组
# ============================================================
p = '打乱数组'
d = make_deck(1747301906, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '实现 Solution 类：<br>'
    'Solution(int[] nums)：使用整数数组 nums 初始化对象<br>'
    'int[] reset()：重设数组到它的初始状态并返回<br>'
    'int[] shuffle()：返回数组随机打乱后的结果')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 遍历一次数组<br>空间：{{c2::O(n)}} — clone 新数组')
add_basic(d, make_front(p, '题解(Fisher-Yates洗牌)'),
    'clone后从i=0到n-1，每次将位置i的元素与[i, n)范围内的随机位置交换，保证等概率。<br>'
    + code(
        'class Solution {\n'
        '    int[] nums;\n'
        '    int n;\n'
        '    Random random = new Random();\n'
        '\n'
        '    public Solution(int[] _nums) {\n'
        '        nums = _nums;\n'
        '        n = nums.length;\n'
        '    }\n'
        '\n'
        '    public int[] reset() {\n'
        '        return nums;\n'
        '    }\n'
        '\n'
        '    public int[] shuffle() {\n'
        '        int[] ans = nums.clone();\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            swap(ans, i, i + random.nextInt(n - i));\n'
        '        }\n'
        '        return ans;\n'
        '    }\n'
        '\n'
        '    void swap(int[] arr, int i, int j) {\n'
        '        int c = arr[i];\n'
        '        arr[i] = arr[j];\n'
        '        arr[j] = c;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'Fisher-Yates 洗牌算法：<br>'
    '从 i=0 到 n-1，每次将位置 i 的元素与 [i, n) 范围内的随机位置交换。<br>'
    '每个排列出现的概率相等（1/n!）：第一个位置有 n 种选择，第二个有 n-1 种...<br>'
    '关键：clone 后 shuffle，保证原数组不被修改。')

# ============================================================
# 7. 第N个数字
# ============================================================
p = '第N个数字'
d = make_deck(1747301907, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '在无限的整数序列 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ... 中找到第 n 位数字。'
    + img('image 7.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 逐位扩大范围查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(数学定位)'),
    '先确定n在哪个位数范围，然后定位到具体数字，最后按位取字符。<br>'
    + code(
        'class Solution {\n'
        '    public int findNthDigit(int n) {\n'
        '        long k = n;\n'
        '        for (int i = 1; ; i++) {\n'
        '            if (i * Math.pow(10, i) &gt; k) {\n'
        '                return Long.toString((int) (k / i))\n'
        '                    .charAt((int) (k % i)) - \'0\';\n'
        '            }\n'
        '            k += Math.pow(10, i);\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '数学三步走：<br>'
    '1. 确定位数范围：1位占10个位置，2位占180个，3位占2700个...i位占 i*10^i 个<br>'
    '2. 定位具体数字：用 k/i 确定第几个数，k%i 确定该数的第几位<br>'
    '3. 取字符：charAt(k%i) - "0" 转换回数字<br>'
    'k 随着 i 增大不断累加 10^i（补零），直到 k 落入当前位数范围。')

# ============================================================
# 8. 分数到小数
# ============================================================
p = '分数到小数'
d = make_deck(1747301908, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个整数，分别表示分子 numerator 和分母 denominator，'
    '以字符串形式返回小数。<br>'
    '如果小数部分为循环小数，则将循环的部分括在括号内。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(denominator)}} — 余数最多有 denominator 种可能<br>空间：{{c2::O(denominator)}} — HashMap 记录余数位置')
add_basic(d, make_front(p, '题解(模拟除法)'),
    '模拟长除法：每次余数*10作为新被除数，HashMap记录余数首次出现位置以检测循环。<br>'
    + code(
        'class Solution {\n'
        '    public String fractionToDecimal(int numerator, int denominator) {\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        long a = numerator, b = denominator;\n'
        '        if (a &lt; 0 && b &gt; 0 || a &gt; 0 && b &lt; 0)\n'
        '            sb.append(\'-\');\n'
        '        a = Math.abs(a);\n'
        '        b = Math.abs(b);\n'
        '        sb.append(a / b);\n'
        '        if (a % b == 0)\n'
        '            return sb.toString();\n'
        '        sb.append(\'.\');\n'
        '        Map&lt;Long, Integer&gt; memory = new HashMap&lt;&gt;();\n'
        '        while ((a = (a % b) * 10) &gt; 0 && !memory.containsKey(a)) {\n'
        '            memory.put(a, sb.length());\n'
        '            sb.append(a / b);\n'
        '        }\n'
        '        if (a == 0)\n'
        '            return sb.toString();\n'
        '        return sb.insert(memory.get(a).intValue(), \'(\')\n'
        '                 .append(\')\').toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '模拟长除法步骤：<br>'
    '1. 先处理符号和整数部分 a/b，若能整除直接返回<br>'
    '2. 添加小数点后，每次：余数 *= 10 作为新被除数，商 append 到结果<br>'
    '3. 用 HashMap&lt;余数, 位置&gt; 检测循环：若余数已存在，说明开始循环<br>'
    '4. 在循环起始位置插入 "("，末尾追加 ")"<br>'
    '关键：转 long 防止溢出；Math.abs() 取绝对值计算。')

# ============================================================
# 9. 数字转换为十六进制数
# ============================================================
p = '数字转换为十六进制数'
d = make_deck(1747301909, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数，编写一个算法将这个数转换为十六进制数。'
    '对于负整数，使用补码运算方法。<br>'
    '十六进制中所有字母(a-f)都必须是小写。'
    + img('image 8.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 每次右移4位<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(取余法)'),
    'num % 16 取每位，num /= 16 移位，负数需 +2^32 偏移后计算。<br>'
    + code(
        'class Solution {\n'
        '    public String toHex(int num) {\n'
        '        if (num == 0)\n'
        '            return "0";\n'
        '        long res = num;\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        if (res &lt; 0)\n'
        '            res = (long) (Math.pow(2, 32) + res);\n'
        '        while (res != 0) {\n'
        '            long temp = res % 16;\n'
        '            char c = (char) (temp + \'0\');\n'
        '            if (temp &gt;= 10) {\n'
        '                c = (char) (temp - 10 + \'a\');\n'
        '            }\n'
        '            sb.append(c);\n'
        '            res /= 16;\n'
        '        }\n'
        '        return sb.reverse().toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(位运算法)'),
    '&15取低4位（等价%16），>>>4无符号右移，负数用补码自动处理。<br>'
    + code(
        'class Solution {\n'
        '    public String toHex(int num) {\n'
        '        if (num == 0)\n'
        '            return "0";\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        while (num != 0) {\n'
        '            int temp = num & 15;\n'
        '            char c = (char) (temp + \'0\');\n'
        '            if (temp &gt;= 10) {\n'
        '                c = (char) (temp - 10 + \'a\');\n'
        '            }\n'
        '            sb.append(c);\n'
        '            num &gt;&gt;&gt;= 4;\n'
        '        }\n'
        '        return sb.reverse().toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '两种方法对比：<br>'
    '1. 取余法：num % 16 取每位，num /= 16 移位，负数需 +2^32 偏移<br>'
    '2. 位运算法（推荐）：num & 15 取低4位，num &gt;&gt;&gt;= 4 无符号右移<br>'
    '位运算法优势：无需额外处理负数，&gt;&gt;&gt; 保证无符号右移，补码自动正确<br>'
    '结果需 reverse()，因为从低位到高位构造。')

# ============================================================
# 10. 不用加减乘除做加法
# ============================================================
p = '不用加减乘除做加法'
d = make_deck(1747301910, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '写一个函数，求两个整数之和，要求在函数体内不得使用 "+"、"-"、"*"、"/" 四则运算符号。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(1)}} — 最多循环32次（int 32位）<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(位运算)'),
    'a^b得无进位和，(a&b)<<1得进位，循环直到进位为0。<br>'
    + code(
        'class Solution {\n'
        '    public int add(int a, int b) {\n'
        '        int res;\n'
        '        while (b != 0) {\n'
        '            res = (a & b) &lt;&lt; 1;\n'
        '            a = a ^ b;\n'
        '            b = res;\n'
        '        }\n'
        '        return a;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '位运算模拟加法原理：<br>'
    '示例 13(1101) + 9(1001)：<br>'
    '不考虑进位：1101 ^ 1001 = 0100（结果为12的二进制）<br>'
    '只算进位：(1101 & 1001) &lt;&lt; 1 = 1001 &lt;&lt; 1 = 10010（进位为10）<br>'
    '12 + 10 = 22，正确。每轮迭代用 XOR 算无进位和，AND&lt;&lt;1 算进位，直到进位为0。')

# ============================================================
# 11. 二进制中1的个数
# ============================================================
p = '二进制中1的个数'
d = make_deck(1747301911, f'算法::其他::{p}')
add_basic(d, make_front(p, '题干'),
    '编写一个函数，输入是一个无符号整数（以二进制串的形式），'
    '返回其二进制表达式中数字位数为 "1" 的个数（汉明重量）。')
add_cloze(d, make_front(p, '复杂度'),
    '逐位法：时间 {{c1::O(32)}}，空间 {{c2::O(1)}}<br>'
    'n&(n-1)法：时间 {{c3::O(k)}}（k为1的个数），空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(逐位判断)'),
    'n & 1判断最低位是否为1（结果为0或1），然后无符号右移1位，循环32次。<br>'
    + code(
        'public class Solution {\n'
        '    public int hammingWeight(int n) {\n'
        '        int res = 0;\n'
        '        while (n != 0) {\n'
        '            res += n & 1;\n'
        '            n &gt;&gt;&gt;= 1;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(n&(n-1))'),
    'n & (n-1) 消除最低位的1，每次消除一个1并计数，循环次数等于1的个数。<br>'
    + code(
        'public class Solution {\n'
        '    public int hammingWeight(int n) {\n'
        '        int res = 0;\n'
        '        while (n != 0) {\n'
        '            res++;\n'
        '            n &= n - 1;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '两种方法对比：<br>'
    '1. 逐位判断法：n & 1 判断最低位 + n &gt;&gt;&gt;= 1 右移，固定 O(32) 次循环<br>'
    '2. n&(n-1) 法：每次消除最低位的 1，循环次数 = 1 的个数（更优）<br>'
    '原理：n-1 会把最低位的 1 变成 0，其右边的 0 全部变 1，与 n 做 AND 运算即消除最低位的 1。<br>'
    '使用 &gt;&gt;&gt; 无符号右移，避免负数高位补 1 导致的无限循环。')

if __name__ == '__main__':
    print(build('../../牌组/其他.apkg'))
