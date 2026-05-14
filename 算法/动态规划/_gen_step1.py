"""
Step 1: Inject complexity analyses into the source markdown file.
Run: python _gen_step1.py
After this, the md will have **复杂度分析** sections for all 37 problems.
"""
import re
from pathlib import Path

TOPIC_DIR = Path(r'D:\anki\算法\动态规划')
MD_PATH = TOPIC_DIR / '动态规划 255444514a3180be947eea7331a4aaa6.md'

# ── Complexity derivations for all 37 DP problems ────────────

COMPLEXITY: dict[str, str] = {
    '最大子数组和': (
        '\n**复杂度分析**\n\n'
        '**DP (Kadane)**：\n'
        '- 时间 O(n)：遍历数组一次，每个位置O(1)操作（1次if + 1次max）→ n×O(1)=O(n)\n'
        '- 空间 O(1)：只需dp和res两个变量，不随n增长\n\n'
        '**分治**：\n'
        '- 时间 O(n log n)：T(n)=2T(n/2)+O(n)，递归深度log n，每层合并O(n)\n'
        '- 空间 O(log n)：递归栈深度'
    ),
    '返回最大子数组的起始位置和结束位置': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：同Kadane算法，额外记录tempStart/start/end三个下标变量仍是O(1)操作 → O(n)\n'
        '- 空间 O(1)：dp、maxSum、tempStart、start、end共5个整型变量，不随n增长'
    ),
    '买卖股票的最佳时机': (
        '\n**复杂度分析**\n\n'
        '**DP（二维状态机）**：\n'
        '- 时间 O(n)：遍历prices数组n天，每天更新持股/不持股两个状态，每次O(1) → n×2×O(1)=O(n)\n'
        '- 空间 O(1)：dp[i]只依赖dp[i-1]，滚动优化后只需hold和notHold两个变量\n\n'
        '**贪心（一次遍历）**：记录历史最低价min，每天计算prices[i]-min并更新最大利润\n'
        '- 时间 O(n) / 空间 O(1)'
    ),
    '买卖股票的最佳时机 II': (
        '\n**复杂度分析**\n\n'
        '**DP（状态机）**：\n'
        '- 时间 O(n)：遍历一次，与I的唯一区别是买入时用dp[i-1][0]-prices[i]（而非-prices[i]），允许用之前的利润再买入 → O(n)\n'
        '- 空间 O(1)：滚动优化后只需hold和notHold两个变量\n\n'
        '**贪心**：只要prices[i]>prices[i-1]就累加差价，等价于无限次交易\n'
        '- 时间 O(n) / 空间 O(1)'
    ),
    '买卖股票的最佳时机 III': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：每天有6种状态（持股/不持股 × 已卖出0/1/2次），状态数固定为6不随n增长，每步O(1) → O(n)\n'
        '- 空间 O(1)：dp[i]只依赖dp[i-1]的6个状态值，用6个变量滚动即可'
    ),
    '买卖股票的最佳时机 IV': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n×k)：外层遍历n天，内层遍历k次交易 → n×k次状态转移。当k≥n/2时等效于无限交易，实际退化为O(n)\n'
        '- 空间 O(k)：buy和sell两个长度为k+1的数组滚动更新。优化技巧：k=min(k, n/2)预处理'
    ),
    '最长上升子序列': (
        '\n**复杂度分析**\n\n'
        '**DP (O(n²))**：\n'
        '- 时间 O(n²)：外层i从0到n-1，内层j从0到i-1 → Σi = n(n-1)/2 = O(n²)\n'
        '- 空间 O(n)：dp[i]数组长度n，每个元素初始化为1\n\n'
        '**贪心+二分 (O(n log n))**：\n'
        '- 时间 O(n log n)：遍历n个元素，每个在tails数组二分查找插入位置（tails长度≤n，二分O(log n)）→ n×O(log n)\n'
        '- 空间 O(n)：tails数组最坏情况存储n个元素'
    ),
    '接雨水': (
        '\n**复杂度分析**\n\n'
        '**DP（预处理左右最大值）**：\n'
        '- 时间 O(n)：三次遍历 → 左→右求left_max(O(n)) + 右→左求right_max(O(n)) + 累加雨水(O(n)) = 3n = O(n)\n'
        '- 空间 O(n)：left_max和right_max各为长度n的数组\n\n'
        '**双指针（最优）**：\n'
        '- 时间 O(n)：左右指针各移动n次，每次O(1)取min计算差值 → O(n)\n'
        '- 空间 O(1)：仅需left、right、left_max、right_max四个变量'
    ),
    '编辑距离': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(m×n)：二维dp表共(m+1)×(n+1)个格子，每格做常数次比较（min of 3 operations） → O(mn)\n'
        '- 空间 O(m×n) → 优化到O(min(m,n))：当前行只依赖上一行和左边，两行滚动即可'
    ),
    '最长公共子序列': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(M×N)：二维dp表共(M+1)×(N+1)格，每格O(1)比较两个字符 → O(MN)\n'
        '- 空间 O(M×N) → 优化到O(min(M,N))：每行只依赖上一行和当前行左侧，保留两行'
    ),
    '爬楼梯': (
        '\n**复杂度分析**\n\n'
        '**迭代DP**：dp[i]=dp[i-1]+dp[i-2]，从1到n迭代n次加法 → 时间O(n)，空间O(1)（prev2/prev1/curr三个变量）\n'
        '**矩阵快速幂**：时间O(log n)，空间O(1)\n'
        '**递归（无记忆化）**：时间O(2^n)，空间O(n) — 不推荐'
    ),
    '使用最小花费爬楼梯': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：遍历n阶，每阶dp[i]=cost[i]+min(dp[i-1],dp[i-2])一次加法和一次min → n×O(1)=O(n)\n'
        '- 空间 O(1)：只依赖前两个状态，prev1和prev2两个变量滚动'
    ),
    '圆环回原点问题': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n×len)：dp[i][j]表示走i步位于位置j的方案数，i从1到n，j从0到len-1 → n×len个状态，每状态O(1)转移 → O(n×len)\n'
        '- 空间 O(len)：第i步只依赖第i-1步，用两个长度为len的数组交替 → O(len)'
    ),
    '零钱兑换': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n×amount)：完全背包问题。外层遍历n种硬币，内层遍历金额1~amount（正序） → n×amount次状态转移\n'
        '- 空间 O(amount)：一维dp数组长度amount+1，dp[j]=min(dp[j], dp[j-coin]+1)'
    ),
    '零钱兑换 II': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n×amount)：完全背包求方案数。外层n种硬币，内层amount个金额（正序） → O(n×amount)\n'
        '- 空间 O(amount)：一维dp数组长度amount+1，dp[j]+=dp[j-coin]'
    ),
    '最大正方形': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(M×N)：双重循环遍历矩阵所有格子，每格取min(左,上,左上)+1 → O(MN)\n'
        '- 空间 O(N)：dp[i][j]只依赖左边、上边、左上角三个位置 → 保留一行dp数组+一个prev对角变量 → O(N)'
    ),
    '不同路径': (
        '\n**复杂度分析**\n\n'
        '**DP**：dp[i][j]=dp[i-1][j]+dp[i][j-1]，双重循环遍历网格 → 时间O(m×n)，空间可优化到O(n)（一行正序更新）\n'
        '**组合数学**：C(m+n-2, m-1) → 时间O(min(m,n))，空间O(1)'
    ),
    '乘积最大子数组': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：遍历一次，同时维护以i结尾的最大乘积imax和最小乘积imin（因为负数×负数可能反转变为最大），3次比较/乘法 → O(n)\n'
        '- 空间 O(1)：imax、imin、max三个变量。关键技巧：遇到nums[i]<0时交换imax和imin'
    ),
    '打家劫舍': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：遍历n间房子，每间计算dp[i]=max(dp[i-1], dp[i-2]+nums[i])，一次比较+一次加法 → O(n)\n'
        '- 空间 O(1)：状态方程只依赖前两个，prev2（dp[i-2]）和prev1（dp[i-1]）两个滚动变量'
    ),
    '打家劫舍 II': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：分两段分别DP：[0,n-2]和[1,n-1]各一次 → 2n = O(n)\n'
        '- 空间 O(1)：每段只用两个滚动变量\n'
        '核心思路：环形问题不能同时偷首尾 → 去掉头或尾 → 两次线性DP取max'
    ),
    '最长重复子数组': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(m×n)：双重循环，dp[i][j]表示以nums1[i-1]和nums2[j-1]结尾的最长公共子数组 → m×n个状态O(1)比较 → O(mn)\n'
        '- 空间 O(min(m,n))：dp[i][j]只依赖dp[i-1][j-1]（左上角），可倒序更新一维数组 → O(min(m,n))'
    ),
    '单词拆分': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n²)：外层i从1到n，内层j从0到i-1 → Σi = n(n+1)/2 = O(n²)次子串检查\n'
        '- 空间 O(n)：dp数组长度n+1 + wordDict的HashSet空间\n'
        '注：substring和set.contains假设为O(1)，因为单词长度通常有上限'
    ),
    '解码方法': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：遍历字符串一次，每步检查1位编码（charAt(i)≠0）和2位编码（10~26） → 两次判断 → O(n)\n'
        '- 空间 O(1)：dp[i]只依赖dp[i-1]和dp[i-2]，两个滚动变量。递推本质同爬楼梯：满足条件时dp[i]=dp[i-1]+dp[i-2]'
    ),
    '三角形最小路径和': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n²)：三角形n行，第i行i个元素，总计n(n+1)/2个状态，每个做min+加法 → O(n²)\n'
        '- 空间 O(n)：自底向上DP，每行只依赖下一行 → 保留一个长度n+1的dp数组'
    ),
    '丑数 II': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：生成n个丑数，每次取min(dp[p2]×2, dp[p3]×3, dp[p5]×5)，移动被选中的指针 → n×O(1)=O(n)\n'
        '- 空间 O(n)：dp数组存储n个丑数。dp天然有序，下一个丑数一定是之前某个丑数×质因子的最小值'
    ),
    '交错字符串': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n×m)：dp[i][j]表示s1前i个+s2前j个能否组成s3前i+j个，共(n+1)×(m+1)状态，每格O(1) → O(nm)\n'
        '- 空间 O(m)：dp[i][j]只依赖上方dp[i-1][j]和左边dp[i][j-1]，一维数组正序更新 → O(m)'
    ),
    '最长递增子序列的个数': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n²)：在LIS DP基础上维护count[i]（以i结尾的LIS个数），外层i内层j → n(n-1)/2 = O(n²)\n'
        '- 空间 O(n)：length[i]和count[i]各一个长度为n的数组'
    ),
    '分割等和子集': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n×target)：0/1背包问题，target=sum/2。n个物品，每个物品遍历target个容量（倒序） → O(n×target)\n'
        '- 空间 O(target)：一维dp倒序遍历（防止同一物品重复使用），数组长度target+1。为什么倒序：防止同一物品被多次选用'
    ),
    '完全平方数': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n√n)：外层遍历1~n（O(n)），内层遍历完全平方数j²≤i，j∈[1,√n] → n×√n = O(n√n)\n'
        '- 空间 O(n)：dp数组长度n+1。等价于完全背包：硬币种类为{1,4,9,16,...}，求最少硬币数'
    ),
    '整数拆分': (
        '\n**复杂度分析**\n\n'
        '**DP**：dp[i]=max(j×max(i-j, dp[i-j]))，外层i 2~n，内层j 1~i-1 → O(n²)；空间O(n)\n'
        '**数学（贪心）**：尽量拆成3。余0→全3，余1→一个4其余3，余2→一个2其余3 → 时间O(1)，空间O(1)'
    ),
    '把数字翻译成字符串': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：同解码方法(LC 91)，遍历数字字符串一次，每步O(1)检查1位(0~9)和2位(10~25)合法性 → O(n)\n'
        '- 空间 O(1)：状态只依赖前两个，滚动变量优化'
    ),
    '掷骰子的N种方法': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n×k×target)：三重循环 → n个骰子 × target个和值 × k个面（1~k枚举） → O(n×k×target)\n'
        '- 空间 O(target)：dp[i][j]只依赖dp[i-1]行 → 保留两行长度target+1交替 → O(target)'
    ),
    '连续子数组的最大和': (
        '\n**复杂度分析**\n\n'
        '同「最大子数组和」(LC 53)：Kadane算法 → 时间O(n)，空间O(1)'
    ),
    '青蛙跳台阶问题': (
        '\n**复杂度分析**\n\n'
        '同「爬楼梯」(LC 70)：dp[i]=dp[i-1]+dp[i-2] → 时间O(n)，空间O(1)'
    ),
    '青蛙跳台阶问题 II': (
        '\n**复杂度分析**\n\n'
        '变态跳台阶：每次可跳1~n级 → dp[i]=2^(i-1)\n'
        '- 时间 O(n)：前缀和一次遍历 → O(n)；或用公式2^(n-1)+快速幂 → O(log n)\n'
        '- 空间 O(1)：一个preSum变量'
    ),
    '斐波那契数列': (
        '\n**复杂度分析**\n\n'
        '同「斐波那契数」(LC 509)：F(n)=F(n-1)+F(n-2)\n'
        '迭代DP：时间O(n)，空间O(1)。矩阵快速幂：时间O(log n)，空间O(1)'
    ),
    '斐波那契数': (
        '\n**复杂度分析**\n\n'
        '- 时间 O(n)：自底向上迭代n次加法 → O(n)\n'
        '- 空间 O(1)：prev1、prev2两个滚动变量\n'
        '矩阵快速幂优化：O(log n)/O(1)。递归（无记忆化）：O(2^n)/O(n) — 不推荐'
    ),
}


def update_md() -> None:
    """Insert complexity analysis sections into the source md."""
    content = MD_PATH.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines: list[str] = []
    i = 0
    heading_pat = re.compile(r'^###\s+(?:\*\*)?(.+?)(?:\*\*)?$')
    inserted = 0

    while i < len(lines):
        line = lines[i]
        m = heading_pat.match(line)
        if m:
            name = m.group(1).strip()
            new_lines.append(line)

            if name in COMPLEXITY:
                j = i + 1
                while j < len(lines) and not heading_pat.match(lines[j]):
                    j += 1

                section = '\n'.join(lines[i + 1:j])
                if '**复杂度分析**' not in section:
                    insert_at = j
                    while insert_at > i + 1 and lines[insert_at - 1].strip() == '':
                        insert_at -= 1

                    new_lines.extend(lines[i + 1:insert_at])
                    new_lines.append(COMPLEXITY[name])
                    if insert_at < j:
                        new_lines.extend(lines[insert_at:j])
                    inserted += 1
                    i = j
                    continue
        new_lines.append(line)
        i += 1

    updated = '\n'.join(new_lines)
    MD_PATH.write_text(updated, encoding='utf-8')
    print(f'Inserted {inserted} complexity sections → {MD_PATH.name}')


if __name__ == '__main__':
    update_md()
