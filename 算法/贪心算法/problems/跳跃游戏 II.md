# 跳跃游戏 II

## 题干
给定一个非负整数数组 nums，你最初位于数组的第一个下标。数组中的每个元素代表你在该位置可以跳跃的最大长度。返回到达最后一个下标的最小跳跃次数。
![image.png](image.png)

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(1)}}

## 题解(贪心 BFS层扩展)
BFS式的层扩展：每次在当前跳跃范围 [start, end] 内找下一跳的最远位置。

```java
class Solution {
    public int jump(int[] nums) {
        // 无论怎么样第一次起跳的起点都是第一个，
        // 然后根据第一个的跳跃距离，在第二次起跳的距离里面选最大的
        // 例如：[2,3,1,1,4]，第一次最多能跳两格，所以第二次起跳的起点可以是3或者1
        // 在第二次开始就要贪心选跳最远的，所以肯定选3
        int start = 0, end = 0, n = nums.length, res = 0;

        while (end < n - 1) {
            int maxPos = 0;
            for (int k = start; k <= end; k++) {
                // k + nums[k]：当前位置+最大的跳动距离就是最后的落点
                maxPos = Math.max(k + nums[k], maxPos);
            }
            // 下一次起跳范围的起点
            start = end + 1;
            // 下一次起跳范围的终点
            end = maxPos;
            res++;
        }
        return res;
    }
}
```

## 题解(贪心 优化)
优化：一次遍历，当 i == end 时表示当前层结束，步数+1。

```java
class Solution {
    public int jump(int[] nums) {
        int end = 0, res = 0, maxPos = 0;
        // 这里之所以不让 i 等于最后一个，会在已经到达终点的情况下重复计算一次
        for (int i = 0; i < nums.length - 1; i++) {
            maxPos = Math.max(maxPos, i + nums[i]);

            if (end == i) {
                end = maxPos;
                res++;
            }
        }
        return res;
    }
}
```
