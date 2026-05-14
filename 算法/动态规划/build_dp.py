"""
Build APKG for Dynamic Programming (37 problems, 7-9 cards each).
Run from 算法/动态规划/ directory (where images live).
Usage: python build_dp.py
Output: ../../牌组/算法/动态规划.apkg
"""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, build


def code(java: str) -> str:
    """Wrap Java code for highlight.js with HTML escaping."""
    import html as _html
    return f'<pre><code class="language-java">{_html.escape(java)}</code></pre>'


# ============================================================
# Deck 0: DP 原理通识
# ============================================================

d0 = make_deck(1747300100, '算法::动态规划::原理通识')

add_basic(d0, '什么是动态规划？两个核心性质？',
    'DP 通过分解为重叠子问题，利用最优子结构递推求最优解。\n'
    '1. 重叠子问题：子问题被反复计算，用记忆化/递推避免重复\n'
    '2. 最优子结构：原问题的最优解包含子问题的最优解')

add_basic(d0, '动态规划解题四步骤？',
    '1. 定义子问题/状态：dp[i] 代表什么？\n'
    '2. 写出状态转移方程\n'
    '3. 确定计算顺序（自底向上，依赖已算出）\n'
    '4. 空间优化（滚动变量/降维/原地修改）')

add_basic(d0, 'DP vs 贪心 vs 分治？',
    'DP：子问题有重叠，记录所有解，可回溯\n'
    '贪心：每步选局部最优，不回溯\n'
    '分治：子问题独立无重叠（如归并排序）')

add_basic(d0, 'DP 空间优化常见手段？',
    '1. 滚动变量：dp[i] 只依赖前 1-2 个状态 → 2-3 个变量\n'
    '2. 降维：二维只依赖上一行+本行左边 → 倒序一维\n'
    '3. 原地修改：直接复用输入数组')

add_basic(d0, '什么题目很可能用 DP？',
    '1. 求最值（最大子数组和、最少硬币）\n'
    '2. 求方案数（不同路径、零钱兑换 II）\n'
    '3. 求可行性（分割等和子集、单词拆分）\n'
    '4. 序列/字符串类：涉及前后选择决策')

add_basic(d0, '线性 DP 常见题型？',
    '1. 单串 dp[i]：以 i 结尾的 xxx\n'
    '2. 双串 dp[i][j]：两个序列匹配（编辑距离、LCS）\n'
    '3. 带维度扩展：增加 [持股][交易次数] 等维度')

add_basic(d0, '背包问题的本质特征？',
    '数组元素 + 目标值，每个元素选/不选。\n'
    '0-1 背包：每件选一次 → 倒序遍历\n'
    '完全背包：每件无限次 → 正序遍历')

add_cloze(d0, '状态转移核心模式：dp[i] = {{c1::max/min}}( {{c2::dp[i-1]}}, {{c3::dp[i-2] + ...}} )',
    '最值型 DP：分类讨论"选或不选"取最优')

add_cloze(d0, '降维关键：倒序防 {{c1::重复使用}}，正序允许 {{c2::无限次使用}}',
    '0-1 背包倒序，完全背包正序')

# ============================================================
# 1. 最大子数组和
# ============================================================
p = '最大子数组和'
d = make_deck(1747300101, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 nums，找出一个具有最大和的连续子数组，返回其最大和。'
    + img('image.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::以 nums[i] 结尾的连续子数组的最大和}}',
    '必须包含 nums[i]')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>if (dp[i-1] > 0) dp[i] = {{c1::dp[i-1] + nums[i]}}<br>'
    + 'else dp[i] = {{c2::nums[i]}}',
    '正前缀累加，负前缀丢弃重来')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::nums[0]}}, res = {{c2::dp[0]}}',
    'res 不能初始化为 0，全负数数组会出错')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len-1 正向遍历。<br>dp[i] 只依赖 dp[i-1]，可以滚动变量优化到 O(1) 空间。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 res（不是 dp[n-1]）。<br>因为最大子数组不一定以最后一个元素结尾。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP (Kadane)</b>：<br>- 时间 O(n)：遍历数组一次，每个位置O(1)操作（1次if + 1次max）→ n×O(1)=O(n)<br>- 空间 O(1)：只需dp和res两个变量，不随n增长<br><br><b>分治</b>：<br>- 时间 O(n log n)：T(n)=2T(n/2)+O(n)，递归深度log n，每层合并O(n)<br>- 空间 O(log n)：递归栈深度')

add_basic(d, make_front(p, '题解(DP)'),
    '正前缀累加，负前缀丢弃重来。O(n) O(1)。<br>'
    + code(
        'class Solution {\n'
        '    public int maxSubArray(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        int[] dp = new int[len];\n'
        '        dp[0] = nums[0];\n'
        '        int res = dp[0];\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            if (dp[i - 1] &gt; 0)\n'
        '                dp[i] = dp[i - 1] + nums[i];\n'
        '            else\n'
        '                dp[i] = nums[i];\n'
        '            res = Math.max(dp[i], res);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(分治)'),
    '分治：左半、右半、跨中点三种情况取 max。T(n)=2T(n/2)+O(n)=O(n log n)。<br>'
    + code(
        'public class Solution {\n'
        '    public int maxSubArray(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        if (len == 0) return 0;\n'
        '        return maxSubArraySum(nums, 0, len - 1);\n'
        '    }\n'
        '\n'
        '    private int maxCrossingSum(int[] nums, int left, int mid, int right) {\n'
        '        int sum = 0;\n'
        '        int leftSum = Integer.MIN_VALUE;\n'
        '        for (int i = mid; i &gt;= left; i--) {\n'
        '            sum += nums[i];\n'
        '            if (sum &gt; leftSum) leftSum = sum;\n'
        '        }\n'
        '        sum = 0;\n'
        '        int rightSum = Integer.MIN_VALUE;\n'
        '        for (int i = mid + 1; i &lt;= right; i++) {\n'
        '            sum += nums[i];\n'
        '            if (sum &gt; rightSum) rightSum = sum;\n'
        '        }\n'
        '        return leftSum + rightSum;\n'
        '    }\n'
        '\n'
        '    private int maxSubArraySum(int[] nums, int left, int right) {\n'
        '        if (left == right) return nums[left];\n'
        '        int mid = left + (right - left) / 2;\n'
        '        return max3(maxSubArraySum(nums, left, mid),\n'
        '                maxSubArraySum(nums, mid + 1, right),\n'
        '                maxCrossingSum(nums, left, mid, right));\n'
        '    }\n'
        '\n'
        '    private int max3(int num1, int num2, int num3) {\n'
        '        return Math.max(num1, Math.max(num2, num3));\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 2. 返回最大子数组的起始位置和结束位置
# ============================================================
p = '最大子数组和(返回位置)'
d = make_deck(1747300102, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数数组 nums，返回最大和的连续子数组的（最大和，起始下标，结束下标）。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp = {{c1::以当前元素结尾的最大子数组和}}<br>'
    + 'maxSum = {{c2::全局最大子数组和}}<br>'
    + 'tempStart = {{c3::当前子数组的起始位置}}',
    '需要额外维护起始位置')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>if (dp + nums[i] &lt; nums[i]) { dp = nums[i]; tempStart = {{c1::i}}; }<br>'
    + 'else dp = {{c2::dp + nums[i]}};',
    '前缀为负贡献时重新开始')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp = {{c1::nums[0]}}, maxSum = {{c2::nums[0]}}, tempStart = {{c3::0}}, start = 0, end = 0',
    '全部从第一个元素开始')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len-1 正向遍历。维护 tempStart 记录当前子数组起点。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 [maxSum, start, end]。<br>注意：只有 dp 严格大于 maxSum 时才更新 start 和 end。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP (Kadane)</b>：<br>- 时间 O(n)：遍历数组一次，每个位置O(1)操作（1次if + 1次max）→ n×O(1)=O(n)<br>- 空间 O(1)：只需dp和res两个变量，不随n增长<br><br><b>分治</b>：<br>- 时间 O(n log n)：T(n)=2T(n/2)+O(n)，递归深度log n，每层合并O(n)<br>- 空间 O(log n)：递归栈深度')

add_basic(d, make_front(p, '题解'),
    '维护 tempStart 记录当前子数组起点，dp > maxSum 时更新 start/end。<br>'
    + code(
        'public class Solution {\n'
        '    public static int[] maxSubArrayRange(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return new int[]{-1, -1};\n'
        '        int dp = nums[0];\n'
        '        int maxSum = nums[0];\n'
        '        int tempStart = 0;\n'
        '        int start = 0;\n'
        '        int end = 0;\n'
        '        for (int i = 1; i &lt; nums.length; i++) {\n'
        '            if (dp + nums[i] &lt; nums[i]) {\n'
        '                dp = nums[i];\n'
        '                tempStart = i;\n'
        '            } else {\n'
        '                dp = dp + nums[i];\n'
        '            }\n'
        '            if (dp &gt; maxSum) {\n'
        '                maxSum = dp;\n'
        '                start = tempStart;\n'
        '                end = i;\n'
        '            }\n'
        '        }\n'
        '        return new int[]{maxSum, start, end};\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 3. 买卖股票的最佳时机
# ============================================================
p = '买卖股票的最佳时机'
d = make_deck(1747300103, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定数组 prices，最多完成 1 笔交易（买入一次并卖出一次），返回最大利润。不能获利返回 0。'
    + img('image 1.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][0] = {{c1::第 i 天不持股的最大现金}}<br>'
    + 'dp[i][1] = {{c2::第 i 天持股的最大现金}}',
    '多阶段决策：每天结束时持股/不持股')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][0] = max({{c1::dp[i-1][0]}}, {{c2::dp[i-1][1]+prices[i]}})<br>'
    + 'dp[i][1] = max({{c3::dp[i-1][1]}}, {{c4::-prices[i]}})',
    '只能买一次：买入直接用 -prices[i]，不能用之前赚的钱')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][0] = {{c1::0}}, dp[0][1] = {{c2::-prices[0]}}',
    '第一天不持股现金为 0，持股即买入花费 prices[0]')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len-1 正向遍历。<br>可以优化为两个变量：持有 = max(持有, -prices[i])，不持有 = max(不持有, 持有+prices[i])。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[len-1][0]（最后一天不持股的最大现金）。<br>因为持股未卖出不算获利。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP（二维状态机）</b>：<br>- 时间 O(n)：遍历prices数组n天，每天更新持股/不持股两个状态，每次O(1) → n×2×O(1)=O(n)<br>- 空间 O(1)：dp[i]只依赖dp[i-1]，滚动优化后只需hold和notHold两个变量<br><br><b>贪心（一次遍历）</b>：记录历史最低价min，每天计算prices[i]-min并更新最大利润<br>- 时间 O(n) / 空间 O(1)')

add_basic(d, make_front(p, '题解(DP)'),
    '只能交易一次，买入用 -prices[i] 而非 dp[i-1][0]-prices[i]。<br>'
    + code(
        'class Solution {\n'
        '    public int maxProfit(int[] prices) {\n'
        '        int len = prices.length;\n'
        '        if (len &lt; 2) return 0;\n'
        '        int[][] dp = new int[len][2];\n'
        '        dp[0][0] = 0;\n'
        '        dp[0][1] = -prices[0];\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            dp[i][0] = Math.max(dp[i - 1][0], dp[i - 1][1] + prices[i]);\n'
        '            dp[i][1] = Math.max(dp[i - 1][1], -prices[i]);\n'
        '        }\n'
        '        return dp[len - 1][0];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(贪心)'),
    '记录历史最低价 min，遍历 prices[i]，max = max(max, prices[i] - min)，min = min(min, prices[i])。<br>'
    '本质：每一天假设在历史最低点买入，当天卖出，取最大利润。')

# ============================================================
# 4. 买卖股票的最佳时机 II
# ============================================================
p = '买卖股票的最佳时机 II'
d = make_deck(1747300104, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定数组 prices，可完成任意多笔交易（同一时间只能持一股），返回最大利润。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][0] = {{c1::第 i 天不持股的最大现金}}<br>'
    + 'dp[i][1] = {{c2::第 i 天持股的最大现金}}',
    '与 I 的状态定义完全相同')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][0] = max(dp[i-1][0], {{c1::dp[i-1][1]+prices[i]}})<br>'
    + 'dp[i][1] = max(dp[i-1][1], {{c2::dp[i-1][0]-prices[i]}})',
    '不限制交易次数：买入时可用之前卖出赚的钱（dp[i-1][0]）')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][0] = {{c1::0}}, dp[0][1] = {{c2::-prices[0]}}',
    '同 I')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len-1 正向遍历。与 I 的唯一代码区别：买入时用 dp[i-1][0]-prices[i] 而非 -prices[i]。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[len-1][0]（最后一天不持股的最大现金）。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP（二维状态机）</b>：<br>- 时间 O(n)：遍历prices数组n天，每天更新持股/不持股两个状态，每次O(1) → n×2×O(1)=O(n)<br>- 空间 O(1)：dp[i]只依赖dp[i-1]，滚动优化后只需hold和notHold两个变量<br><br><b>贪心（一次遍历）</b>：记录历史最低价min，每天计算prices[i]-min并更新最大利润<br>- 时间 O(n) / 空间 O(1)')

add_basic(d, make_front(p, '题解(DP)'),
    '与 I 的唯一区别：买入时用 dp[i-1][0]-prices[i] 而非 -prices[i]。<br>'
    + code(
        'class Solution {\n'
        '    public int maxProfit(int[] prices) {\n'
        '        int len = prices.length;\n'
        '        if (len &lt; 2) return 0;\n'
        '        int[][] dp = new int[len][2];\n'
        '        dp[0][0] = 0;\n'
        '        dp[0][1] = -prices[0];\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            dp[i][0] = Math.max(dp[i - 1][0], dp[i - 1][1] + prices[i]);\n'
        '            dp[i][1] = Math.max(dp[i - 1][1], dp[i - 1][0] - prices[i]);\n'
        '        }\n'
        '        return dp[len - 1][0];\n'
        '    }\n'
        '}'
    ))

add_cloze(d, make_front(p, '题解(贪心)')
    + '<br>if(prices[i] &gt; prices[i-1]) res += {{c1::prices[i] - prices[i-1]}};',
    '只要今天比昨天贵就赚差价，等价于无限次交易')

# ============================================================
# 5. 买卖股票的最佳时机 III
# ============================================================
p = '买卖股票的最佳时机 III'
d = make_deck(1747300105, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定数组 prices，最多完成 2 笔交易，返回最大利润。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j][k]：第 i 天，j = {{c1::是否持股(0/1)}}，k = {{c2::已卖出次数(0/1/2)}}',
    '新增卖出次数维度 k，从 0 到 2')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>不持股已卖k次：max({{c1::dp[i-1][1][k-1]+prices[i]}}, {{c2::dp[i-1][0][k]}})<br>'
    + '持股已卖k次：max({{c3::dp[i-1][0][k]-prices[i]}}, {{c4::dp[i-1][1][k]}})',
    'III 中卖出时 k+1（依赖 k-1），买入时 k 不变')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][0][0] = {{c1::0}}, dp[0][1][0] = {{c2::-prices[0]}}<br>'
    + 'dp[0][0][1]=dp[0][0][2]=dp[0][1][1]=dp[0][1][2] = {{c3::MIN_VALUE/2}}',
    '第一天不可能已卖出或多次交易，设为负无穷')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len-1 正序遍历。共 6 种状态（持股×卖出次数），每一轮更新所有状态。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 max(dp[len-1][0][1], dp[len-1][0][2], 0)。<br>可能卖出 1 次或 2 次获利最大，也可能不交易。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP（状态机）</b>：<br>- 时间 O(n)：遍历一次，与I的唯一区别是买入时用dp[i-1][0]-prices[i]（而非-prices[i]），允许用之前的利润再买入 → O(n)<br>- 空间 O(1)：滚动优化后只需hold和notHold两个变量<br><br><b>贪心</b>：只要prices[i]&gt;prices[i-1]就累加差价，等价于无限次交易<br>- 时间 O(n) / 空间 O(1)')

add_basic(d, make_front(p, '题解'),
    '卖出时交易次数+1。6 种状态：持股/不持股 × 已卖0/1/2次。<br>'
    + code(
        'class Solution {\n'
        '    public int maxProfit(int[] prices) {\n'
        '        int len = prices.length;\n'
        '        int min = Integer.MIN_VALUE / 2;\n'
        '        if (len &lt; 2) return 0;\n'
        '        int[][][] dp = new int[len][2][3];\n'
        '        dp[0][0][0] = 0;\n'
        '        dp[0][1][0] = -prices[0];\n'
        '        dp[0][0][1] = min;\n'
        '        dp[0][0][2] = min;\n'
        '        dp[0][1][1] = min;\n'
        '        dp[0][1][2] = min;\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            dp[i][0][0] = 0;\n'
        '            dp[i][0][1] = Math.max(dp[i-1][1][0] + prices[i], dp[i-1][0][1]);\n'
        '            dp[i][0][2] = Math.max(dp[i-1][1][1] + prices[i], dp[i-1][0][2]);\n'
        '            dp[i][1][0] = Math.max(dp[i-1][0][0] - prices[i], dp[i-1][1][0]);\n'
        '            dp[i][1][1] = Math.max(dp[i-1][0][1] - prices[i], dp[i-1][1][1]);\n'
        '            dp[i][1][2] = min;\n'
        '        }\n'
        '        return Math.max(Math.max(dp[len-1][0][1], dp[len-1][0][2]), 0);\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 6. 买卖股票的最佳时机 IV
# ============================================================
p = '买卖股票的最佳时机 IV'
d = make_deck(1747300106, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数 k 和数组 prices，最多完成 k 笔交易，返回最大利润。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j][k]：第 i 天，j = {{c1::是否持股}}，k = {{c2::已交易次数}}<br>'
    + 'k = min(k, {{c3::len/2}})',
    'k 超过 len/2 等价于无限次交易（退化为 II）')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][0][j] = max(dp[i-1][1][j]+prices[i], dp[i-1][0][j])<br>'
    + 'dp[i][1][j] = max({{c1::dp[i-1][0][j-1]-prices[i]}}, dp[i-1][1][j])',
    'IV 与 III 相反：买入时 j-1（买入算一次交易），卖出时 j 不变')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][0][0] = 0, dp[0][1][0] = {{c1::-prices[0]}}<br>'
    + '其余所有状态初始化为 {{c2::MIN_VALUE/2}}',
    '除 2 防止 -MIN_VALUE+1 溢出变成正数')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len-1，j 从 1 到 k 双重循环。<br>注意 k 需预处理：k = min(k, len/2)。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[len-1][0][k]（最后一天不持股、最多 k 次交易的最大利润）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：每天有6种状态（持股/不持股 × 已卖出0/1/2次），状态数固定为6不随n增长，每步O(1) → O(n)<br>- 空间 O(1)：dp[i]只依赖dp[i-1]的6个状态值，用6个变量滚动即可')

add_basic(d, make_front(p, '题解'),
    '买入时交易次数+1（与 III 相反：III 是卖出时+1）。k 需预处理 min(k, len/2)。<br>'
    + code(
        'class Solution {\n'
        '    public int maxProfit(int k, int[] prices) {\n'
        '        int len = prices.length;\n'
        '        int min = Integer.MIN_VALUE / 2;\n'
        '        if (len &lt; 2) return 0;\n'
        '        int[][][] dp = new int[len][2][k + 1];\n'
        '        k = Math.min(k, len / 2);\n'
        '        for (int i = 1; i &lt;= k; i++) {\n'
        '            dp[0][0][i] = 0;\n'
        '            dp[0][1][i] = -prices[0];\n'
        '        }\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            for (int j = 1; j &lt;= k; j++) {\n'
        '                dp[i][0][j] = Math.max(dp[i-1][1][j] + prices[i], dp[i-1][0][j]);\n'
        '                dp[i][1][j] = Math.max(dp[i-1][0][j-1] - prices[i], dp[i-1][1][j]);\n'
        '            }\n'
        '        }\n'
        '        return dp[len-1][0][k];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 7. 最长上升子序列 (LIS)
# ============================================================
p = '最长上升子序列'
d = make_deck(1747300107, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定一个整数数组 nums，返回其中最长严格递增子序列的长度。子序列不要求连续。'
    + img('image 4.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::以 nums[i] 结尾的最长递增子序列长度}}',
    '必须以 i 结尾')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>for(j=0;j&lt;i;j++) if(nums[j]&lt;nums[i]) dp[i]={{c1::Math.max(dp[i], dp[j]+1)}}',
    '向前扫描所有比 nums[i] 小的位置，取最长+1')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[i] = {{c1::1}}（全部填充为 1）',
    '单个元素本身也是长度为 1 的子序列')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 0 到 len-1 正向遍历，每个 i 内 j 从 0 到 i-1。O(n²)。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 max(dp[0..n-1])，即 res = max(res, dp[i]) 在循环中持续更新。<br>因为最长子序列不一定以最后一个元素结尾。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n×k)：外层遍历n天，内层遍历k次交易 → n×k次状态转移。当k≥n/2时等效于无限交易，实际退化为O(n)<br>- 空间 O(k)：buy和sell两个长度为k+1的数组滚动更新。优化技巧：k=min(k, n/2)预处理')

add_basic(d, make_front(p, '题解(DP)'),
    'O(n²)：每个 i 向前扫描所有比 nums[i] 小的 j，dp[i] = max(dp[i], dp[j]+1)。<br>'
    + code(
        'class Solution {\n'
        '    public int lengthOfLIS(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return 0;\n'
        '        int res = 0;\n'
        '        int[] dp = new int[nums.length];\n'
        '        Arrays.fill(dp, 1);\n'
        '        for (int i = 0; i &lt; nums.length; i++) {\n'
        '            for (int j = 0; j &lt; i; j++) {\n'
        '                if (nums[j] &lt; nums[i]) {\n'
        '                    dp[i] = Math.max(dp[i], dp[j] + 1);\n'
        '                }\n'
        '            }\n'
        '            res = Math.max(dp[i], res);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(二分)'),
    'tails[i] = 长度为 i+1 的子序列的最小尾元素。二分替换，严格递增。O(n log n)。<br>'
    + code(
        'class Solution {\n'
        '    public int lengthOfLIS(int[] nums) {\n'
        '        if (nums.length == 0) return 0;\n'
        '        int[] tails = new int[nums.length];\n'
        '        int res = 0;\n'
        '        for (int num : nums) {\n'
        '            int start = 0, end = res;\n'
        '            while (start &lt; end) {\n'
        '                int mid = (start + end) / 2;\n'
        '                if (tails[mid] &lt; num)\n'
        '                    start = mid + 1;\n'
        '                else\n'
        '                    end = mid;\n'
        '            }\n'
        '            tails[start] = num;\n'
        '            if (res == end) res++;\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 8. 接雨水
# ============================================================
p = '接雨水'
d = make_deck(1747300108, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定 n 个非负整数表示柱状图高度，计算下雨后能接到的雨水总量。'
    + img('image 5.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp_left[i] = {{c1::位置 i 左边最高的柱子高度}}<br>'
    + 'dp_right[i] = {{c2::位置 i 右边最高的柱子高度}}',
    '两遍扫描分别记录左右最高')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp_left[i] = max({{c1::dp_left[i-1]}}, {{c2::height[i-1]}})<br>'
    + 'dp_right[i] = max({{c3::dp_right[i+1]}}, {{c4::height[i+1]}})',
    '左→右记录左边最高，右→左记录右边最高')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp_left[0] = {{c1::0}}（最左边没有左墙）<br>'
    + 'dp_right[len-1] = {{c2::0}}（最右边没有右墙）',
    '边界柱子无法接水')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '先从左到右填 dp_left，再从右到左填 dp_right。<br>第三遍遍历：sum += max(0, min(dp_left[i], dp_right[i]) - height[i])。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 sum（每个柱子接水量的总和）。<br>每个柱子接水量 = min(左边最高, 右边最高) - 当前高度。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP (O(n²))</b>：<br>- 时间 O(n²)：外层i从0到n-1，内层j从0到i-1 → Σi = n(n-1)/2 = O(n²)<br>- 空间 O(n)：dp[i]数组长度n，每个元素初始化为1<br><br><b>贪心+二分 (O(n log n))</b>：<br>- 时间 O(n log n)：遍历n个元素，每个在tails数组二分查找插入位置（tails长度≤n，二分O(log n)）→ n×O(log n)<br>- 空间 O(n)：tails数组最坏情况存储n个元素')

add_basic(d, make_front(p, '题解(DP)'),
    '两遍扫描记录左右最高，第三遍累加：min(左最高, 右最高) - 当前高度。<br>'
    + code(
        'class Solution {\n'
        '    public int trap(int[] height) {\n'
        '        int sum = 0;\n'
        '        int len = height.length;\n'
        '        int[] dp_left = new int[len];\n'
        '        int[] dp_right = new int[len];\n'
        '        for (int i = 1; i &lt; len - 1; i++) {\n'
        '            dp_left[i] = Math.max(dp_left[i - 1], height[i - 1]);\n'
        '        }\n'
        '        for (int i = len - 2; i &gt;= 0; i--) {\n'
        '            dp_right[i] = Math.max(dp_right[i + 1], height[i + 1]);\n'
        '        }\n'
        '        for (int i = 1; i &lt; len - 1; i++) {\n'
        '            int min = Math.min(dp_left[i], dp_right[i]);\n'
        '            if (min &gt; height[i]) {\n'
        '                sum = sum + (min - height[i]);\n'
        '            }\n'
        '        }\n'
        '        return sum;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(双指针)'),
    '双指针 left/right，维护 leftMax/rightMax。<br>'
    '每次移动较矮一侧的指针：若 height[left] &lt; height[right]，处理 left 侧并 left++，否则处理 right 侧并 right--。<br>'
    '容量由短板决定，一次遍历 O(n) O(1)。')

# ============================================================
# 9. 编辑距离
# ============================================================
p = '编辑距离'
d = make_deck(1747300109, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定单词 word1 和 word2，返回将 word1 转换成 word2 的最少操作数。三种操作：插入、删除、替换。'
    + img('image 6.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j] = {{c1::word1 前 i 个字符转换成 word2 前 j 个字符的最少操作数}}',
    '双串 DP，dp[M+1][N+1]')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][j] = min(删除{{c1::dp[i-1][j]+1}}, 插入{{c2::dp[i][j-1]+1}}, 替换{{c3::dp[i-1][j-1]+1}})<br>'
    + '若 word1[i-1]==word2[j-1]：dp[i][j] = min(dp[i][j], {{c4::dp[i-1][j-1]}})',
    '相等时无需操作（替换代价为 0）' + img('image 7.png'))

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[i][0] = {{c1::i}}（删除 i 个字符变空串）<br>'
    + 'dp[0][j] = {{c2::j}}（插入 j 个字符从空串变 word2）',
    '空串 vs 非空串的基本操作次数')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 n1，j 从 1 到 n2 正向遍历。<br>dp[i][j] 依赖左、上、左上，正序即可。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n1][n2]（word1 全部转换为 word2 的最少操作数）。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP（预处理左右最大值）</b>：<br>- 时间 O(n)：三次遍历 → 左→右求left_max(O(n)) + 右→左求right_max(O(n)) + 累加雨水(O(n)) = 3n = O(n)<br>- 空间 O(n)：left_max和right_max各为长度n的数组<br><br><b>双指针（最优）</b>：<br>- 时间 O(n)：左右指针各移动n次，每次O(1)取min计算差值 → O(n)<br>- 空间 O(1)：仅需left、right、left_max、right_max四个变量')

add_basic(d, make_front(p, '题解'),
    '三种操作取 min，相等时直接继承对角线（代价 0）。<br>'
    + code(
        'class Solution {\n'
        '    public int minDistance(String word1, String word2) {\n'
        '        int n1 = word1.length() + 1;\n'
        '        int n2 = word2.length() + 1;\n'
        '        int[][] dp = new int[n1][n2];\n'
        '        for (int i = 0; i &lt; n1; i++) {\n'
        '            dp[i][0] = i;\n'
        '        }\n'
        '        for (int j = 0; j &lt; n2; j++) {\n'
        '            dp[0][j] = j;\n'
        '        }\n'
        '        for (int i = 1; i &lt; n1; i++) {\n'
        '            for (int j = 1; j &lt; n2; j++) {\n'
        '                dp[i][j] = Math.min(Math.min(dp[i-1][j] + 1, dp[i][j-1] + 1), dp[i-1][j-1] + 1);\n'
        '                if (word1.charAt(i-1) == word2.charAt(j-1)) {\n'
        '                    dp[i][j] = Math.min(dp[i][j], dp[i-1][j-1]);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return dp[n1-1][n2-1];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 10. 最长公共子序列 (LCS)
# ============================================================
p = '最长公共子序列'
d = make_deck(1747300110, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定两个字符串 text1 和 text2，返回它们的最长公共子序列长度。子序列不要求连续。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j] = {{c1::text1[0..i-1] 和 text2[0..j-1] 的最长公共子序列长度}}',
    'dp[M+1][N+1]，i=0 或 j=0 表示空串，统一处理边界')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>相等：dp[i][j] = {{c1::dp[i-1][j-1] + 1}}<br>'
    + '不等：dp[i][j] = {{c2::max(dp[i-1][j], dp[i][j-1])}}',
    '相等继承+1，不等取两边最大')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][*] = {{c1::0}}, dp[*][0] = {{c2::0}}',
    '空串与任何字符串 LCS = 0，数组默认就是 0')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 M，j 从 1 到 N 正向遍历。<br>依赖左、上、左上，正序即可。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[M][N]（两个完整字符串的 LCS 长度）。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP（预处理左右最大值）</b>：<br>- 时间 O(n)：三次遍历 → 左→右求left_max(O(n)) + 右→左求right_max(O(n)) + 累加雨水(O(n)) = 3n = O(n)<br>- 空间 O(n)：left_max和right_max各为长度n的数组<br><br><b>双指针（最优）</b>：<br>- 时间 O(n)：左右指针各移动n次，每次O(1)取min计算差值 → O(n)<br>- 空间 O(1)：仅需left、right、left_max、right_max四个变量')

add_basic(d, make_front(p, '题解'),
    '相等：dp[i][j] = dp[i-1][j-1] + 1；不等：dp[i][j] = max(dp[i-1][j], dp[i][j-1])。<br>'
    + code(
        'class Solution {\n'
        '    public int longestCommonSubsequence(String text1, String text2) {\n'
        '        int M = text1.length();\n'
        '        int N = text2.length();\n'
        '        int[][] dp = new int[M + 1][N + 1];\n'
        '        for (int i = 1; i &lt;= M; ++i) {\n'
        '            for (int j = 1; j &lt;= N; ++j) {\n'
        '                if (text1.charAt(i - 1) == text2.charAt(j - 1)) {\n'
        '                    dp[i][j] = dp[i - 1][j - 1] + 1;\n'
        '                } else {\n'
        '                    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return dp[M][N];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 11. 爬楼梯
# ============================================================
p = '爬楼梯'
d = make_deck(1747300111, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '需要 n 阶到楼顶，每次爬 1 或 2 阶，共有多少种方法。'
    + img('image 10.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>f(n) = {{c1::爬到第 n 阶的方法数}}',
    '类似斐波那契')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>f(n) = {{c1::f(n-1) + f(n-2)}}',
    '最后一步跨 1 阶或 2 阶')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>f(1) = {{c1::1}}, f(2) = {{c2::2}}',
    '1 阶只有 1 种，2 阶有 1+1 和 2 两种')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '从 3 到 n 正向递推。<br>可以三变量滚动：p, q, r → r=p+q; p=q; q=r → O(1) 空间。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 f(n) 或滚动变量 r。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(m×n)：二维dp表共(m+1)×(n+1)个格子，每格做常数次比较（min of 3 operations） → O(mn)<br>- 空间 O(m×n) → 优化到O(min(m,n))：当前行只依赖上一行和左边，两行滚动即可')

add_basic(d, make_front(p, '题解(DP)'),
    '三变量滚动：p=f(n-2), q=f(n-1), r=p+q。O(n) O(1)。<br>'
    + code(
        'class Solution {\n'
        '    public int climbStairs(int n) {\n'
        '        if (n &lt;= 2) return n;\n'
        '        int[] f = new int[n + 1];\n'
        '        f[1] = 1;\n'
        '        f[2] = 2;\n'
        '        for (int i = 3; i &lt;= n; i++) {\n'
        '            f[i] = f[i - 1] + f[i - 2];\n'
        '        }\n'
        '        return f[n];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 12. 使用最小花费爬楼梯
# ============================================================
p = '使用最小花费爬楼梯'
d = make_deck(1747300112, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定数组 cost，cost[i] 是踏上第 i 阶的花费。可从第 0 或第 1 阶开始，每次爬 1 或 2 阶，返回到达楼顶的最小花费。'
    + img('image 11.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>minCost[i] = {{c1::到达第 i 阶的最小花费}}',
    '注意：站在第 i 阶的费用已包含 cost[i]')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>minCost[i] = min({{c1::minCost[i-1] + cost[i]}}, {{c2::minCost[i-2] + cost[i-1]}})',
    '从 i-1 跨 1 步或从 i-2 跨 2 步')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>minCost[0] = {{c1::0}}（从第 0 阶开始免费）<br>'
    + 'minCost[1] = {{c2::min(cost[0], cost[1])}}',
    '可从第 0 或第 1 阶开始')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 2 到 size-1 正向遍历。minCost[i] 依赖 i-1 和 i-2。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 minCost[size-1]（到达最后一阶的最小花费）。<br>注意"楼顶"在最后一阶之后，但从最后一阶到楼顶不需要额外花费。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(M×N)：二维dp表共(M+1)×(N+1)格，每格O(1)比较两个字符 → O(MN)<br>- 空间 O(M×N) → 优化到O(min(M,N))：每行只依赖上一行和当前行左侧，保留两行')

add_basic(d, make_front(p, '题解'),
    '与爬楼梯相似，从计数变成求最小值。minCost[i] = min(前1+cost[i], 前2+cost[i-1])。<br>'
    + code(
        'class Solution {\n'
        '    public int minCostClimbingStairs(int[] cost) {\n'
        '        int size = cost.length;\n'
        '        int[] minCost = new int[size];\n'
        '        minCost[0] = 0;\n'
        '        minCost[1] = Math.min(cost[0], cost[1]);\n'
        '        for (int i = 2; i &lt; size; i++) {\n'
        '            minCost[i] = Math.min(minCost[i - 1] + cost[i], minCost[i - 2] + cost[i - 1]);\n'
        '        }\n'
        '        return minCost[size - 1];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 13. 圆环回原点问题
# ============================================================
p = '圆环回原点问题'
d = make_deck(1747300113, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '长度为 m 的圆环（0..m-1），从 0 出发走 n 步，每步顺时针或逆时针 1 格，问回到 0 的方案数。'
    + img('image 12.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j] = {{c1::走 i 步到达位置 j 的方案数}}',
    '两维：步数 × 位置')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][j] = dp[i-1][{{c1::(j-1+len)%len}}] + dp[i-1][{{c2::(j+1)%len}}]',
    '从左右邻居走来，取模处理环形')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][0] = {{c1::1}}（走 0 步在 0 位置有 1 种方案）',
    '其他 dp[0][*] = 0')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 n，j 从 0 到 len-1。dp[i][j] 依赖 dp[i-1][*]。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n][0]（走 n 步后回到 0 的方案数）。')

add_basic(d, make_front(p, '复杂度'),
    '<b>迭代DP</b>：dp[i]=dp[i-1]+dp[i-2]，从1到n迭代n次加法 → 时间O(n)，空间O(1)（prev2/prev1/curr三个变量）<br><b>矩阵快速幂</b>：时间O(log n)，空间O(1)<br><b>递归（无记忆化）</b>：时间O(2^n)，空间O(n) — 不推荐')

add_basic(d, make_front(p, '题解'),
    '从左右邻居走来的方案数之和。取模处理环形：(j-1+len)%len 防负索引。<br>'
    + code(
        'class Solution {\n'
        '    public int climbStairs(int n) {\n'
        '        int length = 10;\n'
        '        int[][] dp = new int[n + 1][length];\n'
        '        dp[0][0] = 1;\n'
        '        for (int i = 1; i &lt; dp.length; i++)\n'
        '            for (int j = 0; j &lt; dp[0].length; j++) {\n'
        '                dp[i][j] = dp[i - 1][(j - 1 + length) % length]\n'
        '                         + dp[i - 1][(j + 1) % length];\n'
        '            }\n'
        '        return dp[n][0];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 14. 零钱兑换
# ============================================================
p = '零钱兑换'
d = make_deck(1747300114, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给你整数数组 coins 和总金额 amount，返回凑成总金额的最少硬币个数。无法凑成返回 -1。硬币无限使用。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::凑金额 i 的最少硬币数}}',
    '完全背包求最小值')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[j] = {{c1::min(dp[j], dp[j-coin] + 1)}}',
    '正序遍历（完全背包允许重复使用）')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::0}}<br>其余 dp[i] = {{c2::amount+1}}（表示无法凑成）',
    '凑 0 元需要 0 个硬币')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '外层硬币，内层金额正序遍历。完全背包正序允许同一硬币多次使用。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '若 dp[amount] == amount+1 返回 -1，否则返回 dp[amount]。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：遍历n阶，每阶dp[i]=cost[i]+min(dp[i-1],dp[i-2])一次加法和一次min → n×O(1)=O(n)<br>- 空间 O(1)：只依赖前两个状态，prev1和prev2两个变量滚动')

add_basic(d, make_front(p, '题解'),
    '完全背包求最小值：dp[j] = min(dp[j], dp[j-coin]+1)，INF 用 amount+1。<br>'
    + code(
        'class Solution {\n'
        '    public int coinChange(int[] coins, int amount) {\n'
        '        int len = coins.length;\n'
        '        int[] dp = new int[amount + 1];\n'
        '        Arrays.fill(dp, amount + 1);\n'
        '        dp[0] = 0;\n'
        '        for (int i = 0; i &lt; len; i++) {\n'
        '            for (int j = coins[i]; j &lt;= amount; j++) {\n'
        '                dp[j] = Math.min(dp[j], dp[j - coins[i]] + 1);\n'
        '            }\n'
        '        }\n'
        '        if (dp[amount] == amount + 1) {\n'
        '            dp[amount] = -1;\n'
        '        }\n'
        '        return dp[amount];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 15. 零钱兑换 II
# ============================================================
p = '零钱兑换 II'
d = make_deck(1747300115, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给你整数数组 coins 和总金额 amount，返回凑成总金额的组合数。硬币无限使用，顺序不同算同一种组合。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::凑金额 i 的组合数}}',
    '完全背包求组合数')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[j] = {{c1::dp[j] + dp[j-coin]}}',
    '从求最小值变成求方案数累加')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::1}}',
    '凑 0 元有一种方案：什么都不选')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '外层硬币，内层金额正序遍历。<b>外层硬币内层金额</b>保证组合数（非排列数），避免 [1,2] 和 [2,1] 重复计数。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[amount]。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：遍历n阶，每阶dp[i]=cost[i]+min(dp[i-1],dp[i-2])一次加法和一次min → n×O(1)=O(n)<br>- 空间 O(1)：只依赖前两个状态，prev1和prev2两个变量滚动')

add_basic(d, make_front(p, '题解'),
    '组合数：dp[j] = dp[j] + dp[j-coin]。dp[0]=1 是关键。外层硬币内层金额保证组合非排列。<br>'
    + code(
        'class Solution {\n'
        '    public int change(int amount, int[] coins) {\n'
        '        int len = coins.length;\n'
        '        if (len == 0) {\n'
        '            if (amount == 0) return 1;\n'
        '            return 0;\n'
        '        }\n'
        '        int[] dp = new int[amount + 1];\n'
        '        dp[0] = 1;\n'
        '        for (int i = coins[0]; i &lt;= amount; i += coins[0])\n'
        '            dp[i] = 1;\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            for (int j = 0; j &lt;= amount; j++) {\n'
        '                if (j - coins[i] &gt;= 0)\n'
        '                    dp[j] = dp[j] + dp[j - coins[i]];\n'
        '            }\n'
        '        }\n'
        '        return dp[amount];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 16. 最大正方形
# ============================================================
p = '最大正方形'
d = make_deck(1747300116, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定 0/1 二维矩阵，返回只包含 1 的最大正方形面积。'
    + img('image 14.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i+1][j+1] = {{c1::以 matrix[i][j] 为右下角的最大正方形边长}}',
    'dp 比 matrix 多一行一列，方便处理边界' + img('image 15.png'))

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>若 matrix[i][j]==\'1\'：dp[i+1][j+1] = min({{c1::dp[i][j+1]}}, {{c2::dp[i+1][j]}}, {{c3::dp[i][j]}}) + 1',
    '取左、上、左上最小值+1，边长受限于最短边')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp 数组全部初始化为 {{c1::0}}（多出的一行一列自然为 0）',
    'matrix[0][0] 也能统一处理')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 0 到 high-1，j 从 0 到 wide-1 双重循环。<br>一维优化：dp[wide+1] + northwest 变量保存左上旧值，倒序遍历 j。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 maxSide * maxSide（最大边长的平方 = 面积）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n×len)：dp[i][j]表示走i步位于位置j的方案数，i从1到n，j从0到len-1 → n×len个状态，每状态O(1)转移 → O(n×len)<br>- 空间 O(len)：第i步只依赖第i-1步，用两个长度为len的数组交替 → O(len)')

add_basic(d, make_front(p, '题解(DP)'),
    '取左、上、左上最小值+1。因正方形边长受限于最短板。<br>'
    + code(
        'class Solution {\n'
        '    public int maximalSquare(char[][] matrix) {\n'
        '        if (matrix == null || matrix.length == 0 || matrix[0].length == 0)\n'
        '            return 0;\n'
        '        int maxSpace = 0;\n'
        '        int high = matrix.length;\n'
        '        int wide = matrix[0].length;\n'
        '        int[][] dp = new int[high + 1][wide + 1];\n'
        '        for (int i = 0; i &lt; high; i++) {\n'
        '            for (int j = 0; j &lt; wide; j++) {\n'
        '                if (matrix[i][j] == \'1\') {\n'
        '                    dp[i+1][j+1] = Math.min(\n'
        '                        Math.min(dp[i+1][j], dp[i][j+1]),\n'
        '                        dp[i][j]) + 1;\n'
        '                    maxSpace = Math.max(maxSpace, dp[i+1][j+1]);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return maxSpace * maxSpace;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(降维优化)'),
    '一维 dp[wide+1] + northwest 保存左上旧值。每列遍历时 dp[col+1] 表示上一行的值。<br>'
    + code(
        'class Solution {\n'
        '    public int maximalSquare(char[][] matrix) {\n'
        '        if (matrix == null || matrix.length &lt; 1 || matrix[0].length &lt; 1)\n'
        '            return 0;\n'
        '        int height = matrix.length;\n'
        '        int width = matrix[0].length;\n'
        '        int maxSide = 0;\n'
        '        int[] dp = new int[width + 1];\n'
        '        int northwest = 0;\n'
        '        for (char[] chars : matrix) {\n'
        '            northwest = 0;\n'
        '            for (int col = 0; col &lt; width; col++) {\n'
        '                int nextNorthwest = dp[col + 1];\n'
        '                if (chars[col] == \'1\') {\n'
        '                    dp[col + 1] = Math.min(Math.min(dp[col], dp[col + 1]), northwest) + 1;\n'
        '                    maxSide = Math.max(maxSide, dp[col + 1]);\n'
        '                } else {\n'
        '                    dp[col + 1] = 0;\n'
        '                }\n'
        '                northwest = nextNorthwest;\n'
        '            }\n'
        '        }\n'
        '        return maxSide * maxSide;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 17. 不同路径
# ============================================================
p = '不同路径'
d = make_deck(1747300117, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '机器人位于 m×n 网格左上角，每次只能向下或向右移动一步，问到达右下角有多少条不同路径。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j] = {{c1::到达 (i,j) 位置的路径数}}',
    '从左上角到 (i,j)')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][j] = {{c1::dp[i-1][j] + dp[i][j-1]}}',
    '从上来 + 从左来 = 杨辉三角形')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[i][0] = {{c1::1}}, dp[0][j] = {{c2::1}}',
    '第一行和第一列只有一条路径（一直向右/下）')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 m-1，j 从 1 到 n-1。<br>一维优化：cur[j] = cur[j] + cur[j-1]（cur[j] 是上一行值）。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[m-1][n-1]（右下角的路径数）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n×amount)：完全背包问题。外层遍历n种硬币，内层遍历金额1~amount（正序） → n×amount次状态转移<br>- 空间 O(amount)：一维dp数组长度amount+1，dp[j]=min(dp[j], dp[j-coin]+1)')

add_basic(d, make_front(p, '题解(DP)'),
    'dp[i][j] = dp[i-1][j] + dp[i][j-1]。一维优化：cur[j] += cur[j-1]。<br>'
    + code(
        'class Solution {\n'
        '    public int uniquePaths(int m, int n) {\n'
        '        int[][] dp = new int[m][n];\n'
        '        for (int i = 0; i &lt; m; i++)\n'
        '            dp[i][0] = 1;\n'
        '        for (int i = 0; i &lt; n; i++)\n'
        '            dp[0][i] = 1;\n'
        '        for (int i = 1; i &lt; m; i++) {\n'
        '            for (int j = 1; j &lt; n; j++) {\n'
        '                dp[i][j] = dp[i][j - 1] + dp[i - 1][j];\n'
        '            }\n'
        '        }\n'
        '        return dp[m - 1][n - 1];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(组合数学)'),
    'C(m+n-2, m-1) = (m+n-2)! / ((m-1)! * (n-1)!)<br>'
    '总共走 m+n-2 步，选其中 m-1 步向下。用 long 累乘再累除防溢出。')

# ============================================================
# 18. 乘积最大子数组
# ============================================================
p = '乘积最大子数组'
d = make_deck(1747300118, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数数组 nums，找出乘积最大的连续子数组，返回乘积。'
    + img('image 19.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>imax = {{c1::以当前元素结尾的最大乘积}}<br>'
    + 'imin = {{c2::以当前元素结尾的最小乘积}}',
    '必须同时维护最大和最小，因为负数相乘会翻转')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>if(nums[i]&lt;0) swap({{c1::imax, imin}})<br>'
    + 'imax = max(imax*nums[i], {{c2::nums[i]}})<br>'
    + 'imin = min(imin*nums[i], {{c3::nums[i]}})',
    '负负得正：最小值×负数可能变最大值')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>imax = {{c1::1}}, imin = {{c2::1}}, max = {{c3::Integer.MIN_VALUE}}',
    'imax/imin 从 1 开始，遇到负数交换后乘第一个元素')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '一次遍历，每遇到元素先判断正负（负则交换 imax/imin），再更新 imax/imin 和全局 max。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 max（全局最大乘积，不是最后一个 imax）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n×amount)：完全背包求方案数。外层n种硬币，内层amount个金额（正序） → O(n×amount)<br>- 空间 O(amount)：一维dp数组长度amount+1，dp[j]+=dp[j-coin]')

add_basic(d, make_front(p, '题解'),
    '同时维护 imax 和 imin。遇负数先交换再乘，因最小值×负数可能变最大值。<br>'
    + code(
        'class Solution {\n'
        '    public int maxProduct(int[] nums) {\n'
        '        int max = Integer.MIN_VALUE, imax = 1, imin = 1;\n'
        '        for (int i = 0; i &lt; nums.length; i++) {\n'
        '            if (nums[i] &lt; 0) {\n'
        '                int tmp = imax;\n'
        '                imax = imin;\n'
        '                imin = tmp;\n'
        '            }\n'
        '            imax = Math.max(imax * nums[i], nums[i]);\n'
        '            imin = Math.min(imin * nums[i], nums[i]);\n'
        '            max = Math.max(max, imax);\n'
        '        }\n'
        '        return max;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 19. 打家劫舍
# ============================================================
p = '打家劫舍'
d = make_deck(1747300119, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定数组 nums 表示房屋金额，相邻房屋不能同晚被偷，返回最大金额。'
    + img('image 20.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::偷前 i 间房子的最大金额}}',
    '子问题：从 k 个房子中能偷到的最大金额' + img('image 22.png'))

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i] = max({{c1::dp[i-1]}}, {{c2::nums[i-1] + dp[i-2]}})',
    '不偷第 i 间 → dp[i-1]；偷第 i 间 → nums[i-1] + dp[i-2]')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::0}}, dp[1] = {{c2::nums[0]}}',
    'dp[0] 是空房子 = 0，dp[1] 是第一间')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 2 到 n 正向遍历。dp[i] 依赖 dp[i-1] 和 dp[i-2]。<br>滚动变量优化：prev, curr → temp = max(curr, prev+i); prev=curr; curr=temp。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n]（偷前 n 间房子的最大金额）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(M×N)：双重循环遍历矩阵所有格子，每格取min(左,上,左上)+1 → O(MN)<br>- 空间 O(N)：dp[i][j]只依赖左边、上边、左上角三个位置 → 保留一行dp数组+一个prev对角变量 → O(N)')

add_basic(d, make_front(p, '题解'),
    '"偷或不偷"经典二分决策：dp[i] = max(dp[i-1], nums[i-1] + dp[i-2])。<br>'
    + code(
        'class Solution {\n'
        '    public int rob(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return 0;\n'
        '        int[] dp = new int[nums.length + 1];\n'
        '        dp[0] = 0;\n'
        '        dp[1] = nums[0];\n'
        '        for (int i = 2; i &lt;= nums.length; i++) {\n'
        '            dp[i] = Math.max(dp[i - 1], nums[i - 1] + dp[i - 2]);\n'
        '        }\n'
        '        return dp[nums.length];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 20. 打家劫舍 II
# ============================================================
p = '打家劫舍 II'
d = make_deck(1747300120, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '房屋首尾相连成环，相邻房屋不能同晚被偷，返回最大金额。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>与 I 完全相同，dp[i] = {{c1::偷前 i 间房子的最大金额}}',
    '关键是处理好环形约束')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i] = max(dp[i-1], {{c1::nums[i-1] + dp[i-2]}})',
    '转移方程与 I 完全一样')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = 0, dp[1] = {{c1::nums[0]}}（同 I）',
    '两次调用 dp 方法，传入不同数组范围')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '分两种情况各跑一次打家劫舍 I：<br>1. 不偷第一家：nums[1..end]<br>2. 不偷最后一家：nums[0..end-1]<br>取 max。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 max(dp(nums[0..n-2]), dp(nums[1..n-1]))。<br>特殊情况：n==1 直接返回 nums[0]。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n×amount)：完全背包求方案数。外层n种硬币，内层amount个金额（正序） → O(n×amount)<br>- 空间 O(amount)：一维dp数组长度amount+1，dp[j]+=dp[j-coin]')

add_basic(d, make_front(p, '题解'),
    '环形 DP 通用套路：拆为两个线性 DP，去头或去尾各跑一次取 max。<br>'
    + code(
        'class Solution {\n'
        '    public int rob(int[] nums) {\n'
        '        if (nums == null || nums.length == 0)\n'
        '            return 0;\n'
        '        if (nums.length == 1)\n'
        '            return nums[0];\n'
        '        return Math.max(dp(Arrays.copyOfRange(nums, 0, nums.length - 1)),\n'
        '                        dp(Arrays.copyOfRange(nums, 1, nums.length)));\n'
        '    }\n'
        '\n'
        '    public int dp(int[] nums) {\n'
        '        int[] dp = new int[nums.length + 1];\n'
        '        dp[0] = 0;\n'
        '        dp[1] = nums[0];\n'
        '        for (int i = 2; i &lt;= nums.length; i++) {\n'
        '            dp[i] = Math.max(dp[i - 1], nums[i - 1] + dp[i - 2]);\n'
        '        }\n'
        '        return dp[nums.length];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 21. 最长重复子数组
# ============================================================
p = '最长重复子数组'
d = make_deck(1747300121, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定两个整数数组 nums1 和 nums2，返回它们的最长公共连续子数组的长度。'
    + img('image 24.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j] = {{c1::以 nums1[i-1] 和 nums2[j-1] 结尾的最长公共子数组长度}}',
    '注意：要求连续！与 LCS 不同')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>相等：dp[i][j] = {{c1::dp[i-1][j-1] + 1}}<br>'
    + '不等：dp[i][j] = {{c2::0}}',
    '不等必须归零！这是与 LCS 的关键区别')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[*][*] = {{c1::0}}',
    '全部初始化为 0，空数组无公共部分')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len1，j 从 1 到 len2。<br>一维优化需倒序遍历 j，不等时手动 dp[j]=0 覆盖旧值。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 maxLen（遍历过程中持续更新的全局最大值）。<br>不是 dp[len1][len2]，因为最长子数组不一定在末尾。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n×len)：dp[i][j]表示走i步位于位置j的方案数，i从1到n，j从0到len-1 → n×len个状态，每状态O(1)转移 → O(n×len)<br>- 空间 O(len)：第i步只依赖第i-1步，用两个长度为len的数组交替 → O(len)')

add_basic(d, make_front(p, '题解(二维DP)'),
    '相等 dp[i][j] = dp[i-1][j-1] + 1；不等必须清零！与 LCS 的关键区别。<br>'
    + code(
        'class Solution {\n'
        '    public int findLength(int[] nums1, int[] nums2) {\n'
        '        int[][] dp = new int[nums1.length + 1][nums2.length + 1];\n'
        '        int maxLen = 0;\n'
        '        for (int i = 1; i &lt; dp.length; i++) {\n'
        '            for (int j = 1; j &lt; dp[0].length; j++) {\n'
        '                if (nums1[i - 1] == nums2[j - 1])\n'
        '                    dp[i][j] = dp[i - 1][j - 1] + 1;\n'
        '                maxLen = Math.max(dp[i][j], maxLen);\n'
        '            }\n'
        '        }\n'
        '        return maxLen;\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(一维优化)'),
    '倒序遍历 j 防止覆盖，不等时手动清零 dp[j]=0。<br>'
    + code(
        'class Solution {\n'
        '    public int findLength(int[] nums1, int[] nums2) {\n'
        '        int[] dp = new int[nums2.length + 1];\n'
        '        int maxLen = 0;\n'
        '        for (int i = 1; i &lt;= nums1.length; i++) {\n'
        '            for (int j = nums2.length; j &gt;= 1; j--) {\n'
        '                if (nums1[i - 1] == nums2[j - 1])\n'
        '                    dp[j] = dp[j - 1] + 1;\n'
        '                else\n'
        '                    dp[j] = 0;\n'
        '                maxLen = Math.max(dp[j], maxLen);\n'
        '            }\n'
        '        }\n'
        '        return maxLen;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 22. 单词拆分
# ============================================================
p = '单词拆分'
d = make_deck(1747300122, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定字符串 s 和单词字典 wordDict，判断 s 是否能拆分为字典中的单词（可重复使用）。'
    + img('image 25.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::s 的前 i 个字符能否被拆分为字典中的单词}}',
    'dp[0] = true 表示空前缀可拆分')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>若 dp[j] && wordDict.contains({{c1::s.substring(j,i)}})，则 dp[i] = {{c2::true}}',
    '切分点 j：前 j 个可拆分 + [j,i) 在字典中')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::true}}',
    '空前缀视为可拆分，便于统一处理')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len，内层 j 从 i-1 到 0 逆序。<br>找到第一个匹配后 break，因为只需要知道是否可拆分。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[len]（整个字符串是否可拆分）。')

add_basic(d, make_front(p, '复杂度'),
    '<b>DP</b>：dp[i][j]=dp[i-1][j]+dp[i][j-1]，双重循环遍历网格 → 时间O(m×n)，空间可优化到O(n)（一行正序更新）<br><b>组合数学</b>：C(m+n-2, m-1) → 时间O(min(m,n))，空间O(1)')

add_basic(d, make_front(p, '题解(DP)'),
    'dp[i] = dp[j] && wordDict.contains(s.substring(j,i))。找到匹配就 break。<br>'
    + code(
        'class Solution {\n'
        '    public boolean wordBreak(String s, List&lt;String&gt; wordDict) {\n'
        '        int len = s.length();\n'
        '        boolean[] dp = new boolean[len + 1];\n'
        '        dp[0] = true;\n'
        '        for (int i = 1; i &lt;= len; i++) {\n'
        '            for (int j = i - 1; j &gt;= 0; j--) {\n'
        '                String temp = s.substring(j, i);\n'
        '                if (wordDict.contains(temp) && dp[j]) {\n'
        '                    dp[i] = true;\n'
        '                    break;\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return dp[len];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(BFS)'),
    'Queue 存起始下标，从 0 开始 BFS。每次 poll 后枚举 end，匹配到单词则入队。visited 数组剪枝防重复。<br>'
    + code(
        'class Solution {\n'
        '    public boolean wordBreak(String s, List&lt;String&gt; wordDict) {\n'
        '        Queue&lt;Integer&gt; queue = new ArrayDeque&lt;&gt;();\n'
        '        boolean[] visit = new boolean[s.length()];\n'
        '        int start = 0;\n'
        '        queue.offer(start);\n'
        '        while (queue.isEmpty() == false) {\n'
        '            int cur = queue.poll();\n'
        '            if (cur == s.length())\n'
        '                return true;\n'
        '            if (visit[cur] == true)\n'
        '                continue;\n'
        '            visit[cur] = true;\n'
        '            for (int i = cur; i &lt;= s.length(); i++) {\n'
        '                String curStr = s.substring(cur, i);\n'
        '                if (wordDict.contains(curStr)) {\n'
        '                    queue.offer(i);\n'
        '                }\n'
        '            }\n'
        '        }\n'
        '        return false;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 23. 解码方法
# ============================================================
p = '解码方法'
d = make_deck(1747300123, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '数字字符串 s 按映射 A->1 ... Z->26 解码。0 不能单独解码，06 不合法。返回解码方法总数。'
    + img('image 31.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::前 i 个字符的解码方法数}}',
    'dp[0]=1 表示空串有 1 种解码方式')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>若 s[i]==0：前位是 1/2 则 dp[i]={{c1::dp[i-2]}}，否则 {{c2::return 0}}<br>'
    + '若 s[i]!=0 且两位数合法(10~26)：dp[i]={{c3::dp[i-1]+dp[i-2]}}<br>'
    + '否则 dp[i]={{c4::dp[i-1]}}',
    '0 必须绑定前面，类似爬楼梯的升级版')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::1}}, dp[1] = {{c2::s[0]==\'0\' ? 0 : 1}}',
    '首字符为 0 直接返回 0')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 length-1 正向遍历。<br>分 s[i]==0 和 s[i]!=0 两类讨论。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[length]（整个字符串的解码方法数）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(M×N)：二维dp表共(M+1)×(N+1)格，每格O(1)比较两个字符 → O(MN)<br>- 空间 O(M×N) → 优化到O(min(M,N))：每行只依赖上一行和当前行左侧，保留两行')

add_basic(d, make_front(p, '题解'),
    '0 必须绑定前面 1 或 2。两位数 10~26 合法则 dp[i]=dp[i-1]+dp[i-2]，否则 dp[i]=dp[i-1]。<br>'
    + code(
        'class Solution {\n'
        '    public int numDecodings(String s) {\n'
        '        int length = s.length();\n'
        '        if (length == 0 || s.charAt(0) == \'0\')\n'
        '            return 0;\n'
        '        int[] dp = new int[length + 1];\n'
        '        dp[0] = 1;\n'
        '        dp[1] = 1;\n'
        '        for (int i = 1; i &lt; length; i++) {\n'
        '            if (s.charAt(i) == \'0\') {\n'
        '                if (s.charAt(i - 1) == \'1\' || s.charAt(i - 1) == \'2\')\n'
        '                    dp[i] = dp[i - 2];\n'
        '                else\n'
        '                    return 0;\n'
        '            } else {\n'
        '                if (s.charAt(i - 1) == \'1\' || (s.charAt(i - 1) == \'2\' && s.charAt(i) &lt;= \'6\'))\n'
        '                    dp[i] = dp[i - 1] + dp[i - 2];\n'
        '                else\n'
        '                    dp[i] = dp[i - 1];\n'
        '            }\n'
        '        }\n'
        '        return dp[length];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 24. 三角形最小路径和
# ============================================================
p = '三角形最小路径和'
d = make_deck(1747300124, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定三角形数组 triangle，从顶部到底部每一步只能走到下一行相邻位置，返回最小路径和。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[j] = {{c1::从底部到当前行第 j 列的最小路径和}}',
    '自底向上：dp 初始化为最后一行的副本 + 1 位')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[j] = min({{c1::dp[j]}}, {{c2::dp[j+1]}}) + triangle[i][j]',
    '从下一行的相邻两个位置（左下、右下）取最小 + 当前值')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp 初始化为最后一行的值（+1 位防止越界）',
    '从最底层开始向上递推')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '自底向上：i 从 n-1 到 0，j 从 0 到 i 正向遍历。<br>好处：不需要处理三角形边缘的边界条件。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[0]（从底部到顶部的唯一位置）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：遍历一次，同时维护以i结尾的最大乘积imax和最小乘积imin（因为负数×负数可能反转变为最大），3次比较/乘法 → O(n)<br>- 空间 O(1)：imax、imin、max三个变量。关键技巧：遇到nums[i]&lt;0时交换imax和imin')

add_basic(d, make_front(p, '题解'),
    '自底向上：dp[j] = min(dp[j], dp[j+1]) + triangle[i][j]。无需处理三角形边缘边界。<br>'
    + code(
        'class Solution {\n'
        '    public int minimumTotal(List&lt;List&lt;Integer&gt;&gt; triangle) {\n'
        '        int n = triangle.size();\n'
        '        int[] dp = new int[n + 1];\n'
        '        for (int i = n - 1; i &gt;= 0; i--) {\n'
        '            for (int j = 0; j &lt;= i; j++) {\n'
        '                dp[j] = Math.min(dp[j], dp[j + 1]) + triangle.get(i).get(j);\n'
        '            }\n'
        '        }\n'
        '        return dp[0];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 25. 丑数 II
# ============================================================
p = '丑数 II'
d = make_deck(1747300125, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '丑数是只包含质因子 2、3、5 的正整数。给定整数 n，返回第 n 个丑数。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::第 i 个丑数}}<br>'
    + '三个指针 p2, p3, p5 = {{c2::各自指向待乘的丑数下标}}',
    '三指针分别追踪乘 2/3/5 的基数')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i] = min({{c1::2*dp[p2]}}, {{c2::3*dp[p3]}}, {{c3::5*dp[p5]}})',
    '取三个候选的最小值作为下一个丑数')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[1] = {{c1::1}}（第一个丑数是 1）<br>'
    + 'p2 = p3 = p5 = {{c2::1}}',
    '三个指针从 1 开始')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 2 到 n。计算 num2/num3/num5，取 min 为 dp[i]。<br>关键：所有 dp[i] 相等的指针都要移动（去重，如 6=2*3=3*2）。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n]（第 n 个丑数）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：遍历n间房子，每间计算dp[i]=max(dp[i-1], dp[i-2]+nums[i])，一次比较+一次加法 → O(n)<br>- 空间 O(1)：状态方程只依赖前两个，prev2（dp[i-2]）和prev1（dp[i-1]）两个滚动变量')

add_basic(d, make_front(p, '题解'),
    '三指针分别乘 2/3/5，取最小值。去重关键：用 if 而非 else-if，相等指针都移动。<br>'
    + code(
        'class Solution {\n'
        '    public int nthUglyNumber(int n) {\n'
        '        int[] dp = new int[n + 1];\n'
        '        dp[1] = 1;\n'
        '        int ptr2 = 1, ptr3 = 1, ptr5 = 1;\n'
        '        for (int i = 2; i &lt;= n; i++) {\n'
        '            int num2 = 2 * dp[ptr2], num3 = 3 * dp[ptr3], num5 = 5 * dp[ptr5];\n'
        '            dp[i] = Math.min(Math.min(num2, num3), num5);\n'
        '            if (dp[i] == num2) ptr2++;\n'
        '            if (dp[i] == num3) ptr3++;\n'
        '            if (dp[i] == num5) ptr5++;\n'
        '        }\n'
        '        return dp[n];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 26. 交错字符串
# ============================================================
p = '交错字符串'
d = make_deck(1747300126, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定 s1、s2、s3，判断 s3 是否由 s1 与 s2 交错组成（保持各自字符相对顺序）。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j] = {{c1::s1 前 i 个 + s2 前 j 个 能否交错组成 s3 前 i+j 个}}',
    '双串 DP，布尔型')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][j] = (dp[i-1][j] && s1[i-1]==s3[i+j-1])<br>'
    + '&nbsp;&nbsp;&nbsp;&nbsp;{{c1::||}} (dp[i][j-1] && s2[j-1]==s3[i+j-1])',
    '当前字符要么来自 s1 要么来自 s2')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][0] = {{c1::true}}<br>'
    + '第一行/列：连续匹配 s1/s2 与 s3 的前缀',
    '处理单个字符串的匹配前缀')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 n，j 从 1 到 m。依赖左和上。前提：s1.len + s2.len == s3.len。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n][m]。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：分两段分别DP：[0,n-2]和[1,n-1]各一次 → 2n = O(n)<br>- 空间 O(1)：每段只用两个滚动变量<br>核心思路：环形问题不能同时偷首尾 → 去掉头或尾 → 两次线性DP取max')

add_basic(d, make_front(p, '题解'),
    'dp[i][j] = (dp[i-1][j] && s1[i-1]==s3[i+j-1]) || (dp[i][j-1] && s2[j-1]==s3[i+j-1])。<br>'
    + code(
        'class Solution {\n'
        '    public boolean isInterleave(String s1, String s2, String s3) {\n'
        '        if (s1.length() + s2.length() != s3.length())\n'
        '            return false;\n'
        '        int n = s1.length(), m = s2.length();\n'
        '        boolean[][] dp = new boolean[n + 1][m + 1];\n'
        '        dp[0][0] = true;\n'
        '        for (int i = 1; i &lt;= n && s1.charAt(i - 1) == s3.charAt(i - 1); i++)\n'
        '            dp[i][0] = true;\n'
        '        for (int j = 1; j &lt;= m && s2.charAt(j - 1) == s3.charAt(j - 1); j++)\n'
        '            dp[0][j] = true;\n'
        '        for (int i = 1; i &lt;= n; i++) {\n'
        '            for (int j = 1; j &lt;= m; j++) {\n'
        '                dp[i][j] = (dp[i - 1][j] && s1.charAt(i - 1) == s3.charAt(i + j - 1))\n'
        '                        || (dp[i][j - 1] && s2.charAt(j - 1) == s3.charAt(i + j - 1));\n'
        '            }\n'
        '        }\n'
        '        return dp[n][m];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 27. 最长递增子序列的个数
# ============================================================
p = '最长递增子序列的个数'
d = make_deck(1747300127, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数数组 nums，返回最长严格递增子序列的个数。'
    + img('image 32.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::以 nums[i] 结尾的 LIS 长度}}<br>'
    + 'count[i] = {{c2::以 nums[i] 结尾的 LIS 的方案数}}',
    '需要同时维护长度和方案数两个数组')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>若 dp[j]+1 &gt; dp[i]：count[i] = {{c1::count[j]}}（重置）<br>'
    + '若 dp[j]+1 == dp[i]：count[i] = {{c2::count[i] + count[j]}}（累加）',
    '更长则重置，等长则累加')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[i] = {{c1::1}}, count[i] = {{c2::1}}',
    '每个元素自身构成 LIS 长度 1 的方案数 1')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 0 到 n-1，j 从 0 到 i-1。<br>最后遍历 dp 找到全局最长长度 maxLen，累加所有 dp[i]==maxLen 位置的 count[i]。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 sum(count[i]) for all i where dp[i] == maxLen。<br>不是返回某个 count[n-1]，因为 LIS 可能以多个位置结尾。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(m×n)：双重循环，dp[i][j]表示以nums1[i-1]和nums2[j-1]结尾的最长公共子数组 → m×n个状态O(1)比较 → O(mn)<br>- 空间 O(min(m,n))：dp[i][j]只依赖dp[i-1][j-1]（左上角），可倒序更新一维数组 → O(min(m,n))')

add_basic(d, make_front(p, '题解'),
    '同时维护 dp[i]（长度）和 count[i]（方案数）。更长重置，等长累加。最后累加所有 dp[i]==maxLen 的 count[i]。<br>'
    + code(
        'class Solution {\n'
        '    public int findNumberOfLIS(int[] nums) {\n'
        '        int n = nums.length;\n'
        '        int[] dp = new int[n];\n'
        '        int[] count = new int[n];\n'
        '        Arrays.fill(dp, 1);\n'
        '        Arrays.fill(count, 1);\n'
        '        int maxLen = 0;\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            for (int j = 0; j &lt; i; j++) {\n'
        '                if (nums[j] &lt; nums[i]) {\n'
        '                    if (dp[j] + 1 &gt; dp[i]) {\n'
        '                        dp[i] = dp[j] + 1;\n'
        '                        count[i] = count[j];\n'
        '                    } else if (dp[j] + 1 == dp[i]) {\n'
        '                        count[i] += count[j];\n'
        '                    }\n'
        '                }\n'
        '            }\n'
        '            maxLen = Math.max(maxLen, dp[i]);\n'
        '        }\n'
        '        int res = 0;\n'
        '        for (int i = 0; i &lt; n; i++) {\n'
        '            if (dp[i] == maxLen) res += count[i];\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 28. 分割等和子集
# ============================================================
p = '分割等和子集'
d = make_deck(1747300128, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给你只包含正整数的非空数组 nums，判断是否可以分割成两个子集，使元素和相等。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[j] = {{c1::能否从数组中选出一些数，和为 j}}',
    '0-1 背包可行性变种，容量 = sum/2')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[j] = {{c1::dp[j] | dp[j - nums[i]]}}',
    '或运算：不选当前数(保持) 或 选当前数(从 j-nums[i] 转移)')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::true}}',
    '不选任何数，和为 0 总是可行的')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '外层 nums[i]，内层 target → nums[i] 倒序遍历。<br>倒序防止同一个元素被重复使用（0-1 背包）。若 sum%2 != 0 直接返回 false。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[target]（target = sum/2）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n²)：外层i从1到n，内层j从0到i-1 → Σi = n(n+1)/2 = O(n²)次子串检查<br>- 空间 O(n)：dp数组长度n+1 + wordDict的HashSet空间<br>注：substring和set.contains假设为O(1)，因为单词长度通常有上限')

add_basic(d, make_front(p, '题解'),
    '0-1 背包变种：dp[j] |= dp[j-num]，倒序遍历防重复。<br>'
    + code(
        'class Solution {\n'
        '    public boolean canPartition(int[] nums) {\n'
        '        int len = nums.length;\n'
        '        int sum = 0;\n'
        '        for (int num : nums) sum += num;\n'
        '        if (sum % 2 != 0) return false;\n'
        '        int target = sum / 2;\n'
        '        boolean[] dp = new boolean[target + 1];\n'
        '        dp[0] = true;\n'
        '        if (nums[0] &lt;= target) dp[nums[0]] = true;\n'
        '        for (int i = 1; i &lt; len; i++) {\n'
        '            for (int j = target; j &gt;= nums[i]; j--) {\n'
        '                if (dp[target]) return true;\n'
        '                dp[j] = dp[j] | dp[j - nums[i]];\n'
        '            }\n'
        '        }\n'
        '        return dp[target];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 29. 完全平方数
# ============================================================
p = '完全平方数'
d = make_deck(1747300129, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数 n，返回和为 n 的完全平方数的最少数量（完全平方数指 1,4,9,16,...）。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::和为 i 的最少完全平方数个数}}',
    '完全背包求最小值')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i] = {{c1::min(dp[i], dp[i - j*j] + 1)}}, j*j &lt;= i',
    '每个完全平方数 j*j 视为一种硬币，完全背包正序')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::0}}<br>dp[i] 初始化为 {{c2::i}}（最坏情况全用 1）',
    '和为 0 需要 0 个数')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 n 正序遍历。内层枚举 j 满足 j*j <= i。完全背包正序。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n]。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：遍历字符串一次，每步检查1位编码（charAt(i)≠0）和2位编码（10~26） → 两次判断 → O(n)<br>- 空间 O(1)：dp[i]只依赖dp[i-1]和dp[i-2]，两个滚动变量。递推本质同爬楼梯：满足条件时dp[i]=dp[i-1]+dp[i-2]')

add_basic(d, make_front(p, '题解'),
    '完全背包：dp[i] = min(dp[i], dp[i - j*j] + 1)。最坏情况全用 1（dp[i]=i）。<br>'
    + code(
        'class Solution {\n'
        '    public int numSquares(int n) {\n'
        '        int[] dp = new int[n + 1];\n'
        '        for (int i = 1; i &lt;= n; i++) {\n'
        '            dp[i] = i;\n'
        '            for (int j = 1; i - j * j &gt;= 0; j++) {\n'
        '                dp[i] = Math.min(dp[i], dp[i - j * j] + 1);\n'
        '            }\n'
        '        }\n'
        '        return dp[n];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 30. 整数拆分
# ============================================================
p = '整数拆分'
d = make_deck(1747300130, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定正整数 n，将其拆分为至少两个正整数之和，使乘积最大，返回最大乘积。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::正整数 i 拆分后的最大乘积}}',
    '至少拆成两个数')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i] = max(dp[i], max({{c1::j * (i-j)}}, {{c2::j * dp[i-j]}}))',
    '拆成两个数(j × i-j) 或 继续拆(i-j)取 dp[i-j]')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[2] = {{c1::1}}（2=1+1→1×1=1）',
    'dp[0] 和 dp[1] 无意义（无法拆成至少两个数）')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 3 到 n，j 从 1 到 i-2。dp[i] 依赖 dp[i-j]（更小的子问题已算出）。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n]。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n²)：三角形n行，第i行i个元素，总计n(n+1)/2个状态，每个做min+加法 → O(n²)<br>- 空间 O(n)：自底向上DP，每行只依赖下一行 → 保留一个长度n+1的dp数组')

add_basic(d, make_front(p, '题解(DP)'),
    '拆成 j+(i-j) 还是 j+继续拆(i-j)：dp[i] = max(dp[i], max(j*(i-j), j*dp[i-j]))。<br>'
    + code(
        'class Solution {\n'
        '    public int integerBreak(int n) {\n'
        '        int[] dp = new int[n + 1];\n'
        '        dp[2] = 1;\n'
        '        for (int i = 3; i &lt;= n; ++i) {\n'
        '            for (int j = 1; j &lt; i - 1; ++j) {\n'
        '                dp[i] = Math.max(dp[i], Math.max(j * (i - j), j * dp[i - j]));\n'
        '            }\n'
        '        }\n'
        '        return dp[n];\n'
        '    }\n'
        '}'
    ))

add_basic(d, make_front(p, '题解(数学)'),
    '尽量拆 3：n 对 3 取余。<br>余 0 → 3^a；余 1 → 3^(a-1)×4；余 2 → 3^a×2。n≤3 返回 n-1。')

# ============================================================
# 31. 把数字翻译成字符串
# ============================================================
p = '把数字翻译成字符串'
d = make_deck(1747300131, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定数字 num，按规则 0->a, 1->b, ..., 25->z 翻译，返回不同翻译方法数量。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::前 i 个数字的翻译方法数}}',
    '与解码方法类似，但 0 也有意义')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>若 10&lt;=temp&lt;=25：dp[i]={{c1::dp[i-1]+dp[i-2]}}<br>'
    + '否则 dp[i]={{c2::dp[i-1]}}',
    '两位数合法范围 10~25，一位数始终合法')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::1}}, dp[1] = {{c2::1}}',
    '第一位数字始终可翻译')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 2 到 len 正向遍历。判断 substring(i-2, i) 是否在 10~25 之间。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[len]。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(M×N)：二维dp表共(M+1)×(N+1)格，每格O(1)比较两个字符 → O(MN)<br>- 空间 O(M×N) → 优化到O(min(M,N))：每行只依赖上一行和当前行左侧，保留两行')

add_basic(d, make_front(p, '题解'),
    '与解码方法的区别：0 有意义（0→a），无需特殊处理。两位数 10~25 合法则 dp[i]=dp[i-1]+dp[i-2]。<br>'
    + code(
        'class Solution {\n'
        '    public int translateNum(int num) {\n'
        '        String s = String.valueOf(num);\n'
        '        int[] dp = new int[s.length() + 1];\n'
        '        dp[0] = 1;\n'
        '        dp[1] = 1;\n'
        '        for (int i = 2; i &lt;= s.length(); i++) {\n'
        '            int temp = Integer.parseInt(s.substring(i - 2, i));\n'
        '            if (temp &gt;= 10 && temp &lt;= 25)\n'
        '                dp[i] = dp[i - 1] + dp[i - 2];\n'
        '            else\n'
        '                dp[i] = dp[i - 1];\n'
        '        }\n'
        '        return dp[s.length()];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 32. 掷骰子的N种方法
# ============================================================
p = '掷骰子的N种方法'
d = make_deck(1747300132, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '有 n 个 m 面骰子（点数 1..m），给定整数 target，返回掷出点数和为 target 的方案数（对 1e9+7 取模）。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i][j] = {{c1::前 i 个骰子和为 j 的方案数}}',
    '分组背包：每个骰子是一个分组，掷出 1~m 点')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i][j] = sum(dp[i-1][{{c1::j-k}}]), k=1..min(m,j)',
    '三重循环：骰子 × 容量 × 决策')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0][0] = {{c1::1}}',
    '0 个骰子和为 0 有 1 种方案')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 n，j 从 0 到 target，k 从 1 到 min(m,j)。<br>一维优化需倒序 j：dp[j] = sum(dp[j-k])，且每轮开始 dp[j]=0 重置。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n][target] % MOD。<br>剪枝：若 n*m < target 直接返回 0（不可能达到）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n²)：三角形n行，第i行i个元素，总计n(n+1)/2个状态，每个做min+加法 → O(n²)<br>- 空间 O(n)：自底向上DP，每行只依赖下一行 → 保留一个长度n+1的dp数组')

add_basic(d, make_front(p, '题解(二维DP)'),
    '分组背包三重循环：骰子 i、容量 j、决策 k（1~m）。<br>'
    + code(
        'class Solution {\n'
        '    private static final int MOD = (int) 1e9 + 7;\n'
        '    public int numRollsToTarget(int n, int m, int target) {\n'
        '        if (n * m &lt; target) return 0;\n'
        '        int[][] dp = new int[n + 1][target + 1];\n'
        '        dp[0][0] = 1;\n'
        '        for (int i = 1; i &lt;= n; i++) {\n'
        '            for (int j = 0; j &lt;= target; j++) {\n'
        '                for (int k = 1; j - k &gt;= 0 && k &lt;= m; k++)\n'
        '                    dp[i][j] = (dp[i][j] + dp[i - 1][j - k]) % MOD;\n'
        '            }\n'
        '        }\n'
        '        return dp[n][target];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 33. 连续子数组的最大和（精简版）
# ============================================================
p = '连续子数组的最大和(精简)'
d = make_deck(1747300133, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数数组 nums，找出最大和的连续子数组，返回其最大和。（精简版，原地 DP）')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>nums[i] 复用为 {{c1::以 nums[i] 结尾的最大子数组和}}',
    '原地修改：直接在原数组上做 DP')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>nums[i] += max({{c1::nums[i-1]}}, 0)',
    '前一个位置贡献为正则累加，为负则丢弃')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>res = {{c1::nums[0]}}',
    '第一个元素即为初始最大值')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 1 到 len-1 正向遍历。每次 nums[i] += max(nums[i-1], 0)，再更新 res。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 res（全局最大值）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：生成n个丑数，每次取min(dp[p2]×2, dp[p3]×3, dp[p5]×5)，移动被选中的指针 → n×O(1)=O(n)<br>- 空间 O(n)：dp数组存储n个丑数。dp天然有序，下一个丑数一定是之前某个丑数×质因子的最小值')

add_basic(d, make_front(p, '题解'),
    '原地 DP：nums[i] += max(nums[i-1], 0)。前一个位置贡献为正则累加，为负则丢弃。<br>'
    + code(
        'class Solution {\n'
        '    public int maxSubArray(int[] nums) {\n'
        '        int res = nums[0];\n'
        '        for (int i = 1; i &lt; nums.length; i++) {\n'
        '            nums[i] += Math.max(nums[i - 1], 0);\n'
        '            res = Math.max(res, nums[i]);\n'
        '        }\n'
        '        return res;\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 34. 青蛙跳台阶问题
# ============================================================
p = '青蛙跳台阶问题'
d = make_deck(1747300134, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '青蛙一次跳 1 级或 2 级台阶，求跳上 n 级台阶的跳法总数。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::跳上第 i 级台阶的跳法数}}',
    '与爬楼梯完全相同')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i] = {{c1::dp[i-1] + dp[i-2]}}',
    '最后一步跳 1 级或 2 级')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::1}}, dp[1] = {{c2::1}}, dp[2] = {{c3::2}}',
    '注意 dp[0]=1 的处理，结果需对 1e9+7 取模')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 3 到 n 正向遍历。可优化为两个变量 i, j 滚动。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n] % 1000000007。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(m×n)：二维dp表共(m+1)×(n+1)个格子，每格做常数次比较（min of 3 operations） → O(mn)<br>- 空间 O(m×n) → 优化到O(min(m,n))：当前行只依赖上一行和左边，两行滚动即可')

add_basic(d, make_front(p, '题解'),
    'dp[i] = dp[i-1] + dp[i-2]，结果对 1000000007 取模。dp[0]=1 用于统一递推。<br>'
    + code(
        'class Solution {\n'
        '    public int numWays(int n) {\n'
        '        int[] dp = new int[Math.max(n + 1, 3)];\n'
        '        dp[0] = 1;\n'
        '        dp[1] = 1;\n'
        '        dp[2] = 2;\n'
        '        for (int i = 3; i &lt;= n; i++) {\n'
        '            dp[i] = dp[i - 1] + dp[i - 2];\n'
        '            dp[i] %= 1000000007;\n'
        '        }\n'
        '        return dp[n];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 35. 青蛙跳台阶问题 II
# ============================================================
p = '青蛙跳台阶问题 II'
d = make_deck(1747300135, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '青蛙一次可以跳 1..n 级台阶，求跳上 n 级台阶的跳法总数。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>f(n) = {{c1::跳上第 n 级台阶的跳法数}}',
    '不限制最大跳跃距离')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>f(n) = {{c1::f(n-1) + f(n-2) + ... + f(2) + f(1)}}<br>'
    + '化简：f(n) = {{c2::2 * f(n-1)}}',
    'f(n) - f(n-1) = f(n-1)，推出等比数列')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>f(1) = {{c1::1}}',
    '公比 2，等比数列')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'f(1)=1，从 2 到 n：dp[i] = 2 * dp[i-1]（或直接返回 2^(n-1)）。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n]（或直接用公式 2^(n-1)）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：变态跳台阶，dp[i]=2^(i-1)，前缀和一次遍历 → O(n)；或用公式2^(n-1)+快速幂 → O(log n)<br>- 空间 O(1)：一个preSum变量')

add_basic(d, make_front(p, '题解'),
    '等比数列：f(n) = 2 * f(n-1) = 2^(n-1)。dp[i] = 2 * dp[i-1]。<br>'
    + code(
        'class Solution {\n'
        '    public int numWays(int n) {\n'
        '        int[] dp = new int[Math.max(n + 1, 3)];\n'
        '        dp[0] = 1;\n'
        '        dp[1] = 1;\n'
        '        dp[2] = 2;\n'
        '        for (int i = 3; i &lt;= n; i++) {\n'
        '            dp[i] = 2 * dp[i - 1];\n'
        '        }\n'
        '        return dp[n];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 36. 斐波那契数列
# ============================================================
p = '斐波那契数列'
d = make_deck(1747300136, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数 n，返回第 n 项斐波那契数（F(0)=0, F(1)=1）。')

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>dp[i] = {{c1::第 i 项斐波那契数}}',
    'F(0)=0, F(1)=1')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>dp[i] = {{c1::dp[i-1] + dp[i-2]}}',
    '标准斐波那契递推')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>dp[0] = {{c1::0}}, dp[1] = {{c2::1}}',
    '注意：爬楼梯第一项从 1 开始，斐波那契从 0 开始')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    'i 从 2 到 n。可滚动变量优化到 O(1)。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 dp[n]（可能需取模 1e9+7）。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n)：自底向上迭代n次加法 → O(n)<br>- 空间 O(1)：prev1、prev2两个滚动变量<br>矩阵快速幂优化：O(log n)/O(1)。递归（无记忆化）：O(2^n)/O(n) — 不推荐')

add_basic(d, make_front(p, '题解'),
    'dp[i] = dp[i-1] + dp[i-2]，对 1000000007 取模。DP O(n) vs 递归 O(2^n)。<br>'
    + code(
        'class Solution {\n'
        '    public int fib(int n) {\n'
        '        if (n == 0) return 0;\n'
        '        int[] dp = new int[n + 1];\n'
        '        dp[0] = 0;\n'
        '        dp[1] = 1;\n'
        '        for (int i = 2; i &lt;= n; i++) {\n'
        '            dp[i] = dp[i - 1] + dp[i - 2];\n'
        '            dp[i] %= 1000000007;\n'
        '        }\n'
        '        return dp[n];\n'
        '    }\n'
        '}'
    ))

# ============================================================
# 37. 斐波那契数
# ============================================================
p = '斐波那契数'
d = make_deck(1747300137, f'算法::动态规划::{p}')

add_basic(d, make_front(p, '题干'),
    '给定整数 n，返回第 n 个斐波那契数。'
    + img('image 33.png'))

add_cloze(d, make_front(p, '定义状态(1/5)')
    + '<br>F(n) = {{c1::第 n 个斐波那契数}}',
    'F(0)=0, F(1)=1, F(2)=1')

add_cloze(d, make_front(p, '转移方程(2/5)')
    + '<br>F(n) = {{c1::F(n-1) + F(n-2)}}',
    '与爬楼梯 n 阶等价，初始值略有不同')

add_cloze(d, make_front(p, '初始化(3/5)')
    + '<br>n==0 → {{c1::0}}, n==1||n==2 → {{c2::1}}',
    '边界条件判断')

add_basic(d, make_front(p, '计算顺序(4/5)'),
    '可用迭代或递归（递归会超时）。DP：从 2 到 n 迭代。')

add_basic(d, make_front(p, '返回结果(5/5)'),
    '返回 F(n)。')

add_basic(d, make_front(p, '复杂度'),
    '- 时间 O(n²)：在LIS DP基础上维护count[i]（以i结尾的LIS个数），外层i内层j → n(n-1)/2 = O(n²)<br>- 空间 O(n)：length[i]和count[i]各一个长度为n的数组')

add_basic(d, make_front(p, '题解'),
    '递归版简洁但指数复杂度 O(2^n)，DP 迭代最优 O(n)。F(0)=0, F(1)=1, F(2)=1。<br>'
    + code(
        'class Solution {\n'
        '    public int fib(int n) {\n'
        '        if (n == 0) return 0;\n'
        '        if (n == 1 || n == 2) return 1;\n'
        '        return fib(n - 1) + fib(n - 2);\n'
        '    }\n'
        '}'
    ))

# ============================================================
# Export
# ============================================================

if __name__ == '__main__':
    result = build('../../牌组/算法/动态规划.apkg')
    print(result)
