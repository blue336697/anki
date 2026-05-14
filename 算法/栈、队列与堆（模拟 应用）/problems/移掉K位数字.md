# 移掉K位数字

## 题干
给定一个以字符串表示的非负整数 num，移除这个数中的 k 位数字，使得剩下的数字最小。
![image 3.png](image%203.png)

![image 4.png](image%204.png)

![image 5.png](image%205.png)

![image 6.png](image%206.png)

![image 7.png](image%207.png)

## 复杂度
时间：{{c1::O(n)}} — 每个字符最多入栈出栈一次
空间：{{c1::O(n)}} — StringBuilder

## 关键技巧
核心贪心思想：高位数字越小，整体数字越小。
维护递增栈就是保证越靠前的数字越小。
边界处理：k有剩余说明数字本身已经递增，从末尾移除；结果为空返回"0"；去除前导零。

## 题解(单调栈)
贪心+单调栈：当前字符小于栈顶时移除栈顶。遍历完若k>0从末尾移除。

```java
class solution {
    public String removeKdigits(String num, int k) {
        if (num.length() == k)
            return "0";
        StringBuilder stack = new StringBuilder();
        for (int i = 0; i < num.length(); i++) {
            char ch = num.charAt(i);
            while (k > 0 && stack.length() != 0
                && stack.charAt(stack.length() - 1) > ch) {
                stack.setLength(stack.length() - 1);
                k--;
            }
            if (ch == '0' && stack.length() == 0)
                continue;
            stack.append(ch);
        }
        String res = stack.substring(0, stack.length() - k < 1 ? 0 : stack.length() - k).toString();
        return res.length() == 0 ? "0" : res;
    }
}
```

## 策略
单调递增栈（贪心）：维护数字{{c1::递增}}序列，使高位尽可能小。
遍历时，当栈顶 > 当前数字且还有移除名额(k>0)时，{{c1::弹出栈顶}}，k--。
关键处理：
1. 当前字符为0且栈为空时{{c1::跳过}}（去除前导零）
2. 遍历完若k仍有剩余，从{{c1::末尾}}移除剩余k位
