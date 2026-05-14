# 至多包含 K 个不同字符的最长子串

## 题干
给定一个字符串 s，找出至多包含 k 个不同字符的最长子串 T，返回其长度。
注意与"至少有K个重复字符的最长子串"区分：本题是种类数限制，后者是重复次数限制。
![image 30.png](image%2030.png)

## 复杂度
时间：{{c1::O(n)}} — 滑动窗口一次遍历
空间：{{c1::O(k)}} — HashMap最多k+1个键

## 关键技巧
标准滑动窗口模板：
1. 右指针扩展：将字符加入窗口，更新计数（首次出现时 count++）
2. 内缩条件：while(count > k) 不满足 → 左指针右移，减少字符计数
3. 字符计数归0时 count--，表示该字符已完全移出窗口
4. 每次窗口合法时更新 maxLen = right-left+1
区分记忆：本题考"种类数 <=k"，另一题考"每类字符重复次数 >=k"（分治/递归）

## 题解(滑动窗口)
标准滑动窗口：count 记录窗口内不同字符种类数。当 count>k 时收紧左边界直到条件恢复。

```java
class Solution {
    public int longestSubstring(String s, int k) {
        if(k == 0)
            return 0;
        Map<Character, Integer> map = new HashMap<>();
        int maxLen = 0, len = s.length();
        int count = 0;
        for(int left = 0, right = 0; right < len; right++){
            map.put(s.charAt(right), map.getOrDefault(s.charAt(right), 0) + 1);
            if(map.get(s.charAt(right)) == 1)
                count++;
            while(count > k){
                map.put(s.charAt(left), map.get(s.charAt(left)) - 1);
                if(map.get(s.charAt(left)) == 0)
                    count--;
                left++;
            }
            maxLen = Math.max(maxLen, right - left + 1);
        }
        return maxLen;
    }
}
```
