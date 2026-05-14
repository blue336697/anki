# 在排序数组中查找数字 I

## 题干
统计一个数字在排序数组中出现的次数。
![image 4.png](image%204.png)

## 复杂度
遍历法：时间 {{c1::O(n)}}，空间 {{c1::O(1)}}
二分法：时间 {{c1::O(log n)}}，空间 {{c1::O(1)}}

## 题解(遍历)
遍历统计 target 出现次数，简单直接。

```java
class Solution {
    public int search(int[] nums, int target) {
        if (nums.length == 0
            || target < nums[0]
            || target > nums[nums.length - 1])
            return 0;
        int temp = 0;
        for (int i = 0; i <= nums.length - 1; i++) {
            if (target == nums[i])
                temp++;
        }
        if (temp == 0)
            return 0;
        return temp;
    }
}
```

## 题解(二分)
二分查找 target 的第一个位置和 target+1 的第一个位置，差值即出现次数。
核心：寻找 >= target 的左边界，count = search(target+1) - search(target)。
```java
class Solution {
    public int search(int[] nums, int target) {
        return lowerBound(nums, target + 1) - lowerBound(nums, target);
    }

    private int lowerBound(int[] nums, int target) {
        int left = 0;
        int right = nums.length;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}
```
