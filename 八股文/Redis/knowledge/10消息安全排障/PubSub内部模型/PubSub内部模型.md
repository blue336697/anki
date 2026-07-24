# PubSub内部模型

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-订阅索引

Q: Redis Pub/Sub 怎样从 channel 找到订阅者？

A:
- 服务端维护 channel → client 集合/字典，client 也记录自己订阅的 channels/patterns，便于发布和断开清理。
- PUBLISH 精确频道可直接遍历该频道订阅者；pattern 订阅还需匹配已注册模式，模式多时成本上升。
- Cluster 的 shard Pub/Sub 使用槽感知的 SSUBSCRIBE/SPUBLISH，减少全集群传播；普通 Pub/Sub 语义不同。
- Pub/Sub 消息不写 keyspace，不由 GET/SCAN 访问。

## 02-投递语义

Q: 为什么 Pub/Sub 是 at-most-once，而不是可靠消息队列？

A:
- 发布时只把消息追加给当前在线订阅客户端；没有服务端持久消息、消费 offset、ACK 或重投。
- 客户端断线、输出缓冲超限或处理前崩溃，消息就丢失。
- PUBLISH 返回接收者数量只表示当时匹配订阅数，不表示业务处理成功。
- 适合在线通知/失效广播；需要可恢复消费应使用 Stream 或专用 MQ。

## 03-慢消费者

Q: 慢 Pub/Sub 消费者怎样拖累 Redis 内存？

A:
- 发布者不等订阅者处理，消息进入每个订阅 client 的输出缓冲。
- 消费速度低于发布速度时缓冲持续增长，达到 `client-output-buffer-limit pubsub` soft/hard 阈值会断开客户端。
- 若阈值过大，单个慢消费者可占大量内存；过小则短突发也易断线。
- 客户端必须监控断线并接受丢消息语义，不能假设自动重连补历史。

## 04-Cluster传播

Q: 普通 Pub/Sub 在 Cluster 中为什么可能有额外总线成本？

A:
- 普通 PUBLISH 需要让所有节点上的订阅者都可能收到，消息会通过 cluster bus 传播。
- 频道名与 key slot 没有天然分片限制，扩节点不一定线性提升广播吞吐。
- Sharded Pub/Sub 将频道映射槽，只在负责槽的 shard 及副本范围传播，更适合大集群。
- 客户端订阅模式、版本和故障切换行为要单独验证。

## 05-选型边界

Q: Pub/Sub、Stream 和 MQ 应如何选择？

A:
- Pub/Sub：最低状态开销、在线广播、允许断线丢失。
- Stream：Redis 内持久日志、消费组/PEL/claim，适合中等规模任务流，但仍受单 key/内存/持久化约束。
- 专用 MQ：更完整的分区、磁盘日志、重平衡、保留和跨地域能力，运维复杂度更高。
- 选择基于丢失/重复容忍、积压规模、顺序、重放和运维，不是只比 API 简单。
