# 打家劫舍 II

## 题干
题干：房屋首尾相连成环，给定数组 `nums`，相邻房屋不能同晚被偷，返回能偷到的最大金额。


- 如果要将第一个房子算上，那么不能将最后一个房子算上
- 反之同理

> 那我们就分两次来求，看那次大就行了
> 


## 定义状态
与 I 完全相同，dp[i] = {{c1::偷前 i 间房子的最大金额}}
> 关键是处理好环形约束

## 转移方程
dp[i] = max(dp[i-1], {{c1::nums[i-1] + dp[i-2]}})
> 转移方程与 I 完全一样

## 初始化
dp[0] = 0, dp[1] = {{c1::nums[0]}}（同 I）
> 两次调用 dp 方法，传入不同数组范围

## 计算顺序
分两种情况各跑一次打家劫舍 I：<br>1. 不偷第一家：nums[1..end]<br>2. 不偷最后一家：nums[0..end-1]<br>取 max。

## 返回结果
返回 max(dp(nums[0..n-2]), dp(nums[1..n-1]))。<br>特殊情况：n==1 直接返回 nums[0]。

## 复杂度
- 时间 O(n)：分两段分别DP：[0,n-2]和[1,n-1]各一次 → 2n = O(n)<br>- 空间 O(1)：每段只用两个滚动变量<br>核心思路：环形问题不能同时偷首尾 → 去掉头或尾 → 两次线性DP取max

## 题解
环形 DP 通用套路：拆为两个线性 DP，去头或去尾各跑一次取 max。
```java
class Solution {
    public int rob(int[] nums) {
        if (nums == null || nums.length == 0)
            return 0;
        if (nums.length == 1)
            return nums[0];
        return Math.max(dp(Arrays.copyOfRange(nums, 0, nums.length - 1)),
                        dp(Arrays.copyOfRange(nums, 1, nums.length)));
    }

    public int dp(int[] nums) {
        int[] dp = new int[nums.length + 1];
        dp[0] = 0;
        dp[1] = nums[0];
        for (int i = 2; i &lt;= nums.length; i++) {
            dp[i] = Math.max(dp[i - 1], nums[i - 1] + dp[i - 2]);
        }
        return dp[nums.length];
    }
}
```
