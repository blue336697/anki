# Linux Namespace 与 cgroup v2

> 基线：namespace 改变进程看到的资源视图，cgroup 组织进程并分配/限制资源。二者组合仍不是完整安全边界。

## 01-namespace本质
Q: Linux namespace 隔离的本质是什么？
A:
- task 关联一组 namespace 对象，内核在查询 PID、mount、网络设备、主机名、IPC 等资源时使用对应视图。
- 多个进程加入同一 namespace 就共享该视图；创建新 namespace 通常从父视图复制/引用初始状态。
- namespace 不模拟另一套内核，容器与宿主仍运行在同一个 Linux 内核上。
- 隔离能力取决于 namespace 类型、权限、挂载传播和内核攻击面，不能只创建 PID namespace 就称为容器。

## 02-PID-namespace
Q: PID namespace 如何让容器内出现 PID 1？
A:
- 同一个 task 在嵌套 PID namespace 层级中拥有不同可见 PID，外层可看到内层进程，内层看不到外层。
- 新 namespace 的第一个进程成为该空间 PID 1，承担信号特殊处理和回收孤儿/僵尸职责。
- 若 PID 1 不正确 wait，容器会积累 zombie；其退出通常导致该 PID namespace 中其他进程被终止。
- `/proc` 必须在对应 mount/PID namespace 视图正确挂载，否则容器内工具可能看到错误进程集合。

## 03-mount-namespace
Q: mount namespace 与 chroot 有何差别？
A:
- mount namespace 隔离 mount tree，使容器可拥有独立挂载、bind mount 和 proc/sysfs 视图。
- mount propagation 决定一个 namespace 的挂载变化是否传播到共享 peer 或子空间，配置错误会泄漏宿主挂载事件。
- chroot 只改变路径解析 root，特权进程仍可能逃逸，也不隔离 mount 操作和其他资源。
- 容器根文件系统通常需要 mount namespace、pivot_root、只读/遮蔽挂载共同构建。

## 04-network-namespace
Q: network namespace 隔离了哪些网络对象？
A:
- 它拥有独立网络设备、IP 地址、路由表、邻居表、防火墙、端口空间和大部分网络协议状态。
- veth pair 常把容器 netns 与宿主 bridge/路由连接，两端像一根虚拟网线。
- 同 netns 内两个进程不能重复绑定冲突端口，不同 netns 可各自使用相同端口。
- 包离开 netns 后仍经过宿主 bridge、路由、NAT、qdisc 和物理网卡，性能与故障需看完整路径。

## 05-user-namespace
Q: user namespace 如何支持 rootless 容器？
A:
- 它把 namespace 内 UID/GID 映射到外部不同、通常无特权的宿主 UID/GID。
- 容器内显示 UID 0 只在该 user namespace 的 capability 范围内拥有特权，不自动成为宿主 root。
- 允许的 uid/gid map、setgroups、文件所有权和其他 namespace 创建受内核与发行版安全策略控制。
- user namespace 缩小宿主权限，但增加内核 namespace 攻击面，不能替代 seccomp、LSM 和补丁。

## 06-cgroup-v2
Q: cgroup v2 的统一层级解决了什么？
A:
- 所有支持 v2 的 controller 组织在一棵统一树中，进程归属与 CPU、memory、IO 等层级控制更一致。
- 每个进程在该层级属于一个 cgroup，子层限制不能突破祖先限制；资源分配沿层级生效。
- controller 通过 `cgroup.subtree_control` 在子树启用，并受 no-internal-process 等结构规则约束。
- v1 可有多套独立层级，旧教程的接口和行为不能直接套到 v2。

## 07-CPU控制
Q: cgroup v2 的 `cpu.weight` 和 `cpu.max` 有什么区别？
A:
- `cpu.weight` 是竞争时的相对份额，系统空闲时某组仍可使用更多 CPU，不是硬核数上限。
- `cpu.max` 用 quota/period 表达带宽上限，达到 quota 后组内任务被 throttled 到下个周期。
- 低 quota 与长周期会造成周期性延迟尖刺；多线程即使平均 CPU 未满也可能集中用完预算。
- `cpu.stat` 的 throttled 计数和 PSI 应与应用延迟一起看，不能只看容器 CPU 百分比。

## 08-memory控制
Q: `memory.low/high/max` 分别表达什么？
A:
- `memory.low` 提供尽力保护，内存未超过祖先保护能力时优先避免回收该组工作集。
- `memory.high` 是节流/回收边界，超过后分配任务承担回收压力但不立即硬失败。
- `memory.max` 是硬上限，组内回收仍无法满足时可触发 memcg OOM。
- `memory.current/events/stat/pressure` 用于解释使用、回收和 OOM，单看 max 无法判断工作集是否健康。

## 09-IO与PID控制
Q: cgroup v2 怎样限制块 I/O 和进程数量？
A:
- `io.max` 可按设备 major:minor 限制 BPS/IOPS，`io.weight` 在支持的调度路径中表达相对份额。
- buffered write 的实际归属、writeback 和共享文件页使 IO 记账比直接请求更复杂，需要目标内核验证。
- `pids.max` 限制 cgroup 内 task 数，防止 fork bomb，但线程也会消耗 task/PID 额度。
- 达到 pids 限制后 fork/clone 失败，不会选择并杀死旧进程，应用要处理资源创建失败。

## 10-cgroup迁移
Q: 把一个运行进程迁移到另一个 cgroup 后，已有资源会全部重新记账吗？
A:
- 写 PID 到目标 `cgroup.procs` 改变后续调度与控制归属，线程迁移规则受 cgroup 类型约束。
- 已分配内存等有状态资源通常不会因为 task 迁移就全部物理移动或简单重新归属。
- 官方 v2 指南因此建议按工作负载逻辑在启动时组织一次，再通过控制文件动态调节，而非频繁迁移。
- 运维工具必须理解 systemd slice/scope 与容器运行时层级，避免把进程移出其管理树。

## 11-正确性审查
Q: 关于 namespace 和 cgroup，哪些说法需要纠正？
A:
- “namespace 限制 CPU 和内存”错误；资源控制主要由 cgroup controller 完成。
- “cgroup 隔离进程看到的 PID 和网络”错误；这是 namespace 视图职责。
- “容器内 root 就是宿主 root”不一定；user namespace 可映射为普通宿主用户，但未启用时风险仍高。
- “cgroup v1/v2 只是文件名变化”错误；统一层级、委派和 controller 语义有重要差别。
