# Strategy 与 Template Method
## 01-Strategy
Q: Strategy 如何封装可替换算法？
A:
- 定义稳定策略接口，每个实现封装一种规则，context 通过组合委托。
- 可按配置/运行时选择，新增实现不修改流程；适合定价、路由、重试政策。
- 策略输入应是领域数据而非整个 ApplicationContext。
- 算法集合封闭且简单时 switch 可能更清晰。
## 02-Template
Q: Template Method 与 Strategy 的复用方式有何不同？
A:
- Template 在基类固定算法骨架，通过 protected hook 让子类覆写步骤，属于继承复用。
- Strategy 把可变算法变对象组合，运行时可替换且更易独立测试。
- 骨架强稳定、步骤共享多可用 Template；变化维度多优先 Strategy。
- hook 过多会形成脆弱基类。
## 03-代码
Q: 运费策略怎样避免 if-else？
A:
```java
interface ShippingFee { Money calculate(Order o); }
final class ExpressFee implements ShippingFee {
    public Money calculate(Order o){ return o.weightFee().add(new Money(1200,"CNY")); }
}
final class Checkout {
    Money total(Order o, ShippingFee fee){ return o.total().add(fee.calculate(o)); }
}
```
- 策略选择放装配/应用层，领域计算保持显式。
## 04-状态区别
Q: Strategy 与 State 为什么结构相似却意图不同？
A:
- Strategy 由客户端选择算法，通常彼此无状态迁移；State 由 context 当前状态决定行为并发生迁移。
- 策略替换不必记录历史，状态变化是领域生命周期。
- 把状态机写成策略选择会让迁移规则散落外部。
- 讨论模式应说清谁选择、何时变化。
## 05-边界
Q: Strategy/Template 常见滥用是什么？
A:
- 每个两行分支创建类导致导航困难，实际变化集合不会扩展。
- 策略内部访问数据库/全局状态，失去纯规则可测试性。
- Template 子类依赖调用顺序和基类字段，修改基类破坏全部实现。
- 先识别真实变化轴再抽象。

