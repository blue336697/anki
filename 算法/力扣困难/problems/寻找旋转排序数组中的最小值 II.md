# 寻找旋转排序数组中的最小值 II

## 题干
已知一个长度为 n 的数组，预先按照升序排列，经由 1 到 n 次旋转后，得到输入数组。数组中可能存在重复元素。请找出数组中的最小元素。与 153 题的区别：本题允许重复元素。

## 复杂度
时间：最坏 {{c1::O(n)}}（全相同元素时），平均 {{c1::O(log n)}}
空间：{{c1::O(1)}}

## 关键技巧
153（无重复）vs 154（有重复）的核心区别：
nums[mid] == nums[right] 时丢失了单调性信息，无法判断最小值在左还是右。
因此只能保守地 right--，最坏退化为 O(n)。
其他情况与153相同：nums[mid]>nums[right]→最小值在右，left=mid+1；nums[mid]<nums[right]→最小值在左或就是mid，right=mid。

## 题解(二分查找)
与153的唯一区别：nums[mid]==nums[right]时无法判断，只能right--缩小范围，最坏退化为O(n)。

```java
class Solution {
    public int findMin(int[] nums) {
        int left = 0;
        int right = nums.length - 1;
        while(left < right){
            int mid = left + (right - left) / 2;
            if(nums[mid] > nums[right])
                left = mid + 1;
            else if(nums[mid] < nums[right])
                right = mid;
            else
                right--;
        }
        return nums[left];
    }
}
```
