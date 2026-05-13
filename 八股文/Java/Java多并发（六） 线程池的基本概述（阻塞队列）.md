# Java多并发（六）| 线程池的基本概述（阻塞队列）

type: Post
status: Published
date: 2022/07/11
summary: 池化技术的优点
tags: Java
category: 技术栈

# 线程池

### 1.池化技术的优点

- 优点

> • ==提高可重复利用性，降低资源消耗==：通过重复利用已创建的线程降低线程创建和销毁造成的消耗。
• ==提高资源响应速度==：当任务到达时,任务可以不需要等到线程创建就能立即执行。
• ==提供对资源的统一管理==：线程是稀缺资源,如果无限制地创建,不仅会消耗系统资源,还会降低系统的稳定性,使用线程池可以进行统一分配、调优和监控。但是，要做到合理利用线程池,必须对其实现原理了如指掌。
• ==提高扩展性==
> 

### 2.线程池的核心底层实现的相关参数

### 1.corePoolSize（线程池的基本大小）

- 概述

> **指定这个大小以后，每次有新任务过来，就会新创建一个线程来执行，不过池中有没有空余线程。直到执行的任务大于这个数就不会在执行了**
> 

### 2.maximumPoolSize（线程池最大数量）

> maximumPoolSize（线程池最大数量）：**线程池允许创建的最大线程数。如果队列满了，并 且已创建的线程数小于最大线程数，则线程池会再创建新的线程执行任务。值得注意的是，如 果使用了无界的任务队列这个参数就没什么效果。**
> 

### 3.runnableTaskQueue（任务队列）

- 概述

> 用于保存等待执行的任务的阻塞队列。可以选择以下几个常用的阻塞队列。剩下还有`LinkedTransferQueue、LinkedBlockingDeque`可自行了解
> 

==ArrayBlockingQueue（有界任务队列）==：

> 是一个基于**数组结构的有界阻塞队列**，此队列按FIFO（先进先出）原 则对元素进行排序。 创建ArrayBlockingQueue对象时,可以指定一个容量.当有任务需要执行时,如果线程池中线程数**小于**corePoolSize,核心线程数则创建新的线程;如果**大于**corePoolsize核心线程数则加入等待队列.如果队列已满则无法加入,在线程数**小于**maxinumPoolSize指定的最大线程数前提下会创建新的线程来执行,如果线程数**大于**maxinumPoolSize最大线程数则执行拒绝策略
> 

```java
    public void put(E e) throws InterruptedException {
        // 校验插入的元素
        checkNotNull(e);
        // 获取全局锁，放置到栈中的局部变量槽中，读取更快
        final ReentrantLock lock = this.lock;
        // 可打断的获取锁
        lock.lockInterruptibly();
        try {
            // 循环如果队列满则阻塞，while 防止虚假唤醒
            while (count == items.length)
                notFull.await();
            //
            enqueue(e);
        } finally {
            lock.unlock();
        }
    }

    private void enqueue(E x) {
        // 得到数据数组的引用
        final Object[] items = this.items;
        // 添加元素
        items[putIndex] = x;
        if (++putIndex == items.length)
            putIndex = 0;
        count++;
        // 唤醒等待消费的线程
        notEmpty.signal();
    }
```

==LinkedBlockingQueue（无界任务队列）==：

> 一个基于**链表结构的阻塞队列**，此队列按FIFO排序元素，吞吐量通 常要高于ArrayBlockingQueue。静态工厂方法Executors.newFixedThreadPool()使用了这个队列。
> 

`与有界队列相比`：

> 除非系统资源耗尽,否则无界队列不存在任务入队失败的情况.当有新的任务时,在系统线程数**小于**corePoolSize,核心线程数则创建新的线程来执行任务;当线程池中线程数量**大于**corePoolSize核心线程数则把任务加入阻塞队列
> 

`如果往无界队列一直添加任务会发生什么`：

> 可能会内存溢出，虽然可能线程数是固定的，但是无界队列突增会内存溢出，结合几个参数讲，看CPU和内存的占用情况
> 

类中除了常规链表的字段，还有两个锁

```java
		/**
     * 获取元素的全局锁
     */
    private final ReentrantLock takeLock = new ReentrantLock();

    /**
     * 插入元素的全局锁
     */
    private final ReentrantLock putLock = new ReentrantLock();
```

`插入方法`：

> 在获取方法 put 中 只会通过 `putLock.lockInterruptibly()`; 把 `putLock` 阻塞，而不会直接阻塞整个队列，获取锁之后就在链表末尾插入节点。
> 

```java
   public void put(E e) throws InterruptedException {
        if (e == null) throw new NullPointerException();
        int c = -1;
        Node<E> node = new Node<E>(e);
        final ReentrantLock putLock = this.putLock;
        final AtomicInteger count = this.count;
        putLock.lockInterruptibly();
        try {
            while (count.get() == capacity) {
                notFull.await();
            }
            enqueue(node);
            c = count.getAndIncrement();
            if (c + 1 < capacity)
                notFull.signal();
        } finally {
            putLock.unlock();
        }
        if (c == 0)
            signalNotEmpty();
    }
```

==SynchronousQueue（直接提交队列）==：

> 一个**不存储元素的阻塞队列**。每个插入操作必须等到另一个线程调用移除操作，否则插入操作一直处于阻塞状态，吞吐量通常要高于`Linked-BlockingQueue`，静态工厂方法`Executors.newCachedThreadPool使`用了这个队列。
> 

> 提交给线程池的任务不会被真实的保存,总是将新的任务提交给线程执行,如果没有空闲线程,则尝试创建新的线程,如果线程数量已经达到 maxinumPoolSize规定的最大值则执行拒绝策略.
> 

==PriorityBlockingQueue（优先任务队列）==：

> 一个**具有优先级的无限阻塞队列**。在此队列中可以根据任务优先级顺序先后执行，可以对自定义的类重写compareTo 方法来自定义排序规则或者传入 comparator 比较器。另外，该队列采用的是堆排序的方式。默认容量为11。由于是无界的那么扩充的时候就是靠数组拷贝
> 

`扩容方法`：

```java
    /**
     * 扩容大小是：
     *      （1）如果原本小于 64，则扩容为原容量的两倍+2
     *      （2）如果大于等于 64，则扩容为原容量的1.5倍
     */
    int newCap = oldCap + ((oldCap < 64) ? (oldCap + 2) : (oldCap >> 1));
```

==DelayQueue（延迟队列）==：

- 概述

> 延迟队列顾名思义，就是支持元素的延迟获取，**内部使用 `PriorityQueue` 来存储元素，加入的元素必须实现 Delayed 接口。创建元素的时候可以指定多久获取该元素，只有到达时间了才能获取。**
> 
- 使用

> **添加元素的时候指定需要延时的时间，因为使用优先队列存储元素，所以头元素就是最早到时的元素，如果时间到了直接获取，如果没到的话就通过 available.awaitNanos(delay); 方法阻塞，另外，每次只允许一个线程进行获取。**
> 
- 获取元素的方法

```java
    /**
     * 延时队列的获取方法
     * @return
     * @throws InterruptedException
     */
    public E take() throws InterruptedException {
        final ReentrantLock lock = this.lock;
        // 全局锁
        lock.lockInterruptibly();
        try {
            for (;;) {
                // 获取头节点
                E first = q.peek();
                if (first == null)
                    available.await();
                else {
                    // 获取延迟时间
                    long delay = first.getDelay(NANOSECONDS);
                    // 如果延迟时间到了直接获取
                    if (delay <= 0)
                        return q.poll();
                    first = null;
                    // 如果有线程在获取元素则阻塞，也就是一次只能一个线程获取元素
                    if (leader != null)
                        available.await();
                    else {
                        // 否则将当前线程设置为 leader 线程
                        Thread thisThread = Thread.currentThread();
                        leader = thisThread;
                        try {
                            // 没到时间则阻塞对应的延时时间
                            available.awaitNanos(delay);
                        } finally {
                            if (leader == thisThread)
                                leader = null;
                        }
                    }
                }
            }
        } finally {
            // 唤醒等待线程以及解锁。
            if (leader == null && q.peek() != null)
                available.signal();
            lock.unlock();
        }
    }
```

- 用处

> • 缓存过期的设计，使用延时队列保存缓存元素的有效期，使用一个线程循环查询，从延时队列获取到了元素，则说明到期。
• 定时任务调度，将定时任务和对应的时间加入到延时队列中，一个消费者不断获取任务，获取到则说明到期，则执行。
> 

### 4.RejectedExecutionHandler（饱和（拒绝）策略）

- 概述

> 当队列和线程池都满了，说明线程池处于饱和状 态，那么必须采取一种策略处理提交的新任务。这个策略默认情况下是AbortPolicy，表示无法 处理新任务时抛出异常。在JDK 1.5中Java线程池框架提供了以下4种策略。还可以自定义饱和策略，重写rejectedExecution方法
> 
- 四种策略

> `AbortPolicy（默认策略）`：**这种拒绝策略在拒绝任务时，会直接抛出异常 RejectedExecutionException （属于RuntimeException），让你感知到任务被拒绝了，于是你便可以根据业务逻辑选择重试或者放弃提交等策略**。`CallerRunsPolicy`：**只要线程池未关闭，只用调用者所在线程来运行任务。 相对而言它就比较完善了，当有新任务提交后，如果线程池没被关闭且没有能力执行，则把这个任务交于提交任务的线程执行，也就是谁提交任务，谁就负责执行任务。这样做主要有两点好处**。
> 
> 
> > • **第一点新提交的任务不会被丢弃，这样也就不会造成业务损失**。
> • **第二点好处是，由于谁提交任务谁就要负责执行任务，这样提交任务的线程就得负责执行任务，而执行任务又是比较耗时的，在这段期间，提交任务的线程被占用，也就不会再提交新的任务，减缓了任务提交的速度，相当于是一个负反馈。在此期间，线程池中的线程也可以充分利用这段时间来执行掉一部分任务，腾出一定的空间，相当于是给了线程池一定的缓冲期**。
> > 
> 1. `DiscardOldestPolicy`：**如果线程池没被关闭且没有能力执行，则会丢弃任务队列中的头结点，通常是存活时间最长的任务，这种策略与第二种不同之处在于它丢弃的不是最新提交的，而是队列中存活时间最长的，这样就可以腾出空间给新提交的任务，但同理它也存在一定的数据丢失风险**。
> 2. `DiscardPolicy`：**这种拒绝策略正如它的名字所描述的一样，当新任务被提交后直接被丢弃掉，也不会给你任何的通知，相对而言存在一定的风险，因为我们提交的时候根本不知道这个任务会被丢弃，可能造成数据丢失**。
- 额外说明

> 当然，也可以根据应用场景需要来实现RejectedExecutionHandler接口自定义策略。如记录 日志或持久化存储不能处理的任务。
> 
- 代码演示

```java
/**
 * 自定义饱和（拒绝）策略
 */

        //创建线程池(核心线程数，最大线程数，线程活动保持时间，线程活动保持时间的单位，阻塞队列，饱和策略)
        ThreadPoolExecutor executor = new ThreadPoolExecutor(5, 5, 0,
                TimeUnit.SECONDS, new LinkedBlockingDeque<>(10), Executors.defaultThreadFactory(),
                new RejectedExecutionHandler() {
                    @Override
                    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
                        //r就是请求的任务，executor就是当前线程池
                        System.out.println(r+"is discarding");
                    }
                });

        //向线程池提交若干任务
        for (int i = 0; i < Integer.MAX_VALUE; i++) {
            executor.execute(r);
        }
    }
}
```

### 5.ThreadFactory（线程工厂）

> ThreadFactory：**用于设置创建线程的工厂，可以通过线程工厂给每个创建出来的线程设 置更有意义的名字。使用开源框架guava提供的ThreadFactoryBuilder可以快速给线程池里的线 程设置有意义的名字，**
> 
- 代码如下：

```java
new ThreadFactoryBuilder().setNameFormat("XX-task-%d").build();
```

### 6.keepAliveTime（存活时间） & unit（时间单位）

- 概述

> **当线程数大于核心数时，这是多余线程在终止前等待新任务的最长时间，超过这个时间线程就会被销毁，unit则是等待时间的单位，也同样需要传入进去。**
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E5%85%AD%EF%BC%89%20%E7%BA%BF%E7%A8%8B%E6%B1%A0%E7%9A%84%E5%9F%BA%E6%9C%AC%E6%A6%82%E8%BF%B0%EF%BC%88%E9%98%BB%E5%A1%9E%E9%98%9F%E5%88%97%EF%BC%89/image.png)

### 3.向线程池提交任务的两种方式：execute()&submit()

- 概述

> 可以使用两个方法向线程池提交任务，分别为`execute()`和`submit()`方法
> 

==execute()==：

- 概述

> execute()方法用于提交不需要返回值的任务，所以无法判断任务是否被线程池执行成功。 通过以下代码可知execute()方法输入的任务是一个Runnable类的实例。
> 
- 执行代码

```java
threadsPool.execute(new Runnable() {
	@Override
	public void run() {
		// TODO Auto-generated method stub
	}
});
```

==submit()==：

- 概述

> submit()方法用于提交需要返回值的任务。线程池会返回一个future类型的对象，通过这个 future对象可以判断任务是否执行成功，并且可以通过future的get()方法来获取返回值，get()方 法会阻塞当前线程直到任务完成，而使用get（long timeout，TimeUnit unit）方法则会阻塞当前线 程一段时间后立即返回，这时候有可能任务没有执行完。
> 
- 执行代码

```java
Future<Object> future = executor.submit(harReturnValuetask);
	try {
		Object s = future.get();
	} catch (InterruptedException e) {
		// 处理中断异常
	} catch (ExecutionException e) {
		// 处理无法执行任务异常
	} finally {
		// 关闭线程池 executor.shutdown();
	}
```

- 注意

> **从上述代码中可以看到submit方法在处理异常时会直接将异常拦截到，但不会抛出，所以当我们用submit方法提交任务时如果某个任务出现异常我们是不知道的，结果并不会显示异常信息**
> 

### 4监控线程池

### 4.1 相关参数

- `taskCount()`：线程池需要执行的任务数量。
- `completedTaskCount()`：线程池在运行过程中已完成的任务数量，小于或等于taskCount。
- `getLargestPoolSize()`：线程池里曾经创建过的最大线程数量。通过这个数据可以知道线程池是 否曾经满过。如该数值等于线程池的最大大小，则表示线程池曾经满过。
- `getPoolSize()`：线程池的线程数量。如果线程池不销毁的话，**线程池里的线程不会自动销 毁（可以设置keepalivetime）**，所以这个大小只增不减。
- `getActiveCount()`：获取活动的线程数。
- `getCorePoolSize()`：线程池中核心线程的数量
- `getMaximumPoolSize()`：返回线程池的最大容量

### 4.2 扩展线程池

> 通过扩展线程池进行监控。可以通过继承线程池来自定义线程池，**重写线程池的 beforeExecute、afterExecute和terminated方法**，也可以在任务执行前、执行后和线程池关闭前执 行一些代码来进行监控。例如，监控任务的平均执行时间、最大执行时间和最小执行时间等。 这几个方法在线程池里是空方法。
> 
- 代码演示

```java
/**
 * 扩展线程池
 */
public class Test05 {
    private static class MyTask implements Runnable{
        //定义任务类
        String name;

        public MyTask(String name) {
            this.name = name;
        }

        @Override
        public void run() {
            System.out.println(name+"任务正在被线程"+Thread.currentThread().getId()+"执行");
            try {
                Thread.sleep(1000);     //模拟任务执行时长
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        //定义扩展线程池，可以定义线程池类继承ThreadPoolExecutor,在子类中重写beforeExecute()/afterExecute()方法
        //也可以直接使用ThreadPoolExecutor的内部类

        ExecutorService service = new ThreadPoolExecutor(5,5,0, TimeUnit.SECONDS,
                new LinkedBlockingDeque<>()){
            //在内部类中重写任务开始方法
            @Override
            protected void beforeExecute(Thread t, Runnable r) {
                System.out.println(t.getId()+"线程准备执行任务："+((MyTask)r).name);
            }

            @Override
            protected void afterExecute(Runnable r, Throwable t) {
                System.out.println(((MyTask)r).name+"任务执行完毕");
            }

            @Override
            protected void terminated() {
                System.out.println("线程池退出");
            }
        };

        for (int i = 0; i < 5; i++) {
            MyTask task = new MyTask("task"+i);
            service.execute(task);
        }

        //关闭线程池，shutdown这个方法是指不在接收线程任务，但已经接收的会让其执行完毕
        service.shutdown();

    }

}
```

### 4.3 优化线程池数量

> 线程池大小对系统性能是有一定影响的,**过大或者过小都会无法发挥最优的系统性能，线程池大小不需要非常精确,只要避免极大或者极小的情况即可**，一般来说,线程池大小需要考虑CPU数量,内存大小等因素.在`<Java Concurrency in Practice>`书中给出一个估算线程池大小的公式：
> 

`线程池大小 = CPU的数量 * 目标CPU的使用率 * (1＋等待时间 / 计算时间)`

### 5.线程池死锁

- 概述

> 如果在线程池中执行的任务A在执行过程中又向线程池提交了任务B，任务B添加到了线程池的等待队列中，如果任务A的结束需要等待任务B的执行结果.就有可能会出现这种情况:线程池中所有的工作线程都处于等待任务处理结果,而这些任务在阻塞队列中等待执行,线程池中没有可以对阻塞队列中的任务进行处理的线程,这种等待会一直持续下去,从而造成死锁
> 
- 改进

> 适合给线程池提交相互独立的任务,而不是彼此依赖的任务.对于彼此依赖的任务,可以考虑分别提交给不同的线程池来执行.
> 

### 6.线程池的异常处理（池中的线程抛出异常怎么办）

### 6.1 submit()方法的不同之处

- 概述

> 使用submit时发生异常会将异常吞并不显示
> 

==解决方法==：

1. 把submit()方法改为execute()方法
2. 对线程池进行扩展，对submit()方法进行包装
- 代码演示

```java
/**
 * 线程池的异常处理：线程池可能会吞了异常报告
 */
public class Test06 {
    private static class DivideTask implements Runnable{
        private int x;
        private int y;

        public DivideTask(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public void run() {
            System.out.println(Thread.currentThread().getName()+"计算:" + x+" /"+ y + "=" +(x/y));
        }
    }

    public static void main(String[] args) {
        //创建线程池
        ThreadPoolExecutor executor = new ThreadPoolExecutor(0,Integer.MAX_VALUE,0, TimeUnit.SECONDS,
                new SynchronousQueue<>());

        //向线程池中添加计算两个数组相除的任务
        for (int i = 0; i < 5; i++) {
            executor.submit(new DivideTask(10,i));
            /*
            * pool-1-thread-5计算:10 /4=2
            pool-1-thread-2计算:10 /1=10
            pool-1-thread-3计算:10 /2=5
            pool-1-thread-4计算:10 /3=3
            * 结果中唯独没有除以0的语句且没有报错
            */
        }
    }
}
```

==对于解决submit()的第二种方法==：

> 对线程池进行扩展，对submit()方法进行包装，**其实就是重写了submit方法**
> 

```java
/**
 * 线程池的异常处理：对线程池进行扩展，对submit()方法进行包装；解决吞异常的问题
 * 自定义线程池，对ThreadPoolExecutor进行扩展
 */
public class Test07 {
    private static class MyThreadPoolExecutor extends ThreadPoolExecutor{
        public MyThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue) {
            super(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue);
        }
        //在自定义线程池类中，定义方法，对执行任务进行包装，接收到两个参数，第一个参数接收要执行的任务，第二个参数是一个Exception异常
        public Runnable wrap(Runnable task, Exception e){
            return new Runnable() {
                @Override
                public void run() {
                    try {
                        task.run();
                    } catch (Exception exception) {
                        e.printStackTrace();
                        throw exception;
                    }
                }
            };
        }

        //重写submit方法

        @Override
        public Future<?> submit(Runnable task) {
            return super.submit(wrap(task,new Exception("客户跟踪异常")));
        }
    }

    private static class DivideTask implements Runnable{
        private int x;
        private int y;

        public DivideTask(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public void run() {
            System.out.println(Thread.currentThread().getName()+"计算:" + x+" /"+ y + "=" +(x/y));
        }
    }

    public static void main(String[] args) {
        //创建线程池
        ThreadPoolExecutor executor = new MyThreadPoolExecutor(0,Integer.MAX_VALUE,0, TimeUnit.SECONDS,
                new SynchronousQueue<>());

        //向线程池中添加计算两个数组相除的任务
        for (int i = 0; i < 5; i++) {
            executor.submit(new DivideTask(10,i));

        }
    }
}
```

### 7.关闭线程池及合理配置线程池

### 7.1 关闭线程池

- 概述

> 可以线程池的shutdown或shutdownNow方法来关闭线程池，原理是遍历整个线程池，调用线程的interrupt方法来中断，如果线程不响应中断则可能永远无法中断
> 
- 区别

> **但是它们存在一定的区别，shutdownNow首先将线程池的状态设置成 STOP，然后尝试停止所有的正在执行或暂停任务的线程，并返回等待执行任务的列表，而 shutdown只是将线程池的状态设置成SHUTDOWN状态，然后中断所有没有正在执行任务的线 程。**
> 
- 用法

> 只要调用了这两个关闭方法中的任意一个，isShutdown方法就会返回true。当所有的任务 都已关闭后，才表示线程池关闭成功，这时调用isTerminaed方法会返回true。**至于应该调用哪 一种方法来关闭线程池，应该由提交到线程池的任务特性决定，通常调用shutdown方法来关闭 线程池，如果任务不一定要执行完，则可以调用shutdownNow方法。**
> 

### 7.2 合理配置线程池

[可以看看](https://www.cnblogs.com/651434092qq/p/14240406.html)

- 配置的决定因素

> • 任务的性质：CPU密集型任务、IO密集型任务和混合型任务。
• 任务的优先级：高、中和低。
• 任务的执行时间：长、中和短。
• 任务的依赖性：是否依赖其他系统资源，如数据库连接。
> 
- 建议使用有界队列，可以预警和稳定性