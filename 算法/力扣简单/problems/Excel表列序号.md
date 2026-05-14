# Excel表列序号

## 题干
给你一个字符串 columnTitle，表示 Excel 表格中的列名称。返回该列名称对应的列序号。A→1, B→2, ..., Z→26, AA→27...

## 复杂度
时间：{{c1::O(n)}} — 遍历字符串
空间：{{c1::O(1)}}

## 关键技巧
26 进制转 10 进制，注意 1-indexed（A=1, Z=26）。
与「Excel表列名称」互为逆运算，那题需要先 cn--，这题需要 +1。
遍历方式：res = res * 26 + (ch - 'A' + 1)。

## 题解
26 进制转 10 进制，注意 1-indexed（A=1, Z=26），每次 res = res * 26 + (ch - A + 1)。

```java
class Solution {
    public int titleToNumber(String s) {
        int len = s.length();
        int res = 0;
        for (int i = 0; i < len; i++) {
            res = res * 26 + (s.charAt(i) - 'A' + 1);
        }
        return res;
    }
}
```
