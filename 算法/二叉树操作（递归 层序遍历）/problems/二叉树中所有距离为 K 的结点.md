# 二叉树中所有距离为 K 的结点

## 题干

## 遍历策略
递归三部曲：1.终止条件 2.处理当前节点逻辑 3.递归调用左右子树。

## 复杂度

## 题解(BFS/DFS)
树转图（领接表）+BFS

```java
class Solution {
    Map<Integer, List<Integer>> map;
    List<Integer> res;
    Set<Integer> visit;
    public List<Integer> distanceK(TreeNode root, TreeNode target, int k) {
        if(root == null)
            return new ArrayList();
        res = new ArrayList<>();
        //使用map存放领接表，key是节点，value是相邻的点
        //之所以使用领接表不用矩阵，对于本体的树转化为图其实属于稀疏图，为了节约内存
        map = new HashMap<>();
        //我们使用BFS的方式去遍历图，以target向外扩散k次就是目标的所有节点了
        dfs(root);
        //我们用一个集合标记去过的节点
        visit = new HashSet<>();
        Deque<Integer> queue = new LinkedList<>();
        queue.add(target.val);
        visit.add(target.val);
        int size = 0;
        while(!queue.isEmpty() && k >= 0){
            size = queue.size();
            for(int i = 0; i < size; i++){
                int temp = queue.poll();
                if(k == 0){ //到达目标距离的所有节点，循环队列里面节点次数最后返回即可
                    res.add(temp);
                    continue;
                }
                //得到当前节点的相邻节点
                List<Integer> nodes = map.get(temp);
                if(nodes == null)   continue;
                for(int node : nodes){
                    //防止重复遍历，如果没有访问过加入队列和访问集合
                    if(!visit.contains(node)){
                        queue.add(node);
                        visit.add(node);
                    }
                }

            }
            k--;
        }
        return res;

    }
    //构建图的边关系：通过dfs遍历每个节点，每个节点将左右孩子分别添加进去，注意是无向图，双向的
    public void dfs(TreeNode root){
        if(root == null)
            return;
        if(root.left != null){
            add(root.val, root.left.val);
            add(root.left.val, root.val);
            dfs(root.left);
        }
        if(root.right != null){
            add(root.val, root.right.val);
            add(root.right.val, root.val);
            dfs(root.right);
        }
    }
    //添加具体的边关系
    public void add(int a, int b){
        if(map.get(a) == null){
            List<Integer> list = new ArrayList<>();
            list.add(b);
            map.put(a, list);
        }else{
            List<Integer> list = map.get(a);
            list.add(b);
            map.put(a, list);
        }
    }
}
```

## 关键技巧
BFS层序遍历：队列+每层size循环；HashMap存储中序val→index映射，O(1)定位根节点位置
