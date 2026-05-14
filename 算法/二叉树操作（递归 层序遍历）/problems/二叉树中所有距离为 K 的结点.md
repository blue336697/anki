# 二叉树中所有距离为 K 的结点

## 题干
给定二叉树、目标节点 target 和距离 k，返回所有距离 target 正好为 k 的节点值。树需要能向父节点方向走，因此常转成无向图。

## 遍历策略
树转无向图 + BFS：先 DFS 建立父子双向邻接表，再从 target 开始按层 BFS 扩散 k 层，最后队列中的节点就是答案。

## 复杂度
时间 O(n)：DFS 建无向邻接表访问每条树边一次，随后从 target 做 BFS，每个节点最多入队一次 -> O(n)<br>空间 O(n)：邻接表、visited 集合和 BFS 队列都可能保存 O(n) 个节点，结果列表另按答案数量计

## 题解(树转图+BFS)
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
