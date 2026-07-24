# 二叉树中所有距离为 K 的结点

## 题干
给定二叉树、目标节点 target 和距离 k，返回所有距离 target 正好为 k 的节点值。树需要能向父节点方向走，因此常转成无向图。

## 遍历策略
树转无向图 + BFS：先 DFS 建立父子双向邻接表，再从 target 开始按层 BFS 扩散 k 层，最后队列中的节点就是答案。

## 复杂度
时间 O(n)：DFS 建无向邻接表访问每条树边一次，随后从 target 做 BFS，每个节点最多入队一次 -> O(n)<br>空间 O(n)：邻接表、visited 集合和 BFS 队列都可能保存 O(n) 个节点，结果列表另按答案数量计

## 题解(树转图+BFS)
树转无向图（邻接表）+ BFS。建边时用 `connect(a, b)` 一次加入双向边，内部用 `computeIfAbsent` 初始化邻接表，避免手写 `get/null/put` 的重复逻辑。

```java
class Solution {
    public List<Integer> distanceK(TreeNode root, TreeNode target, int k) {
        Map<Integer, List<Integer>> graph = new HashMap<>();
        buildGraph(root, graph);

        Deque<Integer> queue = new ArrayDeque<>();
        Set<Integer> visited = new HashSet<>();
        queue.offer(target.val);
        visited.add(target.val);

        while (!queue.isEmpty() && k-- > 0) {
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                int cur = queue.poll();
                for (int next : graph.getOrDefault(cur, Collections.emptyList())) {
                    if (visited.add(next)) {
                        queue.offer(next);
                    }
                }
            }
        }

        List<Integer> res = new ArrayList<>();
        while (!queue.isEmpty()) {
            res.add(queue.poll());
        }
        return res;
    }

    private void buildGraph(TreeNode node, Map<Integer, List<Integer>> graph) {
        if (node == null) {
            return;
        }
        if (node.left != null) {
            connect(node.val, node.left.val, graph);
            buildGraph(node.left, graph);
        }
        if (node.right != null) {
            connect(node.val, node.right.val, graph);
            buildGraph(node.right, graph);
        }
    }

    private void connect(int a, int b, Map<Integer, List<Integer>> graph) {
        graph.computeIfAbsent(a, key -> new ArrayList<>()).add(b);
        graph.computeIfAbsent(b, key -> new ArrayList<>()).add(a);
    }
}
```

## 关键技巧
1. 树要能从子节点走回父节点，所以先转成无向图再 BFS。
2. `connect(a, b)` 负责一次性加入 `a -> b` 和 `b -> a`，建边逻辑集中在一个地方。
3. `computeIfAbsent(key, k -> new ArrayList<>()).add(next)` 可以替代手写 `containsKey/get/put`。
4. BFS 扩散 k 层后，队列中剩下的节点就是距离 target 正好为 k 的节点。
