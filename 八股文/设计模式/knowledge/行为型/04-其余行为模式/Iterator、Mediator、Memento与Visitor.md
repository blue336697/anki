# Iterator、Mediator、Memento 与 Visitor
## 01-Iterator
Q: Iterator 隐藏了什么，fail-fast 又是什么？
A:
- Iterator 暴露顺序访问而隐藏容器表示，客户端无需知道数组、树或分页。
- fail-fast 通过 modification count 尽早发现非预期结构修改，不是并发安全保证。
- snapshot/weakly-consistent iterator 提供不同并发语义和成本。
- 远程分页 iterator 可能每步 IO，接口相同不代表性能相同。
## 02-Mediator
Q: Mediator 何时能减少对象网状依赖？
A:
- 多个组件通过中介协调交互，组件只认识 mediator，适合 UI、工作流和消息路由。
- 中介若承担全部业务会变 God Object，应按用例拆分并让领域规则留在对象。
- Event Bus 是一种松耦合协调，但无类型/顺序治理会更难追踪。
- 简单双向协作直接调用更清晰。
## 03-Memento
Q: Memento 如何在不暴露内部表示时保存快照？
A:
- originator 创建只供自身恢复的状态快照，caretaker 保存但不解释内容。
- 适合编辑器撤销和内存状态；大对象快照可用增量/持久化结构降低空间。
- 数据库备份、Event Sourcing 有更强持久与版本语义，不能简单等同 Memento。
- 快照含敏感数据和旧 schema 时需生命周期治理。
## 04-Visitor代码
Q: Visitor 如何把对稳定对象结构的新操作集中？
A:
```java
sealed interface Expr permits Num, Add { <R> R accept(Visitor<R> v); }
record Num(int value) implements Expr { public <R> R accept(Visitor<R> v){ return v.num(this); } }
record Add(Expr l, Expr r) implements Expr { public <R> R accept(Visitor<R> v){ return v.add(this); } }
interface Visitor<R> { R num(Num n); R add(Add a); }
```
- 新增操作容易，新增元素类型要修改所有 visitor。
## 05-选择边界
Q: 这四种低频模式各自的变化轴是什么？
A:
- Iterator 隔离遍历，Mediator 隔离协作关系，Memento 隔离状态快照，Visitor 隔离稳定类型上的多种操作。
- Visitor 适合 AST 等元素集合稳定场景，业务实体类型频繁变化时维护成本高。
- 现代 Java pattern matching 可替代部分 Visitor，但仍需处理封闭层次。
- 面试应给出问题与代价，不要只背定义。
