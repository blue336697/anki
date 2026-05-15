# Trie 前缀树

## 元信息

- 大类：字符串
- 知识点：Trie 前缀树
- 目标牌组：算法::数据结构与经典算法::字符串::Trie前缀树

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
Trie 解决什么问题？	Trie 前缀树用于高效存储和查询字符串集合，尤其适合前缀匹配。它把公共前缀共享在同一路径上，支持 insert、search、startsWith，常用于自动补全、敏感词、字典匹配、单词搜索剪枝。	算法 数据结构经典算法 字符串 Trie 概念	字符串-Trie	Medium
Trie 节点通常存什么？	节点通常包含 children 指针集合和 isEnd 标记。children 可用数组 `TrieNode[26]`、HashMap&lt;Character, TrieNode&gt; 或压缩结构。isEnd 表示从根到当前节点是否构成完整单词，否则只能说明这是某些单词的前缀。[[img:trie_prefix_tree.svg]]	算法 数据结构经典算法 字符串 Trie 结构	字符串-Trie	Medium
Trie Java 模板怎么写？	模板：<br><pre><code class="language-java">class Trie {<br>    static class Node { Node[] next = new Node[26]; boolean end; }<br>    Node root = new Node();<br>    void insert(String s) {<br>        Node p = root;<br>        for (char c : s.toCharArray()) {<br>            int i = c - 'a';<br>            if (p.next[i] == null) p.next[i] = new Node();<br>            p = p.next[i];<br>        }<br>        p.end = true;<br>    }<br>}</code></pre>search 和 startsWith 都是沿字符走路径，区别是 search 最后要求 end=true。	算法 数据结构经典算法 字符串 Trie 模板	字符串-Trie	Hard
Trie 复杂度怎么推导？	插入、查找、前缀查询的时间复杂度都是 O(L)，L 是字符串长度，与字典中单词数量无直接线性关系。空间最坏 O(总字符数 * 字符集指针成本)，数组 children 查询快但空间大，HashMap children 更省空间但常数更高。	算法 数据结构经典算法 字符串 Trie 复杂度	字符串-Trie	Medium
Trie 和 HashSet 有什么区别？	HashSet 适合完整字符串是否存在，平均 O(L) 计算哈希 + 比较；Trie 适合前缀查询、按前缀枚举、共享公共前缀、边搜索边剪枝。若只做精确查找，HashSet 更简单；若频繁 startsWith 或字典树 DFS，Trie 更合适。	算法 数据结构经典算法 字符串 Trie 对比	字符串-Trie	Medium
Trie 有哪些面试边界？	边界：1. 字符集不固定时不要写死 26；2. 删除单词要考虑共享前缀和引用计数；3. 大规模字典可能内存很大，可用压缩 Trie/双数组 Trie；4. Unicode 字符不能简单 `c-'a'`；5. 词频/TopK 自动补全需要在节点存额外统计。	算法 数据结构经典算法 字符串 Trie 边界	字符串-Trie	Hard
```
