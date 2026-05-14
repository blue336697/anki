"""Build APKG for 回溯法 (Backtracking). 13 problems, full-code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747300200, '算法::回溯法::原理通识')
add_basic(d0, '回溯法核心框架',
    '回溯 = DFS + 状态重置<br>'
    '模板：<br>'
    '1. 选择列表：for 选择 in 选择列表<br>'
    '2. 做选择<br>'
    '3. 递归进入下一层<br>'
    '4. 撤销选择（回溯）<br>'
    '剪枝策略：排序+跳过重复、break提前终止、used数组标记')
add_cloze(d0, '回溯三要素：{{c1::路径（已选）}}、{{c2::选择列表（可选）}}、{{c3::终止条件}}', '回溯本质是决策树的DFS遍历')
add_basic(d0, '排列 vs 组合 vs 子集',
    '排列：顺序有关，used[]数组去重，全排列O(n!)<br>'
    '组合：顺序无关，begin索引去重，每次从begin开始选<br>'
    '子集：收集所有节点（不止叶子），res.add()在进入时立即收集')
add_basic(d0, '回溯去重总结',
    '同层去重（剪枝）：i>0 && nums[i]==nums[i-1] && !used[i-1] → continue<br>'
    '同枝去重（防重复使用）：used[i]标记，回溯时used[i]=false<br>'
    '组合去重：begin索引，每层从i+1或i开始')

# --- Problem decks ---

# ============================================================
# 1. 全排列
# ============================================================
p = '全排列'
d = make_deck(1747300201, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个不含重复数字的数组 nums，返回其所有可能的全排列。' + img('image.png'))
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::nums}}<br>'
    '通过 {{c2::list.contains(num)}} 判断当前元素是否已选，避免同一树枝重复使用')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::list.size() == nums.length}}<br>'
    '剪枝策略：{{c2::跳过 list 中已包含的元素}}（无重复元素，无需排序去重）')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n!)}} — n的全排列数<br>空间：{{c2::O(n)}} — 递归深度')
add_basic(d, make_front(p, '题解(回溯)'),
    '排列：不设begin，每次从0开始选，靠list.contains去重。<br>'
    + code(
        'class Solution {\n'
        '    public List&lt;List&lt;Integer&gt;&gt; permute(int[] nums) {\n'
        '        List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '        if (nums.length == 1) {\n'
        '            res.add(new ArrayList&lt;Integer&gt;(Arrays.asList(nums[0])));\n'
        '            return res;\n'
        '        }\n'
        '        List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
        '        backtrack(res, list, nums);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void backtrack(List&lt;List&lt;Integer&gt;&gt; res, List&lt;Integer&gt; list, int[] nums) {\n'
        '        if (list.size() == nums.length) {\n'
        '            res.add(new ArrayList&lt;&gt;(list));\n'
        '            return;\n'
        '        }\n'
        '        for (int num : nums) {\n'
        '            if (!list.contains(num)) {\n'
        '                list.add(num);\n'
        '                backtrack(res, list, nums);\n'
        '                list.remove(list.size() - 1);\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '排列问题不设begin索引，每层从0开始遍历全部元素。<br>'
    'list.contains(num) 防同枝重复：因为不含重复数字，只需判断是否已选。<br>'
    '回溯时 list.remove(list.size()-1) 恢复状态。')

# ============================================================
# 2. 全排列 II
# ============================================================
p = '全排列 II'
d = make_deck(1747300202, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个可包含重复数字的序列 nums，按任意顺序返回所有不重复的全排列。'
    + img('image 1.png'))
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::nums}}<br>'
    '去重关键：{{c2::排序后}}用 used[i] 数组标记，{{c3::同层跳过相同元素}}')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::list.size() == nums.length}}<br>'
    '剪枝策略：{{c2::i>0 && nums[i]==nums[i-1] && !used[i-1]}} → continue（同层去重）<br>'
    '{{c3::used[i]}} 标记同一树枝已使用的元素')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n!)}} — 最坏情况<br>空间：{{c2::O(n)}} — 递归深度+used数组')
add_basic(d, make_front(p, '题解(回溯+剪枝)'),
    '排序后用used数组防同层重复和同枝重复。used[i-1]==false表示同层已用过。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '    public List&lt;List&lt;Integer&gt;&gt; permuteUnique(int[] nums) {\n'
        '        if (nums.length == 1) {\n'
        '            res.add(new ArrayList&lt;Integer&gt;(Arrays.asList(nums[0])));\n'
        '            return res;\n'
        '        }\n'
        '        List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
        '        boolean[] used = new boolean[nums.length];\n'
        '        Arrays.sort(nums);\n'
        '        back(list, nums, used);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void back(List&lt;Integer&gt; list, int[] nums, boolean[] used) {\n'
        '        if (list.size() == nums.length) {\n'
        '            res.add(new ArrayList&lt;&gt;(list));\n'
        '            return;\n'
        '        }\n'
        '        for (int i = 0; i &lt; nums.length; i++) {\n'
        '            if (i &gt; 0 && nums[i] == nums[i - 1] && used[i - 1] == false)\n'
        '                continue;\n'
        '            if (used[i] == false) {\n'
        '                used[i] = true;\n'
        '                list.add(nums[i]);\n'
        '                back(list, nums, used);\n'
        '                list.remove(list.size() - 1);\n'
        '                used[i] = false;\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '对比'),
    '与全排列 I 的区别：I 无重复元素，只需 list.contains 防同枝重复；<br>'
    'II 有重复元素，需排序+used数组同时防同层重复和同枝重复。<br>'
    '与字符串的排列：完全相同的模板，只是处理 char[] 而非 int[]。')

# ============================================================
# 3. 复原IP地址
# ============================================================
p = '复原IP地址'
d = make_deck(1747300203, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个只包含数字的字符串 s，用以表示一个 IP 地址，返回所有可能的有效 IP 地址。'
    'IP 地址由 4 个 0~255 之间的整数组成，不含前导零。'
    + img('image 2.png') + img('image 3.png'))
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::从 begin 开始截取 1~3 位数字}}<br>'
    '每段需满足：{{c2::值 0~255，且不能有前导零（除非单独一个0）}}')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::begin == len && residue == 0}}（遍历完字符串且刚好4段）<br>'
    '剪枝1：{{c2::residue * 3 &lt; len - i}} → 剩余段数不够分<br>'
    '剪枝2：{{c3::i >= len}} → break（越界）<br>'
    '剪枝3：{{c4::前导零判断}} → len>1 && s.charAt(left)==\'0\'')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(3^4)}} → O(1)，最多 3^4=81 种<br>空间：{{c2::O(1)}} — 递归深度最多4层')
add_basic(d, make_front(p, '题解(DFS)'),
    'residue 记录还需分割的段数，每段截取1~3位，判断有效性后递归。<br>'
    + code(
        'public class Test13 {\n'
        '    public static List&lt;String&gt; restoreIpAddresses(String s) {\n'
        '        int len = s.length();\n'
        '        List&lt;String&gt; res = new ArrayList&lt;&gt;();\n'
        '        if (len &gt; 12 || len &lt; 4) {\n'
        '            return res;\n'
        '        }\n'
        '        Deque&lt;String&gt; path = new ArrayDeque&lt;&gt;(4);\n'
        '        dfs(s, len, 0, 4, path, res);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    private static void dfs(String s, int len, int begin, int residue,\n'
        '            Deque&lt;String&gt; path, List&lt;String&gt; res) {\n'
        '        if (begin == len) {\n'
        '            if (residue == 0) {\n'
        '                res.add(String.join(".", path));\n'
        '            }\n'
        '            return;\n'
        '        }\n'
        '        for (int i = begin; i &lt; begin + 3; i++) {\n'
        '            if (i &gt;= len) {\n'
        '                break;\n'
        '            }\n'
        '            if (residue * 3 &lt; len - i) {\n'
        '                continue;\n'
        '            }\n'
        '            if (judgeIpSegment(s, begin, i)) {\n'
        '                String currentIpSegment = s.substring(begin, i + 1);\n'
        '                path.addLast(currentIpSegment);\n'
        '                dfs(s, len, i + 1, residue - 1, path, res);\n'
        '                path.removeLast();\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '\n'
        '    private static boolean judgeIpSegment(String s, int left, int right) {\n'
        '        int len = right - left + 1;\n'
        '        if (len &gt; 1 && s.charAt(left) == \'0\') {\n'
        '            return false;\n'
        '        }\n'
        '        int res = 0;\n'
        '        while (left &lt;= right) {\n'
        '            res = res * 10 + s.charAt(left) - \'0\';\n'
        '            left++;\n'
        '        }\n'
        '        return res &gt;= 0 && res &lt;= 255;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '剪枝1：residue * 3 &lt; len - i 表示剩余字符太多，当前段不够分。<br>'
    '剪枝2：i &gt;= len 直接break，后面位数更长必然越界。<br>'
    'judgeIpSegment 判断前导零和0~255范围。residue 控制递归深度最多4层。')

# ============================================================
# 4. 括号生成
# ============================================================
p = '括号生成'
d = make_deck(1747300204, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '数字 n 代表生成括号的对数，设计一个函数生成所有可能的并且有效的括号组合。'
    + img('image 4.png'))
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表：{{c1::左括号}}（剩余left>0时）和 {{c2::右括号}}（剩余right>0时）<br>'
    '变量含义：left=剩余可用左括号数，right=剩余可用右括号数')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::left==0 && right==0}} → 加入结果<br>'
    '剪枝策略：{{c2::left > right}} → 直接return（右括号多于左括号必无效）<br>'
    '注意：每次用新字符串 curRes + "("，{{c3::无需显式回溯}}')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(4^n / sqrt(n))}} — 卡特兰数<br>空间：{{c2::O(n)}} — 递归深度')
add_basic(d, make_front(p, '题解(DFS)'),
    '字符串不可变性使得每次递归自动创建新对象，天然回溯，无需显式 remove。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;String&gt; list = new ArrayList&lt;&gt;();\n'
        '    public List&lt;String&gt; generateParenthesis(int n) {\n'
        '        if (n == 0)\n'
        '            return list;\n'
        '        dfs("", n, n);\n'
        '        return list;\n'
        '    }\n'
        '\n'
        '    public void dfs(String curRes, int left, int right) {\n'
        '        if (left == 0 && right == 0) {\n'
        '            list.add(curRes);\n'
        '            return;\n'
        '        }\n'
        '        if (left &gt; right)\n'
        '            return;\n'
        '        if (left &gt; 0) {\n'
        '            dfs(curRes + "(", left - 1, right);\n'
        '        }\n'
        '        if (right &gt; 0) {\n'
        '            dfs(curRes + ")", left, right - 1);\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'left > right 是最核心的剪枝：右括号剩余多于左括号时，已生成的串必无效。<br>'
    '每次传 curRes + "(" 而非修改 StringBuilder，利用字符串不可变性天然回溯。<br>'
    'left 和 right 表示剩余可用数量（而非已用数量），终止条件为两者皆为0。')

# ============================================================
# 5. 子集
# ============================================================
p = '子集'
d = make_deck(1747300205, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个不含重复元素的整数数组 nums，返回该数组所有可能的子集（幂集）。')
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::nums[i..n-1]}}（从 start 开始）<br>'
    '关键：{{c2::每进入递归立即收集当前路径}}（收集所有节点，不止叶子）')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::start == nums.length}} → 自然结束（无显式终止条件）<br>'
    '剪枝策略：{{c2::通过 start 索引控制}}，每次从 start 开始选，避免重复子集')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n * 2^n)}} — 2^n个子集，每个O(n)拷贝<br>空间：{{c2::O(n)}} — 递归深度')
add_basic(d, make_front(p, '题解(回溯)'),
    '子集问题收集所有节点（而非只收集叶子），每进入递归立即 add。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '    public List&lt;List&lt;Integer&gt;&gt; subsets(int[] nums) {\n'
        '        List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
        '        recall(nums, list, 0);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void recall(int[] nums, List&lt;Integer&gt; list, int start) {\n'
        '        res.add(new ArrayList&lt;&gt;(list));\n'
        '        for (int i = start; i &lt; nums.length; i++) {\n'
        '            list.add(nums[i]);\n'
        '            recall(nums, list, i + 1);\n'
        '            list.remove(list.size() - 1);\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '子集 vs 排列的核心区别：子集在进入递归时立即收集（收集所有节点），排列在终止条件处收集（只收集叶子）。<br>'
    'start 索引保证 [1,2] 和 [2,1] 不会重复出现（组合去重）。<br>'
    '空集 [] 也会被收集（首次调用 recall 时 list 为空）。')

# ============================================================
# 6. 单词搜索
# ============================================================
p = '单词搜索'
d = make_deck(1747300206, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个 mxn 二维字符网格 board 和一个字符串单词 word。'
    '如果 word 存在于网格中返回 true；否则返回 false。'
    '单词必须按照字母顺序，通过相邻的单元格内的字母构成。')
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::当前单元格的上下左右四个方向}}<br>'
    '遍历每个格子作为起点，DFS 匹配 word 的每个字符')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::begin == len-1}} → 检查 board[x][y] == charArray[begin]<br>'
    '剪枝1：{{c2::board[x][y] != charArray[begin]}} → 直接 return false<br>'
    '剪枝2：{{c3::visited[x][y]}} 标记已访问，防止走回头路<br>'
    '剪枝3：{{c4::越界检查}} inArea(newX, newY)')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m*n * 3^L)}} — 每个起点，3个方向（不走回头），L为单词长度<br>空间：{{c2::O(L)}} — 递归深度+visited数组')
add_basic(d, make_front(p, '题解(DFS+回溯)'),
    '遍历每个格子作为起点DFS。不能直接return dfs()，因为需要回溯visited。<br>'
    + code(
        'class Solution {\n'
        '    private static final int[][] DIRECTIONS = {{-1, 0}, {0, -1}, {0, 1}, {1, 0}};\n'
        '    private int rows;\n'
        '    private int cols;\n'
        '    private int len;\n'
        '    private boolean[][] visited;\n'
        '    private char[] charArray;\n'
        '    private char[][] board;\n'
        '\n'
        '    public boolean exist(char[][] board, String word) {\n'
        '        rows = board.length;\n'
        '        if (rows == 0) return false;\n'
        '        cols = board[0].length;\n'
        '        visited = new boolean[rows][cols];\n'
        '        this.len = word.length();\n'
        '        this.charArray = word.toCharArray();\n'
        '        this.board = board;\n'
        '        for (int i = 0; i &lt; rows; i++) {\n'
        '            for (int j = 0; j &lt; cols; j++) {\n'
        '                if (dfs(i, j, 0)) {\n'
        '                    return true;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '\n'
        '    private boolean dfs(int x, int y, int begin) {\n'
        '        if (begin == len - 1) {\n'
        '            return board[x][y] == charArray[begin];\n'
        '        }\n'
        '        if (board[x][y] == charArray[begin]) {\n'
        '            visited[x][y] = true;\n'
        '            for (int[] direction : DIRECTIONS) {\n'
        '                int newX = x + direction[0];\n'
        '                int newY = y + direction[1];\n'
        '                if (inArea(newX, newY) && !visited[newX][newY]) {\n'
        '                    if (dfs(newX, newY, begin + 1)) {\n'
        '                        return true;\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '            visited[x][y] = false;\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '\n'
        '    private boolean inArea(int x, int y) {\n'
        '        return x &gt;= 0 && x &lt; rows && y &gt;= 0 && y &lt; cols;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '不能直接 return dfs(newX, newY, begin+1)，否则失败时无法回溯 visited。<br>'
    '必须用 if (dfs(...)) return true 模式，失败后继续尝试其他方向。<br>'
    'begin == len-1 时加速判断最后一个字符，避免多余递归。')

# ============================================================
# 7. 目标和
# ============================================================
p = '目标和'
d = make_deck(1747300207, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非负整数数组 nums 和一个目标数 target。在数组的每个整数前添加 + 或 -，'
    '串联起来构造一个表达式，返回运算结果等于 target 的不同表达式的数目。')
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::+ 或 -}}（每个数字前可以加 + 或 -）<br>'
    '两个分支：{{c2::cur + nums[count]}} 和 {{c3::cur - nums[count]}}')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::count == nums.length}} → 判断 cur == target<br>'
    '剪枝策略：{{c2::记忆化搜索}} — key = count + "_" + cur，避免重复计算<br>'
    '记忆化将时间从 O(2^n) 降到 {{c3::O(n*sum)}}')
add_cloze(d, make_front(p, '复杂度'),
    'DFS+记忆化：时间 {{c1::O(n*sum)}}，空间 {{c2::O(n*sum)}}<br>裸DFS：时间 O(2^n)，空间 O(n)')
add_basic(d, make_front(p, '题解(DFS+记忆化)'),
    '每个数字前选择+或-，两条分支。用 HashMap 记忆化(count, cur)避免重复计算。<br>'
    + code(
        'class Solution {\n'
        '    public int findTargetSumWays(int[] nums, int target) {\n'
        '        return dfs(nums, target, 0, 0);\n'
        '    }\n'
        '\n'
        '    Map&lt;String, Integer&gt; cache = new HashMap&lt;&gt;();\n'
        '    public int dfs(int[] nums, int target, int count, int cur) {\n'
        '        String key = count + "_" + cur;\n'
        '        if (cache.containsKey(key))\n'
        '            return cache.get(key);\n'
        '        if (count == nums.length) {\n'
        '            cache.put(key, cur == target ? 1 : 0);\n'
        '            return cache.get(key);\n'
        '        }\n'
        '        int left = dfs(nums, target, count + 1, cur + nums[count]);\n'
        '        int right = dfs(nums, target, count + 1, cur - nums[count]);\n'
        '        cache.put(key, left + right);\n'
        '        return cache.get(key);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '记忆化 key 设计：count + "_" + cur，用下划线分隔避免歧义（如 count=1,cur=23 与 count=12,cur=3）。<br>'
    '两条分支求和 left+right 后缓存，后续相同状态直接返回。<br>'
    '也可用 DP 转化为 01背包：sum(P) = (target + sum)/2。')

# ============================================================
# 8. 电话号码的字母组合
# ============================================================
p = '电话号码的字母组合'
d = make_deck(1747300208, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个仅包含数字 2-9 的字符串，返回所有它能表示的字母组合。'
    '数字到字母的映射与电话按键相同。')
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::当前数字对应的字母集合}}<br>'
    '映射：2→abc, 3→def, 4→ghi, 5→jkl, 6→mno, 7→pqrs, 8→tuv, 9→wxyz')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::sb.length() == digits.length()}} → 加入结果<br>'
    '无特殊剪枝，每个数字的所有字母都要尝试。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(3^m * 4^n)}}，m为3字母数字数，n为4字母数字数<br>空间：{{c2::O(digits.length())}} — StringBuilder')
add_basic(d, make_front(p, '题解(DFS+回溯)'),
    'index控制处理到第几个数字，StringBuilder 回溯时 deleteCharAt。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;String&gt; list;\n'
        '    String[] allWords = {" ","*","abc","def","ghi","jkl","mno","pqrs","tuv","wxyz"};\n'
        '    public List&lt;String&gt; letterCombinations(String digits) {\n'
        '        list = new ArrayList&lt;&gt;();\n'
        '        if (digits == null || digits.length() == 0) {\n'
        '            return new ArrayList&lt;&gt;();\n'
        '        }\n'
        '        dfs(digits, 0);\n'
        '        return list;\n'
        '    }\n'
        '    StringBuilder sb = new StringBuilder();\n'
        '    public void dfs(String res, int index) {\n'
        '        if (res.length() == index) {\n'
        '            list.add(sb.toString());\n'
        '            return;\n'
        '        }\n'
        '        char ch = res.charAt(index);\n'
        '        int pos = ch - \'0\';\n'
        '        String words = allWords[pos];\n'
        '        for (int i = 0; i &lt; words.length(); i++) {\n'
        '            sb.append(words.charAt(i));\n'
        '            dfs(res, index + 1);\n'
        '            sb.deleteCharAt(sb.length() - 1);\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '映射技巧：String[] allWords 用数组索引直接映射数字到字母串，pos = ch - \'0\'。<br>'
    'StringBuilder 回溯：append → dfs → deleteCharAt(sb.length()-1)。<br>'
    'index 代表当前处理到第几个数字，终止条件为 index == res.length()。')

# ============================================================
# 9. 组合总和
# ============================================================
p = '组合总和'
d = make_deck(1747300209, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个无重复元素的数组 candidates 和一个目标数 target，'
    '找出 candidates 中所有可以使数字和为 target 的组合。candidates 中的数字可以无限制重复被选取。'
    + img('image 5.png'))
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::candidates[i..n-1]}}（从 begin 开始）<br>'
    '关键：{{c2::同数字可无限重复使用}} → 递归时传 i（不是 i+1）')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::target == 0}} → 加入结果<br>'
    '剪枝1：{{c2::target &lt; nums[i]}} → break（排序后，后面更大直接跳出）<br>'
    '剪枝2：{{c3::排序}}保证剪枝1生效，从begin开始防止重复组合')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n^(target/min))}} — 上界<br>空间：{{c2::O(target/min)}} — 递归深度')
add_basic(d, make_front(p, '题解(DFS)'),
    '可重复选取同一数字 → 递归传 i；不可重复 → 传 i+1。排序后用 target &lt; nums[i] 剪枝。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '    Deque&lt;Integer&gt; list = new LinkedList&lt;&gt;();\n'
        '    public List&lt;List&lt;Integer&gt;&gt; combinationSum(int[] candidates, int target) {\n'
        '        Arrays.sort(candidates);\n'
        '        dfs(candidates, 0, target, list);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void dfs(int[] nums, int begin, int target, Deque&lt;Integer&gt; list) {\n'
        '        if (target == 0) {\n'
        '            res.add(new ArrayList&lt;&gt;(list));\n'
        '            return;\n'
        '        }\n'
        '        for (int i = begin; i &lt; nums.length; i++) {\n'
        '            if (target &lt; nums[i])\n'
        '                break;\n'
        '            list.addLast(nums[i]);\n'
        '            dfs(nums, i, target - nums[i], list);\n'
        '            list.removeLast();\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '对比'),
    '与组合总和 II 区别：I 可无限重复用同一个数字(传i)，II 每个数字只能用一次(传i+1+排序去重)。<br>'
    '与零钱兑换区别：零钱兑换是DP求最少硬币数，本题是回溯求所有组合。')

# ============================================================
# 10. 组合总和 II
# ============================================================
p = '组合总和 II'
d = make_deck(1747300210, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个可能包含重复元素的数组 candidates 和一个目标数 target，'
    '找出 candidates 中所有可以使数字和为 target 的组合。candidates 中的每个数字在每个组合中只能使用一次。')
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::candidates[i..n-1]}}（从 begin 开始）<br>'
    '限制：{{c2::每个数字只能用一次}} → 递归传 i+1<br>'
    '去重：{{c3::同层跳过相同元素}} i>begin && nums[i]==nums[i-1]')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::target == 0}} → 加入结果<br>'
    '剪枝1：{{c2::target &lt; nums[i]}} → break（排序后）<br>'
    '剪枝2：{{c3::i>begin && nums[i]==nums[i-1]}} → continue（同层去重，不是 i>0）')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(2^n)}} — 每个元素选或不选<br>空间：{{c2::O(n)}} — 递归深度')
add_basic(d, make_front(p, '题解(DFS+剪枝)'),
    '去重条件用 i>begin 而非 i>0，因为要保留同一树枝上的重复数字。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
        '    public List&lt;List&lt;Integer&gt;&gt; combinationSum2(int[] candidates, int target) {\n'
        '        int n = candidates.length;\n'
        '        Arrays.sort(candidates);\n'
        '        dfs(candidates, target, 0, list);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void dfs(int[] nums, int target, int begin, List&lt;Integer&gt; list) {\n'
        '        if (target == 0) {\n'
        '            res.add(new ArrayList&lt;&gt;(list));\n'
        '            return;\n'
        '        }\n'
        '        for (int i = begin; i &lt; nums.length; i++) {\n'
        '            if (target &lt; nums[i])\n'
        '                break;\n'
        '            if (i &gt; begin && nums[i] == nums[i - 1])\n'
        '                continue;\n'
        '            list.add(list.size(), nums[i]);\n'
        '            dfs(nums, target - nums[i], i + 1, list);\n'
        '            list.remove(list.size() - 1);\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '对比'),
    '与组合总和 I 区别：II 需排序+同层去重(i>begin && ...)，且每个数字只能用一次(传i+1)。<br>'
    '去重条件用 i>begin 而非 i>0，因为要保留同一树枝上的重复数字。')

# ============================================================
# 11. 组合
# ============================================================
p = '组合'
d = make_deck(1747300211, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定两个整数 n 和 k，返回范围 [1, n] 中所有可能的 k 个数的组合。')
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::[begin..n]}}（从 begin 开始选）<br>'
    '组合问题：{{c2::顺序无关}}，用 begin 索引防止 [1,2] 和 [2,1] 重复')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::list.size() == k}} → 加入结果<br>'
    '剪枝策略：{{c2::通过 begin 递增自然剪枝}}，无需额外判断')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(C(n,k) * k)}} — C(n,k)个组合，每个O(k)拷贝<br>空间：{{c2::O(k)}} — 递归深度')
add_basic(d, make_front(p, '题解(DFS)'),
    '组合标准模板：begin索引 + i+1递归 + 终止条件list.size()==k。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;List&lt;Integer&gt;&gt; res = new ArrayList&lt;&gt;();\n'
        '    Deque&lt;Integer&gt; queue = new LinkedList&lt;&gt;();\n'
        '    public List&lt;List&lt;Integer&gt;&gt; combine(int n, int k) {\n'
        '        int[] temp = new int[n];\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            temp[i] = i + 1;\n'
        '        }\n'
        '        dfs(temp, 0, k);\n'
        '        return res;\n'
        '    }\n'
        '\n'
        '    public void dfs(int[] nums, int begin, int k) {\n'
        '        if (queue.size() == k) {\n'
        '            res.add(new ArrayList(queue));\n'
        '            return;\n'
        '        }\n'
        '        for (int i = begin; i &lt; nums.length; i++) {\n'
        '            queue.add(nums[i]);\n'
        '            dfs(nums, i + 1, k);\n'
        '            queue.removeLast();\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '组合模板 = 子集模板 + 终止条件（size==k）。<br>'
    '与组合总和模板完全一样，核心是 begin 索引 + 递归传 i+1。<br>'
    '可以进一步优化：剪掉剩余元素不够选的情况（n-i+1 &lt; k-list.size()）。')

# ============================================================
# 12. 字典序排数
# ============================================================
p = '字典序排数'
d = make_deck(1747300212, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个整数 n，按字典序返回范围 [1, n] 内的所有整数。'
    + img('image 6.png'))
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::cur*10+0 ~ cur*10+9}}（在 cur 后面拼 0~9）<br>'
    '起始值：{{c2::1~9}} 分别作为首位开始 DFS')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::cur > n}} → 直接return<br>'
    '剪枝策略：{{c2::cur > limit}} 时剪掉该分支<br>'
    '本质是十叉树的DFS遍历')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 每个数字访问一次<br>空间：{{c2::O(log10 n)}} — 递归深度')
add_basic(d, make_front(p, '题解(DFS递归)'),
    '字典序本质是十叉树的先序遍历。1~9作为根，每个节点后排0~9作为子节点。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;Integer&gt; list = new ArrayList&lt;&gt;();\n'
        '    public List&lt;Integer&gt; lexicalOrder(int n) {\n'
        '        for (int i = 1; i &lt;= 9; i++) {\n'
        '            dfs(i, n);\n'
        '        }\n'
        '        return list;\n'
        '    }\n'
        '\n'
        '    public void dfs(int cur, int limit) {\n'
        '        if (cur &gt; limit)\n'
        '            return;\n'
        '        list.add(cur);\n'
        '        for (int i = 0; i &lt;= 9; i++)\n'
        '            dfs(cur * 10 + i, limit);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '对比'),
    '与普通回溯不同：不是选/不选问题，而是树的先序遍历。<br>'
    '迭代解法更省空间：j*10、j%10==9回退、j++。')

# ============================================================
# 13. 字符串的排列
# ============================================================
p = '字符串的排列'
d = make_deck(1747300213, f'算法::回溯法::{p}')
add_basic(d, make_front(p, '题干'),
    '输入一个字符串，打印出该字符串中字符的所有排列。你可以以任意顺序返回这个字符串数组。'
    '字符串中可能有重复字符。')
add_cloze(d, make_front(p, '回溯-选择列表'),
    '选择列表 = {{c1::s 的字符数组}}<br>'
    '与全排列 II 完全相同的模板：{{c2::排序+used数组+同层去重}}')
add_cloze(d, make_front(p, '回溯-终止+剪枝'),
    '终止条件：{{c1::sb.length() == ch.length}} → 加入结果<br>'
    '剪枝策略：{{c2::i>0 && ch[i]==ch[i-1] && !used[i-1]}} → continue<br>'
    '与全排列 II 完全一样，只是处理 char[] 而非 int[]')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n!)}} — n个字符的全排列<br>空间：{{c2::O(n)}} — 递归深度+used数组')
add_basic(d, make_front(p, '题解(DFS+剪枝)'),
    '与全排列 II 完全相同模板，区别仅在于处理 char[] vs int[]。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;String&gt; res = new ArrayList&lt;&gt;();\n'
        '    public String[] permutation(String s) {\n'
        '        int len = s.length();\n'
        '        if (len &lt;= 0)\n'
        '            return null;\n'
        '        StringBuilder sb = new StringBuilder();\n'
        '        boolean[] used = new boolean[len];\n'
        '        char[] ch = s.toCharArray();\n'
        '        Arrays.sort(ch);\n'
        '        dfs(ch, sb, used);\n'
        '        return res.toArray(new String[res.size()]);\n'
        '    }\n'
        '\n'
        '    public void dfs(char[] ch, StringBuilder sb, boolean[] used) {\n'
        '        if (sb.length() == ch.length) {\n'
        '            res.add(sb.toString());\n'
        '            return;\n'
        '        }\n'
        '        for (int i = 0; i &lt; ch.length; i++) {\n'
        '            if (i &gt; 0 && ch[i] == ch[i - 1] && used[i - 1] == false)\n'
        '                continue;\n'
        '            if (used[i] == false) {\n'
        '                used[i] = true;\n'
        '                sb.append(ch[i]);\n'
        '                dfs(ch, sb, used);\n'
        '                sb.deleteCharAt(sb.length() - 1);\n'
        '                used[i] = false;\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '对比'),
    '与全排列 II 完全相同的模板，区别仅在于处理 char[] vs int[]。<br>'
    '剪枝用 Set 去重更直观但更慢，排序+used才是最优解。')

if __name__ == '__main__':
    print(build('../../牌组/算法/回溯法.apkg'))
