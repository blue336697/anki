# 至多包含 K 种字符的最长子串
<!-- aliases: 至多包含 K 个不同字符的最长子串, 至多包含K种字符的最长子串 -->
<!-- tags: source::leetcode source::字节 pattern::可变滑动窗口 -->

## 题干
给定字符串 `s` 和非负整数 `k`，返回至多包含 k 种不同字符的最长连续子串长度。

本题限制的是窗口内“不同字符种类数”，不要与“每种字符至少重复 k 次的最长子串”混淆；后者通常使用分治或按字符种类数枚举窗口。

## 指针策略
`right` 右移：{{c1::把新字符加入频次表；若首次出现，不同字符数加一}}。
窗口内种类数 `> k` 时：{{c1::不断右移 left 并减少频次，某字符频次归零时从表中删除}}。
窗口恢复合法后：{{c1::用 right - left + 1 更新最长长度}}。

收缩必须使用 `while`，因为移除一个左端字符后，窗口仍可能包含超过 k 种字符。

## 复杂度
时间：{{c1::O(n)}} — 每个字符最多被 right 加入一次、被 left 移出一次，共 O(2n) 次操作。
空间：{{c1::O(min(n, 字符集大小))}} — 哈希表保存当前窗口中的不同字符；收缩前可能短暂达到 k+1 种。

## 关键技巧
频次表的 `size()` 就是窗口中的不同字符数，无需另设一个可能与哈希表失去同步的 `count`。

当 `k == 0` 时，任何非空窗口都不合法，直接返回 0。空字符串也会由主循环自然得到 0。

## 题解(滑动窗口)
```java
import java.util.HashMap;
import java.util.Map;

class Solution {
    public int lengthOfLongestSubstringKDistinct(String s, int k) {
        if (k == 0) {
            return 0;
        }

        Map<Character, Integer> frequency = new HashMap<>();
        int left = 0;
        int maximum = 0;

        for (int right = 0; right < s.length(); right++) {
            char added = s.charAt(right);
            frequency.merge(added, 1, Integer::sum);

            while (frequency.size() > k) {
                char removed = s.charAt(left++);
                int nextCount = frequency.get(removed) - 1;
                if (nextCount == 0) {
                    frequency.remove(removed);
                } else {
                    frequency.put(removed, nextCount);
                }
            }

            maximum = Math.max(maximum, right - left + 1);
        }
        return maximum;
    }
}
```
