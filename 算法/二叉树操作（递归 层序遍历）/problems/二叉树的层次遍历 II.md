# 二叉树的层次遍历 II

## 题干
给定二叉树根节点，返回自底向上的层序遍历结果，即先收集每层，再把层顺序反转。

## 遍历策略
BFS + 反转层序：先正常从上到下收集每层节点，最后反转层列表；也可以每层结果头插到答案前面。

## 复杂度
时间 O(n)：正常层序遍历访问 n 个节点，最后按层反转或头插层结果，总体仍为 O(n)<br>空间 O(w+n)：队列最多 O(w)，输出结果保存 n 个节点值；不计输出时为 O(w)

## 题解(BFS自底向上)
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
