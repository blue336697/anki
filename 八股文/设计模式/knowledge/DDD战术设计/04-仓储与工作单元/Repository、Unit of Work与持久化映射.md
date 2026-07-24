# Repository、Unit of Work 与持久化映射
## 01-仓储语义
Q: Repository 为什么以聚合为单位而不是每张表一个 DAO？
A:
- Repository 模拟聚合集合，接口使用领域 ID/条件返回完整聚合根，隐藏 SQL/缓存/ORM。
- 只有聚合根通常有 repository，内部实体由根管理，避免绕过不变量单独更新。
- 接口放领域/应用内核，实现在基础设施层；分页 DTO 查询可走独立 read model。
- Repository 不应泄漏 EntityManager、数据库 row 或任意 save 子实体。
## 02-Save语义
Q: `save(order)` 应该 insert、update 还是 upsert？
A:
- 领域接口表达持久化意图，具体由 identity/version 和实现决定；契约应说明新增、并发冲突与返回值。
- 自动 dirty checking 方便但隐藏 SQL 和事务时机；显式 save 更可见，两者均可正确。
- upsert 可能掩盖重复创建和版本冲突，不应默认用数据库语法替代业务语义。
- 保存聚合必须原子维护其内部表和 version。
## 03-UnitOfWork
Q: Unit of Work 解决什么？
A:
- 跟踪一个业务事务中加载/新增/修改的聚合，在 commit 时统一写入并保证数据库原子性。
- JPA persistence context 是一种实现：identity map 保证同 ID 同实例，dirty checking 在 flush 生成 SQL。
- flush 不等于 commit，SQL 已发仍可回滚；长事务会积累对象、锁和陈旧数据。
- 跨数据库/消息不自动在同一 UoW，需 Outbox/Saga 等策略。
## 04-代码示例
Q: 一个不泄漏 JPA 的订单仓储接口怎样定义？
A:
```java
interface OrderRepository {
    Optional<Order> find(OrderId id);
    void add(Order order);
    void save(Order order, long expectedVersion);
}
final class PlaceOrderHandler {
    private final OrderRepository orders;
    void handle(PlaceOrder cmd) { orders.add(Order.place(cmd.buyerId())); }
}
```
- 应用依赖领域接口；JPA adapter 负责 mapper、version 和 SQL。
## 05-边界
Q: Repository 最常见的反模式有哪些？
A:
- `GenericRepository<T>` 暴露任意 CRUD/Specification，使聚合边界和业务意图消失。
- 为了避免 join 把整个上下文对象图 eager load，导致 N+1 或巨型事务。
- 领域对象直接调用 repository，隐藏依赖并使模型难测；通常由应用服务协调。
- 报表查询强行还原聚合，应该使用专用投影/read repository。

