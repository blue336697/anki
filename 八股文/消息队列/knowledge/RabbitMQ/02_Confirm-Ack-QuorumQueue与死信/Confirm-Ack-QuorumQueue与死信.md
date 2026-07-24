# RabbitMQ Confirm、ACK、Quorum Queue 与死信

> 基线：现代 RabbitMQ 可靠性重点是 Publisher Confirm、Consumer Manual ACK 与 Quorum Queue。经典镜像队列已在 RabbitMQ 4.0 移除。

## 01-PublisherConfirm
Q: Publisher Confirm 解决什么问题？
A:
- Channel 进入 confirm 模式后，Broker 会对后续发布返回 ACK 或 NACK，Producer 可知道 Broker 是否承担了当前发布。
- ACK 可按 delivery sequence number 单条或批量确认，客户端需要维护有界的在途消息映射。
- 连接在确认前断开时结果未知，Producer 应重发未确认消息，因此仍可能产生重复。
- Confirm 与 Consumer ACK 互相独立：前者覆盖 Producer 到 Broker，后者覆盖 Broker 到 Consumer。

## 02-持久化条件
Q: durable Queue、persistent message 和 Confirm 为什么缺一不可？
A:
- durable 只让 Queue 元数据在重启后恢复；消息还需要使用持久化 delivery mode 才具有相应磁盘语义。
- Publisher Confirm 告诉客户端 Broker 已按目标 Queue 类型的规则接管消息，未确认消息必须保留并重发。
- Classic 单副本 Queue 即使持久化仍有单机磁盘故障风险；Quorum Queue 才把日志复制到多个成员。
- 可靠链路还要处理 mandatory Return，否则消息可能根本没有被路由到 Queue。

## 03-ConsumerACK
Q: 自动 ACK 和手动 ACK 的故障语义有什么不同？
A:
- 自动 ACK 常在消息发送给客户端后就认为成功，客户端进程随后崩溃会丢失尚未完成的业务处理。
- 手动 ACK 应在本地关键事务成功后发送；连接关闭前未 ACK 的交付会重新入队，形成至少一次。
- delivery tag 只在当前 Channel 上有效，不能跨 Channel ACK；错误 ACK 可能关闭 Channel。
- 可以批量 ACK 降低协议开销，但批次中业务结果不一致时要谨慎确定确认边界。

## 04-NACK与Requeue
Q: `basic.reject/basic.nack` 的 requeue 参数有什么风险？
A:
- `requeue=true` 把消息重新放回队列供再次交付，适合短暂故障，但可能很快再次被同一批消费者取得。
- 永久失败若不断 requeue，会形成 CPU、网络和日志空转的重投循环。
- `requeue=false` 会在配置 DLX 时死信，否则被丢弃；这不是“自动进入某个固定死信队列”。
- 应使用重试次数、退避队列或 Quorum Queue delivery-limit 等机制建立有限失败状态机。

## 05-Prefetch
Q: Prefetch 如何同时影响吞吐、公平性和重复窗口？
A:
- Prefetch 限制一个 Consumer/Channel 尚未 ACK 的在途消息数，防止 Broker 无界推送到慢消费者。
- 值太小会因网络往返和处理间隙降低吞吐，值太大则让快慢消费者分配不均并增加客户端内存。
- 消费者崩溃时，所有未 ACK 消息会重新入队；prefetch 越大，一次故障潜在重复批次越大。
- 应根据单条处理时间、并发数、内存和下游容量压测，不存在适合所有业务的固定数值。

## 06-QuorumQueue
Q: Quorum Queue 如何提供数据安全？
A:
- 每个 Quorum Queue 是一个 Raft 复制组，由 Leader 接收写入并复制日志到 Followers。
- Publisher Confirm 在消息满足多数派接管条件后返回；只要多数成员没有永久丢失，已确认消息具备更强恢复保证。
- 少数派分区不能继续形成合法写多数，系统偏向一致性；成员数越多，复制开销和尾延迟通常越高。
- 推荐使用较小奇数副本组并跨故障域部署，而不是把副本数无限增加。

## 07-ClassicMirroredQueue
Q: 为什么面试时不能继续推荐 Classic Mirrored Queue？
A:
- 经典镜像队列长期存在同步、选主和一致性复杂性，RabbitMQ 已在 2021 年标记弃用，并于 4.0 移除。
- 现代高可靠队列应优先评估 Quorum Queue；需要长日志与重放时评估 Streams。
- 老系统迁移要检查 feature flags、策略、容量和客户端行为，不能只把类型名替换后直接上线。
- 回答版本边界能避免把旧教程中的 `ha-mode` 策略当作当前最佳实践。

## 08-TTL与DLX
Q: 消息在什么情况下会被 Dead Letter Exchange 重新发布？
A:
- 常见触发包括 Consumer reject/nack 且不 requeue、消息 TTL 到期、队列超过长度限制，以及 Quorum Queue 超过 delivery-limit。
- DLX 是普通 Exchange，源 Queue 通过 policy 指定 dead-letter-exchange 和可选 routing key。
- 整个 Queue 因 Queue TTL 过期被删除时，其中消息并不会逐条死信。
- DLX 转发也可能失败或产生重复，关键恢复链路需要监控目标路由和安全策略。

## 09-TTL延迟队列
Q: 为什么“TTL Queue + DLX”实现延迟消息存在头阻塞问题？
A:
- 经典做法把消息放进带 TTL 的等待 Queue，到期后由 DLX 路由到工作 Queue。
- 某些 Queue 类型只有消息到达队头时才真正移除并死信；后入但 TTL 更短的消息可能被前面的长 TTL 消息挡住。
- 通过不同固定延迟档位拆 Queue 可以缓解，但会增加拓扑并限制任意时间。
- 需要大量任意定时、取消和精度控制时，应评估 RabbitMQ 延迟插件或专用调度/具备原生定时能力的平台。

## 10-正确性审查
Q: 关于 RabbitMQ 可靠性，哪些说法需要纠正？
A:
- “开启 durable 就不会丢”错误；还需 persistent message、Confirm、路由校验和副本策略。
- “Publisher Confirm 等于 Consumer ACK”错误；它们分别覆盖链路两端，完全独立。
- “NACK 会自动进入死信队列”错误；必须 `requeue=false` 且源 Queue 配置了有效 DLX 路由。
- “镜像队列仍是现代高可用方案”已过时；RabbitMQ 4.x 应以 Quorum Queue 等当前能力为基线。
