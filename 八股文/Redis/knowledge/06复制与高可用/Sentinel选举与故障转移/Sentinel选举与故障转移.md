# Sentinel选举与故障转移

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-epoch投票

Q: 多个 Sentinel 怎样选出本轮故障转移领导者？

A:
- 发起者递增 current epoch 并向其他 Sentinel 请求在该 epoch 为自己投票。
- 每个 Sentinel 在一个 epoch 只授权一个候选，投票结果通过 is-master-down-by-addr 响应传播。
- 候选获得多数 Sentinel 支持且满足本地条件后成为 leader；失败则等待随机/超时后在新 epoch 重试。
- epoch 防止旧轮次消息覆盖新决策，类似逻辑时钟但不是完整 Raft 日志。

## 02-副本筛选

Q: Sentinel 挑选新主时如何给 replica 排序？

A:
- 先排除 SDOWN、断链过久、复制状态差或配置为不参与提升的 replica。
- 优先比较 `replica-priority`（旧名 slave-priority，数值越小通常越优，0 表示不提升）。
- 再比较复制 offset，数据更接近旧主的优先；仍相同则用 runid 等稳定规则打破平局。
- “机器配置最好”不是默认选择标准，数据新鲜度和明确优先级更关键。

## 03-状态机

Q: Sentinel failover 状态机的主要阶段是什么？

A:
1. WAIT_START：等待成为领导者并到达启动时机。
2. SELECT_SLAVE：选候选 replica。
3. SEND_SLAVEOF_NOONE：让候选执行 REPLICAOF NO ONE。
4. WAIT_PROMOTION：等待 INFO 确认其成为 master。
5. RECONF_SLAVES：按 parallel-syncs 分批把其他 replica 指向新主。
6. UPDATE_CONFIG：发布并持久化新主地址，结束本轮。

## 04-旧主回归

Q: 旧主网络恢复后为什么不会自动继续当主？

A:
- Sentinel 已把配置 epoch 和新主地址传播；发现旧主回来后会向它发送 REPLICAOF 新主。
- 在此之前存在窗口：旧主可能仍认为自己是 master，并接受未更新拓扑的客户端写入。
- Sentinel/Redis 复制不是 fencing 系统，无法让网络隔离的旧主从物理上停止服务。
- 客户端必须正确发现新主，关键写还需 fencing token、数据库约束或业务对账避免脑裂副作用。

## 05-持久化配置

Q: Sentinel 为什么要重写自己的配置文件？

A:
- 运行时发现的 Sentinel、replica、新主地址和 epoch 需要在重启后保留，否则会回到陈旧拓扑。
- Sentinel 原子更新配置文件；目录权限或只读文件系统异常会影响状态持久化和运维。
- 客户端应通过 Sentinel API 查询主，不应把 sentinel.conf 当实时服务发现接口。
- 故障演练要包含 Sentinel 重启、旧主回归和多数 Sentinel 丢失，不只杀一次 master 进程。
