# Page Fault、按需分页与 Copy-on-Write

> 基线：page fault 是地址翻译或权限异常的入口，不等于程序错误。只有无法按 VMA 语义修复时才向用户发送 SIGSEGV/SIGBUS。

## 01-fault类型
Q: 哪些访问会触发 page fault？
A:
- 虚拟地址存在合法 VMA 但 PTE 尚未建立，例如首次访问匿名内存或尚未读入的文件页。
- 写只读 COW 页、访问被换出的页、页迁移中的特殊条目，都需要内核完成状态转换。
- 地址不属于合法 VMA、权限不允许或文件映射超出有效后备范围时，fault 无法正常修复。
- TLB miss 本身通常由硬件 page walk 解决；只有页表或权限需要内核介入才形成 CPU page-fault 异常。

## 02-fault入口
Q: 用户态缺页进入 Linux 后大致怎样处理？
A:
1. CPU 提供 fault 地址和读写执行等错误信息，入口代码取得当前 task 的 mm。
2. 内核在 VMA 管理结构中查找包含地址的区间，并校验访问权限、栈扩展等条件。
3. 根据匿名、文件、swap、COW 或大页映射调用对应 fault handler，分配/读取页面并更新 PTE。
4. 刷新必要 TLB 后返回重试原指令；无法处理则准备 SIGSEGV 或 SIGBUS。

## 03-匿名首次访问
Q: `malloc` 后第一次读写匿名页时发生什么？
A:
- malloc 往往只扩展或映射虚拟地址，物理页可在实际访问时按需分配。
- 首次只读可能映射共享只读 zero page，避免为大量从未写入的零内存立即分配独立页。
- 首次写入触发 fault，分配清零物理页、建立可写 PTE 并计入进程 RSS。
- 因此申请大块内存成功不等于物理内存已经充足，真正触页时仍可能回收、阻塞或 OOM。

## 04-文件缺页
Q: mmap 文件后访问一个不在内存的页面会怎样？
A:
- fault handler 根据 VMA 中的 file 和 offset 定位 address_space/page cache 索引。
- page cache 未命中时分配 folio/page 并提交文件系统读取，当前任务等待 IO 完成。
- 数据有效后建立用户 PTE 指向 page cache 页，后续 `read()` 和其他映射也可共享该缓存。
- 文件被截断、存储 IO 错误或访问超出映射后备时可能收到 SIGBUS，而不一定是 SIGSEGV。

## 05-minor与major
Q: minor fault 和 major fault 的区别是什么？
A:
- minor fault 可在不等待后备存储 IO 的情况下建立映射，例如 COW、已在 page cache 的文件页或新匿名页。
- major fault 需要从文件或 swap 等后备存储读入数据，通常延迟明显更高。
- 两者都是正常按需内存机制的统计分类，不代表 minor 是程序错误较小、major 是崩溃。
- `pidstat -r`、`perf stat`、`/proc` 可观察 fault 数，但要结合延迟、IO 和工作集判断影响。

## 06-fork与COW
Q: fork 的 Copy-on-Write 如何工作？
A:
- fork 复制父进程页表，父子 PTE 指向相同物理页，并把原本可写的私有页标记为只读/COW。
- 任何一方写入时触发保护 fault，内核分配新页、复制内容、更新该进程 PTE 为可写并减少旧页引用。
- 只读共享库和未被修改的数据无需复制，使 fork 后立即 exec 成本远低于复制全部内存。
- fork 仍需复制页表和 VMA 元数据，大地址空间即使 RSS 不变也可能造成显著延迟。

## 07-COW并发
Q: 两个线程或父子进程同时写 COW 页时如何避免错误共享？
A:
- 缺页路径在页表锁、folio/page 引用和 MM 同步规则下重新检查 PTE，不能只依据进入 fault 时的旧状态。
- 一方完成复制后，另一方可能发现映射已经变化并重试，避免重复安装或丢失更新。
- get_user_pages、DMA、页迁移和文件私有映射会让 COW 语义更复杂，历史上也出现过 Dirty COW 类竞态漏洞。
- 面试重点是“只读共享 + 首次写 fault + 原子替换映射”，不是假设单线程。

## 08-MAP_SHARED与PRIVATE
Q: 文件 `MAP_SHARED` 和 `MAP_PRIVATE` 写 fault 有何不同？
A:
- MAP_SHARED 的写入修改 page cache 中共享文件页，脏页之后可回写文件，其他共享映射可能观察到。
- MAP_PRIVATE 使用 COW，写入者获得匿名私有副本，修改不会正常回写原文件。
- 两者首次访问都可能通过 page cache 读取文件，差异主要出现在写入所有权与持久化语义。
- `msync`、fsync、存储缓存和崩溃一致性仍决定共享映射何时可靠落盘。

## 09-预取与fault-around
Q: 为什么顺序 mmap 访问不一定每个页面都产生一次磁盘 IO？
A:
- 文件系统和内存管理可根据访问模式做 readahead/fault-around，一次把相邻页读入 page cache。
- 后续页面仍可能产生 minor fault 来建立 PTE，但不再等待磁盘，或者一次 fault 建立更大范围映射。
- 随机访问会降低预读命中并增加 major fault，`madvise` 可提示顺序、随机或预取策略。
- 优化要区分“磁盘读次数”“major fault”“PTE 建立次数”，三者不是同一指标。

## 10-正确性审查
Q: 关于 Page Fault 和 COW，哪些说法需要纠正？
A:
- “缺页异常就是内存不足”错误；按需分配、文件映射和 COW 都依赖正常 fault。
- “minor fault 完全没有成本”错误；仍要进入内核、分配页、复制数据或修改页表并可能 shootdown。
- “fork 是 O(1)”错误；物理页延迟复制，但页表和元数据复制随地址空间增长。
- “MAP_PRIVATE 修改文件的私有副本会自动写回原文件”错误；其写入通常转为匿名 COW 页。
