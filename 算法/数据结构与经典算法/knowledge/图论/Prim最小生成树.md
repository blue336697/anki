# Prim 最小生成树

## 元信息

- 大类：图论
- 知识点：Prim 最小生成树
- 目标牌组：算法::数据结构与经典算法::图论::Prim最小生成树

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
Prim 算法解决什么问题？	Prim 用来求无向连通带权图的最小生成树 MST：选出 V-1 条边连接所有点，并让总权重最小。它是从一个点开始扩展“已连通集合”，每次选择一条连接集合内外且权重最小的边。	算法 数据结构经典算法 图论 Prim MST 概念	图论-Prim	Medium
Prim 的核心贪心依据是什么？	依据是 MST 的 cut property：对任意一个割，跨过这个割的最小权边一定可以属于某棵最小生成树。Prim 每一步都维护“已加入集合 S”和“未加入集合 V-S”的割，选择跨割最小边，因此局部选择可以安全扩展成全局最优。	算法 数据结构经典算法 图论 Prim 贪心	图论-Prim	Hard
Prim 的堆优化流程是什么？	流程：1. 任取起点入堆，边权为 0；2. 每次弹出连接到未访问点的最小边；3. 若该点已访问则跳过；4. 标记访问，把边权加入答案；5. 将该点连出的所有边加入堆；6. 最后访问点数为 n 才存在 MST。	算法 数据结构经典算法 图论 Prim 机制	图论-Prim	Medium
Prim 的复杂度怎么推导？	邻接表 + 小根堆：每条无向边最多从两个端点入堆，堆操作 O(logE)，整体 O(ElogE)，通常可写 O(ElogV)。空间 O(V+E)：邻接表、visited、堆。邻接矩阵朴素版每次在未加入点中找最小连接代价，V 轮，每轮 O(V)，复杂度 O(V^2)，适合稠密图。	算法 数据结构经典算法 图论 Prim 复杂度	图论-Prim	Hard
Prim Java 模板的关键代码是什么？	核心模板：<br><pre><code class="language-java">boolean[] vis = new boolean[n];<br>PriorityQueue&lt;int[]&gt; pq = new PriorityQueue&lt;&gt;((a,b) -&gt; a[1] - b[1]);<br>pq.offer(new int[]{0, 0}); // node, cost<br>int count = 0, ans = 0;<br>while (!pq.isEmpty() &amp;&amp; count &lt; n) {<br>    int[] cur = pq.poll();<br>    int u = cur[0], cost = cur[1];<br>    if (vis[u]) continue;<br>    vis[u] = true;<br>    count++; ans += cost;<br>    for (int[] e : graph[u]) {<br>        if (!vis[e[0]]) pq.offer(new int[]{e[0], e[1]});<br>    }<br>}<br>return count == n ? ans : -1;</code></pre>注意：如果图不连通，不能得到覆盖所有点的 MST。	算法 数据结构经典算法 图论 Prim 模板	图论-Prim	Hard
Prim 适合哪些例题？	典型信号：给 n 个点和边/距离，要求用最小总成本把所有点连起来。例题：连接所有点的最小费用、最低成本联通所有城市、布线/管道/网络建设类问题。若边需要从点坐标动态计算，常见做法是构造完全图或用 O(n^2) Prim 避免显式存所有边。	算法 数据结构经典算法 图论 Prim 例题	图论-Prim	Medium
Prim 和 Dijkstra 看起来都用堆，区别是什么？	Dijkstra 维护的是“源点到某点的最短路径距离 dist[v]”，每次确定一个点的最短路；Prim 维护的是“把某个未访问点接入当前生成树的最小边权”，每次给生成树加一个点和一条边。Dijkstra 解决最短路径，Prim 解决最小生成树，目标函数完全不同。[[img:mst_prim_kruskal.svg]]	算法 数据结构经典算法 图论 Prim 对比	图论-Prim	Hard
```

