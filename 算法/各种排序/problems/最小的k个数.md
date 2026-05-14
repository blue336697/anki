# 最小的k个数

## 题干
输入整数数组 arr，找出其中最小的 k 个数。以任意顺序返回这 k 个数即可。

## 关键技巧
QuickSelect改造partition：确定基准位置i后与k比较决定递归方向
i > k → 答案在左区间；i < k → 还需在右区间找；i == k → 返回前k个
QuickSelect平均O(n)优于堆的O(n log k)，注意必须先从右往左扫描
大顶堆法比小顶堆更高效（只存k个，空间小）

## 题解(QuickSelect)
改造快排partition：确定基准位置i后与k比较决定递归方向。

```java
class Solution {
    public int[] getLeastNumbers(int[] arr, int k) {
        if (k >= arr.length) return arr;
        return quickSelect(arr, 0, arr.length - 1, k);
    }

    private int[] quickSelect(int[] arr, int left, int right, int k) {
        int i = left, j = right;
        while (i < j) {
            // 必须先从右向左扫描
            while (i < j && arr[left] <= arr[j]) j--;
            while (i < j && arr[left] >= arr[i]) i++;
            swap(arr, i, j);
        }
        swap(arr, left, i);
        if (i > k)
            return quickSelect(arr, left, i - 1, k);
        if (i < k)
            return quickSelect(arr, i + 1, right, k);
        return Arrays.copyOf(arr, k);
    }

    private void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```

## 题解(大顶堆)
大顶堆维护size=k，堆顶是当前k个最小数中最大的。

```java
class Solution {
    public int[] getLeastNumbers(int[] arr, int k) {
        if (k == 0) return new int[0];
        PriorityQueue<Integer> heap = new PriorityQueue<>((a, b) -> b - a);
        for (int num : arr) {
            if (heap.size() < k) {
                heap.offer(num);
            } else if (num < heap.peek()) {
                heap.poll();
                heap.offer(num);
            }
        }
        int[] res = new int[k];
        for (int i = 0; i < k; i++) res[i] = heap.poll();
        return res;
    }
}
```

## 复杂度(QuickSelect)
QuickSelect法：
时间 平均 {{c1::O(n)}}，最坏 {{c1::O(n²)}}
推导(平均)：每次partition减少一半搜索范围 → n + n/2 + n/4 + ... < 2n = O(n)
推导(最坏)：每次只排除一个元素(如已排序数组) → n + (n-1) + ... + 1 = O(n²)
空间 {{c1::O(log n)}}
推导：递归栈深度，每次减半→log n层

## 复杂度(大顶堆)
大顶堆法：
时间 {{c1::O(n log k)}}
推导：遍历n个元素，堆大小k，每次调整O(log k) → n log k
空间 {{c1::O(k)}}
推导：堆中最多存k+1个元素
