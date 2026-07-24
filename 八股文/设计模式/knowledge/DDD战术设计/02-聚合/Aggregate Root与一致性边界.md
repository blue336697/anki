# Aggregate Root 与一致性边界
## 01-定义
Q: 聚合和聚合根分别承担什么职责？
A:
- 聚合是一组作为一致性修改单元的实体和值对象；外部只能持有聚合根 ID 并通过根执行业务行为。
- 根维护内部不变量、控制成员生命周期并提供事务边界。
- 聚合不是“把所有有关对象装进一棵大对象图”，边界过大会导致锁冲突和加载成本。
- 跨聚合引用通常用 ID，跨边界一致性用事件/流程协调。
## 02-不变量
Q: 怎样从业务不变量推导聚合边界？
A:
- 找出必须在一次命令/事务内始终成立的规则，例如订单总额等于行项目之和、已支付订单不能删除行。
- 共同参与这些强一致规则的对象是聚合候选；只需稍后同步的规则不应强塞进同一聚合。
- 并发冲突和事务粒度验证边界：热点根频繁版本冲突说明聚合可能过大。
- 不变量要写进根行为和测试，而不是仅靠调用约定。
## 03-小聚合
Q: 为什么 DDD 倾向小聚合和最终一致？
A:
- 小聚合加载/保存少、事务短、并发冲突低，也容易划分所有权。
- 跨聚合强事务会把模型耦合到单库；通过领域事件让另一个聚合稍后反应更可扩展。
- 最终一致必须定义中间状态、重试、幂等和超时补偿，不是放弃正确性。
- 金融记账等确需原子的不变量应保留在同一边界或专用一致性机制。
## 04-代码示例
Q: Order 聚合如何保护“确认后不能再加行”？
A:
```java
final class Order {
    private final List<OrderLine> lines = new ArrayList<>();
    private OrderStatus status = OrderStatus.DRAFT;
    void addLine(ProductId id, int qty, Money price) {
        if (status != OrderStatus.DRAFT) throw new IllegalStateException("订单已确认");
        if (qty <= 0) throw new IllegalArgumentException("qty");
        lines.add(new OrderLine(id, qty, price));
    }
    List<OrderLine> lines() { return List.copyOf(lines); }
}
```
- 不暴露可变集合，所有修改都经过根。
## 05-并发
Q: 聚合怎样处理并发更新？
A:
- 常用 version 乐观锁：更新 `where id=? and version=?`，影响 0 行表示冲突，再重读或向用户返回。
- 悲观锁适合冲突高且事务短，但会阻塞并可能死锁；分布式锁不是默认答案。
- 命令应尽量表达可重试的意图，避免重放产生重复外部副作用。
- 聚合边界、数据库事务和消息发布原子性需一起设计。
