# Key设计TTL与容量模型

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-Key命名

Q: 一个可治理的 Redis key 命名应包含哪些信息？

A:
- 稳定业务域、对象类型/用途、分片或租户标识、业务主键和 schema/version，例如 `order:v2:{uid}:summary`。
- 使用统一分隔符便于 ACL pattern、扫描和归属；避免把无界文本、隐私数据直接放 key 名。
- Cluster 的 `{tag}` 只包确需同槽部分，不能把整个租户所有 key 都无脑同槽。
- key 名本身也占 SDS、dict 和持久化/网络字节，过长会在海量 key 下显著放大。

## 02-TTL分层

Q: TTL 应怎样按数据语义设计，而不是统一写 24 小时？

A:
- 真相可重建缓存：TTL 由可接受陈旧时间、回源成本和更新频率决定，并加随机抖动。
- 会话/验证码：TTL 是安全与业务状态机边界，写入需原子设置，不能依赖后台最终清理。
- 永久元数据：仍需明确淘汰/迁移/版本策略，`PERSIST` key 会长期占容量。
- 负缓存 TTL 通常短于正常值，避免新建数据长时间不可见。

## 03-单Key估算

Q: 为什么容量估算不能只用 value 序列化长度？

A:
- 每 key 还包括 key SDS、主 dict entry/bucket、redisObject、value 结构、TTL expires entry 和 allocator size class。
- 容器成员还有各自 SDS/entry/跳表层级或 listpack 空间；小 key 的元数据占比尤其高。
- replica、AOF、客户端缓冲、碎片和 COW 是实例级峰值，不能平均摊掉后忽略。
- 用代表性数据实际写入，比较 `MEMORY USAGE`、used_memory 增量和 RSS，建立分位数模型。

## 04-实例容量

Q: 实例 maxmemory 和机器/容器内存之间应怎样建模？

A:
- 峰值 RSS ≈ dataset/overhead + allocator 碎片 + clients/replication/AOF buffers + fork COW + 其他进程/系统余量。
- maxmemory 只约束其中一部分，不能等于容器 limit；写密集持久化实例需给历史 COW 峰值留安全空间。
- 还要按故障场景算：一个节点接管流量、replica full sync、缓存命中下降和重建期。
- 容量告警应有趋势和到顶时间，不只在 90% 时静态报警。

## 05-扩容与降级

Q: Redis 容量接近上限时，正确处置顺序是什么？

A:
- 先确认增长来源和是否泄漏/大 key/缓冲/碎片，避免盲目 FLUSH 或重启。
- 短期：限写/限回填、清理可丢数据、调合理淘汰、扩内存/加分片；操作前评估 fork/迁移峰值。
- 中期：拆 big key、缩短合理 TTL、压缩 schema、冷热分层和均衡槽。
- 预案必须包含 noeviction OOM、淘汰命中率下降、扩容 reshard 对带宽和 p99 的影响。
