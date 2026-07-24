# Stream的rax与listpack

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-stream结构

Q: Stream 顶层结构体和 ID 是什么样？

A:
- `streamID` 是两个 uint64：毫秒时间 `ms` 与同毫秒内序号 `seq`，比较按二元组字典序。
- `stream` 包含 `rax *rax`、当前 length、last_id、first_id、最大已删除 ID、历史添加数和 `rax *cgroups`。
- 主 rax 的 key 是节点主 ID 的大端字节序，value 指向装有多条 entry 的 listpack。
- 源码锚点：`src/stream.h`、`src/t_stream.c`。

## 02-为什么rax分块

Q: 为什么 Stream 不把每条消息单独放一个树节点？

A:
- rax（radix tree）提供按二进制 ID 的有序前缀索引，但每条消息一个节点会有较高指针/节点开销。
- Redis 把一组相邻消息压进 listpack，rax 只索引该块的 master ID；块内 ID 可用差值编码并复用字段名。
- 范围查询先在 rax 定位块，再顺序解析 listpack；兼顾有序查找与内存紧凑。
- `stream-node-max-bytes`、`stream-node-max-entries` 控制块大小，避免一个 listpack 无限制增长。

## 03-listpack条目

Q: Stream 的 listpack 为什么有 master entry、samefields 和 tombstone 概念？

A:
- 节点头部保存 master entry 的字段列表，后续消息若字段集合相同可只写 values，减少重复字段名。
- 每条消息保存相对 master ID 的 ms/seq 差值、字段/值及内部计数，支持紧凑顺序解析。
- 删除消息时可先留下已删除标记/tombstone；当块内删除过多再重写或移除整块，避免每次 XDEL 都大规模搬移。
- 所以 Stream length、entries_added 和最大删除 ID 含义不同，不能把 length 当历史总写入数。

## 04-范围复杂度

Q: XRANGE/XREAD 的复杂度如何从 rax + listpack 推导？

A:
- 在 rax 中定位起始 ID 近似 O(log K)，K 为压缩后的树节点规模；随后解析并返回 M 条消息至少 O(M + 返回字节)。
- 块内定位仍有线性解析，块太大减少树节点却增加局部扫描/搬移。
- XREAD BLOCK 不会占一个工作线程死等；客户端挂到 blocking_keys，消息到达后由事件循环标记 ready 再解阻塞。
- 大 COUNT 或无限范围仍会制造大响应和主线程停顿。

## 05-版本与验证

Q: 怎样验证 Stream 的内部状态而不是只会 XADD/XREAD？

A:
- `XINFO STREAM key FULL` 查看 length、radix-tree-keys/nodes、groups 和 entries；FULL/COUNT 要谨慎用于大流。
- `MEMORY USAGE key` 观察压缩块、消费组和 PEL 共同占用。
- `XINFO GROUPS/CONSUMERS` 区分 lag、pending、idle/active；不能只看 XLEN 判断积压。
- Stream 编码对外显示为 `stream`，内部 rax+listpack 是实现细节，应标明 Redis 版本。
