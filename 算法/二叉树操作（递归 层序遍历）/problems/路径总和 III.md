# 路径总和 III

## 题干
![image.png](image%2012.png)

## 遍历策略
DFS回溯：到达叶子节点时检查 sum==targetSum。路径总和III用前缀和+HashMap优化。

## 复杂度

## 题解(BFS/DFS)
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
