# 二叉搜索树中第K小的元素

## 题干
![image.png](image%208.png)

## 遍历策略
利用BST性质：左<根<右。中序遍历得到有序序列。插入、删除、查找都是O(h)。

## 复杂度

## 题解(BFS/DFS)
利用大根堆（优先队列），但是时间复杂度并不算优秀使用API的排序，这个仅作为观赏，面试写出来直接say goodbye利用二叉搜索树的特性直接中序遍历，省去了排序的过程，时间复杂度最优

```java
public int kthSmallest(TreeNode root, int k) {
        //这里就是使用权重的队列来模拟大根堆的创建过程
        //重写里面的compareTo方法使之降序排列，与树的层次遍历结合，一层一层的检查大根堆
        PriorityQueue<Integer> q = new PriorityQueue<>((a,b)->b-a);
        Deque<TreeNode> d = new ArrayDeque<>();
        d.addLast(root);
        while (!d.isEmpty()) {
            TreeNode node = d.pollFirst();
            //如果此时大根堆的长度还不足k，那么就证明还未建立完成，继续增加新的节点
            //即建立一个容量为k的堆
            if (q.size() < k) {
                q.add(node.val);
                //如果大根堆满了则要比较当前节点值，跟队列中的值
                //如果队首的值大于当前节点值
            } else if (q.peek() > node.val) {
                //当进行出队操作后，剩余的元素来进行大根堆的重构，时刻保证了大根堆
                //对容量为k的大根堆，我们时刻保证个规则，大的出，当全部遍历完
                //剩余的刚好就是我们需要的
                q.poll();   //将根节点出队
                q.add(node.val);
            }

            //也就是说上面的全部操作，就是在优化k个范围内的大根堆，我们找第k个最小的元素
            //那在大根堆中就是k个容量的根节点就是所求的值

            if (node.left != null) d.addLast(node.left);
            if (node.right != null) d.addLast(node.right);
        }
        return q.peek();
    }
```

## 关键技巧
BFS层序遍历：队列+每层size循环
