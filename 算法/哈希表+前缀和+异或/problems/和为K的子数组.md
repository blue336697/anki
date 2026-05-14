# 和为K的子数组

## 题干
给你一个整数数组 nums 和一个整数 k，请你统计并返回该数组中和为 k 的连续子数组的个数。注意：数组中有负数，不能用滑动窗口。

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(n)}} — HashMap 存前缀和

## 关键技巧
核心转化：区间和 = k → preSum[j] - preSum[i-1] = k → preSum[i-1] = preSum[j] - k
HashMap 的 key 存前缀和，value 存该前缀和出现的次数。
初始化 map.put(0,1) 处理从索引 0 开始的子数组。
注意：需要先 containsKey 检查再 put 当前 preSum（不能反过来），避免 k=0 时重复计数。

## 题解(前缀和+HashMap)
preSum[j] - preSum[i-1] = k → preSum[i-1] = preSum[j] - k，找之前有多少个前缀和等于 preSum-k。

```java
class Solution {
    public int subarraySum(int[] nums, int k) {
        if(nums == null || nums.length == 0)
            return 0;
        Map<Integer, Integer> map = new HashMap<>();
        map.put(0, 1);
        int preSum = 0;
        int count = 0;
        for(int num : nums){
            preSum += num;
            if(map.containsKey(preSum - k))
                count += map.get(preSum - k);
            map.put(preSum, map.getOrDefault(preSum, 0) + 1);
        }
        return count;
    }
}
```
