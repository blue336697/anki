# 二叉搜索树的第k大节点

## 题干
![image.png](image%207.png)

## 遍历策略
利用BST性质：左<根<右。中序遍历得到有序序列。插入、删除、查找都是O(h)。

## 复杂度

## 题解(BFS/DFS)
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
