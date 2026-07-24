# 前 K 个高频元素
<!-- aliases: 按频率和字典序TopK单词 -->
<!-- tags: source::leetcode source::字节 pattern::TopK -->

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
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

class Solution {
    public int[] topKFrequent(int[] nums, int k) {
        int[] res = new int[k];
        Map<Integer, Integer> map = new HashMap<>();
        for (int num : nums) {
            map.put(num, map.getOrDefault(num, 0) + 1);
        }
        PriorityQueue<Map.Entry<Integer, Integer>> queue =
                new PriorityQueue<>(
                        (a, b) -> Integer.compare(a.getValue(), b.getValue()));
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
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public int[] topKFrequent(int[] nums, int k) {
        int len = nums.length;
        List<Integer> res = new ArrayList<>();
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

## 字节变形：按频率和字典序 TopK 单词
给定单词数组和 k，返回频率最高的 k 个单词；频率相同时按字典序升序输出。

仍使用大小为 k 的小根堆，但堆顶必须是“最应该被淘汰”的元素：

1. 频率更低的单词优先出堆
2. 频率相同时，字典序{{c1::更大}}的单词优先出堆

因此堆内比较器在同频时使用 `second.compareTo(first)`。最终从堆顶弹出的顺序是答案的逆序，可用 `addFirst` 反向收集。

设输入单词总数为 n，不同单词数为 m：统计 O(n)，m 次堆操作 O(m log k)，空间 O(m+k)。

## 题解(TopK 单词)
```java
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

class Solution {
    public List<String> topKFrequent(String[] words, int k) {
        Map<String, Integer> frequency = new HashMap<>();
        for (String word : words) {
            frequency.merge(word, 1, Integer::sum);
        }

        PriorityQueue<String> topK = new PriorityQueue<>((first, second) -> {
            int frequencyOrder =
                    Integer.compare(frequency.get(first), frequency.get(second));
            if (frequencyOrder != 0) {
                return frequencyOrder;
            }
            return second.compareTo(first);
        });

        for (String word : frequency.keySet()) {
            topK.offer(word);
            if (topK.size() > k) {
                topK.poll();
            }
        }

        LinkedList<String> answer = new LinkedList<>();
        while (!topK.isEmpty()) {
            answer.addFirst(topK.poll());
        }
        return answer;
    }
}
```
