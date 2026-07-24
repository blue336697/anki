# StringTable、intern 与字符串去重

> 基线：JDK 21/25 HotSpot；JDK 6/7 差异只作为历史兼容知识。

## 01-三个概念
Q: class 文件常量池、运行时常量池和 StringTable 有什么区别？
A:
- class 文件常量池是 class 二进制中的表，保存字面量、符号引用等静态结构。
- 类加载后对应信息进入运行时常量池，解析时符号引用可转成直接引用。
- StringTable 是 HotSpot 管理 interned String 的全局哈希结构，保存字符串对象引用。
- 字符串对象和其底层字节数组位于 Java heap；JDK 7 起字符串池也不再位于旧 PermGen。
- 三者有关联但不是同一张表，不能都简称“常量池”后混用。

## 02-字面量与拼接
Q: 字面量、编译期常量拼接和运行期拼接分别会产生什么？
A:
- 相同字符串字面量通常解析到 StringTable 中同一个规范引用。
- 只由编译期常量组成的拼接可被 javac 常量折叠，例如 `"a" + "b"` 直接成为 `"ab"`。
- 包含运行期变量的拼接不会按字面量常量折叠；现代 javac 常通过 invokedynamic/StringConcatFactory 生成拼接策略。
- 循环拼接仍应使用 StringBuilder 或合适的批量 API，避免反复构建中间结果。
- 不应死背“`+` 一定翻译成 new StringBuilder”，具体字节码随 JDK 版本演进。

## 03-intern
Q: `String.intern()` 的语义是什么？为什么不能用固定对象数量口诀回答？
A:
- intern 返回与当前字符串内容相等的规范化池引用；池中已有则返回已有引用，否则建立对应条目。
- 是否复用当前堆对象引用、何时解析字面量以及编译器折叠会影响 `==` 实验结果。
- `==` 比较引用身份，业务字符串内容必须用 equals。
- intern 会增加全局池查找和生命周期压力，只适合高重复、稳定且有测量收益的数据。
- 对象数量题高度依赖字节码、加载顺序和 JDK 实现，应画出每一步而不是背答案。

## 04-内部结构
Q: StringTable 为什么是哈希表？碰撞和容量会怎样影响 intern？
A:
- 通过字符串 hash 定位 bucket，再比较内容，平均查找接近 O(1)。
- 高碰撞或装载过高会增加链/桶扫描和 safepoint/维护成本；实现会随 JDK 版本改进。
- `-XX:StringTableSize` 等参数属于实现调优项，不应把旧 JDK 默认值当现代固定常量。
- 可通过 `jcmd VM.stringtable`、JFR/诊断命令查看条目、bucket 和分布，而不是从业务 key 数猜测。
- 外部不可信字符串的大规模 intern 可能形成内存和 CPU 风险。

## 05-StringDeduplication
Q: G1/ZGC 的字符串去重和 intern 有什么不同？
A:
- String Deduplication 由 GC 在候选 String 中寻找内容相同的底层存储，并让多个 String 共享数据。
- 它不要求业务调用 intern，也不让这些 String 引用身份相同；`s1 == s2` 仍可能为 false。
- 去重节省底层数组内存，但需要候选跟踪、哈希和比较 CPU。
- 是否支持和参数名称取决于收集器/JDK；应通过目标运行时文档和日志确认。
- 先测量重复字符串的 retained size，再评估启用收益。

## 06-正确性审查
Q: 字符串池有哪些常见错误说法？
A:
- “所有字符串都在常量池”：错误，普通 new/拼接可产生未 intern 的堆对象。
- “常量池、运行时常量池、StringTable 是一个东西”：错误。
- “JDK 21 拼接一定生成显式 StringBuilder”：错误，常见实现已使用 invokedynamic。
- “intern 能无成本节省内存”：错误，它有全局表、查找和生命周期成本。
- “String Deduplication 等于 intern”：错误，前者共享底层存储而不统一 String 对象身份。
