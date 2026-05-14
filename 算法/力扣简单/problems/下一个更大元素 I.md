# 下一个更大元素 I

## 题干
nums1 是 nums2 的子集。对于 nums1 中的每个元素，找出在 nums2 中该元素右侧第一个比它大的元素。不存在则返回 -1。

## 复杂度
暴力法：时间 {{c1::O(n*m)}}，空间 {{c1::O(1)}}
单调栈：时间 {{c1::O(n+m)}}，空间 {{c1::O(n)}}

## 关键技巧
优化：单调栈预处理 nums2 中每个元素的「下一个更大元素」，存入 HashMap。
单调递减栈：遇到比栈顶大的元素时，栈顶出栈并记录结果，新元素入栈。
预处理后 nums1 的查询变成 O(1) HashMap 查找。

## 题解(暴力)
先在 nums2 中找到等于 nums1[i] 的元素，再向右找第一个更大的值。

```java
class Solution {
    public int[] nextGreaterElement(int[] nums1, int[] nums2) {

        for (int i = 0; i < nums1.length; i++)
            for (int j = 0; j < nums2.length; j++) {
                int temp = nums1[i];
                if (temp != nums2[j])
                    continue;
                else {
                    int change = findBigger(nums2, j);
                    nums1[i] = change;
                    break;
                }
            }
        return nums1;
    }

    public int findBigger(int[] nums2, int index) {
        for (int i = index + 1; i < nums2.length; i++) {
            if (nums2[index] < nums2[i])
                return nums2[i];
            else
                continue;
        }
        return -1;
    }
}
```
