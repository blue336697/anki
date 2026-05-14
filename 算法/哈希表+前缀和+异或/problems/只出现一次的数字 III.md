# 只出现一次的数字 III

## 题干
给定一个整数数组 nums，其中恰好有两个元素只出现一次，其余所有元素均出现两次。找出那两个只出现一次的元素。

## 复杂度
HashSet法：时间 {{c1::O(n)}}，空间 {{c1::O(n)}}
XOR+分组法：时间 {{c1::O(n)}}，空间 {{c1::O(1)}}

## 关键技巧
全异或得到 temp = a^b。temp≠0说明a和b至少有一位不同。
mask = temp & (-temp)：取 temp 最低位的 1，a和b在这一位上必然不同。
按 mask 分组异或，降维为两个"只出现一次的数字 I"。

## 题解(HashSet)
与只出现一次的数字 I 思路相同，最后 set 中剩两个元素。

```java
class Solution {
    public int[] singleNumber(int[] nums) {
        int len = nums.length;
        if(len < 2)
            return null;
        Set<Integer> set = new HashSet<>();
        for(int i = 0; i < len; i++){
            if(!set.add(nums[i])){
                set.remove(nums[i]);
            }
        }
        int[] res = new int[2];
        int i = 0;
        for(int item : set){
            res[i++] = item;
        }
        return res;
    }
}
```

## 题解(XOR+分组)
全异或得到 temp=a^b≠0，mask取最低位1将数组分成两组，a和b各在一边。

```java
class Solution {
    public int[] singleNumber(int[] nums) {
        int[] res = new int[2];
        int temp = 0;
        for(int num : nums){
            temp ^= num;
        }
        int mask = temp & (-temp);
        for (int num : nums) {
            if ((num & mask) == 0) {
                res[0] ^= num;
            } else {
                res[1] ^= num;
            }
        }
        return res;
    }
}
```
