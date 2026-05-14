# 从上到下打印二叉树 II

## 题干
给定二叉树根节点，按层从上到下打印，每一层单独作为一个列表返回。

## 遍历策略
BFS 分层：队列按层遍历，每轮固定当前层 size，把这一层节点值收集成列表。

## 复杂度
时间 O(n)：层序遍历每个节点入队、出队一次，并加入当前层列表 -> O(n)<br>空间 O(w+n)：队列最多保存最大层宽 w，结果列表保存 n 个节点值；不计输出时为 O(w)

## 题解(BFS分层)
```java
class Solution {
    List<List<Integer>> list = new ArrayList<>();
    Queue<TreeNode> queue = new LinkedList<>();
    public List<List<Integer>> levelOrder(TreeNode root) {
        //levelTraversal(0, root);
        levelTraversal(root);
        return list;
    }

    //递归
    public void levelTraversal(int depth, TreeNode node){
        //list.add(new ArrayList<Integer>().add(node.val));
        if(node == null)
            return;
        if(depth == list.size()){
            list.add(new ArrayList<>());
        }
        //这句代码就是分层的关键，将层数和大list大索引相关联
        list.get(depth).add(node.val);
        levelTraversal(depth + 1, node.left);
        levelTraversal(depth + 1, node.right);

    }

    //非递归方法
    public void levelTraversal(TreeNode root){
        if(root != null)
            queue.add(root);
        while(!queue.isEmpty()){
            List<Integer> temp = new ArrayList<>();
            //这句就是分层的关键，以队列中的节点数为分层的区别，例如第一次进入这个方法时队列初始化完成以后的长度是1，那么就为根结点的层数，当进入第二次循环的时候根结点出列的他的左孩子和右孩子进入队列，长度变为2即为第二层，如果第二层的两个结点都有左右孩子那么队列会进入四个结点，长度变为4即为第三层
            for(int i = queue.size();i>0;i--){
                TreeNode node = queue.poll();
                temp.add(node.val);
                if(node.left != null)
                    queue.add(node.left);
                if(node.right != null)
                    queue.add(node.right);

            }
            list.add(temp);
        }
    }
}
```

## 关键技巧
BFS层序遍历：队列+每层size循环；List<List<Integer>>收集每层结果，new ArrayList<>()创建临时列表
