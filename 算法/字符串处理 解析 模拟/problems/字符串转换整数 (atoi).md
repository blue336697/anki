# 字符串转换整数 (atoi)

## 题干
实现一个 atoi 函数，将字符串转换成整数。规则：1. 丢弃前导空格；2. 检查正负符号；3. 读入数字直到非数字或结尾；4. 如果整数超过32位有符号整数范围，返回边界值。
![image.png](image.png)

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(n)}} — charArray 存储

## 关键技巧
atoi 实现的四个关键步骤：
1. 去前导空格：while 跳过空格字符
2. 符号处理：仅第一个符号有效，用 sign=±1 记录
3. 溢出判断（核心）：MAX/10 提前判断，digit > MAX%10 精确判断最后一位
4. 符号参与计算：res = res*10 + sign*digit，避免最后才乘 sign 导致负溢出

## 题解(模拟)
四步：去空格→取符号→溢出判断→逐位转换，sign 参与运算统一正负。

```java
class Solution {
    public int myAtoi(String str) {
        int len = str.length();
        char[] charArray = str.toCharArray();
        int index = 0;
        while (index < len && charArray[index] == ' ') {
            index++;
        }
        if (index == len) {
            return 0;
        }
        int sign = 1;
        char firstChar = charArray[index];
        if (firstChar == '+') {
            index++;
        } else if (firstChar == '-') {
            index++;
            sign = -1;
        }
        int res = 0;
        while (index < len) {
            char currChar = charArray[index];
            if (currChar > '9' || currChar < '0') {
                break;
            }
            if (res > Integer.MAX_VALUE / 10 ||
                (res == Integer.MAX_VALUE / 10 &&
                 (currChar - '0') > Integer.MAX_VALUE % 10)) {
                return Integer.MAX_VALUE;
            }
            if (res < Integer.MIN_VALUE / 10 ||
                (res == Integer.MIN_VALUE / 10 &&
                 (currChar - '0') > -(Integer.MIN_VALUE % 10))) {
                return Integer.MIN_VALUE;
            }
            res = res * 10 + sign * (currChar - '0');
            index++;
        }
        return res;
    }
}
```
