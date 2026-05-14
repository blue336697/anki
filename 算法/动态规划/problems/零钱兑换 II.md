# 零钱兑换 II

## 题干
题干：给你整数数组 `coins` 和总金额 `amount`，返回可以凑成总金额的 **组合数**（硬币无限使用，顺序不同算同一种组合）。

题目描述

给你整数数组 coins 和总金额 amount，
求可以凑成总金额的组合数。
硬币无限使用，顺序不同算同一种组合。

示例
输入：coins = [1,2,5], amount = 5
输出：4
解释：四种组合
1+1+1+1+1
1+1+1+2
1+2+2
5

动态规划-完全背包 求组合数

- dp[i]：凑金额 i 的方案数
- 初始化：dp[0] = 1
- 转移：dp[i] += dp[i - coin]



## 定义状态
dp[i] = {{c1::凑金额 i 的组合数}}
> 完全背包求组合数

## 转移方程
dp[j] = {{c1::dp[j] + dp[j-coin]}}
> 从求最小值变成求方案数累加

## 初始化
dp[0] = {{c1::1}}
> 凑 0 元有一种方案：什么都不选

## 计算顺序
外层硬币，内层金额正序遍历。<b>外层硬币内层金额</b>保证组合数（非排列数），避免 [1,2] 和 [2,1] 重复计数。

## 返回结果
返回 dp[amount]。

## 复杂度
- 时间 O(n×amount)：完全背包求方案数。外层n种硬币，内层amount个金额（正序） → O(n×amount)<br>- 空间 O(amount)：一维dp数组长度amount+1，dp[j]+=dp[j-coin]

## 题解
组合数：dp[j] = dp[j] + dp[j-coin]。dp[0]=1 是关键。外层硬币内层金额保证组合非排列。
```java
class Solution {
    public int change(int amount, int[] coins) {
        int len = coins.length;
        if (len == 0) {
            if (amount == 0) return 1;
            return 0;
        }
        int[] dp = new int[amount + 1];
        dp[0] = 1;
        for (int i = coins[0]; i &lt;= amount; i += coins[0])
            dp[i] = 1;
        for (int i = 1; i &lt; len; i++) {
            for (int j = 0; j &lt;= amount; j++) {
                if (j - coins[i] &gt;= 0)
                    dp[j] = dp[j] + dp[j - coins[i]];
            }
        }
        return dp[amount];
    }
}
```
