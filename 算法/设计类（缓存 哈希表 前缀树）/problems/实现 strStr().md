# 实现 strStr()

## 题干
给定两个字符串 haystack 和 needle，在 haystack 中找出 needle 出现的第一个位置（从 0 开始）。如果不存在，返回 -1。实现 KMP 算法达到 O(m+n) 时间复杂度。

## 复杂度
KMP：时间 {{c1::O(m+n)}}，空间 {{c1::O(m)}}（next 数组）
暴力法：时间 {{c1::O(m*n)}}，空间 {{c1::O(1)}}

## 关键技巧
KMP 核心：利用已匹配信息，匹配失败时不回溯目标串指针 i，只回退模式串指针 j。
next[i] 含义：pattern[0..i] 的最长相等前后缀长度，即失配时 j 应跳转到的位置。
技巧：字符串前加空格使下标从 1 开始，简化边界处理。
构建 next：i 从 2 开始（next[1]=0），匹配成功 j++，匹配失败 j=next[j]。

## 题解(暴力法)
逐位匹配，不匹配时回溯目标串指针。

```java
class Solution {
    public int strStr(String haystack, String needle) {
        if(needle == null)
            return 0;
        int n = haystack.length(), m = needle.length();
        char[] target = haystack.toCharArray(), pattern = needle.toCharArray();
        for(int i = 0; i <= n - m; i++){
            // 前者就是目标串的指针，当前匹配逐个向后遍历，如果当前不匹配换出发点
            // 后者是模式串的指针，不匹配会被下一轮重置为0
            int begin = i, reStart = 0;
            while(reStart < m && target[begin] == pattern[reStart]){
                begin++;
                reStart++;
            }
            // 如果能够完全匹配，返回原串的「发起点」下标
            if(reStart == m)
                return i;
        }
        return -1;
    }
}
```

## 题解(KMP)
构建 next 数组实现 O(m+n)，失配时目标串指针不回溯，只回退模式串指针。

```java
class Solution {
    public int strStr(String target, String pattern) {
        if(pattern == null)
            return 0;
        int n = target.length(), m = pattern.length();

        // 原串和匹配串前面都加空格，使其下标从 1 开始
        target = " " + target;
        pattern = " " + pattern;
        char[] targets = target.toCharArray(), patterns = pattern.toCharArray();

        // 构建next数组，指明当前模式串与目标串不匹配，模式串回溯到哪个索引继续匹配
        int[] next = new int[m+1];
        // 构造过程 i = 2，j = 0 开始，i 小于等于匹配串长度 【构造 i 从 2 开始】
        for(int i = 2, j = 0; i <= m; i++){
            // 匹配不成功的话，j = next(j)
            while (j > 0 && patterns[i] != patterns[j + 1])
                j = next[j];
            // 匹配成功的话，先让 j++
            if (patterns[i] == patterns[j + 1])
                j++;
            // 更新 next[i]，结束本次循环，i++
            next[i] = j;
        }
        // 匹配过程，i = 1，j = 0 开始，i 小于等于原串长度 【匹配 i 从 1 开始】
        for(int i = 1, j = 0; i <= n; i++){
            // 匹配不成功 j = next(j)
            while (j > 0 && targets[i] != patterns[j + 1])
                j = next[j];
            // 匹配成功的话，先让 j++，结束本次循环后 i++
            if (targets[i] == patterns[j + 1])
                j++;
            // 整一段匹配成功，直接返回下标
            if (j == m)
                return i - m;
        }
        return -1;
    }
}
```
