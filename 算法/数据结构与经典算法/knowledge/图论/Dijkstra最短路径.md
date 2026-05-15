# Dijkstra 最短路径

## 元信息

- 大类：图论
- 知识点：Dijkstra 最短路径
- 目标牌组：算法::数据结构与经典算法::图论::Dijkstra最短路径

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
Dijkstra 解决什么问题？一句话怎么说？	Dijkstra 用来求带权图中“一个源点到其他点”的最短路径。核心前提是边权非负；它每次从未确定点里取当前距离最小的点，并把它的最短距离固定下来，再用它松弛相邻边。	算法 数据结构经典算法 图论 Dijkstra 概念	图论-Dijkstra	Medium
Dijkstra 为什么要求边权非负？	因为 Dijkstra 的贪心假设是：当前从堆里弹出的最小 dist 已经不可能再被后续路径变小。若存在负权边，一个后面才访问的点可能通过负边反过来降低已确定点的距离，贪心结论失效。负权边要考虑 Bellman-Ford / SPFA；多源多汇小规模可考虑 Floyd。	算法 数据结构经典算法 图论 Dijkstra 边界	图论-Dijkstra	Hard
Dijkstra 的核心流程是什么？	流程：1. dist[src]=0，其余为 INF；2. 把源点放入小根堆；3. 每次弹出 dist 最小的点 u；4. 如果弹出的是旧距离则跳过；5. 遍历 u 的所有出边 u->v,w，若 dist[u]+w 更小则更新 dist[v] 并入堆；6. 堆空后 dist 数组就是结果。	算法 数据结构经典算法 图论 Dijkstra 机制	图论-Dijkstra	Medium
Dijkstra 的复杂度怎么推导？	邻接表 + 优先队列：每条边最多触发一次有效松弛并入堆，堆操作 O(logV)，整体 O((V+E)logV)，通常写 O(ElogV)。空间 O(V+E)：邻接表 O(V+E)，dist/visited/堆最坏 O(V+E)。邻接矩阵朴素版每轮扫描所有点找最小值，V 轮，每轮 O(V)，复杂度 O(V^2)。	算法 数据结构经典算法 图论 Dijkstra 复杂度	图论-Dijkstra	Hard
Dijkstra Java 模板的关键代码是什么？	核心模板：<br><pre><code class="language-java">int[] dist = new int[n];<br>Arrays.fill(dist, INF);<br>dist[src] = 0;<br>PriorityQueue&lt;int[]&gt; pq = new PriorityQueue&lt;&gt;((a,b) -&gt; a[1] - b[1]);<br>pq.offer(new int[]{src, 0});<br>while (!pq.isEmpty()) {<br>    int[] cur = pq.poll();<br>    int u = cur[0], d = cur[1];<br>    if (d != dist[u]) continue;<br>    for (int[] e : graph[u]) {<br>        int v = e[0], w = e[1];<br>        if (dist[v] &gt; d + w) {<br>            dist[v] = d + w;<br>            pq.offer(new int[]{v, dist[v]});<br>        }<br>    }<br>}</code></pre>注意 Java 堆里没有 decrease-key，常用“重复入堆 + 旧距离跳过”。	算法 数据结构经典算法 图论 Dijkstra 模板	图论-Dijkstra	Hard
看到哪些题型要想到 Dijkstra？	典型信号：1. 图中边有非负权重；2. 问从一个点到其他点或某个点的最短代价；3. 代价不是边数，而是时间、费用、风险、体力等累加量；4. 需要最小化路径总权重。例题：网络延迟时间、最小体力消耗路径、概率最大路径可转成最大堆变体。	算法 数据结构经典算法 图论 Dijkstra 例题	图论-Dijkstra	Medium
Dijkstra、BFS、Bellman-Ford、Floyd 怎么对比？	BFS：无权图或所有边权相同，复杂度 O(V+E)。Dijkstra：非负权单源最短路，邻接表堆优化 O((V+E)logV)。Bellman-Ford：可处理负权边并检测负环，O(VE)。Floyd：多源最短路，适合点数较小的稠密图，O(V^3)。面试先问边权、负权、源点数量和数据规模。[[img:shortest_path_choice.svg]]	算法 数据结构经典算法 图论 Dijkstra 对比	图论-Dijkstra	Hard
```

