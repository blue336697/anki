# 不同路径 II

## 题干
一个机器人位于一个 m x n 网格的左上角。机器人每次只能向下或者向右移动一步。机器人试图达到网格的右下角。现在考虑网格中有障碍物，障碍物在网格中用 1 表示。那么从左上角到右下角将会有多少条不同的路径？

## 复杂度
DP：时间 {{c1::O(mn)}}，空间 {{c1::O(mn)}}
DFS+记忆化：时间 {{c1::O(mn)}}，空间 {{c1::O(mn)}}

## 关键技巧
不同路径 I 的升级版，增加了障碍物。
初始化：第一行和第一列遇到障碍物后，之后的位置都不可达（dp=0），所以用 && grid[i][0]==0 控制。
转移：dp[i][j] = grid[i][j]==1 ? 0 : dp[i-1][j] + dp[i][j-1]。
障碍物位置路径数为 0，因为不能经过障碍物。

## 题解(DP)
dp[i][j] = dp[i-1][j] + dp[i][j-1]，障碍物位置 dp=0。

```java
class Solution {
    public int uniquePathsWithObstacles(int[][] grid) {
        if (grid == null || grid.length == 0)
            return 0;
        int m = grid.length;
        int n = grid[0].length;
        int[][] dp = new int[m][n];
        // Init first column
        for (int i = 0; i < m && grid[i][0] == 0; i++) {
            dp[i][0] = 1;
        }
        // Init first row
        for (int j = 0; j < n && grid[0][j] == 0; j++) {
            dp[0][j] = 1;
        }
        for (int i = 1; i < m; i++) {
            for (int j = 1; j < n; j++) {
                if (grid[i][j] != 1)
                    dp[i][j] = dp[i - 1][j] + dp[i][j - 1];
            }
        }
        return dp[m - 1][n - 1];
    }
}
```
