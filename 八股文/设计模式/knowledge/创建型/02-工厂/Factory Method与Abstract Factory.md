# Factory Method 与 Abstract Factory
## 01-三种工厂
Q: Simple Factory、Factory Method、Abstract Factory 的变化轴是什么？
A:
- 简单工厂集中 switch 创建，适合类型集合较封闭；它不是 GoF 独立模式但很实用。
- Factory Method 让子类/实现决定创建一种产品，扩展产品类型时增加 creator。
- Abstract Factory 一次创建一族相互兼容产品，如不同云厂商的 Queue/Storage。
- 模式选择取决于创建复杂度和产品族，不要为一个 `new` 建五层接口。
## 02-解耦
Q: 工厂解耦了什么，没有解耦什么？
A:
- 调用方依赖产品接口而非构造细节，工厂集中选择实现、校验参数和组装依赖。
- 调用方仍需决定使用哪个工厂/配置，装配根或 DI 容器承担这个决策。
- 若产品接口泄漏具体类型，工厂只是把 new 挪位置。
- 创建后的业务生命周期不一定由工厂管理。
## 03-代码
Q: 支付渠道工厂怎样避免调用方 switch？
A:
```java
interface Payment { Receipt pay(Money amount); }
interface PaymentFactory { Payment create(); }
final class CardFactory implements PaymentFactory {
    public Payment create() { return new CardPayment(); }
}
final class Checkout {
    Receipt run(PaymentFactory f, Money m) { return f.create().pay(m); }
}
```
- 新渠道新增工厂实现，Checkout 保持稳定。
## 04-抽象工厂
Q: Abstract Factory 如何保证产品族兼容？
A:
- 接口同时暴露一组创建方法，具体工厂返回同一平台/风格的实现，客户端不混搭不兼容对象。
- 新增产品族容易，只新增一个 factory；给所有族新增一种产品会修改所有 factory。
- 若产品维度独立组合，Bridge/DI 注册往往比笛卡尔工厂类更灵活。
- 工厂本身不应包含大量业务流程。
## 05-边界
Q: 工厂模式常见过度设计是什么？
A:
- 每个实现配一个空壳 Factory、FactoryProvider、Manager，调用路径却没有真实变化。
- 用字符串反射创建绕过编译期安全，错误推迟到运行时。
- 把对象池、缓存和 singleton 混进工厂，导致创建语义不可预测。
- 简单构造器或命名静态方法足够时优先它们。

