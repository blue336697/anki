# 从上到下打印二叉树 III

## 题干
给定二叉树根节点，按之字形顺序打印：第一层从左到右，第二层从右到左，依次交替。

## 遍历策略
BFS + 奇偶层方向：按层遍历，用 flag 控制当前层是尾插还是头插，或先收集后按层号反转。

## 复杂度
时间 O(n)：BFS 遍历 n 个节点，按层根据奇偶方向插入或反转，所有节点总处理次数为 n -> O(n)<br>空间 O(w+n)：队列最多 O(w)，输出结果保存 n 个节点值；不计输出时为 O(w)

## 题解(BFS之字形)
跟【二叉树的锯齿形层次遍历】一个样子，设置标志位

```java
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> res = new ArrayList<>();
        if(root == null)
            return res;
        List<Integer> list = new ArrayList<>();
        Queue<TreeNode> queue = new LinkedList<>();
        queue.add(root);
        //由于我们需要Z形遍历，其实就是跟103题一样，设置一个反转标志位即可
        boolean reverse = false;    //默认第一层不反转
        while(!queue.isEmpty()){
            int len = queue.size();
            //我们每次需要在一个while循环中处理完一层，那么需要嵌套for循环来
            for(int i = 0; i < len; i++){
                TreeNode temp = queue.poll();
                list.add(temp.val);
                if(temp.left != null)
                    queue.add(temp.left);
                if(temp.right != null)
                    queue.add(temp.right);
            }
            if(reverse)
                Collections.reverse(list);
            reverse = !reverse;
            res.add(new ArrayList<>(list));
            list.clear();
        }
        return res;
    }
}
```

## 关键技巧
BFS层序遍历：队列+每层size循环；List<List<Integer>>收集每层结果，new ArrayList<>()创建临时列表
