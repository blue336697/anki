# 验证IP地址

## 题干
给定一个字符串 queryIP，如果是有效的 IPv4 地址返回 "IPv4"，如果是有效的 IPv6 地址返回 "IPv6"，都不是返回 "Neither"。

## 复杂度
时间：{{c1::O(n)}} — 一次遍历
空间：{{c1::O(1)}} — 仅用几个变量

## 关键技巧
IPv4 校验关键点：
1. 每段值 0-255，不能有前导零（除非值为0本身）
2. 恰好3个点号，开头结尾不能是点
3. IPv6：每段1-4位十六进制字符，7个冒号
模拟法比正则更可控，可以精确定位错误原因。

## 题解(正则法)
简洁但性能较差，IPv4段匹配0-255，IPv6段匹配1-4位十六进制。

```java
class Solution {
    public String validIPAddress(String queryIP) {
        if (queryIP == null) {
            return "Neither";
        }
        String regex0 = "((\\d)|([1-9]\\d)|(1\\d\\d)|((25[0-5])|2[0-4]\\d))";
        String regexIPv4 = regex0 + "(\\." + regex0 + "){3}";
        String regex1 = "(\\d|[a-f]|[A-F]){1,4}";
        String regexIPv6 = regex1 + "(:" + regex1 + "){7}";
        String result = "Neither";
        if (queryIP.matches(regexIPv4)) {
            result = "IPv4";
        } else if (queryIP.matches(regexIPv6)) {
            result = "IPv6";
        }
        return result;
    }
}
```

## 题解(模拟法)
逐段解析数字，IPv4验证范围0-255+前导零，IPv6验证1-4位十六进制。

```java
class Solution {
    public String validIPAddress(String ip) {
        if (ip.indexOf(".") >= 0 && check4(ip)) return "IPv4";
        if (ip.indexOf(":") >= 0 && check6(ip)) return "IPv6";
        return "Neither";
    }
    boolean check4(String ip) {
        int n = ip.length(), cnt = 0;
        char[] cs = ip.toCharArray();
        for (int i = 0; i < n && cnt <= 3; ) {
            int j = i, x = 0;
            while (j < n && cs[j] >= '0' && cs[j] <= '9' && x <= 255)
                x = x * 10 + (cs[j++] - '0');
            if (i == j) return false;
            if ((j - i > 1 && cs[i] == '0') || (x > 255)) return false;
            i = j + 1;
            if (j == n) continue;
            if (cs[j] != '.') return false;
            cnt++;
        }
        return cnt == 3 && cs[0] != '.' && cs[n - 1] != '.';
    }
    boolean check6(String ip) {
        int n = ip.length(), cnt = 0;
        char[] cs = ip.toCharArray();
        for (int i = 0; i < n && cnt <= 7; ) {
            int j = i;
            while (j < n && ((cs[j] >= 'a' && cs[j] <= 'f')
                || (cs[j] >= 'A' && cs[j] <= 'F')
                || (cs[j] >= '0' && cs[j] <= '9'))) j++;
            if (i == j || j - i > 4) return false;
            i = j + 1;
            if (j == n) continue;
            if (cs[j] != ':') return false;
            cnt++;
        }
        return cnt == 7 && cs[0] != ':' && cs[n - 1] != ':';
    }
}
```
