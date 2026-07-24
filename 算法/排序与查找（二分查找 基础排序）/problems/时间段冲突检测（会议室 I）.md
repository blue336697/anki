# 时间段冲突检测（会议室 I）
<!-- anki-deck: 时间段冲突检测 -->
<!-- tags: source::字节 pattern::区间排序 -->

## 题干
给定若干半开时间段 `[start,end)`，判断一个人能否参加全部时间段：若任意两个区间冲突返回 false，否则返回 true。

半开区间意味着 `[1,3)` 与 `[3,5)` 不冲突，时间 3 只属于后一个区间。

## 排序后的局部判定
按开始时间升序排列后，若存在冲突，则当前区间一定会与前面尚未结束的区间发生重叠。

从左到右扫描，一旦发现：

`current.start < {{c1::previous.end}}`

即可返回 false。端点相等不冲突，因此不能写成 `<=`。

## 与会议室 II 的区别
会议室 I 只问{{c1::是否存在任何冲突}}，发现第一处重叠即可结束。
会议室 II 问{{c1::最大并发区间数}}，需要扫描线或最小堆统计峰值。

两题共享“先按时间排序”的入口，但输出目标和维护状态不同。

## 复杂度
时间：{{c1::O(n log n)}} — 排序占主导，扫描最多 n-1 次比较。
辅助空间：取决于排序实现；扫描本身只使用 O(1) 状态。

## 题解(按开始时间排序)
```java
import java.util.Arrays;
import java.util.Comparator;

class Solution {
    public boolean canAttendAll(int[][] intervals) {
        Arrays.sort(intervals, Comparator.comparingInt(interval -> interval[0]));
        for (int index = 1; index < intervals.length; index++) {
            if (intervals[index][0] < intervals[index - 1][1]) {
                return false;
            }
        }
        return true;
    }
}
```
