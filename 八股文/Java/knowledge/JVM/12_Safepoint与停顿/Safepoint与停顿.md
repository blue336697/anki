# Safepoint、Handshake 与 JVM 停顿

## 01-Safepoint目的
Q: JVM 为什么需要 Safepoint？哪些操作会请求它？
A:
- JVM 在某些全局操作中需要所有相关线程处于可枚举、可重建的安全执行状态。
- GC Roots 枚举、去优化、类重定义、部分偏向锁历史操作、线程 dump 等可能涉及 Safepoint。
- 编译器在方法调用、循环回边等位置布置 poll，使线程能在有限时间内响应请求。
- Safepoint 是 VM 协调机制，不等于 GC；一次长停顿也可能由非 GC VM operation 引起。
- 诊断应同时看 `gc` 与 `safepoint` 统一日志。

## 02-到达延迟
Q: 为什么 “Time to safepoint” 可能很长？
A:
- 某线程长时间运行在缺少 poll 的代码、native 调用或内核不可中断状态，可能延迟全局到达。
- 大量线程需要被协调，操作系统调度和 CPU throttle 也会增加墙钟时间。
- JVM 新版本持续改善 counted loop、polling 和线程局部操作，旧版本结论不能直接套用。
- 到达安全点耗时与安全点内实际 VM 操作耗时应分开分析。
- 结合线程栈、safepoint reason、CPU 调度和 native 状态定位阻塞者。

## 03-ThreadLocalHandshake
Q: Thread-Local Handshake 解决什么问题？
A:
- 一些操作只需目标线程到达安全状态，不必让所有 Java 线程一起停顿。
- Handshake 向单个或部分线程下发回调，在其可安全执行的位置完成栈处理等动作。
- 它减少全局 Safepoint 频率和停顿影响，但不能替代需要全局一致性的操作。
- 具体哪些 VM operation 使用 handshake 会随 JDK 版本演进。
- 面试应讲“缩小协调范围”，而不是说“JVM 不再需要 Safepoint”。

## 04-STW与业务延迟
Q: 为什么 STW 20ms 可能造成远大于 20ms 的请求尾延迟？
A:
- 停顿前后请求会排队，恢复时大量线程同时争抢 CPU、连接和锁，形成协调遗漏与拥塞放大。
- 定时任务、超时轮和连接心跳可能集中触发，造成恢复后的 burst。
- 容器 CPU 限额下，恢复阶段清空积压更慢。
- 上下游超时可能在停顿期间同时到期，引发重试风暴。
- 因此要把 Safepoint/GC 事件与队列长度、线程池、重试、CPU 和 p99 时间线关联。

## 05-正确性审查
Q: Safepoint 有哪些常见误区？
A:
- “Safepoint 就是 GC”：错误，很多 VM 操作都可请求 Safepoint。
- “只有正在运行的线程需要响应”：阻塞/native 状态也有各自协调规则。
- “低暂停 GC 不会有 Safepoint”：错误，只是把主要工作并发化。
- “暂停时间等于业务增加的延迟”：不一定，排队和恢复拥塞会放大尾延迟。
- “Handshake 完全替代全局停顿”：错误，它只缩小部分操作的协调范围。
