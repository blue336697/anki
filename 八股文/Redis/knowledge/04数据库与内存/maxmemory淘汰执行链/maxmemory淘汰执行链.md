# maxmemory淘汰执行链

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-触发时机

Q: maxmemory 淘汰是在后台定时发生，还是写命令路径中发生？

A:
- Redis 在执行可能增加内存的命令前后按路径检查内存状态，必要时进入 `performEvictions`，不是独立守护线程随意删 key。
- 计算可淘汰内存时会扣除某些不应由数据淘汰承担的缓冲，如复制/AOF 相关部分，具体以 `getMaxmemoryState` 为准。
- 若策略是 noeviction 或无法释放足够内存，写命令返回 OOM；读命令通常仍可执行。
- 淘汰发生在主请求关键路径，因此一次释放巨大对象也可能造成延迟。

## 02-策略范围

Q: allkeys-* 与 volatile-* 的候选集合有什么本质区别？

A:
- allkeys 从整个 keyspace 选候选；volatile 只从带 TTL 的 expires 集合选。
- LRU/LFU 按近似冷热，random 随机；volatile-ttl 偏向剩余 TTL 更短的 key；noeviction 不删除。
- 若使用 volatile 策略但很少 key 设置 TTL，可淘汰集合耗尽，即使数据库还有大量无 TTL key 也会 OOM。
- 策略选择应匹配“哪些数据允许丢”，不能只按命中率最高来选。

## 03-候选池

Q: Redis 为什么不是维护全局精确 LRU 链表，而是采样加 eviction pool？

A:
- 每次访问都维护双向 LRU 链会增加指针、写放大和并发/缓存成本。
- `evictionPoolPopulate` 从一个或多个 kvstore 采样 key，按 idle/frequency/TTL 质量插入固定大小候选池。
- 淘汰循环从池中选最差候选，删除后继续采样，直到释放到 maxmemory 以下或达到时间/失败边界。
- `maxmemory-samples` 默认 5；提高可更接近理想策略，但每次淘汰 CPU 更高。

## 04-释放计量

Q: 淘汰一个 key 后，Redis 如何判断已经释放足够内存？

A:
- 目标不是删固定 key 数，而是比较当前内存与 maxmemory 的超额字节。
- 删除后重新估算内存；异步 lazyfree 时逻辑删除已完成，但物理释放在后台，算法还需考虑 pending free。
- 若候选是大 key，单次删除成本/传播成本高；若都是极小 key，可能需要循环很多次。
- eviction 指标要看 `evicted_keys` 速率、OOM、latency 和命中率，单看 key 数不能反映字节效果。

## 05-故障边界

Q: Redis 开启淘汰后为什么仍可能 OOM 或被操作系统杀死？

A:
- maxmemory 管的是 Redis 统计口径，不等于 RSS；碎片、fork COW、复制/客户端缓冲和内核页都可能使进程实际占用更高。
- 淘汰速度可能赶不上写入速度，或 volatile 候选耗尽；大对象释放也可能延迟。
- 容器 limit 若紧贴 maxmemory，没有给 RSS 碎片和 fork 留余量，内核可先 OOM kill。
- 需要容量安全边界、持久化峰值预算和宿主机监控，而不是把 maxmemory 当硬 RSS 上限。
