# listpack紧凑列表

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-整体布局

Q: listpack 的整体字节布局是什么？

A:
```text
[total-bytes:4][num-elements:2][entry...][0xFF]
```
- total-bytes 让整体长度 O(1) 可得；元素数若超过 65534，头字段用 65535 哨兵，真实数量需遍历计算。
- 每个 entry 自描述为整数或字符串编码，末尾跟当前 entry 长度的反向编码 `backlen`。
- 终止字节 `0xFF` 标记结束；整个结构是一段连续内存，缓存局部性好且无逐元素指针开销。
- 源码锚点：`src/listpack.c` 顶部格式说明。

## 02-entry编码

Q: listpack 的一个 entry 如何同时支持整数、短字符串和长字符串？

A:
- 第一个编码字节的高位模式区分 7-bit unsigned integer、不同位宽有符号整数和不同长度字符串。
- 小整数直接嵌入编码位，不再保存十进制字符；字符串长度可能内联在头部，也可能使用更宽长度字段。
- entry 逻辑长度 = encoding header + payload + backlen；正向解析靠 encoding，反向移动先从尾部解码 backlen。
- 因为没有前一元素绝对偏移，插入删除要 memmove 后续字节，是 O(N bytes)。

## 03-为何替代ziplist

Q: listpack 相比 ziplist 解决了什么核心问题？

A:
- ziplist 每个 entry 保存 `prevlen`；前一项变大导致 prevlen 从 1 字节扩到 5 字节，可能连续触发后续 entry 扩容，即连锁更新。
- listpack 的 backlen 描述“当前 entry 自己”的长度，前一项变化不会改变后一项 backlen，因此消除该类级联更新。
- 仍然是连续内存，插入中部仍需搬移大量字节；它解决的是级联元数据扩张，不是把所有操作变成 O(1)。
- Redis 7 已用 listpack 替代旧 ziplist 作为 hash/zset/quicklist 节点等紧凑表示。

## 04-适用边界

Q: 为什么 listpack 只适合“小而少”的元素集合？

A:
- 优点来自连续存储和省指针；元素多或单项大时，线性查找、memmove 和 realloc 成本迅速放大。
- listpack 有 1 GiB 安全上限，但这不是推荐业务大小；实际转换阈值远小于它。
- Hash 默认不超过 512 项且 field/value 不超过 64 字节时可保持 listpack；ZSet 默认 128 项/64 字节。
- 阈值来自 redis.conf，可调但不是越大越省：内存节约会换来主线程延迟。

## 05-复杂度陷阱

Q: 为什么 HGET 在 listpack 编码下不能简单回答绝对 O(1)？

A:
- listpack 没有哈希索引，HGET 需要按 field/value 对顺序扫描，实际是 O(N) 元素/字节。
- 小 N 时连续内存和缓存命中让常数很小，通常比建立 dict 更省内存。
- 转成 hashtable 后平均查找 O(1)，但每项多出 bucket、entry、指针和分配器开销。
- 面试回答应把命令抽象复杂度、当前编码和数据规模放在一起，而不是只背命令表。
