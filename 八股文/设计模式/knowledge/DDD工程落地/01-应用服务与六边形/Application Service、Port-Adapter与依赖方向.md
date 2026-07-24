# Application Service、Port-Adapter 与依赖方向
## 01-应用服务
Q: Application Service 的标准用例流程是什么？
A:
- 接收 command/DTO，做认证授权与基本格式校验，开启事务并通过 repository 加载聚合。
- 调用领域行为，保存结果、发布由聚合产生的事件，提交后返回 DTO/ID。
- 它描述“先后做什么”，业务规则属于领域对象；方法通常短且一个用例一个入口。
- 不应把 HTTP request、JPA entity 或 MQ SDK 传进领域层。
## 02-六边形
Q: Hexagonal Architecture 的 Port 和 Adapter 是什么？
A:
- 入站 port 定义系统提供的用例，HTTP/消息/CLI adapter 调用它；出站 port 定义核心需要的仓储、支付、时钟。
- MySQL、Redis、第三方支付等 adapter 实现出站接口，依赖方向始终指向应用/领域内核。
- 六边形不是必须画六边，也不等于 controller-service-dao 三层改名。
- 核心可脱离框架测试，替换 adapter 不改业务模型。
## 03-DTO映射
Q: 为什么 API DTO、领域对象和持久化对象不应强行共用？
A:
- API 受客户端兼容与序列化约束，领域对象保护行为与不变量，数据库模型受表结构和 ORM 约束。
- 共用会让 JSON setter、懒加载和列字段污染领域，并让任何层修改都连锁影响。
- mapper 有重复成本，但形成明确防腐边界；简单值可直接映射，不必机械复制所有类型。
- 查询 read model 可直接面向 DTO，命令路径才需加载聚合。
## 04-代码示例
Q: 一个下单应用服务如何只做编排？
A:
```java
final class PlaceOrderService {
    private final OrderRepository orders;
    private final Transaction tx;
    OrderId execute(PlaceOrderCommand c) {
        return tx.required(() -> {
            Order order = Order.place(c.buyerId(), c.lines());
            orders.add(order);
            return order.id();
        });
    }
}
```
- `Order.place` 维护规则，事务与仓储由应用层协调。
## 05-边界
Q: 分层/六边形落地为什么容易过度设计？
A:
- 每个简单 CRUD 都创建 command、handler、port、adapter、mapper 会增加导航成本却没有隔离收益。
- 仅在变化方向、外部依赖或领域复杂度需要时引入边界；同模块包可先保持逻辑分层。
- 依赖规则应由模块/架构测试执行，不能只靠目录名字。
- 渐进式 DDD 比一次重写全系统更安全，可先保护核心子域。

