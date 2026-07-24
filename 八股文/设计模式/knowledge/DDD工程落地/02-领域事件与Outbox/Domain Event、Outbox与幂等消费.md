# Domain Event、Outbox 与幂等消费
## 01-领域事件
Q: Domain Event 应表达什么？
A:
- 表达领域中已经发生、业务关心的事实，用过去式命名，如 `OrderConfirmed`，内容是当时事实快照。
- 事件由聚合行为产生，应用层在合适事务边界发布；不应在实体中直接调用 MQ SDK。
- 同上下文内可同步处理，跨上下文通常异步集成，但两者可靠性语义不同。
- 事件不是“任意方法调用异步化”，消费者应因事实作自主决策。
## 02-原子性问题
Q: 数据库提交与 MQ 发布为什么会出现双写不一致？
A:
- 先提交数据库再发消息，进程在中间崩溃会丢事件；先发消息再提交，回滚会让消费者看到不存在事实。
- 简单 try/catch 不能覆盖宕机和网络不确定；分布式事务可解决但成本/可用性高。
- Transactional Outbox 在同一数据库事务写业务数据和 outbox row，后台可靠转发。
- 这保证最终发布，不自动保证只发布一次。
## 03-Outbox流程
Q: Outbox relay 怎样安全重试？
A:
- 事务写 `eventId,type,aggregateId,payload,occurredAt,status`；relay 轮询/CDC 发送并标记。
- 发送成功但标记前崩溃会重复，所以 broker/消费者需按 eventId 幂等。
- 多 relay 用锁、skip locked 或分区领取，失败退避并设死信/告警。
- 清理需保留足够审计与重放窗口，schema 版本也要兼容。
## 04-代码示例
Q: 聚合怎样记录事件而不依赖消息中间件？
A:
```java
final class Order {
    private final List<DomainEvent> events = new ArrayList<>();
    void confirm() {
        // validate and change state
        events.add(new OrderConfirmed(id, Instant.now()));
    }
    List<DomainEvent> pullEvents() {
        List<DomainEvent> copy = List.copyOf(events);
        events.clear(); return copy;
    }
}
```
- Repository/UoW 把状态与事件写入同一事务，relay 再发布。
## 05-消费语义
Q: 如何实现事件消费者幂等并处理乱序？
A:
- 用 eventId 去重表与业务更新同事务，或让业务写天然条件化，如状态/version 只前进。
- “先查再做”若不在同一事务仍有竞态，需唯一约束或原子 compare-and-set。
- 按 aggregateId 分区可保持单聚合顺序，跨聚合不存在全局顺序保证。
- 重试、死信和人工补偿必须可观测，exactly-once 不能只靠宣传语。

