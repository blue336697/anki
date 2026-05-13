"""
Build APKG with images embedded in cards.
Run from 算法/动态规划/ directory (where images live).
Usage: python build_apkg.py
Output: 动态规划.apkg
"""
import genanki

# ============================================================
# Models
# ============================================================

BASIC_MODEL = genanki.Model(
    1747300001,
    'Basic (算法笔记)',
    fields=[{'name': 'Front'}, {'name': 'Back'}],
    templates=[{
        'name': 'Card 1',
        'qfmt': '{{Front}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
    }],
    css='.card{font-family:"Microsoft YaHei",sans-serif;font-size:20px;text-align:center;color:#333;padding:20px}img{max-width:100%;height:auto;margin-top:10px;border-radius:4px}'
)

CLOZE_MODEL = genanki.Model(
    1747300002,
    'Cloze (算法笔记)',
    model_type=1,
    fields=[{'name': 'Text'}, {'name': 'Back Extra'}],
    templates=[{
        'name': 'Cloze',
        'qfmt': '{{cloze:Text}}',
        'afmt': '{{cloze:Text}}<br>{{Back Extra}}',
    }],
    css='.card{font-family:"Microsoft YaHei",sans-serif;font-size:20px;text-align:center;color:#333;padding:20px}.cloze{font-weight:bold;color:#2563eb}img{max-width:100%;height:auto;margin-top:10px;border-radius:4px}'
)

# ============================================================
# Helpers
# ============================================================

ALL_DECKS: list[genanki.Deck] = []
USED_IMAGES: set[str] = set()

def img(name: str) -> str:
    USED_IMAGES.add(name)
    return f'<br><img src="{name}" style="max-width:100%;margin-top:12px">'

def make_deck(deck_id: int, name: str) -> genanki.Deck:
    d = genanki.Deck(deck_id, name)
    ALL_DECKS.append(d)
    return d

def add_basic(deck, front, back):
    deck.add_note(genanki.Note(model=BASIC_MODEL, fields=[front, back]))

def add_cloze(deck, text, extra=""):
    deck.add_note(genanki.Note(model=CLOZE_MODEL, fields=[text, extra]))

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
d = make_deck(1747300101, '算法::动态规划::最大子数组和')
add_basic(d, 'dp[i] 的状态定义？',
    'dp[i] = 以 nums[i] 结尾的连续子数组的最大和（必须包含 nums[i]）')
add_cloze(d, 'if (dp[i-1] > 0) dp[i] = {{c1::dp[i-1] + nums[i]}}; else dp[i] = {{c2::nums[i]}}',
    '正前缀累加，负前缀丢弃重来')
add_basic(d, 'res 初始值为什么不能设为 0？',
    '全负数数组时 max(0, 负数) = 0 错误。应设为 res = nums[0]')
add_basic(d, '分治解法的三种情况？' + img('image.png'),
    '1. 最大子数组在左半\n2. 最大子数组在右半\n3. 跨越中点（向左最大后缀 + 向右最大前缀）')
add_cloze(d, '贪心：if(sum>0) {{c1::sum+=num}} else {{c2::sum=num}}; res={{c3::Math.max(res,sum)}}',
    'sum <= 0 则丢弃前缀重新开始')

# --- 2. 返回起止位置 ---
d = make_deck(1747300102, '算法::动态规划::最大子数组和-返回位置')
add_cloze(d, 'if (dp > maxSum) { maxSum=dp; start={{c1::tempStart}}; end=i; }',
    'dp 严格大于历史最大才更新起止位置')
add_basic(d, 'tempStart 何时更新？',
    'dp + nums[i] < nums[i]（前缀为负贡献）时 tempStart = i，重新开始')

# --- 3. 买卖股票 I ---
d = make_deck(1747300103, '算法::动态规划::买卖股票I')
add_basic(d, '状态定义（只能交易 1 次）？' + img('image 1.png'),
    'dp[i][0] = 第 i 天不持股的最大现金\n'
    'dp[i][1] = 第 i 天持股的最大现金')
add_cloze(d, 'dp[i][0]=max({{c1::dp[i-1][0]}},{{c2::dp[i-1][1]+prices[i]}});\n'
    'dp[i][1]=max({{c3::dp[i-1][1]}},{{c4::-prices[i]}})',
    '只能买一次，买入直接用 -prices[i]')
add_basic(d, '空间优化思路？', '记录历史最低价 min，每天算 prices[i]-min 取最大值')

# --- 4. 买卖股票 II ---
d = make_deck(1747300104, '算法::动态规划::买卖股票II')
add_basic(d, '与 I 的唯一区别？',
    'I:  dp[i][1] = max(dp[i-1][1], -prices[i])\n'
    'II: dp[i][1] = max(dp[i-1][1], dp[i-1][0] - prices[i])\n'
    '← 买入时可用之前卖出赚的钱')
add_cloze(d, 'dp[i][0]=max(dp[i-1][0], {{c1::dp[i-1][1]+prices[i]}});\n'
    'dp[i][1]=max(dp[i-1][1], {{c2::dp[i-1][0]-prices[i]}})',
    '不限制交易次数')
add_basic(d, '贪心解法？', '只要 prices[i] > prices[i-1] 就把差价加入利润')

# --- 5. 买卖股票 III (最多2次) ---
d = make_deck(1747300105, '算法::动态规划::买卖股票III')
add_cloze(d, '新增维度：dp[i][j][k]，j={{c1::是否持股}}，k={{c2::已卖出次数}}',
    'k 从 0 到 2，最多交易 2 次')
add_basic(d, '哪些初始状态无效？',
    'dp[0][0][1]=dp[0][0][2]=dp[0][1][1]=dp[0][1][2]=MIN_VALUE\n'
    '第一天不可能已卖出或多次交易')
add_basic(d, 'III 中卖出算一次交易？', '是的，卖出时 k+1（依赖 k-1），买入时 k 不变')

# --- 6. 买卖股票 IV (最多k次) ---
d = make_deck(1747300106, '算法::动态规划::买卖股票IV')
add_basic(d, '与 III 的关键区别？',
    'III 固定 k=2，IV 中 k 可变。k = min(k, len/2)')
add_cloze(d, 'IV 买入时 j-1（与 III 相反！）：\n'
    'dp[i][1][j]=max({{c1::dp[i-1][0][j-1]-prices[i]}},{{c2::dp[i-1][1][j]}})',
    'IV 买入时算一次交易，III 卖出时才算')

# --- 7. LIS ---
d = make_deck(1747300107, '算法::动态规划::最长上升子序列')
add_basic(d, 'dp[i] 的含义？' + img('image 4.png'),
    '以 nums[i] 结尾的最长严格递增子序列长度')
add_cloze(d, 'for(j=0;j<i;j++) if(nums[j]<nums[i]) dp[i]={{c1::Math.max(dp[i],dp[j]+1)}}',
    'O(n²)，每个位置向前扫描比它小的元素')
add_basic(d, '二分优化（耐心排序）核心？',
    'tails[i] = 长度为 i+1 的子序列的最小尾元素。\n'
    '遍历 num，二分替换 tails 中 >= num 的位置 → O(n log n)')
add_basic(d, '子序列 vs 子数组？', '子序列不要求连续（保持相对顺序），子数组必须连续')

# --- 8. 接雨水 ---
d = make_deck(1747300108, '算法::动态规划::接雨水')
add_basic(d, 'DP 解法核心？' + img('image 5.png'),
    '每个柱子接水量 = min(左边最高, 右边最高) - 当前高度。\n'
    '两遍扫描记录左右最高，第三遍累加。')
add_cloze(d, 'dp_left[i]=max({{c1::dp_left[i-1]}},{{c2::height[i-1]}})\n'
    'dp_right[i]=max({{c3::dp_right[i+1]}},{{c4::height[i+1]}})',
    '左→右记录左边最高，右→左记录右边最高')
add_basic(d, '双指针优化？', '移动较矮一侧的指针，容量由短板决定')

# --- 9. 编辑距离 ---
d = make_deck(1747300109, '算法::动态规划::编辑距离')
add_basic(d, 'dp[i][j] 的含义？' + img('image 6.png'),
    'word1 前 i 个字符 转换成 word2 前 j 个字符的最少操作数')
add_cloze(d, '三种操作：dp[i][j]=min(删除{{c1::dp[i-1][j]+1}}, 插入{{c2::dp[i][j-1]+1}}, 替换{{c3::dp[i-1][j-1]+1}})',
    '每个操作 = 前状态代价 + 1' + img('image 7.png'))
add_basic(d, '字符相同时？',
    'word1[i-1]==word2[j-1] → dp[i][j]=dp[i-1][j-1]（无需操作）')

# --- 10. LCS ---
d = make_deck(1747300110, '算法::动态规划::最长公共子序列')
add_cloze(d, '相等：dp[i][j]={{c1::dp[i-1][j-1]+1}}；不等：dp[i][j]={{c2::max(dp[i-1][j],dp[i][j-1])}}',
    '相等继承+1，不等取两边最大')
add_basic(d, '为什么 dp[M+1][N+1]？', 'i=0 或 j=0 表示空串，LCS = 0，统一处理边界')

# --- 11. 爬楼梯 ---
d = make_deck(1747300111, '算法::动态规划::爬楼梯')
add_cloze(d, '递推：f(n) = {{c1::f(n-1) + f(n-2)}}' + img('image 10.png'),
    '最后一步跨 1 阶或 2 阶，同斐波那契')
add_basic(d, '变量优化？', 'p, q, r 三变量滚动：r=p+q; p=q; q=r → O(1)')

# --- 12. 最小花费爬楼梯 ---
d = make_deck(1747300112, '算法::动态规划::最小花费爬楼梯')
add_cloze(d, 'minCost[i]=min({{c1::minCost[i-1]+cost[i]}},{{c2::minCost[i-2]+cost[i-1]}})' + img('image 11.png'),
    '从 i-1 跨 1 步或 i-2 跨 2 步')
add_basic(d, '起点？', '可从第 0 阶（免费）或第 1 阶开始')

# --- 13. 圆环回原点 ---
d = make_deck(1747300113, '算法::动态规划::圆环回原点')
add_cloze(d, 'dp[i][j]=dp[i-1][{{c1::(j-1+len)%len}}]+dp[i-1][{{c2::(j+1)%len}}]',
    '从左右邻居走来，取模处理环形' + img('image 12.png'))
add_basic(d, '与爬楼梯相似？', '每步两种选择（顺时针/逆时针）→ 类似爬楼梯 + 圆环约束')

# --- 14. 零钱兑换 ---
d = make_deck(1747300114, '算法::动态规划::零钱兑换')
add_basic(d, 'dp[i] 含义？', '凑金额 i 的最少硬币数。dp[0]=0，其余初始化为 amount+1')
add_cloze(d, 'dp[j] = min({{c1::dp[j]}}, {{c2::dp[j-coin]+1}})', '完全背包求最小值，正序遍历')
add_basic(d, '什么背包类型？', '完全背包求最小值')

# --- 15. 零钱兑换 II ---
d = make_deck(1747300115, '算法::动态规划::零钱兑换II')
add_basic(d, '与 I 的区别？', 'I 求最少硬币数，II 求组合数。转移从 min 变成 +=')
add_cloze(d, 'dp[j] = {{c1::dp[j] + dp[j-coin]}}，dp[0] = {{c2::1}}',
    'dp[0]=1 表示凑 0 元有一种方案（什么都不选）')
add_basic(d, '为什么外层硬币内层金额？', '保证组合数（非排列数），避免 [1,2] 和 [2,1] 重复计数')

# --- 16. 最大正方形 ---
d = make_deck(1747300116, '算法::动态规划::最大正方形')
add_basic(d, 'dp[i][j] 的含义？' + img('image 14.png'),
    '以 matrix[i-1][j-1] 为右下角的最大正方形边长')
add_cloze(d, 'dp[i+1][j+1]=min({{c1::dp[i][j+1]}},{{c2::dp[i+1][j]}},{{c3::dp[i][j]}})+1',
    '取左、上、左上最小值+1，边长受限于最短边' + img('image 15.png'))
add_basic(d, '如何降维？',
    '一维 dp[width+1] + northwest 变量保存左上旧值' + img('image 18.png'))

# --- 17. 不同路径 ---
d = make_deck(1747300117, '算法::动态规划::不同路径')
add_cloze(d, 'dp[i][j] = {{c1::dp[i-1][j] + dp[i][j-1]}}',
    '从上来+从左来 = 杨辉三角形')
add_basic(d, '数学解法？', '组合数 C(m+n-2, m-1)')
add_basic(d, '一维优化？', 'cur[j] = cur[j] + cur[j-1]')

# --- 18. 乘积最大子数组 ---
d = make_deck(1747300118, '算法::动态规划::乘积最大子数组')
add_basic(d, '和"最大子数组和"的关键区别？',
    '负数相乘变正！需同时维护 imax（最大乘积）和 imin（最小乘积）。\n'
    '遇到负数时交换 imax 和 imin')
add_cloze(d, 'if(nums[i]<0) { {{c1::swap(imax,imin)}} }',
    '负负得正：最小值×负数可能变最大值' + img('image 19.png'))
add_cloze(d, 'imax=max({{c1::imax*nums[i]}},{{c2::nums[i]}}); imin=min({{c3::imin*nums[i]}},{{c4::nums[i]}})',
    '接在前面或重新开始')

# --- 19. 打家劫舍 ---
d = make_deck(1747300119, '算法::动态规划::打家劫舍')
add_basic(d, '状态转移？' + img('image 20.png'),
    'dp[i] = max(dp[i-1], nums[i-1] + dp[i-2])\n'
    '不偷当前 → dp[i-1]；偷当前 → nums[i-1] + dp[i-2]')
add_basic(d, '为什么是最佳 DP 入门题？' + img('image 22.png'),
    '1. 子问题定义直观（偷前 k 间最大值）\n'
    '2. "偷或不偷"是 DP 最经典二分决策\n'
    '3. 只需前两个状态，便于理解空间优化')
add_cloze(d, 'int temp = max(curr, {{c1::prev + i}}); prev=curr; curr=temp',
    '只保留前两个状态')

# --- 20. 打家劫舍 II ---
d = make_deck(1747300120, '算法::动态规划::打家劫舍II')
add_basic(d, '环形如何处理？',
    '首尾不能同时偷 → 分两种情况取 max：\n'
    '1. 不偷第一家：rob(nums[1..end])\n'
    '2. 不偷最后一家：rob(nums[0..end-1])')
add_basic(d, '环形 DP 通用套路？', '拆为两个线性 DP：去头或去尾，取 max')

# --- 21. 最长重复子数组 ---
d = make_deck(1747300121, '算法::动态规划::最长重复子数组')
add_basic(d, '与 LCS 的区别？',
    '重复子数组要求连续。不等时 dp[i][j] 必须归零，LCS 保留历史最大')
add_cloze(d, '相等：dp[i][j]={{c1::dp[i-1][j-1]+1}}；不等：dp[i][j]={{c2::0}}',
    '不等必须归零！')
add_basic(d, '降维关键？' + img('image 24.png'),
    '倒序遍历 j，不等时 dp[j]=0 手动清零覆盖旧值')

# --- 22. 单词拆分 ---
d = make_deck(1747300122, '算法::动态规划::单词拆分')
add_basic(d, 'dp[i] 的含义？' + img('image 25.png'),
    'dp[i] = s 前 i 个字符能否被拆分为字典中的单词。dp[0]=true')
add_cloze(d, '若 dp[j] && wordDict.contains({{c1::s.substring(j,i)}})，则 dp[i]={{c2::true}}',
    '切分点 j：前 j 个可拆分 + j..i 在字典中')
add_basic(d, '另外两种解法？',
    'BFS：从 0 匹配单词入队直到末尾\n'
    'DFS+记忆化：递归尝试 + vis 剪枝' + img('image 29.png'))

# --- 23. 解码方法 ---
d = make_deck(1747300123, '算法::动态规划::解码方法')
add_basic(d, '与"翻译成字符串"的区别？', '解码中 0 无效！"06" 非法。翻译中 0→a 有效')
add_cloze(d, 's[i]==0：若前为1/2则dp[i]={{c1::dp[i-2]}}，否则{{c2::return 0}}',
    '0 不能单独成字母，必须和前面绑定' + img('image 31.png'))
add_cloze(d, 's[i]!=0且两位数合法：dp[i]=dp[i-1]+dp[i-2]（类似{{c1::爬楼梯}}）',
    '一位数和两位数都可行 → 方案数相加')

# --- 24. 三角形最小路径和 ---
d = make_deck(1747300124, '算法::动态规划::三角形最小路径和')
add_basic(d, '为什么自底向上更方便？',
    '不需要处理三角形边缘的边界条件，直接 min(左下, 右下) + 当前值')
add_cloze(d, 'dp[j] = min({{c1::dp[j]}}, {{c2::dp[j+1]}}) + triangle[i][j]',
    '从下往上滚动更新 dp 数组')

# --- 25. 丑数 II ---
d = make_deck(1747300125, '算法::动态规划::丑数II')
add_basic(d, '三指针法核心？',
    'dp[i] = min(2*dp[p2], 3*dp[p3], 5*dp[p5])\n'
    '三个指针各自独立移动，相等指针都++（去重）')
add_cloze(d, 'dp[i]=min({{c1::2*dp[p2]}},{{c2::3*dp[p3]}},{{c3::5*dp[p5]}})',
    '相等指针都需移动')

# --- 26. 交错字符串 ---
d = make_deck(1747300126, '算法::动态规划::交错字符串')
add_basic(d, 'dp[i][j] 含义？', 's1 前 i 个 + s2 前 j 个 能否交错组成 s3 前 i+j 个')
add_cloze(d, 'dp[i][j] = (dp[i-1][j]&&s1[i-1]==s3[i+j-1]) {{c1::||}} (dp[i][j-1]&&s2[j-1]==s3[i+j-1])',
    '当前字符要么来自 s1 要么来自 s2')

# --- 27. LIS 个数 ---
d = make_deck(1747300127, '算法::动态规划::LIS个数')
add_basic(d, '需要额外维护什么？' + img('image 32.png'),
    'dp[i]（长度）和 count[i]（方案数）。两者同时更新')
add_basic(d, '何时累加 count？',
    'nums[j] < nums[i] 时：\n'
    '- dp[j]+1 > dp[i]：count[i] = count[j]（更长，重置）\n'
    '- dp[j]+1 == dp[i]：count[i] += count[j]（等长，累加）')

# --- 28. 分割等和子集 ---
d = make_deck(1747300128, '算法::动态规划::分割等和子集')
add_basic(d, '什么背包模型？',
    '0-1 背包可行性变种。容量 = sum/2，每个元素选一次，问能否恰好装满')
add_cloze(d, 'for(j=target;j>=nums[i];j--) dp[j]={{c1::dp[j] | dp[j-nums[i]]}}',
    '倒序遍历（0-1 背包），或运算（可行性）')
add_basic(d, '为什么必须倒序？',
    '正序会导致同一元素被重复使用。如 [2,2,3,5] 找 6：正序 dp[6] 会被误判 true')

# --- 29. 完全平方数 ---
d = make_deck(1747300129, '算法::动态规划::完全平方数')
add_basic(d, '什么背包类型？', '完全背包求最小值。dp[i] = 和为 i 的最少平方数个数')
add_cloze(d, 'dp[i] = min(dp[i], {{c1::dp[i-j*j]+1}})，j*j<=i',
    '完全背包正序遍历')
add_basic(d, '四平方和定理？', '任何正整数最多用 4 个完全平方数。若 n=4^a*(8b+7)，最少需 4 个')

# --- 30. 整数拆分 ---
d = make_deck(1747300130, '算法::动态规划::整数拆分')
add_cloze(d, 'dp[i]=max(dp[i], max({{c1::j*(i-j)}}, {{c2::j*dp[i-j]}}))',
    '拆成两个数 或 继续拆更多个数')
add_basic(d, '数学结论？', '尽量拆 3。余 0 全 3，余 1 改 3^(a-1)*4，余 2 加个 2')

# --- 31. 把数字翻译成字符串 ---
d = make_deck(1747300131, '算法::动态规划::把数字翻译成字符串')
add_basic(d, '与解码方法的区别？', '翻译中 0→a 有效，两位数范围 10-25，无需特殊处理 0')
add_cloze(d, 'if(10<=temp<=25) dp[i]={{c1::dp[i-1]+dp[i-2]}}; else dp[i]={{c2::dp[i-1]}}',
    '与爬楼梯同模型')

# --- 32. 掷骰子 ---
d = make_deck(1747300132, '算法::动态规划::掷骰子')
add_basic(d, '问题变量？', 'n 个骰子、m 面、目标和 target。dp[i][j] = 前 i 个骰子和为 j 的方案数')
add_cloze(d, 'dp[i][j] = sum(dp[i-1][{{c1::j-k}}]), k=1..min(m,j)', '三重循环。n*m<target 直接 return 0')

# --- 33. 连续子数组最大和-精简 ---
d = make_deck(1747300133, '算法::动态规划::连续子数组的最大和-精简')
add_cloze(d, '原地 DP：nums[i] += max({{c1::nums[i-1]}}, 0); res = max(res, {{c2::nums[i]}})',
    '利用原数组就地修改，O(1) 额外空间')

# --- 34. 青蛙跳台阶 ---
d = make_deck(1747300134, '算法::动态规划::青蛙跳台阶')
add_basic(d, '与爬楼梯的关系？', '同一道题。青蛙跳 1 或 2 级 = 爬楼梯。f(n)=f(n-1)+f(n-2)')

# --- 35. 青蛙跳台阶 II (1~n级) ---
d = make_deck(1747300135, '算法::动态规划::青蛙跳台阶II')
add_basic(d, '递推公式？', 'f(n)=2*f(n-1)，等比数列公比 2。f(1)=1')
add_cloze(d, '答案公式：f(n) = {{c1::2^(n-1)}}', '等比数列通项')

# --- 36. 斐波那契数列 ---
d = make_deck(1747300136, '算法::动态规划::斐波那契数列')
add_basic(d, 'DP vs 递归？', 'DP O(n) O(1)；递归 O(2^n) 指数爆炸，n=50 几乎跑不完')

# --- 37. 斐波那契数 ---
d = make_deck(1747300137, '算法::动态规划::斐波那契数')
add_basic(d, '和爬楼梯的关系？', '爬楼梯 n 阶 = 斐波那契第 n 项。初始值略有不同' + img('image 33.png'))

# ============================================================
# Export with images
# ============================================================

total = sum(len(d.notes) for d in ALL_DECKS)
pkg = genanki.Package(ALL_DECKS)
pkg.media_files = list(USED_IMAGES)

out = '../../牌组/动态规划.apkg'
pkg.write_to_file(out)
print(f'Done: {len(ALL_DECKS)} decks, {total} cards, {len(USED_IMAGES)} images -> {out}')
