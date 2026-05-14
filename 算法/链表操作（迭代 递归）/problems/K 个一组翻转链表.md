# K 个一组翻转链表

## 题干
给定一个链表，每 k 个节点一组进行翻转，返回修改后的链表。
如果节点总数不是 k 的整数倍，保持最后剩余节点原有顺序。
![34457_XsCvOoSeE4HnyUtb.png](34457_XsCvOoSeE4HnyUtb.png)

## 复杂度
时间：O(n) — 每个节点访问两次（找尾+反转）
空间：O(1) — 原地操作

## 关键技巧
1. dummy节点 — 防止头节点被反转
2. pre 指向每段反转区间的前驱
3. cur 找每段末尾（走k步），不足k个则break
4. 保存断开后的 next，反转区间，重新连接
5. 更新 pre 和 cur 为反转后末尾（即原区间头 start）

## 题解
找到k个节点→断开→反转→重连→更新pre/cur。

```java
class Solution {
    public ListNode reverseKGroup(ListNode head, int k) {
        if (head == null || head.next == null) {
            return head;
        }
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode pre = dummy;
        ListNode cur = dummy;
        while (cur.next != null) {
            for (int i = 0; i < k && cur != null; i++) {
                cur = cur.next;
            }
            if (cur == null) {
                break;
            }
            ListNode next = cur.next;
            cur.next = null;
            ListNode start = pre.next;
            pre.next = reverse(start);
            start.next = next;
            pre = start;
            cur = start;
        }
        return dummy.next;
    }

    public ListNode reverse(ListNode head) {
        if (head == null || head.next == null) {
            return head;
        }
        ListNode pre = null;
        ListNode cur = head;
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
