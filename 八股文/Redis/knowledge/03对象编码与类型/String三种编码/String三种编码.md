# String三种编码

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-int编码

Q: String 什么时候用 int 编码，ptr 里究竟是什么？

A:
- 可无损解析为 long 范围整数的字符串对象可用 `OBJ_ENCODING_INT`，数值直接编码在 `ptr` 的整数位模式中，而非指向 SDS。
- 这样省去 SDS header、字符数组和一次堆分配；执行 INCR 等整数运算也无需先解析十进制文本。
- 返回客户端时再把整数格式化为 RESP 字符串；Redis 的逻辑 String 仍然是字节串语义。
- 一旦 APPEND 或写入不能保持整数编码的内容，就会转为 SDS 编码。

## 02-embstr编码

Q: embstr 的一次分配布局为什么适合短字符串？

A:
- 一块内存连续放置 robj、sdshdr8、buf 和终止零；创建与释放各一次 allocator 调用，局部性好。
- Redis 7.4 的 `OBJ_ENCODING_EMBSTR_SIZE_LIMIT` 为 44 字节，使常见 64 字节 allocator size class 能容纳对象与短 SDS。
- 它是只读式优化：若要原地修改或扩容，转成 raw；否则无法单独 realloc SDS。
- 44 是版本实现常量，不能写成 Redis 协议承诺。

## 03-raw编码

Q: raw 编码的对象和 SDS 如何分配，何时出现？

A:
- robj 与 SDS 是两次独立分配，`ptr` 指向 SDS 的 buf；SDS 可利用 alloc 做预分配和 realloc。
- 新建长度超过 embstr 上限的字符串直接用 raw；短 embstr 被可变命令修改时也可能转 raw。
- raw 多一次指针追踪和分配器元数据，但支持可增长缓冲。
- `OBJECT ENCODING` 可观察 `int/embstr/raw`，但编码变化不影响 GET 返回的逻辑字节。

## 04-命令触发转换

Q: SET、INCR、APPEND、SETRANGE 对 String 编码可能造成什么变化？

A:
- SET 新值会重新创建/优化对象：整数文本可能 int，短文本 embstr，长文本 raw。
- INCR 先把值解析成整数并做溢出检查，结果有机会保持或变成 int；浮点增量最终通常保存规范化字符串。
- APPEND/SETRANGE 要可写 SDS，int/embstr 会解码为 raw；扩大空洞还会写零字节并增加内存。
- 编码优化服务于当前写入形态，不保证历史编码一直保持。

## 05-大String边界

Q: 一个 key 查找是 O(1)，为什么大 String 仍是典型 big key？

A:
- dict 定位 key 平均 O(1)，但 GET/SET 的复制、网络、AOF、复制和客户端解码都至少 O(value bytes)。
- 修改大 String 会触发 realloc/复制；fork 期间写入还可能复制涉及的 COW 页面。
- 大响应占 client output buffer，慢客户端可能让内存持续增长。
- 应限制单值大小、按字段/块拆分、压缩前评估 CPU，并用 `redis-cli --bigkeys/--memkeys` 或采样扫描发现。
