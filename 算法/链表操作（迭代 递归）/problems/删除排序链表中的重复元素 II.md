# 删除排序链表中的重复元素 II

## 题干
删除排序链表中所有含有重复数字的节点，只保留原始链表中没有重复出现的数字。

## 复杂度
时间：O(n) — 一次遍历
空间：O(1) — 原地修改

## 关键技巧
1. dummy节点 — 头节点可能被删除
2. pre 指向已确认不重复的最后一个节点
3. cur 遍历跳过所有值相等的节点，找到右边界
4. 若 pre.next == cur，说明cur没有重复，pre后移
5. 否则 pre.next = cur.next（跳过cur这一段重复的）

## 题解(迭代)
dummy + pre/cur双指针，pre.next==cur说明无重复则pre后移，否则跳过重复区间。

```java
class Solution {
    public ListNode deleteDuplicates(ListNode head) {
        if (head == null)
            return null;
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode pre = dummy;
        ListNode cur = head;
        while (cur != null) {
            while (cur.next != null && cur.val == cur.next.val)
                cur = cur.next;
            if (pre.next == cur)
                pre = cur;
            else
                pre.next = cur.next;
            cur = cur.next;
        }
        return dummy.next;
    }
}
```

## 题解(递归)
递归：遇到重复则跳过全部重复节点，递归处理后续。

```java
class Solution {
    public ListNode deleteDuplicates(ListNode head) {
        if (head == null || head.next == null)
            return head;
        if (head.val != head.next.val) {
            head.next = deleteDuplicates(head.next);
        } else {
            ListNode temp = head.next.next;
            while (temp != null && temp.val == head.val)
                temp = temp.next;
            return deleteDuplicates(temp);
        }
        return head;
    }
}
```

## 对比
与 删除重复元素 的区别：本题全部删除重复元素，前者保留一个
本题必须用 dummy（头节点可能被删），前者不需要
