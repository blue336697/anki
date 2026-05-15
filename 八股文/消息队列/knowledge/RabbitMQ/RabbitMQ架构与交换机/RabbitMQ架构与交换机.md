![RabbitMQ AMQP模型](knowledge/RabbitMQ/RabbitMQ架构与交换机/rabbitmq_architecture.svg)

# RabbitMQ架构与交换机

## AMQP卡
Q: RabbitMQ 和 AMQP 是什么关系？
A:
- RabbitMQ 是消息中间件产品
- AMQP 是高级消息队列协议规范
- RabbitMQ 实现了 AMQP，并提供交换机、队列、绑定、路由等模型
- 使用 AMQP 模型时，生产者通常把消息发到 Exchange
- Exchange 根据路由规则把消息投递到 Queue

## 组件卡
Q: RabbitMQ 核心组件有哪些？
A:
- Producer 生产消息
- Exchange 接收消息并路由
- Queue 存储消息
- Binding 建立 Exchange 和 Queue 的路由关系
- Consumer 从 Queue 消费消息

## 交换机卡
Q: RabbitMQ 有哪些常见交换机类型？
A:
- direct：按 routing key 精确匹配
- fanout：广播到绑定的所有队列
- topic：按通配符模式匹配 routing key
- headers：按消息 header 匹配
- 实际业务常用 direct/topic/fanout，headers 使用较少

## 正确性审查卡
Q: RabbitMQ 架构有哪些常见误区？
A:
- “生产者直接发到队列”：AMQP 模型中通常先发 Exchange
- “fanout 也看 routing key”：通常不看，直接广播
- “Exchange 存储消息”：消息主要存储在 Queue
- “RabbitMQ 只适合低吞吐”：不完整。它更强在路由灵活和协议生态
- “绑定关系无关紧要”：错误。路由是否正确取决于 Binding
