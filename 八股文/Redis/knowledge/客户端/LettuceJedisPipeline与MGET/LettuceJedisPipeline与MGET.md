# LettuceJedisPipeline与MGET

## 客户端卡
Q: Jedis 和 Lettuce 有什么常见区别？
A:
- Jedis 传统上是阻塞 IO 客户端，实例通常不建议多线程共享
- Lettuce 基于 Netty，支持异步、响应式和线程安全连接
- Jedis 使用简单，Lettuce 在高并发和异步场景更灵活
- 实际选择还要看连接池、监控、超时、集群支持和团队熟悉度
- 面试表达：客户端差异不只是 API，而是 IO 模型和并发使用方式

## Pipeline卡
Q: Redis pipeline 解决什么问题？
A:
- pipeline 把多条命令连续发送，减少网络 RTT
- 它不保证事务原子性
- 命令仍由 Redis 按顺序执行
- pipeline 批次过大可能造成客户端和服务端缓冲区膨胀
- 适合大量独立命令批量读写，但要控制批大小和超时

## MGET卡
Q: Redis Cluster 下 mget 多个 key 要注意什么？
A:
- 多 key 命令要求 key 在同一个 slot，否则可能跨槽失败
- 客户端可按 slot 拆分多个 mget 并发请求
- hash tag 可以让相关 key 落到同一 slot
- 过度使用 hash tag 会造成热点槽
- 大批量 mget 还要关注长尾延迟、返回值大小和网络带宽

## 正确性审查卡
Q: Redis 客户端和 pipeline 有哪些常见误区？
A:
- “pipeline 是事务”：错误。它只是批量发送
- “批量越大越快”：不一定。过大导致缓冲区和长尾延迟
- “mget 在 Cluster 下天然支持跨节点”：不一定。要看客户端拆分能力
- “Lettuce 线程安全就不用连接池”：不完整。还要看吞吐、阻塞命令和隔离
- “超时只设一个就够”：错误。连接、命令、重试和拓扑刷新都要治理
