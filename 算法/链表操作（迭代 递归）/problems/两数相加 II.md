# 两数相加 II

## 题干
给定两个非空链表代表两个非负整数，最高位在链表头。
求两数之和，以相同链表形式返回。（正序存储）

## 复杂度
时间：O(m+n) — 两次反转+一次相加
空间：O(m+n) — 结果链表（或O(m+n)用栈）

## 关键技巧
正向存储 → 先反转再加再反转：
1. l1 = reverse(l1)
2. l2 = reverse(l2)
3. 调用 两数相加 逻辑相加
4. return reverse(结果)

或用栈：两个栈分别存l1、l2的值，然后逐个弹出相加

## 题解
正序存储→先反转两个链表→低位相加→再反转结果回来。

```java
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode prev = new ListNode(0);
        int carry = 0;
        ListNode cur = prev;
        l1 = reverse(l1);
        l2 = reverse(l2);
        while (l1 != null || l2 != null) {
            int x = l1 != null ? l1.val : 0;
            int y = l2 != null ? l2.val : 0;
            int sum = x + y + carry;
            carry = sum / 10;
            sum = sum % 10;
            cur.next = new ListNode(sum);
            cur = cur.next;
            if (l1 != null) {
                l1 = l1.next;
            }
            if (l2 != null) {
                l2 = l2.next;
            }
        }
        if (carry == 1) {
            cur.next = new ListNode(carry);
        }
        return reverse(prev.next);
    }

    public ListNode reverse(ListNode node) {
        ListNode pre = null;
        ListNode cur = node;
        ListNode tail = null;
        while (cur != null) {
            tail = cur.next;
            cur.next = pre;
            pre = cur;
            cur = tail;
        }
        return pre;
    }
}
```

## 对比
与 两数相加 的核心区别：本题数字正序存储（高位在头），需先反转
与 链表求和 的关系：链表求和=两数相加（逆序存储）
