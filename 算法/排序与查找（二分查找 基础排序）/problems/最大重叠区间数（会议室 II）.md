# 最大重叠区间数（会议室 II）
<!-- aliases: 会议室II, 最大重叠区间数 -->
<!-- tags: source::字节 pattern::扫描线 pattern::最小堆 -->

## 题干
给定若干半开时间区间 `[start,end)`，求同一时刻最多有多少个区间重叠。

这与“至少需要多少个会议室才能安排所有会议”完全等价：某时刻同时进行几个会议，就至少需要几个会议室；全局最大并发数就是最少会议室数。

由于使用半开区间，某会议在时间 t 结束、另一会议恰好在 t 开始时不冲突。

## 扫描线状态
把每个区间拆成两个事件：

- `(start,+1)`：活跃区间数增加
- `(end,-1)`：活跃区间数减少

按时间升序处理事件；同一时间必须{{c1::先处理 -1 的结束事件，再处理 +1 的开始事件}}，才能符合 `[start,end)` 的语义。

扫描过程中 `active` 表示当前活跃区间数，所有时刻的 `active` 最大值就是答案。

## 最小堆状态
另一种写法是按开始时间排序，用小根堆保存{{c1::当前仍在进行的区间结束时间}}。

处理新区间前，弹出所有 `end <= currentStart` 的已结束区间；再把当前结束时间入堆。此时堆大小就是当前并发数。

堆法容易扩展为“具体分配哪个会议室”；只求最大重叠数时，扫描线通常更直接。

## 复杂度
两种做法都需要排序：

- 扫描线：2n 个事件排序 O(n log n)，扫描 O(n)，额外空间 O(n)
- 最小堆：区间排序 O(n log n)，每个区间至多入堆出堆一次 O(n log n)，堆空间 O(n)

## 题解(扫描线)
```java
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class Solution {
    public int minMeetingRooms(int[][] intervals) {
        List<int[]> events = new ArrayList<>(intervals.length * 2);
        for (int[] interval : intervals) {
            events.add(new int[] {interval[0], 1});
            events.add(new int[] {interval[1], -1});
        }
        events.sort(
                Comparator.<int[]>comparingInt(event -> event[0])
                        .thenComparingInt(event -> event[1]));

        int active = 0;
        int maximum = 0;
        for (int[] event : events) {
            active += event[1];
            maximum = Math.max(maximum, active);
        }
        return maximum;
    }
}
```

## 题解(排序+最小堆)
```java
import java.util.Arrays;
import java.util.Comparator;
import java.util.PriorityQueue;

class Solution {
    public int minMeetingRooms(int[][] intervals) {
        Arrays.sort(intervals, Comparator.comparingInt(interval -> interval[0]));
        PriorityQueue<Integer> endTimes = new PriorityQueue<>();
        int maximum = 0;

        for (int[] interval : intervals) {
            while (!endTimes.isEmpty() && endTimes.peek() <= interval[0]) {
                endTimes.poll();
            }
            endTimes.offer(interval[1]);
            maximum = Math.max(maximum, endTimes.size());
        }
        return maximum;
    }
}
```
