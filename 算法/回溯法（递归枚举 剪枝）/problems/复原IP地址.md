# 复原IP地址

## 题干
给定一个只包含数字的字符串 s，用以表示一个 IP 地址，返回所有可能的有效 IP 地址。IP 地址由 4 个 0~255 之间的整数组成，不含前导零。
![image 2.png](image%202.png)

![image 3.png](image%203.png)

## 回溯-选择列表
选择列表 = {{c1::从 begin 开始截取 1~3 位数字}}
每段需满足：{{c1::值 0~255，且不能有前导零（除非单独一个0）}}

## 回溯-终止+剪枝
终止条件：{{c1::begin == len && residue == 0}}（遍历完字符串且刚好4段）
剪枝1：{{c1::residue * 3 < len - i}} → 剩余段数不够分
剪枝2：{{c1::i >= len}} → break（越界）
剪枝3：{{c1::前导零判断}} → len>1 && s.charAt(left)=='0'

## 复杂度
时间：{{c1::O(3^4)}} → O(1)，最多 3^4=81 种
空间：{{c1::O(1)}} — 递归深度最多4层

## 关键技巧
剪枝1：residue * 3 < len - i 表示剩余字符太多，当前段不够分。
剪枝2：i >= len 直接break，后面位数更长必然越界。
judgeIpSegment 判断前导零和0~255范围。residue 控制递归深度最多4层。

## 题解(DFS)
residue 记录还需分割的段数，每段截取1~3位，判断有效性后递归。

```java
public class Test13 {
    public static List<String> restoreIpAddresses(String s) {
        int len = s.length();
        List<String> res = new ArrayList<>();
        if (len > 12 || len < 4) {
            return res;
        }
        Deque<String> path = new ArrayDeque<>(4);
        dfs(s, len, 0, 4, path, res);
        return res;
    }

    private static void dfs(String s, int len, int begin, int residue,
            Deque<String> path, List<String> res) {
        if (begin == len) {
            if (residue == 0) {
                res.add(String.join(".", path));
            }
            return;
        }
        for (int i = begin; i < begin + 3; i++) {
            if (i >= len) {
                break;
            }
            if (residue * 3 < len - i) {
                continue;
            }
            if (judgeIpSegment(s, begin, i)) {
                String currentIpSegment = s.substring(begin, i + 1);
                path.addLast(currentIpSegment);
                dfs(s, len, i + 1, residue - 1, path, res);
                path.removeLast();
            }
        }
    }

    private static boolean judgeIpSegment(String s, int left, int right) {
        int len = right - left + 1;
        if (len > 1 && s.charAt(left) == '0') {
            return false;
        }
        int res = 0;
        while (left <= right) {
            res = res * 10 + s.charAt(left) - '0';
            left++;
        }
        return res >= 0 && res <= 255;
    }
}
```
