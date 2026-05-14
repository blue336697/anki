# IP地址与整数的转换

## 题干
实现 IPv4 地址与整数的相互转换：IP→整数：将 IPv4 地址（如 "192.168.1.1"）转换为32位长整数。整数→IP：将32位长整数转换为 IPv4 地址字符串。

## 复杂度
时间：{{c1::O(1)}} — 固定4段
空间：{{c1::O(1)}}

## 关键技巧
IP 地址本质是32位无符号整数，每段8位（0-255）。
IP→整数：res = (res << 8) | segment，逐段左移8位并拼接
整数→IP：num & 255 取低8位，num >>= 8 右移，循环4次后逆序输出
注意：Java 中 int 是有符号的，IP 最高段可能 >=128，所以用 long 避免符号问题。

## 题解(IP→整数)
每段左移8位（<<8），再用 | 拼接当前段。

```java
class Solution {
    public long ipToInt(String ip) {
        String[] segs = ip.split("\\.");
        long res = 0;
        for (int i = 0; i < 4; i++) {
            res = (res << 8) | Integer.parseInt(segs[i]);
        }
        return res;
    }
}
```

## 题解(整数→IP)
每次取低8位（&255），右移8位（>>=8），提取顺序从低位到高位，拼接需逆序。

```java
class Solution {
    public String intToIp(long num) {
        String[] parts = new String[4];
        for (int i = 0; i < 4; i++) {
            parts[i] = String.valueOf(num & 255);
            num >>= 8;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 3; i >= 0; i--) {
            sb.append(parts[i]);
            if (i != 0) sb.append(".");
        }
        return sb.toString();
    }
}
```
