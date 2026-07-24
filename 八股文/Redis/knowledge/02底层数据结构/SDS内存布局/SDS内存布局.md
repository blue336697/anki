# SDS内存布局

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-五种头部

Q: SDS 的 sdshdr5/8/16/32/64 分别长什么样？

A:
- `sds` 对外只是指向 `buf` 的 `char*`，真实 header 位于指针前方；`s[-1]` 的低 3 位标识 header 类型。
- sdshdr8/16/32/64 都是 packed 结构：对应位宽的 `len`、`alloc`，再加 `flags` 和柔性数组 `buf[]`。
- sdshdr5 把长度塞进 flags 高 5 位，没有 alloc；源码说明它主要用于不可增长的短字符串布局。
- header 按所需容量选择，短字符串不会为 64 位 len/alloc 多付固定开销。
- 源码锚点：`src/sds.h`。

## 02-O1长度与二进制安全

Q: SDS 为什么既能 O(1) 取长度，又能保存二进制？

A:
- 长度来自 header 的 `len`，`sdslen` 读取 `s[-1]` 后按类型定位字段，不需要像 strlen 一样扫描到 `\0`。
- 内容长度由 len 明确界定，因此中间可以包含 `\0`、RESP 字节或压缩数据；这就是二进制安全。
- `buf[len]` 仍保留终止零，便于把 SDS 传给要求 C 字符串的函数，但终止零不是逻辑长度依据。
- `alloc-len` 给出尾部可用空间，使追加前可以判断是否需要重新分配。

## 03-指针寻址

Q: 只拿到 char* 类型的 sds，Redis 怎么找到 len 和 alloc？

A:
- 先读 `flags = s[-1]`，用 `flags & SDS_TYPE_MASK` 得到类型。
- 例如 sdshdr8：把 `(s - sizeof(sdshdr8))` 转成 header 指针，再读 `len/alloc`。
- 结构体使用 packed，保证字段紧邻且 buf 的地址计算符合布局；这也意味着访问宽字段时不能假定天然对齐。
- 这种“返回 buf 指针、header 藏在前面”的设计兼容大量 C 字符串 API，同时保留元数据。

## 04-内存示例

Q: 一个长度 5、容量 10 的 sdshdr8 在内存中如何排列？

A:
```text
[len=5][alloc=10][flags=TYPE_8][h][e][l][l][o][\0][free x5]
                                ^
                                sds 指针
```
- `sdslen(s)=5`，`sdsalloc(s)=10`，`sdsavail(s)=5`。
- 分配大小至少为 header 3 字节 + alloc 10 字节 + 终止零 1 字节，另有分配器自身元数据和 size class 浪费。
- `MEMORY USAGE` 看到的是更接近实际分配的估算，不只是 14 字节逻辑布局。

## 05-SDS与C字符串

Q: 面试中怎样完整比较 SDS 与 C 字符串？

A:
- 长度：SDS O(1)，C 字符串 strlen O(N)。
- 安全：SDS 显式容量、统一扩容，降低缓冲区溢出风险；C API 依赖调用者正确管理空间。
- 内容：SDS 二进制安全，C 字符串以首个 `\0` 为结束。
- 追加：SDS 利用预留空间摊销分配成本；C 字符串通常需手工 realloc 与复制。
- 兼容：SDS 的 buf 仍以 `\0` 结尾，可在满足二进制前提时复用 C API。
