# RocketMQ Rebalance、Offset、重试与死信

> 基线：经典 4.x 客户端主要按 Queue 分配并维护 Group Offset；5.x 新客户端可采用消息级负载均衡和 InvisibleDuration 状态机。

## 01-Rebalance输入
Q: 经典队列级 Rebalance 依赖哪些输入？
A:
- 输入包括 Topic 的 MessageQueue 集合、同一 ConsumerGroup 的在线客户端 ID 列表、当前实例 ID 和分配算法。
- 客户端通过心跳向 Broker 注册订阅与成员信息，并周期执行 Rebalance；Broker 或路由变化会改变输入集合。
- 所有成员必须看到相近且排序一致的 Queue 和客户端列表，才能各自计算出不重叠的分配结果。
- 网络抖动或视图短暂不一致会造成迁移窗口，因此 Rebalance 天然需要幂等和可恢复 Offset。

## 02-分配算法
Q: Queue 平均分配算法怎样工作，为什么消费者可能空闲？
A:
- 算法通常对排序后的 Queue 和 Consumer ID 做确定性切片，使每个成员独立算出自己负责的集合。
- Queue 不能在队列级模型中拆给多个实例，所以当消费者实例数大于 Queue 数时，多出的实例没有任务。
- Queue 数不能整除消费者数时，部分实例会多承担一个或一段 Queue，负载不一定按消息量均匀。
- 热点 Queue 即使只分给一个实例，也可能远重于其他 Queue；平均分配的是数量，不是实际工作量。

## 03-触发与代价
Q: 哪些事件会触发 Rebalance，它为什么可能造成抖动？
A:
- Consumer 上下线、心跳超时、Topic Queue 数变化、Broker 路由变化和订阅变更都会重新计算归属。
- 新归属需要创建 PullRequest，旧归属需要停止拉取、等待消费或持久化 Offset并移除 ProcessQueue。
- 实例频繁重启会让 Queue 不断迁移，缓存失效、短暂停顿和重复消费随之增加。
- 扩容前应先稳定实例、预热依赖并观察 Queue 数，不要在积压压力下进行无节制自动伸缩。

## 04-撤销竞态
Q: Rebalance 时为什么可能重复消费？
A:
- 旧消费者已处理并提交业务事务，但 Offset 尚未成功提交时失去 Queue；新消费者会从旧 Offset 再次拉取。
- 旧 ProcessQueue 被标记 dropped 前，已经进入线程池的任务可能仍在运行，与新所有者形成短暂并发。
- 网络分区会让成员视图收敛需要时间，Broker 端锁和客户端状态只能降低窗口，无法代替业务幂等。
- 所以 RocketMQ 官方也要求消费逻辑具备幂等性，Rebalance 不是严格的一次性所有权事务。

## 05-Offset含义
Q: Consumer Offset、MinOffset 和 MaxOffset 分别表示什么？
A:
- QueueOffset 是消息在逻辑 Queue 中的位置；MinOffset 是当前仍保留的最早位置，MaxOffset 通常指向最新消息之后的边界。
- Consumer Offset 是某个 Group 下一次应读取或已确认推进到的位置，具体 API 表达要结合版本。
- `MaxOffset - ConsumerOffset` 可近似表示队列积压条数，但不能直接代表积压字节、处理时间或业务风险。
- 若 Consumer Offset 小于 MinOffset，说明对应历史消息已被清理，无法仅靠继续拉取恢复。

## 06-Offset存储
Q: 集群消费和广播消费的 Offset 存在哪里？
A:
- 经典集群消费由 Broker 端按 Topic、Group、Queue 维护 Offset，实例替换后仍能继承消费进度。
- 客户端会在内存中更新并按策略提交，异常退出前未提交的进度可能导致重启后重复。
- 经典广播消费常把每个实例的进度保存在本地，因为每个实例都要独立消费一份。
- 本地广播进度随容器漂移或磁盘丢失可能消失，所以广播不宜承担需要严格恢复的关键任务。

## 07-初始与重置
Q: 新 Group 第一次消费和人工重置 Offset 有哪些风险？
A:
- 初始位置受客户端版本、消费模式、是否存在历史 Offset 和配置影响；RocketMQ 5.x 官方模型通常从首次接收时的最大 Offset 开始。
- 不能背诵“永远从最早”或“永远从最新”，上线前应在目标版本和客户端上验证。
- 重置到过去可用于修复和回放，但会带来重复、旧 Schema、冷数据 IO 和下游洪峰。
- 重置到未来相当于跳过消息，必须经过业务授权、记录范围，并由对账确认被跳过的数据可舍弃。

## 08-经典重试Topic
Q: 经典并发消费失败后，消息怎样进入重试链路？
A:
- Listener 返回失败或抛出异常后，客户端/Broker 将消息转入与 ConsumerGroup 关联的重试 Topic，常见命名为 `%RETRY%group`。
- 重试消息携带原 Topic、消费次数等属性，经过预设延迟后再次投递给该 Group。
- 达到最大重试次数后进入该 Group 的死信队列，常见命名为 `%DLQ%group`。
- 这是经典实现细节；不同版本、消费类型和顺序消费的重试状态与间隔配置并不完全相同。

## 09-5x消费状态机
Q: RocketMQ 5.x 为什么用 Ready、Inflight、WaitingRetry、Commit、DLQ 描述消费？
A:
- Ready 表示可被取得；取得后进入 Inflight，在不可见窗口内避免被其他消费者立即重复拿走。
- 成功 ACK 进入 Commit；失败或超时按消费者类型进入 WaitingRetry 或重新 Ready，超过次数进入 DLQ。
- PushConsumer 由 SDK 管理回调和重试，SimpleConsumer 由应用管理 InvisibleDuration 与 ACK。
- 状态机更适合解释消息级负载均衡，不能直接拿经典 Queue Offset 提交的每个细节套用。

## 10-死信恢复
Q: 死信消息应该怎样治理和恢复？
A:
- 首先按业务键、异常类型和版本区分永久数据错误、代码缺陷与暂时依赖故障，不能直接整队重放。
- 修复消费者后，把选定死信复制到受控恢复 Topic 或使用管理能力重投，保留原消息 ID、业务键和失败上下文。
- 设置限速、独立 Group 和熔断，确保恢复流量不会再次击穿生产依赖。
- 对 DLQ 数量、最老年龄和增长率告警；没有责任人和恢复流程的 DLQ 只是延迟的数据丢失。

## 11-正确性审查
Q: 关于 Rebalance、Offset 和重试，哪些说法需要纠正？
A:
- “一个 Queue 永远只会被一个消费者处理”缺少时间边界；重平衡迁移时可能出现短暂重复和并发。
- “积压量就是 MaxOffset 减 Offset，所以能直接算恢复时间”不完整；还需消息大小、处理成本和热点分布。
- “重试会一直进行直到成功”错误；通常存在次数、时间和死信边界，顺序消息策略也不同。
- “4.x 和 5.x 消费模型完全相同”错误；要先确认客户端类型、队列级或消息级负载均衡以及 ACK 方式。
