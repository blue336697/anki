# Record、Sealed Class 与模式匹配

> 基线：JDK 21/25 正式语言能力。

## 01-Record语义
Q: record 编译后提供什么？它适合和不适合哪些模型？
A:
- record 声明一组组件，并自动形成私有 final 字段、访问器、规范构造器以及基于组件的 equals/hashCode/toString。
- 它表达“透明数据载体”，适合 DTO、值对象、消息和模式匹配输入。
- record 类隐式 final，不能继承普通类，但可实现接口；组件引用的对象仍可能可变。
- ORM 实体常依赖无参构造、代理和可变生命周期，不应仅为减少样板代码强行改成 record。
- 需要校验时可写 compact constructor，但应避免在构造期间泄漏 `this`。

## 02-Sealed层次
Q: sealed class/interface 解决什么问题？`permits` 的边界是什么？
A:
- sealed 类型限制直接子类型集合，让领域状态和代数数据类型更封闭、可枚举。
- 直接子类型必须声明为 final、sealed 或 non-sealed，明确后续扩展策略。
- 允许的直接子类型需满足同模块或特定包等编译规则；它是语言/模块约束，不是运行时鉴权机制。
- 封闭层次配合 switch 穷尽性检查，可以减少遗漏状态分支。
- 对需要第三方自由扩展的 SPI，sealed 往往不合适。

## 03-switch模式匹配
Q: JDK 21 的 switch 模式匹配怎样选择分支？顺序为什么重要？
A:
- case 可按类型模式匹配并绑定变量，也可处理 `null` 和使用 `when` guard。
- 更具体或受 guard 限制的分支应放在能覆盖它的宽泛类型之前，否则会被编译器判定支配。
- 对 sealed 层次和 enum，编译器可检查穷尽性；类型演进后仍需考虑二进制兼容与 MatchException。
- 模式 switch 减少 `instanceof + cast` 样板，但复杂业务规则不应全部塞入巨大 switch。
- 它在 JDK 17 只是 preview，JDK 21 才正式。

## 04-Record Pattern
Q: Record Pattern 与普通类型模式有什么区别？
A:
- 类型模式只验证类型并绑定整个对象；record pattern 还能按组件结构解构。
- 模式可嵌套，用编译期类型检查表达层次化数据读取，减少手工 accessor 调用。
- 解构调用 record accessor；访问器异常会使匹配过程异常完成。
- 嵌套模式提高表达力，也可能让分支难读；复杂转换仍应抽取方法。
- 只对 record 的透明组件建模有效，不是任意对象字段反射解构。

## 05-正确性审查
Q: 现代 Java 数据建模有哪些误区？
A:
- “record 就是 Lombok `@Data`”：错误，record 有语言级组件、final 类和特定相等语义。
- “record 完全不可变”：错误，组件引用的对象可能可变。
- “sealed 后所有子孙类型都固定”：错误，non-sealed 分支可重新开放。
- “switch pattern JDK 17 正式”：错误，JDK 17 是首轮预览。
- “模式匹配替代多态”：不绝对；开放扩展更适合多态，封闭数据变体常适合模式匹配。
