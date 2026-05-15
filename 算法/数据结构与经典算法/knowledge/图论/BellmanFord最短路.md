# Bellman-Ford 最短路

## 元信息

- 大类：图论
- 知识点：Bellman-Ford 最短路
- 目标牌组：算法::数据结构与经典算法::图论::BellmanFord最短路

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
Bellman-Ford 解决什么问题？	Bellman-Ford 求单源最短路，特点是可以处理负权边，并能检测从源点可达的负权环。它通过反复松弛所有边，让最多经过 k 条边的最短路逐步收敛。	算法 数据结构经典算法 图论 BellmanFord 概念	图论-BellmanFord	Medium
Bellman-Ford 为什么要松弛 V-1 轮？	在没有负权环的图中，一条简单最短路径最多包含 V-1 条边。第 1 轮能得到最多 1 条边的最短路，第 k 轮能得到最多 k 条边的最短路，所以做 V-1 轮后所有简单最短路都应收敛。	算法 数据结构经典算法 图论 BellmanFord 原理	图论-BellmanFord	Hard
Bellman-Ford Java 模板怎么写？	模板：<br><pre><code class="language-java">int[] dist = new int[n];<br>Arrays.fill(dist, INF); dist[src] = 0;<br>for (int i = 0; i &lt; n - 1; i++) {<br>    boolean changed = false;<br>    for (int[] e : edges) {<br>        int u = e[0], v = e[1], w = e[2];<br>        if (dist[u] != INF &amp;&amp; dist[v] &gt; dist[u] + w) {<br>            dist[v] = dist[u] + w; changed = true;<br>        }<br>    }<br>    if (!changed) break;<br>}</code></pre>如果第 V 轮仍能松弛，说明存在源点可达的负权环。	算法 数据结构经典算法 图论 BellmanFord 模板	图论-BellmanFord	Hard
Bellman-Ford 复杂度怎么推导？	外层最多 V-1 轮，每轮遍历所有 E 条边，时间 O(VE)。空间 O(V) 保存 dist。它比 Dijkstra 慢，但换来负权边和负权环检测能力。	算法 数据结构经典算法 图论 BellmanFord 复杂度	图论-BellmanFord	Medium
什么时候不用 Bellman-Ford？	如果边权非负且图较大，优先 Dijkstra；如果要所有点对最短路且点数小，考虑 Floyd；如果只是无权步数，BFS 更简单。Bellman-Ford 的位置是“负权单源最短路/限制最多经过 K 条边的最短路”。	算法 数据结构经典算法 图论 BellmanFord 对比	图论-BellmanFord	Medium
Bellman-Ford 和“最多 K 站中转”题有什么关系？	最多 K 站中转等价于最多使用 K+1 条边的最短路。可以做 K+1 轮松弛，并且每轮必须基于上一轮 dist 的拷贝更新，避免一轮内连续使用多条边导致超过边数限制。	算法 数据结构经典算法 图论 BellmanFord 例题	图论-BellmanFord	Hard
```
