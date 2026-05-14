# 反转链表 II

## 题干
反转从位置 m 到 n 的链表。1 <= m <= n <= 链表长度。
![image 1.png](image%201.png)

## 复杂度
时间：O(n) — 最坏遍历到 n
空间：O(1) — 原地反转

## 关键技巧
1. dummy节点：防止 m=1 时头节点丢失
2. 找到第 m-1 个节点（反转区间的前驱）
3. 对 [m, n] 区间执行标准链表反转
4. 重新连接：区间前驱.next = 反转后头；区间原头.next = 原 n.next

## 题解
dummy节点找到前驱，反转[m,n]区间后重新连接。

```java
class Solution {
    public ListNode reverseBetween(ListNode head, int m, int n) {
        ListNode res = new ListNode(0);
        res.next = head;
        ListNode node = res;
        // find the node before the reversal segment
        for (int i = 1; i < m; i++) {
            node = node.next;
        }
        ListNode nextHead = node.next;
        ListNode next = null;
        ListNode pre = null;
        // reverse from m to n
        for (int i = m; i <= n; i++) {
            next = nextHead.next;
            nextHead.next = pre;
            pre = nextHead;
            nextHead = next;
        }
        // reconnect
        node.next.next = next;
        node.next = pre;
        return res.next;
    }
}
```

## 对比
与 反转链表 的区别：全反转无需找前驱、无需重连
与 K个一组 的区别：K个一组分段多次反转，II 只反转一段
