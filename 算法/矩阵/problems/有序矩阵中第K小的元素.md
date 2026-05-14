# 有序矩阵中第K小的元素

## 题干
给定一个 n x n 矩阵，其中每行和每列元素均按升序排序，找到矩阵中第 k 小的元素。注意：它是排序后的第 k 小元素，而不是第 k 个不同的元素。

## 复杂度
小根堆：时间 {{c1::O(k log n)}}，空间 {{c1::O(n)}} -- 堆中最多 n 行各一个元素

## 关键技巧
归并思想：每行的第一个元素是当前行最小的，用优先队列维护各行当前最小元素的竞争。
队列中存储 (行号, 列号)，比较器用 matrix[row][col] 的值。
每次弹出后，将该行的下一个元素（col+1）入队。弹出 k 次即为答案。

## 题解(小根堆+归并)
小根堆+归并思想：每行第一个入队，每次弹出最小值后该行右移，k-1次后堆顶即答案。

```java
class Solution {
    public int kthSmallest(int[][] matrix, int k) {
        PriorityQueue<int[]> queue = new PriorityQueue<>((n1, n2) ->
            matrix[n1[0]][n1[1]] - matrix[n2[0]][n2[1]]);
        int len = matrix.length;
        for (int i = 0; i < len; i++)
            queue.offer(new int[]{i, 0});
        while (--k > 0) {
            int[] min = queue.poll();
            int x = min[0], y = min[1] + 1;
            if (y < len)
                queue.offer(new int[]{x, y});
        }
        int[] min = queue.poll();
        return matrix[min[0]][min[1]];
    }
}
```
