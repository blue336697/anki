# SDS扩容与释放

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-扩容算法

Q: sdsMakeRoomFor 的扩容算法逐步是什么？

A:
1. 若 `avail >= addlen` 直接返回，不分配。
2. 计算必需长度 `reqlen=len+addlen`。
3. greedy 模式下，若新长度小于 `SDS_MAX_PREALLOC`（1 MiB）则容量翻倍，否则额外增加 1 MiB。
4. 根据新容量选择 header 类型；追加场景即使很短也不使用 sdshdr5，因为它没有 alloc。
5. header 类型不变可 realloc；类型变化则重新分配、复制内容并重写 header。

## 02-摊还复杂度

Q: SDS 追加为什么通常是摊还 O(1)，但单次仍可能 O(N)？

A:
- 有空闲空间时只 memcpy 新内容并更新 len，是 O(k)，k 为追加字节数。
- 容量不足时可能 realloc；若地址移动，需要复制已有 N 字节，因此该次是 O(N+k)。
- 小于 1 MiB 的倍增使扩容次数呈对数级，连续逐字节追加的总复制成本受控，因此说“摊还 O(1)”是针对每次固定大小追加。
- 超过 1 MiB 后按 1 MiB 增长，限制过度预分配，但超大字符串连续增长会更频繁 realloc。

## 03-惰性释放

Q: sdsclear、sdsRemoveFreeSpace 和释放对象有什么区别？

A:
- `sdsclear` 把 len 置 0 并写终止零，但保留 alloc，适合复用缓冲。
- `sdsRemoveFreeSpace` 把分配缩到当前长度，可能更换 header/地址；节省内存但付出 realloc 成本。
- `sdsfree` 通过 header 类型找到真实分配起点并整体释放。
- Redis 不会每次字符串变短都主动收缩，否则容易在伸缩流量下形成分配抖动和碎片。

## 04-embstr转raw

Q: 短字符串从 embstr 变成 raw 的精确原因是什么？

A:
- Redis 7.4 中新建字符串长度不超过 44 字节时通常可用 embstr，robj 与 sdshdr8/缓冲区一次连续分配。
- embstr 的 SDS 不能独立 realloc；APPEND、SETRANGE 等需要修改/扩容时，会解码复制成 raw。
- raw 是 robj 与 SDS 两次独立分配，SDS 可正常利用 alloc 和 realloc。
- 44 是当前源码常量 `OBJ_ENCODING_EMBSTR_SIZE_LIMIT`，属于实现细节，应标版本，不能当协议保证。

## 05-线上边界

Q: SDS 设计能避免哪些问题，不能避免哪些问题？

A:
- 能避免反复 strlen、常见缓冲区溢出和逐次追加都重新分配。
- 不能避免大 value 占用内存与网络、主线程复制巨型字符串、分配器碎片和 COW 放大。
- `GET` 一个百 MB value 即使查找 O(1)，返回与复制仍是 O(value bytes)。
- 应结合 `proto-max-bulk-len`、客户端输出缓冲、big key 扫描和业务 value 分片控制，而不是只看命令复杂度表。
