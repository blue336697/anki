# 链表中倒数第k个节点

## 题干
输入一个链表，输出该链表中倒数第 k 个节点。
![image 8.png](image%208.png)

![image 9.png](image%209.png)

## 指针策略
前后指针：former 先走 {{c1::k 步}}
然后 former 和 latter 一起走，直到 {{c1::former == null}}
此时 {{c1::latter}} 就是倒数第 k 个节点

## 复杂度
时间：{{c1::O(n)}} — 两个指针各走一次
空间：{{c1::O(1)}}

## 题解(前后指针)
former先走k步，然后两个指针一起走直到former为null，latter即为倒数第k个。
```java
class Solution {
    public ListNode getKthFromEnd(ListNode head, int k) {
        ListNode former = head, latter = head;
        for(int i = 0; i < k; i++)
            former = former.next;
        while(former != null) {
            former = former.next;
            latter = latter.next;
        }
        return latter;
    }
}
```
