# 至少有K个重复字符的最长子串

## 题干
给定字符串 s 和一个整数 k，找出 s 中的最长子串，要求该子串中的每一字符出现次数都不少于 k。返回这一子串的长度。

## 复杂度
时间：{{c1::O(26n) → O(n)}} — 每层递归最多26次分割
空间：{{c1::O(26²)}} — 递归栈深度最多26层

## 关键技巧
分治思想：如果某个字符在整个字符串中出现次数 < k，则任何合法子串都不能包含该字符。因此可以用该字符分割字符串，对每个子串递归求解，取最大值。
关键理解：分割字符一定不在答案子串中，所以按它分割不会漏掉答案。
递归最多26层（26个小写字母），每层O(n)，总复杂度 O(26n)。

## 题解(递归分治)
核心：以出现次数<k的字符为分割点，递归处理分割后的子串。

```java
class Solution {
    public int longestSubstring(String s, int k) {
        if (s.length() < k)
            return 0;
        Map<Character, Integer> map = new HashMap<>();
        for (int i = 0; i < s.length(); i++) {
            map.put(s.charAt(i), map.getOrDefault(s.charAt(i), 0) + 1);
        }
        for (char ch : map.keySet()) {
            if (map.get(ch) < k) {
                int res = 0;
                for (String str : s.split(String.valueOf(ch)))
                    res = Math.max(res, longestSubstring(str, k));
                return res;
            }
        }
        return s.length();
    }
}
```
