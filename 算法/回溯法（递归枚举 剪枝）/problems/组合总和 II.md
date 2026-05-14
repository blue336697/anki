# 组合总和 II

## 题干
给定一个可能包含重复元素的数组 candidates 和一个目标数 target，找出 candidates 中所有可以使数字和为 target 的组合。candidates 中的每个数字在每个组合中只能使用一次。

## 回溯-选择列表
选择列表 = {{c1::candidates[i..n-1]}}（从 begin 开始）
限制：{{c1::每个数字只能用一次}} → 递归传 i+1
去重：{{c1::同层跳过相同元素}} i>begin && nums[i]==nums[i-1]

## 回溯-终止+剪枝
终止条件：{{c1::target == 0}} → 加入结果
剪枝1：{{c1::target < nums[i]}} → break（排序后）
剪枝2：{{c1::i>begin && nums[i]==nums[i-1]}} → continue（同层去重，不是 i>0）

## 复杂度
时间：{{c1::O(2^n)}} — 每个元素选或不选
空间：{{c1::O(n)}} — 递归深度

## 题解(DFS+剪枝)
去重条件用 i>begin 而非 i>0，因为要保留同一树枝上的重复数字。

```java
class Solution {
    List<List<Integer>> res = new ArrayList<>();
    List<Integer> list = new ArrayList<>();
    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        int n = candidates.length;
        Arrays.sort(candidates);
        dfs(candidates, target, 0, list);
        return res;
    }

    public void dfs(int[] nums, int target, int begin, List<Integer> list) {
        if (target == 0) {
            res.add(new ArrayList<>(list));
            return;
        }
        for (int i = begin; i < nums.length; i++) {
            if (target < nums[i])
                break;
            if (i > begin && nums[i] == nums[i - 1])
                continue;
            list.add(list.size(), nums[i]);
            dfs(nums, target - nums[i], i + 1, list);
            list.remove(list.size() - 1);
        }
    }
}
```

## 对比
与组合总和 I 区别：II 需排序+同层去重(i>begin && ...)，且每个数字只能用一次(传i+1)。
去重条件用 i>begin 而非 i>0，因为要保留同一树枝上的重复数字。
