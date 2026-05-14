# N皇后

## 题干
n 皇后问题研究的是如何将 n 个皇后放置在 n×n 的棋盘上，并且使皇后彼此之间不能相互攻击。皇后可以攻击同一行、同一列、同一正对角线或同一副对角线上的任意单位。给你一个整数 n，返回所有不同的 n 皇后问题的解决方案。

## 复杂度
时间：{{c1::O(n!)}} — 每行有最多n个选择，且逐步减少
空间：{{c1::O(n²)}} — 棋盘数组

## 关键技巧
逐行放置 + 回溯剪枝：
1. 每行只放一个皇后，row 递增，天然避免行冲突
2. isValid 只检查列、左上对角线、右上对角线（下半部分还没放）
3. 45°对角线：i-1, j-1 递减；135°对角线：i-1, j+1 递增
4. 回溯：放皇后 → 递归下一行 → 撤销皇后 → 尝试下一列
5. 终止条件：row == n 时收集结果

## 题解(DFS+回溯)
逐行放置 + 回溯剪枝：每行只放一个皇后，isValid 只检查列、左上对角线、右上对角线。

```java
class Solution {
    List<List<String>> res;
    char[][] chessboard;
    public List<List<String>> solveNQueens(int n) {
        chessboard = new char[n][n];
        res = new ArrayList<>();
        for (char[] c : chessboard) {
            Arrays.fill(c, '.');
        }
        backTrack(n, 0);
        return res;
    }
    public void backTrack(int n, int row) {
        if (row == n) {
            res.add(Array2List());
            return;
        }
        for (int col = 0; col < n; col++) {
            if (isValid(row, col, n)) {
                chessboard[row][col] = 'Q';
                backTrack(n, row + 1);
                chessboard[row][col] = '.';
            }
        }
    }
    public List Array2List() {
        List<String> list = new ArrayList<>();
        for (char[] c : chessboard) {
            list.add(String.copyValueOf(c));
        }
        return list;
    }
    public boolean isValid(int row, int col, int n) {
        for (int i=0; i < row; i++) {
            if (chessboard[i][col] == 'Q') {
                return false;
            }
        }
        for (int i=row-1, j=col-1; i>=0 && j>=0; i--, j--) {
            if (chessboard[i][j] == 'Q') {
                return false;
            }
        }
        for (int i=row-1, j=col+1; i>=0 && j<=n-1; i--, j++) {
            if (chessboard[i][j] == 'Q') {
                return false;
            }
        }
        return true;
    }
}
```
