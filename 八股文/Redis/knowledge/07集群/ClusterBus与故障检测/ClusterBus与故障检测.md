# ClusterBus与故障检测

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-双端口

Q: Cluster 节点为什么除了客户端端口还需要 cluster bus？

A:
- 客户端端口处理 RESP 命令；cluster bus 使用节点间二进制协议交换 PING/PONG、gossip、FAIL、PUBLISH、选举等。
- 默认常见 bus 端口是数据端口 + 10000，也可按版本/配置明确指定；防火墙必须允许节点间双向通信。
- bus 链接问题可导致集群误判/无法收敛，即使客户端端口仍可连接。
- TLS 部署还要分别考虑客户端与集群总线加密配置。

## 02-gossip内容

Q: PING/PONG 消息中的 gossip section 传播什么？

A:
- 消息头携带发送者 epoch、复制 offset、槽 bitmap、主从角色和 cluster state。
- gossip section 抽样携带其他节点 id、地址、ping/pong 时间与 flags，使故障信息逐步扩散。
- 不是每个包都携带全量节点矩阵，降低 O(N²) 带宽；代价是视图收敛有延迟。
- 节点直接通信加 gossip 让集群无中心，但节点数过大时 bus 开销和收敛都会变差。

## 03-PFAIL

Q: 一个节点何时被本地标记 PFAIL？

A:
- 本节点向目标发送 PING 后，超过 `cluster-node-timeout` 仍没有足够新鲜 PONG/数据，就认为疑似失联。
- PFAIL 是本地怀疑，可能由单向网络、事件循环阻塞或该观察者自身故障造成。
- PFAIL 状态通过 gossip 传播给其他 master，作为形成 FAIL 的投票证据。
- 调低 node timeout 可缩短检测，但增加网络抖动下误判和切换。

## 04-FAIL

Q: PFAIL 怎样升级为全局可行动的 FAIL？

A:
- 负责槽的 master 收集其他 master 对目标 PFAIL 的报告；在有效窗口内达到 master 多数后标 FAIL。
- FAIL 消息通过集群传播，使其他节点快速接受该故障状态并允许其 replica 发起故障转移。
- 使用 master 多数而非所有节点，保证部分故障下仍能行动并抑制少数分区。
- 若多数 master 不可达，集群可能保持/进入 FAIL，而不是让每个分区都继续写。

## 05-检测盲区

Q: Cluster 故障检测为什么不能消除脑裂和数据丢失？

A:
- 检测和 gossip 有时间窗口；旧 master 在被多数隔离但仍有客户端连接时可能短暂接收写。
- 复制异步，提升 replica 可能缺少最后写入；cluster-node-timeout 只控制部分时间边界。
- cluster-require-full-coverage、replica-validity-factor 等配置影响可用性/安全取舍，但不是共识提交。
- 关键写需要幂等、版本/fencing、持久化和外部真相源。
