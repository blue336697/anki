# 前 K 个高频元素

## 题干
给你一个整数数组 nums 和一个整数 k，请你返回其中出现频率前 k 高的元素。你可以按任意顺序返回答案。

## 复杂度
优先队列：时间 {{c1::O(n log k)}}，空间 {{c1::O(n)}}
桶排序：时间 {{c1::O(n)}}，空间 {{c1::O(n)}}

## 关键技巧
两种解法取舍：
1. 小根堆 O(n log k)：适合 k 很小的情况，只维护 k 个元素
2. 桶排序 O(n)：适合 k 接近 n 的情况，不需要排序
小根堆为什么不能换成大根堆？因为出队只能从堆顶，大根堆会把频率最高的出掉。

## 题解(优先队列-小根堆)
用小根堆维护大小为k，堆顶是最小频率，遍历完后堆中留下的就是前k高。

```java
class Solution {
    public int[] topKFrequent(int[] nums, int k) {
        int[] res = new int[k];
        Map<Integer, Integer> map = new HashMap<>();
        for (int num : nums) {
            map.put(num, map.getOrDefault(num, 0) + 1);
        }
        Set<Map.Entry<Integer, Integer>> entries = map.entrySet();
        PriorityQueue<Map.Entry<Integer, Integer>> queue = new PriorityQueue<>((a, b) -> a.getValue() - b.getValue());
        for(Map.Entry<Integer, Integer> entry: map.entrySet()){
            queue.offer(entry);
            if(queue.size() > k)
                queue.poll();
        }
        for (int i = k - 1; i >= 0; i--) {
            res[i] = queue.poll().getKey();
        }
        return res;
    }
}
```

## 题解(桶排序)
以频率作为数组下标（桶），频率相同的放同一桶，从高到低取前k个。

```java
class Solution {
    public int[] topKFrequent(int[] nums, int k) {
        int len = nums.length;
        List<Integer> res = new ArrayList();
        Map<Integer, Integer> map = new HashMap<>();
        for(int num : nums){
            map.put(num, map.getOrDefault(num, 0) + 1);
        }
        List<Integer>[] buckets = new List[nums.length+1];
        for(int key : map.keySet()){
            int count = map.get(key);
            if(buckets[count] == null)
                buckets[count] = new ArrayList<>();
            buckets[count].add(key);
        }
        for(int i = buckets.length - 1; i >= 0 && res.size() < k; i--){
            if(buckets[i] == null)
                continue;
            res.addAll(buckets[i]);
        }
        int[] res01 = new int[k];
        for(int i = 0; i < res.size(); i++){
            res01[i] = res.get(i);
        }
        return res01;
    }
}
```
