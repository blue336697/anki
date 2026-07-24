# 复制ID偏移量与Backlog

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-复制坐标

Q: Redis 用什么坐标标识一段可继续复制的历史？

A:
- 主节点维护 40 字节十六进制 replication ID（replid）和单调递增的 replication offset。
- replid 标识数据历史分支，offset 标识该分支复制流中的字节位置；只比较 offset 而不比较 replid 会把不同历史误接。
- replica 记录自己已处理的主 replid/offset，断线重连用 `PSYNC <replid> <offset>` 请求续传。
- `INFO replication` 可观察 master_replid、master_repl_offset 和 replica offset。

## 02-replid2

Q: 为什么还需要 replid2 和 second_repl_offset？

A:
- replica 被提升为新主时会生成新 replid，但短时间仍需允许原拓扑中的 replica 按旧历史部分同步。
- 新主把旧 replid 保存为 replid2，并记录旧历史有效到的 second_repl_offset。
- 请求落在旧 ID 且 offset 不超过边界时仍可判定为同一历史连续段，减少故障切换后的全量同步。
- 这是 PSYNC2 改进，不能理解成永远保存两条完整历史。

## 03-复制缓冲结构

Q: Redis 7.4 的 replication backlog 还是一个简单环形 char 数组吗？

A:
- 当前实现使用共享的 `replBufBlock` 链表块：refcount、唯一 id、块起始 repl_offset、size/used 和柔性 buf。
- replica 客户端与 backlog 可共享同一批块，通过各自引用位置推进，减少为每个副本复制一份输出字节。
- backlog 还用 rax 对每隔若干块建立 offset 索引，加快从请求 offset 定位块；源码常量每 64 块建索引。
- 旧资料所说“固定环形缓冲区”表达的是有限历史窗口原理，但结构细节已演进。

## 04-窗口大小

Q: repl-backlog-size 应该怎样按断线窗口估算？

A:
- 近似下限 = 峰值复制写入字节率 × 希望容忍的最长断线秒数，再加协议和突发安全余量。
- 若请求 offset 早于 backlog 最老字节，即使 replid 匹配也只能 FULLRESYNC。
- backlog 不是命令条数，而是传播后的 RESP 字节；大 value、批量命令和过期传播都会消耗窗口。
- 默认示例仅 1 MiB 往往不足生产高写入；用 `repl_backlog_first_byte_offset/histlen` 与实际速率校准。

## 05-边界与验证

Q: 什么条件下 replid 和 offset 都看似合理，仍不能部分同步？

A:
- backlog 已被覆盖、主节点重启/历史链不兼容、请求 offset 超出有效区间，都会拒绝。
- backlog 可能在无 replica 一段时间后按 TTL 释放；之后再连只能全量。
- 网络代理改写/截断、磁盘无盘同步能力不匹配也可能影响后续全量路径，但不是 PSYNC 坐标本身。
- 查看主从日志中的 `Partial resynchronization accepted` 或 `Full resync`，并核对 replid/offset/backlog 区间。
