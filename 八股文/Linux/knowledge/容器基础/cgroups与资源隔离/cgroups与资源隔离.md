# cgroups与资源隔离

## cgroups卡
Q: cgroups 在 Linux 和容器中解决什么问题？
A:
- cgroups 用于限制、统计和隔离进程组资源
- 可控制 CPU、内存、IO、进程数等资源
- Docker、Kubernetes 使用 cgroups 实现容器资源限制
- namespace 负责视图隔离，cgroups 负责资源限制
- 面试表达：容器不是轻量虚拟机，核心依赖 namespace 和 cgroups 等内核能力

## CPU卡
Q: 容器 CPU limit 和 throttling 如何理解？
A:
- CPU request/limit 最终会映射到 cgroup CPU 配置
- limit 限制容器可使用的 CPU 时间
- 超过配额会发生 throttling，表现为应用延迟升高
- 即使宿主机还有空闲 CPU，容器也可能因 limit 被限流
- Java 服务要关注容器感知 CPU 和线程池配置

## 内存卡
Q: 容器内存限制和 OOM 有什么特点？
A:
- 容器内存受 cgroup 限制，不是宿主机总内存
- 超出限制会触发 cgroup OOM，杀掉容器内进程
- JVM 堆、直接内存、线程栈、metaspace、page cache 都可能计入
- 只设置堆大小不代表容器不会 OOM
- 排查要看容器事件、dmesg、memory.stat 和应用内存配置

## 正确性审查卡
Q: cgroups 和容器资源有哪些常见误区？
A:
- “容器有独立内核”：通常错误。容器共享宿主机内核
- “limit 只影响资源用量不影响延迟”：错误。CPU throttling 会增加延迟
- “容器 OOM 一定是 JVM 堆太大”：不一定。堆外、线程和缓存都可能
- “namespace 和 cgroups 是一回事”：错误。一个做视图隔离，一个做资源控制
- “宿主机没满容器就不会受限”：错误。cgroup limit 可以单独限制容器
