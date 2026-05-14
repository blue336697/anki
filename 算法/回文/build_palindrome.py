"""Build APKG for 回文 (Palindrome). 8 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747300700, '算法::回文::原理通识')
add_basic(d0, '回文核心解法',
    '1. 双指针对撞：i=0, j=n-1, while(i&lt;j) 比较首尾字符<br>'
    '2. 中心扩散法：center 从 0 到 2*len-1, left=center/2, right=left+center%2, 向两侧扩展<br>'
    '3. 动态规划：dp[i][j] 表示 s[i..j] 是否为回文，dp[i][j]=s[i]==s[j] && (j-i&lt;2 || dp[i+1][j-1])')
add_cloze(d0, '中心扩散法核心：center 从 0 到 {{c1::2*len-1}}<br>'
    'left = {{c2::center/2}}, right = left + {{c3::center%2}}<br>'
    '奇偶统一：center为偶数时 left==right（奇数长度），奇数时 left+1==right（偶数长度）')
add_basic(d0, '回文串 DP 状态定义',
    'dp[i][j] = s[i..j] 是否为回文串（boolean）<br>'
    '转移：s[i]==s[j] && (j-i&lt;2 || dp[i+1][j-1])<br>'
    '遍历顺序：j 从 0 到 len-1（右边界），i 从 0 到 j（左边界）')

# ============================================================
# 1. 回文子串
# ============================================================
p = '回文子串'
d = make_deck(1747300701, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s，计算这个字符串中有多少个回文子串。'
    '具有不同开始位置或结束位置的子串，即使是由相同的字符组成，也会被视作不同的子串。'
    + img('image.png'))
add_cloze(d, make_front(p, '复杂度'),
    'DP：时间 {{c1::O(n²)}}，空间 {{c2::O(n²)}}<br>'
    '中心扩散：时间 {{c3::O(n²)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(DP)'),
    'dp[i][j] 表示 s[i..j] 是否为回文串。转移：s[i]==s[j] && (j-i&lt;2 || dp[i+1][j-1])。<br>'
    + code(
        'class Solution {\n'
        '    public int countSubstrings(String s) {\n'
        '        int len = s.length();\n'
        '        boolean[][] dp = new boolean[len][len];\n'
        '        int ans = 0;\n'
        '\n'
        '        for (int j = 0; j &lt; len; j++) {\n'
        '            for (int i = 0; i &lt;= j; i++) {\n'
        '                if (s.charAt(i) == s.charAt(j) &amp;&amp; (j - i &lt; 2 || dp[i + 1][j - 1])) {\n'
        '                    dp[i][j] = true;\n'
        '                    ans++;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return ans;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(中心扩散)'),
    'center 从 0 到 2*len-1 统一奇偶，left=center/2, right=left+center%2 向两侧扩展。<br>'
    + code(
        'class Solution {\n'
        '    public int countSubstrings(String s) {\n'
        '        int res = 0, len = s.length();\n'
        '        for (int center = 0; center &lt; len * 2 - 1; center++) {\n'
        '            int left = center / 2;\n'
        '            int right = left + center % 2;\n'
        '            while (left &gt;= 0 &amp;&amp; right &lt; len &amp;&amp; s.charAt(left) == s.charAt(right)) {\n'
        '                res++;\n'
        '                left--;\n'
        '                right++;\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '回文子串问题的三种解法可互相迁移：<br>'
    '1. DP：适合求个数/最长，dp[i][j] 依赖 dp[i+1][j-1]，注意遍历顺序 j 外层 i 内层<br>'
    '2. 中心扩散：center 公式统一奇偶，空间最优 O(1)<br>'
    '3. 马拉车(Manacher)：O(n)，面试较少要求')

# ============================================================
# 2. 最长回文子串
# ============================================================
p = '最长回文子串'
d = make_deck(1747300702, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s，找到 s 中最长的回文子串。' + img('image 1.png'))
add_cloze(d, make_front(p, '复杂度'),
    'DP：时间 {{c1::O(n²)}}，空间 {{c2::O(n²)}}<br>'
    '中心扩散：时间 {{c3::O(n²)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(DP)'),
    'dp[i][j] 表示 s[i..j] 是否为回文串，同时维护 maxLen 和 begin 记录最长结果。<br>'
    + code(
        'class Solution {\n'
        '    public String longestPalindrome(String s) {\n'
        '        int len = s.length();\n'
        '        if (len &lt; 2)\n'
        '            return s;\n'
        '\n'
        '        int maxLen = 1;\n'
        '        int begin = 0;\n'
        '        boolean[][] dp = new boolean[len][len];\n'
        '        for (int i = 0; i &lt; len; i++)\n'
        '            dp[i][i] = true;\n'
        '        char[] chars = s.toCharArray();\n'
        '\n'
        '        for (int j = 1; j &lt; len; j++) {\n'
        '            for (int i = 0; i &lt; j; i++) {\n'
        '                if (chars[i] != chars[j])\n'
        '                    dp[i][j] = false;\n'
        '                else {\n'
        '                    if (j - i &lt; 3)\n'
        '                        dp[i][j] = true;\n'
        '                    else\n'
        '                        dp[i][j] = dp[i + 1][j - 1];\n'
        '                }\n'
        '                if (dp[i][j] &amp;&amp; j - i + 1 &gt; maxLen) {\n'
        '                    maxLen = j - i + 1;\n'
        '                    begin = i;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return s.substring(begin, begin + maxLen);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(中心扩散)'),
    '极致版：复用 center 公式统一奇偶，每次扩散成功时尝试更新最长结果。<br>'
    + code(
        'class Solution {\n'
        '    public String longestPalindrome(String s) {\n'
        '        int len = s.length();\n'
        '        String result = "";\n'
        '\n'
        '        for (int i = 0; i &lt; len * 2 - 1; i++) {\n'
        '            int left = i / 2;\n'
        '            int right = left + i % 2;\n'
        '            while (left &gt;= 0 &amp;&amp; right &lt; len &amp;&amp; s.charAt(left) == s.charAt(right)) {\n'
        '                String tmp = s.substring(left, right + 1);\n'
        '                if (tmp.length() &gt; result.length()) {\n'
        '                    result = tmp;\n'
        '                }\n'
        '                left--;\n'
        '                right++;\n'
        '            }\n'
        '        }\n'
        '        return result;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '回文子串问题的三种解法可互相迁移：<br>'
    '1. DP：适合求个数/最长，dp[i][j] 依赖 dp[i+1][j-1]，注意遍历顺序 j 外层 i 内层<br>'
    '2. 中心扩散：center 公式统一奇偶，空间最优 O(1)<br>'
    '3. 马拉车(Manacher)：O(n)，面试较少要求')

# ============================================================
# 3. 分割回文串
# ============================================================
p = '分割回文串'
d = make_deck(1747300703, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s，将 s 分割成一些子串，使每个子串都是回文串。返回 s 所有可能的分割方案。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n * 2^n)}} — 每个位置可切可不切，每次判断回文O(n)<br>'
    '优化：预处理 dp[i][j] → O(2^n)<br>空间：{{c2::O(n)}} — 递归深度')
add_basic(d, make_front(p, '题解(回溯+回文判断)'),
    '回溯框架：startIndex 控制切割起点，isPalindrome 判断子串是否回文，是则加入路径继续递归。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;List&lt;String&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '    Deque&lt;String&gt; list = new LinkedList&lt;&gt;();\n'
        '\n'
        '    public List&lt;List&lt;String&gt;&gt; partition(String s) {\n'
        '        dfs(s, 0);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void dfs(String s, int startIndex) {\n'
        '        if (startIndex &gt;= s.length()) {\n'
        '            res.add(new ArrayList&lt;&gt;(list));\n'
        '            return;\n'
        '        }\n'
        '        for (int i = startIndex; i &lt; s.length(); i++) {\n'
        '            if (isPalindrome(s, startIndex, i)) {\n'
        '                String temp = s.substring(startIndex, i + 1);\n'
        '                list.add(temp);\n'
        '            } else\n'
        '                continue;\n'
        '            dfs(s, i + 1);\n'
        '            list.removeLast();\n'
        '        }\n'
        '    }\n'
        '\n'
        '    private boolean isPalindrome(String s, int startIndex, int end) {\n'
        '        for (int i = startIndex, j = end; i &lt; j; i++, j--) {\n'
        '            if (s.charAt(i) != s.charAt(j)) {\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '回溯+回文判断的组合题型。<br>'
    '优化：预处理 dp[i][j] 使回文判断 O(1)，整体从 O(n*2^n) 降到 O(2^n)。')

# ============================================================
# 4. 最长回文子序列
# ============================================================
p = '最长回文子序列'
d = make_deck(1747300704, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s，找出其中最长的回文子序列的长度。子序列不要求连续。')
add_cloze(d, make_front(p, '复杂度'),
    'LCS 法：时间 {{c1::O(n²)}}，空间 {{c2::O(n²)}}<br>'
    '区间DP：时间 {{c3::O(n²)}}，空间 {{c4::O(n²)}}<br>'
    '核心区别：子序列不连续，dp[i][j] 不要求 s[i]==s[j]')
add_basic(d, make_front(p, '题解(LCS 法)'),
    '将 s 与 reverse(s) 求最长公共子序列。巧妙利用回文对称性：正着反着读一样。<br>'
    + code(
        'class Solution {\n'
        '    public int longestPalindromeSubseq(String s) {\n'
        '        int len = s.length();\n'
        '        if (len == 0)\n'
        '            return 0;\n'
        '        if (len == 1)\n'
        '            return 1;\n'
        '\n'
        '        int[][] dp = new int[len + 1][len + 1];\n'
        '        String s2 = reverse(s);\n'
        '        for (int i = 1; i &lt;= len; i++) {\n'
        '            for (int j = 1; j &lt;= len; j++) {\n'
        '                if (s.charAt(i - 1) == s2.charAt(j - 1))\n'
        '                    dp[i][j] = dp[i - 1][j - 1] + 1;\n'
        '                else\n'
        '                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);\n'
        '            }\n'
        '        }\n'
        '        return dp[len][len];\n'
        '    }\n'
        '\n'
        '    public String reverse(String s) {\n'
        '        char[] chars = s.toCharArray();\n'
        '        int i = 0, j = chars.length - 1;\n'
        '        while (i &lt; j) {\n'
        '            char temp = chars[i];\n'
        '            chars[i] = chars[j];\n'
        '            chars[j] = temp;\n'
        '            i++;\n'
        '            j--;\n'
        '        }\n'
        '        return new String(chars);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(区间DP)'),
    'dp[i][j] 定义为 s[i..j] 的最长回文子序列长度。s[i]==s[j] 时 +2，不等时取左右较大者。<br>'
    + code(
        'class Solution {\n'
        '    public int longestPalindromeSubseq(String s) {\n'
        '        int len = s.length();\n'
        '        int[][] dp = new int[len][len];\n'
        '        for (int i = 0; i &lt; len; i++) {\n'
        '            dp[i][i] = 1;\n'
        '        }\n'
        '        for (int i = len - 1; i &gt;= 0; i--) {\n'
        '            for (int j = i + 1; j &lt; len; j++) {\n'
        '                if (s.charAt(i) == s.charAt(j))\n'
        '                    dp[i][j] = dp[i + 1][j - 1] + 2;\n'
        '                else\n'
        '                    dp[i][j] = Math.max(dp[i + 1][j], dp[i][j - 1]);\n'
        '            }\n'
        '        }\n'
        '        return dp[0][len - 1];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '方法1：s 与 reverse(s) 求 LCS（最长公共子序列），巧妙利用回文对称性。<br>'
    '方法2：区间 DP，dp[i][j] 定义为 s[i..j] 的最长回文子序列长度。<br>'
    '与最长回文子串区别：子序列不要求连续，不等时可以跳过一侧继续。')

# ============================================================
# 5. 验证回文串
# ============================================================
p = '验证回文串'
d = make_deck(1747300705, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串，验证它是否是回文串，只考虑字母和数字字符，可以忽略字母的大小写。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 双指针一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(双指针+过滤)'),
    '双指针跳过非字母数字字符，& 0xDF 将小写转大写统一比较。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isPalindrome(String s) {\n'
        '        char[] ss = s.toCharArray();\n'
        '        int len = ss.length, i = 0, j = len - 1;\n'
        '        while (i &lt; j) {\n'
        '            while (i &lt; j &amp;&amp; !Character.isLetterOrDigit(ss[i]))\n'
        '                ++i;\n'
        '            while (i &lt; j &amp;&amp; !Character.isLetterOrDigit(ss[j]))\n'
        '                --j;\n'
        '            if ((ss[i++] &amp; 0xDF) != (ss[j--] &amp; 0xDF))\n'
        '                return false;\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '双指针+跳过非字母数字字符。<br>'
    '字符大小写统一：& 0xDF（小写转大写）或 Character.toLowerCase()。<br>'
    '基础模板：isPalindrome(s, start, end) — 双指针从两端向中间比较。')

# ============================================================
# 6. 验证回文字符串 Ⅱ
# ============================================================
p = '验证回文字符串 Ⅱ'
d = make_deck(1747300706, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非空字符串 s，最多删除一个字符。判断是否能成为回文字符串。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 最多调用两次 isPalindrome<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(双指针+贪心)'),
    '遇到不匹配时，尝试删除左边或右边一个字符，剩余部分必须是回文。<br>'
    + code(
        'class Solution {\n'
        '    public boolean validPalindrome(String s) {\n'
        '        int begin = 0;\n'
        '        int end = s.length() - 1;\n'
        '        while (begin &lt; end) {\n'
        '            if (s.charAt(begin) != s.charAt(end))\n'
        '                return isPalindrome(s, begin + 1, end)\n'
        '                    || isPalindrome(s, begin, end - 1);\n'
        '            begin++;\n'
        '            end--;\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '\n'
        '    private boolean isPalindrome(String s, int startIndex, int end) {\n'
        '        for (int i = startIndex, j = end; i &lt; j; i++, j--) {\n'
        '            if (s.charAt(i) != s.charAt(j)) {\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '关键：当 s[begin]!=s[end] 时，有两种可能：删除 begin 或删除 end。<br>'
    '只需检查 s[begin+1..end] 或 s[begin..end-1] 是否为回文。<br>'
    '不需要继续递归删除，因为题目只允许删除一次。')

# ============================================================
# 7. 回文数
# ============================================================
p = '回文数'
d = make_deck(1747300707, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '判断一个整数是否是回文数。回文数是指正序和倒序读都是一样的整数。'
    + img('image 2.png') + img('image 3.png'))
add_cloze(d, make_front(p, '复杂度'),
    '全反转法：时间 {{c1::O(log n)}}，空间 {{c2::O(1)}}<br>'
    '半反转法：时间 {{c3::O(log n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(全反转)'),
    '将整数完全反转后与原数比较，注意处理溢出和不合法输入。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isPalindrome(int x) {\n'
        '        if (x &lt; 0 || x &gt; Integer.MAX_VALUE)\n'
        '            return false;\n'
        '        int i = 0, j = 0;\n'
        '        int temp = x;\n'
        '        while (temp != 0) {\n'
        '            i = temp % 10;\n'
        '            j = j * 10 + i;\n'
        '            temp /= 10;\n'
        '        }\n'
        '        return j == x;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(半反转)'),
    '只反转数字的后半部分，与前半部分比较。偶数位完全相等，奇数位去掉中间位。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isPalindrome(int x) {\n'
        '        if (x &lt; 0 || (x % 10 == 0 &amp;&amp; x != 0))\n'
        '            return false;\n'
        '        int revertedNumber = 0;\n'
        '        while (x &gt; revertedNumber) {\n'
        '            revertedNumber = revertedNumber * 10 + x % 10;\n'
        '            x /= 10;\n'
        '        }\n'
        '        return revertedNumber == x || revertedNumber / 10 == x;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '半反转法：只反转数字的后半部分，与前半部分比较。<br>'
    '退出条件 x &lt;= revertedNumber 表示已经处理了一半以上。<br>'
    '特殊情况：负数不是回文；末位为0的非零数不是回文。')

# ============================================================
# 8. 回文链表
# ============================================================
p = '回文链表'
d = make_deck(1747300708, f'算法::回文::{p}')
add_basic(d, make_front(p, '题干'),
    '判断一个链表是否为回文链表。' + img('image 4.png'))
add_cloze(d, make_front(p, '复杂度'),
    '数组法：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    '快慢指针+反转：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(数组+双指针)'),
    '将链表值复制到 ArrayList，然后用双指针从两端向中间判断回文。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isPalindrome(ListNode head) {\n'
        '        List&lt;Integer&gt; vals = new ArrayList&lt;Integer&gt;();\n'
        '\n'
        '        ListNode currentNode = head;\n'
        '        while (currentNode != null) {\n'
        '            vals.add(currentNode.val);\n'
        '            currentNode = currentNode.next;\n'
        '        }\n'
        '\n'
        '        int front = 0;\n'
        '        int back = vals.size() - 1;\n'
        '        while (front &lt; back) {\n'
        '            if (!vals.get(front).equals(vals.get(back))) {\n'
        '                return false;\n'
        '            }\n'
        '            front++;\n'
        '            back--;\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'O(1)空间解法：快慢指针找中点 → 反转后半部分 → 双指针比较前后两部分 → 还原链表。<br>'
    '注意：反转后比较时，odd长度链表中间节点不需要比较（被包含在反转部分中）。')

if __name__ == '__main__':
    print(build('../../牌组/回文.apkg'))
