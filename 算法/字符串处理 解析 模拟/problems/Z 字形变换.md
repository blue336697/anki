# Z 字形变换

## 题干
将一个给定字符串 s 根据给定的行数 numRows，以从上往下、从左到右进行 Z 字形排列。返回按行读取得到的字符串。

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(n)}} — 每行一个 StringBuilder

## 关键技巧
不需要真的构造 Z 字形矩阵，只需模拟行的上下移动：
1. 用 List<StringBuilder> 存储每行的字符
2. flag 变量控制当前行号的增减方向：遇第一行向下(+1)，遇最后一行向上(-1)
3. 最后按行拼接即得结果。空间 O(numRows + n)，时间 O(n)。

## 题解(flag转向)
flag 控制上下移动方向，到达边界时反转 flag。

```java
class Solution {
    public String convert(String s, int numRows) {
        if (numRows < 2)
            return s;
        List<StringBuilder> rows = new ArrayList<StringBuilder>();
        for (int i = 0; i < numRows; i++)
            rows.add(new StringBuilder());
        int i = 0, flag = -1;
        for (char ch : s.toCharArray()) {
            rows.get(i).append(ch);
            if (i == 0 || i == numRows - 1)
                flag = -flag;
            i += flag;
        }
        StringBuilder res = new StringBuilder();
        for (StringBuilder row : rows)
            res.append(row);
        return res.toString();
    }
}
```
