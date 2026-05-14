# 第N个数字

## 题干
在无限的整数序列 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ... 中找到第 n 位数字。
![image 7.png](image%207.png)

## 复杂度
时间：{{c1::O(log n)}} — 逐位扩大范围查找
空间：{{c1::O(1)}}

## 关键技巧
数学三步走：
1. 确定位数范围：1位占10个位置，2位占180个，3位占2700个...i位占 i*10^i 个
2. 定位具体数字：用 k/i 确定第几个数，k%i 确定该数的第几位
3. 取字符：charAt(k%i) - "0" 转换回数字
k 随着 i 增大不断累加 10^i（补零），直到 k 落入当前位数范围。

## 题解(数学定位)
先确定n在哪个位数范围，然后定位到具体数字，最后按位取字符。

```java
class Solution {
    public int findNthDigit(int n) {
        long k = n;
        for (int i = 1; ; i++) {
            if (i * Math.pow(10, i) > k) {
                return Long.toString((int) (k / i))
                    .charAt((int) (k % i)) - '0';
            }
            k += Math.pow(10, i);
        }
    }
}
```
