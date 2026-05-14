# 买卖股票的最佳时机 III

## 题干
题干：给定数组 `prices`，你最多可以完成 **2 笔交易**（同一时间只能持有一股），返回最大利润。





## 定义状态
dp[i][j][k]：第 i 天，j = {{c1::是否持股(0/1)}}，k = {{c1::已卖出次数(0/1/2)}}
> 新增卖出次数维度 k，从 0 到 2

## 转移方程
不持股已卖k次：max({{c1::dp[i-1][1][k-1]+prices[i]}}, {{c1::dp[i-1][0][k]}})<br>持股已卖k次：max({{c1::dp[i-1][0][k]-prices[i]}}, {{c1::dp[i-1][1][k]}})
> III 中卖出时 k+1（依赖 k-1），买入时 k 不变

## 初始化
dp[0][0][0] = {{c1::0}}, dp[0][1][0] = {{c1::-prices[0]}}<br>dp[0][0][1]=dp[0][0][2]=dp[0][1][1]=dp[0][1][2] = {{c1::MIN_VALUE/2}}
> 第一天不可能已卖出或多次交易，设为负无穷

## 计算顺序
i 从 1 到 len-1 正序遍历。共 6 种状态（持股×卖出次数），每一轮更新所有状态。

## 返回结果
返回 max(dp[len-1][0][1], dp[len-1][0][2], 0)。<br>可能卖出 1 次或 2 次获利最大，也可能不交易。

## 复杂度
- 时间 O(n)：每天有6种状态（持股/不持股 × 已卖出0/1/2次），状态数固定为6不随n增长，每步O(1) → O(n)<br>- 空间 O(1)：dp[i]只依赖dp[i-1]的6个状态值，用6个变量滚动即可

## 题解
卖出时交易次数+1。6 种状态：持股/不持股 × 已卖0/1/2次。
```java
class Solution {
    public int maxProfit(int[] prices) {
        int len = prices.length;
        int min = Integer.MIN_VALUE / 2;
        if (len &lt; 2) return 0;
        int[][][] dp = new int[len][2][3];
        dp[0][0][0] = 0;
        dp[0][1][0] = -prices[0];
        dp[0][0][1] = min;
        dp[0][0][2] = min;
        dp[0][1][1] = min;
        dp[0][1][2] = min;
        for (int i = 1; i &lt; len; i++) {
            dp[i][0][0] = 0;
            dp[i][0][1] = Math.max(dp[i-1][1][0] + prices[i], dp[i-1][0][1]);
            dp[i][0][2] = Math.max(dp[i-1][1][1] + prices[i], dp[i-1][0][2]);
            dp[i][1][0] = Math.max(dp[i-1][0][0] - prices[i], dp[i-1][1][0]);
            dp[i][1][1] = Math.max(dp[i-1][0][1] - prices[i], dp[i-1][1][1]);
            dp[i][1][2] = min;
        }
        return Math.max(Math.max(dp[len-1][0][1], dp[len-1][0][2]), 0);
    }
}
```
