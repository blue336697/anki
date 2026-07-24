# RabbitMQ Exchange、Queue 与路由模型

> 基线：以 AMQP 0-9-1 常见模型和现代 RabbitMQ 4.x 运维边界为主。RabbitMQ 在本牌组中用于理解路由模型和与 RocketMQ 的差异。

## 01-核心实体
Q: RabbitMQ 中 Producer、Exchange、Queue、Binding 和 Consumer 如何协作？
A:
- Producer 把消息发布到 Exchange，并携带 routing key；它通常不直接指定最终 Queue。
- Binding 定义 Exchange 到 Queue 或另一个 Exchange 的路由规则，Exchange 根据自身类型计算目标。
- Queue 保存被路由进来的消息，Consumer 从 Queue 获取并通过 ACK/NACK 表示处理结果。
- Exchange 本身通常不存储消息；如果没有任何匹配路由且未配置返回或备选策略，消息可能被丢弃。

## 02-DirectExchange
Q: Direct Exchange 的路由规则是什么？
A:
- 消息 routing key 与 Binding key 完全相等时，消息被路由到对应绑定 Queue。
- 同一个 key 可以绑定多个 Queue，因此一条消息可以复制到多个目标；一个 Queue 也能绑定多个 key。
- 默认 Exchange 是名称为空的特殊 Direct Exchange，Queue 声明后通常自动以队列名作为 binding key 绑定。
- Direct 适合有限、明确的业务分类，不等于“只能点对点”。

## 03-TopicExchange
Q: Topic Exchange 的 `*` 和 `#` 怎样匹配？
A:
- routing key 通常由点分隔单词，如 `order.cn.created`；Binding pattern 按这些单词匹配。
- `*` 匹配恰好一个单词，`#` 匹配零个或多个单词，例如 `order.*.created` 与 `order.#`。
- 过宽的 `#` 绑定会扩大消息扇出和存储成本，复杂通配规则也会增加治理难度。
- routing key 是路由契约，应有稳定命名规范，不能把任意用户输入直接作为高基数拓扑。

## 04-Fanout与Headers
Q: Fanout 和 Headers Exchange 适合什么场景？
A:
- Fanout 忽略 routing key，把消息路由到所有绑定 Queue，适合配置刷新、广播通知等明确扇出。
- Headers 根据消息 header 的键值和 `x-match` 规则匹配，表达力更强但路由成本和契约复杂度更高。
- “所有实例都收到”仍要为实例或业务建立相应 Queue；同一 Queue 的多个消费者是竞争消费，不是广播。
- 简单类别优先 Direct/Topic，避免为了灵活性使用难以观测和治理的 Headers 规则。

## 05-Queue属性
Q: durable、exclusive、auto-delete 分别控制什么？
A:
- durable 表示 Broker 重启后 Queue 定义是否保留，不代表其中每条消息一定安全，消息持久化与复制还要单独配置。
- exclusive Queue 只允许声明它的连接使用，并在连接关闭时删除，适合临时回复或会话资源。
- auto-delete 在最后一个消费者取消后按条件删除，和“空队列立即删除”不是同义词。
- Queue 重新声明时关键属性必须兼容，否则 Channel 会因 precondition failed 关闭；生产拓扑应由一致的配置管理。

## 06-Connection与Channel
Q: 为什么 RabbitMQ 客户端通常复用 Connection 并创建多个 Channel？
A:
- TCP Connection 建立和 TLS 握手成本较高，Channel 在一条连接上多路复用 AMQP 会话，隔离 publish、consume 和事务状态。
- Channel 不是线程安全共享对象的通用替代，客户端应遵循具体库的并发模型。
- 协议级错误常只关闭出错 Channel，连接仍可服务其他 Channel；网络故障则影响整条 Connection。
- Channel 数过多也会消耗 Broker 进程、内存和心跳资源，应使用池化或有界生命周期。

## 07-Unroutable
Q: Producer 怎样发现消息没有路由到任何 Queue？
A:
- Publisher Confirm 只说明 Broker 对发布请求的处理结果，本身不保证至少匹配一个 Queue。
- 发布时设置 `mandatory`，无匹配 Queue 的消息会通过 `basic.return` 返回客户端；应用必须注册并处理 Return 回调。
- Alternate Exchange 可把无路由消息转到备选交换机统一审计，但配置错误仍需告警。
- 只开 Confirm 不开 mandatory/return 处理，会出现“发布确认成功但业务消息无处可去”。

## 08-竞争消费
Q: 一个 Queue 有多个 Consumer 时，消息怎样分配？
A:
- Broker 向该 Queue 的活跃消费者分发消息，通常形成竞争消费，一条交付只交给其中一个 Consumer。
- 分发并非严格按业务处理能力公平，prefetch、未确认消息数、消费者速度和优先级都会影响。
- 若要让多个业务各收到一份，应为每个业务创建独立 Queue 并绑定同一 Exchange。
- Consumer 宕机后未 ACK 消息可重新入队交给其他实例，因此业务仍需幂等。

## 09-Queue类型
Q: Classic Queue、Quorum Queue 和 Stream 的定位有什么不同？
A:
- Classic Queue 适合传统低延迟队列语义，但现代版本不应再依赖已移除的经典镜像队列方案获得复制。
- Quorum Queue 基于 Raft 复制，强调数据安全和明确的多数派语义，写延迟与磁盘成本更高。
- Stream 是追加日志和按 Offset 重放模型，更适合长保留、大积压、多个订阅者和流式读取。
- 选型应基于可靠性、重放、延迟、积压和拓扑寿命，而不是把所有 Queue 都无差别改为 quorum。

## 10-正确性审查
Q: 关于 RabbitMQ 路由模型，哪些说法不准确？
A:
- “Producer 把消息直接发到 Queue”忽略了 AMQP Exchange 路由层；默认 Exchange 只是让它看起来像直发。
- “Fanout 保证每个消费者都收到”错误；它路由到 Queue，同一 Queue 内消费者仍竞争。
- “durable Queue 里的消息一定不丢”错误；还需 persistent 消息、Publisher Confirm 和适当副本类型。
- “Confirm 成功说明消息一定进入某个 Queue”错误；无路由也可能确认，需 mandatory Return 或备选交换机。
