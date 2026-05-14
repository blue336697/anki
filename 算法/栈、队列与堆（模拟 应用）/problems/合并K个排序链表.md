# 合并K个排序链表

## 题干
给你一个链表数组，每个链表都已经按升序排列。将所有链表合并到一个升序链表中，返回合并后的链表。

## 复杂度
时间：{{c1::O(N log k)}} — N为总节点数，k为链表数，每次堆操作O(log k)
空间：{{c1::O(k)}} — 堆中最多k个节点

## 关键技巧
两种主要方法：
1. 小根堆：PriorityQueue，每次取最小值，O(N log k)
2. 分治法两两合并：递归拆分成两半再合并，O(N log k)，无需额外堆空间
核心：始终取当前K个链表头部的最小值。堆方法更直观，分治法空间更优。

## 题解(小根堆)
比较器 (v1,v2)->v1.val-v2.val 建立小根堆。每次弹出最小节点后将其next入堆。

```java
class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        Queue<ListNode> pq = new PriorityQueue<>((v1, v2) -> v1.val - v2.val);
        for (ListNode node : lists) {
            if (node != null) {
                pq.offer(node);
            }
        }
        ListNode dummyHead = new ListNode(0);
        ListNode tail = dummyHead;
        while (!pq.isEmpty()) {
            ListNode minNode = pq.poll();
            tail.next = minNode;
            tail = minNode;
            if (minNode.next != null) {
                pq.offer(minNode.next);
            }
        }
        return dummyHead.next;
    }
}
```

## 策略
小根堆解法：将所有链表的{{c1::头结点}}加入PriorityQueue。
每次poll出{{c1::最小}}节点接到结果链表尾部，然后将该节点的{{c1::next}}（若不为空）加入堆中。
重复直到堆为空。比较器：(a,b)->{{c1::a.val-b.val}}（升序=小根堆）。
