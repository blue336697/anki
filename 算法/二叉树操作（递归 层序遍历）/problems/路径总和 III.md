# 路径总和 III
<!-- anki-deck: 路径总和 III（前缀和解法） -->

## 题干
给定二叉树根节点和目标和，统计路径和等于目标值的路径数量。路径不要求从根开始或到叶子结束，但必须向下走。

![image.png](image%2012.png)

## 遍历策略
双递归：外层枚举每个节点作为路径起点，内层从该起点向下累计路径和。
前缀和：DFS 过程中维护从根到当前节点路径上的前缀和计数；如果当前前缀和为 `cur`，则满足 `cur - old = targetSum` 的祖先前缀和 `old = cur - targetSum` 都能和当前节点组成一条合法向下路径。

## 复杂度
双递归时间 O(n*h)：外层把每个节点都当作路径起点，内层最多向下遍历 h 层；退化树 h=n 时为 O(n^2)，平衡树 h=logn 时约 O(nlogn)<br>前缀和时间 O(n)：每个节点只进入 DFS 一次，每次 HashMap 查询、更新和回溯都是均摊 O(1)<br>前缀和空间 O(h)：HashMap 只保存当前递归路径上的前缀和计数，递归栈也是树高 h；退化树 O(n)，平衡树 O(logn)

## 题解(双递归)
与第二种的区别就是不从当前根节点触发，每个节点作为根节点都可以双递归，时间复杂度很大前缀和+回溯，其实这种一眼就可以使用前缀和

```java
class Solution {
    int pathSumRes;
    public int pathSum(TreeNode root, long targetSum) {
        if(root == null)
            return 0;
        //这道题说了不要求从根节点出发，每个节点作为根节点都可以往下进行，符合条件就能增加路径数
        dfs(root, targetSum);
        //所以我们还要在主函数的递归中，去递归当前根节点的左右孩子作为根节点时能否符合条件
        pathSum(root.left, targetSum);
        pathSum(root.right, targetSum);
        return pathSumRes;
    }

    public void dfs(TreeNode root, long sum){
        if(root == null)
            return;
        sum -= root.val;
        if(sum == 0)
            pathSumRes++;
        dfs(root.left, sum);
        dfs(root.right, sum);
    }
}
```

## 题解(前缀和)
把从根到当前节点的路径看成一条数组路径，`cur` 表示当前路径前缀和。若之前某个祖先位置的前缀和为 `cur - targetSum`，那么祖先之后到当前节点这一段路径和就是 `targetSum`。进入节点时加入当前前缀和，离开节点时回溯删除，避免左右子树互相污染。

```java
class Solution {
    public int pathSum(TreeNode root, int targetSum) {
        Map<Long, Integer> prefixCount = new HashMap<>();
        prefixCount.put(0L, 1);
        return dfs(root, 0L, targetSum, prefixCount);
    }

    private int dfs(TreeNode node, long curSum, int targetSum, Map<Long, Integer> prefixCount) {
        if (node == null) {
            return 0;
        }

        curSum += node.val;
        int res = prefixCount.getOrDefault(curSum - targetSum, 0);

        prefixCount.put(curSum, prefixCount.getOrDefault(curSum, 0) + 1);
        res += dfs(node.left, curSum, targetSum, prefixCount);
        res += dfs(node.right, curSum, targetSum, prefixCount);
        prefixCount.put(curSum, prefixCount.get(curSum) - 1);

        return res;
    }
}
```

## 关键技巧
1. `prefixCount.put(0L, 1)` 表示从根节点开始的一段路径也可以被统计。
2. 查询 `prefixCount.getOrDefault(curSum - targetSum, 0)`，含义是有多少个祖先前缀和能和当前节点组成目标路径。
3. DFS 进入节点时加入 `curSum`，离开节点前必须回溯减一，否则左子树的前缀和会污染右子树。
4. 使用 `long` 保存前缀和，避免节点值和路径累加后发生 `int` 溢出。
