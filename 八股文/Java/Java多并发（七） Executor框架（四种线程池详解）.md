# Java多并发（七）| Executor框架（四种线程池详解）

type: Post
status: Published
date: 2022/07/12
summary: Executor框架
tags: Java
category: 技术栈

# Executor框架

- 概述

> Java的线程既是工作单元，也是执行机制。从JDK 5开始，把工作单元与执行机制分离开 来。工作单元包括Runnable和Callable，而执行机制由Executor框架提供。
> 
- Executor的两级调度模型

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image.png)

## 1.Executor框架的结构和成员

### 1.1 结构

- 三大组成部分

> 任务：被执行的任务需要实现：`Runnable接口或Callable`接口。任务的执行：包括任务执行机制的核心接口`Executor`，以及继承自`Executor`的 `ExecutorService`接口。`Executor`框架有两个关键类实现了`ExecutorService`接口 （`ThreadPoolExecutor和ScheduledThreadPoolExecutor`）。异步计算的结果：包括接口`Future`和实现`Future`接口的`FutureTask`类。
> 
- 类与结构图

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%201.png)

- Executor的使用流程

> • 主线程首先要创建实现`Runnable或者Callable`接口的任务对象。工具类`Executors`可以把一 个`Runnable`对象封装为一个`Callable`对象`（Executors.callable（Runnable task）`或 `Executors.callable（Runnable task，Object resule））`。
• 然后可以把`Runnable`对象直接交给`ExecutorService`执行`（ExecutorService.execute（Runnable command））`；或者也可以把`Runnable`对象或`Callable`对象提交给`ExecutorService`执行`（Executor- Service.submit（Runnable task）或ExecutorService.submit（Callable<T>task））`。
• 如果执行`ExecutorService.submit（…），ExecutorService`将返回一个实现`Future`接口的对象 （到目前为止的JDK中，返回的是`FutureTask`对象）。由于`FutureTask`实现了`Runnable`，程序员也可 以创建`FutureTask`，然后直接交给`ExecutorService`执行。
• 最后，主线程可以执行`FutureTask.get()`方法来等待任务执行完成。主线程也可以执行
`FutureTask.cancel（boolean mayInterruptIfRunning）`来取消此任务的执行
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%202.png)

### 1.2 成员

### 1.ThreadPoolExecutor

- 概述

> ThreadPoolExecutor通常使用工厂类Executors来创建。Executors可以创建3种类型的，下面分别进行介绍
> 

==FixedThreadPool==：

- 概述

> 是由`Executors`来提供的，**创建固定数量线程，核心和最大相等**
> 
- 适用

> `FixedThreadPool`适用于为了满足资源管理的需求，而需要限制当前线程数量的应用场 景，它适用于负载比较重的服务器。
> 

==SingleThreadExecutor==：

- 概述

> Executors提供，**创建使用单个线程，核心和最大都是1**
> 
- 适用

> `SingleThreadExecutor`适用于需要保证顺序地执行各个任务；并且在任意时间点，不会有多 个线程是活动的应用场景。
> 

==CachedThreadPool==：

- 概述

> 是Executors提供的，**创建一个会根据需要创建新线程，核心线程数为0**
> 
- 适用

> `CachedThreadPool`是大小无界的线程池，适用于执行很多的短期异步任务的小程序，或者 是负载较轻的服务器。
> 

### 2.ScheduledThreadPoolExecutor

- 概述

> 可由Executors创建两种类型
> 

==ScheduledThreadPoolExecutor==：

- 概述

> 包含若干个线程的ScheduledThreadPoolExecutor，**即固定大小**
> 
- 适用

> `ScheduledThreadPoolExecutor`适用于需要多个后台线程执行周期任务，同时为了满足资源 管理的需求而需要限制后台线程的数量的应用场景。
> 

==SingleThreadScheduledExecutor==：

- 概述

> 创建单个线程的ScheduledThreadPoolExecutor
> 
- 适用

> `SingleThreadScheduledExecutor`适用于需要单个后台线程执行周期任务，同时需要保证顺 序地执行各个任务的应用场景。
> 

### 3.Future接口

- 概述

> 用来返回异步计算的结果,当为Runnable和Callable接口的实现类提交给上述的4中线程池会向我们返回一个FutureTask对象
> 
- 常用方法

> • boolean cancel(boolean mayInterruptIfRunning) ：尝试取消执行任务
• boolean isCancelled() ：判断任务是否被取消。
• boolean isDone() ： 判断任务是否已经被执行完成。
• get() ：等待任务执行完成并获取运算结果。
• get(long timeout, TimeUnit unit) ：多了一个超时时间。
> 

### 4.Runnable接口和Callable接口

- 概述

> Runnable接口和Callable接口的实现类，都可以被线程池执行。**它们之间的区别是Runnable不会返回结果，而Callable可以返回结 果。** 除了可以自己创建实现Callable接口的对象外，还可以使用工厂类Executors来把一个 Runnable包装成一个Callable。
> 

> 对于Runnable是一个古老类，而Callable是则是1.5引入解决Runnable无法处理的情况，对于前者不会返回结果或抛出异常；并发类Executors可以将Runnable改变为Callable
> 

## 2.ThreadPoolExecutor详解

- 概述

> 框架中最核心的了是ThreadPoolExecutor，它是线程池的核心类，主要有下面四个组件构成，其实还有三个组件，但没这几个核心
> 
- 核心构成

> • corePool：核心线程池的大小。
• maximumPool：最大线程池的大小。
• BlockingQueue：用来暂时保存任务的工作队列。
• RejectedExecutionHandler：当ThreadPoolExecutor已经关闭或ThreadPoolExecutor已经饱和 时（达到了最大线程池大小且工作队列已满），execute()方法将要调用的Handler。**即饱和策略**
> 
- 其他构成

> • 线程工厂
• 存活时间
• 存活时间的单位
> 

### 2.1 FixedThreadPool详解

- 代码

```java
    /**
     创建一个线程池，该线程池重用在共享无界队列上运行的固定数量的线程。在任何时候，
     最多nThreads线程将是活动的处理任务。如果在所有线程都处于活动状态时提交了其他任务，
     它们将在队列中等待，直到有线程可用。如果任何线程在关闭之前的执行过程中由于失败而终止，
     如果需要执行后续任务，新的线程将取代它。池中的线程将一直存在，直到显式shutdown 。
	参数：
	nThreads – 池中的线程数
	回报：
	新创建的线程池
	抛出：
	IllegalArgumentException – 如果nThreads <= 0
     */
    public static ExecutorService newFixedThreadPool(int nThreads) {
        return new ThreadPoolExecutor(nThreads, nThreads,
                                      0L, TimeUnit.MILLISECONDS,
                                      new LinkedBlockingQueue<Runnable>());
    }
```

- 概述

> 该线程池的核心数和最大数都会被设置为指定的`nthreads`的数量，当线程池中的线程数大于核心数，`kat`是为多余线程等待任务的最大等待时间，超过这个则多余的线程会被销毁，如果`kat`为0那么多余的线程会被立刻停止
> 
- 流程图
1. 如果当前线程数小于核心数，那么直接创建线程执行
2. 当核心数和线程数相等（线程池完成预热），之后的任务会被加入到阻塞队列
3. 线程完成任务会反复的从队列里获取任务来执行

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%203.png)

- 如果使用无界队列作为工作队列的影响，队列容量是MAX
1. 同样执行任务的线程数等于核心数，任务直接加入队列等待
2. 最大核心数为无效
3. kat为无效
4. 由于为无界，那么在没有设置`shutdown或shutdownNow`方法时无法触发饱和策略，即不会拒绝任务

### 2.2 SingleThreadExecutor详解

- 代码

```sql
/*
创建一个使用单个工作线程在无界队列上运行的 Executor。 （但请注意，如果该单线程在关闭前的
执行过程中因失败而终止，则如果需要执行后续任务，则新线程将取代它。）任务保证按顺序执行，并
且不会有多个任务处于活动状态在任何给定时间。与其他等效的newFixedThreadPool(1)不同，
返回的执行程序保证不可重新配置以使用额外的线程。
回报：
新创建的单线程 Executor
*/
public static ExecutorService newSingleThreadExecutor() {
        return new FinalizableDelegatedExecutorService
            (new ThreadPoolExecutor(1, 1,
                                    0L, TimeUnit.MILLISECONDS,
                                    new LinkedBlockingQueue<Runnable>()));
    }
```

- 概述

> 该线程池的核心数和最大数都设置成了1，其他参数与Fixed线程池保持一致，使用无界队列作为工作队列时与Fixed的影响一致
> 
- 流程图
1. 运行的线程数小于核心数，则创建一个
2. 当线程池中有一个线程时（完成预热），之后的任务则加入任务队列
3. 线程执行完任务，无限反复的从任务队列中拿任务

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%204.png)

### 2.3 CachedThreadPool详解

- 代码

```java
public static ExecutorService newCachedThreadPool() {
        return new ThreadPoolExecutor(0, Integer.MAX_VALUE,
                                      60L, TimeUnit.SECONDS,
                                      new SynchronousQueue<Runnable>());
    }
```

- 概述

> 从源代码看，该线程池核心为0，最大线程数为MAX，也就是说线程池是无界的，kat为60s，也就是说空闲线程等待任务的最长时间为60s，时间已过空闲线程被取消
> 

> 同时使用没有容量的任务队列（不存储元素的阻塞队列SynchronousQueue），但是线程池是无界的，意味着提交任务的速度高于线程池处理任务的速度是，会创建大量新线程，会消耗CPU和内存资源
> 
- 流程图
1. 首先提交任务，在线程池有空闲线程时执行拉取任务，提交与拉取匹配，任务开始执行
2. 如果线程池为空，或是没有空闲线程，将没有线程执行拉取任务，那么线程池会新建一个线程去执行
3. 执行完任务的线程，继续循环执行拉取任务，任务规定了最大空闲时间，时间一到没有任何任务提供，那么该线程被销毁

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%205.png)

- SynchronousQueue队列的工作流程

> SynchronousQueue是一个没有容量的阻塞队列。每个插入操作必须等待另一 个线程的对应移除操作，即要有匹配线程
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%206.png)

## 3.ScheduledThreadPoolExecutor详解

- 概述

> 计划线程池继承于ThreadPoolExecutor，主要用来在给定延迟之后运行任务，或者定期执行任务。它的功能与Timer类似，但是该线程池更加强大更加灵活。因为Timer对应的是单个后台线程，而该线程池可以在构造函数中指定多个对应的后台线程
> 

### 3.1 运行机制

- 流程图

> 图中的工作队列是一个优先级的无限界队列，所以最大线程数的设置就没有什么意义了
> 
> 1. 当调用图中的两个方法，会向队列中添加一个实现了`RunnableScheduledFutur接口的ScheduledFutureTask`。
> 2. 然后线程池获取task执行任务
> 
> ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%207.png)
> 
- 为了实现计划性所做出的改变（与ThreadPoolExecutor的不同）

> • 使用DelayQueue作为任务队列。
• 获取任务的方式不同（后文会说明）。
• 执行周期任务后，增加了额外的处理（后文会说明）。
> 

### 3.2 实现

- ScheduledFutureTask的三个变量

> 前面说过队列中放的任务必须是这种类型的任务，这个对象有三个变量分别是
> 
> - long型成员变量time，表示这个任务将要被执行的具体时间。
> - long型成员变量sequenceNumber，表示这个任务被添加到ScheduledThreadPoolExecutor中 的序号。
> - long型成员变量period，表示任务执行的间隔周期。
- 队列任务执行

> 我们前面说过这个队列是带优先级的，也就是其中封装了PriorityQueue，在队列中会以time这个变量为权值进行排列，小的在前先执行；如果time相同则比较sequenceNumber，序号小的先执行
> 
- 任务执行的具体流程图
1. 从任务队列中获取time大于当前时间且是对头的任务
2. 执行该任务
3. 修改该任务的time变量为下次将要被执行的时间
4. 将这个修改完的任务放回队列中

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%208.png)

- 获取任务源码分析

> 源码是JDK8的，available是Condition配合实现等待通知，**大致总结为。第二部在一个循环内，直到获取到头元素**
> 
> 1. 获取LOCK
> 2. **如果队列为空，则等待；如果队列不为空，且time比当前时间大，等待time时间到；如果time时间小于当前时间，丢弃任务，获取队列头元素，如果为空则唤醒全部线程**
> 3. 释放LOCK

```java
public RunnableScheduledFuture<?> take() throws InterruptedException {
            final ReentrantLock lock = this.lock;	//上锁
            lock.lockInterruptibly();	//中断等待获取锁的线程
            try {
                for (;;) {
                    RunnableScheduledFuture<?> first = queue[0];	//获取任务队列的头节点
                    if (first == null)	//为空则继续等待
                        available.await();
                    else {
                        long delay = first.getDelay(NANOSECONDS);//不为空得到头节点的time
                        if (delay <= 0)//time小于当前时间 当头节点扔掉并返回
                            return finishPoll(first);
                        first = null; // don't retain ref while waiting
                        if (leader != null) //如果线程正忙，继续等待
                            available.await();
                        else {	//有空闲线程
                            Thread thisThread = Thread.currentThread();
                            leader = thisThread;
                            try {
                            //走到这一步也就是说time比当前时间大，那么我们需要等待到time
                                available.awaitNanos(delay);
                            } finally {
                                if (leader == thisThread)
                                    leader = null;
                            }
                        }
                    }
                }
            } finally {
            			//有新的任务来，唤醒线程
                if (leader == null && queue[0] != null)
                    available.signal();
                lock.unlock();
            }
        }
```

- 添加任务到队列源码分析

> 大概流程就是
> 
> 1. 获取LOCK
> 2. 添加任务；如果添加的任务是队列头元素那么唤醒线程执行任务
> 3. 释放LOCK

```java
public boolean offer(Runnable x) {
            if (x == null)
                throw new NullPointerException();
            RunnableScheduledFuture<?> e = (RunnableScheduledFuture<?>)x;
            final ReentrantLock lock = this.lock;
            lock.lock();
            try {
                int i = size;
                if (i >= queue.length)
                    grow();
                size = i + 1;
                if (i == 0) {
                    queue[0] = e;
                    setIndex(e, 0);
                } else {
                    siftUp(i, e);
                }
                if (queue[0] == e) {
                    leader = null;
                    available.signal();
                }
            } finally {
                lock.unlock();
            }
            return true;
        }
```

## 4.FutureTask详解

- 概述

> Future接口和实现Future接口的FutureTask类，代表异步计算的结果
> 

### 4.1 FutureTask简介

- 概述

> FutureTask除了实现了Future还实现了Runnable也就是说除了能交给Executor执行还能直接点run执行，根据run方法执行的时间FutureTask可以处于下面三个状态
> 
> 1. 未启动：就是创建好但未执行run
> 2. 已启动：执行中
> 3. 已完成：执行完或被cancel或抛出异常
- 线程调用get方法和cancel方法与Task状态之间的转换

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%209.png)

### 4.2 FutureTask的使用

- 概述

> 这里是说配合Executor怎么执行task任务，
> 
> - 可以把FutureTask交给Executor执行；
> - 也可以通过ExecutorService.submit（…）方法返回一个 FutureTask，然后执行FutureTask.get()方法或FutureTask.cancel（…）方法。
> - 除此以外，还可以单独 使用FutureTask。
- 用法

> 当一个线程需要等待另一个线程把某个任务执行完后它才能继续执行，此时可以使用 FutureTask。假设有多个线程执行若干任务，每个任务最多只能被执行一次。当多个线程试图 同时执行同一个任务时，只允许一个线程执行任务，其他线程需要等待这个任务执行完后才 能继续执行。
> 

```java
private final ConcurrentMap<Object, Future<String>> taskCache =
            new ConcurrentHashMap<Object, Future<String>>();

    private String executionTask(final String taskName)
            throws ExecutionException, InterruptedException {
        while (true) {
            Future<String> future = taskCache.get(taskName); // 1.1,2.1
            if (future == null) {
                Callable<String> task = new Callable() {
                    public String call() throws InterruptedException {
                        System.out.println("我正在执行"+taskName);
                        return taskName;
                    }
                }; // 1.2创建任务
                FutureTask<String> futureTask = new FutureTask(task);
                future = taskCache.putIfAbsent(taskName, futureTask); // 1.3
                if (future == null) {
                    future = futureTask;
                    futureTask.run(); // 1.4执行任务
                }
            }
            try {
                return future.get(); // 1.5,2.2线程在此等待任务执行完成
            } catch (CancellationException e) {
                taskCache.remove(taskName, future);
            }
        }
    }
```

- 上面代码执行图

> 当两个线程试图同时执行同一个任务时，
> 
> 
> **如果Thread 1执行1.3后Thread 2执行2.1，那么接 下来Thread 2将在2.2等待，直到Thread 1执行完1.4后Thread 2才能从2.2（FutureTask.get()）返回。**
> 
> ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%2010.png)
> 

### 4.3 FutureTask的实现

- 概述

> `FutureTask`的实现基于`AbstractQueuedSynchronizer`（以下简称为AQS）。`java.util.concurrent`中 的很多可阻塞类（比如`ReentrantLock`）都是基于AQS来实现的。AQS是一个同步框架，它提供通 用机制来原子性管理同步状态、阻塞和唤醒线程，以及维护被阻塞线程的队列。
> 
- 阻塞调用线程的实现

> 至少一个`acquire`操作。这个操作阻塞调用线程，除非/直到AQS的状态允许这个线程继续 执行。`FutureTask`的acquire操作为`get()/get（long timeout，TimeUnit unit）`方法调用。
> 
- 解除一个或多个阻塞线程

> 至少一个release操作。这个操作改变AQS的状态，改变后的状态可允许一个或多个阻塞 线程被解除阻塞。FutureTask的release操作包括`run()方法和cancel（…）方法`。
> 
- 这些专用方法的调用都是通过在AQS与Task中间又加入了一层封装

> **基于“复合优先于继承”的原则，FutureTask声明了一个内部私有的继承于AQS的子类 `Sync`，对FutureTask所有公有方法的调用都会委托给这个内部子类。**
> 

> **总的来说这一层封装就是具体实现了获取与释放，sync通过这个两个方法来检查和更新同步状态，内部一些操作直接调用原生AQS的方法即可**
> 
- 调用过程

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%2011.png)

- get的调用

> • 调用AQS.acquireSharedInterruptibly（int arg）方法然后通过回调Sync来判断acquire操作是否成功，即state为执行完成状态或被取消且runner不为null
• 成功则返回；失败则到任务队列中去等待其他线程执行释放操作
• 其他线程执行释放操作，唤醒当前线程后，当前线程再次判断acquire操作是否成功，state返回1则离开线程等待队列并唤醒它的后继线程（级联唤醒）
• 最后返回计算结果或抛出异常
> 
- run的调用
    - 执行构造函数指定的任务（Callable.call）
    
    ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%2012.png)
    
    - 以CAS来更新状态，如果成功则result变量的值就是call的执行结果值，然后调用释放方法
    - 释放方法还是会回调Sync的释放来执行，设置runner线程为null，然后返回true，开始调用的释放方法会唤醒线程等待队列中的第一个线程
    - 调用结束方法done
- 级联唤醒

> 上面说到如果执行完回调的acquire方法不成功即状态不为执行完成状态或已取消状态，当前线程回到线程等待队列中去排队，直到被唤醒；当某个线程执行释放会唤醒第一个线程
> 

> **当线程E执行run()方法时，会唤醒队列中的第一个线程A。线程A被唤醒后，首先把自己从 队列中删除，然后唤醒它的后继线程B，最后线程A从get()方法返回。线程B、C和D重复A线程 的处理流程。最终，在队列中等待的所有线程都被级联唤醒并从get()方法返回。**
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%B8%83%EF%BC%89%20Executor%E6%A1%86%E6%9E%B6%EF%BC%88%E5%9B%9B%E7%A7%8D%E7%BA%BF%E7%A8%8B%E6%B1%A0%E8%AF%A6%E8%A7%A3%EF%BC%89/image%2013.png)

## 5.这里简单提一嘴CompletableFuture

[美团技术团队-很详细的解析](https://tech.meituan.com/2022/05/12/principles-and-practices-of-completablefuture.html)

- 概述

> 该类实现自Future和CompletionStage，分别让其拥有异步处理能力和函数式变成的能力，可以通过new和工厂创建；即让异步任务之间产生相互的顺序，A要等B执行完一起返回，而C只要执行完就可以返回，这种复杂的编排能力该类可以提供
> 
- Future的回调地狱

> 存在异步任务的代码，不能保证能按照顺序执行，如果我们需要代码顺序执行，要怎么写呢？**这种回调函数的层层嵌套，就叫做回调地狱。回调地狱会造成代码可复用性不强，可阅读性差，可维护性(迭代性差)，扩展性差等等问题。**
> 

```java
ExecutorService executor = Executors.newFixedThreadPool(5);
ListeningExecutorService guavaExecutor = MoreExecutors.listeningDecorator(executor);
ListenableFuture<String> future1 = guavaExecutor.submit(() -> {
    //step 1
    System.out.println("执行step 1");
    return "step1 result";
});
ListenableFuture<String> future2 = guavaExecutor.submit(() -> {
    //step 2
    System.out.println("执行step 2");
    return "step2 result";
});
ListenableFuture<List<String>> future1And2 = Futures.allAsList(future1, future2);
Futures.addCallback(future1And2, new FutureCallback<List<String>>() {
    @Override
    public void onSuccess(List<String> result) {
        System.out.println(result);
        ListenableFuture<String> future3 = guavaExecutor.submit(() -> {
            System.out.println("执行step 3");
            return "step3 result";
        });
        Futures.addCallback(future3, new FutureCallback<String>() {
            @Override
            public void onSuccess(String result) {
                System.out.println(result);
            }
            @Override
            public void onFailure(Throwable t) {
            }
        }, guavaExecutor);
    }

    @Override
    public void onFailure(Throwable t) {
    }}, guavaExecutor);
```

- 如果使用CompletableFuture

> 就非常简单明了了
> 

```java
ExecutorService executor = Executors.newFixedThreadPool(5);
CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(() -> {
    System.out.println("执行step 1");
    return "step1 result";
}, executor);
CompletableFuture<String> cf2 = CompletableFuture.supplyAsync(() -> {
    System.out.println("执行step 2");
    return "step2 result";
});
cf1.thenCombine(cf2, (result1, result2) -> {
    System.out.println(result1 + " , " + result2);
    System.out.println("执行step 3");
    return "step3 result";
}).thenAccept(result3 -> System.out.println(result3));
```

- 常用方法

> • ==runAsync==：不需要依赖任务结果自己就异步执行
• ==supplyAsync==：同runAsync。只不过可以返回结果
• ==thenApply==：就是需要某个线程的任务结果采用执行，由该完成的任务的future去调用，一元依赖
> 

```java
CompletableFuture<String> cf3 = cf1.thenApply(result1 -> {
  //result1为CF1的结果
  //......
  return "result3";
});
```

> • ==thenCombine==：由完成的来调用，即二元依赖
> 

```java
CompletableFuture<String> cf4 = cf1.thenCombine(cf2, (result1, result2) -> {
  //result1和result2分别为cf1和cf2的结果
  return "result4";
});
```

> • ==allof==：多元依赖，指定的future全部完成一起返回
> 

```java
CompletableFuture<Void> cf6 = CompletableFuture.allOf(cf3, cf4, cf5);
CompletableFuture<String> result = cf6.thenApply(v -> {
  //这里的join并不会阻塞，因为传给thenApply的函数是在CF3、CF4、CF5全部完成时，才会执行 。
  result3 = cf3.join();
  result4 = cf4.join();
  result5 = cf5.join();
  //根据result3、result4、result5组装最终result;
  return "result";
});
```