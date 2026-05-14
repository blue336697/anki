# 二叉树的层次遍历 II

## 题干

## 遍历策略
层序遍历(BFS)：队列存储，每层按size循环处理。

## 复杂度

## 题解(BFS/DFS)
没啥好说的层次遍历就完事了

```java
public class Solution {
    public List<List<Integer>> levelOrderBottom(TreeNode root) {
        List<List<Integer>> ans = new LinkedList<>();
        if (root == null)
            return ans;
        //设置队列
        Queue<TreeNode> queue = new LinkedList<>();
        //根结点入队
        queue.offer(root);
        while (!queue.isEmpty()) {
            int len = queue.size();
            List<Integer> tempList = new LinkedList<>();
            //广度优先遍历，以队列的长度为次数将本层的所有结点全部入队
            for (int i = 0; i < len; i++) {
                TreeNode node = queue.poll();
                tempList.add(node.val);
                if (node.left != null)
                    queue.offer(node.left);
                if (node.right != null)
                    queue.offer(node.right);
            }
            //ans.add(tempList);
            ans.add(0, tempList); //这里写成这样就不要最后反转了，改为头插
        }
        //Collections.reverse(ans);
        return ans;
    }
}
```

## 关键技巧
BFS层序遍历：队列+每层size循环；List<List<Integer>>收集每层结果，new ArrayList<>()创建临时列表
