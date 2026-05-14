# 掷骰子的N种方法

## 题干
题干：有 `n` 个 `m` 面骰子（点数为 `1..m`），给定整数 `target`，返回掷出点数和为 `target` 的方案数（通常对 `1e9+7` 取模）。



## 定义状态
dp[i][j] = {{c1::前 i 个骰子和为 j 的方案数}}
> 分组背包：每个骰子是一个分组，掷出 1~m 点

## 转移方程
dp[i][j] = sum(dp[i-1][{{c1::j-k}}]), k=1..min(m,j)
> 三重循环：骰子 × 容量 × 决策

## 初始化
dp[0][0] = {{c1::1}}
> 0 个骰子和为 0 有 1 种方案

## 计算顺序
i 从 1 到 n，j 从 0 到 target，k 从 1 到 min(m,j)。<br>一维优化需倒序 j：dp[j] = sum(dp[j-k])，且每轮开始 dp[j]=0 重置。

## 返回结果
返回 dp[n][target] % MOD。<br>剪枝：若 n*m < target 直接返回 0（不可能达到）。

## 复杂度
- 时间 O(n×k×target)：三重循环 → n个骰子 × target个和值 × k个面（1~k枚举） → O(n×k×target)<br>- 空间 O(target)：dp[i][j]只依赖dp[i-1]行 → 保留两行长度target+1交替 → O(target)

## 题解(二维DP)
分组背包三重循环：骰子 i、容量 j、决策 k（1~m）。
```java
class Solution {
    private static final int MOD = (int) 1e9 + 7;
    public int numRollsToTarget(int n, int m, int target) {
        if (n * m &lt; target) return 0;
        int[][] dp = new int[n + 1][target + 1];
        dp[0][0] = 1;
        for (int i = 1; i &lt;= n; i++) {
            for (int j = 0; j &lt;= target; j++) {
                for (int k = 1; j - k &gt;= 0 && k &lt;= m; k++)
                    dp[i][j] = (dp[i][j] + dp[i - 1][j - k]) % MOD;
            }
        }
        return dp[n][target];
    }
}
```
