# 和可被 K 整除的子数组

## 题干
给定一个整数数组 nums 和一个整数 k，返回其中元素之和可被 k 整除的（连续、非空）子数组的数目。
![image 1.png](image%201.png)

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(min(n,k))}} — HashMap 存余数

## 关键技巧
同余定理：若 preSum[j] 和 preSum[i-1] 对 k 同余，则区间和可被 k 整除。
关键：负数的余数处理 — Java中 -1%5=-1，需转化为正余数：(k - (-sum)%k) % k
统计方法：遍历完后再按组合数公式 C(m,2) 计算，而非边遍历边算。

## 题解(前缀和+余数)
同余定理：若 preSum[j] 和 preSum[i-1] 对 k 同余，则区间和可被 k 整除。组合数 C(m,2) 计算。

```java
class Solution {
    public int subarraysDivByK(int[] nums, int k) {
        Map<Integer, Integer> map = new LinkedHashMap<>();
        int sum = 0;
        for(int i = 0; i < nums.length; i++){
            sum += nums[i];
            int mod = sum >= 0 ? sum % k : (k - (-sum) % k) % k;
            if(map.containsKey(mod))
                map.put(mod, map.get(mod) + 1);
            else
                map.put(mod, 1);
        }
        int res = 0;
        for (Map.Entry<Integer, Integer> item : map.entrySet()) {
            res += item.getValue() * (item.getValue() - 1) / 2;
            if(item.getKey() == 0)
                res += item.getValue();
        }
        return res;
    }
}
```
