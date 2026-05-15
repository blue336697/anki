# Floyd 多源最短路

## 元信息

- 大类：图论
- 知识点：Floyd 多源最短路
- 目标牌组：算法::数据结构与经典算法::图论::Floyd多源最短路

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
Floyd 算法解决什么问题？	Floyd-Warshall 用于求所有点对之间的最短路径，也就是多源最短路。它使用动态规划，允许以编号不超过 k 的点作为中转点，不断更新 dist[i][j]。	算法 数据结构经典算法 图论 Floyd 概念	图论-Floyd	Medium
Floyd 的状态转移是什么？	dist[i][j] 表示 i 到 j 的当前最短距离。枚举中转点 k，如果经过 k 更短，则更新：dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])。k 必须放最外层，表示逐步放开可用中转点集合。	算法 数据结构经典算法 图论 Floyd DP	图论-Floyd	Hard
Floyd Java 模板怎么写？	模板：<br><pre><code class="language-java">for (int i = 0; i &lt; n; i++) Arrays.fill(dist[i], INF);<br>for (int i = 0; i &lt; n; i++) dist[i][i] = 0;<br>for (int[] e : edges) dist[e[0]][e[1]] = Math.min(dist[e[0]][e[1]], e[2]);<br>for (int k = 0; k &lt; n; k++) {<br>    for (int i = 0; i &lt; n; i++) {<br>        for (int j = 0; j &lt; n; j++) {<br>            if (dist[i][k] != INF &amp;&amp; dist[k][j] != INF) {<br>                dist[i][j] = Math.min(dist[i][j], dist[i][k] + dist[k][j]);<br>            }<br>        }<br>    }<br>}</code></pre>注意 INF 防溢出，且根据题意决定有向/无向边初始化。	算法 数据结构经典算法 图论 Floyd 模板	图论-Floyd	Hard
Floyd 复杂度怎么推导？	三重循环枚举 k、i、j，每层 n 次，时间 O(n^3)。dist 矩阵保存任意两点之间距离，空间 O(n^2)。因此 Floyd 适合点数较小、需要多源查询或图较稠密的场景。	算法 数据结构经典算法 图论 Floyd 复杂度	图论-Floyd	Medium
Floyd 能处理负权边吗？	Floyd 可以处理负权边，但不能存在负权环。如果 dist[i][i] 最终小于 0，说明存在从 i 可达并回到 i 的负权环，最短路没有良定义。没有负权时，多源最短路也可多次 Dijkstra，取决于点边规模。	算法 数据结构经典算法 图论 Floyd 边界	图论-Floyd	Hard
Floyd 适合哪些题？	典型信号：点数不大、任意两点距离、多次最短路查询、关系传递闭包。例题：找到阈值距离内邻居最少的城市、课程/可达性传递、判断任意两点最短距离是否满足约束。	算法 数据结构经典算法 图论 Floyd 例题	图论-Floyd	Medium
```
