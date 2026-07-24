# Cluster副本选举与一致性

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-选举资格

Q: master FAIL 后，哪些 replica 有资格发起 Cluster failover？

A:
- 必须是该失败 master 的 replica，复制链路/数据新鲜度满足配置边界，且没有被禁止参与。
- replica 根据自身复制 offset 排名计算延迟，越新的副本越早发起，减少多人同时竞争。
- 手动 `CLUSTER FAILOVER` 还有协调、FORCE、TAKEOVER 等不同安全边界，不能与自动选举混用解释。
- 没有合格 replica 时该 master 的槽保持不可服务。

## 02-投票规则

Q: Cluster master 怎样给 replica 投票？

A:
- 候选递增/使用新的 config epoch 并广播请求；每个有投票权 master 在一个 epoch 通常只投一次。
- 只有该候选对应 master 已被标 FAIL、请求时序有效等条件满足才授权。
- 候选获得负责槽 master 的多数票后提升，接管旧 master 槽并广播新配置。
- epoch 用于解决槽配置冲突；更高 configEpoch 的 owner 声明胜出。

## 03-数据丢失窗口

Q: Cluster 自动故障转移的数据丢失窗口来自哪里？

A:
- 主节点对客户端确认后，复制是异步的；故障时获胜 replica 的 offset 可能落后。
- 旧 master 在少数分区中可能短暂接受写，恢复后被降为 replica，这些孤立写消失。
- 更长 node timeout 增大潜在孤主窗口但减少误切；更短相反。
- WAIT/min-replicas 可减损，不能提供线性一致性；关键业务仍需上层幂等与对账。

## 04-集群可用状态

Q: 什么时候 cluster_state 会变为 FAIL？full coverage 有什么影响？

A:
- 有槽未分配、负责槽的 master FAIL 且无接管，或多数 master 不可达等条件会影响集群状态。
- `cluster-require-full-coverage yes` 时任一槽不可用可让整个集群停止服务；设为 no 可让仍覆盖的槽继续服务。
- no 提升部分可用性，但应用访问缺失槽仍失败，跨 key 业务可能得到不完整结果。
- 这是可用性策略，不修复槽本身，也不改变数据一致性。

## 05-Sentinel对比

Q: Redis Cluster 与 Sentinel 的高可用机制根本差异是什么？

A:
- Sentinel 管理一个不分片的主从组，客户端通过 Sentinel 找当前主；数据集仍由单主承载。
- Cluster 同时负责 16384 槽分片、节点间路由、每分片复制和故障转移，客户端必须处理槽拓扑。
- Sentinel 的 quorum/leader election 与 Cluster 的 master 多数/replica election 是两套协议。
- 需要水平容量与多分片选 Cluster；只需单数据集主从自动切换可用 Sentinel，不能仅按“节点更多”选型。
