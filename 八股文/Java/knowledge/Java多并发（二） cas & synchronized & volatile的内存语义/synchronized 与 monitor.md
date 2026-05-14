# synchronized 与 monitor

## 概念卡
Q: synchronized 锁住的对象分别是什么？

A:
- 普通同步实例方法：锁当前实例对象，也就是 `this`。
- 静态同步方法：锁当前类的 `Class` 对象。
- 同步代码块：锁 `synchronized(...)` 括号里的对象。
- 判断关键：必须竞争同一个 monitor，才会互斥。

## 机制卡
Q: synchronized 代码块在 JVM 层面怎么实现？

A:
- 同步代码块通常编译为 `monitorenter` 和 `monitorexit`。
- 线程进入同步块前尝试获得对象关联的 monitor，退出或异常退出时释放 monitor。
- 编译器会生成异常路径，保证已进入的 monitor 能被释放。
- 同步方法不是简单插入这两条指令，而是在方法标志上带 `ACC_SYNCHRONIZED`，由方法调用/返回过程隐式完成 monitor 进入和退出。

## 图示卡
Q: monitor 中 EntryList、WaitSet、Owner 的关系怎么理解？

A:
- EntryList：竞争 monitor 但尚未获得锁的线程。
- Owner：当前持有 monitor 的线程。
- WaitSet：调用 `wait()` 后释放锁并等待通知的线程集合。
- `notify/notifyAll` 只把线程从 WaitSet 移回竞争队列，不等于立刻获得锁。

![monitor waitset entrylist](jc02_monitor_waitset_entrylist.png)

## 边界卡
Q: wait/notify 和 synchronized 的关系是什么？

A:
- `wait()` 必须在持有对象 monitor 时调用，否则会抛出 `IllegalMonitorStateException`。
- 调用 `wait()` 会释放当前 monitor，并进入该 monitor 的 WaitSet。
- 被 `notify/notifyAll` 唤醒后，线程还要重新竞争同一个 monitor，拿到锁后才能继续执行。
- 所以 wait/notify 是 monitor 条件等待机制，不是独立于 synchronized 的线程通信魔法。

## 正确性审查卡
Q: 原文中关于 synchronized 的哪句话要修正？

A:
- “方法同步同样可以使用 monitorenter/monitorexit 实现”容易误导。更准确是：同步代码块使用 `monitorenter/monitorexit`；同步方法由 `ACC_SYNCHRONIZED` 标志表示，JVM 在调用和返回时隐式执行 monitor 进入/退出。
- “任何一个对象都一个 monitor 对象与之关联”应补成“每个对象都可以作为 monitor 锁对象，具体实现由 JVM 管理”。
