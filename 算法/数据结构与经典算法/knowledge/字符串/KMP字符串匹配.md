# KMP 字符串匹配

## 元信息

- 大类：字符串
- 知识点：KMP 字符串匹配
- 目标牌组：算法::数据结构与经典算法::字符串::KMP字符串匹配

## TSV 导出区

字段顺序：

```text
Front<TAB>Back<TAB>Tags<TAB>Source<TAB>Difficulty
```

```tsv
KMP 解决什么问题？	KMP 用于在文本串 text 中查找模式串 pattern，时间复杂度 O(n+m)。它通过 next/lps 数组记录模式串前缀和后缀的最长匹配长度，失配时不回退文本指针，只移动模式串指针。	算法 数据结构经典算法 字符串 KMP 概念	字符串-KMP	Medium
lps/next 数组表示什么？	lps[i] 表示 pattern[0..i] 这个前缀子串中，最长的“真前缀 = 真后缀”的长度。真前缀不能等于整个串。失配时，模式串可以跳到 lps[j-1]，复用已经匹配过的公共前后缀。[[img:kmp_lps_fallback.svg]]	算法 数据结构经典算法 字符串 KMP next	字符串-KMP	Hard
KMP 为什么文本指针不用回退？	因为失配前已经知道 text 的一段后缀等于 pattern 的一段前缀。lps 告诉我们模式串应该移动到哪个位置才能复用这段匹配，因此 text 指针继续向前即可，避免朴素匹配中重复比较。	算法 数据结构经典算法 字符串 KMP 原理	字符串-KMP	Hard
KMP Java 匹配模板是什么？	模板：<br><pre><code class="language-java">int[] lps = build(pattern);<br>int j = 0;<br>for (int i = 0; i &lt; text.length(); i++) {<br>    while (j &gt; 0 &amp;&amp; text.charAt(i) != pattern.charAt(j)) j = lps[j - 1];<br>    if (text.charAt(i) == pattern.charAt(j)) j++;<br>    if (j == pattern.length()) return i - j + 1;<br>}<br>return -1;</code></pre>完整实现还要处理 pattern 为空的边界。	算法 数据结构经典算法 字符串 KMP 模板	字符串-KMP	Hard
KMP 复杂度怎么推导？	构造 lps 时指针 i 单调前进，j 只按 lps 回退，总摊还 O(m)。匹配时 i 单调扫描 text，j 前进和回退总次数也受 n 控制，总 O(n)。空间 O(m) 保存 lps。	算法 数据结构经典算法 字符串 KMP 复杂度	字符串-KMP	Medium
KMP 常见题型有哪些？	典型：实现 strStr、判断重复子字符串、字符串旋转匹配、最短回文中的前后缀匹配。若只是 Java 工程代码，`indexOf` 足够；算法面试中 KMP 考的是失配回退和前后缀复用。	算法 数据结构经典算法 字符串 KMP 例题	字符串-KMP	Medium
```
