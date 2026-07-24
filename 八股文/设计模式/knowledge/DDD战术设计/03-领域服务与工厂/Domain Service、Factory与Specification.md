# Domain Service、Factory 与 Specification
## 01-领域服务
Q: 什么逻辑应放 Domain Service？
A:
- 当一个领域操作不自然属于单个实体/值对象，且表达核心业务规则时使用领域服务。
- 它应使用领域语言、通常无状态，参数和返回值是领域对象；外部 IO 通过端口抽象。
- 不能把所有业务都堆进 `XxxDomainService`，能属于实体的行为仍应回到实体。
- 应用编排、事务、鉴权和 DTO 转换不是领域服务职责。
## 02-Factory
Q: Factory 在 DDD 中为什么不只是 new 的包装？
A:
- 创建复杂聚合需一次满足不变量、选择子类型或协调多个值对象时，工厂隐藏构造过程。
- 简单实体可直接命名构造器/静态方法，无需模式仪式。
- 工厂返回完整有效聚合，不能先创建半成品再由调用者按顺序 set。
- 重建持久化对象通常由 Repository/mapper 负责，与业务新建语义分开。
## 03-Specification
Q: Specification 如何表达可组合业务规则？
A:
- 把“候选是否满足规则”封装为对象，可组合 and/or/not，并以领域名字复用。
- 纯内存 specification 可调用实体行为；查询 specification 还需由 repository 翻译为 SQL，能力边界要明确。
- 不能让领域层依赖 ORM Criteria；翻译失败的规则应在内存评估或拆分。
- 规则只用一次且简单时普通方法更清晰，不必模式化。
## 04-代码示例
Q: 跨订单与折扣策略的领域服务怎样保持端口隔离？
A:
```java
interface DiscountPolicy { Money discountFor(BuyerId buyer, Money total); }
final class PricingService {
    Money payable(Order order, DiscountPolicy policy) {
        Money total = order.total();
        return total.subtract(policy.discountFor(order.buyerId(), total));
    }
}
```
- PricingService 表达领域计算，策略端口由基础设施提供；它不开始事务或发送 HTTP。
## 05-对比
Q: Entity 方法、Domain Service 与 Application Service 如何区分？
A:
- 单聚合内部不变量优先实体/根方法；跨对象但仍是领域计算用 Domain Service。
- Application Service 负责用例编排、事务、仓储、权限和消息，不承载可复用核心规则。
- 判断标准是职责与语言，不是类名后缀；贫血模型常把所有规则错误放应用服务。
- 测试中领域服务应可无框架快速运行，应用服务则用端口 mock 验证编排。

