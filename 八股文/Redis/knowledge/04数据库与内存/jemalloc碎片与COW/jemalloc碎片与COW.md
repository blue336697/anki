# jemalloc碎片与COW

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-used与RSS

Q: used_memory、allocator_active、allocator_resident 和 RSS 为什么不同？

A:
- used_memory 主要是 Redis 已分配并计入的数据/结构；allocator_active 是分配器为对象激活的页，resident 是分配器驻留物理页。
- RSS 还包含代码、栈、共享库、页表及分配器外内存，通常大于 used_memory。
- 删除对象后内存可能回到 jemalloc arena 而未归还 OS，所以 used 下降而 RSS 高位维持。
- `mem_fragmentation_ratio=RSS/used` 在 used 很小时会失真，应看绝对字节和 allocator 指标。

## 02-碎片来源

Q: Redis 内存碎片主要从哪里来？

A:
- jemalloc size class 向上取整产生内部碎片；不同生命周期对象交错使页难以整体归还，形成外部碎片。
- 大量变长 value、编码转换、rehash 双表、客户端缓冲伸缩都会制造尺寸和生命周期差异。
- THP 可能放大 fork/COW 和延迟；操作系统页缓存与内核网络缓冲也不在简单 used_memory 中。
- 碎片不是 `MEMORY PURGE` 一次就必然消失，取决于空闲页能否被释放。

## 03-active-defrag

Q: active defrag 怎样整理内存，为什么会消耗 CPU？

A:
- Redis 检测高碎片后渐进扫描对象，把仍在使用的数据复制到更合适的分配块，再更新所有内部指针。
- 必须为不同编码实现可安全移动/修复指针的逻辑，不能让通用 allocator 自行搬对象。
- 工作按 CPU 百分比和阈值受控；提高 aggressiveness 能更快降碎片，但与请求争主线程 CPU。
- 开启前先确认使用支持的 jemalloc 构建和碎片确实是根因。

## 04-fork与COW

Q: fork 后什么操作会真正增加 COW 内存？

A:
- fork 初始只复制页表，父子共享物理页；任一进程写某页时内核复制该页。
- Redis 主进程持续写 key、更新对象 LRU/LFU 元数据、rehash 或碎片整理都可能弄脏页。
- 写入少量逻辑字节也可能复制整页；THP 下粒度可能更大，因此写流量与内存布局决定 COW 峰值。
- 子进程读全量数据还会争内存带宽和页缓存，RDB/AOF rewrite 不是“零成本后台任务”。

## 05-容量预算

Q: 有持久化时 maxmemory 应如何给 RSS 和 COW 留余量？

A:
- 不能把 maxmemory 配到容器/机器内存上限；需预留 allocator 碎片、客户端/复制缓冲、fork 页表和 COW 峰值。
- 写密集且数据集大时 COW 可显著，最可靠依据是历史 `rdb_last_cow_size/aof_last_cow_size` 加安全系数。
- 还要给 OS、监控 agent 和文件页缓存留空间，避免 swap 或 OOM kill。
- 容量模型应按峰值 value/连接/复制拓扑和持久化并发压测，而不是只用 key 数×平均 value。
