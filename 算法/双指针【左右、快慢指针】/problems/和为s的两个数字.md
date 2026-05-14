# 和为s的两个数字

## 题干
输入一个递增排序的数组和一个数字 target，在数组中查找两个数，使得它们的和正好是 target。
![image 6.png](image%206.png)

## 指针策略
左右指针 low=0, high=n-1 对撞。
sum>target → {{c1::high--}}；sum<target → {{c1::low++}}
sum==target → {{c1::返回结果}}
前提：数组{{c1::已排序}}

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(1)}}

## 题解(对撞指针)
利用递增特性，sum偏大则high--，偏小则low++。
```java
class Solution {
    public int[] twoSum(int[] nums, int target) {
        int low = 0;
        int high = nums.length - 1;
        int[] res = new int[2];
        while(true){
            if(nums[low] + nums[high] == target){
                res[0] = nums[low];
                res[1] = nums[high];
                return res;
            } else if(nums[low] + nums[high] > target)
                high--;
            else if(nums[low] + nums[high] < target)
                low++;
        }
    }
}
```
