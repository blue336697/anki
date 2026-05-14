# x 的平方根

## 题干
给你一个非负整数 x，计算并返回 x 的算术平方根。由于返回类型是整数，结果只保留整数部分，小数部分将被舍去。不允许使用内置指数函数和算符。

## 复杂度
二分法：时间 {{c1::O(log x)}}，空间 {{c1::O(1)}}
牛顿迭代：时间 {{c1::O(log x)}}（二次收敛），空间 {{c1::O(1)}}

## 关键技巧
二分法本质：找 <=x 的最大元素（与搜索插入位置找 >=x 的最小元素相对应）。
范围查询规律：<= target 返回 right；>= target 返回 left。
牛顿法：利用切线逼近零点，x_{n+1} = (x_n + N/x_n) / 2，收敛极快。

## 题解(二分查找)
找小于等于x的最大整数平方根：mid*mid<=x时记录并向右逼近；注意用long防溢出。

```java
class Solution {
    public int mySqrt(int x) {
        long left = 0, right = 10000000;
        long res = 0;
        while (left <= right) {
            long mid = (left + right) / 2;
            if (mid * mid <= x) {
                res = mid;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return (int) res;
    }
}
```

## 题解(牛顿迭代)
牛顿迭代公式：x_{n+1} = (x_n + N/x_n) / 2，二次收敛速度极快。

```java
class Solution {
    int temp;

    public int mySqrt(int x) {
        temp = x;
        if (x == 0)
            return 0;
        return (int) sqrts(x);
    }

    public double sqrts(double x) {
        double res = (x + temp / x) / 2;
        if (res == x) {
            return x;
        } else {
            return sqrts(res);
        }
    }
}
```
