# Excel表列名称

## 题干
给你一个整数 columnNumber，返回它在 Excel 表中相对应的列名称。A→1, B→2, ..., Z→26, AA→27, AB→28...
![image 2.png](image%202.png)

## 复杂度
时间：{{c1::O(log n)}} — 每次除以 26（底数为 26）
空间：{{c1::O(1)}}

## 关键技巧
核心陷阱：Excel 列号是 1-indexed（A=1），但取模运算需要 0-indexed。
所以每次循环先 cn--，这样 A→0, B→1, ..., Z→25。
最后需要 reverse 因为先算出来的是低位。

## 题解
关键：先 cn-- 再取模。因为 A 对应 1 而非 0，需要将 1-indexed 转为 0-indexed。

```java
class Solution {
    public String convertToTitle(int cn) {
        StringBuilder sb = new StringBuilder();
        while (cn > 0) {
            cn--;
            sb.append((char)(cn % 26 + 'A'));
            cn /= 26;
        }
        sb.reverse();
        return sb.toString();
    }
}
```
