# 磁盘 I/O、空间、inode 与文件故障排查

> 基线：容量、inode、文件系统、块设备延迟和应用 fsync 是不同故障面。先定位层次，再执行清理或重启。

## 01-df与du
Q: `df` 和 `du` 数字为什么可能差很多？
A:
- df 根据文件系统 superblock/分配器统计已分配块，du 遍历当前目录树可见文件并汇总文件块。
- 已删除但仍被进程打开的文件占块计入 df，却没有路径让 du 看到。
- sparse file 的逻辑大小与实际 blocks 不同，du 是否使用 apparent-size 会改变结果。
- mount 覆盖、bind mount、权限和快照/保留块也会让两个命令观察范围不同。

## 02-deleted-open
Q: 磁盘满时怎样找已删除但仍占空间的文件？
A:
- 使用 `lsof +L1` 或检查 `/proc/*/fd` 中带 `(deleted)` 的链接，确认 inode 仍被哪些进程 file 引用。
- 日志轮转若只 rename/unlink 而服务未 reopen，旧 fd 会继续写入无名 inode。
- 优先让应用正确 reopen/关闭，或在确认内容可丢弃后对 fd 做受控 truncate；直接 kill 要评估业务影响。
- 只有最后引用释放后文件系统才回收数据块，删除同名新文件没有作用。

## 03-inode耗尽
Q: `df -h` 还有空间但创建文件报 ENOSPC，为什么检查 inode？
A:
- 传统文件系统 inode 数量可能在格式化时确定，大量小文件可先耗尽 inode 而不是数据块。
- `df -i` 看 inode 使用，按目录统计文件数定位缓存、session、临时文件或日志碎片。
- 删除海量文件本身会消耗目录锁、journal 和 IO，不能高峰期无节制执行。
- XFS 等 inode 分配模型不同，仍可能受元数据空间、配额或项目限制，错误码需结合文件系统。

## 04-iostat
Q: `iostat -x` 中 r/s、w/s、await、aqu-sz、util 应怎样关联？
A:
- r/s、w/s 与吞吐表示请求率和字节率，平均请求大小可帮助识别小随机或大顺序 IO。
- await 是请求从进入块层到完成的平均时间，包含排队和设备服务，不等于纯硬件 latency。
- aqu-sz 近似时间窗口内平均在途队列，队列升高且吞吐不再上升常表示饱和。
- `%util` 在可并行 NVMe 上不再简单等于“100% 就只能串行”，要结合延迟、队列和设备能力。

## 05-应用归因
Q: 怎样找到是谁产生了磁盘 I/O？
A:
- `pidstat -d`、iotop 可按进程/线程看读写速率与延迟趋势，但 buffered write 与后台 writeback 可能错开时间。
- `/proc/<pid>/io` 区分 read/write bytes、syscalls 和 cancelled_write_bytes，解释逻辑 IO 与设备 IO。
- 块层 tracepoint/eBPF 可按进程、cgroup、设备和延迟聚合，文件系统 trace 可进一步关联 inode/路径。
- 页缓存命中读不会产生设备 IO，大量 write 系统调用也可能稍后才由 flusher 写盘。

## 06-fsync尖刺
Q: 应用 fsync 延迟突然升高时应检查什么？
A:
- 同设备是否有大量 writeback、其他租户 flush、journal commit 或快照/RAID 后台任务。
- 文件系统脏页、journal 状态、块层队列、设备 cache/firmware 与介质 GC 是否同时变化。
- 应用是否从批量提交退化为每条事务 fsync，或多个线程在同一文件/目录提交争用。
- 用 fsync 延迟直方图和 block trace 对齐，而不是只看平均 await。

## 07-D状态
Q: 大量进程 D 状态时怎样定位等待点？
A:
- `ps` 的 wchan、`/proc/<pid>/stack`、SysRq task dump 或 perf off-CPU 查看内核阻塞栈。
- 常见原因包括块 IO、NFS、文件系统冻结、journal、设备 reset 和不可中断锁等待。
- D 状态任务通常不能立即响应普通信号，kill -9 也要等内核等待返回。
- 先确认共同设备/挂载和栈，不要重复发送 kill 造成更多待清理资源。

## 08-文件系统只读
Q: 文件系统突然 remount read-only 可能意味着什么？
A:
- ext4/XFS 等检测到元数据、journal 或设备 IO 严重错误时，可能按 errors 策略停止写入以防进一步破坏。
- dmesg/journal 中的文件系统错误和块设备 sense/NVMe 状态是关键证据。
- 强行 remount rw 或清除错误会继续写坏数据，通常应先停止业务、做镜像/备份并按文件系统工具离线检查。
- 根因可能在盘、线缆、控制器、虚拟存储或内存，不只是“文件系统软件故障”。

## 09-设备健康
Q: 如何区分文件系统慢和底层设备异常？
A:
- 查看 `dmesg` 的 timeout、reset、I/O error，SMART/NVMe health 的介质错误、剩余寿命、温度和错误日志。
- 设备固件 GC、热降频、RAID rebuild、云盘突发额度耗尽可表现为无显式坏盘错误的尾延迟。
- 对比裸设备基线、其他分区/租户和块层 completion latency，确认慢发生在提交前还是设备完成阶段。
- 生产盘压测必须隔离并限制破坏性操作，不能用写满测试验证在线故障。

## 10-容量清理
Q: 磁盘满时为什么不能直接 `rm -rf` 最大目录就结束？
A:
- 先确认路径、挂载点、业务保留和是否有 bind/容器层，避免删除错误文件系统。
- 正在写的数据库、journal、WAL 或容器 runtime 文件直接删除可能破坏恢复和仍不释放空间。
- 应优先停止增长、轮转/归档可删数据、释放已删除 fd，并持续观察 inode 与块回收。
- 清理后还要修复保留策略、磁盘水位告警和增长预测，否则故障会重复。

## 11-fd与文件锁
Q: “文件打不开/无法替换”时还应检查哪些内核对象？
A:
- fd 上限、权限、只读 mount、quota、inode、路径长度和 SELinux/AppArmor 都可能让 open 失败，errno 是第一线索。
- advisory lock 只约束合作进程，强制锁语义依文件系统；`lslocks`、`/proc/locks` 可查看。
- mmap、执行中的二进制、NFS lease 和容器 overlay copy-up 可能改变替换行为与空间。
- 使用 strace 精确看失败 syscall 和 errno，比根据应用“文件异常”日志猜测更快。

## 12-正确性审查
Q: 磁盘与文件排障中哪些做法需要避免？
A:
- “du 小于 df 就运行 du 有 bug”错误；首先检查 deleted-open、快照、保留块和挂载范围。
- “util 100% 说明 NVMe 完全不能处理更多请求”过度简化；需看队列、延迟和吞吐。
- “kill -9 能立即杀死 D 状态进程”错误；任务要等不可中断内核路径返回。
- “文件系统只读直接 remount rw”危险；必须先保存错误现场并排除设备/元数据损坏。
