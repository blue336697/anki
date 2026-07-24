# RocketMQ Topic、MessageQueue 与消息模型

> 基线：Topic 是业务分类，MessageQueue 是存储和并行消费的最小分片。物理 CommitLog 与逻辑 Queue 必须分开理解。

## 01-Topic与Queue
Q: Topic 和 MessageQueue 的关系是什么？
A:
- Topic 是具有同一业务语义和治理策略的消息集合；一个 Topic 由分布在一个或多个 Broker 上的多个 MessageQueue 组成。
- Queue 内用递增逻辑 Offset 标识消息顺序，是经典队列级负载均衡和局部有序的基本单位。
- Queue 并不是一份独立消息文件；经典存储中不同 Topic、Queue 的消息共同顺序写入 CommitLog，再由 ConsumeQueue 建逻辑索引。
- 增加 Queue 可以提高生产与消费并行度，但也增加路由、索引、Rebalance 和文件管理成本。

## 02-消息结构
Q: 一条 RocketMQ 消息有哪些关键字段，它们分别服务什么能力？
A:
- Topic 决定业务路由，body 保存负载；Tag 用于单值分类过滤，properties 保存 Keys、业务属性和系统属性。
- Keys 用于按业务标识查询和排障，不应被误认为数据库式唯一索引或可靠去重约束。
- QueueId 与 QueueOffset 标识逻辑队列位置，CommitLogOffset 标识物理日志位置。
- MessageId 的生成和含义随客户端与版本可能不同，业务幂等应使用自定义稳定业务键。

## 03-普通消息生命周期
Q: 普通消息从创建到删除经历哪些状态？
A:
- Producer 构造消息并发送，Broker 接收后写入物理存储，同时或随后生成可供逻辑 Queue 消费的索引。
- 消息进入可消费状态后，Consumer 根据订阅和进度拉取；消费成功只推进 Group 的 Offset 或状态，不立即删除消息体。
- 同一消息可被多个 ConsumerGroup 独立消费，也可通过重置 Offset 在保留期内再次读取。
- 文件达到保留策略或磁盘清理条件后按段删除，删除是存储生命周期行为，不由某个消费者 ACK 单独触发。

## 04-Queue数量
Q: Queue 数量怎样影响吞吐和扩容？
A:
- 队列级负载均衡下，一个 Queue 同一时刻通常分配给 Group 内一个消费者实例，因此 Queue 数是实例并行度的上限。
- Queue 太少会使新增消费者空闲；太多会增加 ConsumeQueue 文件、客户端 PullRequest、Rebalance 和路由元数据开销。
- 顺序消息还要考虑业务键倾斜：即使 Queue 很多，热点键仍只能在自己的 Queue 上串行处理。
- 应根据峰值吞吐、单消费者能力、未来扩容和 Broker 分布预先规划，不能等积压后无成本地修改。

## 05-ConsumerGroup语义
Q: ConsumerGroup 为什么既是扩容单位又是消费进度单位？
A:
- 同一 Group 中的实例被认为执行同一种业务逻辑，共同分担订阅消息；增加实例是横向扩容。
- Broker 按 Group 维护消费 Offset、重试和死信相关状态，因此同一 Group 重启或换实例后可以延续进度。
- 不同 Group 即使订阅相同 Topic，也各自拥有进度并各消费一份，用于多个独立下游。
- 同 Group 的订阅表达式和处理语义必须一致，否则某些 Queue 可能按不同规则处理，形成不可预测遗漏。

## 06-集群与广播
Q: 集群消费和广播消费有什么差别？
A:
- 集群消费中同 Group 的实例共同分摊消息，目标是一条消息由该业务组中的某个实例处理。
- 广播消费中每个实例各处理一份，更像进程级通知；经典 Java 客户端常在本地保存广播进度。
- 广播实例离线期间的恢复、重试和进度语义与集群模式不同，不适合关键业务的可靠任务分发。
- 需要多个业务都收到消息时，通常创建多个 ConsumerGroup，而不是用同一 Group 的广播冒充多个业务订阅者。

## 07-Tag与Key
Q: Tag、Key 和业务属性分别应该怎样使用？
A:
- Tag 适合一个 Topic 内少量稳定子类型的服务端过滤，例如订单创建与取消；不应承载高基数业务 ID。
- Key 适合按订单号、请求号定位消息和建立查询线索，可以一条消息设置多个业务检索键。
- 自定义 properties 可携带版本、来源和追踪上下文，但会计入消息大小并参与协议编码。
- 高频变化或复杂权限边界更适合拆 Topic；不要依靠大量 Tag 把完全不同生命周期的业务塞进同一 Topic。

## 08-正确性审查
Q: 关于 Topic 和 Queue，哪些说法需要加边界？
A:
- “Queue 就是一份物理文件”不准确；经典 RocketMQ 使用共享 CommitLog 和每个 Topic-Queue 的逻辑 ConsumeQueue。
- “Queue 越多吞吐越高”不准确；达到磁盘、网络、线程或下游瓶颈后，更多 Queue 只增加管理开销。
- “消费成功后消息立即从 Broker 删除”不准确；消费进度与消息保留分离，文件按保留和磁盘策略清理。
- “MessageId 能保证业务唯一”不成立；业务动作的唯一性必须由业务键和状态机定义。
