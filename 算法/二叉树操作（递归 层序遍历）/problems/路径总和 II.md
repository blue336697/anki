# 路径总和 II

## 题干
![image.png](image%2011.png)

## 遍历策略
DFS回溯：到达叶子节点时检查 sum==targetSum。路径总和III用前缀和+HashMap优化。

## 复杂度

## 题解(BFS/DFS)
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
