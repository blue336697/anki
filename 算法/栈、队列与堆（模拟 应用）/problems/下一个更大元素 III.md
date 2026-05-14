# 下一个更大元素 III

## 题干
给定一个32位正整数 n，找出符合32位整数范围的下一个更大的元素。
如果不存在这样的整数，返回 -1。本质是求下一个排列。

## 复杂度
时间：{{c1::O(n log n)}} — 主要是排序开销
空间：{{c1::O(n)}} — 字符数组

## 关键技巧
本质是"下一个排列"问题，与单调栈关系不大。
核心：从右找到第一个升序对，这是可以变大的位置。
将后半段排序后，选其中刚好大于分界点的数与分界点交换。
注意：结果可能超出int范围，需用long检查并返回-1。

## 题解(下一个排列)
从右找第一个升序对，排序后半段，找>分界点的最小数交换。

```java
class Solution {
    public int nextGreaterElement(int n) {
        char[] chars = String.valueOf(n).toCharArray();
        StringBuilder sb = new StringBuilder();
        int len = chars.length;
        for (int i = len - 1; i > 0; i--) {
            if (chars[i] > chars[i - 1]) {
                Arrays.sort(chars, i, len);
                for (int j = i; j < len; j++) {
                    if (chars[j] > chars[i - 1]) {
                        char temp = chars[j];
                        chars[j] = chars[i - 1];
                        chars[i - 1] = temp;
                        for (int k = 0; k < len; k++) {
                            sb.append(chars[k]);
                        }
                        long res = Long.parseLong(sb.toString());
                        if (res > Integer.MAX_VALUE)
                            return -1;
                        else
                            return (int)res;
                    }
                }
            }
        }
        return -1;
    }
}
```

## 策略
下一个排列算法：
1. 从右向左找第一个{{c1::升序对}} (chars[i] > chars[i-1])
2. 将 i-1 之后的子数组{{c1::排序}}（升序）
3. 在排序后的子数组中找第一个{{c1::大于}} chars[i-1] 的数并交换
4. 检查结果是否超出{{c1::Integer.MAX_VALUE}}
