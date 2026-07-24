# Entity、Value Object 与 Money 实现
## 01-实体
Q: Entity 的身份语义是什么？
A:
- 实体由跨时间稳定的 identity 区分，属性改变后仍是同一个业务对象，如 OrderId 对应订单。
- equality 通常基于同类型 identity，不应把所有可变字段纳入 hashCode 后放进 HashSet。
- ID 可由领域、应用或持久化生成，但未持久化实体的相等规则必须明确。
- 有 ID 不代表对象自动是聚合根，聚合还承担一致性边界。
## 02-值对象
Q: Value Object 为什么应不可变并按值相等？
A:
- 值对象描述一个度量/概念，没有独立生命周期；Money(100,CNY) 可被另一个相同值替换。
- 构造时验证不变量，字段 final，无 setter；运算返回新值，减少共享修改和并发问题。
- equals/hashCode 使用全部语义字段，货币、单位等不能遗漏。
- JPA 等工具要求不应迫使领域公开可变 API，可用转换器/嵌入映射隔离。
## 03-Money规则
Q: Money 值对象应封装哪些规则？
A:
- 使用最小货币单位 long 或精确 decimal，明确 currency、scale 和 rounding，禁止 double。
- 加减必须同币种，负数是否允许由领域场景决定；兑换是独立汇率服务而非 Money 自行猜测。
- 格式化属于展示层，领域对象保存计算语义。
- 防溢出、序列化和数据库精度也属于完整不变量。
## 04-代码示例
Q: 一个最小可用的 Money 值对象怎样实现？
A:
```java
record Money(long cents, String currency) {
    Money {
        if (currency == null || currency.isBlank())
            throw new IllegalArgumentException("currency");
    }
    Money add(Money other) {
        if (!currency.equals(other.currency)) throw new IllegalArgumentException("币种不同");
        return new Money(Math.addExact(cents, other.cents), currency);
    }
}
```
- record 提供不可变与值相等，构造器和行为集中保护规则。
## 05-选择判断
Q: 一个概念该建实体还是值对象？
A:
- 问“属性都一样时是否仍需区分两个实例”“是否要追踪生命周期和历史”；需要则倾向实体。
- 地址在用户地址簿可能有 AddressId，在订单快照中可作为值对象，分类取决于上下文。
- 不要因为数据库有主键就把每张表建实体，ORM 技术身份不等于领域身份。
- 值对象可显著减少 primitive obsession，让方法签名表达单位和规则。

