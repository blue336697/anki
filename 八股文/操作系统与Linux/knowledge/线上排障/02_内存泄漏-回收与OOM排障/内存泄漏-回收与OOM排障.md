# 内存泄漏、回收、Swap 与 OOM 排障

> 基线：先区分系统内存压力、进程工作集、allocator 保留、Page Cache、内核 slab 与 cgroup 限制，再谈“泄漏”。

## 01-第一现场
Q: 内存告警出现后应先保存哪些证据？
A:
- `/proc/meminfo`、`vmstat`、`free`、PSI memory、swap 活动、OOM 日志和时间线。
- 进程/容器 RSS、PSS、匿名/文件映射、cgroup memory.current/max/events/stat。
- 最近发布、流量、缓存命中、线程数、连接数和大对象请求，确认增长是否与业务事件同步。
- OOM 前后现场差异比 OOM 后单次 top 更有价值，监控应预先保留趋势。

## 02-MemAvailable
Q: 为什么不能用 MemFree 判断是否内存不足？
A:
- Linux 会把空闲页用于 Page Cache 和可回收内核缓存，MemFree 长期较低通常正常。
- MemAvailable 估算在不引发严重 swap 的情况下可用于新负载的页，考虑部分 cache 和水位。
- dirty/writeback、不可回收 slab、锁页和高阶连续页需求使“可用总量”也不能覆盖所有分配场景。
- 压力判断还需看 direct reclaim、major fault、swap in/out 和 memory PSI。

## 03-进程映射
Q: 怎样解释一个进程的 RSS 组成？
A:
- `/proc/<pid>/smaps_rollup` 给出 Rss、Pss、Private、Shared、Anonymous、Swap 等汇总。
- 匿名 RSS 常来自 heap、线程栈、匿名 mmap 和运行时；文件 RSS 包含代码、共享库和 mmap/page cache。
- 共享页在每个进程 RSS 重复计入，PSS 按共享者分摊，评估多进程总成本时更准确。
- VSZ 很大可能只是预留地址或稀疏映射，不等于实际占用物理页。

## 04-泄漏与保留
Q: 如何区分对象泄漏和分配器保留/碎片？
A:
- 泄漏表现为仍可达/未释放对象和 allocated bytes 持续增长，可用 heap dump/profile 定位持有链。
- allocator 保留表现为业务活对象稳定但 resident/RSS 高，空闲块留在 arena/tcache 或无法凑成整页归还。
- 比较 allocated、active、resident/retained 指标与匿名 RSS，执行受控 trim 或替换 allocator 做对照。
- 只看 RSS 不能证明泄漏，Page Cache、JIT、线程栈和 native 库也在进程内存中。

## 05-page-fault
Q: minor/major fault 突增分别提示什么？
A:
- minor fault 增长可能来自首次匿名触页、fork COW、mmap 已缓存页或大规模页表重建，仍会消耗 CPU。
- major fault 需要后备存储 IO，常见于冷文件、swap-in 或工作集超出内存，直接影响尾延迟。
- 结合 `pidstat -r`、perf faults、磁盘 IO 和 mmap 行为判断，不要把所有 fault 都称“缺页到磁盘”。
- 容器重启/部署后的冷启动 fault 与长期 steady-state 抖动意义不同。

## 06-reclaim与PSI
Q: 怎样确认应用正在承受内存回收压力？
A:
- `vmstat` 看扫描/回收、kswapd、direct reclaim、swap，`/proc/vmstat` 提供更细事件。
- `/proc/pressure/memory` 的 some 表示至少部分任务因内存受阻，full 表示所有非空闲任务同时停顿的严重 thrashing。
- cgroup v2 也提供 memory.pressure，可区分某容器自身压力与宿主全局压力。
- RSS 不再增长但 PSI 和延迟上升，可能是系统在持续回收维持表面稳定。

## 07-swap
Q: 怎样判断是合理 swap 使用还是 swap thrashing？
A:
- 仅看到 swap used 非零可能是历史冷页，若 `si/so` 低且业务稳定未必有问题。
- 持续 swap-in/out、major fault、设备高 IO、CPU 等待和 PSI memory/full 上升说明工作集来回换入换出。
- 找出匿名内存大户、cgroup 限制和 swappiness/工作集，再决定扩容、限流或调整 swap。
- 直接 `swapoff` 会迫使所有页换入，内存不足时可能触发 OOM，不能作为无风险清理命令。

## 08-slab
Q: 进程 RSS 不高但系统内存不断下降，为什么要检查 slab？
A:
- dentry、inode、网络对象、文件对象和各类内核 cache 使用 slab，不计入某个进程普通 RSS。
- `/proc/slabinfo`、`slabtop` 可看对象数量、缓存大小和增长，`SReclaimable/SUnreclaim` 区分可回收倾向。
- 大量文件扫描、连接跟踪、泄漏驱动或未关闭内核对象都可能使某类 cache 增长。
- 可回收 slab 也不代表立即无成本释放，需结合 shrinker、引用和内存压力。

## 09-THP与碎片
Q: 内存充足却出现高阶分配/THP 延迟时检查什么？
A:
- 查看 buddyinfo/pagetypeinfo 的高阶空闲块、compaction 事件和 THP fault/collapse/split 统计。
- 总空闲页可能被不可移动页分割，无法形成连续大页，分配线程参与 compaction 产生尖刺。
- THP 策略、数据库访问模式和 NUMA 会改变收益，必要时用 madvise 或关闭特定工作负载大页做对照。
- 这类问题不是普通用户对象泄漏，增加一点 free 也未必恢复高阶连续性。

## 10-OOM证据
Q: 怎样确认进程是被 OOM killer 杀死？
A:
- 查 `dmesg`/journal 的 `Out of memory`、`oom-kill`、constraint、被选 task、score 和内存摘要。
- memcg OOM 还要查 `memory.events` 的 oom/oom_kill，以及编排器/container runtime 事件。
- shell exit 137 仅表示常见的 SIGKILL 编码，人工 kill、liveness 超时也会相同。
- 保存被杀前 cgroup 使用和 `oom_score_adj`，否则只能知道结果，无法解释为什么选中它。

## 11-NUMA
Q: 单个 NUMA node 内存压力为什么可能先于全机 OOM/延迟？
A:
- 任务 cpuset、mempolicy 或设备 DMA 可能限制可分配 node/zone，即使远端 node 仍有空闲。
- first-touch 不均使一个 node 匿名页集中，内存回收和远端访问延迟先在局部发生。
- `numastat -p`、`/sys/devices/system/node/node*/meminfo` 和 perf 远端访问指标帮助定位。
- 盲目 `numactl --interleave=all` 可能缓解容量却降低局部性，应按访问模式压测。

## 12-正确性审查
Q: 内存排障中哪些结论需要避免？
A:
- “available 低就是某进程泄漏”错误；要区分匿名、文件 cache、slab、cgroup 与回收。
- “RSS 不下降说明 free 没生效”错误；allocator 可能保留空闲块供复用。
- “exit 137 一定是 OOM”错误；必须有内核/cgroup 证据。
- “清 Page Cache 能解决内存问题”通常只是破坏缓存并制造 IO，未修复工作集、泄漏或限制根因。
