# Sentinel监控与主观客观下线

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-实例模型

Q: Sentinel 内部为被监控主节点保存哪些状态？

A:
- `sentinelRedisInstance` 记录名称、地址、flags、配置 epoch、最近 PING/PONG/INFO 时间、down-after 等。
- 主实例还关联发现的 replicas 和其他 sentinels 字典，以及当前领导者/故障转移状态。
- Sentinel 周期向实例 PING、向主/从发 INFO，并通过 Pub/Sub hello 频道交换自身和主节点视图。
- 它是独立 Redis 进程的特殊模式，不依赖外部 ZooKeeper 保存成员关系。

## 02-SDOWN

Q: 主观下线 SDOWN 是怎样判定的？

A:
- 单个 Sentinel 在连续超过 `down-after-milliseconds` 未得到可接受回复后，把实例标为 S_DOWN。
- 可接受回复不等于业务命令一定成功；连接错误、超时或错误类型都会影响最后可用时间。
- SDOWN 只代表这个 Sentinel 的本地判断，可能由局部网络分区或自身卡顿造成。
- 对 replica/Sentinel 实例的故障判断也可用 SDOWN，但主节点故障转移还需要 ODOWN。

## 03-ODOWN

Q: 客观下线 ODOWN 怎样由多个 Sentinel 形成？

A:
- 已 SDOWN 的 Sentinel 通过 `SENTINEL is-master-down-by-addr` 询问其他 Sentinel 对同一主节点的判断。
- 在有效时间窗口内，认为主下线的 Sentinel 数达到该 master 配置的 quorum，才标记 O_DOWN。
- quorum 用于确认“足够多观察者同意主不可达”，不等于选举领导者所需的多数票。
- 只有 master 会进入 ODOWN 并触发自动 failover；replica 的 SDOWN 用于候选过滤。

## 04-quorum与多数

Q: 为什么 quorum=2 不代表两个 Sentinel 就能完成故障转移？

A:
- ODOWN 需要达到配置 quorum；发起故障转移的 Sentinel 还必须在当前 epoch 获得多数 Sentinel 授权。
- 例如 5 个 Sentinel、quorum=2：两人可确认 ODOWN，但领导者仍需至少 3 票。
- 这防止少数分区自行完成选主；同时意味着多数 Sentinel 不可用时即使 quorum 视图满足，也可能无法自动切换。
- 生产通常部署奇数个 Sentinel 并放在独立故障域。

## 05-监控边界

Q: Sentinel 能检测 Redis 进程存活，为什么不等于业务可用性监控？

A:
- PING/INFO 成功不代表关键 Lua、热点 key、客户端 TLS/DNS、连接池或下游数据库正常。
- Sentinel 的视角是实例和复制拓扑，无法验证业务读写语义与缓存正确性。
- 需要独立黑盒探针执行受控读写、监控应用错误率/p99，并和 Sentinel 事件关联。
- down-after 太短易误切，太长延长 RTO；必须按网络抖动和业务 SLA 压测。
