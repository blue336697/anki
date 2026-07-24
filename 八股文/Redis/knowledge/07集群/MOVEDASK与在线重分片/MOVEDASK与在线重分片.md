# MOVEDASK与在线重分片

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-MOVED

Q: MOVED 重定向表达什么，客户端应该怎样处理？

A:
- `-MOVED slot host:port` 表示该槽的稳定/权威 owner 不是当前节点。
- 客户端把本次请求发往目标，并更新本地 slot map；成熟客户端可能立即或批量刷新完整拓扑。
- MOVED 不是临时一次性跳转，不能只重试而永不更新路由，否则每次都多一跳。
- 非 cluster-aware 客户端会把 MOVED 当错误，代理/SDK 必须明确支持 Cluster。

## 02-ASK

Q: ASK 与 MOVED 的语义为什么不同？

A:
- `-ASK slot target` 表示槽正在迁移，目标节点可能已拥有这个具体 key，但槽最终 owner 尚未切换。
- 客户端只对下一条命令先向目标发送 `ASKING`，然后执行原命令；不应永久更新 slot map。
- ASKING 在 client flags 中临时授权 importing 节点服务该槽，执行一条后清除。
- 把 ASK 当 MOVED 会过早把该槽所有请求路由到尚未完整导入的节点。

## 03-迁移状态

Q: 源节点 MIGRATING 和目标节点 IMPORTING 分别怎样影响请求？

A:
- 源节点仍是槽 owner；若 key 还在源端就直接服务，若 key 已迁走则返回 ASK。
- 目标节点标 IMPORTING 后，只有带 ASKING 的请求才可访问迁入 key，普通请求仍按旧槽归属重定向。
- 多 key 命令在迁移中若部分 key 在源、部分在目标，可能返回 TRYAGAIN，无法保证原子跨两处执行。
- 最后所有 key 搬完，再向集群发布新槽 owner，稳定后才出现 MOVED。

## 04-MIGRATE流程

Q: 在线 reshard 搬一个 key 时通常经历哪些步骤？

A:
- 工具在目标设置 IMPORTING、源设置 MIGRATING，枚举该槽 key。
- 源通过 MIGRATE/RESTORE-ASKING 把序列化 value、TTL 等发送给目标，成功后删除源 key。
- 迁移期间新写由上述 ASK 规则处理；工具反复搬直到槽为空。
- 最后对所有 master 更新 `CLUSTER SETSLOT <slot> NODE <target>`，用 config epoch/gossip 收敛。

## 05-HashTag风险

Q: hash tag 除了实现多 key 同槽，还会带来什么生产风险？

A:
- 相同 tag 的所有 key 永远在一槽，无法通过普通 reshard 把其中一部分拆到另一节点。
- 如果 tag 选租户/活动等高倾斜维度，会形成单槽热点和容量大户。
- Cluster 的 16384 槽只分 key，不拆单个大 key；一个巨型 ZSet/Hash 仍受单节点内存和主线程限制。
- tag 应只覆盖确需原子多 key 操作的最小集合，并做槽分布与热点监控。
