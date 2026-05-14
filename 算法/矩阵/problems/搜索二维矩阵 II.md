# 搜索二维矩阵 II

## 题干
编写一个高效的算法来搜索 m x n 矩阵 matrix 中的一个目标值 target。该矩阵具有以下特性：每行的元素从左到右升序排列；每列的元素从上到下升序排列。

## 复杂度
右上角搜索：时间 {{c1::O(m+n)}}，空间 {{c1::O(1)}}
逐行二分：时间 {{c1::O(m log n)}}，空间 {{c1::O(1)}}

## 关键技巧
与搜索二维矩阵的区别：本题只保证每行每列有序，不保证行间严格递增，所以不能用展平二分。
右上角搜索本质：每次排除一行或一列，最多 m+n 步。
逐行二分是另一种备选方案，在 m 远小于 n 时更优。

## 题解(右上角搜索)
比 target 大 -> 排除当前列(j--)，比 target 小 -> 排除当前行(i++)。

```java
class Solution {
    public boolean searchMatrix(int[][] matrix, int target) {
        if (matrix.length == 0 && matrix[0].length == 0)
            return false;
        int i = 0, j = matrix[0].length - 1;
        while (i < matrix.length && j >= 0) {
            if (matrix[i][j] > target) {
                j--;
            } else if (matrix[i][j] < target) {
                i++;
            } else {
                return true;
            }
        }
        return false;
    }
}
```
