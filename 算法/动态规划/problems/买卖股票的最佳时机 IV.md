# 买卖股票的最佳时机 IV

## 题干
题干：给定整数 `k` 和数组 `prices`，你最多可以完成 `k` 笔交易（同一时间只能持有一股），返回最大利润。


## 定义状态
dp[i][j][k]：第 i 天，j = {{c1::是否持股}}，k = {{c2::已交易次数}}<br>k = min(k, {{c3::len/2}})
> k 超过 len/2 等价于无限次交易（退化为 II）

## 转移方程
dp[i][0][j] = max(dp[i-1][1][j]+prices[i], dp[i-1][0][j])<br>dp[i][1][j] = max({{c1::dp[i-1][0][j-1]-prices[i]}}, dp[i-1][1][j])
> IV 与 III 相反：买入时 j-1（买入算一次交易），卖出时 j 不变

## 初始化
dp[0][0][0] = 0, dp[0][1][0] = {{c1::-prices[0]}}<br>其余所有状态初始化为 {{c2::MIN_VALUE/2}}
> 除 2 防止 -MIN_VALUE+1 溢出变成正数

## 计算顺序
i 从 1 到 len-1，j 从 1 到 k 双重循环。<br>注意 k 需预处理：k = min(k, len/2)。

## 返回结果
返回 dp[len-1][0][k]（最后一天不持股、最多 k 次交易的最大利润）。

## 复杂度
- 时间 O(n×k)：外层遍历n天，内层遍历k次交易 → n×k次状态转移。当k≥n/2时等效于无限交易，实际退化为O(n)<br>- 空间 O(k)：buy和sell两个长度为k+1的数组滚动更新。优化技巧：k=min(k, n/2)预处理

## 题解
买入时交易次数+1（与 III 相反：III 是卖出时+1）。k 需预处理 min(k, len/2)。
```java
class Solution {
    public int maxProfit(int k, int[] prices) {
        int len = prices.length;
        int min = Integer.MIN_VALUE / 2;
        if (len &lt; 2) return 0;
        int[][][] dp = new int[len][2][k + 1];
        k = Math.min(k, len / 2);
        for (int i = 1; i &lt;= k; i++) {
            dp[0][0][i] = 0;
            dp[0][1][i] = -prices[0];
        }
        for (int i = 1; i &lt; len; i++) {
            for (int j = 1; j &lt;= k; j++) {
                dp[i][0][j] = Math.max(dp[i-1][1][j] + prices[i], dp[i-1][0][j]);
                dp[i][1][j] = Math.max(dp[i-1][0][j-1] - prices[i], dp[i-1][1][j]);
            }
        }
        return dp[len-1][0][k];
    }
}
```
