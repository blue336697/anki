# 打家劫舍 III

## 题干
> 每个节点可选择偷或者不偷两种状态，根据题目意思，相连节点不能一起偷
> 
- 当前节点选择偷时，那么两个孩子节点就不能选择偷了
- 当前节点选择不偷时，两个孩子节点只需要拿最多的钱出来就行(两个孩子节点偷不偷没关系)

> 我们使用一个大小为 2 的数组来表示 int[] res = new int[2] 0 代表不偷，1 代表偷 任何一个节点能偷到的最大钱的状态可以定义为
> 
- 当前节点选择不偷：当前节点能偷到的最大钱数 = 左孩子能偷到的钱 + 右孩子能偷到的钱
- 当前节点选择偷：当前节点能偷到的最大钱数 = 左孩子选择自己不偷时能得到的钱 + 右孩子选择不偷时能得到的钱 + 当前节点的钱数

## 遍历策略
树形DP：每个节点返回两个值 [偷当前节点的收益, 不偷当前节点的收益]。自底向上。

## 复杂度

## 题解(BFS/DFS)
终极方法> 每个节点可选择偷或者不偷两种状态，根据题目意思，相连节点不能一起偷- 当前节点选择偷时，那么两个孩子节点就不能选择偷了

```java
public int rob(TreeNode root) {
    int[] result = robErgodic(root);
    return Math.max(result[0], result[1]);
}

public int[] robErgodic(TreeNode root) {
    if (root == null) 
        return new int[2];
    int[] result = new int[2];

    int[] left = robErgodic(root.left);
    int[] right = robErgodic(root.right);

    result[0] = Math.max(left[0], left[1]) + Math.max(right[0], right[1]);
    result[1] = left[0] + right[0] + root.val;

    return result;
}
```

## 关键技巧
自底向上递归：先计算子树结果，再汇总返回当前层
