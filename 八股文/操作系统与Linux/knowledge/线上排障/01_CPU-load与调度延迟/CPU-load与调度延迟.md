# CPU、Load 与调度延迟排障

> 基线：先保存时间窗口和业务影响，再按系统、进程、线程、调用栈下钻。CPU 使用率、load average、PSI 和调度延迟描述不同问题。

## 01-第一现场
Q: 收到“CPU 高”告警后第一步应该做什么？
A:
- 记录开始时间、持续时长、业务 QPS/延迟/错误、实例与发布变更，避免只保存一张 top 截图。
- 确认是单核、全机、容器 quota 还是 steal，比较用户态、内核态、IRQ/softirq、iowait 分布。
- 找到进程后下钻到线程，再把线程 ID 与应用线程 dump、perf 栈和请求 trace 对齐。
- 先观察再重启；重启会清除线程、栈、计数器和内核等待现场。

## 02-CPU时间
Q: top 中 us、sy、ni、id、wa、hi、si、st 分别说明什么？
A:
- us/ni 是普通/调整 nice 的用户态执行，sy 是内核态执行，hi/si 是硬中断与软中断。
- id 是空闲，wa 表示采样期间 CPU 空闲且系统有 I/O 等待，并非某进程“使用 CPU 做 IO”。
- st 是虚拟 CPU 被 hypervisor 安排给其他 guest 的时间，高 steal 指向宿主争用。
- 百分比是时间窗口聚合，短尖刺和单核热点会被多核平均掩盖。

## 03-load
Q: 高 load、低 CPU 常见原因是什么？
A:
- 大量任务处于 D 状态等待块设备、网络文件系统、内核锁或不可中断路径，会计入 load。
- CPU quota throttling、虚拟化 steal 或 runqueue 周期拥塞也可能让任务可运行却拿不到实际 CPU。
- 查看 `vmstat` 的 r/b、`ps` 状态和 wchan、PSI cpu/io、iostat 与调度延迟区分原因。
- 不能因为 CPU idle 还有余量就断言 load 无害；业务线程可能都卡在不可并行资源。

## 04-单核热点
Q: 总 CPU 不高但服务延迟高，为什么要检查单核？
A:
- 单线程 event loop、锁持有者、GC 线程、网络 softirq 或热点 Queue 可能打满一个 CPU，其他核空闲。
- `mpstat -P ALL`、top per-CPU、`pidstat -t` 和 `/proc/interrupts` 可定位哪个核、哪个线程。
- CPU affinity、cgroup cpuset、IRQ 绑定和 NUMA 会限制任务不能使用所有显示在线 CPU。
- 优化方向可能是分片、消除串行点或重分布 IRQ，而不是给机器再加核。

## 05-线程定位
Q: 怎样从高 CPU 进程定位到代码线程？
A:
- `top -H -p PID` 或 `pidstat -t -p PID` 找到持续高 CPU 的 TID。
- Java 等运行时需把十进制 TID 转成线程 dump 使用的 nid 格式，连续多次采样确认不是瞬时线程。
- 原生程序用 `perf top -p` 或 `perf record -t TID` 获取用户/内核混合栈，确保符号与 frame pointer/unwind 可用。
- 线程名可能被截断或重复，TID、时间和栈才是可靠关联。

## 06-perf-stat
Q: `perf stat` 哪些指标能区分“做了很多工作”和“CPU 效率低”？
A:
- cycles、instructions 与 IPC 反映每周期完成指令；低 IPC 可能来自 cache miss、分支失败、内存或序列化等待。
- context-switches、cpu-migrations、page-faults 反映调度与内存活动，不能单独作为性能结论。
- cache-misses 和 branch-misses 需与硬件事件支持、采样范围和工作负载基线比较。
- 在相同业务吞吐下对比版本，避免只因 QPS 增加而把 cycles 总量上升判为回退。

## 07-onCPU火焰图
Q: on-CPU flame graph 能回答什么？
A:
- 横向宽度表示采样中某调用栈占 CPU 的比例，能发现热循环、序列化、正则、压缩、锁自旋和系统调用热点。
- 它不能直接显示函数每次延迟，也不包含睡眠等待时间；窄但很慢的阻塞调用可能不突出。
- 采样频率、符号、内联/JIT 映射和栈回溯质量影响结论，unknown 栈要先修复采集。
- 结合业务 trace 和吞吐判断热函数是必要工作还是可消除浪费。

## 08-offCPU
Q: CPU 不高但请求慢，off-CPU 分析为什么重要？
A:
- 线程可能在 futex、磁盘、网络、定时器或调度队列睡眠，on-CPU profiler看不到等待时间。
- sched tracepoint、eBPF off-CPU stack、perf sched 和线程 dump 可记录阻塞栈与唤醒延迟。
- 需要区分主动等待资源、已经 runnable 但迟迟未调度，以及 cgroup throttling。
- 把阻塞时长按调用栈聚合，才能判断应优化锁、下游、IO 还是 CPU 配额。

## 09-sy与softirq
Q: system CPU 或 softirq 很高应怎样下钻？
A:
- sy 高可来自频繁 syscall、页缺失、文件系统、网络、锁或内核安全过滤；用 perf kernel stack 和 syscall 统计定位。
- si 高结合 `/proc/softirqs`、`/proc/interrupts` 判断 NET_RX、timer、RCU 等类型和 CPU 分布。
- 网络场景检查 PPS、NAPI、GRO、drop、IRQ affinity；块场景检查 completion 和设备队列。
- 不能简单把“内核态高”归因 Linux bug，应用小包、频繁调用和线程模型常是源头。

## 10-cgroup限流
Q: 容器 CPU 使用率不满为什么仍会发生 throttling？
A:
- `cpu.max` 在 period 内限制 quota，多线程可在周期前半段迅速用完预算，随后整体等待下个周期。
- 平均到一分钟的 CPU 可能低于 limit，但毫秒级请求会看到周期性长尾。
- 查看 cgroup `cpu.stat` 的 nr_throttled/throttled_usec、cpu.pressure 和应用延迟时间线。
- 调整 quota/period、减少突发并发或增加实例要结合下游容量，不能只提高 limit 掩盖热代码。

## 11-锁竞争
Q: 锁竞争为什么可能同时表现为 CPU 高或 CPU 低？
A:
- 自旋或用户态 CAS 重试会消耗 CPU，火焰图出现原子操作、spin 或锁 fast path。
- mutex/futex 竞争会让线程睡眠，CPU 可能不高但上下文切换、off-CPU 和延迟上升。
- 持锁者若被抢占、阻塞 IO 或运行在受限 cgroup，会放大所有等待者尾延迟。
- 用锁 profile、futex trace、线程 dump 和共享数据访问路径确认，不能仅凭线程状态猜。

## 12-正确性审查
Q: CPU 排障中哪些常见结论是错误的？
A:
- “load 高就是 CPU 高”错误；D 状态 IO 等待也计入 load。
- “多核总 CPU 50% 就没有 CPU 瓶颈”错误；单核串行点可能已经饱和。
- “iowait 高表示 CPU 正在忙于 IO”错误；它是特定采样条件下的空闲等待分类。
- “重启恢复说明问题解决”错误；重启只清状态，未解释热代码、锁、配额或中断根因。
