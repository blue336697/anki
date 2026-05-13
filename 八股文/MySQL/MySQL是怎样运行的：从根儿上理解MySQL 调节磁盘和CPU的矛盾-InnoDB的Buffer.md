# MySQL是怎样运行的：从根儿上理解MySQL|调节磁盘和CPU的矛盾-InnoDB的Buffer Pool

type: Post
status: Published
date: 2022/03/15
slug: example-4
summary: InnoDB 存储引擎在处理客户端的请求时，当需要访问某个页的数据时，就会把完整的页的数据全部加载到内存中，也就是说即使我们只需要访问一个页的一条记录，那也需要先把整个页的数据加载到内存中。将整个页加载到内存中后就可以进行读写访问了，在进行完读写访问之后并不着急把该页对应的内存空间释放掉，而是将其 缓存 起来，这样将来有请求再次访问该页面时，就可以省去磁盘 IO 的开销了。
tags: Mysql
category: 数据库

# 前言：本博文是对MySQL是怎样运行的：从根儿上理解MySQL这本书的归纳和总结

# 18.调节磁盘和CPU的矛盾-InnoDB的Buffer Pool

## 1.缓存的重要性

- 概述

> InnoDB 存储引擎在处理客户端的请求时，当需要访问某个页的数据时，就会把完整的页的数据全部加载到内存中，也就是说即使我们只需要访问一个页的一条记录，那也需要先把整个页的数据加载到内存中。将整个页加载到内存中后就可以进行读写访问了，在进行完读写访问之后并不着急把该页对应的内存空间释放掉，而是将其 缓存 起来，这样将来有请求再次访问该页面时，就可以省去磁盘 IO 的开销了。
> 

## 2.InnoDB的Buffer Pool

### 2.1 啥是个Buffer Pool

- 概述

> 设计 InnoDB 的大叔为了缓存磁盘中的页，在 MySQL 服务器启动的时候就向操作系统申请了一片连续的内存，他们给这片内存起了个名，叫做 Buffer Pool （中文名是 缓冲池 ）。
> 
- buffer中页面组成

> 在缓冲池中会有大致三种类型：空闲页、未同步的脏页、同步的脏页（干净页），脏页下面会详解哦
> 
- 大小设置

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image.png)

> 默认有128M的大小，最小值为5M（当设置小于5M时会自动设置为5M）
> 

### 2.2 Buffer Pool内部组成

- 概述

> 缓存页的大小与数据页一样为16kb，每个缓存页对应一个控制信息（控制块），这些控制信息包括该页所属的表空间编号、页号、缓存页在 Buffer Pool 中的地址、链表节点信息、一些锁信息以及 LSN 信息。控制块集中存放在缓冲池的前面，而缓存页集中存放在缓冲池的后面
> 
- 大致结构如下

> 在操作系统这门课中，CPU根据不同的调度算法来进行内存的分配，而不同的调度算法都会产生相对应的内部碎片或者外部碎片
> 

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image%201.png)

- 小贴士

> 每个控制块大约占用缓存页大小的5%，在MySQL5.7.21这个版本中，每个控制块占用的大小是808字节。而我们设置的innodb_buffer_pool_size并不包含这部分控制块占用的内存空间大小，也就是说InnoDB在为Buffer Pool向操作系统申请连续的内存空间时，这片连续的内存空间一般会比innodb_buffer_pool_size的值大5%左右。
> 

### 2.3 free链表的管理

- 概述

> 在对于缓冲池初始化后，里面是没有磁盘页的，那么随着语句的执行源源不断的磁盘页加入进来，那么我们遇到新加入的磁盘页应该加入到池子里的那个地方呢，那些地方是已经使用过的、那些地方是没有使用的。这时我们会将空闲的缓存页对应的控制块通过链表连接起来，这称为free链表，使用了就从链表中剔除就好
> 
- 结构如下

> 假设缓冲池的最大缓存页容量为n，可以看到不论是分页还是什么，只要有链表
> 
> 
> **几乎**
> 

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image%202.png)

- 小贴士

> mysql中会有很多类似的链表都有基节点，所在内存大概在40字节左右，并不包含在为Buffer Pool申请的一大片连续内存空间之内。
> 

### 2.4 缓存页的哈希处理

- 概述

> 当新加入的磁盘页进入到缓冲池时，我们怎么判断这个磁盘页是否被二次缓冲了，又或者我们怎么知道该页在不在缓冲池中呢？此时回想以前，我们是根据表空间号+页号来快速定位到一个页的，那么此时为了实现一一对应的关系，我们引入一个哈希表，key是表空间号 + 页号，value是缓存页。那么找到是一种路，找不到又是一种路喽
> 

### 2.5 flush链表的管理（连接脏页的链表）

- 概述

> 此链表是为了解决当我们修改了缓存页的数据那么我们怎么该与磁盘页进行同步呢，如果修改的第一时间就同步的化那么对于频繁的操作是很耗资源的，所以会在统一的时间进行同步。此时问题来了我们怎么知道那些缓存页是做过修改的，所以使用一个链表来连接这些做过修改的缓存页
> 
- 结构与free链表一致

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image%203.png)

### 2.6 LRU（Least Recently Used）链表的管理

### 2.6.1 缓存不够的窘境

- 概述

> 此时我们需要很多很多链表，需要很多很多缓存页来提高性能，就会出现内存凭借，在计算机组成原理与操作系统中，我们得知虚拟内存和进程调度以及分页替换等，这些的核心思想就是替换，那么对于缓存我们也可以通过一定的替换算法进行一定程度的瘦身
> 

### 2.6.2 简单的LRU链表

- 概述

> 如果出现缓存池没有空闲的缓存页给新的磁盘页时，此时会采用淘汰掉部分最近很少使用（LRU）的缓存页，那么我们怎么知道缓存页最近使用了没使用呢，此时LRU链表应运而生，根据最近使用了与否调成到该链表的头部，那么尾部自然而然就是最近没有使用的缓存页了
> 

### 2.6.3 划分区域的LRU链表

- 概述

> 根据上一节的标题你可以看到简单的，也就是说不够完全满足我们的需求，会出现以下几种缺陷情况
> 
1. 情况一

> InnoDB提供了一种提前加载页的方式称为：“预读”，预读又分为线性预读和随机预读；
> 
> - 线性预读：设计 InnoDB 的大叔提供了一个系统变量 `innodb_read_ahead_threshold` ，如果顺序访问了某个区`（ extent ）`的页面超过这个系统变量的值，就会触发一次 异步 读取下一个区中全部的页面到`BufferPool`的请求，注意 异步 读取意味着从磁盘中加载这些被预读的页面并不会影响到当前工作线程的正常执行。这个 `innodb_read_ahead_threshold` 系统变量的值默认是 56 ，我们可以在服务器启动时通过启动参数或者服务器运行过程中直接调整该系统变量的值，不过它是一个全局变量，注意使用 `SET GLOBAL` 命令来修改哦
> - 随机预读：如果 `Buffer Pool` 中已经缓存了某个区的13个连续的页面，不论这些页面是不是顺序读取的，都会触发一次 异步 读取本区中所有其的页面到 `Buffer Pool` 的请求。设计 InnoDB 的大叔同时提供了`innodb_random_read_ahead` 系统变量，它的默认值为 `OFF` ，也就意味着 InnoDB 并不会默认开启随机预读的功能，如果我们想开启该功能，可以通过修改启动参数或者直接使用 SET GLOBAL 命令把该变量的值设置为 `ON` 。

> 总结：其实无论是线性预读还是随机预读，都不重要，你需要知道的是每次的预读都会将预读的页放到LRU链表的头部，那么如果出现预读的页从没使用并且缓冲池的也不是很大的时候，会导致尾部的缓存页频繁的淘汰，使命中率下降
> 
1. 情况二

> 当遇到全表扫描的情况就很无语了，意味着LRU链表在一直换血换阵容，同样也会大大影响命中率
> 
- 应对方式

> InnoDB为了解决这种情况会将LRU划分为两个区域：
> 
> - 一部分存储使用频率非常高的缓存页，所以这一部分链表也叫做 `热数据` ，或者称 `young区域` 。
> - 另一部分存储使用频率不是很高的缓存页，所以这一部分链表也叫做 `冷数据` ，或者称 `old区域` 。
- 区域结构图，young在前，old在后

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image%204.png)

- 注意

> 我们是按照某个比例将LRU链表分成两半的，不是某些节点固定是young区域的，某些节点固定是old区域的，随着程序的运行，某个节点所属的区域也可能发生变化
> 
- 比例设置

> 我们可以通过查看系统变量 `innodb_old_blocks_pct` 的值来确定 old 区域在 LRU链表 中所占的比例，并且可以在配置文件或修改全局变量两种方式进行修改
> 

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image%205.png)

- 针对两种情况的优化

> 对于预读页面可能不进行后续访问的优化：会将首次在缓冲池出现的磁盘页放到old链表的头部，从而不影响young区经常访问的页对于全表扫描：当进行此操作时，平均到每个页的访问时间肯定是非常小的，由于有上一种的优化规则，所以我们额外维护一个变量来记录通常缓存页被访问时间与上次访问时间的间隔，当这个间隔很小的很小的时候意味着我们不需要将这个页从old区移动到young区，如果大于这个间隔则会被放到young的头部。同样可以对这个变量进行修改
> 

### 2.6.4 更进一步优化LRU链表

- 概述

> 对于young区来说，频繁的移动缓存页也会造成不必要的资源浪费，所以当被使用的缓存页处于young链表长度的1/4的后边时，那么就会被移动到表头
> 
- 总结

> 优化这些的目的就是尽量高效的提高 Buffer Pool 的缓存命中率。
> 

### 2.7 其他的一些链表

> 为了更好的管理 Buffer Pool 中的缓存页，除了我们上边提到的一些措施，设计 InnoDB 的大叔们还引进了其他的一些 链表 ，比如 unzip LRU链表 用于管理解压页， zip clean链表 用于管理没有被解压的压缩页， zip free数组 中每一个元素都代表一个链表，它们组成所谓的 伙伴系统 来为压缩页提供内存空间等等，反正是为了更好的管理这个 Buffer Pool 引入了各种链表或其他数据结构
> 

### 2.8 刷新脏页到磁盘

- 从 LRU链表 的冷数据中刷新一部分页面到磁盘

> 后台线程会定时从 LRU链表 尾部开始扫描一些页面，扫描的页面数量可以通过系统变量innodb_lru_scan_depth 来指定，如果从里边儿发现脏页，会把它们刷新到磁盘。这种刷新页面的方式被称之为 BUF_FLUSH_LRU 。
> 
- 从 flush链表 中刷新一部分页面到磁盘

> 后台线程也会定时从 flush链表 中刷新一部分页面到磁盘，刷新的速率取决于当时系统是不是很繁忙。这种刷新页面的方式被称之为BUF_FLUSH_LIST 。
> 
- 其他情况：

> 当处理脏页的进程较慢，用户加载磁盘页时没有free的缓存页，会将LRU的最后一个缓存页进行刷新，这种刷新单个页面到磁盘中的刷新方式被称之为 BUF_FLUSH_SINGLE_PAGE 。当然，有时候系统特别繁忙时，也可能出现用户线程批量的从 flush链表 中刷新脏页的情况，很显然在处理用户请求过程中去刷新脏页是一种严重降低处理速度的行为（毕竟磁盘的速度满的要死），这属于一种迫不得已的情况
> 

### 2.8.1 两种脏页到磁盘的情况会十分影响效率

- `redo log 写满了，要 flush 脏页`，这种情况是 InnoDB 要尽量避免的。因为出现这种情况的时候，整个系统就不能再接受更新了，所有的更新都必须堵住。如果你从监控上看，这时候更新数会跌为 0。
- `内存不够用了，要先将脏页写到磁盘`，这种情况其实是常态。此时如果查询的记录大多都是脏页的记录你会发现速度会非常慢

> 这种就是上面介绍的LRU链表和flush链表刷新的常态
> 

### 2.8.2 InnoDB 刷脏页的控制策略

- 刷新脏页速度的控制

> 你可以通过合理正确的设置参数 innodb_io_capacity，来告诉存储引擎你的io能力有多厉害，如果设置错误，系统会认为当前系统性能很差，导致脏页累计
> 
- 为什么需要控制速度

> 上面这个参数表示的是全力刷新脏页的速度，但总不能一直保持这个速度把，毕竟如果全部资源都用来刷新脏页，那磁盘别的功能还做不做了，所以InnoDB会参考==脏页比例和redo日志的写入速度==来控制刷新速度，根据这两个因素存储引擎会得到两个不同的数字大小
> 
- 根据脏页比例

> 参数 innodb_max_dirty_pages_pct 是脏页比例上限，默认值是 75%。InnoDB 会根据当前的脏页比例（脏页比例是用脏页的数量除全部缓冲池的页面数量）（假设为 M），根据一定的公式F1(M)算出一个范围在 0 到 100 之间的数字
> 
- redo日志写入速度的计算

> InnoDB 每次写入的日志都有一个序号，当前写入的序号跟 checkpoint 对应的序号之间的差值，我们假设为 N。InnoDB 会根据这个 N 算出一个范围在 0 到 100 之间的数字，这个计算公式可以记为 F2(N)。F2(N) 算法比较复杂，你只要知道 N 越大，算出来的值越大就好了。
> 
- 得出刷新速度

> 根据上述算得的 F1(M) 和 F2(N) 两个值，取其中较大的值记为 R，之后引擎就可以按照 innodb_io_capacity 定义的能力乘以 R% 来控制刷脏页的速度
> 

### 2.8.2 InnoDB 刷新脏页的有趣策略--》连坐

- 概述

> 当你要查询的记录在脏页中时，存储引擎会将该脏页进行同步，反映到你的查询速度就是变慢了，注意如果需同步的脏页旁边的数据页也是脏页，InnoDB会连带这一起刷新，如果一片全是脏页那就很影响效率
> 
- 连坐触发的控制参数

> 在 InnoDB 中，innodb_flush_neighbors 参数就是用来控制这个行为的，值为 1 的时候会有上述的“连坐”机制，值为 0 时表示不找邻居，自己刷自己的。
> 
- 优化方向

> 当在SSD还未普及的时候，这种连坐会大大节省随机IO，从而提高系统效率，但现在SSD普及了，读写速度（IOPS）上去了，提示这个脏页刷新的瓶颈而是单次刷新的数量必须尽量少，减少连带关系，所以MySQL8.0将该参数设置为了0
> 

### 2.9 多个Buffer Pool实例

- 概述

> 当缓冲池特别大，并且要提供高并发的访问需求同时还要满足同步问题（锁），这时一个缓冲池就会拖慢速度。会将这一个缓冲池进行拆分，每个都是独立的缓冲池称为缓冲池实例，独立申请内存空间，独立的各种链表，以提高高并发的能力，同样可以设置 innodb_buffer_pool_instances 的值来修改 Buffer Pool 实例的个数
> 
- 结构图

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image%206.png)

- 实例大小计算

> innodb_buffer_pool_size/innodb_buffer_pool_instances，也就是总共的大小除以实例的个数，结果就是每个 Buffer Pool 实例占用的大小
> 
- 总结

> 当然也不是越多越好，当innodb_buffer_pool_size的值小于1G的时候设置多个实例是无效的，InnoDB会默认把innodb_buffer_pool_instances 的值修改为1。而我们鼓励在Buffer Pool大小或等于1G的时候设置多个Buffer Pool实例。
> 

### 2.10 innodb_buffer_pool_chunk（大块）_size

- 概述

> 在 5.7.5版本及以后，支持我们能在服务器运行中调整缓冲池的大小，那么如果进行此操作，也就意味着我们需要将原先缓冲池的一丝一毫全部都复制到新申请的一片连续的内存中，这是非常消耗资源的，此时mysql引入新的划分单位：chunk，在缓冲池中是由一个一个chunk组成的，并且申请内存空间也是根据chunk来申请大小的
> 
- 结构图

![image.png](MySQL%E6%98%AF%E6%80%8E%E6%A0%B7%E8%BF%90%E8%A1%8C%E7%9A%84%EF%BC%9A%E4%BB%8E%E6%A0%B9%E5%84%BF%E4%B8%8A%E7%90%86%E8%A7%A3MySQL%20%E8%B0%83%E8%8A%82%E7%A3%81%E7%9B%98%E5%92%8CCPU%E7%9A%84%E7%9F%9B%E7%9B%BE-InnoDB%E7%9A%84Buffer%20/image%207.png)

- 总结

> 所以在运行时调整缓冲池的大小，是以chunk为单位来增删的，它的默认值是 134217728 ，也就是 128M 。不过需要注意的是，innodb_buffer_pool_chunk_size的值只能在服务器启动时指定，在服务器运行过程中是不可以修改的，之所以不能修改是因为虽然单位化小，但同样要进行复制移动的耗时操作啊！
> 

### 2.11 配置Buffer Pool时的注意事项

- 涉及的变量：
`innodb_buffer_pool_size`：缓冲池大小
`innodb_buffer_pool_chunk_size`：chunk大小
`innodb_buffer_pool_instances`：缓冲池实例数量
1. `innodb_buffer_pool_size` 必须是 `innodb_buffer_pool_chunk_size × innodb_buffer_pool_instances` 的倍数（这主要是想保证每一个 Buffer Pool 实例中包含的 chunk 数量相同）。
2. 如果我们指定的 `innodb_buffer_pool_size` 大于 2G 并且不是 2G 的整数倍，那么服务器会自动的把`innodb_buffer_pool_size` 的值调整为 2G 的整数倍
3. 如果在服务器启动时， `innodb_buffer_pool_chunk_size × innodb_buffer_pool_instances` 的值已经大于 `innodb_buffer_pool_size` 的值，那么 `innodb_buffer_pool_chunk_size` 的值会被服务器自动设置为`innodb_buffer_pool_size / innodb_buffer_pool_instances` 的值。

### 2.12 查看Buffer Pool的状态信息

```sql
mysql> SHOW ENGINE INNODB STATUS\\G
(...省略前边的许多状态)
----------------------
BUFFER POOL AND MEMORY
----------------------
Total memory allocated 13218349056;
Dictionary memory allocated 4014231
Buffer pool size 786432
Free buffers 8174
Database pages 710576
Old database pages 262143
Modified db pages 124941
Pending reads 0
Pending writes: LRU 0, flush list 0, single page 0
Pages made young 6195930012, not young 78247510485
108.18 youngs/s, 226.15 non-youngs/s
Pages read 2748866728, created 29217873, written 4845680877
160.77 reads/s, 3.80 creates/s, 190.16 writes/s
Buffer pool hit rate 956 / 1000, young-making rate 30 / 1000 not 605 / 1000
Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
LRU len: 710576, unzip_LRU len: 118
I/O sum[134264]:cur[144], unzip sum[16]:cur[0]
--------------
(...省略后边的许多状态)
mysql>

```

- Total memory allocated ：代表 Buffer Pool 向操作系统申请的连续内存空间大小，包括全部控制块、缓存页、以及碎片的大小。
- Dictionary memory allocated ：为数据字典信息分配的内存空间大小，注意这个内存空间和 Buffer Pool没啥关系，不包括在 Total memory allocated 中。
- Buffer pool size ：代表该 Buffer Pool 可以容纳多少缓存 页 ，注意，单位是 页 ！
- Free buffers ：代表当前 Buffer Pool 还有多少空闲缓存页，也就是 free链表 中还有多少个节点。
- Database pages ：代表 LRU 链表中的页的数量，包含 young 和 old 两个区域的节点数量。
- Old database pages ：代表 LRU 链表 old 区域的节点数量。
- Modified db pages ：代表脏页数量，也就是 flush链表 中节点的数量。
- Pending reads ：正在等待从磁盘上加载到 Buffer Pool 中的页面数量。当准备从磁盘中加载某个页面时，会先为这个页面在 Buffer Pool 中分配一个缓存页以及它对应的控制块，然后把这个控制块添加到 LRU 的 old 区域的头部，但是这个时候真正的磁盘页并没有被加载进来， Pending reads 的值会跟着加1。
- Pending writes LRU ：即将从 LRU 链表中刷新到磁盘中的页面数量。
- Pending writes flush list ：即将从 flush 链表中刷新到磁盘中的页面数量。
- Pending writes single page ：即将以单个页面的形式刷新到磁盘中的页面数量。
- Pages made young ：代表 LRU 链表中曾经从 old 区域移动到 young 区域头部的节点数量。这里需要注意，一个节点每次只有从 old 区域移动到 young 区域头部时才会将 Pages made young 的值加1，也就是说如果该节点本来就在 young 区域，由于它符合在 young 区域1/4后边的要求，下一次访问这个页面时也会将它移动到 young 区域头部，但这个过程并不会导致 Pages made young 的值加1。
- Page made not young ：在将 innodb_old_blocks_time 设置的值大于0时，首次访问或者后续访问某个处在 old 区域的节点时由于不符合时间间隔的限制而不能将其移动到 young 区域头部时， Page made not young 的值会加1。这里需要注意，对于处在 young 区域的节点，如果由于它在 young 区域的1/4处而导致它没有被移动到young 区域头部，这样的访问并不会将 Page made not young 的值加1。
- youngs/s ：代表每秒从 old 区域被移动到 young 区域头部的节点数量。
- non-youngs/s ：代表每秒由于不满足时间限制而不能从 old 区域移动到 young 区域头部的节点数量。
- Pages read 、 created 、 written ：代表读取，创建，写入了多少页。后边跟着读取、创建、写入的速率。
- Buffer pool hit rate ：表示在过去某段时间，平均访问1000次页面，有多少次该页面已经被缓存到Buffer Pool 了。
- young-making rate ：表示在过去某段时间，平均访问1000次页面，有多少次访问使页面移动到 young 区域的头部了。需要大家注意的一点是，这里统计的将页面移动到 young 区域的头部次数不仅仅包含从 old 区域移动到young 区域头部的次数，还包括从 young 区域移动到 young 区域头部的次数（访问某个 young 区域的节点，只要该节点在 young 区域的1/4处往后，就会把它移动到 young 区域的头部）。
- not (young-making rate) ：表示在过去某段时间，平均访问1000次页面，有多少次访问没有使页面移动到 young 区域的头部。需要大家注意的一点是，这里统计的没有将页面移动到 young 区域的头部次数不仅仅包含因为设置了innodb_old_blocks_time 系统变量而导致访问了 old 区域中的节点但没把它们移动到 young 区域的次数，还包含因为该节点在 young 区域的前1/4处而没有被移动到 young 区域头部的次数。
- LRU len ：代表 LRU链表 中节点的数量。
- unzip_LRU ：代表 unzip_LRU链表 中节点的数量（由于我们没有具体唠叨过这个链表，现在可以忽略它的值）。
- I/O sum ：最近50s读取磁盘页的总数。
- I/O cur ：现在正在读取的磁盘页数量。
- I/O unzip sum ：最近50s解压的页面数量。
- I/O unzip cur ：正在解压的页面数量

## 3.总结

1. 磁盘太慢，用内存作为缓存很有必要。
2. `Buffer Pool` 本质上是 InnoDB 向操作系统申请的一段连续的内存空间，可以通过
`innodb_buffer_pool_size` 来调整它的大小。
3. `Buffer Pool` 向操作系统申请的连续内存由控制块和缓存页组成，每个控制块和缓存页都是一一对应的，在填充足够多的控制块和缓存页的组合后， `Buffer Pool` 剩余的空间可能产生不够填充一组控制块和缓存页，这部分空间不能被使用，也被称为 碎片 。
4. InnoDB 使用了许多 链表 来管理 Buffer Pool 。
5. free链表 中每一个节点都代表一个空闲的缓存页，在将磁盘中的页加载到 Buffer Pool 时，会从 free链表 中寻找空闲的缓存页。
6. 为了快速定位某个页是否被加载到 `Buffer Pool` ，使用 `表空间号 + 页号` 作为 key ，缓存页作为 value ，建立哈希表。
7. 在 `Buffer Pool` 中被修改的页称为 `脏页` ，脏页并不是立即刷新，而是被加入到 `flush`链表 中，待之后的某个时刻同步到磁盘上。
8. LRU链表 分为`young 和 old`两个区域，可以通过`innodb_old_blocks_pct`来调节 old 区域所占的比例。首次从磁盘上加载到 Buffer Pool 的页会被放到 old 区域的头部，在 `innodb_old_blocks_time` 间隔时间内访问该页不会把它移动到 `young` 区域头部。在 `Buffer Pool` 没有可用的空闲缓存页时，会首先淘汰掉 old 区域的一些页。
9. 我们可以通过指定 `innodb_buffer_pool_instances` 来控制 Buffer Pool 实例的个数，每个 `Buffer Pool` 实例中都有各自独立的链表，互不干扰。
10. 自 `MySQL 5.7.5` 版本之后，可以在服务器运行过程中调整 Buffer Pool 大小。每个 `Buffer Pool` 实例由若干个`chunk`组成，每个 `chunk` 的大小可以在服务器启动时通过启动参数调整。
11. 可以用下边的命令查看 Buffer Pool 的状态信息：`SHOW ENGINE INNODB STATUS\\G`

## 4.change buffer

- 概述

> 当需要更新一个数据页时，如果数据页在内存中就直接更新，而如果这个数据页还没有在内存中的话，在不影响数据一致性的前提下，InnoDB 会将这些更新操作缓存在 change buffer 中，这样就不需要从磁盘中读入这个数据页了。在下次查询需要访问这个数据页的时候，将数据页读入内存，然后执行 change buffer 中与这个页有关的操作。通过这种方式就能保证这个数据逻辑的正确性
> 
- buffer大小的设置

> change buffer 用的是 buffer pool 里的内存，因此不能无限增大。change buffer 的大小，可以通过参数 innodb_change_buffer_max_size来动态设置。这个参数设置为 50 的时候，表示 change buffer 的大小最多只能占用 buffer pool 的 50%。
> 
- 操作具有持久化

> change buffer可以看成也是一个数据页，需要被持久化到 系统表空间（ibdata1），以及把这个change buffer页的改动记录在redo log里，事后刷进系统表空间（ibdata1）。
> 
- merge

> 将change buffer中的操作应用到原数据页，得到最新结果的过程称为 merge。除了访问这个数据页会触发merge外，系统有后台线程会定期 merge。在数据库正常关闭（shutdown）的过程中，也会执行 merge 操作。
> 

### 4.1 change buffer的适用场景

- 好处

> 显然，如果能够将更新操作先记录在 change buffer，减少读磁盘，语句的执行速度会得到明显的提升。而且，数据读入内存是需要占用 buffer pool 的，所以这种方式还能够避免占用内存，提高内存利用率。但注意这种好处只会在当前更新的目标页不在内存中，且你使用的是普通索引（因为唯一索引会将不存在的页从磁盘读到内存），而普通索引就会使用这个changebuffer
> 
- 适用场景

> 我们知道对应merge发生时候就会对数据真正更新的时候，那么对于buffer中如果存在大量的记录，此次的merge收益会十分大，但如果更新完（写入buffer的记录很少）需要立即访问，此时就会触发merge，这样随机IO并有减少反而增加了维护成文，所以可以看到buffer适用于写多读少的场景
> 
- 注意

> 这个buffer主要是针对二级索引的，上面说的数据页，指的是二级索引树的数据页，并不是聚簇索引即主键树的数据页。 如涉及到索引字段的更新，也是要更新对应的索引数据的，而索引树对应的数据页不在内存中，则changeBuffer会先保存这个数据，之后会和对应的数据页进行merge过程。 redoLog也是会记录这一动作的，所以更新对应索引树的数据不会丢失。
> 
- 解释（是在更新操作的前提下）

> 为什么说这个buffer是针对二级索引的，因为索引是针对与对应索引列的检索效率提升，对于持久化肯定是根据每个表的主键的聚簇索引来顺序插入IO，那么这样对于二级索引这种辅助索引来说，根据索引列建立的B+数相对于主键的B+在磁盘上就会是随机IO，所以会对IO性能造成影响，于是乎change buffer营运而生，其实主要就是针对插入一条数据之后，对辅助索引的磁盘随机IO效率的优化
> 

### 4.2 唯一索引和普通索引该选哪个呢

- 概述

> 其实，这两类索引在查询能力上是没差别的，主要考虑的是对更新性能的影响。
> 

> 所以，我建议你尽量选择普通索引。如果所有的更新后面，都马上伴随着对这个记录的查询，那么你应该关闭 change buffer。而在其他情况下，change buffer 都能提升更新性能。
> 
- 实际效果

> 在实际使用中，你会发现，普通索引和 change buffer 的配合使用，对于数据量大的表的更新优化还是很明显的。特别地，在使用机械硬盘时，change buffer 这个机制的收效是非常显著的。所以，当你有一个类似“历史数据”的库，并且出于成本考虑用的是机械硬盘时，那你应该特别关注这些表里的索引，尽量使用普通索引，然后把 change buffer 尽量开大，以确保这个“历史数据”表的数据写入速度。
>