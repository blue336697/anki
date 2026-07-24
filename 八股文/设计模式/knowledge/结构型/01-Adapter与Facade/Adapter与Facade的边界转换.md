# Adapter 与 Facade 的边界转换
## 01-Adapter
Q: Adapter 的核心意图是什么？
A:
- 把已有接口转换为客户端需要的目标接口，复用不兼容实现；对象适配器通常用组合。
- 它转换调用和数据格式，不应悄悄改变关键业务语义。
- 常用于第三方 SDK、遗留系统和六边形架构出站 adapter。
- 若能直接修改双方且只有一次调用，额外适配层未必必要。
## 02-Facade
Q: Facade 与 Adapter 有何区别？
A:
- Facade 为复杂子系统提供更简单、面向用例的入口，底层接口本来可能兼容但太复杂。
- Adapter 解决接口不匹配；Facade 简化协作并隐藏调用顺序。
- Facade 不应成为拥有所有业务的 God Service，核心规则仍在领域对象。
- 客户端可在必要时使用底层高级接口，取决于封装策略。
## 03-代码
Q: 如何把第三方短信 SDK 适配为通知端口？
A:
```java
interface Notifier { void send(Phone phone, String text); }
final class SmsAdapter implements Notifier {
    private final VendorSms sdk;
    public void send(Phone p, String text) {
        sdk.push(p.countryCode(), p.number(), text);
    }
}
```
- 核心只依赖 Notifier，vendor DTO/错误在 adapter 内转换。
## 04-类适配对比
Q: 组合适配为什么通常优于继承适配？
A:
- 组合可适配 final 类、多个实现并在运行时替换，也不暴露被适配者全部 API。
- 继承适配受单继承和基类耦合限制，但需要覆写 protected hook 时可能合适。
- 默认优先对象适配，保持依赖显式。
- 适配层应有契约测试验证异常、超时和字段语义。
## 05-误区
Q: Adapter/Facade 最常见的问题是什么？
A:
- 只做字段搬运却让第三方状态码渗入领域，未真正防腐。
- Facade 方法参数仍要求客户端理解全部子系统，接口并未简化。
- 双向 adapter 造成循环依赖和模型模糊，应明确上下游。
- 不要把所有 `XxxUtil` 都称 Facade。

