# IP地址与整数的转换
<!-- tags: source::字节 variant::工程手写 -->

## 题干
实现 IPv4 地址与整数的相互转换：IP→整数：将 IPv4 地址（如 "192.168.1.1"）转换为32位长整数。整数→IP：将32位长整数转换为 IPv4 地址字符串。

## 复杂度
时间：{{c1::O(L)}} — 扫描输入字符串；IPv4 最长 15 个字符，所以工程上也可视为 O(1)
空间：{{c1::O(1)}} — 固定保存 4 段

## 关键技巧
IP 地址本质是32位无符号整数，每段8位（0-255）。
IP→整数：res = (res << 8) | segment，逐段左移8位并拼接
整数→IP：num & 255 取低8位，num >>= 8 右移，循环4次后逆序输出
注意：Java 中 int 是有符号的，IP 最高段可能 >=128，所以用 long 避免符号问题。

## 题解(IP→整数)
先校验恰好四段且每段是 0～255 的十进制整数；随后把已有结果左移 8 位，再用 `|` 拼接当前段。

```java
class Solution {
    public long ipToInt(String ip) {
        String[] segs = ip.split("\\.");
        if (segs.length != 4) {
            throw new IllegalArgumentException("IPv4 must contain 4 segments");
        }
        long res = 0;
        for (String seg : segs) {
            if (!seg.matches("\\d{1,3}")) {
                throw new IllegalArgumentException("invalid IPv4 segment: " + seg);
            }
            int value = Integer.parseInt(seg);
            if (value > 255) {
                throw new IllegalArgumentException("segment out of range: " + seg);
            }
            res = (res << 8) | value;
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
        if (num < 0 || num > 0xFFFF_FFFFL) {
            throw new IllegalArgumentException("unsigned IPv4 integer out of range");
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 3; i >= 0; i--) {
            long segment = (num >>> (i * 8)) & 0xFF;
            sb.append(segment);
            if (i != 0) sb.append(".");
        }
        return sb.toString();
    }
}
```

## 字节变形：无符号边界
Java 没有无符号 `int` 作为普通业务类型。IPv4 的最大整数是 `4294967295`，已经超过 `Integer.MAX_VALUE`，因此接口和中间结果都使用 `long`。转换时必须校验整数位于 `[0, 0xFFFF_FFFFL]`，不能让负数通过带符号右移得到伪结果。
