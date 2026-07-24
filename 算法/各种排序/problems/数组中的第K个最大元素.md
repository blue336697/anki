# 数组中的第K个最大元素
<!-- aliases: 数据流第K大 -->
<!-- tags: source::leetcode source::字节 pattern::TopK -->

## 题干
给定整数数组 nums 和整数 k，返回数组中第 k 个最大的元素。
注意：是排序后的第 k 个最大元素，而非第 k 个不同元素。
![image.png](image.png)

## 关键技巧
小顶堆维护size=k：遍历数组逐个加入，超k则poll最小值，堆顶即第k大
大根堆更贴合语义：建堆后只需k-1次交换+调整，堆顶就是答案
heapify三步：(1)找largest (2)不相等则swap (3)递归向下调整
建堆从len/2-1开始：因为叶子节点(len/2到len-1)已经是单元素堆

## 题解(PriorityQueue 小顶堆)
维护大小为 k 的小顶堆，堆顶即第 k 大。

```java
import java.util.PriorityQueue;

class Solution {
    public int findKthLargest(int[] nums, int k) {
        PriorityQueue<Integer> heap = new PriorityQueue<>();
        for (int num : nums) {
            heap.add(num);
            if (heap.size() > k) {
                heap.poll();
            }
        }
        return heap.peek();
    }
}
```

## 题解(自实现大根堆)
大根堆：天然与"第K大"语义一致，k-1次堆排序后堆顶即答案。

```java
class Solution {
    public int findKthLargest(int[] nums, int k) {
        int len = nums.length;
        // 建大根堆：从最后一个非叶子节点向上调整
        for (int i = len / 2 - 1; i >= 0; i--) {
            heapify(nums, i, len);
        }
        // k-1 次交换+调整，堆顶即第k大
        for (int i = 0; i < k - 1; i++) {
            swap(nums, 0, len - 1 - i);
            heapify(nums, 0, len - 1 - i);
        }
        return nums[0];
    }

    private void heapify(int[] nums, int root, int heapSize) {
        int largest = root;
        int left = 2 * root + 1;
        int right = 2 * root + 2;
        if (left < heapSize && nums[left] > nums[largest])
            largest = left;
        if (right < heapSize && nums[right] > nums[largest])
            largest = right;
        if (largest != root) {
            swap(nums, root, largest);
            heapify(nums, largest, heapSize);
        }
    }

    private void swap(int[] nums, int i, int j) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
}
```

## 复杂度(PriorityQueue)
PriorityQueue小顶堆法：
时间 {{c1::O(n log k)}}
推导：遍历n个元素，每个元素入堆/出堆操作O(log k) → n × log k
空间 {{c1::O(k)}}
推导：堆中最多保留k个元素

## 复杂度(自实现大根堆)
自实现大根堆法：
时间 {{c1::O(n + k log n)}}
推导：Floyd 自底向上建堆 O(n)，之后做 k-1 次交换与向下调整，每次 O(log n)；当 k=n 时最坏 O(n log n)
空间 {{c1::O(1)}}
推导：原地建堆，全部操作在原数组上进行

## 字节变形：数据流第 K 大
初始化时给定 k 和一批初始数字，之后不断调用 `add(value)`，每次都返回当前数据流中的第 k 大元素。

离线数组可以使用快速选择或原地堆；数据流无法预知未来元素，也不能每次重新排序。应长期维护一个大小不超过 k 的小根堆：

- 堆内保存{{c1::当前最大的 k 个元素}}
- 堆顶是这 k 个元素中最小的，因此正好是{{c1::全局第 k 大}}
- 新元素入堆后若大小超过 k，弹出堆顶

单次 `add` 时间 O(log k)，长期空间 O(k)。重复值按出现次数计入排名。

## 题解(数据流小根堆)
```java
import java.util.PriorityQueue;

class KthLargest {
    private final int k;
    private final PriorityQueue<Integer> topK = new PriorityQueue<>();

    public KthLargest(int k, int[] nums) {
        this.k = k;
        for (int value : nums) {
            add(value);
        }
    }

    public int add(int value) {
        topK.offer(value);
        if (topK.size() > k) {
            topK.poll();
        }
        return topK.peek();
    }
}
```
