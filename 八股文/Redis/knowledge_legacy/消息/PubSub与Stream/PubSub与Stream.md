# PubSub与Stream

## 01-母题输出卡
Q: Pub/Sub、Stream 和专业 MQ 应怎样按投递语义选型？

A:
- Pub/Sub 是在线广播、at-most-once；订阅者离线或处理失败后消息无法重放
- Stream 持久保存条目，支持消费组、PEL、ACK 和 claim，可构建 at-least-once 处理
- Stream 的可靠性仍取决于 Redis 持久化、复制、内存和业务幂等
- 专业 MQ 在长期堆积、跨机房、事务、路由和生态运维上通常更成熟
- 选型先回答能否丢、保留多久、吞吐与堆积量、顺序范围和失败恢复

## 02-PubSub边界卡
Q: Redis Pub/Sub 为什么适合失效通知，却不适合关键订单消息？

A:
- 发布时只向当前在线订阅者推送，服务端不保留供离线消费者重放的记录
- 订阅者网络断开或处理异常，消息可能永久丢失且没有 ACK
- 它低延迟、广播简单，适合 UI 推送、在线事件和可由事实源重新校准的缓存失效
- 关键订单事件需要持久化、重试、积压和审计，Pub/Sub 无法独立提供
- Redis 7 的 sharded Pub/Sub 改善 Cluster 广播扩展性，但不改变 at-most-once 语义

## 03-Stream消费卡
Q: Stream 消费组怎样处理消费者崩溃后的未确认消息？

A:
- `XREADGROUP` 投递后消息进入组的 Pending Entries List，并记录所属消费者
- 业务成功后 `XACK` 清除 pending；ACK 应在业务副作用成功之后执行
- 消费者崩溃时用 `XPENDING` 发现超时消息，再用 `XCLAIM/XAUTOCLAIM` 转交
- 消息可能被再次投递，因此消费者必须用业务 ID 做幂等
- 重试超过阈值要进入死信或人工处理，不能永远在 PEL 循环

## 04-堆积与保留卡
Q: Stream 长期堆积会发生什么，如何设置保留和容量保护？

A:
- Stream 数据、消费组元数据和 PEL 都占内存，慢消费者会让积压持续增长
- 用 `MAXLEN` 或 `MINID` trimming 控制保留，但删除过早会影响重放与审计
- 监控流长度、最老消息年龄、pending 数、消费者 idle 和 claim 次数
- 达到水位时限流生产者、扩消费者或降级，不应等 Redis 内存淘汰业务消息
- 大规模长期保留通常更适合 Kafka 等磁盘日志系统

## 05-可靠性选型卡
Q: 已有 Redis 时，什么情况下仍不应该用 Stream 代替 Kafka/RocketMQ？

A:
- 需要超大吞吐、数天到数月保留、分区级扩展和大规模回放时，专业日志系统更合适
- 需要成熟事务消息、复杂路由、跨地域复制或完善运维生态时，不应只为少部署一个组件而降级能力
- Redis 同时承载缓存与消息会共享内存和故障域，缓存峰值可能影响消息可靠性
- 轻量内部任务、短期保留且团队能治理 PEL/幂等时，Stream 可以降低复杂度
- 选型要写清数据丢失窗口、恢复步骤和容量上限

## 06-十分钟闭卷验收卡
Q: 怎样闭卷完成 Redis 消息能力连续追问？

A:
- 先明确 Pub/Sub at-most-once 与 Stream at-least-once
- 画出 XREADGROUP、PEL、XACK、XPENDING、claim 的失败恢复链
- 解释为什么 ACK 仍需业务幂等
- 给出 trimming、堆积告警和死信策略
- 对比 Stream 与专业 MQ 的故障域、保留和扩展性
- 只会说“Pub/Sub 会丢、Stream 持久化”，应按未掌握处理
