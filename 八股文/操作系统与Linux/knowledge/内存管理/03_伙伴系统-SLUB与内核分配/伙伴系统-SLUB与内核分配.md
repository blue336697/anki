# 伙伴系统、SLUB 与 Linux 内核内存分配

> 基线：伙伴系统管理页框块，SLUB 管理小内核对象；`kmalloc`、`vmalloc`、用户 malloc 分属不同层次。

## 01-物理内存模型
Q: Linux 如何从 NUMA node、zone 到 page 描述物理内存？
A:
- NUMA node 表示具有不同本地访问距离的内存节点；每个 node 内再按硬件寻址约束划分 zone。
- 内核用 `struct page`/folio 等元数据描述物理页状态、引用、映射、LRU 或 slab 归属。
- zone 维护空闲页、watermark 和伙伴 free_area，分配器优先按 GFP 允许的 node/zone 寻找。
- 物理地址连续、虚拟地址连续和 NUMA 本地是三个不同属性，分配 API 必须说明需要哪一种。

## 02-buddy阶
Q: 伙伴系统的 order 是什么？
A:
- order k 表示 `2^k` 个连续基础页组成的块；基础页若为 4 KiB，则 order 3 是 32 KiB。
- 每个 zone 的 free_area 按 order 维护空闲块集合，快速查找至少满足请求的连续页块。
- 分配较小 order 时可把更大块不断二分；释放时若同阶 buddy 空闲则合并到更高 order。
- buddy 地址可由块号按对应 order 翻转一位计算，这要求块按幂次对齐。

## 03-分裂与合并
Q: 伙伴系统怎样处理 order 2 请求而只有 order 5 空闲块？
A:
- 从 order 5 取一块，拆成两个 order 4，其中一半进入 order 4 空闲表。
- 继续拆所持一半为两个 order 3，再拆成两个 order 2，把每次未使用 buddy 放入对应 free_area。
- 释放 order 2 块时检查它的同阶 buddy；若同样空闲且可合并，则移除 buddy 并形成 order 3，递归向上。
- 合并只能恢复满足对齐的伙伴，散落已占用小页会造成高阶外部碎片。

## 04-PCP
Q: per-CPU page list 为什么能降低伙伴锁竞争？
A:
- order-0 等常用页分配若每次都操作 zone 共享 free_area，会在多核形成锁和 cache line 热点。
- 每 CPU 缓存一批页，本地快速分配与释放；达到高低水位时再批量向伙伴系统补充或归还。
- PCP 提升吞吐但使一部分空闲页暂存在各 CPU，本地数量与全局可用高阶块不是一回事。
- 内存压力、CPU offline 和 drain 操作会把 PCP 页回收到全局管理。

## 05-GFP标志
Q: GFP flags 为什么不仅表示“从哪里分配”？
A:
- 它同时约束可使用 zone、是否允许睡眠、直接回收、IO/文件系统递归、失败重试和紧急保留等行为。
- 进程上下文常可用可睡眠分配，硬中断/自旋锁区必须使用原子上下文允许的有限策略。
- 原子分配依赖预留和现有空闲页，不保证成功；调用方仍要处理 NULL 或使用预分配。
- 随意使用强制重试 flag 可能造成长停顿和系统级回收，不能只为“避免失败”。

## 06-Slab目的
Q: 已有伙伴系统，为什么还需要 slab/SLUB？
A:
- 内核频繁申请几十到几百字节对象，直接占用整页会产生巨大内部碎片。
- slab allocator 把页块切成同类型或同大小对象，缓存已构造对象并减少初始化成本。
- 专用 `kmem_cache` 还能设置对齐、构造和调试策略，适合 inode、dentry、task 等高频对象。
- 伙伴系统向 slab 提供页，slab 再向内核子系统提供对象，两层解决不同粒度问题。

## 07-SLUB结构
Q: SLUB 的快速分配路径大致怎样工作？
A:
- 每个 kmem_cache 按 node 管理 slab，并为 CPU 保留当前活跃 slab 与 freelist。
- 本 CPU 从 freelist 弹出对象通常无需全局锁；耗尽后再从 partial slab 或伙伴系统取得新 slab。
- 释放对象尽量回到相应 slab，跨 CPU free 需要安全更新 freelist，并可能把空 slab归还页分配器。
- 对象 metadata 可编码在空闲对象中，开启 redzone、poison、KASAN 等调试会改变布局和性能。

## 08-kmalloc与vmalloc
Q: `kmalloc` 和 `vmalloc` 的连续性有什么不同？
A:
- kmalloc 返回内核虚拟连续且通常物理连续的内存，小对象来自 slab，大块最终受伙伴高阶分配限制。
- vmalloc 只保证虚拟地址连续，可把分散物理页通过内核页表拼接，适合较大、不要求 DMA 物理连续的区域。
- vmalloc 需要建立页表、TLB 同步，访问局部性和分配释放开销通常高于 kmalloc。
- DMA 还要使用 DMA API 处理设备地址、IOMMU 和缓存一致性，不能简单把 kmalloc 地址交给设备。

## 09-碎片与compaction
Q: 系统明明有很多空闲内存，为什么高阶页分配仍会失败？
A:
- 空闲页可能被已分配页切碎，无法形成满足 order 的物理连续块，属于外部碎片。
- 内存 compaction 尝试迁移可移动页，把空闲页聚合到连续区域；不可移动页会阻断整理。
- THP、hugetlb、巨大 DMA buffer 和高阶网络缓冲更依赖连续页，可能触发直接 compaction 和延迟尖刺。
- `buddyinfo`、`pagetypeinfo`、compaction tracepoint 可判断问题，而不能只看 MemAvailable。

## 10-正确性审查
Q: 关于 Linux 内存分配器，哪些说法需要纠正？
A:
- “伙伴系统按字节分配任意大小内存”错误；它按 `2^order` 个页管理连续页块。
- “SLUB 替代了伙伴系统”错误；SLUB 的 slab 页面仍来自页分配器。
- “vmalloc 更容易分配所以总是更好”错误；它有页表、TLB、映射和访问开销且不物理连续。
- “空闲内存总量足够就不会分配失败”错误；zone、NUMA、GFP、上下文和高阶碎片都影响结果。
