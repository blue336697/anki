# Page Cache、内存回收、Writeback 与 OOM

> 基线：Linux 会主动把可用内存用于缓存。判断内存压力要看 MemAvailable、reclaim、swap、PSI 和工作集，而不是要求 free 长期很大。

## 01-PageCache
Q: Linux Page Cache 缓存什么，为什么属于“已使用内存”？
A:
- 它缓存文件内容的 folio/page，以 address_space 和文件偏移作为索引，read、mmap 和 write 可共享。
- 读命中避免设备 IO；写通常先修改缓存并标 dirty，之后异步回写。
- 缓存页占用物理内存所以计入 used，但干净文件页在压力下可直接丢弃并从文件重读。
- 因此低 free、高 cache 通常是正常利用，不等于内存泄漏。

## 02-buffer与cache
Q: `free` 输出中的 buff/cache 应怎样理解？
A:
- 现代 Linux 的 cache 包含 page cache 以及可回收 slab 等，buffers 只占较小的块设备元数据语义。
- `MemAvailable` 估算在不发生严重 swap 的情况下可供新工作负载使用的内存，比 MemFree 更有意义。
- 一部分 cache 是 dirty、writeback、mlock 或不可回收对象，不能把全部 buff/cache 当成立即可用。
- 容器内看到的统计还受 cgroup 记账与宿主全局内存影响，需要同时看 cgroup memory.stat。

## 03-读路径
Q: buffered read 在 Page Cache miss 时怎样完成？
A:
- VFS/文件系统按 inode address_space 和页索引查缓存，命中则把数据复制到用户缓冲。
- 未命中时分配缓存 folio/page，提交块层 IO，任务等待或由预读提前填充相邻页。
- IO 完成后页面标记 uptodate，后续 read 或 mmap fault 可共享同一缓存内容。
- 顺序预读提高吞吐，但随机工作负载可能污染缓存；fadvise/madvise 可辅助表达模式。

## 04-写路径
Q: buffered write 返回成功时数据在哪里？
A:
- 内核通常先把用户数据复制到 page cache 页并标 dirty，更新文件大小和元数据后即可返回。
- 此时数据可能仅在 RAM，后台 writeback 稍后把脏页提交文件系统和块设备。
- `write()` 成功不等于断电后可恢复；需要 fsync/fdatasync 及正确文件系统、设备 flush 语义。
- 脏页达到阈值会让写线程被节流甚至参与回写，表现为业务 write 延迟突然上升。

## 05-writeback
Q: 后台回写由哪些机制推进？
A:
- flusher/writeback worker 按脏页年龄、比例、内存域和文件系统策略选择 inode/page 批量写出。
- 脏页经历 dirty、writeback、clean 或 error 状态，IO 完成前不能简单按干净页丢弃。
- `balance_dirty_pages` 一类机制限制产生脏页过快的进程，让写入速率逐渐接近设备可持续吞吐。
- 回写错误必须反馈给 fsync/后续写入路径；应用不能只看最初 write 成功。

## 06-watermark与kswapd
Q: zone watermark 和 kswapd 如何维持可分配页？
A:
- 每个 zone 维护 min/low/high 等水位，快速分配低于阈值时唤醒后台 kswapd 回收。
- kswapd 尝试把空闲页恢复到目标水位，让普通分配不必在请求路径长时间等待。
- 若后台来不及，分配线程进入 direct reclaim，延迟直接出现在业务请求上。
- 水位还受低内存保留、NUMA node、zone 类型和分配 order 影响，系统总 free 不能说明某 zone 一定可用。

## 07-reclaim
Q: 内存回收如何在文件页和匿名页之间选择？
A:
- 干净文件页可直接从 page cache 移除，未来从文件重读；脏文件页需先 writeback。
- 匿名页没有原始文件后备，若启用 swap 可写入 swap 后释放，否则更难回收。
- 内核依据活跃度、refault、swappiness、memcg 与现代多代 LRU 等信号判断工作集，避免只按“最近一次访问”机械淘汰。
- 回收错误会产生 page cache 抖动、swap thrashing 和高 memory PSI。

## 08-MGLRU
Q: Multi-Gen LRU 相比经典 active/inactive LRU 想改善什么？
A:
- 经典模型用 active/inactive 列表近似冷热，扫描和晋升在大内存、多 cgroup 场景可能不够准确。
- MGLRU 按代际记录页面最近被观察到的访问年龄，在代之间老化并优先回收更老页面。
- 目标是更好识别工作集、降低 refault 和扫描成本，但是否启用、接口与行为依内核版本和发行版配置。
- 面试应把它作为现代回收演进，不要声称所有 Linux 机器都已经使用相同 MGLRU 参数。

## 09-swap
Q: swap 的作用只是“物理内存不够时救命”吗？
A:
- swap 为冷匿名页提供后备，使物理内存可留给活跃匿名工作集和有价值文件 cache。
- 适量 swap 可提高利用率，但持续大量 swap-in/out 表明工作集超过内存，延迟会急剧恶化。
- zswap/zram 可用压缩内存减少磁盘访问，但消耗 CPU 和额外元数据，不增加真实工作集容量。
- `si/so`、major fault、swap cache、PSI 和延迟要联合判断，swap 使用量非零不等于正在抖动。

## 10-NUMA
Q: NUMA first-touch 和自动 NUMA balancing 如何影响性能？
A:
- 匿名页通常在首次实际触页的 CPU 所属 node 分配，因此初始化线程的位置决定物理页归属。
- 线程迁移到远端 CPU 后会增加访问延迟和互联带宽；自动 NUMA balancing 可采样并迁移页或任务。
- 多线程由单线程集中初始化大数组可能把页放到一个 node，造成其他 CPU 远端访问。
- numactl、numastat、perf c2c 和拓扑信息可验证，盲目绑核/绑内存可能导致某 node 先 OOM。

## 11-THP
Q: Transparent Huge Pages 有什么收益和风险？
A:
- THP 用 PMD 等大页映射覆盖更多内存，降低页表和 TLB miss，适合大而连续的匿名工作集。
- 分配、fault、compaction、拆分和 COW 大页可能造成延迟尖刺，内存碎片和浪费也更明显。
- `always/madvise/never` 等策略与后台 khugepaged 行为依发行版而异，数据库常需结合自身访问模式压测。
- hugetlb 预留大页与 THP 是不同机制，不能混为“开启大页”。

## 12-overcommit
Q: Linux overcommit 为什么会让内存申请成功但运行时 OOM？
A:
- 用户申请虚拟内存时，内核可允许承诺总量超过 RAM+swap，因为许多映射不会全部触页或会共享。
- overcommit policy 和 commit limit 控制承诺检查强度，但实际物理压力发生在缺页和写入时。
- malloc/mmap 成功只说明虚拟地址与承诺策略允许，不保证未来每个匿名页都可驻留。
- 关键服务要设置合理内存上限、监控工作集并处理分配失败，不能依赖申请阶段一次性证明。

## 13-OOM
Q: Linux OOM killer 怎样选择和终止任务？
A:
- 分配在允许的 reclaim、compaction 和 swap 路径后仍无法满足，可能触发全局、NUMA/zone 或 memcg 范围 OOM。
- 内核根据任务内存贡献、`oom_score_adj`、可杀性和约束计算候选，选择牺牲进程释放内存。
- 被选进程收到致命终止并由 OOM reaper 等机制加快回收，但若大量页不可回收，系统仍可能迟迟不恢复。
- `dmesg`/journal 中的 OOM report、约束、被杀 task 和内存统计是权威现场，不能只看应用 exit 137。

## 14-cgroup OOM
Q: 容器 OOM 与宿主全局 OOM 有什么区别？
A:
- cgroup v2 `memory.max` 限制该层级可用内存，超限且回收失败时可在该 cgroup 范围选择牺牲任务。
- 宿主可能仍有空闲内存，但容器因自身 hard limit OOM；反之未正确限制的容器也可能触发全局 OOM。
- `memory.current`、`memory.events`、`memory.stat`、`memory.pressure` 与容器运行时事件应一起检查。
- exit 137 只表示 SIGKILL 常见编码，可能来自 OOM、人工 kill 或编排系统，必须用内核和 cgroup 证据确认。

## 15-正确性审查
Q: 关于 Linux 内存，哪些说法需要纠正？
A:
- “free 越多系统越健康”错误；Linux 会用闲置 RAM 做可回收缓存，关键是 available 和压力。
- “write 返回就已落盘”错误；buffered write 多数只完成 page cache 修改。
- “swap 一使用就说明内存泄漏”错误；冷页可能合理驻留 swap，持续换入换出才代表抖动。
- “OOM 一定杀内存最大的进程”错误；选择受 OOM 约束域、分数调整和任务属性共同影响。
