# 数据结构与经典算法

面向五年后端面试的算法原理牌组。这个目录不只收 LeetCode 题解，而是整理经典数据结构和算法的：

- 解决什么问题
- 适用条件和失败边界
- 核心思想和模板代码
- 复杂度推导
- 常见例题映射
- 面试追问对比

## 已覆盖知识点

- BFS 与多源 BFS
- Dijkstra 最短路径
- Bellman-Ford 最短路
- Floyd 多源最短路
- Prim 最小生成树
- Kruskal 最小生成树
- 并查集
- 拓扑排序
- 二叉堆与优先队列
- Trie 前缀树
- KMP 字符串匹配
- 线段树
- 树状数组
- 红黑树、跳表、B+树对比

## 目录

```text
diagrams/
  *.drawio      # drawio-skill 生成的可编辑源文件
  *.svg         # APKG 内使用的图片 fallback
knowledge/
  区间结构/
    树状数组.md
    线段树.md
  图论/
    BFS与多源BFS.md
    BellmanFord最短路.md
    Dijkstra最短路径.md
    Floyd多源最短路.md
    Prim最小生成树.md
    Kruskal最小生成树.md
    并查集.md
    拓扑排序.md
  堆与队列/
    二叉堆与优先队列.md
  字符串/
    KMP字符串匹配.md
    Trie前缀树.md
  树结构/
    红黑树跳表B加树对比.md
build_apkg.py
MANIFEST.md
```

## 配图

已为结构型/流程型知识点补充 8 张图：

- shortest_path_choice：BFS / Dijkstra / Bellman-Ford / Floyd 选择关系
- mst_prim_kruskal：Prim 与 Kruskal 对比
- union_find_path_compression：并查集路径压缩与按大小合并
- topological_sort_kahn：Kahn 拓扑排序流程
- trie_prefix_tree：Trie 前缀树结构
- kmp_lps_fallback：KMP lps 失配回退
- segment_tree_bit：线段树与树状数组对比
- tree_index_comparison：红黑树、跳表、B+树对比

说明：draw.io desktop CLI 在当前 macOS sandbox 中导出失败，因此保留 `.drawio` 源文件，并生成 `.svg` 作为 Anki 可显示媒体。

## 构建

```bash
cd 算法/数据结构与经典算法
python3 build_apkg.py
```

输出：

```text
牌组/算法/数据结构与经典算法.apkg
```

牌组层级：

```text
算法::数据结构与经典算法::<大类>::<知识点>
```

例如：

```text
算法::数据结构与经典算法::图论::Dijkstra最短路径
算法::数据结构与经典算法::字符串::KMP字符串匹配
```
