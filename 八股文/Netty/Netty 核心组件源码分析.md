# Netty | 核心组件源码分析

type: Post
status: Published
date: 2023/04/22
summary: 核心组件源码分析
tags: Netty
category: 中间件

# Netty核心组件源码分析

[线程模型的各种组件理解](https://www.cnblogs.com/xfeiyun/p/15883276.html)

## 1.NioEventLoopGroup源码分析

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image.png)

- 概述

> 我们在服务启动辅助类中添加了两个线程组，都是这个类。对于这个类所做的事情就是
> 
> - 创建一定数量的`NioEventLoop`线程组并初始化。
> - 创建线程选择器`chooser`。当获取线程时，通过选择器来获取。
> - **创建线程工厂并构建线程执行器。**
- 初始化

> 初始化该线程池时会默认调用其父类的构造器，其中需要注意确定其线程数的参数为`DEFAULT_EVENT_LOOP_THREADS`属性，默认为CPU核心的2倍
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%201.png)

- 生产线程组的步骤

> 
> 
> 1. 创建一定数量（根据线程数）的EventExecutor数组
> 2. 调用子类的newChild方法完成数组的初始化，顺便提一嘴基于Epoll模型实现的线程组以及IO多路复用模型线程组都可以调用具体子类的newChild方法来实现
- 初始化线程的六个参数

> 
> 
> 1. 创建线程的线程组，**线程组通过next方法获取线程**
> 2. 线程执行器，启动线程的
> 3. NIO的选择器的提供者
> 4. run方法中控制选择循环的
> 5. 非IO任务提交时的拒绝策略
> 6. 队列工厂（AQS的同步队列）

```java
@Override
    protected EventLoop newChild(Executor executor, Object... args) throws Exception {
        EventLoopTaskQueueFactory queueFactory = args.length == 4 ? (EventLoopTaskQueueFactory) args[3] : null;
        return new NioEventLoop(this, executor, (SelectorProvider) args[0],
            ((SelectStrategyFactory) args[1]).newSelectStrategy(), (RejectedExecutionHandler) args[2], queueFactory);
    }
```

- 选择选择器对象的策略：根据线程条数是否为2的幂次来选择线程组

> • 是：使用==与远算==计算下一个选择的线程组的下标index，性能更高一点
• 否：使用取==余运算==的选择下一个线程组的下标index
> 
- NioEventLoop被包装成FastThreadLocalThread

> 由于基本线程类型会被包装，且线程状态自身管理所以需要线程执行器，通过Executor和默认线程工厂进行newThread，线程名字形如`NioEventLoopGroup-xxxid`
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%202.png)

## 2.NioEventLoop源码剖析（key就是管道的映射，即我们所说的信道）

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%203.png)

- NioEventLoop的五个核心功能，当然功能还是派发给别的类做，咱们这个线程就是统筹规划的作用

> 
> 
> 1. 开启Selector并初始化。
> 2. 把ServerSocketChannel注册到Selector上。
> 3. 执行Run方法处理各种I/O事件，如`OP_ACCEPT、OP_CONNECT、OP_READ、 OP_WRITE`事件。
> 4. 执行定时调度任务。
> 5. 解决JDK空轮询bug。
- 功能图

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%204.png)

- Netty优化线程开启Selector

> 使用反射机制将两个（一个向外即代理，一个向内）以hashSet为结构提供访问就绪key的集合，替换成以数组为结构的SelectedSelectionKeySet，**数组遍历效率高，当然优化是可选的**
> 
- run方法主要实现三部分的功能

> • 用来轮询轮询就绪的信道
• 用来处理轮询到的SelectionKey
• 用来执行队列任务
> 
- 第一部分：用来轮询轮询就绪的信道（内部还是AQS那套使用状态量）

> 轮询过程中通过调用selectNow和select（超时时间）两种不同的方法来进行轮询
> 
> 1. 当定时任务需要触发之前未轮询，会调用selectNow立刻返回
> 2. 当定时任务需要触发但被轮询过（空轮询或阻塞超时轮询），就不会调用now方法
> 3. 任务队列中的任务，一直无其他线程触发唤醒动作，则需立即调用now方法，并立即返回，防止队列中的任务超时后才处理
> 4. 超时方法阻塞运行时，会有以下四种情况进行唤醒：==①.其他选出唤醒
> ②.检测到就绪key ③.遇到空轮询 ④.超时自动醒来==除了空轮询其他情况则跳出循环处理任务
> 
> ![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%205.png)
> 
- 为什么除了空轮询

> 但是JDK中epoll的实现却是有漏洞的，其中最有名的就是NIO空轮询bug。**理论上无客户端连接时Selector.select() 方法会阻塞，但空轮询bug导致：即使无客户端连接，NIO照样不断的从select本应该阻塞的Selector.select()中wake up出来，导致CPU100%问题。Netty自己在这里做了优化**，这里是一处，后续还会通过当空轮询次数达到一定次数会直接更换selector
> 
- 第二部分：用来处理轮询到的SelectionKey（IO任务）

> processSelectedKeys：由题目可知就是处理轮询得到的key，通过key取出附件，并通过触发附件的unsafe()去底层调用IO的读写操作
> 

> 附件：就是该任务所要执行的对应操作，关联到底层的IO动作
> 
- 第三部分：执行队列任务（非IO任务）

> runAllTasks：主要就是执行任务队列和定时任务队列中的任务，如心跳检测、异步写操作等；首先根据（I/O事件与taskQueue运行的时间占比）得到的时间计算任务执行时长，
> 
> 
> **一个loop线程管理着很多个channel，而每个channel的任务可能非常多，执行完IO类型的事件可能执行不到，所以每执行64个任务就会检测任务执行时长是否够用，用完就不在执行后续任务了**
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%206.png)

- 关于唤醒
[!!!!!!!](https://blog.csdn.net/qq_45859054/article/details/115562343)
- 三个部分组合而成的run方法

> **在这个run方法中会有一个预唤醒操作，为了防止执行超时任务的时候，执行完后又有新的任务添加，此时处理的线程是无法被及时唤醒的，而此时的wakeUp又是true，导致其他线程也唤醒不了，这种等待超时才执行的消耗在某些场景下是无法接收的，所以会有一个预唤醒操作防止这个的出现**
> 
- 重构Selector（reBuildSelector）

> 从select函数的代码解读中发现，Netty在空轮询次数大于或等于 阈值（默认512）时，需要重新构建Selector。重新构建Selector的方 式比较巧妙：重新打开一个新的Selector，将旧的Selector上的key和attchment（附件）复制过去，同时关闭旧的Selector。
> 
- 注册信道的方法在两个地方被调用

> 
> 
> 1. 在绑定端口前，将NioServerSocketChannel的信道注册到Boss线程中的selector
> 2. loop线程监听到有链路接入时，把socketChannel包装成NioSocketChannel，然后注册到worker线程中去，然后调用附件对象的unsafe方法进行注册

## 3.Channel源码剖析

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%207.png)

- 概述

> 信道/频道就是Netty抽象出来对网络IO进行读写操作的相关接口，主要功能就是**网络IO的读写、客户端发起的连接、主动关闭连接、关闭链路、获取通信双方的网路地址**；通用功能主要在AbstractChannel中去定义，一些特定的就在不同的实现类去实现
> 

> 由于网络IO的协议众多，每种协议还有BIO和NIO之分，所以AbstractChannel并没有直接的操作网路IO，每种协议会在这个抽象上面继续抽象一层；就比如AbstractNioChannel就是Netty重新封装了Epoll模型的实现
> 
- AbstractChannel的重要属性

> • EventLoop：每个Channel对应一个Loop线程（一个Loop线程对应很多个channel）
• DefaultChannelPipeline：处理解码和编码的业务容器
• Unsafe：这个就是附件中带个各种IO相关的操作，都是调用这个来实现的，什么连接的读写、网络的读写、链路的关闭和发起连接等等，**Unsafe表示的不对外使用不是线程不安全的意思**
> 

> AbstractChannel的实现功能的结构图，Unsafe类是一个抽象类，
> 
> 
> **具体实现都在其子类，Unsafe大量运用的模板方法模式，集体实现细节由子类完成**
> 
> ![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%208.png)
> 
- Netty中对AbstractChannel的实现

> 上面说过AbstractChannel只是完成很简单的，其他的还需要自己的定制，Netty中的具体实现就是AbstractNioChannel，比起原始类增加了属性和方法，什么对于Unsafe类的信道连接绑定细节都是在这实现的
> 
- AbstractNioChannel三个重要属性

```java
//真正用到的NIO Channel
private final SelectableChannel ch;
//监听感兴趣的事件
protected final int readInterestOp;
//信道注册到Selector后获取的Key
volatile SelectionKey selectionKey;
```

- AbstractNioChannel中doRegister方法解析

> 该方法会在AbstractUnsafe中被register0方法中被调用
> 

> 该方法主要就做了这么几件事
> 
> - 通过JavaNio底层的javaChannel方法获取具体的信道
> - 把信道注册到loop线程的Selector上
> - 将注册后返回的Key上面设置信道感兴趣的事件：**如果存在缓存还在而未删除但已取消的Key，这时会强制调用SelectNow方法，将已经取消的Key从选择器中删除**
- AbstractNioChannel中的AbstractNioUnsafe

> AbstractNioUnsafe类是对Nio场景下的方法进行了扩展实现什么connect()、flush0()（**这个就是调用NioSocketChannel的写方法来完成数据写入Socket的工作**）等方法。该类继承了AbstractChannel中的AbstraCTUnsafe类和实现了NioUnsafe（AbstractNioChannel的内部接口实现了Unsafe接口）
> 
> 
> ![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%209.png)
> 
- AbstractNioUnsafe中的Connect方法

> 大致流程如下：
> 
> - 设置任务为不可取消状态，并确定channel已经打开和确保没有正在进行的连接
> - 远程连接会出现三种情况：
> ==①.连接成功返回True==：触发ChannelActive事件，将channel的key设置为OP_READ，监听网络读操作位；
> ==②.暂时没有连接上，服务端没有返回ACK应答，连接结果不确定返回false==：获取连接超时时间，根据时间设置定时任务，达到时间后触发校验。如果校验未通过连接没有完成，关闭连接句柄释放资源，设置异常堆栈并取消注册操作；如果校验通过增加连接结果监听器，如果接收到连接完成的通知，看连接是否被取消，如果被取消则释放资源和句柄，取消注册
> ==③.连接失败，直接抛出IO异常==：同样关闭句柄，释放资源，发起注册操作并从多路复用器上移除
- AbstractNioByteChannel

> AbstractNioChannel拥有了NIO的注册、连接等功能；但他的读写IO能力交给了其子类。Netty对I/O的读/写分为`POJO对象 与ByteBuf和FileRegion`，因此在`AbstractNioChannel`的基础上继续抽 象 了 一 层 ， 分 为 `AbstractNioMessageChannel 与 AbstractNioByteChannel` 。
> 

> 该类的功能图如下
> 
> - flushTask：task任务主要负责发送缓存链表中的数据
> 由于写是写在缓冲区的，当调用flush方法，会把数据写入socket中并向网络发送。因此当缓存中的数据未发送完成时，需要将此任务再次添加到loop线程中等待下一次的执行
> - doWrite和doWriteInternal方法在AbstractChannel的flush0方法：作用就是从ChannelOutboundBuffer缓冲区中获取待发送数据，进行循环发送，结果有三种
> ①.发送成功，跳出循环返回
> ②.TCP缓冲区已满，未发出任何数据跳出循环，并将OP_WRITE
> 时间添加到key的感兴趣事件集中
> ③.默认写16次还未发送完，此时key对应的写事件就会被移除，并且添加一个flushTask任务，先去执行其他任务，当下一回检测到次任务在执行
> - NioByteUnsafe的read方法实现思路分为三步：
> ①.获取channel的配置对象、内存分配器并计算
> ②.进入循环：使用分配器获取缓存容器，调用读字节方法从通道接收缓存区将数据读取到缓存容器中，如果未读到数据或链路关闭则跳出循环；当前循环次数达到16次同样会跳出循环。**由于TCP会产生粘包问题，所以每次读取都会触发channelRead事件，进而进行业务逻辑处理的handler**
> ③.跳出循环，表示本次读取已结束，调用allocHandle的
> readComplete()方法，记录读取记录，用于下次分配合理内存
> 
> ![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2010.png)
> 
- AbstractNioMessageChannel

> 该类是负责写入和读取的数据类型时Object，并不是字节流，所以我们重点就要讨论与字节流有什么不同
> 

> 由于传输的是对象，所以不存在粘包问题，在read方法中先循环读取数据包再触发channelRead事件
> 
- AbstractNioMessageChannel写数据

> 在写数据时，把缓存outboundBuffer中的数据包依次写入Channel中。如果写满了或者写的次数达到限制了，则在channel对应的key上设置OP_WRITE事件，随后退出，其后OP_WRITE事件的处理逻辑和Byte字节流写逻辑一样
> 
- NioSocketChannel

> 该实现类是集大成者，是AbstractNioByteChannel的子类和SocketChannel的实现类；Netty服务每个Socket连接都会生成一个NioSocketChannel对象，再起父类的基础上封装了读写与连接操作
> 
- NioSocketChannel的核心功能

> 
> 
> - 提供javaChannel方法以获取SocketChannel
> - 实现了读字节的doReadBytes()方法，从SocketChannel读取数据
> - 重写了写的方法（doWrite()方法、doWriteBytes()方法），将数据写入Socket
> - 实现了连接方法，与客户端进行连接
> 
> ![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2011.png)
> 
- 几个方法的调用关系

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2012.png)

- 到这里总结以下读写方法

> • 无论是读还是写都是进行循环读或者循环写
• 对于读来说，你要先获得缓存容器，获得内存分配器并清空上次记录进行内存分配，然后开始循环读形成链表节点加入链表，已无数据就跳出循环，释放链路资源并且其中如果对同一个事件读取次数超过限制也会跳出循环；然后根据你是传送的字节还是对象；字节就要频繁触发channelRead事件来进行粘包处理和其他业务逻辑，如果对象就是全部读完再触发channelRead事件来业务逻辑，记录此次记录并为下次合理分配内存做优化
• 对于写来说，无非就是先获取key的兴趣事件集，然后获取缓存节点的数据，进行写入到TCP缓存区的操作，数据发完在集合中消除对应事件；然后循环获取下一个缓存节点的数据，同样有对于同一个事件有循环写的最大次数
> 
- NioServerSocketChannel源码剖析

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2013.png)

> 该类由服务端使用，并且只负责监听Socket的接入，不关心IO的读写；对于Socket的接入通过newSocket方法打开ServerSocketChannel，其多路复用器注册与NioSocketChannel的多路复用器注册一样，是由父类AbstractNio Channel实现
> 
- 实现监听新加入的连接方法doReadMessages()

> 方法中会为每个新连接创建一个NioSocketChannel
> 

## 4.Netty缓冲区ByteBuf源码剖析

- 概述

> 这个ByteBuf就是代替Java中NIO中的ByteBuffer，跟上面的channel代替了JavaNIo自己的channel一样，都是由复杂变简单，ByteBuf的子类非常多，这里就介绍核心类
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2014.png)

- 其他改变

> • 内存指针：在这种区域内肯定有个指针来指向接下来要使用的区域，对Java自身的NIO来说只有一个这样的指针，那么读写状态需要手动调用方法来回切换；但是Netty是读写分离两个指针
• 缓存大小：对于原生JavaNIO这个缓存区是无法进行扩容或收缩，每次编码时都要对剩余空间进行校验；而Netty会自动扩容
• 复制对象：对于原生NIO，复制后的新对象与原对象共享内存但位置指针独立维护；而Netty引入内存池（由一定数量的ByteBuf组成），当读取数据时无序每次分配新的缓存容器，从原来的缓存容器中共享出来，并初始化大小和维护读写指针即可
• Netty采用对象引用需要手动回收，没复制一份缓存容器或派生出一份新的，引用值就要+1
> 
- AbstractByteBuf源码剖析

> 该类为ByteBuf的子类，定义了一套读写操作的方法，所以具体操作还需要子类来实现；读写索引，就是读写指针，标记读写索引就是如果解码不完整读写指针需要复位，就要先做个标记
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2015.png)

- writeBytes

> 上面说到该容器会自动扩容，那么扩容需要校验和计算新的扩容值，我们要求扩容前与扩容后都为2的整数次幂，这样好扩容。所以在代码中主要就体现在，校验是否需要扩容，如果扩容，计算新的扩容量，大致步骤跟HashMap的扩容很像
> 
- readBytes

> 首先会检测ByteBuf是否可读，检测其可读长度是否小于length，然后调用getBytes()方法从当前读索引开始，数据的具体读取就是将length个字节复制到目标byte数组中，不同的子类对应不同的复制方法，所以该类为一个抽象方法，这里简单说明一下PooledHeapByteBuf子类实现的getBytes()
> 

> 主要多的事就是检查目标数据的存储空间是否够用，然后再检查缓存容器的可读内容是否足够，然后就将缓存容器中的内容读取到数组中去
> 
- AbstractReferenceCountedByteBuf 源码剖析

> 该类引用计数法管理ByteBuf生命周期，由于为了实现零拷贝所以Netty是直接使用堆外内存来进行读写操作的，虽然减少了内存的迁移次数，但是这篇内存的分配和回收效率要远远低于JVM堆内存对象的回收效率；
> 

> 对此Netty引入引用计数法来管理这篇内存的引用和释放；Netty采用先分配一个很大的内存，然后不断的重复利用这快内存；
> 

> 例如：**当从SocketChannel中读取数据时，先在大内 存块中切一小部分来使用，由于与大内存共享缓存区，所以需要增加 大内存的引用值，当用完小内存后，再将其放回大内存块中，同时减少其引用值**
> 
- AbstractReferenceCountedByteBuf 的功能图

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2016.png)

- refCnt引用值属性

> 如果想要使用引用计数法大多都要继承AbstractReferenceCountedByteBuf ，而该类的refCnt就是来记录引用数的，考虑到并发的操作，所以该变量使用volatile关键字修饰，因为这块大内存中会创建出无数个小内存ByteBuf，所以使用原子变量AtomicIntegerFieldUpdater去更新，而不是AtomicInteger，这是因为AtomicInteger比AtomicIntegerFieldUpdater多占16B的空间，很多个小的ByteBuf证明需要很多个原子变量类去更新，所以能节省一点是一点
> 

> 初始值在新版本从原来的1（大于0表示可用，等于0表示已释放）改为现在的2，因为读写指针的关系把应该
> 
- updater属性

> 该属性负责完成该类大部分的功能
> 
- ReferenceCountUpdater

> 该类是AbstractReferenceCountedByteBuf的辅助类，用于完成对引用计数值的具体操作，功能图如下
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2017.png)

> 新版本对该类的改动很大采用了乐观锁方式来 修改refCnt，并在修改后进行校验。例如，retain()方法在增加了refCnt后，如果出现了溢出，则回滚并抛异常。在旧版本中，采用的 是原子性操作，不断地提前判断，并尝试调用compareAndSet。与之相 比，新版本的吞吐量有所提高，但若还是采用refCnt的原有方式，从1 开始每次加1或减1，则会引发一些问题，需要重新设计。这也是新版本改动较大的主要原因。
> 
- CompositeByteBuf源码剖析

> CompositeByteBuf的主要功能是组合多个ByteBuf，对外提供统一 的readerIndex和writerIndex。由于它只是将多个ByteBuf的实例组装 到一起形成了一个统一的视图，并没有对ByteBuf中的数据进行拷贝，因此也属于Netty零拷贝的一种，主要应用于编码和解码
> 
- 功能图

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2018.png)

- PooledByteBuf源码剖析

> 下面介绍一个非常重要的ByteBuf抽象类——PooledByteBuf。这 个类继承于AbstractReference CountedByteBuf，其对象主要由内存 池分配器PooledByteBufAllocator创建。比较常用的实现类有两种： 一种是基于堆外直接内存池构建的PooledDirectByteBuf，是Netty在 进行I/O的读/写时的内存分配的默认方式，堆外直接内存可以减少内 存 数 据 拷 贝 的 次 数 ； 另 一 种 是 基 于 堆 内 内 存 池 构 建 的PooledHeapByteBuf。
> 
- 功能图

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2019.png)

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2020.png)

## 5.Netty内存泄漏检测机制源码剖析

- 概述

> Netty默认情况下是使用的池化的PooledByteBuf，由于这类在使用完需要手动释放，否则会导致内存泄漏；为了解决Netty运用JDK的弱引用和引用队列设计了一 套专门的内存泄漏检测机制，用于实现对需要手动释放的ByteBuf对象的监控。
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2021.png)

- 原理

> Netty的内存泄漏检测主要就是看ByteBuf内存是否正常释放，向要实现这个机制，就需要完成以下三步：
> 
> 1. 采集ByteBuf对象。
> 2. 记录ByteBuf的最新调用轨迹信息，方便溯源。
> 3. 检查是否有泄漏，并进行日志输出。
- 过程

> 
> 
> 1. 采集入口返回的ByteBuf对象，对该对象进行一层包装，包装分为两种：SimpleLeakAwareByteBuf 与AdvancedLeakAwareByteBuf。后者是前者的子类，两者都是记录Buf的调用轨迹，区别在于后者记录Buf的所有操作；而前者只会在Buf被销毁时告诉检测工具把正常销毁对象从检测缓存中移除，不会记录Buf的操作
> 2. 对于每个Buf对象的调用信息都记录在其弱引用，这个弱引用对象和Buf都被包装在了SimpleLeakAwareByteBuf ，里面除了调用轨迹还有关闭检测的功能，Buf被销毁自然需要关闭资源检测，防止误报
> 3. 创建这个弱引用时需要配合引用队列，当检测是否有资源泄漏时，会遍历这个队列，找到已回收的Buf引用，通过这个引用判断是否调用了销毁接口，检测是否有泄漏
- 引用队列和弱引用缓存

> **Netty除了会把弱引用加入到队列中，还会缓存一份，当Buf销毁后，对应缓存中的引用会被移除，当去遍历引用队列，检测其引用在缓存中是否被销毁，如果缓存中没有说明没有发生泄漏；将这些弱引用放在缓存中等于变相的强引用了，因为如果没有强引用，那么可能会发生软引用对象在遍历之前就会回收了，调用信息全没了，所以缓存在全部Set中**
> 
- 内存泄漏器ResourceLeakDetector源码 剖析

> 实际监控缓冲区的就是该类，每个Buf都会有个该类的实例。该类的track方法就是整套检测系统对于单个Buf的入口，提供资源采集逻辑，什么队列和缓存的维护也都靠它
> 
- 弱引用记录链表

> 上面说到要记录轨迹信息，这个由上面类的私有实现类DefaultResourceLeak负责，调用的记录就会加入此类的Record链表中，由于有长度限制，所以不会保存全部的记录
> 
- Netty的内存泄漏检测机制的四种检测级别

> 
> 
> - DISABLED：表示禁用，不开启检测。
> - SIMPLE：Netty的默认设置，表示按一定比例采集。若采集的ByteBuf出现泄漏，则打印LEAK:XXX等日志，但没有ByteBuf的任何调 用栈信息输出，因为它使用的包装类是SimpleLeakAwareByteBuf，不会进行记录。**上线稳定后设置这个**
> - ADVANCED：它的采集与SIMPLE级别的采集一样，但会输出ByteBuf 的 调 用 栈 信 息 ， 因 为 它 使 用 的 包 装 类 是AdvancedLeakAwareByteBuf。**出现泄漏，重启服务并设置成这个排查**
> - PARANOID：偏执级别，这种级别在ADVANCED的基础上按100%的比例采集。**一般初上线时设置这个**
- 入口AbstractByteBufAllocator 的toLeakAwareBuffer()方法

> 该类的此方法就是整套系统的初始化，会为每个Buf分配内存泄漏检测器ResourceLeakDetector，并对处理完的Buf进行包装返回
> 
- track方法

> 先获取检测级别，当级别是简单和先前会采取随机数策略，根据数字采用不同的策略，然后调用reportLeak方法，该方法循环获取引用队列的弱引用，来检查是否有泄漏，并且会输出泄露记录和调用栈记录；reportLeak方法会在循环中通过调用dispose方法来判断是否泄漏（就是看缓存和队列的关系）
> 
- record方法

> 该方法就是对record调用记录链表的初始化和操作，首先会判断链表头是否为空，然后获取链表的长度，上面说到链表有长度限制的，方法会调用toString方法来获取Record创建时的调用栈信息，其中会跳过一个无用的栈信息，并且将有用的信息格式化
> 

# Netty读/写请求源码剖析

## 1.ServerBootstrap启动过程剖析

- NIO服务器的概述

> 该类是服务器的启动模板，我们在自己搭建Netty服务器时，从主方法中每次都要加载优化为静态加载，我们先来复习复习NIO中比较重要的几个类：在Netty中都被封装成别的带有Nio前缀的字样，**注意这里说的封装并不是完全就不用NIO那套了，因为最终都会被JVM执行，Netty封装的再花，最终也要通过JavaNIO这套在底层打交道**
> 
- ==Selector==：多路复用器，核心组件。负责监听通道（channel）的各个事件，并检查各个通道是否处于可读写状态，实现单线程管理多链路
- ==ServerSocketChannel==：socket的抽象即通道，是连接selector与socket的桥梁，开启监听端口，当监听到有新的TCP连接，新建ServerSocketChannel并注册到selector，并设置监听事件**OP_ACCEPT**
- ==SocketChannel==：连接到TCP网络Socket上的通道，上面负责监听接入，而这个主要就是通道的抽象承载。创建方式两种：1.创建SocketChannel去主动连接服务器；2.当客户端连接到ServerSocketChannel时会创建一个SocketChannel
- 三者配合处理流程（也就是一个Netty服务器所具备的）

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2022.png)

- Netty服务启动主要涉及的类和方法

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2023.png)

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2024.png)

- 步骤

> 
> 
> 1. 创建两个线程组，并实例化每个线程组的子线程数组，Boss只设置一条数组，Worker线程组默认为核心数*2，同时每个loop线程都会开启一个多路复用器
> 2. 通过反射创建NioServerSocketChannel，为什么利用反射？因为又不只有TCP协议的NIO你个猪头，想要什么建什么，并将channel赋值给SelectableChannel的ch属性
> 3. 初始化channel，设置属性attr和参数option，并将handler添加到channel的Pipeline管道中
> 4. 通过Unsafe调用register0方法，执行channel的doRegister方法，底层调用JavaNIO的注册方法把channel注册到选择器中，同时带上附件，这里附件就是channel本身，前面说到这个附件就是指向那些事件的发起者，后续事件轮询到就绪key就是通过附件获取的。注册成功后，添加回调任务即为上面定义的handler
> 5. 注册成功后，会 触 发 ChannelFutureListener 的 operationComplete()方法，此方法会带上主线程的ChannelPromise参数（主线程获取loop线程执行结果就从这获取） ，主要做的工作就是绑定端口（也是bind调用dobind），当绑定成功后， 会触发active事件，为注册到Selector上的ServerSocketChannel加上监听OP_ACCEPT事件；最终运行ChannelPromise的safeSetSuccess()方法唤醒server Bootstrap.bind(port).sync()。
- 对于以上步骤的思考

> 
> 
> 1. ServerSocketChannel在注册到Selector上后为何要等到绑定端口才设置监听OP_ACCEPT事件？（跟Netty的事件触发模型有关）
> 2. NioServerSocketChannel 的 Handler 管道DefaultChannelPipeline是如何添加Handler并触发各种事件的？

## 2.Netty对I/O就绪事件的处理

- 对于每一个channl都有如下的结构

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2025.png)

### 2.1 NioEventLoop处理就绪OP_ACCEPT

> 上面讲到当进行完5步，设置好监听OP_ACCEPT事件，那么当Socket通道接入以后，OP_ACCEPT事件时间就绪，Netty会怎么处理呢，先来看看NioEventLoop处理就绪OP_ACCEPT事件的时序图
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2026.png)

- 对于时序图的步骤解释

> 
> 
> 1. 当Loop线程的多路复用器Selector轮询到就绪的key时，会判断此key的类型是否为OP_ACCEPT，如果是那么这个key的附件就是NioServerSocketChannel本身，所以获取附件对象，再触发此对象的辅助类Unsafe进行读操作
> 2. 在 NioMessageUnsafe 的 read() 方 法 中 会 执 行doReadMessages （ 此 处 用 到 了 模 板 设 计 模 式 ） 。 真 正 调 用 的 是AbstractNioMessageChannel 的 子 类 NioServerSocketChannel 的doReadMessages() 方 法 。 此 方 法 最 终 调 用 ServerSocketChannel 的accept()方法，以获取接入的SocketChannel。将accept()方法在AbstractNioChannel的构造方法中设置为非阻塞状态，不管是否有Channel接入，都会立刻返回，并且一次最多默认获取16个，可以通过 设 置 option 参 数MAX_MESSAGES_PER_READ 来 调 整 。 获 取 到SocketChannel 后 ， 构 建 NioSocketChannel ， 并 把 构 建 好 的NioSocketChannel对象作为消息msg传送给Handler（此Handler是ServerBootstrapAcceptor ） ， 触 发 Pipeline 管 道 的fireChannelRead()方法，进而触发read事件，最后会调用Handler的channelRead()方法。
> 3. 在ServerBootstrapAcceptor的channelRead()方法中，把NioSocketChannel注册到Worker线程上，同时绑定Channel的Handler链。
> 4. 当将NioSocketChannel注册到Selector上时，有部分代码需要解 读 ， NioSocketChannel 对 应 的 NioEventLoop 线 程 在 未 启 动 时 ，eventLoop.inEventLoop()会返回false。若Worker的线程为16，则 在前面16个NioSocketChannel注册时，都会把注册看作一个Task并添 加到NioEventLoop的队列中，同时启动NioEventLoop队列，唤醒Selector。
> 5. NioEventLoop I/O的读/写线程已开启，并一直轮询监听是否触发了OP_READ事件

### 2.2 NioEventLoop就绪处理之OP_READ（一）

> 上面说完了建立好了一切准备工作，现在worker线程组中的loop线程就该读取socket链路传来的数据了，对于接收和处理的过程与上面建立连接差不多，区别在于实际处理Unsafe类从NioMessageUnsafe变成 了NioByteUnsafe，Handler类变成了用户设置的编/解码器，以及业务 逻辑处理Handler不再是ServerBootstrapAcceptor。下面请看时序图
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2027.png)

- 时序解读

> 与上面类似而本小节中的NioByteUnsafe不断地调用NioSocketChannel的doReadBytes()方法从Channel中读取数据，再把读取到的ByteBuf交 给 管 道 Pipeline ， 并 触 发 后 续 一 系 列 ChannelInboundHandler 的channelRead()方法。整个读取数据的过程涉及的Handler都是以HeadContext开头的，按顺序运行用户自定义的各个解码器和服务端业务逻辑处理Handler。
> 
- channelRead()方法等解码方法的流程

> 
> 
> 1. channelRead()方法首先会判断msg是否为ByteBuf类型，只 有在是的情况下才会进行解码。这也是为什么将StringDecoder等MessageToMessageCodec解码器放在ByteToMessageDecoder子类解码器 后面的原因，这时的msg一般是堆外直接内存DirectByteBuf，因为采 用堆外直接内存在传输时可以少一次复制。然后判断是否为第一次解 码，若是，则直接把msg赋值给cumulation（cumulation是读半包字节 容器）；若不是，则需要把msg写入cumulation中，写入之前要判断是否需要扩容。
> 2. 把新读取到的数据写入cumulation后，调用callDecode()方 法。在callDecode()方法中会不断地调用子类的decode()方法，直到 当前cumulation无法继续解码。无法继续解码分两种情况：第一种情 况是无可读字节；第二种情况是经历过decode()方法后，可读字节数没有任何变化。
> 3. 执行完callDecode()方法后，进入finally代码块进行收尾 工作。若cumulation不为空，且不可读时，需要把cumulation释放掉 并赋空值，若连续16次（discardAfterReads的默认值）字节容器cumulation中仍然有未被业务拆包器读取的数据，则需要进行一次压 缩 ： 将 有 效 数 据 段 整 体 移 到 容 器 首 部 ， 同 时 用 一 个 成 员 变 量firedChannelRead来标识本次读取数据是否拆到了一个业务数据包， 并触发fireChannelRead事件，将拆到的业务数据包传递给后续的Handler，最后把out放回对象池中。
- 解码器的分类

> • 一种是根据特殊字符解码（如DelimiterBasedFrameDecoder），找到ByteBuf中是否有对应的特殊字 符，若有，则截断读取对应的消息；
• 另一种是根据写入消息体长度值 解码（如LengthFieldBasedFrameDecoder），这种解码器的一般用法
是先读取前面4个字节的int值，再根据这个值去读取可用的数据包。
> 

### 2.3 NioEventLoop就绪处理之OP_READ（二）

- 概述

> 上面是分析了对于事件的接收处理以及分发给各个解码handler的处理过程，那么对于**业务handler**的处理的结果的返回过程我们再详细说一下，请先思考如下的问题
> 
1. Netty在写操作时会依次调用哪些Handler？

> 如下图，我们可以和读数据时作为对比，看看管道内发生了什么
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2028.png)

> 在读数据时，Handler从HeadContext开始到解码器父类ByteToMessageDecoder，再到具体解码器，最后调用业务逻辑处理类ServerHandler。在写数据时，Handler从TailContext开始到编码器父类MessageToMessageEncoder，再到具体编码器，最后调用HeadContext。其中的TailContext只起了引用串联的作用，具体逻辑处理是由其父类实现的。而HeadContext的一个属 性——unsafe，此属性处理了Channel的接入和数据的写入、关闭等。Handler链的顺序如图5-7所示。
> 

> HeadContext和TailContext之间连接了各种编码器、解 码器，形成了整个Handler链表，图中的箭头表示编码器和解码器的查 找方向。Handler链表的头部和尾部都是在DefaultChannelPipeline的构造方法中定义好的
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2029.png)

> 当发生读事件（在Netty里也叫输入`inbound入站`事件）时，I/O
EventLoop 线 程 先 从 HeadContext 中 依 次 向 后 查 找
ChannelInboundHandler类型的Handler，并调用其channelRead()方 法。当发生写操作`outbound出站`事件时，从TailContext中依次向前查找
ChannelOutboundHandler类型的Handler，并调用其write()方法。这 也是为何解码器先追加的被先调用，而编码器正好相反的缘故。
> 
1. 在业务Handler中，若开启了额外业务线程，那么在Netty内部是如何把业务线程的结果数据经过I/O线程发送出去的呢？

> 例如这个额外业务线程的业务是ctx.channel().writeAndFlush(JSONObject.toJSONString(response))时，Loop线程如何获取response内容并写会给channel呢？
> 

> 在写的过程会有两种task，分 别 是 WriteTask 和
WriteAndFlushTask，主要根据是否刷新来决定使用哪种task。每个Channel都有一条NioEventLoop线程与之对 应，**在NioEventLoop的父类SingleThreadEventExecutor中有个队列属 性 ， 叫 taskQueue ， 它 主 要 通 过 SingleThreadEventExecutor 的execute() 方 法 存 放 非 EventLoop 线 程 的 任 务** ， 包 括 WriteTask 和WriteAddFlushTask这两种WriteTask。当调用添加任务时，会唤醒EventLoop线程，从而I/O线程会去调用这些任务的run()方法，并把结果写回Socket通道。
> 
1. 为了提高网络的吞吐量，在调用write时，数据并没有直接被写到 Socket 中 ，而是被写到了Netty的缓冲区（ChannelOutboundBuffer）中，在并发很大的情况下，当对方接收数 据较慢时，Netty的写缓冲区如何防止内存溢出，防止出现大量内存无法释放的情况

> 我们先来了解一下ChannelOutboundBuffer，它由一个链表构成，每个链表节点Entry有消息内容和next指针等，类中有十分重要的五个属性，如下图
> 

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2030.png)

- 缓冲区处理过程如下

![image.png](Netty%20%E6%A0%B8%E5%BF%83%E7%BB%84%E4%BB%B6%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/image%2031.png)