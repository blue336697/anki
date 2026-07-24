# 合并K个排序链表
<!-- aliases: 多路有序日志流合并 -->
<!-- tags: source::leetcode source::字节 pattern::多路归并 -->

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
import java.util.PriorityQueue;
import java.util.Queue;

class Solution {
    public ListNode mergeKLists(ListNode[] lists) {
        Queue<ListNode> pq =
                new PriorityQueue<>((v1, v2) -> Integer.compare(v1.val, v2.val));
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
重复直到堆为空。比较器使用 {{c1::Integer.compare(a.val, b.val)}}，避免直接相减溢出。

## 字节变形：多路有序日志流合并
给定 k 路分别按时间戳升序排列的日志流，合并成全局有序日志列表。

它与合并 K 个有序链表的状态完全相同：

- 堆中只保存{{c1::每一路当前尚未输出的第一条日志}}
- 弹出全局最小日志后，只把{{c1::同一路的下一条日志}}加入堆
- 堆大小最多为 k，而不是总日志数 N

堆节点必须携带日志、流编号和流内下标。时间戳相同时可按流编号排序，得到确定性的跨流输出顺序；如果还要求同一流内稳定，原下标天然保证顺序。

总日志数为 N 时，时间 O(N log k)，额外空间 O(k)，返回结果空间 O(N)。

## 题解(多路日志归并)
```java
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;

class Solution {
    public List<Log> mergeLogs(List<List<Log>> streams) {
        PriorityQueue<Cursor> minimums = new PriorityQueue<>(
                Comparator.<Cursor>comparingLong(cursor -> cursor.log.timestamp)
                        .thenComparingInt(cursor -> cursor.streamIndex));

        for (int streamIndex = 0; streamIndex < streams.size(); streamIndex++) {
            if (!streams.get(streamIndex).isEmpty()) {
                minimums.offer(
                        new Cursor(streams.get(streamIndex).get(0), streamIndex, 0));
            }
        }

        List<Log> result = new ArrayList<>();
        while (!minimums.isEmpty()) {
            Cursor current = minimums.poll();
            result.add(current.log);

            int nextIndex = current.elementIndex + 1;
            List<Log> source = streams.get(current.streamIndex);
            if (nextIndex < source.size()) {
                minimums.offer(new Cursor(
                        source.get(nextIndex), current.streamIndex, nextIndex));
            }
        }
        return result;
    }

    static class Log {
        private final long timestamp;
        private final String message;

        Log(long timestamp, String message) {
            this.timestamp = timestamp;
            this.message = message;
        }
    }

    private static class Cursor {
        private final Log log;
        private final int streamIndex;
        private final int elementIndex;

        private Cursor(Log log, int streamIndex, int elementIndex) {
            this.log = log;
            this.streamIndex = streamIndex;
            this.elementIndex = elementIndex;
        }
    }
}
```
