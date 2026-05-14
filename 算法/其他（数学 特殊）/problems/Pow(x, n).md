# Pow(x, n)

## 题干
实现 pow(x, n)，即计算 x 的 n 次幂函数（即 x^n）。n 可以是负数。
![image 3.png](image%203.png)

![image 4.png](image%204.png)

## 复杂度
时间：{{c1::O(log n)}} — 指数每次折半
空间：{{c1::O(1)}}（迭代）/ {{c1::O(log n)}}（递归）

## 关键技巧
快速幂核心：指数折半。
迭代法：for(i=n; i!=0; i/=2)，奇数轮 res*=x，每轮 x*=x。
递归法：n为偶数时返回 myPow(x*x, n/2)，奇数时多乘一个 x（负数乘 1/x）。
时间复杂度 O(log n)，比暴力 O(n) 快得多。

## 题解(快速幂-迭代)
指数每次折半，奇数轮累乘当前x，每轮x自乘，处理负数时取倒数。

```java
public double myPow(double x, int n) {
    double res = 1.0;
    for (int i = n; i != 0; i /= 2) {
        if (i % 2 != 0) {
            res *= x;
        }
        x *= x;
    }
    return n < 0 ? 1 / res : res;
}
```

## 题解(快速幂-递归)
位运算判断奇偶：(n & 1) == 0 即偶数，递归每次折半，负数时在外层乘1/x。

```java
public double myPow(double x, int n) {
    if (n == 0) {
        return 1.0;
    } else if ((n & 1) == 0) {
        return myPow(x * x, n / 2);
    } else {
        return (n > 0 ? x : 1.0 / x) * myPow(x * x, n / 2);
    }
}
```
