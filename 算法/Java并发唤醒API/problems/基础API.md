# Object.wait/notify + Thread.sleep + join

## wait/notify 核心机制
`wait()` / `notify()` / `notifyAll()` 是 {{c1::Object 类的方法}}，必须在 {{c2::synchronized 块/方法内}} 调用，否则抛出 IllegalMonitorStateException。

```java
synchronized (lock) {
    while (conditionNotMet) {   // 必须用 while，不能用 if！
        lock.wait();             // 释放锁 + 进入等待
    }
    // 执行业务...
    lock.notifyAll();            // 唤醒所有等待线程
}
```

## 为什么用 while 不用 if
{{c1::虚假唤醒（spurious wakeup）}} — 线程可能在没有 notify 的情况下被唤醒。

## wait vs sleep 对比
| | Object.wait() | Thread.sleep() |
|------|------|------|
| 所属类 | Object | Thread |
| 释放锁 | {{c1::释放}} | {{c2::不释放}} |
| 唤醒方式 | notify/notifyAll | 时间到自动醒 / interrupt |
| 调用条件 | 必须在 synchronized 内 | 任意位置 |
| 用途 | 线程间通信协作 | 单纯延时等待 |

## Thread.join() — 等待另一个线程结束
```java
Thread t1 = new Thread(() -> { /* work */ });
t1.start();
t1.join();  // 当前线程阻塞，直到 t1 执行完毕
t1.join(1000); // 最多等1秒
```
底层原理：{{c3::join() 内部调用 wait()，线程结束后 JVM 自动 notifyAll()}}

## 标准 wait/notify 交替打印模板
```java
public class AlternatePrint {
    private final Object lock = new Object();
    private int num = 1;

    public void printOdd() {
        synchronized (lock) {
            while (num <= 100) {
                if (num % 2 == 0) { lock.wait(); continue; }
                System.out.println("奇数: " + num++);
                lock.notify();
            }
        }
    }

    public void printEven() {
        synchronized (lock) {
            while (num <= 100) {
                if (num % 2 == 1) { lock.wait(); continue; }
                System.out.println("偶数: " + num++);
                lock.notify();
            }
        }
    }
}
```
注意：{{c4::print 完要 notify 对方}}，否则对方永远 wait。

## API 速查
| API | 释放锁 | 唤醒方式 | 必须同步 |
|------|:--:|------|:--:|
| `Thread.sleep(ms)` | ❌ | 时间到/interrupt | ❌ |
| `Object.wait()` | ✅ | notify/notifyAll | ✅ synchronized |
| `Thread.join()` | ❌(内部wait) | 线程结束/interrupt | ❌ |
