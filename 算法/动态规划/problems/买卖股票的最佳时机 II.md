# 买卖股票的最佳时机 II

## 题干
题干：给定数组 `prices`，你可以完成 **任意多笔交易**（同一时间只能持有一股；卖出后才能再次买入），返回最大利润。







## 定义状态
dp[i][0] = {{c1::第 i 天不持股的最大现金}}<br>dp[i][1] = {{c2::第 i 天持股的最大现金}}
> 与 I 的状态定义完全相同

## 转移方程
dp[i][0] = max(dp[i-1][0], {{c1::dp[i-1][1]+prices[i]}})<br>dp[i][1] = max(dp[i-1][1], {{c2::dp[i-1][0]-prices[i]}})
> 不限制交易次数：买入时可用之前卖出赚的钱（dp[i-1][0]）

## 初始化
dp[0][0] = {{c1::0}}, dp[0][1] = {{c2::-prices[0]}}
> 同 I

## 计算顺序
i 从 1 到 len-1 正向遍历。与 I 的唯一代码区别：买入时用 dp[i-1][0]-prices[i] 而非 -prices[i]。

## 返回结果
返回 dp[len-1][0]（最后一天不持股的最大现金）。

## 复杂度
<b>DP（状态机）</b>：<br>- 时间 O(n)：遍历一次，与I的唯一区别是买入时用dp[i-1][0]-prices[i]（而非-prices[i]），允许用之前的利润再买入 → O(n)<br>- 空间 O(1)：滚动优化后只需hold和notHold两个变量<br><br><b>贪心</b>：只要prices[i]>prices[i-1]就累加差价，等价于无限次交易<br>- 时间 O(n) / 空间 O(1)

## 题解(DP)
与 I 的唯一区别：买入时用 dp[i-1][0]-prices[i] 而非 -prices[i]。
```java
class Solution {
    public int maxProfit(int[] prices) {
        int len = prices.length;
        if (len &lt; 2) return 0;
        int[][] dp = new int[len][2];
        dp[0][0] = 0;
        dp[0][1] = -prices[0];
        for (int i = 1; i &lt; len; i++) {
            dp[i][0] = Math.max(dp[i - 1][0], dp[i - 1][1] + prices[i]);
            dp[i][1] = Math.max(dp[i - 1][1], dp[i - 1][0] - prices[i]);
        }
        return dp[len - 1][0];
    }
}
```

## 题解(贪心)

