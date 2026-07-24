# 多部件AOF与重写

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-MP-AOF结构

Q: Redis 7 的多部件 AOF 目录里有哪些文件？

A:
- 一个 BASE AOF 表示某时刻完整数据基线，可是 RDB preamble 或 AOF 命令格式。
- 零个或多个 INCR AOF 保存 base 生成期间及之后的增量命令。
- manifest 记录当前生效 base、incr 序列和历史文件，加载不再靠猜文件名顺序。
- 文件通常位于 `appenddirname` 目录；这与 Redis 6 的单一 appendonly.aof 认知不同。

## 02-重写流程

Q: BGREWRITEAOF 在 MP-AOF 下怎样避免旧版巨型重写缓冲？

A:
1. 主进程先切开新的 INCR AOF 并持久化 manifest，使重写期间新写入直接进入独立增量文件。
2. fork 子进程按快照生成新的临时 BASE；默认可使用 RDB preamble。
3. 子进程成功后，主进程原子更新 manifest，把新 BASE 与当前 INCR 设为活动集合。
4. 旧 base/incr 标为 history，再由后台删除。
- Redis 7 不再需要把全部重写期间增量长期堆在旧式内存 rewrite buffer 中。

## 03-为什么能压缩

Q: AOF rewrite 为什么能显著缩小文件，而不需要逐条理解旧历史？

A:
- 子进程遍历当前内存最终状态，为每个 key 生成恢复该状态所需的最少命令或直接写 RDB preamble。
- 例如同一 key 的百万次 INCR 可折叠成最终值；过期/删除过的历史不再输出。
- 重写结果与当前状态等价，不保留审计历史和每次业务操作顺序。
- 它是状态重建，不是对旧 AOF 文本逐行做 peephole 优化。

## 04-原子切换

Q: 重写完成时怎样避免崩溃后拿到半个 AOF 集合？

A:
- 新 base 先写临时文件并完成刷盘/关闭，再改名到目标文件。
- manifest 在内存中构造新版本，写临时 manifest 后原子 rename；只有 manifest 指向的文件集合生效。
- 历史文件延后删除，切换失败仍可回到旧 manifest 所指集合。
- 文件系统 rename 原子性不等于目录项绝对持久，源码还会按需要 fsync 目录/文件，恢复仍需验证。

## 05-重写代价

Q: AOF rewrite 已改进，为什么仍可能造成线上抖动？

A:
- 仍需 fork、遍历全数据集、序列化和大量磁盘写；父进程继续写会产生 COW。
- 新 INCR 与子进程 BASE 同时写盘，可能争带宽；manifest 切换和文件清理也有 I/O。
- `auto-aof-rewrite-percentage/min-size` 应结合磁盘余量和业务低峰，而不是只追求文件最小。
- 监控 rewrite 时间、COW、delayed fsync、磁盘空间和失败重试。
