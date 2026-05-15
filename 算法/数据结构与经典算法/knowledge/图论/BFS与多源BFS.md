# BFS 与多源 BFS

## 元信息

- 大类：图论
- 知识点：BFS 与多源 BFS
- 目标牌组：算法::数据结构与经典算法::图论::BFS与多源BFS

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
BFS 解决什么问题？	BFS 广度优先搜索适合无权图或所有边权相同的最短步数问题。它从起点按层扩展，第一次访问到某个节点时，路径长度就是最短步数。常见场景：迷宫最短路、单词接龙、二叉树层序遍历、网格扩散。	算法 数据结构经典算法 图论 BFS 概念	图论-BFS	Medium
BFS 为什么能求无权最短路？	因为 BFS 是按距离层次扩展的：先访问距离为 0 的起点，再访问距离为 1 的节点，再访问距离为 2 的节点。无权图中每条边代价相同，所以第一次到达节点时，不可能存在更短路径还没被发现。	算法 数据结构经典算法 图论 BFS 原理	图论-BFS	Medium
多源 BFS 是什么？	多源 BFS 是把多个起点同时入队，初始距离都设为 0，然后一起向外扩散。它等价于新增一个虚拟源点，向所有真实源点连一条 0 权边。适合“离最近的 0/腐烂橘子/最近出口/最近陆地”这类问题。	算法 数据结构经典算法 图论 BFS 多源BFS	图论-BFS	Medium
BFS Java 模板怎么写？	模板：<br><pre><code class="language-java">Deque&lt;int[]&gt; q = new ArrayDeque&lt;&gt;();<br>boolean[][] vis = new boolean[m][n];<br>q.offer(new int[]{sx, sy}); vis[sx][sy] = true;<br>int step = 0;<br>while (!q.isEmpty()) {<br>    int size = q.size();<br>    for (int k = 0; k &lt; size; k++) {<br>        int[] cur = q.poll();<br>        for (int[] d : dirs) {<br>            int nx = cur[0] + d[0], ny = cur[1] + d[1];<br>            if (valid(nx, ny) &amp;&amp; !vis[nx][ny]) {<br>                vis[nx][ny] = true; q.offer(new int[]{nx, ny});<br>            }<br>        }<br>    }<br>    step++;<br>}</code></pre>层序题用 size 控制一层；距离数组题可直接 dist[nx][ny]=dist[x][y]+1。	算法 数据结构经典算法 图论 BFS 模板	图论-BFS	Hard
BFS 复杂度怎么推导？	邻接表图：每个点最多入队一次，每条边最多被扫描一次，时间 O(V+E)，空间 O(V)。网格图：每个格子最多入队一次，每次检查四/八个方向，时间 O(mn)，空间 O(mn)。	算法 数据结构经典算法 图论 BFS 复杂度	图论-BFS	Medium
BFS、DFS、Dijkstra 怎么选？	BFS：无权图最短步数。DFS：枚举路径、连通块、回溯搜索，不保证最短。Dijkstra：非负权图最短代价，边权不相等时用。看到“最少步数/每步代价相同”优先 BFS；看到“费用/时间/体力不同”考虑 Dijkstra。[[img:shortest_path_choice.svg]]	算法 数据结构经典算法 图论 BFS 对比	图论-BFS	Hard
```
