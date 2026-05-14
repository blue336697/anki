# 打家劫舍 III

## 题干
给定一棵二叉树，每个节点代表金额，相邻父子节点不能同时偷，返回能偷到的最大金额。

> 每个节点可选择偷或者不偷两种状态，根据题目意思，相连节点不能一起偷
> 
- 当前节点选择偷时，那么两个孩子节点就不能选择偷了
- 当前节点选择不偷时，两个孩子节点只需要拿最多的钱出来就行(两个孩子节点偷不偷没关系)

> 我们使用一个大小为 2 的数组来表示 int[] res = new int[2] 0 代表不偷，1 代表偷 任何一个节点能偷到的最大钱的状态可以定义为
> 
- 当前节点选择不偷：当前节点能偷到的最大钱数 = 左孩子能偷到的钱 + 右孩子能偷到的钱
- 当前节点选择偷：当前节点能偷到的最大钱数 = 左孩子选择自己不偷时能得到的钱 + 右孩子选择不偷时能得到的钱 + 当前节点的钱数

## 遍历策略
树形 DP：每个节点返回两个状态：偷当前节点、不偷当前节点。偷当前则不能偷孩子；不偷当前则孩子可偷可不偷取最大。

## 复杂度
时间 O(n)：树形 DP 后序遍历每个节点一次，每个节点计算偷/不偷两个状态，常数操作 -> O(n)<br>空间 O(h)：递归栈高度为 h；每层只返回长度为 2 的状态数组，不额外保存所有节点状态时额外空间为 O(h)

## 题解(树形DP)
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
