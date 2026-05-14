# 全排列 II

## 题干
给定一个可包含重复数字的序列 nums，按任意顺序返回所有不重复的全排列。
![image 1.png](image%201.png)

## 回溯-选择列表
选择列表 = {{c1::nums}}
去重关键：{{c1::排序后}}用 used[i] 数组标记，{{c1::同层跳过相同元素}}

## 回溯-终止+剪枝
终止条件：{{c1::list.size() == nums.length}}
剪枝策略：{{c1::i>0 && nums[i]==nums[i-1] && !used[i-1]}} → continue（同层去重）
{{c1::used[i]}} 标记同一树枝已使用的元素

## 复杂度
时间：{{c1::O(n!)}} — 最坏情况
空间：{{c1::O(n)}} — 递归深度+used数组

## 题解(回溯+剪枝)
排序后用used数组防同层重复和同枝重复。used[i-1]==false表示同层已用过。

```java
class Solution {
    List<List<Integer>> res = new ArrayList<>();
    public List<List<Integer>> permuteUnique(int[] nums) {
        if (nums.length == 1) {
            res.add(new ArrayList<Integer>(Arrays.asList(nums[0])));
            return res;
        }
        List<Integer> list = new ArrayList<>();
        boolean[] used = new boolean[nums.length];
        Arrays.sort(nums);
        back(list, nums, used);
        return res;
    }

    public void back(List<Integer> list, int[] nums, boolean[] used) {
        if (list.size() == nums.length) {
            res.add(new ArrayList<>(list));
            return;
        }
        for (int i = 0; i < nums.length; i++) {
            if (i > 0 && nums[i] == nums[i - 1] && used[i - 1] == false)
                continue;
            if (used[i] == false) {
                used[i] = true;
                list.add(nums[i]);
                back(list, nums, used);
                list.remove(list.size() - 1);
                used[i] = false;
            }
        }
    }
}
```

## 对比
与全排列 I 的区别：I 无重复元素，只需 list.contains 防同枝重复；
II 有重复元素，需排序+used数组同时防同层重复和同枝重复。
与字符串的排列：完全相同的模板，只是处理 char[] 而非 int[]。
