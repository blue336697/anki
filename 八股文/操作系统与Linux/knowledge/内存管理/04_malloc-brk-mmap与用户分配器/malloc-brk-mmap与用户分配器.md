# malloc、brk、mmap 与用户态内存分配器

> 基线：`malloc/free` 是 libc/分配器 API，不是系统调用。以下 ptmalloc、arena、tcache 属于常见 glibc 实现，jemalloc/tcmalloc 等结构不同。

## 01-分层关系
Q: 应用调用 `malloc` 后，用户分配器和内核分别负责什么？
A:
- 用户分配器管理进程已经取得的虚拟内存块，完成切分、合并、缓存和并发控制。
- 当现有 heap/arena 不足时，分配器通过 brk 或 mmap 向内核申请新的虚拟地址范围。
- 内核创建/调整 VMA，物理页通常在首次访问缺页时才按需分配。
- free 先把块归还分配器，是否 munmap 或缩小 brk 取决于块位置、大小、碎片和实现策略。

## 02-brk堆
Q: brk 模型怎样扩展传统进程 heap？
A:
- 进程有 program break，brk/sbrk 调整数据段末端，扩大时形成连续虚拟堆区。
- 分配器从堆顶取得大块再切分给小请求，顶部连续空闲时才容易把 break 向下收缩归还内核。
- 堆中间释放的洞仍可复用，但不能直接解除中间页映射，否则会破坏单一连续区。
- ASLR、线程分配和现代分配器使“所有 malloc 都只来自堆顶”成为过时简化。

## 03-mmap大块
Q: 为什么大块分配常使用匿名 mmap？
A:
- mmap 可创建独立 VMA，释放整个映射时 munmap 能直接归还地址空间和物理页，不受堆顶位置限制。
- 大块映射避免把主 heap 切碎，但增加 VMA 数、页表、系统调用和 TLB 管理成本。
- 分配器使用 mmap 的阈值会动态或按配置变化，不应背一个固定 128 KiB 作为所有环境真相。
- 地址空间释放不保证物理内存立刻从所有统计消失，仍可能有内核延迟和共享/锁页影响。

## 04-chunk与bin
Q: glibc ptmalloc 如何组织已经取得的内存？
A:
- 用户指针前后通常有 chunk metadata，保存大小、前块状态等，用于边界定位和合并。
- 不同大小和状态的空闲块进入 fastbin、small/large bin、unsorted bin 等结构，按策略快速复用。
- 相邻空闲 chunk 可合并降低外部碎片，但 fastbin/tcache 为速度可能延迟合并。
- 元数据位于进程可写内存附近，越界写可能破坏 allocator 状态并形成安全漏洞。

## 05-tcache
Q: tcache 为什么快，又带来什么代价？
A:
- 每线程缓存少量各尺寸空闲 chunk，malloc/free 常可在本线程链表完成，不访问 arena 全局锁。
- 高频小对象吞吐提高，但空闲内存分散在多个线程缓存中，其他线程或系统暂时不能直接复用。
- 线程数量多、尺寸类别多时，缓存会增加进程 RSS 与碎片；线程退出或阈值触发才归并一部分。
- tcache 结构和安全检查随 glibc 版本变化，面试应讲 per-thread cache 思想而非背字段偏移。

## 06-arena
Q: 多线程程序为什么会有多个 arena？
A:
- 单一 heap 锁会让并发 malloc/free 串行，ptmalloc 为线程分配或复用多个 arena 降低锁竞争。
- 每个 arena 管理自己的堆段和 bins；跨线程释放可把块还给所属 arena，仍需同步。
- arena 越多并发越好但内存碎片与保留越多，容器内可能出现业务对象不多但 RSS 偏高。
- 可通过分配器配置、线程数和替代 allocator 调整，不能把所有 RSS 增长直接判为泄漏。

## 07-free不降RSS
Q: `free()` 后 RSS 为什么经常不下降？
A:
- free 只保证对象不再属于调用者，块可能留在 tcache、arena bins 中等待未来复用。
- brk heap 中间的空闲页难以直接归还，只有顶部收缩或 madvise 丢弃整页才会减少驻留。
- 页面含有其他仍使用 chunk 时不能整体释放，内部/外部碎片使空闲字节不等于可还页。
- 区分泄漏与 allocator retained memory 要看堆 profile、活对象、匿名 RSS 和长期稳定性。

## 08-mmap语义
Q: mmap 的 `MAP_PRIVATE/SHARED` 与 `MAP_ANONYMOUS` 分别控制什么？
A:
- ANONYMOUS 表示没有普通文件后备，初始内容为零；文件映射则由 fd 和 offset 确定后备对象。
- PRIVATE 表示写时复制，修改不正常回写后备文件；SHARED 让多个映射共享 page cache 修改。
- `PROT_READ/WRITE/EXEC` 是页权限，是否允许组合还受打开模式、文件系统和安全策略限制。
- flag 控制映射语义，不等于物理页立即分配，也不保证共享写已经持久化。

## 09-madvise与回收
Q: 应用如何向内核表达内存访问和回收意图？
A:
- `madvise` 可提示顺序/随机访问、预取、无需当前页、大页倾向等，具体效果是策略提示而非绝对命令。
- `MADV_DONTNEED` 等操作可能丢弃私有匿名页内容或解除驻留，后续访问重新 fault，语义需按映射类型确认。
- 分配器可用 madvise 归还空闲整页而保留虚拟地址，RSS 下降但 VMA/VSZ 不一定变化。
- 过度主动回收会造成反复 fault 和清零，应用应依据工作集而非看到空闲就清。

## 10-诊断与正确性
Q: 怎样诊断“malloc 很多/内存不归还”，并纠正常见误区？
A:
- 用 `/proc/<pid>/smaps_rollup` 区分 anonymous/file RSS、PSS 和 swap，再用 heap profiler 判断活对象与分配调用栈。
- 比较 allocator allocated、active、resident/retained 等指标，确认是泄漏、碎片、线程缓存还是 page cache。
- “malloc 成功说明物理内存足够”错误；过量承诺和按需 fault 会把失败推迟。
- “free 必须立即把内存还给 OS”错误；API 只结束对象所有权，归还策略由分配器与整页可释放性决定。
