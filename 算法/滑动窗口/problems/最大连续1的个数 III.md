# 最大连续1的个数 III

## 题干
给定一个由若干 0 和 1 组成的数组 A，最多可以将 K 个 0 变成 1，返回仅包含 1 的最长连续子数组的长度。

## 指针策略
题意转化：窗口中最多允许 {{c1::K 个 0}}
right移动：{{c1::每次遍历 end++，遇到 0 则 zero++}}
left移动：{{c1::while(zero > K)}} 收缩 start，遇到 0 则 zero--
更新结果：{{c1::每次循环都更新 res = max(res, end-start+1)}}

## 复杂度
时间：{{c1::O(n)}} — 每个元素最多访问两次
空间：{{c1::O(1)}}

## 题解(滑动窗口)
题意转化为窗口中最多 K 个 0，超过 K 时收缩左边界。

```java
class Solution {
    public int longestOnes(int[] nums, int k) {
        int len = nums.length;
        if (len == 0)
            return 0;
        int zero = 0, res = 0, start = 0;
        for (int end = 0; end < len; end++) {
            if (nums[end] == 0)
                zero++;
            while (zero > k) {
                if (nums[start++] == 0)
                    zero--;
            }
            res = Math.max(res, end - start + 1);
        }
        return res;
    }
}
```
