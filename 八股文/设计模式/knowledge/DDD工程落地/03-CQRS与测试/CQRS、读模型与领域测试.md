# CQRS、读模型与领域测试
## 01-CQRS
Q: CQRS 的最小含义是什么？
A:
- 命令模型负责执行业务行为和保护不变量，查询模型为读取场景优化；接口和模型分离，不必分库。
- 读侧可直接 SQL 投影 DTO，写侧加载聚合，避免为报表扭曲聚合边界。
- 只有读写复杂度/扩展需求明显时才值得，引入异步投影会增加最终一致和运维。
- CQRS 不等于 Event Sourcing，两者可独立使用。
## 02-读模型
Q: 异步投影 read model 怎样维护？
A:
- 订阅领域/集成事件，以 eventId 幂等更新反规范化表、搜索索引或缓存。
- 投影保存消费位置，可重建/回放；schema 变更用新投影并行构建后切换。
- 用户刚写后可能读不到，需业务接受、read-your-write 路由或同步返回关键结果。
- 投影不是权威真值，丢失可由事件/源数据恢复。
## 03-EventSourcing边界
Q: Event Sourcing 为什么不是“用了 MQ”？
A:
- 它以不可变事件序列作为聚合权威状态，当前状态通过 replay/fold 得到；MQ 只是传输设施。
- 优点是完整审计与时态重建，代价是事件版本、快照、回放副作用和删除隐私数据困难。
- 事件一旦成为历史契约不能随意改含义，upcaster/迁移策略不可缺。
- 大多数系统只需状态存储+领域事件，不必采用 Event Sourcing。
## 04-代码示例
Q: 领域测试如何直接验证聚合规则和事件？
A:
```java
@Test void confirmedOrderCannotAddLine() {
    Order order = Order.draft(new BuyerId("B1"));
    order.addLine(product, 1, money);
    order.confirm();
    assertThrows(IllegalStateException.class,
        () -> order.addLine(product, 1, money));
    assertTrue(order.pullEvents().get(0) instanceof OrderConfirmed);
}
```
- 测试无需 Spring/数据库，直接验证状态、不变量和产生的事实。
## 05-测试金字塔
Q: DDD 系统各层应分别测什么？
A:
- 值对象/聚合/领域服务用快速单元测试覆盖规则与边界；property-based test 适合金额/状态不变量。
- 应用服务用 fake port 验证事务编排和调用；adapter contract/integration test 验证 SQL、MQ、第三方协议。
- 少量端到端测试验证 wiring 与关键旅程，不能用慢 E2E 替代领域规则测试。
- 架构测试可禁止领域层依赖 Spring/JPA/adapter 包，持续守住依赖方向。
