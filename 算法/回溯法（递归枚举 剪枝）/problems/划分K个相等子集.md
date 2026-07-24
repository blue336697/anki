# 划分K个相等子集

## 题干
给定一个正整数数组 `nums` 和整数 `k`，判断能否把全部元素恰好划分成 `k` 个非空子集，使每个子集的元素和相等。每个数组元素只能使用一次。

## 必要条件
设总和为 `sum`，每个桶的目标和为 `target = sum / k`：

- `k` 必须满足 {{c1::1 <= k <= nums.length}}，否则无法得到 k 个非空子集
- `sum % k` 必须为 {{c1::0}}
- 降序排序后，最大元素不能大于 {{c1::target}}

这些条件只能快速排除不可能情况，不能单独证明一定可以划分。

## 搜索状态
`usedMask` 的第 i 位表示{{c1::nums[i] 是否已经放入某个桶}}。
`bucketSum` 表示{{c1::当前正在填充的桶的元素和}}。
`bucketsLeft` 表示{{c1::包括当前桶在内还未完成的桶数}}。

当前桶达到 `target` 时，开始填下一个空桶。只剩一个桶时可以直接返回 true，因为所有未使用元素的总和必然等于一个 `target`。

## 记忆化为什么只需 usedMask
在正整数前提下，同一个 `usedMask` 对应唯一的已使用元素总和。该总和能唯一确定已经填满多少个桶以及当前桶的 `bucketSum`，因此可只按 `usedMask` 记忆化。

但每次递归都必须从全部未使用元素中选择。旧实现一边按 `usedMask` 缓存，一边使用会变化的 `start` 限制候选范围，使“相同 mask”的搜索空间可能不同，缓存语义不完整。

## 剪枝
降序排序：{{c1::让大数优先入桶，更早触发超出 target 的失败}}。
同层相同值去重：{{c1::本层尝试过某个数值并失败后，不再尝试另一个相同数值}}。
空桶首元素失败后停止：桶彼此没有编号，{{c1::空桶里更换另一个首元素只是在交换桶的标签}}；降序下固定最大的未使用元素属于某个桶即可。

## 复杂度
状态压缩记忆化最多有 `2^n` 个掩码，每个状态最多枚举 n 个元素。
时间上界：{{c1::O(n · 2^n)}}。
空间：{{c1::O(2^n + n)}} — 记忆化数组与递归栈。

## 题解(状态压缩回溯)
该实现适用于本题常见的 `n <= 16` 约束，因此使用 `int` 位掩码。

```java
import java.util.Arrays;

class Solution {
    private int[] nums;
    private int target;
    private Boolean[] memo;

    public boolean canPartitionKSubsets(int[] nums, int k) {
        if (k <= 0 || k > nums.length) {
            return false;
        }

        int sum = 0;
        for (int value : nums) {
            sum += value;
        }
        if (sum % k != 0) {
            return false;
        }

        target = sum / k;
        Arrays.sort(nums);
        reverse(nums);
        if (nums[0] > target) {
            return false;
        }

        this.nums = nums;
        this.memo = new Boolean[1 << nums.length];
        return dfs(0, 0, k);
    }

    private boolean dfs(int usedMask, int bucketSum, int bucketsLeft) {
        if (bucketsLeft == 1) {
            return true;
        }
        if (bucketSum == target) {
            return dfs(usedMask, 0, bucketsLeft - 1);
        }
        if (memo[usedMask] != null) {
            return memo[usedMask];
        }

        int previous = -1;
        for (int i = 0; i < nums.length; i++) {
            if ((usedMask & (1 << i)) != 0
                    || nums[i] == previous
                    || bucketSum + nums[i] > target) {
                continue;
            }

            int nextMask = usedMask | (1 << i);
            if (dfs(nextMask, bucketSum + nums[i], bucketsLeft)) {
                return memo[usedMask] = true;
            }
            previous = nums[i];

            if (bucketSum == 0) {
                break;
            }
        }
        return memo[usedMask] = false;
    }

    private void reverse(int[] values) {
        for (int left = 0, right = values.length - 1; left < right; left++, right--) {
            int temp = values[left];
            values[left] = values[right];
            values[right] = temp;
        }
    }
}
```
