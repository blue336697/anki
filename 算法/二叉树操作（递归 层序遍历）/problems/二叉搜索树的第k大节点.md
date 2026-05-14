# 二叉搜索树的第k大节点

## 题干
给定一棵二叉搜索树和整数 k，返回第 k 大节点值。BST 的反向中序遍历会得到降序序列。

![image.png](image%207.png)

## 遍历策略
反向中序遍历：BST 的右→根→左顺序是降序。访问计数到 k 时得到第 k 大节点。

## 复杂度
时间 O(h+k)：反向中序先沿右链走到最大值方向，再访问 k 个节点得到第 k 大；最坏 k=n 时为 O(n)<br>空间 O(h)：递归栈或显式栈保存当前路径，平衡树 O(log n)，退化树 O(n)

## 题解(反向中序)
```java
class Solution {
    List<Integer> list = new ArrayList<>();
    public int kthLargest(TreeNode root, int k) {
        inOrder(root);
        return list.get(list.size() - k);
    }

    public void inOrder(TreeNode root){
        if(root.left != null)
            inOrder(root.left);
        list.add(root.val);
        if(root.right != null)
            inOrder(root.right);
    }
}
```

## 关键技巧
递归三部曲：1.终止条件 2.处理当前层逻辑 3.递归调用左右子树
