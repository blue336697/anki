# RocketMQ、RabbitMQ、Kafka 选型

> 基线：本仓库以公司主要使用的 RocketMQ 为学习和工程主线；RabbitMQ、Kafka 只用于建立能力边界，不维护三套平均深度的教程。

## 01-产品抽象
Q: RocketMQ、RabbitMQ、Kafka 最核心的抽象差异是什么？
A:
- RocketMQ 是面向业务消息的分布式日志与队列系统，强调 Topic-Queue、消费组、事务、顺序、重试和定时消息。
- RabbitMQ 以 Exchange-Binding-Queue 路由为核心，适合复杂路由、低延迟任务和 AMQP 生态。
- Kafka 以 Partition 追加日志和 ConsumerGroup Offset 为核心，擅长高吞吐流式数据、长保留与生态计算。
- 三者都有发布订阅和持久化，但核心抽象不同会影响路由、回放、积压和运维方式。

## 02-存储模型
Q: 三者的存储与消费进度有什么主要差异？
A:
- RocketMQ 经典实现共享 CommitLog，并为 Topic-Queue 建 ConsumeQueue；Group Offset 与消息物理保留分离。
- Kafka 每个 Topic Partition 自身就是有序日志段，ConsumerGroup 提交 Partition Offset，可在保留期内重放。
- RabbitMQ 传统 Queue 更强调消息交付和 ACK 后清理；Streams 才更接近可重放追加日志。
- 因此“大规模历史回放”天然更贴近 Kafka/Stream 模型，“业务重试与死信”则 RocketMQ/RabbitMQ 表达更直接。

## 03-路由能力
Q: 路由复杂度较高时如何选择？
A:
- RabbitMQ Direct、Topic、Fanout、Headers Exchange 和 Binding 能在 Broker 端表达丰富路由拓扑。
- RocketMQ 主要按 Topic、Queue、Tag/SQL 属性过滤，适合业务类型明确、路由治理相对简单的场景。
- Kafka 通常按 Topic 与 Partition key 分流，复杂事件路由更多交给流处理或应用层。
- 如果只是为了几个固定业务下游，不应因 RabbitMQ 路由更丰富就忽略公司已有平台和运维成本。

## 04-顺序与吞吐
Q: 三者如何在顺序和吞吐之间取舍？
A:
- RocketMQ 与 Kafka 都以 Queue/Partition 为局部有序单位，通过增加分片并行，业务键映射决定热点。
- RabbitMQ Queue 具有交付顺序，但多 Consumer、重投和优先级会使业务完成顺序更复杂；严格顺序通常也需单活处理。
- Kafka 在连续大吞吐日志和批量读取上更有优势，RocketMQ 更贴近业务消息状态和重试治理。
- 不存在既全局有序、无限并行又零故障重排的方案，选型前必须明确顺序域。

## 05-事务消息
Q: 三者的“事务”能力为什么不能直接横向写成完全等价？
A:
- RocketMQ 事务消息协调 Producer 本地事务与消息最终可见，通过 Half Message、EndTransaction 和回查完成。
- Kafka 事务重点是原子写多个 Partition，并可把已消费 Offset 与下游 Kafka 写入纳入 read-process-write 事务范围。
- RabbitMQ 的 AMQP Channel transaction 会影响吞吐，工程上更多使用 Publisher Confirm；它不等于数据库与消息原子双写。
- 三者都不能自动把任意消费者数据库副作用变成全局 Exactly-once。

## 06-延迟重试
Q: 延迟消息和失败重试方面三者有什么倾向？
A:
- RocketMQ 原生提供消费重试、DLQ、经典延迟级别和 5.x 时间戳定时消息，业务消息场景较完整。
- RabbitMQ 可用 TTL、DLX、delivery-limit 和插件组合重试与延迟，但要注意头阻塞和路由安全。
- Kafka 通常由应用建立 retry Topic、时间轮服务或流处理逻辑，没有与业务 ConsumerGroup 同形态的原生 DLQ 工作流。
- 选择时要比较团队是否已有统一重试平台，而不只比较产品功能表。

## 07-高可用
Q: 三者的副本与故障切换思路有什么不同？
A:
- RocketMQ 可使用经典主从、DLedger 或 Controller 等形态，可靠性取决于刷盘、复制 ACK、同步副本和选主。
- RabbitMQ Quorum Queue 为每个 Queue 建 Raft 复制组，偏向多数派一致性；Classic 镜像队列已移除。
- Kafka Partition 由 Leader/Follower 副本和 ISR 管理，Producer ACK 与最小同步副本配置决定写入边界。
- 任何“有三副本所以不丢”的回答都不完整，还要说明 ACK 点、失去多数时行为和客户端重试。

## 08-公司为何主用RocketMQ
Q: 公司内部主要使用 RocketMQ 时，为什么学习和新业务应以它为主线？
A:
- 现有集群、监控、权限、发布规范、故障经验和运维值班比纸面性能参数更能降低生产风险。
- Java 业务可直接复用事务、顺序、延迟、重试和消息轨迹等成熟能力，团队排障语言统一。
- 深入 CommitLog、消费模型和版本边界，能解释真实线上积压、重复和主从故障，而不是只会调用 API。
- 只有出现 RocketMQ 明确无法满足的约束，如 Kafka 流生态或 RabbitMQ 复杂 AMQP 路由，才值得承担第二平台成本。

## 09-选型问题清单
Q: 做 MQ 选型前至少要回答哪些量化问题？
A:
1. 峰值与平均 TPS、消息大小分布、端到端延迟分位数、保留时长和最大积压是多少？
2. 需要哪一级顺序、重试、定时、事务、回放、路由和多租户隔离？
3. 可接受的 RPO/RTO、跨机房策略、磁盘容量和故障时降级行为是什么？
4. 团队已有哪套监控、运维、客户端规范和事故经验，迁移与双平台成本是多少？

## 10-正确性审查
Q: MQ 选型中哪些“排行榜式结论”应避免？
A:
- “Kafka 吞吐最高，所以所有场景都选 Kafka”忽略业务消息重试、路由、定时和运维生态。
- “RabbitMQ 可靠性最好”或“RocketMQ 一定不丢”都没有说明 Queue 类型、刷盘、副本与 ACK 边界。
- “功能更多就更合适”忽略团队能力、已有基础设施和故障恢复经验。
- 本仓库的结论是以 RocketMQ 为主，不是宣称它在所有维度领先；选型必须由业务约束和组织成本共同决定。
