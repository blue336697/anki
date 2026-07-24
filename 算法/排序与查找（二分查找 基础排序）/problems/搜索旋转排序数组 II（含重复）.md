# 搜索旋转排序数组 II（含重复）
<!-- anki-deck: 搜索旋转排序数组II -->
<!-- tags: source::字节 variant::含重复 -->

## 题干
给定一个可能包含重复元素的旋转非递减数组 `nums` 和目标值 `target`，判断目标值是否存在。

本题只返回布尔值。它不同于：

- “搜索旋转排序数组”：元素互不相同，要求返回下标，时间可保证 O(log n)
- “含重复并返回最小下标”的自定义题：要求全局最小物理下标，直接线性扫描更清晰可靠

## 重复元素破坏了什么
无重复时，通过 `nums[left] <= nums[mid]` 可以判断左半边有序。但若：

`nums[left] == nums[mid] == nums[right]`

例如 `[1,0,1,1,1]`，旋转点可能在左边；在 `[1,1,1,0,1]` 中又可能在右边。此时仅凭三个值无法判断哪一半有序。

处理方式是 `left++`、`right--`：两端与 mid 相同，而 mid 已确认不等于 target，所以丢弃这两个重复边界不会漏掉唯一的目标值。

## 二分分支
先检查 `nums[mid] == target`。排除三点相等后：

1. 若 `nums[left] <= nums[mid]`，左半边有序
2. 否则右半边有序
3. 判断 target 是否位于有序半边的闭开值域内，决定保留哪一侧

值域边界必须一边包含、一边排除 mid，因为 mid 已经检查过。

## 复杂度
平均时间：{{c1::O(log n)}}。
最坏时间：{{c1::O(n)}} — 大量相同元素时每轮只能收缩常数个边界。
空间：{{c1::O(1)}}。

因此“存在重复元素”使最坏时间不再能保证 O(log n)，这是信息不足导致的下界，不只是实现不够优化。

## 题解(二分+重复边界收缩)
```java
class Solution {
    public boolean search(int[] nums, int target) {
        int left = 0;
        int right = nums.length - 1;

        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                return true;
            }

            if (nums[left] == nums[mid] && nums[mid] == nums[right]) {
                left++;
                right--;
            } else if (nums[left] <= nums[mid]) {
                if (nums[left] <= target && target < nums[mid]) {
                    right = mid - 1;
                } else {
                    left = mid + 1;
                }
            } else {
                if (nums[mid] < target && target <= nums[right]) {
                    left = mid + 1;
                } else {
                    right = mid - 1;
                }
            }
        }
        return false;
    }
}
```
