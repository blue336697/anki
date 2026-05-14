# 两数之和 II - 输入有序数组

## 题干
给你一个下标从 1 开始的整数数组 numbers，该数组已按非递减顺序排列。找出两个数之和等于目标数 target，返回两个数的下标（1-indexed）。

## 复杂度
时间：{{c1::O(n)}} — 双指针一次遍历
空间：{{c1::O(1)}}

## 关键技巧
利用数组有序性：如果 sum > target，则任何与 j 的组合都会更大，所以 j 左移。
如果 sum < target，则任何与 i 的组合都会更小，所以 i 右移。
这本质上是在二维矩阵中搜索，双指针每次排除一行或一列。

## 题解(双指针)
左指针在开头，右指针在末尾，和太大则右指针左移，和太小则左指针右移。

```java
class Solution {
    public int[] twoSum(int[] numbers, int target) {
        int len = numbers.length;
        int i = 0, j = len - 1;
        while (i < j) {
            int sum = numbers[i] + numbers[j];
            if (sum > target)
                j--;
            else if (sum < target)
                i++;
            else
                return new int[]{i + 1, j + 1};
        }
        return new int[]{-1, -1};
    }
}
```
