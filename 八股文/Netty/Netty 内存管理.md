# Netty | 内存管理

type: Post
status: Published
date: 2023/04/23
summary: 内存管理
tags: Netty
category: 中间件

# Netty内存管理

## 1.Netty内存管理策略介绍

- Netty内存管理层级结构

> 为了提高内存使用效率，Netty引入jemalloc内存分配算法，netty内存管理层级如下：
> 
> - 图中为了避免线程竞争和同步，每个IO线程对应一个PoolThreadCache（线程本地缓存），负责小内存的快速申请和释放
> - 如果PoolThreadCache获取不到内存，就要开始从PoolArena的内存池中分配，**但是其内存使用完是释放回PoolThreadCache中的方便下次使用**
> - 如果从PoolArena也分配不到内存，就要从堆内外内存中申请，单位是PoolChunk，如果该内存块大小为12M则会被放入PoolArena，还是方便重复利用
> - 如果超过12M默认，则直接在对内外创建，其实就是不归PoolChunk管了，用完直接回收
> 
> ![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image.png)
> 
- 内存分配导图及步骤

> 
> 
> 1. **Netty在分配具体内存之前，会获取本次内存分配的大小**，具体的内存分配由PoolArena统一管理，先从线程的本地缓存中获取，本地缓存采取固定长度队列缓存线程之前使用过的内存
> 2. 若本地无缓存就是要从PoolArena获取，**若大于等于8K或在PoolArena分配内存失败，再会去PoolChunkList中查找可分配的PoolChunk。**
> 3. 若PoolChunkList也分配失败，则创建新的PoolChunk，**如果分配完又小于8k则交给PoolArena管理，而不是加入对应的List**
> 
> ![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%201.png)
> 

## 2.PoolChunk内存分配

### 2.1 PoolChunk分配大于或等于8KB的内存

- 概述

> **Netty底层的内存分配和管理主要由PoolChunk实现**，大于16MB的
PoolChunk由于不放入内存池管理，比较简单
> 
- 内存块（PoolChunk）

> PoolChunk你可以看做是一个大内存块，里面会被分为一个一个小的内存块，分配的单位实际由小的构成，
> 
> 
> **并且在分配内存时会存在预分配的行为，即多分配几个小块**
> 
> ![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%202.png)
> 
- PoolChunk的抽象数据结构

> 
> 
> 
> PoolChunk内部维护一棵平衡二叉树，`默认由2048个page组成， 一个page默认为8KB，整个Chunk默认为16MB`，结构如下 ：当分配的内存大于某一值的时候需要通过公式`（int d=11-(log2(normCapacity：分配的内存)-13)）`指定算出搜索的层数，例如算出10则只能在小于等于10的层上寻找还未被分配的节点
> 
> ![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%203.png)
> 

> 实际底层的存储就够是一个放下来所有节点的数组memoryMap，key是节点，value是节点的高度值（最高为12）；派送出来还有一个depthMap，**这个map一直不会改变通过depthMap可以获取节点的 内存大小，还可以获取节点的初始高度值**，那么也就是说前者是会发生变化的，**如果需要分配的内存不在前者数组中，会得不到高度值进而会进行加工处理**
> 
- 如何查找对应的可用节点并更新其父节点的高度值的呢？

> Netty采用前序遍历，采用左、右、根的访问顺序，来看内存是否够用，不够看兄弟节点，如果够用则继续向下一层遍历，**因为我们要找一个最接近请求内存值算出来的那个层数d**
> 
- 详情看源码寻找节点的allocateNode方法

> **通过id异或与id同层级最左边的 元素的下标值得到偏移量，再用偏移量乘以当前层级节点的内存大 小，进而获取在PoolChunk整个内存中的偏移量。有了偏移量和需要分 配 的 内 存 大 小 Length ， 以 及 最 大 可 分 配 内 存 的 大 小 （ 可 根 据runLength(id)计算得出），即可初始化PooledByteBuf，完成内存分 配。**
> 

```java
//d就是申请了多少内存算出的高度
private int allocateNode(int d) {
        int id = 1;
        //掩码，与id进行位运算后若大于0，这说明id对应的高度大于等于d
        int initial = - (1 << d);
        //通过id过得存储节点数组中的对应大小
        byte val = value(id);
        if (val > d) { //空间无法满足则分配失败
            return -1;
        }
        //满足则继续寻找最合适的
        while (val < d || (id & initial) == 0) {
            id <<= 1;	//寻找下一层
            val = value(id);	//获得本层的高度值
            if (val > d) {	//高度大于d说明还能找到更小的
                id ^= 1;	//异或为右孩子，即兄弟节点
                val = value(id);//在获取兄弟节点的高度值
            }
        }
        byte value = value(id);	//直到id合适获取对应高度
        assert value == d && (id & initial) == 1 << d : String.format("val = %d, id & initial = %d, d = %d",
                value, id & initial, d);
        setValue(id, unusable); 	//然后标识为不可用
        updateParentsAlloc(id);	//更新父结点的高度值
        return id;	//返回高度值
    }
```

- 小结

> 其实对于网络传输很少发生大于8KB的数据出现，所以我们要关注接下来小于8KB的情况
> 

### 2.2 PoolChunk分配小于8KB的内存

- PoolSubpage数组

> 该数组与memoryMap差不多，都为2048个页（subpages），每个page节点只能分配一种PoolSubpage`（tiny、small、normal）`，所以subpages的下标与page的偏移量一一对应，每一page均可分配一个PoolSubpage链表，表头就是数组中的元素，**即subpages数组有2048个由PoolSubpage链表组成的，每个索引位置的元素就是链表的头节点**
> 

![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%204.png)

- 数组分配步骤

> 
> 
> 1. 在PoolChunk二叉树找page节点，从2048开始，我们在复习一边二叉树的结构，可以看到2048个page都在11层，将page节点与2048进行异或可以得到subpages的在PoolSubpage中的下标
> 2. 取出对应下标的值，判断是否为空，为空创建新的
> 3. 该数组分为两种一个位`0~512B的tiny数组，和512B~8kb的small数组` ，此时还未区分所以将该数组加入到缓冲池中，以便后续调用
> 4. 缓冲池对应两个数组也有两种类型，分别是`存储(0,512)个字节的tinySubpagePools和存储[512,8192)个字节的smallSubpagePools 。`**数组扩容的elemSize，对于前者是从16B开始，每次增加16B；对于后者则是512成倍上涨**
> 5. tiny从16B开始，因此数组长度为512/16=32B；small从512开始，数组共有四个元素通过分配的内存elemSize可以快速定位数组缓冲的位置
> 6. 如何通过分配的内存从缓存池中快速找到对应的PoolSubpage链表？（findSubpagePoolHead）：**对于tiny可以将elemSize无符号右移4位得到数组的下标tableIdx；而对于small对elemSize先除1024在除2看某一步是否为0，最终找到tableIdx。有了tableIdx就可以定位数组中的链表了**
> 7. 若数组定位失败或者链表不可再分配元素则会退1步骤循环分配直到有地方
> 
> ![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%205.png)
> 

- 源码分析

```java
private long allocateSubpage(int normCapacity) {
		//得到是tiny还是small缓冲池对应空间的head指针
        PoolSubpage<T> head =
        arena.findSubpagePoolHead(normCapacity);
        int d = maxOrder; //小于8kb只在11层分配
        //分配前需要将数组加入缓冲池，以便下次调用，那么就加锁head
        synchronized (head) {
        	//获取一个可用节点
            int id = allocateNode(d);
            if (id < 0) {
                return id;
            }

            final PoolSubpage<T>[] subpages = this.subpages;
            final int pageSize = this.pageSize;
			//可用page减1，表示已使用
            freeBytes -= pageSize;
			//根据page的偏移值异或2048得到PoolSubpage的索引
            int subpageIdx = subpageIdx(id);
            //然后根据page获取对应的PoolSubpage链表
            PoolSubpage<T> subpage = subpages[subpageIdx];
            //除了head为空则创建追加到该链表head的后面
            if (subpage == null) {
                subpage = new PoolSubpage<T>(head, this, id, runOffset(id), pageSize, normCapacity);
                subpages[subpageIdx] = subpage;
            } else {
            //这里同样会把该节点加到head后面，相当于向前移动了
                subpage.init(head, normCapacity);
            }
            //为该链表节点内存分配
            return subpage.allocate();
        }
    }
```

## 3.PoolSubpage内存分配与释放

### 3.1 内存分配与buf容器的联系

- 概述

> 前面讲过，每一个PoolSubpage是由PoolChunk的page生成的，page可以生成很多种的PoolSubpage，但是每一个page只能生成其中一种的PoolSubpage；PoolSubpage可以分为很多段，每段大小相同，分配时动态根据需要变化
> 
- PoolSubpage的重要字段

```java
	final PoolChunk<T> chunk;	//当前分配内存的chunk
	//当前page在chunk的memory数组中的下标id
    private final int memoryMapIdx;
    //当前page在chunk实际存在的偏移量
    private final int runOffset;
    //page的大小默认为8K
    private final int pageSize;
    //位图，当前段PoolSubpage的使用情况
    private final long[] bitmap;
	//链表的特征，前一个后一个
    PoolSubpage<T> prev;
    PoolSubpage<T> next;

   	//每段的大小，最小值为16B
    int elemSize;
    //段的总数量
    private int maxNumElems;
    //long数组的长度值
    private int bitmapLength;
    private int nextAvail;	//下一个可用位置
    private int numAvail;	//可用段的数量
```

- PoolSubpage的段实例

![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%206.png)

- 内存分配源码

> 根据allocate()、getNextAvail()、findNextAvail()、findNextAvail0()这四个方法可得知大概的分配步骤就是：
> 
> 1. 获取PoolSubpage的一个可用位置，找到该位置对应的bit数组下标
> 2. 根据下标找到bit数组中实际可用的位数据
> 3. 设置位占用信息
> 4. 如果此page已经分配完了，则直接从缓冲池中剔除
> 5. 将page的索引和PoolSubpage的索引一起返回，低**32位是page在PoolChunk的二叉树中的位置memoryMapIdx、高32位是PoolSubpage中分配的内存段在page中的相对偏移量**
- 底层内存与buf的联系

> 根据源码内存分配成功为得到一个handle，而在Netty上层控制这部分内存的是一个buf容器即ByteBuf，那么这个底层handle如何跟上层的ByteBuf联系上的呢？
> 
> 1. 通过handle计算出page的偏移量
> 2. 通过handle计算出该段在page中的相对偏移量
> 3. 两者计算出该段在chunk中的相对偏移量
> 4. buf容器的缓冲池从channel读取数据，要用上面的偏移量来获取具体的buf容器
> 5. 然后缓冲池将定位到的容器复制一份新的，并初始化新的容器元数据，这个新的容器是与原容器共享内存的；通过offset指定读/写位置，用limit来限制读/写范围。

> 相关联系的方法
> 
> 1. PoolChunk的allocate方法：根据返回的page和PoolSubpage索引进行分配内存，获取一个容器对象并初始化
> 2. PoolChunk的initBuf方法：根据返回的两者索引计算出两者的偏移量，然后根据两者的偏移量算出在chunk的偏移量
> 3. PoolChunk的initBufWithSubapge方法：根据chunk的偏移量+该段在page的偏移量+堆外内存地址初始化buf容器
> 4. PooledByteBuf的idx方法：获取在容器的位置
> 5. PooledByteBuf的newInxx方法：复制新的容器

### 3.2 内存释放

首先根据handle指针找到内存在PoolChunk和PoolSubpage中的相对偏移量

1. 若PoolSubpage上的偏移量大于0

> 则去位图中将使用的位置全部设置为0，然后清理缓冲区的相关节点，然后将释放的区域追加到Arena 的PoolSubpage缓存池中，方便下次直接从缓冲池中获取
> 
1. 若PoolSubpage上的偏移量等于0

> 若在PoolSubpage上的偏移量等于0，或者PoolSubpage释放 完 后 返 回 false （ PoolSubpage 已 全 部 释 放 完 ， 同 时 从 Arena 的
PoolSubpage缓存池中移除了），则只需更新PoolChunk二叉树对应节
点的高度值，并更新其所有父节点的高度值及可用字节数即可。
> 

## 4.PoolArena内存管理

- 概述

> 该类根据最前的结构图可谓是内存分配的最大管理者及最大分配单位了，**当Netty从channel中读取数据时，需要内存分配器来分配内存，最终的分配工作其实是PoolArena来分配的，它是内存管理的入口**；那么他跟PoolChunk、PoolSubpage、PoolByteBuf有什么关系呢？
> 
- PoolArena内部结构

> 由于Netty是高并发系统，为减少线程争抢同一块内存的竞争，提高内存分配的效率，默认情况下会创建多个PoolArena并放入线程的本地缓存中，
> 

![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%207.png)

### 4.1 PoolArena的各种chunk链表

- 概述

> 根据上面的结构图可以看到PoolChunkList是PoolChunk链表，对于Netty的重复利用内存机制而言，一般每次分配内存是先去之前的chunk内存块进行分配的，这么多个内存块该怎么管理呢？**根据内存块内部的利用率来划分为了几个不同的chunk链表**，该列表有两个重要属性：即 minUsage 和 maxUsage 。
> 
> - 当chunk利用率高于当前列表规定的maxUsage，就会移动至下一个链表的中
> - 反之利用率下降到当前规定的minUsage，就会移动到上一个链表
- 结构图

![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%208.png)

1. qInit：该链表存储率为`[0%,25%)`，minUsage为Integer的最小值，当chunk被创建时，如果内存分配一只小于25，那么即使完全释放也不会回收这一部分
2. q000：利用率为`[1%,50%)`，当chunk进入该链表后，如果内存被完全释放，会被直接删除chunk，物理内存被回收，避免chunk越来越多
3. q025：利用率为`[25%,75%)`，为了避免在临界点反复横跳所以将设置为重叠
4. q050：利用率为`[50%,100%)`，**为了提高内存分配的成功率，同时让chunk的利用率保持较高水平，分配内存时会选择从q050开始，尤其是在业务繁忙期；此时如果在q000开始，那么会让回收概率大大降低，浪费大量内存**
5. q075：利用率为`[75%,100%)`，**在50和100之间的缓冲，在等于100被回收一部分后的chunk不那么块进入q050，否则下一回又会被优先选中，导致内存利用率一直处于100边缘，因此PoolArena在分配内存时把q075放在了最后。**
6. q100：存储内存利用率为`100%`的PoolChunk，无法再继续分配，只能等待释放。

### 4.2 PoolArena的内存分配

- 概述

> 对于PoolArena的职责就是获取想要获取的内存，对于内存的不同交给处理的下层结构也就不同，可是说它是内存的最大管理者，我们从它的分配方法allocate中就可以看出
> 
- 注意

> chunk的默认大小为12MB，当大于12并且小于16，还是有chunk负责的，但是大于16则直接堆外了
> 

### 4.2.1 allocate方法的流程

- 小于8192的情况

> • **根据normalizeCapacity方法获取请求的容量的优化版normCapacity**，根据normCapacity是小于512还是512到8192之间，来分配tiny还是small管理；
• 都是先看本地缓存有没有，
• 没有再去后面缓冲池之类的申请流程（比如就是去获取subpages中的索引，然后获取头节点，看头节点后面是否还有内存，有就初始化buf容器等）
• 如果两者都没有空间了对本PoolArena加锁，去调用allocateNormal方法
> 

> **这里小提一下`normalizeCapacity`方法，这个方法会根据申请的内存，如果申请的恰巧是512、1024等翻倍就可能超过临界点的值进行减一，然后到正儿八经分配的时候在加一，所以我们称为优化版**
> 
- 大于8192小于12MB

> • 还是先从本地缓存中获取
• 没有就正常申请流程调用allocateNormal方法
> 
- 大于12MB

> 调用allocateHuge方法，大于12MB时不放入缓存池
> 

### 4.2.2 allocateNormal方法的流程

- 概述

> 上面提到基本上内存不够或者给稍微大一点的内存需求都要调用这方法，此就要引入chunk链表进行分配内存了
> 
- 判断chunkList

> 先从`q050->q05->q000->qInit->q075`的顺序分配内存，都是或关系，从对应链表循环取出chunk分配成功则直接返回true
> 

```java
	if (q050.allocate(buf, reqCapacity, normCapacity) || q025.allocate(buf, reqCapacity, normCapacity) ||
            q000.allocate(buf, reqCapacity, normCapacity) || qInit.allocate(buf, reqCapacity, normCapacity) ||
            q075.allocate(buf, reqCapacity, normCapacity)) {
            return;
        }
```

- 5个链表都没能分配成功

> **此时就要开启一块新的chunk内存了，然后进行分配，分配成功后加入对应的list**
> 

### 4.3 PoolArena内存释放

- 非内存池（缓冲池）的内存释放

> 直接调用destroyChunk方法释放物理内存就好
> 
- 内存池的内存释放

> • 先尝试放入线程本地缓存然后释放
• **没有成功放入则调用freeChunk直接释放chunk（根据源码可以看到分配和释放都要加锁对Arena），然后调用poolChunkList的free方法看被回收chunk在对应链表的对应位置并调用remove将chunk回收，==若内存没有被再分配完全闲置或list是q000则直接销毁（物理释放）==**
> 

### 4.4 本地缓存PoolThreadCache

- 概述

> 每个线程的本地缓存内部其实是有多个MemoryRegionCache，每种类型的内存都有一个MemoryRegionCache数组与之对应，MemoryRegionCache中有个队列，这个队列主要是用来存放内存对象的
> 

### 4.5 Netty内存分配时序图

1. 在应用Netty时，通过默认设 置PooledByteBufAllocator执行ByteBuf的分配。
2. 当用NioByteUnsafe的 read() 方 法 读 取 NioSocketChannel 数 据 时 ，
3. 需 要 调 用PooledByteBufAllocator去分配内存，
4. 具体分配多少内存，由Handle的guess()方法决定，此方法只预测所需的缓冲区的大小，不进行实际 的 分 配 。
5. PooledByteBufAllocator 从 PoolThreadLocalCache 中 获 取
PoolArena，
6. 最终的内存分配工作由PoolArena完成。

![image.png](Netty%20%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86/image%209.png)

### 4.6 RecvByteBufAllocator内存分配计算

- 概述

> 前面我们深入底层聊到内存分配，但是当channel中来数据我们应该分配多少内存去读合适呢？例如来了1KB的数据，**我们应该是分配8KB（大于512小于8192，则从512成倍上涨）还是分配16B（tiny最开始的初始值）内存去读取呢？**
> 
> - 前者会造成浪费
> - 后者会拖慢性能
- 再议NioEventLoop线程处理OP_READ事件

> 在Netty中一般是由两个类来处理内存的分配的：
①.PooledByteBufAllocator默认实现类ByteBufAllocator；
②.AdaptiveRecvByteBufAllocator的默认实现类RecvByteBufAllocator
> 

> **在管道的默认配置中，前者主要处理内存的分配，而后者主要计算每次读循环时应该分配多少内存（NioByteUnsafe之所以需要循环读取，主 要是因为分配的初始ByteBuf不一定能够容纳读取到的所有数据。）**
> 
- 循环读过程解读以及调整缓冲区

> 在读取channel方法中，会调用该类的handle来计算分配的内存，并且还会记录本次实际读到数据的大小，优化预测下一次内存分配的大小，从而实现自动的增加或者减少：**如果上一次缓冲区被填满了，那么预测的字节数变大；反之如果连续两次都没有填满已分配的缓冲区，那么预测字节数就会变小**
> 

> 上述实现的底层就是靠`maxIndex、minIndex以及decreaseNow`这三个属性判断下次缓冲区是否需要增加或者减少
> 
- SIZE_TABLE 数组

> 该数组就是本类记录不同的内存块大小，按照分配需求找到合适的内存块（**集体查找就是根据size然后调用getSizeTableIndex方法，采用二分查找，找到相匹配合适的**），数组中的数值都是**2的次幂方**便好找，当需要内存小增幅不大，反之则增幅很大，所以你看
> 
> - **16到512，每次都是16递增**
> - **512往上都是成倍递增直到int的最大值**
- 调整缓冲区（record方法）详解

> 在分配器中的计算机handle实现中有上面我们提到的三种属性，步骤如下
> 
> 1. **如果实际使用字节数小于缓冲区的容量，判断decreaseNow（默认为false）是否连续两次都为true，这说明下次分配需要减小；第一次小于则将该标志位置为true**
> 2. **如果实际大于缓冲区容量，将index下标`+4`，设置nextReceiveBufferSize下次分配内存数，例如当前缓存为512，下次则变成`512*2的四次方`即设置为该值，并将decreaseNow置为false**
> 3. **每次读取结束都会通过readComplete方法调用record方法的**