# Linux 块层、bio、blk-mq 与 I/O 调度

> 基线：描述现代 Linux blk-mq 通用路径。具体文件系统、device-mapper、虚拟块设备和 NVMe/SCSI 驱动会增加层次。

## 01-端到端路径
Q: 文件系统提交一次块 I/O 到设备大致经过哪些层？
A:
- buffered writeback 或 Direct I/O 根据文件逻辑偏移通过文件系统映射得到物理块范围。
- 内核用 bio 描述一组页片段、设备、扇区和读写属性，可经过 md、dm、加密或快照层转换。
- 块层合并、拆分并形成 request，blk-mq 把请求放入软件/硬件队列，由设备驱动提交。
- 设备完成后中断/NAPI 式 completion 向上结束 request 和 bio，唤醒等待者或完成异步回调。

## 02-bio
Q: `struct bio` 表达什么？
A:
- bio 是块 I/O 的基本描述，包含目标块设备、起始扇区、操作标志和由 page/offset/length 组成的向量。
- 它描述内存页与设备逻辑块之间的数据传输，不等同一个用户 read，也不一定等同一个设备命令。
- 大 bio 可能按设备最大传输、段数、边界拆分，邻近 bio 也可能在上层合并。
- bio 完成回调把错误和已完成范围传回提交者，异步生命周期要求正确引用页面和对象。

## 03-request
Q: request 与 bio 有什么关系？
A:
- request 是块层面向设备调度和驱动提交的请求，可包含一个或多个可合并 bio。
- 它记录命令类型、范围、deadline/调度信息、tag 和完成状态，最终映射为设备队列命令。
- 合并减少设备命令和中断开销，但会增加等待聚合时间，延迟与吞吐需要折中。
- flush、discard 等无数据操作也可表现为 request，不是所有请求都有用户数据 buffer。

## 04-blk-mq
Q: blk-mq 为什么替代单队列块层？
A:
- 现代多核和 NVMe 有多个硬件提交队列，单全局 request queue 会产生锁与 cache line 争用。
- blk-mq 为 CPU/软件上下文组织 software queue，并映射到一个或多个 hardware dispatch queue。
- tag 唯一标识设备在途命令，驱动可高并发提交和按 tag 完成，充分利用硬件队列深度。
- 队列数量、CPU affinity 和中断分布影响 NUMA 局部性，不能只把 blk-mq 理解为“多建几个链表”。

## 05-merge与split
Q: 块层为什么既会 merge 又会 split 请求？
A:
- 相邻且属性兼容的 bio/request 可前向或后向合并，减少命令数并提高顺序吞吐。
- 超过设备最大扇区、scatter-gather 段数、边界或对齐限制的 I/O 必须拆分。
- 加密、RAID、LVM 和文件系统 extent 还会改变最终范围，用户一次 1 MiB write 不保证设备只收到一个命令。
- 用 blktrace/bpftrace 等观察实际 request 大小分布比根据应用调用猜测可靠。

## 06-IO调度器
Q: mq-deadline、BFQ、none 等调度策略分别倾向什么？
A:
- none 主要做基本合并和直接分派，常适合自身有强队列能力的 NVMe，但并非所有负载都最佳。
- mq-deadline 在读写排序与截止时间之间折中，防止某类请求长期饥饿，适合通用块设备。
- BFQ 按进程/队列预算提供带宽公平和交互体验，额外调度成本更高。
- 可用调度器、默认值和实现随设备类型与发行版变化，选型应基于延迟分位数和公平目标压测。

## 07-queue-depth
Q: I/O queue depth 为什么太小和太大都不好？
A:
- 深度太小无法让 SSD/NVMe 并行通道保持忙碌，吞吐低且设备内部调度机会少。
- 深度太大使请求在软件和设备队列中等待，尾延迟、超时恢复和内存占用上升。
- 数据库并发、应用线程数、异步提交数和设备硬件队列共同决定实际在途深度。
- 最佳点取决于读写比例、请求大小、SLA 和设备，不能用厂商峰值 QD 直接配置线上。

## 08-NVMe
Q: NVMe 为什么改变了传统 I/O 调度假设？
A:
- NVMe 支持大量 submission/completion queue 和高并发命令，单核锁与机械寻道不再是主要瓶颈。
- CPU、PCIe、NUMA、IRQ affinity、驱动 tag 和软件栈开销会成为微秒级延迟的重要部分。
- 无机械磁头并不意味着请求顺序完全无关；写放大、FTL、GC、热状态和设备缓存仍影响尾延迟。
- 现代调优要关注每 CPU 队列和完成路径，不应只套用旋转磁盘“排序减少寻道”结论。

## 09-flush-FUA-discard
Q: flush、FUA 和 discard 分别表达什么？
A:
- flush 请求让设备把之前易失缓存中的写推进持久介质，并建立顺序屏障语义。
- FUA 要求特定写在报告完成前达到非易失状态，能否高效支持取决于设备。
- discard/TRIM 告诉 SSD 某些逻辑块不再使用，便于内部回收，不代表安全擦除。
- 文件系统 fsync、barrier 需要块层和设备正确实现这些语义，关闭 flush 可能提升基准但破坏崩溃保证。

## 10-观测与正确性
Q: 怎样观测块层瓶颈，并纠正常见误区？
A:
- `iostat -x` 看吞吐、await、队列和设备利用率，但不同并行设备上 `%util=100` 的含义有限。
- PSI io、应用延迟、块层 tracepoint、request 大小和队列深度能区分设备慢、排队深还是上层回写。
- “await 高就是磁盘坏”错误；大量队列、cgroup 限流、flush 和文件系统锁都可能贡献等待。
- “NVMe 不需要任何 I/O 调度”过度绝对；公平、限流、合并和尾延迟仍可能需要块层策略。
