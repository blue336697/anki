# 路径总和 II

## 题干
给定二叉树根节点和目标和，返回所有从根到叶子节点、节点值之和等于目标和的路径。

![image.png](image%2011.png)

## 遍历策略
DFS 回溯：维护当前路径和 path 列表；到叶子时检查目标和，命中则复制 path；返回上一层时移除当前节点。

## 复杂度
时间 O(n*h)：DFS 每个节点访问一次；每条满足条件的根到叶路径需要复制当前路径，单次复制最多 h，输出复制成本按答案规模计<br>空间 O(h+r)：递归栈和当前路径为 O(h)，r 为所有答案路径保存的总节点数；不计输出时为 O(h)

## 题解(DFS回溯)
```java
//这道题有三个注意的点
class Solution {
    //dfs
    List<List<Integer>> res = new ArrayList<>();
    public List<List<Integer>> pathSum(TreeNode root, int targetSum) {
        List<Integer> path = new ArrayList<>();
        dfs(root, targetSum, path);
        return res;
    }

    public void dfs(TreeNode root, int sum, List<Integer> path) {
        if(root == null) return;
        sum = sum - root.val;
        path.add(root.val);
        if(root.left == null && root.right == null && sum == 0) {
            //1.不能在这里直接res.add（path），应该重新new一个将当前满足路径的元素集合传入res，如果一直用path直接穿入，会有数据冗余
            res.add(new ArrayList<>(path));
            //2.不能满足条件后即这个if满足后直接返回，因为会缺少一次回溯，会不能将path的重复元素删除，所以我们需要在进行一次回溯会删除
        }
        dfs(root.left, sum, path);
        dfs(root.right, sum, path);
        //3.需要进行回溯，对每次path满足条件或不满足条件的进行筛选
        path.remove(path.size() - 1);
    }
}
```

## 关键技巧
List<List<Integer>>收集每层结果，new ArrayList<>()创建临时列表；DFS+回溯：递归后撤销选择（path.removeLast()）
