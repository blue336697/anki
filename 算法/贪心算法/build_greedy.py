"""Build APKG for 贪心算法 (Greedy). 9 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747300900, '算法::贪心算法::原理通识')
add_basic(d0, '贪心算法核心思想',
    '贪心算法：每一步都选择当前看起来最优的选择（局部最优），期望最终达到全局最优。<br>'
    '关键三要素：<br>'
    '1. 贪心选择性质：局部最优能导致全局最优<br>'
    '2. 最优子结构：问题的最优解包含子问题的最优解<br>'
    '3. 贪心策略选择：根据问题特点选择合适的贪心策略')
add_cloze(d0, '贪心常见策略分类',
    '1. 区间调度：按{{c1::结束时间}}排序，每次选最早结束的<br>'
    '2. 跳跃游戏：维护{{c2::最远可达距离}}，逐步扩展边界<br>'
    '3. 排序贪心：自定义{{c3::比较器}}，按拼接/组合结果排序<br>'
    '4. 双指针贪心：记录{{c4::字符最后出现位置}}，划分区间')
add_basic(d0, '贪心 vs 动态规划',
    '贪心：每步选局部最优，不回退，通常更快（O(n)或O(n log n)）<br>'
    'DP：记录所有子问题状态，通过状态转移得到最优解<br>'
    '判断标准：问题是否具有贪心选择性质？（局部最优→全局最优）<br>'
    '反例：0-1背包不能用贪心，因为物品不可分割')

# ============================================================
# 1. 跳跃游戏
# ============================================================
p = '跳跃游戏'
d = make_deck(1747300901, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非负整数数组 nums，你最初位于数组的第一个下标。'
    '数组中的每个元素代表你在该位置可以跳跃的最大长度。'
    '判断你是否能够到达最后一个下标。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历，维护最远可达距离<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(贪心)'),
    '维护最远可达距离 temp，当 i &gt; temp 时说明当前位置不可达。<br>'
    + code(
        'class Solution {\n'
        '    public boolean canJump(int[] nums) {\n'
        '        int i = 0, temp = 0, n = nums.length;\n'
        '        while (i &lt; n) {\n'
        '            if (i &gt; temp)\n'
        '                return false;\n'
        '            // 这一步可以防止有循环0的出现\n'
        '            // 出现循环0，temp得不到更新，i就会大于temp返回false\n'
        '            // 又能允许形如 [2,5,0,0] 的数组通过\n'
        '            temp = Math.max(temp, i + nums[i++]);\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心：维护最远可达距离 temp = max(temp, i + nums[i])<br>'
    '当 i &gt; temp 时说明当前位置不可达，返回 false。<br>'
    'temp 得不到更新+出现0时自然卡住，巧妙处理了「循环0」的情况。')

# ============================================================
# 2. 跳跃游戏 II
# ============================================================
p = '跳跃游戏 II'
d = make_deck(1747300902, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非负整数数组 nums，你最初位于数组的第一个下标。'
    '数组中的每个元素代表你在该位置可以跳跃的最大长度。'
    '返回到达最后一个下标的最小跳跃次数。' + img('image.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(贪心 BFS层扩展)'),
    'BFS式的层扩展：每次在当前跳跃范围 [start, end] 内找下一跳的最远位置。<br>'
    + code(
        'class Solution {\n'
        '    public int jump(int[] nums) {\n'
        '        // 无论怎么样第一次起跳的起点都是第一个，\n'
        '        // 然后根据第一个的跳跃距离，在第二次起跳的距离里面选最大的\n'
        '        // 例如：[2,3,1,1,4]，第一次最多能跳两格，所以第二次起跳的起点可以是3或者1\n'
        '        // 在第二次开始就要贪心选跳最远的，所以肯定选3\n'
        '        int start = 0, end = 0, n = nums.length, res = 0;\n'
        '\n'
        '        while (end &lt; n - 1) {\n'
        '            int maxPos = 0;\n'
        '            for (int k = start; k &lt;= end; k++) {\n'
        '                // k + nums[k]：当前位置+最大的跳动距离就是最后的落点\n'
        '                maxPos = Math.max(k + nums[k], maxPos);\n'
        '            }\n'
        '            // 下一次起跳范围的起点\n'
        '            start = end + 1;\n'
        '            // 下一次起跳范围的终点\n'
        '            end = maxPos;\n'
        '            res++;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(贪心 优化)'),
    '优化：一次遍历，当 i == end 时表示当前层结束，步数+1。<br>'
    + code(
        'class Solution {\n'
        '    public int jump(int[] nums) {\n'
        '        int end = 0, res = 0, maxPos = 0;\n'
        '        // 这里之所以不让 i 等于最后一个，会在已经到达终点的情况下重复计算一次\n'
        '        for (int i = 0; i &lt; nums.length - 1; i++) {\n'
        '            maxPos = Math.max(maxPos, i + nums[i]);\n'
        '\n'
        '            if (end == i) {\n'
        '                end = maxPos;\n'
        '                res++;\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 3. 整数转罗马数字
# ============================================================
p = '整数转罗马数字'
d = make_deck(1747300903, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数，将其转为罗马数字。'
    '输入范围：1 &lt;= num &lt;= 3999。<br>'
    '规则：1=I, 5=V, 10=X, 50=L, 100=C, 500=D, 1000=M。<br>'
    '特殊规则：4=IV, 9=IX, 40=XL, 90=XC, 400=CD, 900=CM。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(1)}} — 固定13个面值，最多循环13*3次<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(贪心)'),
    '贪心：按面值从大到小，每次选不大于 num 的最大面值，注意用 &gt;= 而非 &gt;。<br>'
    + code(
        'class Solution {\n'
        '    public String intToRoman(int num) {\n'
        '        // 组成罗马数字的最基本的字符组成单元罗列如下\n'
        '        // 把阿拉伯数字与罗马数字可能出现的所有情况和对应关系，放在两个数组中\n'
        '        // 按照阿拉伯数字的大小降序排列\n'
        '        int[] nums = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};\n'
        '        String[] romans = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};\n'
        '\n'
        '        StringBuilder stringBuilder = new StringBuilder();\n'
        '        int index = 0;\n'
        '        while (index &lt; 13) {\n'
        '            // 特别注意：这里是等号\n'
        '            while (num &gt;= nums[index]) {\n'
        '                stringBuilder.append(romans[index]);\n'
        '                num -= nums[index];\n'
        '            }\n'
        '            index++;\n'
        '        }\n'
        '        return stringBuilder.toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '贪心策略：按面值从大到小，每次减去能减的最大面值。<br>'
    '关键：需要包含 900, 400, 90, 40, 9, 4 这些减法组合面值。<br>'
    '这些特殊面值各只允许出现一次（如1800=MDCCC，不是CMCM）。')

# ============================================================
# 4. 划分字母区间
# ============================================================
p = '划分字母区间'
d = make_deck(1747300904, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个字符串 s。我们要把这个字符串划分为尽可能多的片段，'
    '同一字母最多出现在一个片段中。返回一个表示每个字符串片段的长度的列表。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 两次遍历字符串<br>空间：{{c2::O(26)}} — farthestPos 数组')
add_basic(d, make_front(p, '题解(贪心+双指针)'),
    '先记录每个字符最后出现位置，遍历时维护已扫描字符的最远位置。当 i==最远位置时切分。<br>'
    + code(
        'class Solution {\n'
        '    public List&lt;Integer&gt; partitionLabels(String s) {\n'
        '        int[] farthestPos = new int[26];\n'
        '        int len = s.length();\n'
        '        // 记录字符出现的最后位置（最远位置）\n'
        '        for (int i = 0; i &lt; len; i++) {\n'
        '            farthestPos[s.charAt(i) - \'a\'] = i;\n'
        '        }\n'
        '\n'
        '        List&lt;Integer&gt; res = new ArrayList&lt;&gt;();\n'
        '        int start = 0;                        // 待切割的起始位置\n'
        '        int scannedCharMaxPos = 0;            // 已扫描的字符中最远的位置\n'
        '\n'
        '        for (int i = 0; i &lt; len; i++) {\n'
        '            int curCharMaxPos = farthestPos[s.charAt(i) - \'a\'];\n'
        '            // 取几个字符中最远的，因为当前字符段要包含某个字符的全部字符\n'
        '            // 更新「已扫描的字符中最远的位置」\n'
        '            scannedCharMaxPos = Math.max(scannedCharMaxPos, curCharMaxPos);\n'
        '            if (i == scannedCharMaxPos) {\n'
        '                res.add(i - start + 1);\n'
        '                start = i + 1;\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '贪心策略：先记录每个字符最后出现的位置 → 遍历时维护已扫描字符的最远位置 → '
    '当 i==最远位置时切分。<br>'
    '本质：每个片段必须包含其中所有字符的全部出现，所以片段的右边界是所有字符最远位置的最大值。')

# ============================================================
# 5. 加油站
# ============================================================
p = '加油站'
d = make_deck(1747300905, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '在一条环路上有 n 个加油站，第 i 个加油站有汽油 gas[i] 升。'
    '从第 i 个加油站开往第 i+1 个需要消耗汽油 cost[i] 升。'
    '找出可以绕环路行驶一周的出发加油站编号，不存在则返回 -1。'
    + img('image 1.png') + img('image 2.png') + img('image 3.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(贪心-最低点法)'),
    '找到累积剩余油量最低点 minSpare，其下一个位置 (minIndex+1)%len 即为起点。<br>'
    + code(
        'class Solution {\n'
        '    public int canCompleteCircuit(int[] gas, int[] cost) {\n'
        '        if (gas.length == 0 || cost.length == 0)\n'
        '            return -1;\n'
        '        int len = gas.length;\n'
        '        // 剩余油量\n'
        '        int spare = 0;\n'
        '        int minSpare = Integer.MAX_VALUE;\n'
        '        int minIndex = 0;\n'
        '        for (int i = 0; i &lt; gas.length; i++) {\n'
        '            spare += gas[i] - cost[i];\n'
        '            // 记录剩余油量的最小值\n'
        '            if (spare &lt; minSpare) {\n'
        '                minSpare = spare;\n'
        '                minIndex = i;\n'
        '            }\n'
        '        }\n'
        '        // 如果最后剩余油量小于0，那么也就是说不成环了\n'
        '        // 不小于0，则返回更新加油站的索引，此时按照题目的例子应该是3号\n'
        '        // 但是我们的索引2点意思就是2到3，所以需要额外处理\n'
        '        return spare &lt; 0 ? -1 : (minIndex + 1) % len;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '关键理解：如果总剩余油量 spare &gt;= 0，则一定存在解。<br>'
    '找到累积剩余油量的最低点 minSpare，其下一个位置 (minIndex+1)%len 即为起点。<br>'
    '理解：最低点之后到终点这一段一定不会再低于0，因为最低点之后都在回升。')

# ============================================================
# 6. 最大数
# ============================================================
p = '最大数'
d = make_deck(1747300906, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一组非负整数 nums，重新排列每个数的顺序（每个数不可拆分）使之组成一个最大的整数。'
    + img('image 4.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n log n)}} — 排序开销<br>空间：{{c2::O(n)}} — 字符串数组')
add_basic(d, make_front(p, '题解(排序贪心)'),
    '自定义排序：对于 a 和 b，比较拼接结果 ba 和 ab，ba 更大则 b 排前面（降序）。<br>'
    + code(
        'public class Solution {\n'
        '    public static String largestNumber(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return "";\n'
        '        int len = nums.length;\n'
        '        String[] sa = new String[len];\n'
        '        for (int i = 0; i &lt; len; i++)\n'
        '            sa[i] = "" + nums[i];\n'
        '        // 这里就是使用贪心算法，比较两个元素组合起来的最大值\n'
        '        Arrays.sort(sa, (a, b) -&gt; {\n'
        '            String ab = a + b, ba = b + a;\n'
        '            return ba.compareTo(ab);\n'
        '        });\n'
        '\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        for (String num : sa)\n'
        '            sb.append(num);\n'
        '\n'
        '        int length = sb.length();\n'
        '        int k = 0;\n'
        '        while (k &lt; length - 1 && sb.charAt(k) == \'0\') k++;\n'
        '        return sb.substring(k);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '自定义排序：对于 a 和 b，比较 ab 和 ba 的拼接结果。<br>'
    '若 b+a &gt; a+b（字典序），则 b 应该排在 a 前面（降序）。<br>'
    '边界：全0数组应返回"0"而非"00...0"，需要去除前导0。')

# ============================================================
# 7. 把数组排成最小的数
# ============================================================
p = '把数组排成最小的数'
d = make_deck(1747300907, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '输入一个非负整数数组，把数组里所有数字拼接起来排成一个数，'
    '打印能拼接出的所有数字中最小的一个。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n log n)}} — 排序开销<br>空间：{{c2::O(n)}} — 字符串数组')
add_basic(d, make_front(p, '题解(排序贪心)'),
    '自定义排序：对于 a 和 b，比较拼接结果 ab 和 ba，ab 更小则 a 排前面（升序）。<br>'
    + code(
        'class Solution {\n'
        '    public String minNumber(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return null;\n'
        '        int n = nums.length;\n'
        '        String[] strArr = new String[n];\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            strArr[i] = "" + nums[i];\n'
        '        }\n'
        '\n'
        '        // 比较两个值的大小\n'
        '        // 这里就是使用贪心算法，比较两个元素组合起来的最小值\n'
        '        /**\n'
        '         * 这里说一下compareTo方法的返回值，是返回两个字符串的ASCII码差值\n'
        '         * 这里ab.compareTo(ba)就相当于ab - ba 即返回ASCII差值的升序\n'
        '         * 反之ba.compareTo(ab)则为降序\n'
        '         */\n'
        '        Arrays.sort(strArr, (a, b) -&gt; {\n'
        '            String ab = a + b, ba = b + a;\n'
        '            // 这里如果是ab在前就是升序，也就是最小值，根据上面的解释我们就需要升序\n'
        '            return ab.compareTo(ba);\n'
        '        });\n'
        '\n'
        '        for (String item : strArr)\n'
        '            sb.append(item);\n'
        '        return sb.toString();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '与「最大数」相反：比较 a+b 和 b+a。<br>'
    '若 a+b &lt; b+a（字典序升序），则 a 排在 b 前面。使用 (a+b).compareTo(b+a)。<br>'
    '两题本质相同，仅在排序方向不同：最大数用降序，最小数用升序。')

# ============================================================
# 8. 最大交换
# ============================================================
p = '最大交换'
d = make_deck(1747300908, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非负整数，你至多可以交换一次数字中的任意两位。返回你能得到的最大值。')
add_cloze(d, make_front(p, '复杂度'),
    '暴力法：时间 {{c1::O(n²)}}，空间 {{c2::O(n)}}<br>'
    '贪心优化：时间 {{c3::O(n)}}，空间 {{c4::O(10)}} — last 数组记录每个数字最后出现位置')
add_basic(d, make_front(p, '题解(贪心)'),
    '从高位到低位，在右侧找比当前位大且最大的数交换（多个相同时选最靠后的）。<br>'
    + code(
        'class Solution {\n'
        '    public int maximumSwap(int num) {\n'
        '        char[] chars = String.valueOf(num).toCharArray();\n'
        '        for (int i = 0; i &lt; chars.length; i++) {\n'
        '            // 当前字符\n'
        '            int cur = chars[i] - \'0\';\n'
        '            // 找到暂时最大的：例如98368来说，你如果只找到9的话不进行更换\n'
        '            // 最后还有一个第二大的8呢\n'
        '            int max = Integer.MIN_VALUE;\n'
        '            // 记录暂时那个最大的值的索引\n'
        '            int index = -1;\n'
        '            // 第二个指针开始从i的后面继续遍历\n'
        '            // 这里如果是前一段已经是升序排列的就直接跳过\n'
        '            // 那么max和index都没得到更新也就进入不了下面的循环\n'
        '            for (int j = i + 1; j &lt; chars.length; j++) {\n'
        '                int cmp = chars[j] - \'0\';\n'
        '                // 比较当前的和j对应的元素值\n'
        '                // 在拿上面的98368，一直会跳过98，直到i=2和j=4就会循环得到更新\n'
        '                if (cmp &gt; cur && cmp &gt;= max) {\n'
        '                    // 符合条件就更新最大的值\n'
        '                    max = cmp;\n'
        '                    // 将最大的值的索引记录\n'
        '                    index = j;\n'
        '                }\n'
        '            }\n'
        '            // 这个符合max被更新过，index也被更新过\n'
        '            // 防止到最后直接什么都没变就不会进入循环\n'
        '            if (max != Integer.MIN_VALUE && index != -1) {\n'
        '                char temp = chars[i];\n'
        '                chars[i] = chars[index];\n'
        '                chars[index] = temp;\n'
        '                StringBuilder sb = new StringBuilder();\n'
        '                for (int k = 0; k &lt; chars.length; k++)\n'
        '                    sb.append(chars[k]);\n'
        '                return Integer.parseInt(sb.toString());\n'
        '            }\n'
        '        }\n'
        '        return num;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '贪心策略：从高位开始，每次在右侧找一个最大的数交换。<br>'
    '注意：若有多个相同最大值，选最靠后的（cmp &gt;= max），因为交换后同样大的数越靠后结果越大。<br>'
    '技巧：预处理 last[10] 数组记录每个数字最后出现位置，可从 O(n²) 优化到 O(n)。')

# ============================================================
# 9. 最长连续递增序列
# ============================================================
p = '最长连续递增序列'
d = make_deck(1747300909, f'算法::贪心算法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个未经排序的整数数组，找到最长且连续递增的子序列，并返回该序列的长度。')
add_cloze(d, make_front(p, '复杂度'),
    'DP：时间 {{c1::O(n)}}，空间 {{c2::O(n)}}<br>'
    '贪心：时间 {{c3::O(n)}}，空间 {{c4::O(1)}}')
add_basic(d, make_front(p, '题解(动态规划)'),
    'dp[i] 表示以 nums[i] 结尾的最长连续递增序列的长度。若递增则 dp[i]=dp[i-1]+1。<br>'
    + code(
        'class Solution {\n'
        '    public int findLengthOfLCIS(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        if (len &lt;= 0)\n'
        '            return 0;\n'
        '        // dp[i]是以nums[i]结尾的最长连续递增序列的长度\n'
        '        int[] dp = new int[len];\n'
        '        // 初始化值为1，没有连续的自身为1\n'
        '        Arrays.fill(dp, 1);\n'
        '        int res = 0;\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            // 如果没有满足条件就直接跳过，该值在下一次被用到也是原始值\n'
        '            // 相当于分隔了\n'
        '            if (nums[i] &gt; nums[i - 1])\n'
        '                dp[i] = dp[i - 1] + 1;\n'
        '            res = res &gt; dp[i] ? res : dp[i];\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(贪心)'),
    '维护当前递增长度 curLength，不满足条件时重置为 1，贪心的"断点分隔"思想。<br>'
    + code(
        'class Solution {\n'
        '    public int findLengthOfLCIS(int[] nums) {\n'
        '        int curLength = 1;\n'
        '        int ans = 1;\n'
        '        for (int i = 1; i &lt; nums.length; i++) {\n'
        '            if (nums[i] &gt; nums[i - 1]) {\n'
        '                curLength++;\n'
        '            } else {\n'
        '                curLength = 1;\n'
        '            }\n'
        '            ans = Math.max(ans, curLength);\n'
        '        }\n'
        '        return ans;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '贪心 vs DP：<br>'
    'DP：dp[i] 表示以 i 结尾的最长连续递增长度，若递增则 dp[i]=dp[i-1]+1<br>'
    '贪心：维护当前递增长度 curLength，不满足条件时重置为 1<br>'
    '贪心更简洁，空间 O(1)，因为当前状态只依赖前一个元素。')

if __name__ == '__main__':
    print(build('../../牌组/算法/贪心算法.apkg'))
