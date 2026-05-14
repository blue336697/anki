# 数组中的第K个最大元素

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
时间 {{c1::O(n log n)}}
推导：建堆O(n)，但k次heapify每次O(log n) → 实际k次调整即O(k log n)，最坏k=n时为O(n log n)
空间 {{c1::O(1)}}
推导：原地建堆，全部操作在原数组上进行
