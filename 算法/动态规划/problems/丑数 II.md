# 丑数 II

## 题干
题干：丑数是只包含质因子 2、3、5 的正整数。给定整数 `n`，返回第 `n` 个丑数。



## 定义状态
dp[i] = {{c1::第 i 个丑数}}<br>三个指针 p2, p3, p5 = {{c2::各自指向待乘的丑数下标}}
> 三指针分别追踪乘 2/3/5 的基数

## 转移方程
dp[i] = min({{c1::2*dp[p2]}}, {{c2::3*dp[p3]}}, {{c3::5*dp[p5]}})
> 取三个候选的最小值作为下一个丑数

## 初始化
dp[1] = {{c1::1}}（第一个丑数是 1）<br>p2 = p3 = p5 = {{c2::1}}
> 三个指针从 1 开始

## 计算顺序
i 从 2 到 n。计算 num2/num3/num5，取 min 为 dp[i]。<br>关键：所有 dp[i] 相等的指针都要移动（去重，如 6=2*3=3*2）。

## 返回结果
返回 dp[n]（第 n 个丑数）。

## 复杂度
- 时间 O(n)：生成n个丑数，每次取min(dp[p2]×2, dp[p3]×3, dp[p5]×5)，移动被选中的指针 → n×O(1)=O(n)<br>- 空间 O(n)：dp数组存储n个丑数。dp天然有序，下一个丑数一定是之前某个丑数×质因子的最小值

## 题解
三指针分别乘 2/3/5，取最小值。去重关键：用 if 而非 else-if，相等指针都移动。
```java
class Solution {
    public int nthUglyNumber(int n) {
        int[] dp = new int[n + 1];
        dp[1] = 1;
        int ptr2 = 1, ptr3 = 1, ptr5 = 1;
        for (int i = 2; i &lt;= n; i++) {
            int num2 = 2 * dp[ptr2], num3 = 3 * dp[ptr3], num5 = 5 * dp[ptr5];
            dp[i] = Math.min(Math.min(num2, num3), num5);
            if (dp[i] == num2) ptr2++;
            if (dp[i] == num3) ptr3++;
            if (dp[i] == num5) ptr5++;
        }
        return dp[n];
    }
}
```
