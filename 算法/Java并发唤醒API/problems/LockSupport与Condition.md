# LockSupport + Lock/Condition

## LockSupport.park/unpark（最底层原语）
`LockSupport` 是 {{c1::JUC 的底层原语}}，AQS/ReentrantLock 都基于它。**不需要 synchronized，不需要锁！**

```java
// unpark 可以先于 park 调用 — 许可证机制
LockSupport.unpark(t1);   // 给 t1 颁发许可证（最多1张）
LockSupport.park();       // 消费许可证；没有则阻塞

// park 响应中断但不抛异常，需手动检查
LockSupport.park();        // 被 interrupt 后立即返回
Thread.interrupted();      // 清除中断标志
```

核心特性：
- {{c2::unpark 可以先于 park 调用}} — 许可证最多 1 个，累积无效
- {{c3::不需要持有锁}} — 可在任意位置调用
- {{c4::park 不抛 InterruptedException}} — 需手动 Thread.interrupted()

## park/unpark 交替打印
```java
class ParkPrint {
    static Thread t1, t2;
    static int num = 1;

    public static void main(String[] args) {
        t1 = new Thread(() -> {
            while (num <= 100) {
                if (num % 2 == 0) { LockSupport.park(); continue; }
                System.out.println("奇数: " + num++);
                LockSupport.unpark(t2);
            }
        });
        t2 = new Thread(() -> {
            while (num <= 100) {
                if (num % 2 == 1) { LockSupport.park(); continue; }
                System.out.println("偶数: " + num++);
                LockSupport.unpark(t1);
            }
        });
        t1.start(); t2.start();
    }
}
```

## Lock + Condition（比 wait/notify 更灵活）
```java
Lock lock = new ReentrantLock();
Condition cond = lock.newCondition();

lock.lock();
try {
    while (conditionNotMet) cond.await();  // = wait()
    cond.signal();     // = notify()，唤醒一个
    cond.signalAll();  // = notifyAll()
} finally {
    lock.unlock();
}
```

优势：{{c5::一个 Lock 可创建多个 Condition}}，实现精确唤醒。

## 三组 API 对比
| | wait/notify | Condition | park/unpark |
|------|------|------|------|
| 需要锁 | ✅ synchronized | ✅ Lock | ❌ |
| 多条件队列 | ❌ | ✅ | N/A(指定线程) |
| unpark先于park | N/A | N/A | ✅ |
| 精确唤醒 | ❌ | ✅ signal | ✅ unpark(t) |
| 中断异常 | ✅ 抛 | ✅ 抛 | ❌ 需手动检查 |
