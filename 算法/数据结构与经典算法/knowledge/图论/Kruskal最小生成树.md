# Kruskal 最小生成树

## 元信息

- 大类：图论
- 知识点：Kruskal 最小生成树
- 目标牌组：算法::数据结构与经典算法::图论::Kruskal最小生成树

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
Kruskal 算法解决什么问题？	Kruskal 用来求无向带权图的最小生成树。它不从某个点扩展，而是把所有边按权重从小到大排序，依次尝试加入；如果一条边连接的是两个不同连通分量，就加入 MST，否则跳过以避免成环。	算法 数据结构经典算法 图论 Kruskal MST 概念	图论-Kruskal	Medium
Kruskal 为什么需要并查集？	Kruskal 的核心判断是“加入这条边会不会形成环”。在无向图里，如果边的两个端点已经在同一个连通分量中，加入就会成环；否则可以安全连接两个分量。并查集可以高效维护连通分量，支持 find/union 近似 O(1) 均摊。	算法 数据结构经典算法 图论 Kruskal 并查集	图论-Kruskal	Medium
Kruskal 的核心流程是什么？	流程：1. 将所有边按权重升序排序；2. 初始化并查集，每个点单独成分量；3. 遍历边 (u,v,w)；4. 若 find(u)!=find(v)，加入该边并 union；5. 累加权重和边数；6. 当边数等于 n-1 时结束；7. 若结束后边数不足 n-1，说明图不连通。	算法 数据结构经典算法 图论 Kruskal 机制	图论-Kruskal	Medium
Kruskal 的复杂度怎么推导？	排序所有边是主成本：O(ElogE)。遍历边时每次做 find/union，路径压缩 + 按秩合并后均摊近似 O(alpha(V))，总计 O(E alpha(V))，通常被排序覆盖。整体 O(ElogE)，空间 O(V+E)：边列表和并查集数组。	算法 数据结构经典算法 图论 Kruskal 复杂度	图论-Kruskal	Hard
Kruskal Java 模板的关键代码是什么？	核心模板：<br><pre><code class="language-java">Arrays.sort(edges, (a,b) -&gt; a[2] - b[2]);<br>UnionFind uf = new UnionFind(n);<br>int ans = 0, used = 0;<br>for (int[] e : edges) {<br>    int u = e[0], v = e[1], w = e[2];<br>    if (uf.union(u, v)) {<br>        ans += w;<br>        used++;<br>        if (used == n - 1) break;<br>    }<br>}<br>return used == n - 1 ? ans : -1;</code></pre>关键：union 返回 true 表示原本不连通，这条边被选入 MST。	算法 数据结构经典算法 图论 Kruskal 模板	图论-Kruskal	Hard
Kruskal 适合哪些例题？	典型信号：给出边列表或容易枚举边，要求最小成本连接所有点/城市/岛屿。例题：连接所有点的最小费用、最低成本联通所有城市、冗余连接变体。边天然是列表时 Kruskal 很顺手；完全图点很多时显式建边可能 O(n^2) 空间，需要权衡。	算法 数据结构经典算法 图论 Kruskal 例题	图论-Kruskal	Medium
Prim 和 Kruskal 怎么选？	稀疏图、边列表输入：Kruskal 简单直接，排序边即可。稠密图、邻接矩阵或从某点逐步扩展更自然：Prim 更合适。Kruskal 关注“边从小到大连接分量”，Prim 关注“当前树向外扩展最便宜的边”。两者都基于 cut property，只是组织方式不同。[[img:mst_prim_kruskal.svg]]	算法 数据结构经典算法 图论 Kruskal 对比	图论-Kruskal	Hard
```

