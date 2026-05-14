# 字典序的第K小数字

## 题干
给定整数 n 和 k，返回 [1, n] 中字典序第 k 小的数字。字典序即数字按照字符串顺序排序：1, 10, 100, 101, ... 11, 12, ... 2, 20...
![image 5.png](image%205.png)

![image 6.png](image%206.png)

## 复杂度
时间：{{c1::O(log n)}} — 在十叉树上逐层移动
空间：{{c1::O(1)}}

## 关键技巧
将问题建模为十叉树的先序遍历：
getCount(prefix, n)：统计以 prefix 为前缀且在 [1,n] 内的节点数量
每层：next = prefix+1，当前层节点数 = min(n+1, next) - cur
然后 cur *= 10, next *= 10 进入下一层
判断逻辑：cur + count > k 则在子树内，prefix *= 10 深入；否则 prefix++ 跳到兄弟。

## 题解(十叉树遍历)
将问题建模为十叉树先序遍历，getCount统计以prefix为前缀的节点数，若k在子树内则深入，否则向右兄弟移动。

```java
class Solution {
    public int findKthNumber(int n, int k) {
        int prefix = 1;
        int cur = 1;
        while (cur < k) {
            int count = getCount(prefix, n);
            if (cur + count > k) {
                prefix *= 10;
                cur++;
            } else {
                prefix++;
                cur += count;
            }
        }
        return prefix;
    }

    public int getCount(int prefix, int n) {
        int cur = prefix;
        int next = prefix + 1;
        int resCount = 0;
        while (cur <= n) {
            resCount += Math.min(n + 1, next) - cur;
            cur *= 10;
            next *= 10;
        }
        return resCount;
    }
}
```
