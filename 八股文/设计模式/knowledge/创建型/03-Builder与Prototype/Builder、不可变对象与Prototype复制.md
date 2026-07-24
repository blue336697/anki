# Builder、不可变对象与 Prototype 复制
## 01-Builder
Q: Builder 适合解决什么构造问题？
A:
- 参数多、可选项多、构造有步骤且最终对象应不可变时，builder 提供可读命名和集中校验。
- 它把“收集参数”的可变阶段与构建后不可变对象分开，build 时一次验证跨字段不变量。
- 少量必填参数用构造器/静态工厂更简单。
- Builder 不应允许产生缺少必填字段的半成品。
## 02-代码
Q: 一个安全的 Request Builder 怎样在 build 时校验？
A:
```java
final class Request {
    static final class Builder {
        private URI uri; private Duration timeout = Duration.ofSeconds(1);
        Builder uri(URI v){ uri=v; return this; }
        Builder timeout(Duration v){ timeout=v; return this; }
        Request build(){
            Objects.requireNonNull(uri);
            if (timeout.isNegative()) throw new IllegalArgumentException();
            return new Request(uri, timeout);
        }
    }
}
```
- 默认值与校验只存在一处。
## 03-Prototype
Q: Prototype 与普通复制/clone 有什么关系？
A:
- 通过现有对象生成同类变体，适合创建成本高或运行时才知道具体类型。
- Java `Cloneable` 语义薄弱且易浅拷贝，通常用 copy constructor、静态 copy 或不可变 `withX`。
- 不可变对象可安全共享内部值，复制只替换变化部分。
- 有 identity 的实体复制必须生成新 ID 并明确业务语义。
## 04-深浅拷贝
Q: 浅拷贝为什么会造成隐藏共享？
A:
- 浅拷贝只复制字段引用，原对象和副本仍共享可变集合/子对象，一方修改影响另一方。
- 深拷贝递归复制但对象图、循环引用、外部资源和 identity 使其昂贵且含义不清。
- 优先不可变值和防御性复制，避免通用序列化深拷贝。
- 连接、线程、锁等资源不能靠字段复制得到独立语义。
## 05-边界
Q: Builder 与 Prototype 应怎样选择？
A:
- 从业务参数创建新对象、需要校验步骤选 Builder；从模板派生相似配置选 Prototype/copy。
- Builder 可提供 `toBuilder` 组合两者，但仍要重新验证。
- ORM 实体通常不应随意 builder/clone，容易绕过聚合规则和身份。
- 模式价值是明确创建语义，不是生成更多样板代码。
