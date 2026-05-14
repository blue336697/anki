"""Build APKG for 字符串 (String). 14 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747301400, '算法::字符串::原理通识')
add_basic(d0, '字符串处理核心方法',
    '1. StringBuilder/StringBuffer：可变字符串，用于频繁拼接场景，避免 String 的 O(n²) 复制开销<br>'
    '2. 字符操作：charAt(i)取值，- \'0\'转数字，- \'a\'转字母索引<br>'
    '3. 双指针技术：首尾对撞（回文）、快慢指针（滑动窗口）、读写指针（原地修改）<br>'
    '4. 数字与字符互转：char - \'0\' → int，int + \'0\' → char，Integer.parseInt()，String.valueOf()')
add_cloze(d0, '字符串常用技巧',
    '1. 数字字符转整数：{{c1::ch - \'0\'}}<br>'
    '2. 整数转字符：(char)({{c2::n + \'0\'}}) 或 (char)(n - 10 + \'a\')<br>'
    '3. 大小写统一：ch &amp; {{c3::0xDF}} 或 Character.toLowerCase()<br>'
    '4. split 正则转义：{{c4::"\\\\."}} 匹配点号，"\\\\s+" 匹配连续空格<br>'
    '5. 溢出判断公式：res &gt; MAX/10 {{c5::||}} (res == MAX/10 &amp;&amp; digit &gt; MAX%10)')
add_basic(d0, '字符串模拟与解析',
    '字符串解析问题的一般步骤：<br>'
    '1. 去除前导/尾随空格（trim / 双指针跳过）<br>'
    '2. 处理符号位（正负号、特殊标记）<br>'
    '3. 逐字符解析数字（注意进位、溢出判断）<br>'
    '4. 特殊分隔符处理（"."、":"、括号等）<br>'
    '5. 字符串拼接结果构造（StringBuilder + reverse）')

# ============================================================
# 1. 字符串相加
# ============================================================
p = '字符串相加'
d = make_deck(1747301401, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个字符串形式的非负整数 num1 和 num2，计算它们的和并同样以字符串形式返回。'
    '不能使用任何內建的用于处理大整数的库（如 BigInteger），也不能直接将输入的字符串转换为整数形式。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(max(N, M))}} — 从末尾到头部逐位遍历<br>空间：{{c2::O(max(N, M))}} — StringBuilder 存储结果')

add_basic(d, make_front(p, '题解(模拟竖式加法)'),
    '从末尾逐位相加，while 条件包含 carry!=0 处理最高位进位。<br>'
    + code(
        'class Solution {\n'
        '    public String addStrings(String num1, String num2) {\n'
        '        StringBuilder res = new StringBuilder("");\n'
        '        int i = num1.length() - 1, j = num2.length() - 1, carry = 0;\n'
        '        while (i &gt;= 0 || j &gt;= 0 || carry != 0) {\n'
        '            int n1 = i &gt;= 0 ? num1.charAt(i) - \'0\' : 0;\n'
        '            int n2 = j &gt;= 0 ? num2.charAt(j) - \'0\' : 0;\n'
        '            int tmp = n1 + n2 + carry;\n'
        '            carry = tmp / 10;\n'
        '            res.append(tmp % 10);\n'
        '            i--; j--;\n'
        '        }\n'
        '        if (carry == 1) res.append(1);\n'
        '        return res.reverse().toString();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '模拟竖式加法的三个关键点：<br>'
    '1. while 条件必须包含 carry != 0，处理最高位进位（如 99+1 = 100）<br>'
    '2. 字符转数字：ch - \'0\'，取余 append 后要 reverse（因为是从低位到高位拼接）<br>'
    '3. 缺位补0：用三元运算符 i&gt;=0 ? num1.charAt(i)-\'0\' : 0 统一处理不等长')

# ============================================================
# 2. 比较版本号
# ============================================================
p = '比较版本号'
d = make_deck(1747301402, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '比较两个版本号 version1 和 version2。版本号由一个或多个修订号组成，各修订号由一个 \'.\' 连接。'
    '如果 version1 &gt; version2 返回 1，version1 &lt; version2 返回 -1，否则返回 0。')
add_cloze(d, make_front(p, '复杂度'),
    '分割法：时间 {{c1::O(max(N, M))}}，空间 {{c2::O(N + M)}}<br>'
    '双指针：时间 {{c3::O(max(N, M))}}，空间 {{c4::O(1)}}')

add_basic(d, make_front(p, '题解(分割法)'),
    '直接 split 后逐段比较，注意 "." 的转义。<br>'
    + code(
        'class Solution {\n'
        '    public int compareVersion(String version1, String version2) {\n'
        '        String[] s1 = version1.split("\\\\.");\n'
        '        String[] s2 = version2.split("\\\\.");\n'
        '        for (int i = 0; i &lt; s1.length || i &lt; s2.length; ++i) {\n'
        '            int num1 = 0, num2 = 0;\n'
        '            if (i &lt; s1.length)\n'
        '                num1 = Integer.parseInt(s1[i]);\n'
        '            if (i &lt; s2.length)\n'
        '                num2 = Integer.parseInt(s2[i]);\n'
        '            if (num1 &gt; num2)\n'
        '                return 1;\n'
        '            if (num1 &lt; num2)\n'
        '                return -1;\n'
        '        }\n'
        '        return 0;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(双指针)'),
    '双指针无需 split 数组，空间 O(1)，逐字符解析数字并在遇到 "." 时比较。<br>'
    + code(
        'class Solution {\n'
        '    public int compareVersion(String version1, String version2) {\n'
        '        int i = 0, j = 0;\n'
        '        while (i &lt; version1.length() || j &lt; version2.length()) {\n'
        '            int num1 = 0;\n'
        '            for (; i &lt; version1.length() && version1.charAt(i) != \'.\'; ++i) {\n'
        '                num1 = num1 * 10 + version1.charAt(i) - \'0\';\n'
        '            }\n'
        '            ++i;\n'
        '            int num2 = 0;\n'
        '            for (; j &lt; version2.length() && version2.charAt(j) != \'.\'; ++j) {\n'
        '                num2 = num2 * 10 + version2.charAt(j) - \'0\';\n'
        '            }\n'
        '            ++j;\n'
        '            if (num1 &gt; num2)\n'
        '                return 1;\n'
        '            if (num1 &lt; num2)\n'
        '                return -1;\n'
        '        }\n'
        '        return 0;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '版本号比较本质是逐段解析+比较，核心技巧：<br>'
    '1. 缺位补0：短的版本号缺失的修订号视为 0（如 1.0 == 1.0.0）<br>'
    '2. 双指针优化：不用 split 创建数组，直接在遍历中逐字符累加数字<br>'
    '3. 注意 split("\\.") 中的点号需要转义')

# ============================================================
# 3. 字符串转换整数 (atoi)
# ============================================================
p = '字符串转换整数 (atoi)'
d = make_deck(1747301403, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '实现一个 atoi 函数，将字符串转换成整数。规则：'
    '1. 丢弃前导空格；2. 检查正负符号；3. 读入数字直到非数字或结尾；'
    '4. 如果整数超过32位有符号整数范围，返回边界值。' + img('image.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(n)}} — charArray 存储')

add_basic(d, make_front(p, '题解(模拟)'),
    '四步：去空格→取符号→溢出判断→逐位转换，sign 参与运算统一正负。<br>'
    + code(
        'class Solution {\n'
        '    public int myAtoi(String str) {\n'
        '        int len = str.length();\n'
        '        char[] charArray = str.toCharArray();\n'
        '        int index = 0;\n'
        '        while (index &lt; len && charArray[index] == \' \') {\n'
        '            index++;\n'
        '        }\n'
        '        if (index == len) {\n'
        '            return 0;\n'
        '        }\n'
        '        int sign = 1;\n'
        '        char firstChar = charArray[index];\n'
        '        if (firstChar == \'+\') {\n'
        '            index++;\n'
        '        } else if (firstChar == \'-\') {\n'
        '            index++;\n'
        '            sign = -1;\n'
        '        }\n'
        '        int res = 0;\n'
        '        while (index &lt; len) {\n'
        '            char currChar = charArray[index];\n'
        '            if (currChar &gt; \'9\' || currChar &lt; \'0\') {\n'
        '                break;\n'
        '            }\n'
        '            if (res &gt; Integer.MAX_VALUE / 10 ||\n'
        '                (res == Integer.MAX_VALUE / 10 &&\n'
        '                 (currChar - \'0\') &gt; Integer.MAX_VALUE % 10)) {\n'
        '                return Integer.MAX_VALUE;\n'
        '            }\n'
        '            if (res &lt; Integer.MIN_VALUE / 10 ||\n'
        '                (res == Integer.MIN_VALUE / 10 &&\n'
        '                 (currChar - \'0\') &gt; -(Integer.MIN_VALUE % 10))) {\n'
        '                return Integer.MIN_VALUE;\n'
        '            }\n'
        '            res = res * 10 + sign * (currChar - \'0\');\n'
        '            index++;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'atoi 实现的四个关键步骤：<br>'
    '1. 去前导空格：while 跳过空格字符<br>'
    '2. 符号处理：仅第一个符号有效，用 sign=±1 记录<br>'
    '3. 溢出判断（核心）：MAX/10 提前判断，digit &gt; MAX%10 精确判断最后一位<br>'
    '4. 符号参与计算：res = res*10 + sign*digit，避免最后才乘 sign 导致负溢出')

# ============================================================
# 4. 字符串相乘
# ============================================================
p = '字符串相乘'
d = make_deck(1747301404, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个以字符串形式表示的非负整数 num1 和 num2，返回它们的乘积，也以字符串形式表示。'
    '不能使用任何內建的 BigInteger 库或直接将输入转换为整数。'
    + img('image 1.png') + img('image 2.png'))
add_cloze(d, make_front(p, '复杂度'),
    '竖式累加法：时间 {{c1::O(MN + M+N)}}，空间 {{c2::O(M+N)}}<br>'
    '位置索引法：时间 {{c3::O(MN)}}，空间 {{c4::O(M+N)}} — 少了一层循环相加')

add_basic(d, make_front(p, '题解(竖式累加法)'),
    '逐位相乘再累加：num2 的每一位乘 num1 的全部位，结果补零后用字符串相加函数累加。<br>'
    + code(
        'class Solution {\n'
        '    public String multiply(String num1, String num2) {\n'
        '        if (num1.equals("0") || num2.equals("0"))\n'
        '            return "0";\n'
        '        String res = "0";\n'
        '        for (int i = num2.length() - 1; i &gt;= 0; i--) {\n'
        '            int carry = 0;\n'
        '            StringBuilder temp = new StringBuilder();\n'
        '            for (int j = 0; j &lt; num2.length() - i - 1; j++) {\n'
        '                temp.append(0);\n'
        '            }\n'
        '            int n2 = num2.charAt(i) - \'0\';\n'
        '            for (int j = num1.length() - 1; j &gt;= 0 || carry != 0; j--) {\n'
        '                int n1 = j &gt;= 0 ? num1.charAt(j) - \'0\' : 0;\n'
        '                int partSum = (n1 * n2 + carry) % 10;\n'
        '                temp.append(partSum);\n'
        '                carry = (n1 * n2 + carry) / 10;\n'
        '            }\n'
        '            res = addStrings(res, temp.reverse().toString());\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public String addStrings(String num1, String num2) {\n'
        '        StringBuilder res = new StringBuilder();\n'
        '        int i = num1.length() - 1, j = num2.length() - 1, carry = 0;\n'
        '        while (i &gt;= 0 || j &gt;= 0 || carry != 0) {\n'
        '            int n1 = i &gt;= 0 ? num1.charAt(i) - \'0\' : 0;\n'
        '            int n2 = j &gt;= 0 ? num2.charAt(j) - \'0\' : 0;\n'
        '            int temp = n1 + n2 + carry;\n'
        '            carry = temp / 10;\n'
        '            res.append(temp % 10);\n'
        '            i--;\n'
        '            j--;\n'
        '        }\n'
        '        if (carry == 1)\n'
        '            res.append(1);\n'
        '        return res.reverse().toString();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(位置索引法)'),
    '规律：num1[i]*num2[j] 的结果存于 res[i+j](进位) 和 res[i+j+1](当前位)，一次遍历完成。<br>'
    + code(
        'class Solution {\n'
        '    public String multiply(String num1, String num2) {\n'
        '        if (num1.equals("0") || num2.equals("0"))\n'
        '            return "0";\n'
        '        int[] res = new int[num1.length() + num2.length()];\n'
        '        for (int i = num1.length() - 1; i &gt;= 0; i--) {\n'
        '            int n1 = num1.charAt(i) - \'0\';\n'
        '            for (int j = num2.length() - 1; j &gt;= 0; j--) {\n'
        '                int n2 = num2.charAt(j) - \'0\';\n'
        '                int sum = res[i + j + 1] + n1 * n2;\n'
        '                res[i + j] += sum / 10;\n'
        '                res[i + j + 1] = sum % 10;\n'
        '            }\n'
        '        }\n'
        '        StringBuilder result = new StringBuilder();\n'
        '        for (int i = 0; i &lt; res.length; i++) {\n'
        '            if (i == 0 && res[i] == 0)\n'
        '                continue;\n'
        '            result.append(res[i]);\n'
        '        }\n'
        '        return result.toString();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '两种方法对比：<br>'
    '1. 竖式累加法：直观但需要额外 addStrings 循环，常数较大<br>'
    '2. 位置索引法：利用 num1[i]*num2[j] → res[i+j]+res[i+j+1] 的规律，一次遍历完成<br>'
    '核心规律：M位×N位结果最多 M+N 位，i+j 位置存进位并在后续迭代中累加。')

# ============================================================
# 5. 翻转字符串里的单词
# ============================================================
p = '翻转字符串里的单词'
d = make_deck(1747301405, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串，逐个翻转字符串中的每个单词。单词是由非空格字符组成的序列。'
    '返回的字符串中单词间应当仅用一个空格分隔，并且不应有任何额外的空格。')
add_cloze(d, make_front(p, '复杂度'),
    'API法：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    '双端队列：时间 {{c3::O(n)}}，空间 {{c4::O(n)}}')

add_basic(d, make_front(p, '题解(API法)'),
    '最简洁：trim+split("\\\\s+")+Collections.reverse+join。<br>'
    + code(
        'class Solution {\n'
        '    public String reverseWords(String s) {\n'
        '        s = s.trim();\n'
        '        List&lt;String&gt; wordList = Arrays.asList(s.split("\\\\s+"));\n'
        '        Collections.reverse(wordList);\n'
        '        return String.join(" ", wordList);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(双端队列)'),
    'offerFirst 将单词插入队头实现逆序，join 拼接时自动加空格。<br>'
    + code(
        'class Solution {\n'
        '    public String reverseWords(String s) {\n'
        '        int left = 0, right = s.length() - 1;\n'
        '        while (left &lt;= right && s.charAt(left) == \' \') {\n'
        '            ++left;\n'
        '        }\n'
        '        while (left &lt;= right && s.charAt(right) == \' \') {\n'
        '            --right;\n'
        '        }\n'
        '        Deque&lt;String&gt; d = new ArrayDeque&lt;String&gt;();\n'
        '        StringBuilder word = new StringBuilder();\n'
        '        while (left &lt;= right) {\n'
        '            char c = s.charAt(left);\n'
        '            if ((word.length() != 0) && (c == \' \')) {\n'
        '                d.offerFirst(word.toString());\n'
        '                word.setLength(0);\n'
        '            } else if (c != \' \') {\n'
        '                word.append(c);\n'
        '            }\n'
        '            ++left;\n'
        '        }\n'
        '        d.offerFirst(word.toString());\n'
        '        return String.join(" ", d);\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '两种方法对比：<br>'
    '1. API法：trim()+split("\\\\s+")+reverse()+join() 最简洁<br>'
    '2. 双端队列：手动去除首尾空格，遍历中构建单词，遇到空格时将单词 push 到队头<br>'
    '注意：split("\\\\s+") 中的 \\\\s+ 匹配一个或多个空白字符')

# ============================================================
# 6. 字符串解码
# ============================================================
p = '字符串解码'
d = make_deck(1747301406, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个经过编码的字符串，返回它解码后的字符串。编码规则为: k[encoded_string]，'
    '表示其中方括号内部的 encoded_string 正好重复 k 次。k 保证为正整数。可以认为原始数据不包含数字。')
add_cloze(d, make_front(p, '复杂度'),
    '栈法：时间 {{c1::O(S)}} — S 为展开后的长度<br>空间：{{c2::O(S)}} — 两个栈存储中间状态<br>'
    '递归法：时间 {{c3::O(S)}}，空间 {{c4::O(嵌套层数)}}')

add_basic(d, make_front(p, '题解(栈)'),
    '遇 [ 将当前倍数和字符串入栈后重置，遇 ] 时取出栈顶倍数和字符串进行拼接。<br>'
    + code(
        'class Solution {\n'
        '    public String decodeString(String s) {\n'
        '        StringBuilder str = new StringBuilder();\n'
        '        Deque&lt;Integer&gt; stack_num = new LinkedList&lt;&gt;();\n'
        '        int num = 0;\n'
        '        Deque&lt;String&gt; stack_str = new LinkedList&lt;&gt;();\n'
        '        for (Character c : s.toCharArray()) {\n'
        '            if (c == \'[\') {\n'
        '                stack_num.push(num);\n'
        '                stack_str.push(str.toString());\n'
        '                num = 0;\n'
        '                str = new StringBuilder();\n'
        '            } else if (c == \']\') {\n'
        '                StringBuilder temp = new StringBuilder();\n'
        '                int cur_num = stack_num.pop();\n'
        '                for (int i = 0; i &lt; cur_num; i++)\n'
        '                    temp.append(str);\n'
        '                str = new StringBuilder(stack_str.pop() + temp);\n'
        '            } else if (c &gt;= \'0\' && c &lt;= \'9\')\n'
        '                num = num * 10 + Integer.parseInt(c + "");\n'
        '            else\n'
        '                str.append(c);\n'
        '        }\n'
        '        return str.toString();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(递归)'),
    '遇 [ 递归进入内层，返回时带回内层结束位置和解码结果。<br>'
    + code(
        'class Solution {\n'
        '    public String decodeString(String s) {\n'
        '        return dfs(s, 0)[0];\n'
        '    }\n'
        '    private String[] dfs(String s, int i) {\n'
        '        StringBuilder res = new StringBuilder();\n'
        '        int multi = 0;\n'
        '        while (i &lt; s.length()) {\n'
        '            if (s.charAt(i) &gt;= \'0\' && s.charAt(i) &lt;= \'9\')\n'
        '                multi = multi * 10 + Integer.parseInt(String.valueOf(s.charAt(i)));\n'
        '            else if (s.charAt(i) == \'[\') {\n'
        '                String[] tmp = dfs(s, i + 1);\n'
        '                i = Integer.parseInt(tmp[0]);\n'
        '                while (multi &gt; 0) {\n'
        '                    res.append(tmp[1]);\n'
        '                    multi--;\n'
        '                }\n'
        '            } else if (s.charAt(i) == \']\')\n'
        '                return new String[] { String.valueOf(i), res.toString() };\n'
        '            else\n'
        '                res.append(String.valueOf(s.charAt(i)));\n'
        '            i++;\n'
        '        }\n'
        '        return new String[] { res.toString() };\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '双栈解法：stack_num 存倍数，stack_str 存之前的字符串。<br>'
    '遇 \'[\' 时将当前 num 和 str 入栈后重置，遇 \']\' 时取出栈顶倍数和字符串进行拼接。<br>'
    '核心理解：括号嵌套时，栈保证 inner 结果先拼接完成，再与 outer 合并。<br>'
    '递归法一样优雅：遇 \'[\' 递归进入下一层，遇 \']\' 返回当前层结果和结束位置。')

# ============================================================
# 7. 最长公共前缀
# ============================================================
p = '最长公共前缀'
d = make_deck(1747301407, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '编写一个函数来查找字符串数组中的最长公共前缀。如果不存在公共前缀，返回空字符串 ""。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(S)}} — S 为所有字符串字符总数<br>空间：{{c2::O(1)}}')

add_basic(d, make_front(p, '题解(横向扫描)'),
    '以第一个字符串为基准，逐个与后续字符串比较，每次缩短 res。<br>'
    + code(
        'class Solution {\n'
        '    public String longestCommonPrefix(String[] strs) {\n'
        '        if (strs == null || strs.length == 0)\n'
        '            return "";\n'
        '        String res = strs[0];\n'
        '        for (int i = 1; i &lt; strs.length; i++) {\n'
        '            int resCount = 0;\n'
        '            for (; resCount &lt; res.length() && resCount &lt; strs[i].length(); resCount++) {\n'
        '                if (res.charAt(resCount) != strs[i].charAt(resCount)) {\n'
        '                    break;\n'
        '                }\n'
        '            }\n'
        '            res = res.substring(0, resCount);\n'
        '            if (res == "")\n'
        '                return "";\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '横向扫描：以第一个字符串为公共前缀的初始值，然后逐个与后面的字符串比较，'
    '每次将 res 缩短到两者的公共前缀长度。一旦 res 为空，直接返回 ""。<br>'
    '其他方法：纵向扫描（逐列比较所有字符串的同一位置）、分治法、二分查找。')

# ============================================================
# 8. 验证IP地址
# ============================================================
p = '验证IP地址'
d = make_deck(1747301408, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 queryIP，如果是有效的 IPv4 地址返回 "IPv4"，如果是有效的 IPv6 地址返回 "IPv6"，'
    '都不是返回 "Neither"。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}} — 仅用几个变量')

add_basic(d, make_front(p, '题解(正则法)'),
    '简洁但性能较差，IPv4段匹配0-255，IPv6段匹配1-4位十六进制。<br>'
    + code(
        'class Solution {\n'
        '    public String validIPAddress(String queryIP) {\n'
        '        if (queryIP == null) {\n'
        '            return "Neither";\n'
        '        }\n'
        '        String regex0 = "((\\\\d)|([1-9]\\\\d)|(1\\\\d\\\\d)|((25[0-5])|2[0-4]\\\\d))";\n'
        '        String regexIPv4 = regex0 + "(\\\\." + regex0 + "){3}";\n'
        '        String regex1 = "(\\\\d|[a-f]|[A-F]){1,4}";\n'
        '        String regexIPv6 = regex1 + "(:" + regex1 + "){7}";\n'
        '        String result = "Neither";\n'
        '        if (queryIP.matches(regexIPv4)) {\n'
        '            result = "IPv4";\n'
        '        } else if (queryIP.matches(regexIPv6)) {\n'
        '            result = "IPv6";\n'
        '        }\n'
        '        return result;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(模拟法)'),
    '逐段解析数字，IPv4验证范围0-255+前导零，IPv6验证1-4位十六进制。<br>'
    + code(
        'class Solution {\n'
        '    public String validIPAddress(String ip) {\n'
        '        if (ip.indexOf(".") &gt;= 0 && check4(ip)) return "IPv4";\n'
        '        if (ip.indexOf(":") &gt;= 0 && check6(ip)) return "IPv6";\n'
        '        return "Neither";\n'
        '    }\n'
        '    boolean check4(String ip) {\n'
        '        int n = ip.length(), cnt = 0;\n'
        '        char[] cs = ip.toCharArray();\n'
        '        for (int i = 0; i &lt; n && cnt &lt;= 3; ) {\n'
        '            int j = i, x = 0;\n'
        '            while (j &lt; n && cs[j] &gt;= \'0\' && cs[j] &lt;= \'9\' && x &lt;= 255)\n'
        '                x = x * 10 + (cs[j++] - \'0\');\n'
        '            if (i == j) return false;\n'
        '            if ((j - i &gt; 1 && cs[i] == \'0\') || (x &gt; 255)) return false;\n'
        '            i = j + 1;\n'
        '            if (j == n) continue;\n'
        '            if (cs[j] != \'.\') return false;\n'
        '            cnt++;\n'
        '        }\n'
        '        return cnt == 3 && cs[0] != \'.\' && cs[n - 1] != \'.\';\n'
        '    }\n'
        '    boolean check6(String ip) {\n'
        '        int n = ip.length(), cnt = 0;\n'
        '        char[] cs = ip.toCharArray();\n'
        '        for (int i = 0; i &lt; n && cnt &lt;= 7; ) {\n'
        '            int j = i;\n'
        '            while (j &lt; n && ((cs[j] &gt;= \'a\' && cs[j] &lt;= \'f\')\n'
        '                || (cs[j] &gt;= \'A\' && cs[j] &lt;= \'F\')\n'
        '                || (cs[j] &gt;= \'0\' && cs[j] &lt;= \'9\'))) j++;\n'
        '            if (i == j || j - i &gt; 4) return false;\n'
        '            i = j + 1;\n'
        '            if (j == n) continue;\n'
        '            if (cs[j] != \':\') return false;\n'
        '            cnt++;\n'
        '        }\n'
        '        return cnt == 7 && cs[0] != \':\' && cs[n - 1] != \':\';\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'IPv4 校验关键点：<br>'
    '1. 每段值 0-255，不能有前导零（除非值为0本身）<br>'
    '2. 恰好3个点号，开头结尾不能是点<br>'
    '3. IPv6：每段1-4位十六进制字符，7个冒号<br>'
    '模拟法比正则更可控，可以精确定位错误原因。')

# ============================================================
# 9. 36进制加法
# ============================================================
p = '36进制加法'
d = make_deck(1747301409, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '36进制数的加法。36进制的数表示为 0-9 正常表，10-35 用 a-z 表示。'
    '例如 1b = 47，2x = 105。实现两个36进制字符串的加法。' + img('image 3.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(max(N, M))}} — 从末尾逐位相加<br>空间：{{c2::O(max(N, M))}} — StringBuilder')

add_basic(d, make_front(p, '题解(模拟)'),
    '与十进制加法完全相同的框架，仅基数从10变为36，增加字符映射函数。<br>'
    + code(
        'class Solution {\n'
        '    private char getChar(int n) {\n'
        '        if (n &lt;= 9)\n'
        '            return (char) (n + \'0\');\n'
        '        else\n'
        '            return (char) (n - 10 + \'a\');\n'
        '    }\n'
        '\n'
        '    private int getInt(char ch) {\n'
        '        if (\'0\' &lt;= ch && ch &lt;= \'9\')\n'
        '            return ch - \'0\';\n'
        '        else\n'
        '            return ch - \'a\' + 10;\n'
        '    }\n'
        '\n'
        '    public String addStrings(String num1, String num2) {\n'
        '        StringBuilder res = new StringBuilder("");\n'
        '        int i = num1.length() - 1, j = num2.length() - 1, carry = 0;\n'
        '        while (i &gt;= 0 || j &gt;= 0 || carry != 0) {\n'
        '            int n1 = i &gt;= 0 ? getInt(num1.charAt(i)) : 0;\n'
        '            int n2 = j &gt;= 0 ? getInt(num2.charAt(j)) : 0;\n'
        '            int tmp = n1 + n2 + carry;\n'
        '            carry = tmp / 36;\n'
        '            res.append(getChar(tmp % 36));\n'
        '            i--; j--;\n'
        '        }\n'
        '        if (carry == 1) res.append(getChar(1));\n'
        '        return res.reverse().toString();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '与「字符串相加」对比记忆：框架完全相同，仅有三个差异：<br>'
    '1. 基数：/10 和 %10 → /36 和 %36<br>'
    '2. 字符映射：ch-\'0\' ↔ n+\'0\' → 增加 ch-\'a\'+10 ↔ n-10+\'a\'<br>'
    '3. 本质上任何进制加法都可用此模板，只需替换基数和映射函数')

# ============================================================
# 10. 至少有K个重复字符的最长子串
# ============================================================
p = '至少有K个重复字符的最长子串'
d = make_deck(1747301410, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定字符串 s 和一个整数 k，找出 s 中的最长子串，要求该子串中的每一字符出现次数都不少于 k。'
    '返回这一子串的长度。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(26n) → O(n)}} — 每层递归最多26次分割<br>空间：{{c2::O(26²)}} — 递归栈深度最多26层')

add_basic(d, make_front(p, '题解(递归分治)'),
    '核心：以出现次数&lt;k的字符为分割点，递归处理分割后的子串。<br>'
    + code(
        'class Solution {\n'
        '    public int longestSubstring(String s, int k) {\n'
        '        if (s.length() &lt; k)\n'
        '            return 0;\n'
        '        Map&lt;Character, Integer&gt; map = new HashMap&lt;&gt;();\n'
        '        for (int i = 0; i &lt; s.length(); i++) {\n'
        '            map.put(s.charAt(i), map.getOrDefault(s.charAt(i), 0) + 1);\n'
        '        }\n'
        '        for (char ch : map.keySet()) {\n'
        '            if (map.get(ch) &lt; k) {\n'
        '                int res = 0;\n'
        '                for (String str : s.split(String.valueOf(ch)))\n'
        '                    res = Math.max(res, longestSubstring(str, k));\n'
        '                return res;\n'
        '            }\n'
        '        }\n'
        '        return s.length();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '分治思想：如果某个字符在整个字符串中出现次数 &lt; k，则任何合法子串都不能包含该字符。'
    '因此可以用该字符分割字符串，对每个子串递归求解，取最大值。<br>'
    '关键理解：分割字符一定不在答案子串中，所以按它分割不会漏掉答案。<br>'
    '递归最多26层（26个小写字母），每层O(n)，总复杂度 O(26n)。')

# ============================================================
# 11. 压缩字符串
# ============================================================
p = '压缩字符串'
d = make_deck(1747301411, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符数组 chars，使用原地算法压缩它。压缩规则：如果字符连续出现 cnt 次，'
    '则压缩为 [字符] + [cnt]（cnt&gt;1时）。返回压缩后数组的新长度。必须原地修改输入数组。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}} — 原地修改')

add_basic(d, make_front(p, '题解(双指针+数字反转)'),
    '数字逆序写入后再反转数组片段，避免使用 String 对象（更符合"原地"要求）。<br>'
    + code(
        'class Solution {\n'
        '    public int compress(char[] cs) {\n'
        '        int n = cs.length;\n'
        '        int i = 0, j = 0;\n'
        '        while (i &lt; n) {\n'
        '            int idx = i;\n'
        '            while (idx &lt; n && cs[idx] == cs[i]) idx++;\n'
        '            int cnt = idx - i;\n'
        '            cs[j++] = cs[i];\n'
        '            if (cnt &gt; 1) {\n'
        '                int start = j, end = start;\n'
        '                while (cnt != 0) {\n'
        '                    cs[end++] = (char) ((cnt % 10) + \'0\');\n'
        '                    cnt /= 10;\n'
        '                }\n'
        '                reverse(cs, start, end - 1);\n'
        '                j = end;\n'
        '            }\n'
        '            i = idx;\n'
        '        }\n'
        '        return j;\n'
        '    }\n'
        '    void reverse(char[] cs, int start, int end) {\n'
        '        while (start &lt; end) {\n'
        '            char t = cs[start];\n'
        '            cs[start] = cs[end];\n'
        '            cs[end] = t;\n'
        '            start++; end--;\n'
        '        }\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(双指针+直接转换)'),
    'i 用于扫描，j 用于写入。统计连续字符数后用 String.valueOf 写入数字。<br>'
    + code(
        'class Solution {\n'
        '    public int compress(char[] cs) {\n'
        '        int n = cs.length;\n'
        '        int i = 0, j = 0;\n'
        '        while (i &lt; n) {\n'
        '            int idx = i;\n'
        '            while (idx &lt; n && cs[idx] == cs[i]) idx++;\n'
        '            int cnt = idx - i;\n'
        '            cs[j++] = cs[i];\n'
        '            if (cnt &gt; 1) {\n'
        '                int end = j;\n'
        '                String str = String.valueOf(cnt);\n'
        '                for (int k = 0; k &lt; str.length(); k++) {\n'
        '                    cs[end++] = str.charAt(k);\n'
        '                }\n'
        '                j = end;\n'
        '            }\n'
        '            i = idx;\n'
        '        }\n'
        '        return j;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '双指针原地压缩：i（读指针）扫描原数组，j（写指针）写入压缩结果。<br>'
    '数字写入的两种方式：<br>'
    '1. String.valueOf(cnt)：简洁但创建了额外字符串对象<br>'
    '2. 逆序取余+反转：真正原地，字符逐位写入后反转数字片段<br>'
    '注意：压缩后的长度可能比原数组短或长（计数为1时不变），j 始终表示新长度。')

# ============================================================
# 12. Z 字形变换
# ============================================================
p = 'Z 字形变换'
d = make_deck(1747301412, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '将一个给定字符串 s 根据给定的行数 numRows，以从上往下、从左到右进行 Z 字形排列。'
    '返回按行读取得到的字符串。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(n)}} — 每行一个 StringBuilder')

add_basic(d, make_front(p, '题解(flag转向)'),
    'flag 控制上下移动方向，到达边界时反转 flag。<br>'
    + code(
        'class Solution {\n'
        '    public String convert(String s, int numRows) {\n'
        '        if (numRows &lt; 2)\n'
        '            return s;\n'
        '        List&lt;StringBuilder&gt; rows = new ArrayList&lt;StringBuilder&gt;();\n'
        '        for (int i = 0; i &lt; numRows; i++)\n'
        '            rows.add(new StringBuilder());\n'
        '        int i = 0, flag = -1;\n'
        '        for (char ch : s.toCharArray()) {\n'
        '            rows.get(i).append(ch);\n'
        '            if (i == 0 || i == numRows - 1)\n'
        '                flag = -flag;\n'
        '            i += flag;\n'
        '        }\n'
        '        StringBuilder res = new StringBuilder();\n'
        '        for (StringBuilder row : rows)\n'
        '            res.append(row);\n'
        '        return res.toString();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '不需要真的构造 Z 字形矩阵，只需模拟行的上下移动：<br>'
    '1. 用 List&lt;StringBuilder&gt; 存储每行的字符<br>'
    '2. flag 变量控制当前行号的增减方向：遇第一行向下(+1)，遇最后一行向上(-1)<br>'
    '3. 最后按行拼接即得结果。空间 O(numRows + n)，时间 O(n)。')

# ============================================================
# 13. 找到字符串中所有字母异位词
# ============================================================
p = '找到字符串中所有字母异位词'
d = make_deck(1747301413, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个字符串 s 和 p，找到 s 中所有 p 的异位词的子串，返回这些子串的起始索引。'
    '异位词指由相同字母重排列形成的字符串（不区分大小写）。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 滑动窗口一次遍历<br>空间：{{c2::O(26)}} — window 和 needs 数组')

add_basic(d, make_front(p, '题解(滑动窗口)'),
    'needCount 跟踪已满足条件的字符种类数，等于 pCount 时窗口是异位词。<br>'
    + code(
        'class Solution {\n'
        '    public List&lt;Integer&gt; findAnagrams(String s, String p) {\n'
        '        int[] window = new int[26], needs = new int[26];\n'
        '        List&lt;Integer&gt; res = new ArrayList&lt;&gt;();\n'
        '        int len1 = p.length(), len2 = s.length();\n'
        '        for (int i = 0; i &lt; len1; i++) {\n'
        '            needs[p.charAt(i) - \'a\']++;\n'
        '        }\n'
        '        int pCount = 0;\n'
        '        for (int i = 0; i &lt; 26; i++) {\n'
        '            if (needs[i] &gt; 0) {\n'
        '                pCount++;\n'
        '            }\n'
        '        }\n'
        '        int left = 0, right = 0;\n'
        '        int needCount = 0;\n'
        '        while (right &lt; len2) {\n'
        '            char ch = s.charAt(right);\n'
        '            right++;\n'
        '            if (needs[ch - \'a\'] &gt; 0) {\n'
        '                window[ch - \'a\']++;\n'
        '                if (window[ch - \'a\'] == needs[ch - \'a\'])\n'
        '                    needCount++;\n'
        '            }\n'
        '            while (right - left &gt;= len1) {\n'
        '                if (needCount == pCount)\n'
        '                    res.add(left);\n'
        '                char remove = s.charAt(left);\n'
        '                left++;\n'
        '                if (needs[remove - \'a\'] &gt; 0) {\n'
        '                    if (window[remove - \'a\'] == needs[remove - \'a\'])\n'
        '                        needCount--;\n'
        '                    window[remove - \'a\']--;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    '滑动窗口解题三步：<br>'
    '1. 扩展右指针（加入新字符，更新 window 和 needCount）<br>'
    '2. 收缩判断（当窗口长度 ≥ p 的长度时，判断 needCount==pCount）<br>'
    '3. 收缩左指针（移出字符，更新 window 和 needCount）<br>'
    '关键优化：不比较整个 needs 和 window 数组，而是用 needCount 跟踪已满足条件的字符种类数。')

# ============================================================
# 14. IP地址与整数的转换
# ============================================================
p = 'IP地址与整数的转换'
d = make_deck(1747301414, f'算法::字符串::{p}')
add_basic(d, make_front(p, '题干'),
    '实现 IPv4 地址与整数的相互转换：'
    'IP→整数：将 IPv4 地址（如 "192.168.1.1"）转换为32位长整数。'
    '整数→IP：将32位长整数转换为 IPv4 地址字符串。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(1)}} — 固定4段<br>空间：{{c2::O(1)}}')

add_basic(d, make_front(p, '题解(IP→整数)'),
    '每段左移8位（&lt;&lt;8），再用 | 拼接当前段。<br>'
    + code(
        'class Solution {\n'
        '    public long ipToInt(String ip) {\n'
        '        String[] segs = ip.split("\\\\.");\n'
        '        long res = 0;\n'
        '        for (int i = 0; i &lt; 4; i++) {\n'
        '            res = (res &lt;&lt; 8) | Integer.parseInt(segs[i]);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(整数→IP)'),
    '每次取低8位（&amp;255），右移8位（&gt;&gt;=8），提取顺序从低位到高位，拼接需逆序。<br>'
    + code(
        'class Solution {\n'
        '    public String intToIp(long num) {\n'
        '        String[] parts = new String[4];\n'
        '        for (int i = 0; i &lt; 4; i++) {\n'
        '            parts[i] = String.valueOf(num &amp; 255);\n'
        '            num &gt;&gt;= 8;\n'
        '        }\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        for (int i = 3; i &gt;= 0; i--) {\n'
        '            sb.append(parts[i]);\n'
        '            if (i != 0) sb.append(".");\n'
        '        }\n'
        '        return sb.toString();\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '关键技巧'),
    'IP 地址本质是32位无符号整数，每段8位（0-255）。<br>'
    'IP→整数：res = (res &lt;&lt; 8) | segment，逐段左移8位并拼接<br>'
    '整数→IP：num &amp; 255 取低8位，num &gt;&gt;= 8 右移，循环4次后逆序输出<br>'
    '注意：Java 中 int 是有符号的，IP 最高段可能 &gt;=128，所以用 long 避免符号问题。')

if __name__ == '__main__':
    print(build('../../牌组/字符串.apkg'))
