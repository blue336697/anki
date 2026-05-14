# 下一个更大元素 II

## 题干
给定一个循环数组 nums，返回数组中每个元素的下一个更大的元素。
如果不存在则输出 -1。循环数组：数组的最后一个元素的下一个元素是数组的第一个元素。
![image 8.png](image%208.png)

## 复杂度
时间：{{c1::O(n)}} — 遍历2n次，每个元素入栈出栈各一次
空间：{{c1::O(n)}} — 栈空间

## 关键技巧
循环数组的处理技巧：遍历2n次，用 i%n 访问。
第一遍 (0~n-1)：正常入栈处理
第二遍 (n~2n-1)：只处理栈中剩余元素，不入栈（因为都已入过）
用 Arrays.fill(res, -1) 初始化，未找到的就保持 -1。

## 题解(单调栈+循环)
核心：遍历2n次模拟循环，i%n下标。i<n时才入栈防止重复。

```java
class Solution {
    public int[] nextGreaterElements(int[] nums) {
        int n = nums.length;
        int[] res = new int[n];
        Arrays.fill(res, -1);
        Stack<Integer> stack = new Stack<>();
        for (int i = 0; i < n * 2; i++) {
            while (!stack.isEmpty() && nums[i % n] > nums[stack.peek()])
                res[stack.pop()] = nums[i % n];
            if (i < n)
                stack.push(i % n);
        }
        return res;
    }
}
```

## 策略
单调递增栈 + 循环数组：遍历{{c1::2*n}}次（模拟循环）。
用 {{c1::i % n}} 访问数组元素，实现循环遍历。
栈内存储下标，栈底→栈顶对应元素{{c1::递减}}。
当 i < n 时才将下标入栈（避免重复入栈）。
