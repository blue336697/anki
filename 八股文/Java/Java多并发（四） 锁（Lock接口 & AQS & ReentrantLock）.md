# Java多并发（四）| 锁（Lock接口 & AQS & ReentrantLock）

type: Post
status: Published
date: 2022/07/09
summary: Lock接口与synchronized的对比
tags: Java
category: 技术栈

# Lock

[美团技术团队的文章，建议阅览](https://tech.meituan.com/2018/11/15/java-lock.html)

## 1.Lock接口与synchronized的对比

### 1.1 概述

> 锁是用来控制多个线程访问共享资源的方式，一般来说，一个锁能够防止多个线程同时 访问共享资源（但是有些锁可以允许多个线程并发的访问共享资源，比如读写锁）。**在Lock接 口出现之前，Java程序是靠synchronized关键字实现锁功能的，而Java SE 5之后，并发包中新增 了Lock接口（以及相关实现类）用来实现锁功能，它提供了与synchronized关键字类似的同步功 能，只是在使用时需要显式地获取和释放锁**。虽然它缺少了（通过synchronized块或者方法所提 供的）隐式获取释放锁的便捷性，但是却拥有了锁获取与释放的可操作性、可中断的获取锁以 及超时获取锁等多种synchronized关键字所不具备的同步特性。
> 

> 使用synchronized关键字将会隐式地获取锁，但是它将锁的获取和释放固化了，也就是先 获取再释放。当然，这种方式简化了同步的管理，可是扩展性没有显示的锁获取和释放来的 好。例如，针对一个场景，手把手进行锁获取和释放，先获得锁A，然后再获取锁B，当锁B获得 后，释放锁A同时获取锁C，当锁C获得后，再释放B同时获取锁D，以此类推。这种场景下， synchronized关键字就不那么容易实现了，而使用Lock却容易许多。
> 

```java
Lock lock = new ReentrantLock();
lock.lock();
try {
} finally {
 lock.unlock();
 }
```

> **注意上述代码在finally释放锁是保证获取锁以后能够释放资源；而不将获取锁写在try中是因为如果再过去锁之后发生异常异常抛出会导致锁无故释放**
> 

### 1.2 Lock接口提供的synchronized关键字不具备的主要特性

- 概述

> synchronized的同步是jvm底层实现的，对一般程序员来说程序遇到出乎意料的行为的时候，除了查官方文档几乎没有别的办法；而显示锁除了个别操作用了底层的Unsafe类(LockSupport封装了Unsafe类)之外，几乎都是用java语言实现的，我们可以通过学习显示锁的源码，来更加得心应手的使用显示锁。
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image.png)

- Lock相对于synchronized的缺点

> • 使用比较复杂，这点之前提到了，需要手动加锁，解锁，而且还必须保证在异常状态下也要能够解锁。而synchronized的使用就简单多了。
• 效率较低，synchronized关键字毕竟是jvm底层实现的，因此用了很多优化措施来优化速度(偏向锁、轻量锁等)，而显示锁的效率相对低一些。
> 

### 1.3 Lock接口的相关API

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%201.png)

## 2.队列同步器（AQS）同步状态不是锁

- 概述

> 队列同步器`AbstractQueuedSynchronizer`（以下简称同步器），是用来构建锁或者其他同步组 件的基础框架，它使用了一个int成员变量表示同步状态，通过内置的FIFO队列来完成资源获 取线程的排队工作，它的主要工作方式是继承，官方推荐子类被定义为自定义同步组件的静态内部类；像什么`reentrantlock、countdownlatch`都是同步组件
> 
- 资源共享方式

> Exclusive（独占，只有一个线程能执行，如ReentrantLock）和Share（共享，多个线程可同时执行，如Semaphore/CountDownLatch）。
> 

### 2.1 AQS的相关重写方法和通用模板方法

- 概述

> 重写同步器指定的方法时，需要使用同步器提供的如下3个方法来访问或修改同步状态。
> 
> - getState()：获取当前同步状态。
> - setState(int newState)：设置当前同步状态。
> - compareAndSetState(int expect,int update)：使用CAS设置当前状态，该方法能够保证状态 设置的原子性。
- 可重写方法

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%202.png)

- 模板方法

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%203.png)

### 2.2 AQS的实现分析

### 1. 同步队列

- 概述

> **同步队列是一个FIFP的双向队列，当前线程获取同步状态失败时，同步器会将当前线程以及等待状态等信息构造成一个节点（Node），并加入到同步队列的队尾，同时将当前线程阻塞，当同步状态被释放会将队头节点中的线程唤醒，再次尝试获取同步状态，等获取到就会将自己设置成头节点，这个过程必须是线程安全的**
> 
- 注意

> 设置尾结点的方法为compareAndSetTail(Node expect,Node update)，而**设置头节点的方法不必是线程安全的，该next的指向就好，注意在这里说的头节点和尾节点都是同步器里面的两个节点**
> 
- 图示基本结构

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%204.png)

- 节点的属性类型与名称及描述

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%205.png)

### 2. 独占式同步状态获取与释放

- 同步器的acquire方法即获取

> **此方法就是的代码部分一共做了同步状态获取（tryAcquire来获取同步状态，失败后才有加下来的步骤）、节点构造、加入同步队列以及在同步队列自旋即被阻塞，只有当前驱节点的出队或阻塞线程被中断阻塞线程才被唤醒**
> 

```java
public final void acquire(int arg) {
        if (!tryAcquire(arg) &&
            acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
            selfInterrupt();
       }
```

- acquire方法引申出的addWaiter方法和enq方法

> 前者将节点加入尾部，后者确保能成功添加到尾部（以死循环自旋的方式一直尝试），两者都是用CAS来确保节点安全添加
> 

```java
private Node addWaiter(Node mode) {
        Node node = new Node(Thread.currentThread(), mode);
        // Try the fast path of enq; backup to full enq on failure
        Node pred = tail;
        if (pred != null) {
            node.prev = pred;
            if (compareAndSetTail(pred, node)) {
                pred.next = node;
                return node;
            }
        }
        enq(node);
        return node;
    }

private Node enq(final Node node) {
        for (;;) {
            Node t = tail;
            if (t == null) { // Must initialize
                if (compareAndSetHead(new Node()))
                    tail = head;
            } else {
                node.prev = t;
                if (compareAndSetTail(t, node)) {
                    t.next = node;
                    return t;
                }
            }
        }
    }
```

- acquire方法引申出的acquireQueued方法

> **当节点成功接入队列后就进入了一个自旋状态，每个节点都在自我观察当满足条件获取到同步状态就会从这个自旋过程中退出，注意哦自旋节点的过程对应线程也在阻塞哦**
> 

> 前面说过只有前驱节点是头节点才能够尝试获取同步状态这是因为：注意这个头节点不是同步器的head
> 
> 1. 头节点是成功获取到同步状态的节点，而头节点的线程释放了同步状态之后，将会 唤醒其后继节点，后继节点的线程被唤醒后需要检查自己的前驱节点是否是头节点。
> 2. 维护同步队列的FIFO原则
> 
> ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%206.png)
> 
- 同步器的acquire方法调用流程图

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%207.png)

- 同步器的release方法即释放

> 当该节点获得了同步状态，也就证明对共享资源有了修改权即拿到了锁，那么拿到同步状态完成相应逻辑代码就要考虑释放同步状态了，直接看代码；代码显示当执行该方法时会唤醒头节点的后继节点（在提醒一下这个头节点不是同步器的head），unparkSuccessor(h)来完成这一任务，当然这个方法底层还能继续剖析后面会有详解
> 

```java
public final boolean release(int arg) {
        if (tryRelease(arg)) {
            Node h = head;
            if (h != null && h.waitStatus != 0)
                unparkSuccessor(h);
            return true;
        }
        return false;
    }
```

### 3. 共享式同步状态的获取和释放

- 概述

> 与独占式的区别就是在同一时刻共享状态能否被多个线程获取到，对于读写文件来说，写时就是独占式，而读则可以是共享式
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%208.png)

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%209.png)

- 调用acquireShared方法可以共享式的获取同步状态

> 在该方法中同步器调用tryAcquireShared来尝试获取同步状态，在自旋过程中如果此方法返回大于等于0就说明成功获取到同步状态，并调用doAcquireShared来执行这一自旋获取的过程
> 
- 调用releaseShared方法可以共享式的释放同步状态

> 同样释放时会唤起后续处于等待的节点，但是与独占式的区别就是在释放方法doReleaseShared中必须要保证线程安全（通过循环或CAS），会因为是在多线程的情况下
> 

### 4. 独占式超时获取同步状态

- 概述

> 调用同步器的`doAcquireNanos(int arg, long nanosTimeout)`可以超时获取同步状态，获取成功返回true；在Java5之前中断一个被阻塞线程，线程中断标志位会被修改但依然在阻塞；而Java5之后在等待获取同步状态时被中断会立刻返回抛出异常，**而这个超时则是这个过程的增强版**，在支持响应中断的同时支持超时获取；参数nanosTimeout的计算公式是`nanosTimeout -= now-lastTime`，大于0则表明超时时间未到，反之亦然。
> 
- doAcquireNanos方法

> 在获取同步状态的过程与独占式的获取相同，但在获取失败的时候处理有所不同，当获取失败则会去检查是否超时，若没有超时则重新计算`nanosTimeout`，然后等待相应`nanosTimeout`的纳秒时间后从parkNanos方法返回；从方法上来看当满足`nanosTimeout<=spinForTimeoutThreshold（1000纳秒）`这时虽然超时时间大于零但不会进入超时等待而是直接快速进入自旋过程来等待同步状态，避免不精准
> 
- 代码如下

> 在jdk6中又加一层封装来处理当前线程的后续行为
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2010.png)

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2011.png)

### 5. 总结

> AQS可以理解为使用lock这种锁时提供的统一化框架结构，里面的锁分为独占式和共享式，那你需要自己实现一些功能时，你要自定义这个同步器，并且要实现一些拓展功能，可以自定义同步组件，而自定义同步器往往以同步组件内部类的形式出现
> 

## 3.Java中的各种锁

### 3.1 重入锁（ReentrantLock）

- 概述

> 顾名思义，就是支持重进入的锁，他表示该锁能够支持一个线程对资源的重复加锁，除此之外，该锁还支持获取锁时的公平或非公平性选择；当没有考虑重入性时如果调用两次lock方法就会出现自己卡自己的情况；默认实现为非公平锁
> 
- 与synchronized对比，即都支持可重入

> `synchronized`关键字是支持隐性的重进入，你可以重复递归一段试试。`ReentrantLock`虽然没能像`synchronized`关键字一样支持隐式的重进入，但是在调用lock()方 法时，已经获取到锁的线程，能够再次调用lock()方法获取锁而不被阻塞。
> 
- 注意

> **对于重入锁和不可重入锁你可以发现很强调当前线程的是否拥有了锁，那么可以推断出来可重入和不可重入都是独占锁，也就是写锁，当线程获取不到锁那么直接会失败**
> 

### 1. 实现可重入

实现可重入需要解决以下两个问题：

1. 线程再次获取锁：锁要去识别占据锁的线程是否为当前再次请求获取锁的线程，如果是则再次成功获取
2. 锁的最终释放：线程重复获取了n次锁，那么同样要释放n次锁，其他线程能够成功获取，**锁的最终释放要求锁对于获取进行计数自增，计数表示当前锁被重复获取的次数，而锁 被释放时，计数自减，当计数等于0时表示锁已经成功释放。**
- 获取与释放

> **ReentrantLock的获取（以非公平锁为例）nonfairTryAcquire和释放tryRelease方法，两个方法都对于state进行加或减的操作；对于释放操作而言当进行到第n此操作，必须前面的（n-1）次返回都是false同时同步状态完全释放了才能返回true（方法中就是state为0时就返回true）**
> 

```java
final boolean nonfairTryAcquire(int acquires) {
            final Thread current = Thread.currentThread();
            int c = getState();
            if (c == 0) {
                if (compareAndSetState(0, acquires)) {
                    setExclusiveOwnerThread(current);
                    return true;
                }
            }
            //这个就是锁来判断当前线程是否是重复获取
            else if (current == getExclusiveOwnerThread()) {
            	//更新状态
                int nextc = c + acquires;
                if (nextc < 0) // overflow
                    throw new Error("Maximum lock count exceeded");
                setState(nextc);
                return true;
            }
            return false;
        }

protected final boolean tryRelease(int releases) {
			//释放也要更新状态啊
            int c = getState() - releases;
            if (Thread.currentThread() != getExclusiveOwnerThread())
                throw new IllegalMonitorStateException();
            boolean free = false;
            if (c == 0) {
                free = true;
                setExclusiveOwnerThread(null);
            }
            setState(c);
            return free;
        }
```

### 2. 公平锁与非公平锁

- 概述

> **如果在绝对时间上，先对锁进行获取的请求一定先 被满足，那么这个锁是公平的，反之，是不公平的。公平的获取锁，也就是等待时间最长的线 程最优先获取锁，也可以说锁获取是顺序的。也就是FIFO。ReentrantLock提供了一个构造函数，能够控制锁 是否是公平的。事实上，公平的锁机制往往没有非公平的效率高，但是，并不是任何场景都是以TPS作为 唯一的指标，公平锁能够减少“饥饿”发生的概率，等待越久的请求越是能够得到优先满足。**
> 
- 流程

> • 与公平锁相比非公平锁上来就尝试CAS修改资源尝试插队，修改成功，将持有锁线程修改为当前线程，然后成功就直接返回true并修改状态量了
• 失败则去尝试获取锁，先获取当前线程的状态量，如果状态量为0，就代表当前线程没有持有锁，尝试将状态值改为1，成功则直接更新状态量然后修改获取锁线程为当前线程返回true，同样这里是直接进行插队判断CAS的
• 如果状态量不为0，说明已有其他线程持有该锁，那么就需要判断当前线程跟持有锁的线程是否一致（可重入性），一致则更新状态量返回true
• 如果状态量小于0则表示重入次数过多，都超过int的最大值了
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2012.png)

- 代码分析

> 这里我们分析公平锁，非公平锁在上面。对于公平锁的获取方法多了一个`!hasQueuedPredecessors()`这个判断，即当前加入同步队列的节点是否有前驱节点的判断，如果true就表明有其他线程比当前线程更早的请求锁，那么需要等前驱节点释放以后再能获取哦
> 
- 总结

> 我们可以写一个测试用例来看非公平锁和公平锁区别，从实例中可以看到非公平锁出现线程连续获取锁的情况，其实很好理解为什么会这样，当释放完成由于是不公平的，刚释放完的线程自然比在队列的快，具有天然优势；从这可以看出非公平会造成线程饥饿的现象，
> 
> 
> **可是默认又设定的是非公平，这是因为非公平下线程切换少，虽然造成饥饿但是保证了其吞吐量；而公平虽然保证了线程获取锁的FIFO，但是有极其严重的代价就是大量的线程切换**
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2013.png)

- 注意

> 在非公平锁的挣抢中，刚来的线程如果正好碰到了锁是空闲的，并且成功抢到了锁，那么对于等待队列的线程都是非公平的，但如果没有成功抢到锁同样是需要去等待队列排队的，此时对于CPU来说需要唤醒的线程数+1。**即先尝试插队，失败在排队**
> 

> 在底层例如Reentrantlock，公平与非公平的区别就是在公平锁中多一个对于线程是否是同步队列的第一个，你排队来的都不在队列中咋可能在第一个呢
> 

### 3.2 读写锁（ReetrantReadWriteLock）

- 概述

> 之前提到过的锁基本都是排他锁，这些锁在同一时刻只允许一个线程访问。而读写锁在同一时刻可以允许多个读线程访问，但是在写线程访问时，所有的读 线程和其他写线程均被阻塞。读写锁维护了一对锁，一个读锁和一个写锁，通过分离读锁和写 锁，使得并发性相比一般的排他锁有了很大提升。
> 
- 应用场景

> **除了保证写操作对读操作的可见性以及并发性的提升之外，读写锁能够简化读写交互场 景的编程方式。假设在程序中定义一个共享的用作缓存数据结构，它大部分时间提供读服务 （例如查询和搜索），而写操作占有的时间很少，但是写操作完成之后的更新需要对后续的读 服务可见。**
> 
- 与以前jdk5之前方式的对比

> 在没有读写锁支持的（Java 5之前）时候，如果需要完成上述工作就要使用Java的等待通知 机制，就是当写操作开始时，所有晚于写操作的读操作均会进入等待状态，只有写操作完成并 进行通知之后，所有等待的读操作才能继续执行（写操作之间依靠synchronized关键进行同 步），这样做的目的是使读操作能读取到正确的数据，不会出现脏读。改用读写锁实现上述功 能，只需要在读操作时获取读锁，写操作时获取写锁即可。当写锁被获取到时，后续（非当前写 操作线程）的读写操作都会被阻塞，写锁释放之后，所有操作继续执行，编程方式相对于使用 等待通知机制的实现方式而言，变得简单明了。
> 
- 读写锁的特性

> 一般情况下，读写锁的性能都会比排它锁好，
> 
> 
> **因为大多数场景读是多于写的。在读多于写 的情况下，读写锁能够提供比排它锁更好的并发性和吞吐量**
> 
> ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2014.png)
> 

### 1. 读写锁的接口与示例

- 概述

> ReadWriteLock仅仅定义了获取读锁和写锁两个方法，即readLock方法和writeLock方法，但该接口的实现ReentrantReadWriteLock除了接口方法还提供了一些便于监控内部工作状态的方法如下图：
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2015.png)

### 2. 读写状态的设计

- 概述

> 读写锁你依赖于同步器来实现同步功能的，那么读写状态就是其同步状态，回想自定义器同步器我们使用一个int型来表示锁被一个线程重复获取的次数，那么读写锁如何在同步状态（一个整型变量）上维护多个读线程和一个写线程呢；
> 
- 按位切割使用

> 如果在一个整型变量上维护多种状态，就一定需要按位切割使用这个变量，读写锁将这个状态分割为两个部分，高16位表示读，低16位表示写如下图
> 
- 图示

> 如图表示当前同步状态表示一个线程获取了读锁，且重进入了两次，同时也连续获取了两次读锁；通过**位运算**就可以迅速确定读和写各自的状态
> 
> - 例如当同步状态为S，写状态就等于`S & 0x0000FFFF（将高16位全部抹去）`，读状态就等于`S>>>16（无符号补0右移 16位）`
> - 当写状态增加1时，等于`S+1`，当读状态增加1时，等于`S+(1<<16)，也就是 S + 0x00010000`。
> 
> ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2016.png)
> 
- 总结

> S不等于0时，当写状态`（S&0x0000FFFF）`等于0时，则读 状态`（S>>>16）`大于0，即读锁已被获取。代码处体现更为明显
> 

### 3. 写锁的获取与释放

- 概述

> 写锁是支持重入的排它锁，如果当前线程已经获取了写锁，则增加写状态；如果当前线程获取写锁时，已经有线程占用即读状态不为0或者该线程即这个获取到读锁的线程不是获取写锁的线程那就会进入等待状态
> 
- 分析获取代码

> 在源码中除了重入条件以外，增加了一个读锁是否存在，如果存在读锁将不能被获取，这是因为写锁操作要对读锁具有可见性，如果允许这个情况的发生，读锁根本无法感知写锁进行操作，造成同步问题，所以直接禁止；同理当写锁存在时任何读锁将被阻塞
> 

```java
protected final boolean tryAcquire(int acquires) {
			1. 如果读取计数非零或写入计数非零且所有者是不同的线程，则失败。
			2. 如果计数饱和，则失败。 （只有在 count 已经非零时才会发生这种情况。）
			3. 否则，如果该线程是可重入获取或队列策略允许，则该线程有资格获得锁定。
			如果是这样，请更新状态并设置所有者。
            Thread current = Thread.currentThread();
            int c = getState();
            int w = exclusiveCount(c);//获取写状态
            if (c != 0) {
                // (Note: if c != 0 and w == 0 then shared count != 0)
                //下面这句就印证了读状态和写状态相互的推论
                //写状态为空也就是说明此时在读
                if (w == 0 || current != getExclusiveOwnerThread())
                    return false;
                if (w + exclusiveCount(acquires) > MAX_COUNT)
                    throw new Error("Maximum lock count exceeded");
                // Reentrant acquire
                setState(c + acquires);
                return true;
            }
            if (writerShouldBlock() ||
                !compareAndSetState(c, c + acquires))
                return false;
            setExclusiveOwnerThread(current);
            return true;
        }
```

- 分析释放

> 释放与重入锁的释放类似，都是一层一层状态对应，当写状态为0就证明写锁被释放了，方便后面读写锁获取
> 

### 4. 读锁的获取与释放

- 概述

> 根据读的需求可以得知这个锁肯定是共享式锁，能够被多个线程同时获取并且可重入，在没有其他写线程访问或者写状态为0，读锁总会被成功的获取，所以只需要在更新状态的时候要求线程安全，如果获取读锁的是当前线程则增加读状态，如果当前线程在获取读锁时，写锁已经被其他线程占用则等待
> 
- JDK5到JDK6的变化

> 获取读锁的实现从Java 5到Java 6变得复杂许多，主要原因是新增了一 些功能，例如getReadHoldCount()方法，作用是返回当前线程获取读锁的次数。读状态是所有线 程获取读锁次数的总和，而每个线程各自获取读锁的次数只能选择保存在ThreadLocal中，由 线程自身维护，这使获取读锁的实现变得复杂。
> 
- 代码分析

> 在tryAcquireShared(int unused)方法中，如果其他线程已经获取了写锁，则当前线程获取读 锁失败，进入等待状态。如果当前线程获取了写锁或者写锁未被获取，则当前线程（线程安全， 依靠CAS保证）增加读状态，成功获取读锁。
> 

```java
Thread current = Thread.currentThread();
            int c = getState();
            if (exclusiveCount(c) != 0 &&
                getExclusiveOwnerThread() != current)
                return -1;
            if (!readerShouldBlock() &&
           r < MAX_COUNT &&
           compareAndSetState(c, c + SHARED_UNIT)) {
           ....
           return 1;}
           //读状态的获取上限到了
           return fullTryAcquireShared(current);
```

- 释放锁

> 读锁的每次释放（线程安全的，可能有多个读线程同时释放读锁）均减少读状态，减少的 值是`（1<<16）`。
> 

### 5. 锁降级

- 概述

> 锁降级就是写锁降级称为读锁。**如果当前线程拥有写锁，然后将其释放，最后再获取读 锁，这种分段完成的过程不能称之为锁降级。锁降级是指把持住（当前拥有的）写锁，再获取到 读锁，随后释放（先前拥有的）写锁的过程。**
> 
- 代码过程

```java
//必须先释放读锁，要不然写锁会被堵塞
readLock.unlock();
//锁降级从写锁的获取开始
writeLock.lock();
//获取读锁，注意此时是在当前线程获取了写锁的情况下获取读锁是可以的，
//别的线程获取就不行会被堵塞保证可见性
readLock.lock();
//释放写锁，完成锁降级
writeLock.unlock();
```

- 代码分析

> **我们前面说过在获取读锁时，如果别人的线程获取到了写锁，当前读锁的获取是会被阻塞的，那么我们在看锁降级中获取完写锁后再去获取读锁就是必不可少的了，如果没有这个读锁的获取，直接释放写锁，那此时另一个线程获取到了写锁进行了修改，那么当前线程是无法感受到数据的更新的，那么在获取写锁的同时，当前线程获取读锁就很理所当然了**
> 
- 为什么不存在锁升级

> **读锁升级写锁？你自己把上面的顺序调换一下就知道为什么不行了，如果在这个过程中有很多个线程获取到了读锁，在此时某个线程获取到写锁因为要进行锁升级，进行了数据修改别的线程是感受不到的**
> 

## 4. LockSuppert工具

- 概述

> 当需要阻塞或唤醒一个线程的时候，都会使用LockSupport工具类来完成相应 工作。LockSupport定义了一组的公共静态方法，这些方法提供了最基本的线程阻塞和唤醒功 能，而LockSupport也成为构建同步组件的基础工具。
> 
- LockSupport提供的阻塞和唤醒方法

> **在Java 6中，LockSupport增加了park(Object blocker)、parkNanos(Object blocker,long nanos) 和parkUntil(Object blocker,long deadline)3个方法，用于实现阻塞当前线程的功能，其中参数 blocker是用来标识当前线程在等待的对象（以下称为阻塞对象），该对象主要用于问题排查和 系统监控。**
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2017.png)

### 4.1 park方法详解

- 概述

> park这个方法会阻塞当前线程，只有以下4种情况中的一种发生时，该方法才会返回。
> 
> - 与park对应的unpark执行或已经执行时。“已经执行”是指unpark先执行，然后再执行park的情况。
> - 线程被中断时。
> - 等待完time参数指定的毫秒数时。
> - 异常现象发生时，这个异常现象没有任何原因。

```java
public static void park(Object blocker) {
        Thread t = Thread.currentThread();
        setBlocker(t, blocker);
        UNSAFE.park(false, 0L);
        setBlocker(t, null);
    }
//UNSAFE.park是一个本地方法
public native void park(boolean isAbsolute, long time);
```

- JVM中的显示

> 继续看一下JVM是如何实现park方法：park在不同的操作系统中使用不同的方式实现，在 Linux下使用的是系统方法pthread_cond_wait实现。在window是WaitForSingleObject实现的
> 

> 当线程被阻塞队列阻塞时，线程会进入WAITING（parking）状态。我们可以使用jstack dump 阻塞的生产者线程看到这点，如下。
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2018.png)

## 5. Condition接口（底层的阻塞和唤醒都有lockSupport提供的）

- 概述

> 任意一个Java对象，都拥有一组监视器方法（定义在java.lang.Object上），主要包括wait()、 wait(long timeout)、notify()以及notifyAll()方法，这些方法与synchronized同步关键字配合，可以 实现等待/通知模式。Condition接口也提供了类似Object的监视器方法，与Lock配合可以实现等 待/通知模式，但是这两者在使用方式以及功能特性上还是有差别的。
> 
- object的监视器方法和condition接口的对比

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2019.png)

- condition接口的部分方法

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2020.png)

- 有界队列

> 当队列为空想要获取元素的线程将会被阻塞，知道队列中有元素；当队列满时，线程的插入操作也会被阻塞直到队列出现空位。
> 

```java
public class BoundedQueue<T> {
    private Object[] items;
    //添加下标，删除和下标和数组当前数量
    private int addIndex, removeIndex, count;
    private Lock lock = new ReentrantLock();
    private Condition notEmpty = lock.newCondition();
    private Condition notFull = lock.newCondition();

    public BoundedQueue(int size) {
        items = new Object[size];
    }

    //添加一个元素，如果数组满，则添加线程进入等待状态，直到有空位
    public void add(T t) throws InterruptedException{
        lock.lock();
        try {
            while(count == items.length)
                notFull.await();
            if(++addIndex == items.length)
                addIndex = 0;
            ++count;
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
    }

    //由头部删除一个元素，如果数组空，则删除线程进入等待状态，直到有新添加元素
    @SuppressWarnings("unchecked")
    public T remove() throws InterruptedException{
        lock.lock();
        try {
            while (count == 0)
                notEmpty.await();
            Object x = items[removeIndex];
            if(++removeIndex == items.length)
                removeIndex = 0;
            --count;
            notFull.signal();
            return (T) x;
        } finally {
            lock.unlock();
        }
    }
}
```

- 总结

> **上述示例中，BoundedQueue通过add(T t)方法添加一个元素，通过remove()方法移出一个 元素。以添加方法为例。 首先需要获得锁，目的是确保数组修改的可见性和排他性。当数组数量等于数组长度时， 表示数组已满，则调用notFull.await()，当前线程随之释放锁并进入等待状态。如果数组数量不 等于数组长度，表示数组未满，则添加元素到数组中，同时通知等待在notEmpty上的线程，数 组中已经有新元素可以获取。 在添加和删除方法中使用while循环而非if判断，目的是防止过早或意外的通知，只有条件 符合才能够退出循环。回想之前提到的等待/通知的经典范式，二者是非常类似的。**
> 

### 5.1 Condition的实现

- 概述

> ConditionObject是同步器AbstractQueuedSynchronizer的内部类，因为Condition的操作需要 获取相关联的锁，所以作为同步器的内部类也较为合理。每个Condition对象都包含着一个队 列（以下称为等待队列），该队列是Condition对象实现等待/通知功能的关键。
> 

### 5.2 等待队列

- 概述

> 等待队列是一个`FIFO`的队列，在队列中的每个节点都包含了一个线程引用，该线程就是 在`Condition`对象上等待的线程，如果一个线程调用了`Condition.await()`方法，那么该线程将会 释放锁、构造成节点加入等待队列并进入等待状态。事实上，节点的定义复用了同步器中节点 的定义，也就是说，同步队列和等待队列中节点类型都是同步器的静态内部类 `AbstractQueuedSynchronizer.Node`。
> 
- 基本结构

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2021.png)

- 同步队列和等待队列的关系

> 在`Object`的监视器模型上，一个对象拥有一个同步队列和等待队列，而并发包中的 Lock（更确切地说是同步器）拥有一个同步队列和多个等待队列。`Condition`的实现是同步器的内部类，因此每个`Condition`实例都能够访问同步器 提供的方法，相当于每个`Condition`都拥有所属同步器的引用。
> 
> 
> ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2022.png)
> 

### 5.3 等待

- 概述

> 当获取到锁的线程（也就是在同步队列的队首节点）调用了`await`方法就会将此节点的信息，全部复制到一个新节点（通过一个叫`addConditionWaiter`的方法）并加入到等待队列的队尾；然后调用AQS的一个fullyRelease函数，将持有的锁释放掉
> 
- 等待队列被唤醒

> 被唤醒的情况有两种就是有`condition调用signal方法`，或者等待线程被中断抛出异常
> 
- 图示

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2023.png)

### 5.4 通知

- 过程

> • 调用`Condition`的`signal()`方法，将会唤醒在等待队列中等待时间最长的节点（首节点），在 唤醒节点之前，会将节点移到同步队列中。
• 调用该方法的前置条件是当前线程必须获取了锁（**就是说调用这个方法的线程必须是获取了锁的，然后接下来会进行锁的释放，否则会抛出异常**），可以看到`signal()`方法进行了 `isHeldExclusively()`检查，**也就是当前线程必须是获取了锁的线程（就是condition对应的那个lock）**。接着获取等待队列的首节点，将其移动到同步队列并使用`LockSupport`唤醒节点中的线程。
• **通过调用同步器的`enq(Node node)`方法，等待队列中的头节点线程安全地移动到同步队 列。当节点移动到同步队列后，当前线程再使用`LockSupport`唤醒该节点的线程。**
• **被唤醒后的线程，将从`await()`方法中的`while`循环中退出（`isOnSyncQueue(Node node)`方法 返回true，节点已经在同步队列中），进而调用同步器的`acquireQueued()`方法加入到获取同步状 态的竞争中。**
• **成功获取同步状态（或者说锁）之后，被唤醒的线程将从先前调用的`await()`方法返回，此 时该线程已经成功地获取了锁。**
• **`Condition`的`signalAll()`方法，相当于对等待队列中的每个节点均执行一次signal()方法，效 果就是将等待队列中所有节点全部移动到同步队列中，并唤醒每个节点的线程。**
> 
- 图示

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%9B%9B%EF%BC%89%20%E9%94%81%EF%BC%88Lock%E6%8E%A5%E5%8F%A3%20&%20AQS%20&%20ReentrantLock%EF%BC%89/image%2024.png)