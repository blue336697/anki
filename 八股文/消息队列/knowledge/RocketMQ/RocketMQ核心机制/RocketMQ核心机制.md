# RocketMQ核心机制

## 架构卡
Q: RocketMQ 的核心组件有哪些？
A:
- Producer 负责发送消息
- Broker 负责消息存储和投递
- Consumer 负责消费消息
- NameServer 负责轻量级路由注册和发现
- Topic 下有多个 MessageQueue，用于并行存储和消费

## 存储卡
Q: RocketMQ 的消息存储模型如何理解？
A:
- CommitLog 顺序写保存消息主体
- ConsumeQueue 是按 Topic/Queue 组织的消费索引
- IndexFile 支持按 key 查询消息
- 顺序写 CommitLog 提高写入吞吐
- 消费通过 ConsumeQueue 定位 CommitLog 中的消息

## 消费卡
Q: RocketMQ 消费模式有哪些？
A:
- 集群消费：同一消费者组内消息被多个消费者分摊
- 广播消费：每个消费者都消费一份消息
- PushConsumer 本质上也常基于拉取和长轮询封装
- 消费进度按消费者组和队列维护
- 业务常用集群消费来水平扩展处理能力

## 正确性审查卡
Q: RocketMQ 有哪些常见误区？
A:
- “RocketMQ 没有路由中心”：有 NameServer，但它比 ZooKeeper 轻量
- “Push 就是 Broker 主动无限推”：不准确，通常是长轮询拉取封装
- “一个 Topic 只有一个队列”：错误。Topic 可有多个 MessageQueue
- “顺序写就不会丢消息”：不够。还要看刷盘、副本和确认策略
- “集群消费每个消费者都收到全部消息”：错误。那是广播消费语义
