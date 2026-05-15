# 内存问题与OOM

## free卡
Q: Linux 中 free 命令看到的 buff/cache 如何理解？
A:
- Linux 会尽量使用空闲内存做页缓存和 buffer
- buff/cache 可在内存压力下回收
- available 比 free 更能反映可用内存
- 内存少不一定是泄漏，可能是缓存利用充分
- 排查要结合进程 RSS、swap、cache、slab 和 OOM 日志

## OOM卡
Q: Linux OOM Killer 什么时候会触发？
A:
- 系统或 cgroup 内存无法满足分配请求时可能触发 OOM
- 内核根据 oom_score 等因素选择牺牲进程
- 容器环境常见的是 cgroup 限制触发 OOM
- OOM 日志可从 dmesg、journalctl 或容器事件中查看
- 应结合内存上限、堆大小、直接内存、线程栈和页缓存分析

## 泄漏卡
Q: 线上内存持续上涨如何排查？
A:
- 先区分进程 RSS 增长、页缓存增长还是 slab 增长
- Java 服务要看堆、直接内存、metaspace、线程栈
- native 程序可用 pmap、smaps、perf、jemalloc profile 等工具
- 容器要看 cgroup memory.current 和 memory.stat
- 结合发布变更、流量、对象数量和 GC 日志判断

## 正确性审查卡
Q: Linux 内存排查有哪些常见误区？
A:
- “free 很小就是没内存”：错误。available 更关键
- “OOM 一定是堆泄漏”：不一定。直接内存、线程、page cache、cgroup 都可能
- “加 swap 就能解决”：不完整。swap 可能显著增加延迟
- “容器看到的内存就是宿主机全部内存”：不一定。受 cgroup 限制
- “重启后内存下降就证明泄漏”：不充分。缓存和工作集也会下降
