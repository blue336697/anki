# RocketMQ Push、Pull、长轮询与消费线程模型

> 基线：经典 PushConsumer 是客户端托管的拉取。RocketMQ 5.x 还提供 PushConsumer、SimpleConsumer 等新客户端语义，不能混为同一套 Offset 模型。

## 01-Push本质
Q: 为什么说 RocketMQ PushConsumer 本质上仍然是 Pull？
A:
- Broker 不维护到每个业务监听器的主动推送流；客户端后台 PullMessageService 持续向 Broker 发起拉取请求。
- SDK 把路由、Rebalance、长轮询、流控、本地缓存和消费线程池封装起来，对业务暴露 Listener 回调，因此使用体验像 Push。
- 这种模式避免 Broker 主动控制大量客户端连接上的业务并发，同时让客户端根据本地积压调节拉取。
- 面试中应说“客户端托管 Pull”，而不是简单回答 Broker 主动推送。

## 02-PullRequest
Q: 经典 PushConsumer 中一个 PullRequest 代表什么？
A:
- 它通常绑定一个 MessageQueue、下一次拉取 Offset、所属 ProcessQueue 和 ConsumerGroup。
- Rebalance 为新分配的 Queue 创建 ProcessQueue 与 PullRequest，并把它提交给 PullMessageService 循环执行。
- 每次响应后，客户端根据找到消息、无新消息、Offset 非法等状态更新下一位置并安排后续拉取。
- Queue 被撤销时 ProcessQueue 会标记 dropped，后续拉取和消费必须停止，避免旧所有者继续处理。

## 03-Broker长轮询
Q: Broker 长轮询怎样避免没有消息时客户端空转？
A:
- Pull 请求到达时若目标 Queue 暂无满足条件的新消息，Broker 可挂起请求而不是立即返回空结果。
- PullRequestHoldService 按 Topic-Queue 保存等待请求；新消息派发到达时触发通知并重新检查 Offset 与过滤条件。
- 到达挂起超时也会唤醒请求，客户端收到空结果后继续下一轮，防止请求永久占用。
- 长轮询减少无效请求又保持较低到达延迟，但 Broker 仍需控制挂起请求数量、超时扫描和网络资源。

## 04-拉取结果
Q: 经典拉取常见结果状态分别意味着什么？
A:
- `FOUND` 表示返回一批匹配消息，客户端把它们放入 ProcessQueue 并推进下一拉取 Offset。
- `NO_NEW_MSG` 或 `NO_MATCHED_MSG` 表示当前无新消息或被过滤，通常使用 Broker 建议的下一 Offset 继续。
- `OFFSET_ILLEGAL` 表示请求位置超出当前有效范围，可能由保留清理、错误提交或重置造成。
- 处理 Offset 异常不能静默跳过关键数据，应结合 min/max Offset、业务保留期和告警策略决定修正。

## 05-ProcessQueue
Q: ProcessQueue 在客户端内存中保存什么，为什么它不是 Broker Queue？
A:
- 它是某个客户端当前持有 MessageQueue 的本地消费快照，缓存已拉取但尚未完成处理的 MessageExt。
- 结构会跟踪消息数量、总大小、最大 Offset、消费锁和 dropped 状态，为并发消费、顺序消费和本地流控服务。
- Broker MessageQueue 是持久化逻辑分片；ProcessQueue 会随 Rebalance 创建和丢弃，进程重启后不保留。
- 本地缓存过大既占堆又扩大重平衡和崩溃后的重复窗口，因此 SDK 会根据阈值暂停继续拉取。

## 06-并发消费
Q: 并发消费线程池如何影响吞吐和消息完成顺序？
A:
- 拉取服务按批次把消息提交给 ConsumeMessageConcurrentlyService，消费线程池并行调用 Listener。
- 即使消息来自同一 Queue，批次和线程并发也可能使业务完成顺序不同于 QueueOffset 顺序。
- 成功消息推进可提交位置，失败消息进入重试；一批内部分成功时要理解客户端如何拆分结果。
- 增大线程数只在业务 CPU 或外部依赖有余量时有效，否则会增加连接竞争、超时和重复。

## 07-消费结果与异步派发
Q: 为什么不应在 PushConsumer Listener 中把消息丢到另一个线程后立即返回成功？
A:
- Listener 返回成功会让 SDK 认为本次处理已完成并推进消费状态，而真正异步任务可能随后失败或进程崩溃。
- 返回前必须完成关键业务事务，或者至少把任务可靠写入本地持久化工作表，再由独立工作者处理。
- 长任务若无法在消费期限内完成，应选择可控制不可见时间的 SimpleConsumer 或拆分任务，而不是伪异步。
- SDK 的消费线程池已经提供并行度，额外线程池需要明确所有权、容量、拒绝和关闭语义。

## 08-SimpleConsumer
Q: RocketMQ 5.x SimpleConsumer 与 PushConsumer 的核心差别是什么？
A:
- SimpleConsumer 由业务主动调用 receive 获取消息，并显式调用 ack；并发、批次和处理流程由应用管理。
- Broker 为已取消息设置 InvisibleDuration，在不可见期内其他消费者不会再次取得；超时未 ACK 后可重新投递。
- 处理可能超过初始不可见时间时，应及时 changeInvisibleDuration，而不是等重复发生后再去重。
- 它适合需要自定义异步流程和消费节奏的场景，但应用必须自己承担线程、背压和 ACK 管理。

## 09-消费超时
Q: 消费处理时间过长会引发什么连锁反应？
A:
- PushConsumer 监听器长期占用线程会使本地 ProcessQueue 增长、拉取受限、消费延迟上升，并可能触发超时重试。
- SimpleConsumer 若不可见时间到期，消息会重新可见，旧任务可能仍在执行，于是产生并发重复。
- 顺序消费中长任务或失败还会阻塞同一消息组或 Queue 后续消息，放大尾延迟。
- 应把任务拆短、为外部调用设置 deadline、持久化长任务状态，并监控处理时长分位数而非只看平均值。

## 10-正确性审查
Q: 关于 RocketMQ 消费线程模型，哪些说法需要修正？
A:
- “PushConsumer 是 Broker 主动推消息”错误；经典实现由客户端后台长轮询拉取。
- “拉到消息就算消费成功”错误；还要经过业务处理和消费结果提交。
- “增加消费线程一定提升吞吐”错误；Queue 并行度、下游容量、锁和外部连接池都可能先成为瓶颈。
- “Listener 可以随意异步化”错误；提前返回成功会破坏 SDK 的可靠重试边界。
