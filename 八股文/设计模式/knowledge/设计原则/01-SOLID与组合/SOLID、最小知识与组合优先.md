# SOLID、最小知识与组合优先
## 01-SRP
Q: 单一职责的“职责”怎样判断？
A:
- 职责是同一类变化原因/利益相关者，而不是“类只能有一个方法”；一起变化的规则应聚合。
- Controller 同时校验业务、SQL、发消息会因多种原因修改，测试与复用困难。
- 过度拆成大量一行类也会增加导航，边界应围绕变化和内聚。
- 用提交历史和业务角色验证，而不是数代码行。
## 02-OCP
Q: 开闭原则如何避免每次新增规则修改巨大 if/else？
A:
- 把稳定流程与可变策略分开，通过接口/组合注册新实现；不是要求任何代码永不修改。
- 只对已识别的变化轴抽象，提前为所有可能性设计会制造复杂度。
- switch 对封闭枚举可能最清晰，插件式策略适合持续新增。
- 测试应固定稳定契约，扩展实现共享 contract test。
## 03-LSPISP
Q: LSP 与接口隔离如何约束继承和接口？
A:
- 子类型必须保持父类型前置条件不加强、后置条件不削弱和不变量，调用方无需识别具体类型。
- 正方形继承可变矩形常破坏宽高独立设置，说明分类“是一个”不等于行为可替换。
- ISP 让客户端只依赖所需小能力，避免实现抛 UnsupportedOperationException。
- 小接口按角色拆分，不等于每个方法一个接口。
## 04-DIP代码
Q: 依赖倒置如何让业务不依赖具体支付 SDK？
A:
```java
interface PaymentPort { Receipt charge(OrderId id, Money amount); }
final class PayOrder {
    private final PaymentPort payments;
    PayOrder(PaymentPort payments) { this.payments = payments; }
    Receipt execute(Order o) { return payments.charge(o.id(), o.total()); }
}
```
- 高层定义所需端口，基础设施 adapter 实现；依赖注入只是装配手段。
## 05-组合优先
Q: 为什么“组合优于继承”不是禁止继承？
A:
- 组合可运行时替换行为、避免脆弱基类和状态耦合；策略、装饰器大量使用它。
- 继承适合稳定的真正可替换类型层次与模板骨架，仍需遵守 LSP。
- 迪米特法则要求对象只与直接协作者通信，减少深链 `a.getB().getC()` 对结构的依赖。
- 原则用于解释权衡，冲突时以业务清晰度和变化成本决定。

