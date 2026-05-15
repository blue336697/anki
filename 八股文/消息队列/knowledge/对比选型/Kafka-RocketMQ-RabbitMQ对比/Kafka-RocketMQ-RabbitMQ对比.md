# Kafka-RocketMQ-RabbitMQ对比

## 场景对比卡
Q: Kafka、RocketMQ、RabbitMQ 的典型适用场景怎么对比？
A:
- Kafka 更适合高吞吐日志流、埋点、数据同步、流式处理
- RocketMQ 更适合业务消息、电商交易、事务消息、延时消息
- RabbitMQ 更适合路由灵活、协议标准、延迟敏感、中小规模业务消息
- 三者都能做消息队列，但设计侧重点不同
- 面试表达：选型要从业务语义和运维生态出发，不只看吞吐

## 存储架构卡
Q: Kafka 和 RocketMQ 的 Broker 架构和存储有什么区别？
A:
- Kafka 以 Topic-Partition 日志为核心，分区日志天然有序
- RocketMQ 使用 CommitLog 顺序写，ConsumeQueue 做消费索引
- Kafka 消费位点通常由消费者组维护在内部 Topic
- RocketMQ 按 Topic、Queue、ConsumerGroup 管理消费进度
- 二者都利用顺序写提升吞吐，但索引和消费模型不同

## 确认机制卡
Q: Kafka 和 RocketMQ 的消息确认机制有什么不同？
A:
- Kafka 生产端通过 acks 控制 leader 或 ISR 确认级别
- Kafka 消费端通过 offset 提交表示消费进度
- RocketMQ 生产端发送后收到 Broker 结果
- RocketMQ 消费端返回消费状态，失败可进入重试或死信
- 本质都要处理生产确认、存储可靠、消费确认三段链路

## 正确性审查卡
Q: MQ 对比选型有哪些常见误区？
A:
- “Kafka 不能做业务消息”：能做，但事务/延时/业务语义支持要评估
- “RabbitMQ 吞吐低所以不能用”：中小规模和复杂路由场景依然合适
- “RocketMQ 一定适合所有电商场景”：还要看团队运维和生态
- “只看单机吞吐选型”：错误。可靠性、顺序、延迟、运维和业务语义同样重要
- “换 MQ 就能解决业务设计问题”：错误。幂等、补偿、限流仍要业务设计
