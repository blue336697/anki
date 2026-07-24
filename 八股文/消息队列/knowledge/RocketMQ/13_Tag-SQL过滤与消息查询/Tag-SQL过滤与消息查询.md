# RocketMQ Tag、SQL92 过滤与消息查询

> 基线：过滤决定某个 ConsumerGroup 能看到哪些消息，Key 查询用于排障定位。过滤条件属于订阅契约，同组实例必须保持一致。

## 01-Topic与过滤边界
Q: 应该拆 Topic，还是在同一 Topic 中用 Tag 过滤？
A:
- 不同业务域、权限、消息类型、保留期、吞吐等级或故障影响面的消息应拆 Topic，形成独立治理边界。
- 同一业务域内少量稳定子类型可使用 Tag，例如订单创建、取消和完成，减少 Topic 爆炸。
- RocketMQ 5.x 对 NORMAL、FIFO、TRANSACTION、DELAY 等消息类型有 Topic 类型语义，不应只靠 Tag 混装。
- 如果两个订阅方需要完全不同的容量和 SLA，即使 Schema 相似也应考虑拆 Topic。

## 02-Tag过滤
Q: RocketMQ Tag 过滤的规则和内部优化是什么？
A:
- Producer 为消息设置单个 Tag，Consumer 可订阅一个 Tag、用 `||` 组合多个 Tag，或用 `*` 匹配全部。
- Broker 可先利用 ConsumeQueue 中的 TagsCode 做快速候选过滤，再在需要时读取消息属性进行确认。
- Tag 适合精确字符串分类，不支持任意层级通配或范围比较。
- 哈希优化不改变契约语义；应用不能直接依赖 TagsCode 数值或认为它是全局无碰撞标识。

## 03-SQL92过滤
Q: SQL92 属性过滤能表达什么？
A:
- Producer 在消息 properties 中设置自定义属性，Consumer 使用比较、逻辑运算、`IS NULL`、`BETWEEN`、`IN` 等受支持表达式筛选。
- Broker 在服务端执行过滤，避免大量无关消息传给客户端，但表达式计算和属性读取比 Tag 更昂贵。
- 属性缺失、类型不匹配或表达式求值异常通常会让消息不匹配，因此 Schema 和类型必须稳定。
- SQL92 支持范围受版本与 Broker 配置影响，上线前要在目标集群验证，而不是假设完整数据库 SQL 都可用。

## 04-订阅一致性
Q: 为什么同一 ConsumerGroup 的订阅表达式必须一致？
A:
- 同 Group 实例共同承担同一业务职责，Broker 可能把不同 Queue 或消息分给不同实例。
- 如果实例 A 订阅 TagA、实例 B 订阅 TagB，最终收到哪些消息取决于 Queue 归属和最近注册的订阅数据，可能产生永久遗漏。
- Topic、过滤表达式和版本应作为部署配置统一发布，并在 Broker/客户端连接信息中巡检。
- 需要不同过滤结果的业务应使用不同 ConsumerGroup，而不是让同组实例各自决定。

## 05-过滤与Offset
Q: 被过滤掉的消息会不会阻止 Consumer Offset 前进？
A:
- Broker 拉取会扫描逻辑 Queue，从请求 Offset 向后查找满足表达式的消息，并返回建议的下一 Offset。
- 不匹配消息对该 Group 不需要业务消费，但逻辑扫描位置仍会越过它们，否则每次拉取都会重复检查。
- 因此后来修改订阅表达式不会自动补回此前被过滤并越过的历史消息。
- 若需要追溯，应创建新 Group 或受控重置 Offset，并确认消息仍在保留期内。

## 06-Key与IndexFile
Q: 用消息 Key 查询时应注意什么？
A:
- Key 会参与 Broker IndexFile 构建，可按业务订单号或请求号取得一组候选 CommitLogOffset。
- 哈希碰撞、多 Key、索引容量和派发延迟意味着结果可能多条、延迟或不完整，不能作为在线数据库查询接口。
- 查询后应读取消息 properties 验证真实 Key，并结合 Topic、时间范围和业务发送记录缩小范围。
- Key 是排障线索，业务幂等与权威状态仍应存放在数据库。

## 07-消息轨迹
Q: 消息轨迹能回答哪些问题，不能回答哪些问题？
A:
- 轨迹可关联 Producer 发送、Broker 存储、Consumer 投递和消费结果，帮助定位消息停在哪一段。
- 业务应传播 traceId、业务键、消息 ID、Topic、Queue、Offset 与 ConsumerGroup，形成跨系统关联。
- 轨迹采集本身也可能采样、延迟或失败，缺少轨迹不等于消息一定没发送。
- 它不能证明消费者数据库状态正确，最终仍需业务幂等记录和对账数据。

## 08-正确性审查
Q: 关于过滤和查询，哪些常见说法需要纠正？
A:
- “Tag 可以像 RabbitMQ Topic Exchange 一样任意通配”错误；RocketMQ Tag 主要是精确值及 `||` 组合。
- “同 Group 不同实例可以订阅不同 Tag 来分工”错误；这会破坏订阅一致性。
- “修改 Tag 订阅后历史消息会自动补消费”错误；此前 Offset 可能已经越过。
- “按 Key 查询是强一致唯一索引”错误；IndexFile 是带哈希与派发延迟的辅助索引。
