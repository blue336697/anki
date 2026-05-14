# 路径总和 III

## 题干
给定二叉树根节点和目标和，统计路径和等于目标值的路径数量。路径不要求从根开始或到叶子结束，但必须向下走。

![image.png](image%2012.png)

## 遍历策略
双递归 / 前缀和：当前代码用外层枚举每个起点、内层向下找路径；更优写法是 DFS 维护前缀和计数，查询 currentSum-target。

## 复杂度
时间 O(n*h)：当前代码是双递归，外层把每个节点都当作路径起点，内层 dfs 向下枚举从该起点出发的路径；最坏退化树 h=n 时为 O(n^2)，平衡树约 O(n log n)。若改成前缀和 HashMap 可优化到 O(n)<br>空间 O(h)：外层递归和内层 dfs 的调用深度都受树高 h 限制，退化树 O(n)，平衡树 O(log n)

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

## 关键技巧
使用long类型防止int溢出
