# 螺旋矩阵 II

## 题干
给你一个正整数 n，生成一个包含 1 到 n^2 所有元素，且元素按顺时针顺序螺旋排列的 n x n 正方形矩阵 matrix。
![image 1.png](image%201.png)

## 复杂度
时间：{{c1::O(n^2)}} -- 填充 n^2 个格子
空间：{{c1::O(1)}} -- 除结果矩阵外

## 关键技巧
与螺旋矩阵 I 的代码高度对称：
螺旋矩阵 I：读取数据到 list，break 方式退出
螺旋矩阵 II：写入数据到矩阵，num <= target 方式退出
核心都是四个方向 + 边界收缩。正方形矩阵无需 break 检查，直接 while(num<=n*n) 即可。

## 题解(边界收缩)
与螺旋矩阵I对称：四个方向填充数字，边界逐步收缩，while(num<=n*n)控制。

```java
class Solution {
    public int[][] generateMatrix(int n) {
        int left = 0, right = n - 1, top = 0, low = n - 1;
        int[][] res = new int[n][n];
        int num = 1, target = n * n;
        while (num <= target) {
            // Left to right
            for (int i = left; i <= right; i++)
                res[top][i] = num++;
            top++;
            // Top to bottom
            for (int i = top; i <= low; i++)
                res[i][right] = num++;
            right--;
            // Right to left
            for (int i = right; i >= left; i--)
                res[low][i] = num++;
            low--;
            // Bottom to top
            for (int i = low; i >= top; i--)
                res[i][left] = num++;
            left++;
        }
        return res;
    }
}
```
