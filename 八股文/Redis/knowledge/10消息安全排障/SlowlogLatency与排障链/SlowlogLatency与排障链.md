# SlowlogLatency与排障链

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-Slowlog范围

Q: SLOWLOG 记录的耗时包含网络和排队吗？

A:
- slowlog 计时主要覆盖命令实际执行阶段，不包含客户端网络 I/O 和回复在 socket/output buffer 的等待。
- 阈值 `slowlog-log-slower-than` 以微秒配置，默认示例 10000；负数禁用，0 记录所有命令但开销高。
- 日志是固定长度环形列表，超过 `slowlog-max-len` 会覆盖旧项，不是长期审计日志。
- 所以客户端慢但 slowlog 空，不代表 Redis 一定没问题。

## 02-LatencyMonitor

Q: Latency Monitor 与 Slowlog 关注点有什么不同？

A:
- latency monitor 记录 fork、AOF fsync、command、expire-cycle、eviction 等内部事件的延迟尖峰。
- 需设置 `latency-monitor-threshold` 毫秒阈值；默认 0 关闭，`LATENCY LATEST/HISTORY/DOCTOR` 分析事件。
- Slowlog 以命令为条目，Latency 以内部事件类型聚合；两者互补。
- 阈值太高漏尖峰，太低增加采样/噪声，应按 SLA 配置。

## 03-内存排障

Q: 发现 Redis 内存上涨时应按什么顺序区分数据、缓冲、碎片和 COW？

A:
1. `INFO memory` 看 used_memory、dataset、clients、replication、AOF、allocator 和 RSS。
2. 对比 key 数/过期数与 MEMORY STATS，判断数据集是否真实增长。
3. 查 client list/output buffer、replica backlog、AOF buffer 和 lazyfree pending。
4. 看 allocator active/resident、fragmentation_bytes；持久化期间看 COW 指标。
5. 用安全 SCAN/MEMORY USAGE 采样 key 分布，避免直接全量 DEBUG。

## 04-CPU排障

Q: Redis 单核 CPU 高时怎样区分热 key、慢命令和后台任务？

A:
- `INFO commandstats/latencystats` 看命令 calls、usec、rejected/failed；slowlog 找单次重命令。
- 热 key 可能每次很快但 calls 巨大，需客户端/代理采样与节点网络分布佐证。
- `INFO persistence` 查 fork/rewrite，`INFO stats` 查 expire/evict，系统 perf/CPU steal 看宿主机。
- 不要立刻重启：会丢现场并可能触发全量复制/冷缓存，让问题更重。

## 05-端到端链

Q: 一条可复用的 Redis 延迟排障证据链是什么？

A:
- 先确认客户端观测：pool wait、connect、command、decode 各阶段和受影响命令/key。
- 再看 Redis：instantaneous ops、blocked clients、slowlog、latency events、CPU、内存/缓冲。
- 再看依赖：磁盘 fsync/fork、网络丢包/重传、宿主机调度、Cluster 重定向和复制 lag。
- 最后用时间戳对齐，而不是把多个不同时段指标拼成因果；修复后用同一压测/指标验证。
