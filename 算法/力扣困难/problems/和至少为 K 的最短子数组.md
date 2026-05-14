# 和至少为 K 的最短子数组

## 题干
给你一个整数数组 nums 和一个整数 k，找出 nums 中和至少为 k 的最短非空子数组，并返回该子数组的长度。如果不存在这样的子数组，返回 -1。
注意：nums 中可能包含负数，因此不能使用普通滑动窗口。

## 复杂度
时间：{{c1::O(n)}} — 一次遍历+单调队列
空间：{{c1::O(n)}} — 前缀和+队列

## 关键技巧
为什么不能用普通滑动窗口？因为 nums[i] 可能为负，右指针右移不保证区间和增大，左指针右移不保证区间和减小（无二段性）。
正确解法：前缀和 + 单调递增队列。
1. 计算前缀和 prefix[i]
2. 队列维护 prefix 值的递增序列（若 prefix[i] <= 队尾，则队尾的值永无机会成为最优左边界）
3. 队首满足 prefix[i]-prefix[q.peek()] >= k 则更新答案并弹出（后续更长的子数组不可能是最优）

## 题解(前缀和+单调队列)
前缀和 + 单调递增队列：prefix[i] 维护递增序列，队首满足条件则更新答案。

```java
class Solution {
    public int shortestSubarray(int[] nums, int k) {
        int len = nums.length;
        int[] prefix = new int[len + 1];
        for(int i = 0; i < len; i++){
            prefix[i+1] = prefix[i] + nums[i];
            if(nums[i] >= k)
                return 1;
        }
        int res = Integer.MAX_VALUE;
        Deque<Integer> queue = new ArrayDeque<>();
        for(int i = 0; i < prefix.length; i++){
            while(!queue.isEmpty() && prefix[i] <= prefix[queue.getLast()])
                queue.removeLast();
            while(!queue.isEmpty() && prefix[i] - prefix[queue.peek()] >= k)
                res = Math.min(res, i - queue.poll());
            queue.add(i);
        }
        return res == Integer.MAX_VALUE ? -1 : res;
    }
}
```
