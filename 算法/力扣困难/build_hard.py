"""Build APKG for 力扣困难 (LeetCode Hard). 21 problems, complete Java code solutions."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code in <pre><code> for highlight.js syntax highlighting."""
    return f'<pre><code class="language-java">{java}</code></pre>'


# --- Principles deck ---
d0 = make_deck(1747302100, '算法::力扣困难::原理通识')
add_basic(d0, '困难题核心思想',
    '困难题通常考察多个知识点的组合运用：<br>'
    '1. 动态规划 + 状态压缩：正则匹配、鸡蛋掉落、通配符匹配<br>'
    '2. DFS/回溯 + 剪枝：N皇后、解数独、24点游戏<br>'
    '3. 单调栈 + 数组压缩：柱状图最大矩形、最大矩形<br>'
    '4. 前缀和 + 单调队列/二分：最短子数组、分割数组<br>'
    '5. 排序 + 贪心/LIS：俄罗斯套娃、最长递增子序列')
add_cloze(d0, '困难题常见算法分类',
    '1. 动态规划：{{c1::状态定义 + 状态转移 + 初始化 + 遍历顺序 + 返回值}} 五部曲<br>'
    '2. 回溯法：{{c2::DFS + 剪枝 + 状态恢复}}，排列/组合/棋盘类问题<br>'
    '3. 二分查找：{{c3::单调性/二段性}}是使用二分的前提，找峰顶/分割点/旋转点<br>'
    '4. 单调栈：{{c4::找左右第一个比当前元素小/大的位置}}，确定宽度计算面积<br>'
    '5. 堆/优先队列：维护{{c5::数据流的中位数}}或前K大/小的元素')
add_basic(d0, '困难题解题策略',
    '1. 先分析是否具有最优子结构 → 尝试DP或贪心<br>'
    '2. 先分析是否可转化为搜索问题 → 尝试DFS/BFS + 剪枝/记忆化<br>'
    '3. 先分析是否具有单调性/二段性 → 尝试二分查找<br>'
    '4. 前缀和 + 某种数据结构（单调队列/哈希表）→ 子数组问题通解<br>'
    '5. 多解法交叉验证：先暴力保底 → 逐步优化（记忆化 → DP → 状态压缩）')
add_cloze(d0, '困难题常见陷阱',
    '1. 负数破坏单调性：和至少为K的最短子数组不能用{{c1::滑动窗口}}，要用{{c2::前缀和+单调队列}}<br>'
    '2. 重复元素：旋转排序数组最小值II中{{c3::nums[mid]==nums[right]}}时只能right--<br>'
    '3. 精度问题：24点游戏中用{{c4::23.999~24.001}}范围判断而非==<br>'
    '4. 前导零：最大数/最小数拼接后需去除{{c5::前导零}}，全零数组返回"0"<br>'
    '5. 哨兵技巧：单调栈问题在数组两端加{{c6::高度为0的哨兵}}避免空栈判断')

# ============================================================
# 1. 矩阵中的最长递增路径
# ============================================================
p = '矩阵中的最长递增路径'
d = make_deck(1747302101, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个 m x n 整数矩阵 matrix，找出其中最长递增路径的长度。'
    '对于每个单元格，你可以往上、下、左、右四个方向移动。'
    '不能在对角线方向上移动，也不能移动到边界外。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m*n)}} — 每个格子只计算一次（记忆化）<br>空间：{{c2::O(m*n)}} — visited 数组')
add_basic(d, make_front(p, '题解(DFS+记忆化)'),
    'DFS + 记忆化搜索，preVal 记录上一步的值，只有严格递增 matrix[i][j] &gt; preVal 才继续搜索。<br>'
    + code(
        'class Solution {\n'
        '    int[][] visited;\n'
        '    int n, m;\n'
        '    public int longestIncreasingPath(int[][] matrix) {\n'
        '        int maxRes = 0;\n'
        '        n = matrix.length;\n'
        '        m = matrix[0].length;\n'
        '        visited = new int[n][m];\n'
        '        for(int i = 0; i &lt; n; i++){\n'
        '            for(int j = 0; j &lt; m; j++){\n'
        '                maxRes = Math.max(maxRes, dfs(matrix, i, j, Integer.MIN_VALUE));\n'
        '            }\n'
        '        }\n'
        '        return maxRes;\n'
        '    }\n'
        '\n'
        '    public int dfs(int[][] matrix, int i, int j, int preTemp){\n'
        '        if(i &gt;= n || j &gt;= m || i &lt;0 || j &lt; 0)\n'
        '            return 0;\n'
        '        if(matrix[i][j] &lt;= preTemp)\n'
        '            return 0;\n'
        '        if(visited[i][j] &gt; 0)\n'
        '            return visited[i][j];\n'
        '        int under = dfs(matrix, i + 1, j, matrix[i][j]);\n'
        '        int top = dfs(matrix, i - 1, j, matrix[i][j]);\n'
        '        int left = dfs(matrix, i, j - 1, matrix[i][j]);\n'
        '        int right = dfs(matrix, i, j + 1, matrix[i][j]);\n'
        '        visited[i][j] = Math.max(Math.max(under, top), Math.max(left, right)) + 1;\n'
        '        return visited[i][j];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '核心：DFS + 记忆化搜索(memoization)，每个格子计算后存入 visited 数组。'
    '<br>visited[i][j] 表示以(i,j)为起点的最长递增路径长度。<br>'
    '关键条件：matrix[i][j] &lt;= preVal 时剪枝（非严格递增直接返回0）。<br>'
    '四个方向取最大值 + 1，记忆化保证每个格子只算一次。')

# ============================================================
# 2. 分发糖果
# ============================================================
p = '分发糖果'
d = make_deck(1747302102, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    'n 个孩子站成一排，给你一个整数数组 ratings 表示每个孩子的评分。'
    '你需要按照以下要求给这些孩子分发糖果：<br>'
    '1. 每个孩子至少分配到 1 个糖果<br>'
    '2. 相邻两个孩子中评分高的必须获得更多的糖果<br>'
    '请你计算最少需要准备多少颗糖果。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 两次遍历<br>空间：{{c2::O(n)}} — dp 数组')
add_basic(d, make_front(p, '题解(贪心-两遍遍历)'),
    '贪心两遍扫描：左→右处理左边邻居，右→左用 Math.max 处理右边邻居。<br>'
    + code(
        'class Solution {\n'
        '    public int candy(int[] ratings) {\n'
        '        int len = ratings.length;\n'
        '        if(len == 0)\n'
        '            return 0;\n'
        '        int[] dp = new int[len];\n'
        '        Arrays.fill(dp, 1);\n'
        '        for(int i = 1; i &lt; len; i++){\n'
        '            if(ratings[i] &gt; ratings[i-1])\n'
        '                dp[i] = dp[i-1] + 1;\n'
        '        }\n'
        '        for(int i = len - 2; i &gt;= 0; i--){\n'
        '            if(ratings[i] &gt; ratings[i+1])\n'
        '                dp[i] = Math.max(dp[i], dp[i+1] + 1);\n'
        '        }\n'
        '        int res = 0;\n'
        '        for(int nums : dp)\n'
        '            res += nums;\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '贪心两遍扫描：<br>'
    '第一遍（左→右）：只处理左边邻居，保证比左边高的孩子多拿糖。<br>'
    '第二遍（右→左）：处理右边邻居，用 Math.max 避免覆盖第一遍已确定的更优值。<br>'
    '两遍可以交换顺序，但后面的遍历必须用前面的结果取 max 优化最终结果。')

# ============================================================
# 3. 正则表达式匹配
# ============================================================
p = '正则表达式匹配'
d = make_deck(1747302103, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个字符串 s 和一个字符规律 p，实现一个支持 "." 和 "*" 的正则表达式匹配。<br>'
    '". "匹配任意单个字符；" * "匹配零个或多个前面的那一个元素。<br>'
    '匹配应覆盖整个字符串，而非部分匹配。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m*n)}} — 二维DP填表<br>空间：{{c2::O(m*n)}} — dp数组(m=s.length, n=p.length)')
add_basic(d, make_front(p, '题解(DP)'),
    '*匹配0次→dp[i][j-2]（跳过x*），*匹配多次→dp[i-1][j]（s前移，p保持）。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isMatch(String s, String p) {\n'
        '        char[] cs = s.toCharArray();\n'
        '        char[] cp = p.toCharArray();\n'
        '        boolean[][] dp = new boolean[cs.length + 1][cp.length + 1];\n'
        '        dp[0][0] = true;\n'
        '        for (int j = 1; j &lt;= cp.length; j++) {\n'
        '            if (cp[j - 1] == \'*\') {\n'
        '                dp[0][j] = dp[0][j - 2];\n'
        '            }\n'
        '        }\n'
        '        for (int i = 1; i &lt;= cs.length; i++) {\n'
        '            for (int j = 1; j &lt;= cp.length; j++) {\n'
        '                if (cs[i - 1] == cp[j - 1] || cp[j - 1] == \'.\') {\n'
        '                    dp[i][j] = dp[i - 1][j - 1];\n'
        '                } else if (cp[j - 1] == \'*\') {\n'
        '                    if (cs[i - 1] == cp[j - 2] || cp[j - 2] == \'.\') {\n'
        '                        dp[i][j] = dp[i][j - 2]\n'
        '                                || dp[i - 1][j];\n'
        '                    } else {\n'
        '                        dp[i][j] = dp[i][j - 2];\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return dp[cs.length][cp.length];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'DP五部曲：<br>'
    '1. 状态：dp[i][j] 表示 s[0,i-1] 和 p[0,j-1] 是否匹配<br>'
    '2. 非*：字符相等或p[j-1]==\'.\' → dp[i-1][j-1]<br>'
    '3. 是*：看p[j-2]<br>'
    '&nbsp;&nbsp;&nbsp;- 匹配：dp[i][j-2]（*匹配0次）|| dp[i-1][j]（*匹配多次）<br>'
    '&nbsp;&nbsp;&nbsp;- 不匹配：只能 dp[i][j-2]（*作废）<br>'
    '4. 初始化：dp[0][0]=true；s为空时"x*"可匹配0次<br>'
    '5. 注意：万能串 .* 可匹配任意长度')

# ============================================================
# 4. 数据流的中位数
# ============================================================
p = '数据流的中位数'
d = make_deck(1747302104, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '中位数是有序整数列表中间的值。实现 MedianFinder 类：<br>'
    '- addNum(int num)：将数据流中的整数添加到数据结构中<br>'
    '- findMedian()：返回到目前为止所有元素的中位数<br>'
    '如果列表大小是偶数，中位数是中间两个数的平均值。')
add_cloze(d, make_front(p, '复杂度'),
    'addNum：{{c1::O(log n)}} — 堆操作<br>'
    'findMedian：{{c2::O(1)}} — 直接取堆顶<br>'
    '空间：{{c3::O(n)}} — 两个堆存储所有元素')
add_basic(d, make_front(p, '题解(大根堆+小根堆)'),
    '双堆维护中位数：大根堆存较小的一半，小根堆存较大的一半。先入大根堆→弹出堆顶入小根堆→若小根堆更大则弹回。<br>'
    + code(
        'class MedianFinder {\n'
        '    PriorityQueue&lt;Integer&gt; min;\n'
        '    PriorityQueue&lt;Integer&gt; max;\n'
        '    public MedianFinder() {\n'
        '        min = new PriorityQueue&lt;&gt;();\n'
        '        max = new PriorityQueue&lt;&gt;((a,b) -&gt; {return b - a;});\n'
        '    }\n'
        '    public void addNum(int num) {\n'
        '        max.add(num);\n'
        '        min.add(max.remove());\n'
        '        if (min.size() &gt; max.size())\n'
        '            max.add(min.remove());\n'
        '    }\n'
        '    public double findMedian() {\n'
        '        if (max.size() == min.size())\n'
        '            return (max.peek() + min.peek()) / 2.0;\n'
        '        else\n'
        '            return max.peek();\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '双堆维护中位数：<br>'
    '大根堆(max)存较小的一半（倒序），小根堆(min)存较大的一半（正序）。<br>'
    '平衡策略：max 元素数 = min 元素数 或 max 比 min 多1。<br>'
    '中位数 = 若相等取两堆顶平均，否则取 max 堆顶。<br>'
    '插入流程：先入max → max弹出入min → 若min比max大则min弹出入max。<br>'
    '注意除法用 2.0 而非 2，避免整数除法。')

# ============================================================
# 5. 鸡蛋掉落
# ============================================================
p = '鸡蛋掉落'
d = make_deck(1747302105, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给你 k 枚相同的鸡蛋，和一栋从第 1 层到第 n 层共有 n 层楼的建筑。'
    '已知存在楼层 f ，满足 0 &lt;= f &lt;= n ，任何从高于 f 的楼层落下的鸡蛋都会碎，'
    '从 f 楼层或比它低的楼层落下的鸡蛋都不会碎。'
    '每次操作，你可以取一枚没有碎的鸡蛋并把它从任一楼层 x 扔下。'
    '请你计算并返回要确定 f 确切的值的最小操作次数是多少？'
    + img('image.png') + img('image 1.png'))
add_cloze(d, make_front(p, '复杂度-数学法'),
    'calcF(K,T) 递归：时间 {{c1::O(K*T)}}（T为结果值）<br>'
    'DP法：时间 {{c2::O(K*N)}} 或提前退出<br>'
    '空间：数学法 {{c3::O(1)}} 或 DP法 {{c4::O(K*N)}}')
add_basic(d, make_front(p, '题解(数学法)'),
    'calcF(K,T)表示K个蛋T次操作最多能确定的楼层数。碎+K-1,T-1；不碎+K,T-1。<br>'
    + code(
        'class Solution {\n'
        '    public int superEggDrop(int k, int n) {\n'
        '        int T = 1;\n'
        '        while (calcF(k, T) &lt; n + 1)\n'
        '            T++;\n'
        '        return T;\n'
        '    }\n'
        '    public int calcF(int K, int T){\n'
        '        if (T == 1 || K == 1)\n'
        '            return T + 1;\n'
        '        return calcF(K - 1, T - 1) + calcF(K, T - 1);\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '题解(DP)'),
    'dp[k][m]表示k个蛋m次操作最多能确定的楼层数，达到N时返回m。<br>'
    + code(
        'class Solution {\n'
        '    public int superEggDrop(int K, int N) {\n'
        '        int[][] dp = new int[K + 1][N + 1];\n'
        '        for (int m = 1; m &lt;= N; m++) {\n'
        '            dp[0][m] = 0;\n'
        '            for (int k = 1; k &lt;= K; k++) {\n'
        '                dp[k][m] = dp[k][m - 1] + dp[k - 1][m - 1] + 1;\n'
        '                if (dp[k][m] &gt;= N) {\n'
        '                    return m;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return N;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 6. 通配符匹配
# ============================================================
p = '通配符匹配'
d = make_deck(1747302106, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s 和一个字符模式 p，实现一个支持 "?" 和 " * " 的通配符匹配。<br>'
    '"?" 可以匹配任何单个字符；" * " 可以匹配任意字符串（包括空字符串）。<br>'
    '匹配需覆盖整个字符串。'
    + img('image 2.png') + img('image 3.png') + img('image 4.png') + img('image 5.png')
    + img('image 6.png') + img('image 7.png') + img('image 8.png') + img('image 9.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m*n)}} — 二维DP<br>空间：{{c2::O(m*n)}} — dp数组')
add_basic(d, make_front(p, '题解(DP)'),
    '*的二义性：dp[i-1][j]（*匹配空串）| dp[i][j-1]（*匹配当前字符后继续匹配）。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isMatch(String s, String p) {\n'
        '        int m = s.length(), n = p.length();\n'
        '        boolean[][] dp = new boolean[n+1][m+1];\n'
        '        dp[0][0] = true;\n'
        '        for(int i = 1; i &lt;= n; i++){\n'
        '            if(p.charAt(i-1) != \'*\')\n'
        '                break;\n'
        '            dp[i][0] = true;\n'
        '        }\n'
        '        for(int i = 1; i &lt;= n; i++){\n'
        '            for(int j = 1; j &lt;= m; j++){\n'
        '                if(p.charAt(i - 1) == s.charAt(j - 1) || p.charAt(i - 1) == \'?\')\n'
        '                    dp[i][j] = dp[i-1][j-1];\n'
        '                else if(p.charAt(i - 1) == \'*\')\n'
        '                    dp[i][j] = dp[i-1][j] | dp[i][j-1];\n'
        '            }\n'
        '        }\n'
        '        return dp[n][m];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '与正则匹配的区别：<br>'
    '1. 正则的 * 修饰前一个字符（如 a*），通配符的 * 独立匹配任意串<br>'
    '2. 通配符更简单：dp[i][j] 表示 p 的前 i 个和 s 的前 j 个是否匹配<br>'
    '3. ? 等价于正则的 .（匹配单个字符）<br>'
    '4. * 转移：不看*（dp[i-1][j]）|| 看*（dp[i][j-1]）<br>'
    '5. 用 | 而非 || 因为需要同时考虑两条转移路径')

# ============================================================
# 7. 最大矩形
# ============================================================
p = '最大矩形'
d = make_deck(1747302107, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个仅包含 0 和 1 、大小为 rows x cols 的二维二进制矩阵，'
    '找出只包含 1 的最大矩形，并返回其面积。'
    + img('image 10.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(rows*cols)}} — 每行遍历所有列+单调栈<br>空间：{{c2::O(cols)}} — heights 数组')
add_basic(d, make_front(p, '题解(逐行压缩+单调栈)'),
    '将每一行转化为柱状图：连续1累加高度，遇到0重置为0。复用柱状图最大矩形解法。<br>'
    + code(
        'class Solution {\n'
        '    public int maximalRectangle(char[][] matrix) {\n'
        '        if (matrix.length == 0) {\n'
        '            return 0;\n'
        '        }\n'
        '        int[] heights = new int[matrix[0].length];\n'
        '        int res = 0;\n'
        '        for (int row = 0; row &lt; matrix.length; row++) {\n'
        '            for (int col = 0; col &lt; matrix[0].length; col++) {\n'
        '                if (matrix[row][col] == \'1\') {\n'
        '                    heights[col] += 1;\n'
        '                } else {\n'
        '                    heights[col] = 0;\n'
        '                }\n'
        '            }\n'
        '            res = Math.max(res, findThisLayer(heights));\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '    public int findThisLayer(int[] heights){\n'
        '        int len = heights.length;\n'
        '        if(len == 0)\n'
        '            return 0;\n'
        '        if(len == 1)\n'
        '            return heights[0];\n'
        '        int[] newHeights = new int[len + 2];\n'
        '        newHeights[0] = 0;\n'
        '        System.arraycopy(heights, 0, newHeights, 1, len);\n'
        '        newHeights[len + 1] = 0;\n'
        '        heights = newHeights;\n'
        '        Deque&lt;Integer&gt; stack = new ArrayDeque&lt;&gt;();\n'
        '        stack.addLast(0);\n'
        '        int res = 0;\n'
        '        for(int i = 1; i &lt; heights.length; i++){\n'
        '            while(heights[i] &lt; heights[stack.peekLast()]){\n'
        '                int curHeight = heights[stack.pollLast()];\n'
        '                int curWidth = i - stack.peekLast() - 1;\n'
        '                res = Math.max(res, curHeight * curWidth);\n'
        '            }\n'
        '            stack.addLast(i);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '二维转一维：把每列看作柱子，逐行向下累计高度（遇1加1，遇0归0）。<br>'
    '每一行都是一个"柱状图中最大矩形"问题（题9），用单调栈求解。<br>'
    '本质：所有可能的矩形都可以被某一行的柱状图表示。<br>'
    '时间复杂度 O(rows*cols) = 遍历每行 * 单调栈O(cols)。')

# ============================================================
# 8. 24 点游戏
# ============================================================
p = '24 点游戏'
d = make_deck(1747302108, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个长度为4的整数数组 cards，判断是否能通过加、减、乘、除'
    '（可加括号）运算得到 24。除法运算为实数除法。'
    + img('image 11.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(1)}} — 固定4张牌，有限组合<br>空间：{{c2::O(1)}} — 递归栈深固定')
add_basic(d, make_front(p, '题解(回溯)'),
    '精度判断：用 23.999~24.001 范围代替 ==24。每次选两个数运算后数组缩减1。<br>'
    + code(
        'class Solution {\n'
        '    public boolean judgePoint24(int[] nums) {\n'
        '        double[] doubles = Arrays.stream(nums).asDoubleStream().toArray();\n'
        '        return judgePoint24(doubles);\n'
        '    }\n'
        '    public boolean judgePoint24(double[] nums) {\n'
        '        if (nums.length == 1) {\n'
        '            return nums[0] &gt; 23.999 &amp;&amp; nums[0] &lt; 24.001;\n'
        '        }\n'
        '        for (int x = 0; x &lt; nums.length - 1; x++) {\n'
        '            for (int y = x + 1; y &lt; nums.length; y++) {\n'
        '                boolean isValid = false;\n'
        '                double[] temp = new double[nums.length - 1];\n'
        '                System.arraycopy(nums, 0, temp, 0, y);\n'
        '                System.arraycopy(nums, y + 1, temp, y, temp.length - y);\n'
        '                temp[x] = nums[x] + nums[y];\n'
        '                isValid = isValid || judgePoint24(temp);\n'
        '                temp[x] = nums[x] - nums[y];\n'
        '                isValid = isValid || judgePoint24(temp);\n'
        '                temp[x] = nums[y] - nums[x];\n'
        '                isValid = isValid || judgePoint24(temp);\n'
        '                temp[x] = nums[x] * nums[y];\n'
        '                isValid = isValid || judgePoint24(temp);\n'
        '                if (nums[y] != 0) {\n'
        '                    temp[x] = nums[x] / nums[y];\n'
        '                    isValid = isValid || judgePoint24(temp);\n'
        '                }\n'
        '                if (nums[x] != 0) {\n'
        '                    temp[x] = nums[y] / nums[x];\n'
        '                    isValid = isValid || judgePoint24(temp);\n'
        '                }\n'
        '                if (isValid) {\n'
        '                    return true;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '回溯核心思想：<br>'
    '1. 每次从数组中选两个不同的数，用四种运算符组合出一个新数<br>'
    '2. 新数放在 x 位置，删除 y 位置，数组长度减1<br>'
    '3. 递归直到数组长度为1，判断是否等于24<br>'
    '4. 关键：无需考虑括号 — 任选两数运算自然覆盖了所有括号组合<br>'
    '5. 精度陷阱：浮点运算用绝对值范围判断，除数为0要跳过')

# ============================================================
# 9. 柱状图中最大的矩形
# ============================================================
p = '柱状图中最大的矩形'
d = make_deck(1747302109, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定 n 个非负整数，用来表示柱状图中各个柱子的高度。每个柱子彼此相邻，且宽度为 1 。'
    '求在该柱状图中，能够勾勒出来的矩形的最大面积。'
    + img('image 12.png') + img('image 13.png') + img('image 14.png') + img('image 15.png')
    + img('image 16.png') + img('image 17.png') + img('image 18.png') + img('image 19.png')
    + img('image 20.png') + img('image 21.png') + img('image 22.png'))
add_cloze(d, make_front(p, '复杂度'),
    '暴力：时间 {{c1::O(n²)}}，空间 {{c2::O(1)}}<br>'
    '单调栈+哨兵：时间 {{c3::O(n)}}，空间 {{c4::O(n)}}')
add_basic(d, make_front(p, '题解(单调栈+哨兵)'),
    '哨兵技巧：左右各加一个高度0的柱子，左哨兵保证栈永不为空，右哨兵保证所有元素最终出栈。<br>'
    + code(
        'class Solution {\n'
        '    public int largestRectangleArea(int[] heights) {\n'
        '        int len = heights.length;\n'
        '        if (len == 0) {\n'
        '            return 0;\n'
        '        }\n'
        '        if (len == 1) {\n'
        '            return heights[0];\n'
        '        }\n'
        '        int res = 0;\n'
        '        int[] newHeights = new int[len + 2];\n'
        '        newHeights[0] = 0;\n'
        '        System.arraycopy(heights, 0, newHeights, 1, len);\n'
        '        newHeights[len + 1] = 0;\n'
        '        len += 2;\n'
        '        heights = newHeights;\n'
        '        Deque&lt;Integer&gt; stack = new ArrayDeque&lt;&gt;(len);\n'
        '        stack.addLast(0);\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            while (heights[i] &lt; heights[stack.peekLast()]) {\n'
        '                int curHeight = heights[stack.pollLast()];\n'
        '                int curWidth = i - stack.peekLast() - 1;\n'
        '                res = Math.max(res, curHeight * curWidth);\n'
        '            }\n'
        '            stack.addLast(i);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '单调递增栈：栈中存下标，对应高度严格递增。<br>'
    '当遇到比栈顶矮的柱子时，栈顶柱子的右边界确定 → 弹出并计算面积。<br>'
    '宽度 = i - stack.peekLast() - 1（当前右边界 - 左边界 - 1）。<br>'
    '哨兵优化：在原数组两端加高度0，省去空栈判断和末尾清栈逻辑。<br>'
    '核心理解：每个柱子的最大矩形由左右第一个比它矮的柱子界定。')

# ============================================================
# 10. N皇后
# ============================================================
p = 'N皇后'
d = make_deck(1747302110, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    'n 皇后问题研究的是如何将 n 个皇后放置在 n×n 的棋盘上，'
    '并且使皇后彼此之间不能相互攻击。皇后可以攻击同一行、同一列、'
    '同一正对角线或同一副对角线上的任意单位。'
    '给你一个整数 n，返回所有不同的 n 皇后问题的解决方案。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n!)}} — 每行有最多n个选择，且逐步减少<br>空间：{{c2::O(n²)}} — 棋盘数组')
add_basic(d, make_front(p, '题解(DFS+回溯)'),
    '逐行放置 + 回溯剪枝：每行只放一个皇后，isValid 只检查列、左上对角线、右上对角线。<br>'
    + code(
        'class Solution {\n'
        '    List&lt;List&lt;String&gt;&gt; res;\n'
        '    char[][] chessboard;\n'
        '    public List&lt;List&lt;String&gt;&gt; solveNQueens(int n) {\n'
        '        chessboard = new char[n][n];\n'
        '        res = new ArrayList&lt;&gt;();\n'
        '        for (char[] c : chessboard) {\n'
        '            Arrays.fill(c, \'.\');\n'
        '        }\n'
        '        backTrack(n, 0);\n'
        '        return res;\n'
        '    }\n'
        '    public void backTrack(int n, int row) {\n'
        '        if (row == n) {\n'
        '            res.add(Array2List());\n'
        '            return;\n'
        '        }\n'
        '        for (int col = 0; col &lt; n; col++) {\n'
        '            if (isValid(row, col, n)) {\n'
        '                chessboard[row][col] = \'Q\';\n'
        '                backTrack(n, row + 1);\n'
        '                chessboard[row][col] = \'.\';\n'
        '            }\n'
        '        }\n'
        '    }\n'
        '    public List Array2List() {\n'
        '        List&lt;String&gt; list = new ArrayList&lt;&gt;();\n'
        '        for (char[] c : chessboard) {\n'
        '            list.add(String.copyValueOf(c));\n'
        '        }\n'
        '        return list;\n'
        '    }\n'
        '    public boolean isValid(int row, int col, int n) {\n'
        '        for (int i=0; i &lt; row; i++) {\n'
        '            if (chessboard[i][col] == \'Q\') {\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        for (int i=row-1, j=col-1; i&gt;=0 &amp;&amp; j&gt;=0; i--, j--) {\n'
        '            if (chessboard[i][j] == \'Q\') {\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        for (int i=row-1, j=col+1; i&gt;=0 &amp;&amp; j&lt;=n-1; i--, j++) {\n'
        '            if (chessboard[i][j] == \'Q\') {\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '逐行放置 + 回溯剪枝：<br>'
    '1. 每行只放一个皇后，row 递增，天然避免行冲突<br>'
    '2. isValid 只检查列、左上对角线、右上对角线（下半部分还没放）<br>'
    '3. 45°对角线：i-1, j-1 递减；135°对角线：i-1, j+1 递增<br>'
    '4. 回溯：放皇后 → 递归下一行 → 撤销皇后 → 尝试下一列<br>'
    '5. 终止条件：row == n 时收集结果')

# ============================================================
# 11. 解数独
# ============================================================
p = '解数独'
d = make_deck(1747302111, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '编写一个程序，通过填充空格来解决数独问题。数独的解法需遵循如下规则：<br>'
    '1. 数字 1-9 在每一行只能出现一次<br>'
    '2. 数字 1-9 在每一列只能出现一次<br>'
    '3. 数字 1-9 在每一个以粗实线分隔的 3x3 宫内只能出现一次<br>'
    '数独部分空格已填有数字，空白格用 "." 表示。'
    + img('image 23.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：最坏 {{c1::O(9^(n*n))}}，实际远小于此（剪枝有效）<br>空间：{{c2::O(1)}} — 原地修改board')
add_basic(d, make_front(p, '题解(DFS+回溯+三维剪枝)'),
    '三维剪枝：行、列、3x3宫格三个维度排除已用数字。宫格起点=(row/3)*3, (col/3)*3。<br>'
    + code(
        'class Solution {\n'
        '    public void solveSudoku(char[][] board) {\n'
        '        dfs(board);\n'
        '    }\n'
        '    public boolean dfs(char[][] board){\n'
        '        for(int i = 0; i &lt; board.length; i++){\n'
        '            for(int j = 0; j &lt; board[0].length; j++){\n'
        '                if(board[i][j] != \'.\')\n'
        '                    continue;\n'
        '                for(char k = \'1\'; k &lt;= \'9\'; k++){\n'
        '                    if(isVaild(i, j, k, board)){\n'
        '                        board[i][j] = k;\n'
        '                        if(dfs(board))\n'
        '                            return true;\n'
        '                        board[i][j] = \'.\';\n'
        '                    }\n'
        '                }\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '    public boolean isVaild(int row, int col, char val, char[][] board){\n'
        '        for (int i = 0; i &lt; 9; i++){\n'
        '            if (board[row][i] == val){\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        for (int j = 0; j &lt; 9; j++){\n'
        '            if (board[j][col] == val){\n'
        '                return false;\n'
        '            }\n'
        '        }\n'
        '        int startRow = (row / 3) * 3;\n'
        '        int startCol = (col / 3) * 3;\n'
        '        for (int i = startRow; i &lt; startRow + 3; i++){\n'
        '            for (int j = startCol; j &lt; startCol + 3; j++){\n'
        '                if (board[i][j] == val){\n'
        '                    return false;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return true;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '与N皇后的区别：<br>'
    '1. 需要遍历所有空格（双重for），而非逐行放置<br>'
    '2. 三维剪枝：行、列、3x3宫格三个维度排除已用数字<br>'
    '3. 宫格起点计算：startRow = (row/3)*3，startCol = (col/3)*3<br>'
    '4. 贪心选择：优先填充可能性最少的格子可加速<br>'
    '5. 一旦找到解立即返回 true，利用短路效应剪枝')

# ============================================================
# 12. 寻找旋转排序数组中的最小值 II
# ============================================================
p = '寻找旋转排序数组中的最小值 II'
d = make_deck(1747302112, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '已知一个长度为 n 的数组，预先按照升序排列，经由 1 到 n 次旋转后，'
    '得到输入数组。数组中可能存在重复元素。请找出数组中的最小元素。'
    '与 153 题的区别：本题允许重复元素。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：最坏 {{c1::O(n)}}（全相同元素时），平均 {{c2::O(log n)}}<br>空间：{{c3::O(1)}}')
add_basic(d, make_front(p, '题解(二分查找)'),
    '与153的唯一区别：nums[mid]==nums[right]时无法判断，只能right--缩小范围，最坏退化为O(n)。<br>'
    + code(
        'class Solution {\n'
        '    public int findMin(int[] nums) {\n'
        '        int left = 0;\n'
        '        int right = nums.length - 1;\n'
        '        while(left &lt; right){\n'
        '            int mid = left + (right - left) / 2;\n'
        '            if(nums[mid] &gt; nums[right])\n'
        '                left = mid + 1;\n'
        '            else if(nums[mid] &lt; nums[right])\n'
        '                right = mid;\n'
        '            else\n'
        '                right--;\n'
        '        }\n'
        '        return nums[left];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '153（无重复）vs 154（有重复）的核心区别：<br>'
    'nums[mid] == nums[right] 时丢失了单调性信息，无法判断最小值在左还是右。<br>'
    '因此只能保守地 right--，最坏退化为 O(n)。<br>'
    '其他情况与153相同：nums[mid]&gt;nums[right]→最小值在右，left=mid+1；'
    'nums[mid]&lt;nums[right]→最小值在左或就是mid，right=mid。')

# ============================================================
# 13. 分割数组的最大值
# ============================================================
p = '分割数组的最大值'
d = make_deck(1747302113, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个非负整数数组 nums 和一个整数 m，你需要将这个数组分成 m 个非空的连续子数组。'
    '设计一个算法使得这 m 个子数组各自和的最大值最小。'
    + img('image 24.png'))
add_cloze(d, make_front(p, '复杂度'),
    '二分法：时间 {{c1::O(n*log(sum))}}，空间 {{c2::O(1)}}<br>'
    'DP法：时间 {{c3::O(n²*m)}}，空间 {{c4::O(n*m)}}')
add_basic(d, make_front(p, '题解(二分查找)'),
    '二分"子数组和的最大值"，贪心验证分割数。下界=max(nums)，上界=sum(nums)。<br>'
    + code(
        'public class Solution {\n'
        '    public int splitArray(int[] nums, int m) {\n'
        '        int max = 0;\n'
        '        int sum = 0;\n'
        '        for (int num : nums) {\n'
        '            max = Math.max(max, num);\n'
        '            sum += num;\n'
        '        }\n'
        '        int left = max;\n'
        '        int right = sum;\n'
        '        while (left &lt; right) {\n'
        '            int mid = left + (right - left) / 2;\n'
        '            int splits = split(nums, mid);\n'
        '            if (splits &gt; m) {\n'
        '                left = mid + 1;\n'
        '            } else {\n'
        '                right = mid;\n'
        '            }\n'
        '        }\n'
        '        return left;\n'
        '    }\n'
        '    private int split(int[] nums, int maxIntervalSum) {\n'
        '        int splits = 1;\n'
        '        int curIntervalSum = 0;\n'
        '        for (int num : nums) {\n'
        '            if (curIntervalSum + num &gt; maxIntervalSum) {\n'
        '                curIntervalSum = 0;\n'
        '                splits++;\n'
        '            }\n'
        '            curIntervalSum += num;\n'
        '        }\n'
        '        return splits;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '二分答案 + 贪心验证：<br>'
    '1. 答案具有二段性：若最大和为 X 时能分成 &lt;=m 段，则更大的X也能<br>'
    '2. 下界 left = max(nums)（至少一段包含最大元素），上界 right = sum(nums)<br>'
    '3. split 函数贪心分割：当前和+num&gt;mid时另起一段，段数+1<br>'
    '4. 分裂数 &gt; m → mid太小，left=mid+1；否则 right=mid<br>'
    '5. DP法（O(n²*m)）适合理解，二分法才是最优解')

# ============================================================
# 14. 不同的子序列
# ============================================================
p = '不同的子序列'
d = make_deck(1747302114, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s 和一个字符串 t，计算在 s 的子序列中 t 出现的个数。<br>'
    '字符串的一个子序列是指通过删除一些字符而不改变剩余字符相对位置形成的新字符串。'
    + img('image 25.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(m*n)}} — 二维DP<br>空间：{{c2::O(m*n)}} — dp数组')
add_basic(d, make_front(p, '题解(DP)'),
    '匹配时两种策略之和：不用s[i-1]匹配t[j-1] + 用s[i-1]匹配t[j-1]。<br>'
    + code(
        'class Solution {\n'
        '    public int numDistinct(String s, String t) {\n'
        '        int slen = s.length();\n'
        '        int tlen = t.length();\n'
        '        int[][] dp = new int[slen+1][tlen+1];\n'
        '        for(int i = 0; i &lt;= slen; i++){\n'
        '            for(int j = 0; j &lt;= tlen; j++){\n'
        '                if(j == 0)\n'
        '                    dp[i][j] = 1;\n'
        '                else if(i == 0)\n'
        '                    dp[i][j] = 0;\n'
        '                else{\n'
        '                    if(s.charAt(i-1) == t.charAt(j-1)){\n'
        '                        dp[i][j] = dp[i-1][j] + dp[i-1][j-1];\n'
        '                    }\n'
        '                    else{\n'
        '                        dp[i][j] = dp[i-1][j];\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return dp[slen][tlen];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    'DP状态：dp[i][j] 表示 s 的前 i 个字符中 t 的前 j 个字符出现的次数。<br>'
    '初始化：dp[i][0]=1（空t是任何s的子序列，有1种方案"不选任何字符"）。<br>'
    '转移：s[i-1]==t[j-1]时，dp[i][j]=dp[i-1][j]+dp[i-1][j-1]<br>'
    '&nbsp;&nbsp;(不使用s[i-1]去匹配t[j-1]的方案 + 使用s[i-1]去匹配t[j-1]的方案)<br>'
    's[i-1]!=t[j-1]时，dp[i][j]=dp[i-1][j]（只能不用当前s字符）')

# ============================================================
# 15. 最大子矩阵
# ============================================================
p = '最大子矩阵'
d = make_deck(1747302115, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个正整数、负整数和 0 组成的 N × M 矩阵，编写代码找出元素总和最大的子矩阵。'
    '返回一个数组 [r1, c1, r2, c2]，其中 r1, c1 分别代表子矩阵左上角的行号和列号，'
    'r2, c2 分别代表右下角的行号和列号。若有多个满足条件的子矩阵，返回任意一个均可。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n²*m)}} — 枚举上下边界+一维Kadane<br>空间：{{c2::O(m)}} — sumCol数组+常数')
add_basic(d, make_front(p, '题解(前缀和+Kadane)'),
    '纵向压缩：枚举上下行i~j，将列累加成一维数组sumCol，再用Kadane求最大子数组和及其起止位置。<br>'
    + code(
        'class Solution {\n'
        '    public int[] getMaxMatrix(int[][] matrix) {\n'
        '        int[] res = new int[4];\n'
        '        int n = matrix.length;\n'
        '        int m = matrix[0].length;\n'
        '        int[] sumCol = new int[m];\n'
        '        int sum;\n'
        '        int maxsum = Integer.MIN_VALUE;\n'
        '        int leftRowNum = 0, leftColNum = 0;\n'
        '        for(int i = 0; i &lt; n; i++){\n'
        '            for(int k = 0; k &lt; m; k++)\n'
        '                sumCol[k] = 0;\n'
        '            for(int j = i; j &lt; n; j++){\n'
        '                sum = 0;\n'
        '                for(int z = 0; z &lt; m; z++){\n'
        '                    sumCol[z] += matrix[j][z];\n'
        '                    if(sum &gt; 0)\n'
        '                        sum += sumCol[z];\n'
        '                    else{\n'
        '                        sum = sumCol[z];\n'
        '                        leftRowNum = i;\n'
        '                        leftColNum = z;\n'
        '                    }\n'
        '                    if(sum &gt; maxsum){\n'
        '                        maxsum = sum;\n'
        '                        res[0] = leftRowNum;\n'
        '                        res[1] = leftColNum;\n'
        '                        res[2] = j;\n'
        '                        res[3] = z;\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '二维最大子矩阵 = 枚举上下边界 + 一维最大子数组（Kadane算法变形）。<br>'
    '关键步骤：<br>'
    '1. sumCol[z] 记录第z列在行i到行j之间的累加和<br>'
    '2. 内层对sumCol用Kadane算法，找最大子数组和及其起止位置<br>'
    '3. 每次更新最大值时同时记录左上角(row=i, col=leftCol)和右下角(row=j, col=z)<br>'
    '4. 注意 sum&lt;=0 时重新自立门户，记录新的左上角起始位置')

# ============================================================
# 16. 和至少为 K 的最短子数组
# ============================================================
p = '和至少为 K 的最短子数组'
d = make_deck(1747302116, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个整数数组 nums 和一个整数 k，找出 nums 中和至少为 k 的最短非空子数组，'
    '并返回该子数组的长度。如果不存在这样的子数组，返回 -1。<br>'
    '注意：nums 中可能包含负数，因此不能使用普通滑动窗口。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 一次遍历+单调队列<br>空间：{{c2::O(n)}} — 前缀和+队列')
add_basic(d, make_front(p, '题解(前缀和+单调队列)'),
    '前缀和 + 单调递增队列：prefix[i] 维护递增序列，队首满足条件则更新答案。<br>'
    + code(
        'class Solution {\n'
        '    public int shortestSubarray(int[] nums, int k) {\n'
        '        int len = nums.length;\n'
        '        int[] prefix = new int[len + 1];\n'
        '        for(int i = 0; i &lt; len; i++){\n'
        '            prefix[i+1] = prefix[i] + nums[i];\n'
        '            if(nums[i] &gt;= k)\n'
        '                return 1;\n'
        '        }\n'
        '        int res = Integer.MAX_VALUE;\n'
        '        Deque&lt;Integer&gt; queue = new ArrayDeque&lt;&gt;();\n'
        '        for(int i = 0; i &lt; prefix.length; i++){\n'
        '            while(!queue.isEmpty() &amp;&amp; prefix[i] &lt;= prefix[queue.getLast()])\n'
        '                queue.removeLast();\n'
        '            while(!queue.isEmpty() &amp;&amp; prefix[i] - prefix[queue.peek()] &gt;= k)\n'
        '                res = Math.min(res, i - queue.poll());\n'
        '            queue.add(i);\n'
        '        }\n'
        '        return res == Integer.MAX_VALUE ? -1 : res;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '为什么不能用普通滑动窗口？因为 nums[i] 可能为负，右指针右移不保证区间和增大，'
    '左指针右移不保证区间和减小（无二段性）。<br>'
    '正确解法：前缀和 + 单调递增队列。<br>'
    '1. 计算前缀和 prefix[i]<br>'
    '2. 队列维护 prefix 值的递增序列（若 prefix[i] &lt;= 队尾，则队尾的值永无机会成为最优左边界）<br>'
    '3. 队首满足 prefix[i]-prefix[q.peek()] &gt;= k 则更新答案并弹出（后续更长的子数组不可能是最优）')

# ============================================================
# 17. 山脉数组中查找目标值
# ============================================================
p = '山脉数组中查找目标值'
d = make_deck(1747302117, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个山脉数组 mountainArr，返回使得 mountainArr.get(index) 等于 target 的最小下标。'
    '如果不存在这样的下标，返回 -1。<br>'
    '山脉数组：先严格递增后严格递减的数组（长度&gt;=3），只有一个峰顶。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(log n)}} — 三次二分查找<br>空间：{{c2::O(1)}}')
add_basic(d, make_front(p, '题解(三次二分)'),
    '三步二分：1.找峰顶 2.升序区二分 3.降序区二分。找峰顶：mid&gt;mid+1→峰顶在左（含mid），否则在右。<br>'
    + code(
        'class Solution {\n'
        '    public int findInMountainArray(int target, MountainArray m) {\n'
        '        int len = m.length();\n'
        '        if(len &lt; 3)\n'
        '            return -1;\n'
        '        int topIndex = findTop(m, 0, len - 1);\n'
        '        int addIndex = findAdd(m, 0, topIndex, target);\n'
        '        if(addIndex != -1)\n'
        '            return addIndex;\n'
        '        int reduceIndex = findReduce(m, topIndex + 1, len - 1, target);\n'
        '        return reduceIndex;\n'
        '    }\n'
        '    public int findAdd(MountainArray m, int i, int j, int target){\n'
        '        int left = i, right = j;\n'
        '        while(left &lt; right){\n'
        '            int mid = (left + right) / 2;\n'
        '            if(target &lt; m.get(mid))\n'
        '                right = mid - 1;\n'
        '            else\n'
        '                left = mid;\n'
        '        }\n'
        '        return m.get(left) == target ? left : -1;\n'
        '    }\n'
        '    public int findReduce(MountainArray m, int i, int j, int target){\n'
        '        int left = i, right = j;\n'
        '        while(left &lt; right){\n'
        '            int mid = (left + right) / 2;\n'
        '            if(target &lt; m.get(mid))\n'
        '                left = mid - 1;\n'
        '            else\n'
        '                right = mid;\n'
        '        }\n'
        '        return m.get(left) == target ? left : -1;\n'
        '    }\n'
        '    public int findTop(MountainArray m, int i, int j){\n'
        '        while(i &lt; j){\n'
        '            int mid = (i + j) / 2;\n'
        '            if(m.get(mid) &gt; m.get(mid + 1))\n'
        '                j = mid;\n'
        '            else\n'
        '                i = mid + 1;\n'
        '        }\n'
        '        return i;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '三步二分：<br>'
    '1. 找峰顶：mid &gt; mid+1 → 峰顶在左（含mid），否则峰顶在右（不含mid）<br>'
    '2. 升序区二分：target &lt; mid → right=mid-1，否则 left=mid<br>'
    '3. 降序区二分：target &lt; mid → left=mid-1（降序，小数在右），否则 right=mid<br>'
    '核心：将山脉数组分为两段有序数组，分别二分查找。总复杂度 O(log n)。')

# ============================================================
# 18. 俄罗斯套娃信封问题
# ============================================================
p = '俄罗斯套娃信封问题'
d = make_deck(1747302118, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个二维整数数组 envelopes，其中 envelopes[i] = [wi, hi]，表示第 i 个信封的宽度和高度。'
    '当另一个信封的宽度和高度都比这个信封大的时候，这个信封就可以放进另一个信封里。'
    '请计算最多能有多少个信封能组成一组"俄罗斯套娃"信封。'
    + img('image 26.png') + img('image 27.png') + img('image 28.png') + img('image 29.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n log n)}} — 排序+二分LIS<br>空间：{{c2::O(n)}} — top数组')
add_basic(d, make_front(p, '题解(排序+二分LIS)'),
    '宽度升序、同宽高度降序后，对高度数组求LIS（二分扑克牌堆法）。宽度相同时高度降序防止同宽嵌套。<br>'
    + code(
        'class Solution {\n'
        '    public int maxEnvelopes(int[][] envelopes) {\n'
        '        int n = envelopes.length;\n'
        '        if(n &lt; 2){\n'
        '            return n;\n'
        '        }\n'
        '        Arrays.sort(envelopes, (a, b)-&gt;{\n'
        '            if(a[0] == b[0])\n'
        '                return b[1] - a[1];\n'
        '            return a[0] - b[0];\n'
        '        });\n'
        '        int[] height = new int[n];\n'
        '        for (int i = 0; i &lt; n; i++)\n'
        '            height[i] = envelopes[i][1];\n'
        '        int piles = 0;\n'
        '        int[] top = new int[n];\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            int poker = height[i];\n'
        '            int left = 0, right = piles;\n'
        '            while (left &lt; right) {\n'
        '                int mid = (left + right) / 2;\n'
        '                if (top[mid] &gt;= poker)\n'
        '                    right = mid;\n'
        '                else\n'
        '                    left = mid + 1;\n'
        '            }\n'
        '            if (left == piles) piles++;\n'
        '            top[left] = poker;\n'
        '        }\n'
        '        return piles;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '二维LIS问题的转化：<br>'
    '1. 排序规则：宽度升序；宽度相同时，高度降序<br>'
    '2. 高度降序的意义：宽度相同的信封不能嵌套，降序保证同宽度的不会被选入LIS<br>'
    '3. 对高度数组求最长递增子序列（LIS），用二分法（扑克牌堆）O(n log n)<br>'
    '4. LIS二分法：top[]数组维护各堆堆顶，二分查找插入位置<br>'
    '5. 若 top[mid] &gt;= poker → right=mid；否则 left=mid+1')

# ============================================================
# 19. 让字符串成为回文串的最少插入次数
# ============================================================
p = '让字符串成为回文串的最少插入次数'
d = make_deck(1747302119, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给你一个字符串 s，每一次操作你都可以在字符串的任意位置插入任意字符。'
    '请你返回让 s 成为回文串的最少操作次数。')
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n²)}} — 二维DP<br>空间：{{c2::O(n²)}} — dp数组')
add_basic(d, make_front(p, '题解(DP-最长回文子序列)'),
    '最少插入次数 = 字符串总长度 - 最长回文子序列长度。dp[i][j]表示s[i..j]中最长回文子序列长度。<br>'
    + code(
        'class Solution {\n'
        '    public int minInsertions(String s) {\n'
        '        int len = s.length();\n'
        '        int[][] dp = new int[len][len];\n'
        '        for(int i = 0; i &lt; len; i++){\n'
        '            dp[i][i] = 1;\n'
        '        }\n'
        '        for(int i = len - 1; i &gt;= 0; i--){\n'
        '            for(int j = i + 1; j &lt; len; j++){\n'
        '                if(s.charAt(i) == s.charAt(j))\n'
        '                    dp[i][j] = dp[i+1][j-1] + 2;\n'
        '                else\n'
        '                    dp[i][j] = Math.max(dp[i+1][j], dp[i][j-1]);\n'
        '            }\n'
        '        }\n'
        '        return len - dp[0][len - 1];\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '巧妙转化：求最少插入字符数 = 求原字符串中已经构成回文的字符数（最长回文子序列），'
    '其余字符需要配对插入。<br>'
    'DP状态：dp[i][j] 表示 s[i..j] 中最长回文子序列的长度。<br>'
    '转移：s[i]==s[j] → dp[i+1][j-1]+2；否则 max(dp[i+1][j], dp[i][j-1])。<br>'
    '遍历顺序：i 从 n-1 到 0（从下到上），j 从 i+1 到 n-1（从左到右）。')

# ============================================================
# 20. 至多包含 K 个不同字符的最长子串
# ============================================================
p = '至多包含 K 个不同字符的最长子串'
d = make_deck(1747302120, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    '给定一个字符串 s，找出至多包含 k 个不同字符的最长子串 T，返回其长度。<br>'
    '注意与"至少有K个重复字符的最长子串"区分：本题是种类数限制，后者是重复次数限制。'
    + img('image 30.png'))
add_cloze(d, make_front(p, '复杂度'),
    '时间：{{c1::O(n)}} — 滑动窗口一次遍历<br>空间：{{c2::O(k)}} — HashMap最多k+1个键')
add_basic(d, make_front(p, '题解(滑动窗口)'),
    '标准滑动窗口：count 记录窗口内不同字符种类数。当 count&gt;k 时收紧左边界直到条件恢复。<br>'
    + code(
        'class Solution {\n'
        '    public int longestSubstring(String s, int k) {\n'
        '        if(k == 0)\n'
        '            return 0;\n'
        '        Map&lt;Character, Integer&gt; map = new HashMap&lt;&gt;();\n'
        '        int maxLen = 0, len = s.length();\n'
        '        int count = 0;\n'
        '        for(int left = 0, right = 0; right &lt; len; right++){\n'
        '            map.put(s.charAt(right), map.getOrDefault(s.charAt(right), 0) + 1);\n'
        '            if(map.get(s.charAt(right)) == 1)\n'
        '                count++;\n'
        '            while(count &gt; k){\n'
        '                map.put(s.charAt(left), map.get(s.charAt(left)) - 1);\n'
        '                if(map.get(s.charAt(left)) == 0)\n'
        '                    count--;\n'
        '                left++;\n'
        '            }\n'
        '            maxLen = Math.max(maxLen, right - left + 1);\n'
        '        }\n'
        '        return maxLen;\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '标准滑动窗口模板：<br>'
    '1. 右指针扩展：将字符加入窗口，更新计数（首次出现时 count++）<br>'
    '2. 内缩条件：while(count &gt; k) 不满足 → 左指针右移，减少字符计数<br>'
    '3. 字符计数归0时 count--，表示该字符已完全移出窗口<br>'
    '4. 每次窗口合法时更新 maxLen = right-left+1<br>'
    '区分记忆：本题考"种类数 &lt;=k"，另一题考"每类字符重复次数 &gt;=k"（分治/递归）')

# ============================================================
# 21. O(1)时间插入、删除和获取随机元素-允许重复
# ============================================================
p = 'O(1)时间插入、删除和获取随机元素-允许重复'
d = make_deck(1747302121, f'算法::力扣困难::{p}')
add_basic(d, make_front(p, '题干'),
    'RandomizedCollection 是一种包含数字集合的数据结构，支持重复元素。<br>'
    '实现以下功能，每个函数的平均时间复杂度为 O(1)：<br>'
    'insert(val)：向集合中插入 val（允许重复）<br>'
    'remove(val)：从集合中移除一个 val（如果有多个，只移除一个）<br>'
    'getRandom()：从当前集合中随机获取一个数字')
add_cloze(d, make_front(p, '复杂度'),
    'insert：{{c1::O(1)}}，remove：{{c2::O(1)}}，getRandom：{{c3::O(1)}}<br>空间：{{c4::O(n)}} — 数组+HashMap')
add_basic(d, make_front(p, '题解(HashMap+Array)'),
    '数组保证O(1)随机访问，HashMap(val→索引Set)保证O(1)查找。删除时与末尾交换再删末尾。<br>'
    + code(
        'public class RandomizedCollection {\n'
        '    Map&lt;Integer, Set&lt;Integer&gt;&gt; map;\n'
        '    int[] arr;\n'
        '    int size;\n'
        '    public RandomizedCollection() {\n'
        '        map = new HashMap&lt;&gt;();\n'
        '        arr = new int[20000];\n'
        '        size = 0;\n'
        '    }\n'
        '    public boolean insert(int val) {\n'
        '        arr[size++] = val;\n'
        '        Set&lt;Integer&gt; indexs = map.getOrDefault(val, new HashSet&lt;&gt;());\n'
        '        boolean result = indexs.isEmpty();\n'
        '        indexs.add(size-1);\n'
        '        map.put(val, indexs);\n'
        '        return result;\n'
        '    }\n'
        '    public boolean remove(int val) {\n'
        '        Set&lt;Integer&gt; indexs = map.getOrDefault(val, new HashSet&lt;&gt;());\n'
        '        boolean result = indexs.isEmpty();\n'
        '        if(!result){\n'
        '            int maxIndex = Integer.MIN_VALUE;\n'
        '            for(int index : indexs){\n'
        '                maxIndex = Math.max(maxIndex, index);\n'
        '            }\n'
        '            indexs.remove(maxIndex);\n'
        '            if(indexs.size() == 0)\n'
        '                map.remove(val);\n'
        '            else\n'
        '                map.put(val, indexs);\n'
        '            System.arraycopy(arr, maxIndex + 1, arr, maxIndex, size - maxIndex + 1);\n'
        '            size--;\n'
        '            if(size != maxIndex)\n'
        '                adjustMap(maxIndex);\n'
        '            return true;\n'
        '        }else\n'
        '            return false;\n'
        '    }\n'
        '    public int getRandom() {\n'
        '        int random = (int)(Math.random() * size);\n'
        '        return arr[random];\n'
        '    }\n'
        '    public void adjustMap(int index){\n'
        '        int pre = Integer.MIN_VALUE;\n'
        '        for (int i = index; i &lt; size; i++) {\n'
        '            if(pre == arr[i])\n'
        '                continue;\n'
        '            Set&lt;Integer&gt; integers = map.get(arr[i]);\n'
        '            Set&lt;Integer&gt; newIndexs = new HashSet&lt;&gt;();\n'
        '            for (Integer integer : integers) {\n'
        '                if(integer &gt; index)\n'
        '                    newIndexs.add(integer-1);\n'
        '                else\n'
        '                    newIndexs.add(integer);\n'
        '            }\n'
        '            map.put(arr[i], newIndexs);\n'
        '            pre = arr[i];\n'
        '        }\n'
        '    }\n'
        '}'
    ))
add_basic(d, make_front(p, '关键技巧'),
    '数据结构设计题的关键思想：<br>'
    '1. 数组保证 O(1) 随机访问（getRandom用随机下标）<br>'
    '2. HashMap保证 O(1) 查找（val→索引集合，Set处理重复元素）<br>'
    '3. 删除技巧：将要删除的元素与数组末尾交换，再删除末尾（O(1)而非O(n)）<br>'
    '4. 难点：删除后需更新被移动元素的索引映射，否则查找会出错<br>'
    '5. 与不重复版本的区别：不重复版用 Map&lt;Integer,Integer&gt;；重复版用 Map&lt;Integer,Set&lt;Integer&gt;&gt;')

if __name__ == '__main__':
    print(build(r'../../牌组/力扣困难.apkg'))
