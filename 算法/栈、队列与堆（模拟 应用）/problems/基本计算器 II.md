# 基本计算器 II

## 题干
实现一个基本计算器来计算简单的字符串表达式。支持 +、-、*、/、^、%、(、)。整数除法仅保留整数部分。

## 复杂度
时间：{{c1::O(n)}} — 每个字符处理一次
空间：{{c1::O(n)}} — 两个栈

## 关键技巧
双栈法处理表达式求值是经典模式。
核心要点：1. 运算符优先级映射  2. 栈内优先级>=当前时立即计算  3. 括号内的独立计算
前置补0技巧：将 (- 变为 (0-，(+ 变为 (0+)，统一处理负数情况。
calc函数：弹出两个数字和一个操作符，计算结果压回nums。

## 题解(核心逻辑)
优先级比较是核心：>= 确保同优先级的从左到右计算。前置补0处理一元运算符。

```java
class Solution {
    Map<Character, Integer> map = new HashMap<>() {{
        put('-', 1);
        put('+', 1);
        put('*', 2);
        put('/', 2);
        put('%', 2);
        put('^', 3);
    }};

    public int calculate(String s) {
        s = s.replaceAll(" ", "");
        char[] cs = s.toCharArray();
        int n = s.length();
        Deque<Integer> nums = new ArrayDeque<>();
        nums.addLast(0);
        Deque<Character> ops = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            char c = cs[i];
            if (c == '(') {
                ops.addLast(c);
            } else if (c == ')') {
                while (!ops.isEmpty()) {
                    if (ops.peekLast() != '(') {
                        calc(nums, ops);
                    } else {
                        ops.pollLast();
                        break;
                    }
                }
            } else {
                if (isNumber(c)) {
                    int u = 0;
                    int j = i;
                    while (j < n && isNumber(cs[j]))
                        u = u * 10 + (cs[j++] - '0');
                    nums.addLast(u);
                    i = j - 1;
                } else {
                    if (i > 0 && (cs[i - 1] == '(' || cs[i - 1] == '+' || cs[i - 1] == '-')) {
                        nums.addLast(0);
                    }
                    while (!ops.isEmpty() && ops.peekLast() != '(') {
                        char prev = ops.peekLast();
                        if (map.get(prev) >= map.get(c)) {
                            calc(nums, ops);
                        } else {
                            break;
                        }
                    }
                    ops.addLast(c);
                }
            }
        }
        while (!ops.isEmpty()) calc(nums, ops);
        return nums.peekLast();
    }

    void calc(Deque<Integer> nums, Deque<Character> ops) {
        if (nums.isEmpty() || nums.size() < 2) return;
        if (ops.isEmpty()) return;
        int b = nums.pollLast(), a = nums.pollLast();
        char op = ops.pollLast();
        int ans = 0;
        if (op == '+') ans = a + b;
        else if (op == '-') ans = a - b;
        else if (op == '*') ans = a * b;
        else if (op == '/') ans = a / b;
        else if (op == '^') ans = (int)Math.pow(a, b);
        else if (op == '%') ans = a % b;
        nums.addLast(ans);
    }

    boolean isNumber(char c) {
        return Character.isDigit(c);
    }
}
```

## 策略
双栈法：{{c1::数字栈 nums}} + {{c1::操作符栈 ops}}。
遇到数字：取出完整数字入nums。
遇到 (：直接入ops。
遇到 )：不断计算直到遇到 ( 并弹出。
遇到运算符：将栈内{{c1::优先级高于或等于}}当前运算符的先算掉，再入栈。
最终将栈内剩余运算符全部计算。
