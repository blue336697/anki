# JVM 参数、统一日志与 GC 诊断

> 基线：JDK 21/25。优先使用 JEP 158/271 统一日志，不再以 CMS 专用参数作为主线。

## 01-参数分层
Q: 线上 JVM 参数应按什么层次设计？
A:
- 容量层：`-Xms/-Xmx`、Metaspace、Direct Memory、线程栈和容器总内存之间必须有完整预算。
- 收集器层：明确 G1、ZGC 或 Parallel；先使用合理默认值建立基线，避免复制不理解的参数模板。
- 可观测层：统一 GC 日志、OOM heap dump、错误日志、JFR 和必要的 Native Memory Tracking。
- 稳定性层：容器感知、退出策略、熔断/重启、磁盘空间和日志轮转，避免诊断功能反过来拖垮节点。
- 参数值必须与 JDK 发行版、容器 CPU/内存限制和真实工作负载一起版本化。

## 02-容器内存预算
Q: 已设置 `-Xmx`，为什么 Java 进程仍会被容器 OOMKill？
A:
- `-Xmx` 只限制 Java heap，不包含 Metaspace、Code Cache、线程栈、Direct Buffer、GC 辅助结构、JNI 和 libc。
- 可近似建模：`RSS ≈ heap committed + metaspace + code cache + thread stacks + direct/native + JVM overhead`。
- 平台线程数乘以 `-Xss` 会形成显著地址空间与提交内存；大量虚拟线程不一线程一 OS 栈，但其 continuation/对象仍占堆。
- 容器限制应高于稳定 RSS 并保留突发和 native allocator 碎片余量；不要让 `Xmx` 等于容器上限。
- OOMKill 往往没有 Java 异常，排查需结合 cgroup memory events、内核日志和进程级指标。

## 03-统一GC日志
Q: JDK 21 怎样配置一份可用于生产诊断的 GC 日志？
A:
```text
-Xlog:gc*,safepoint:file=logs/gc.log:time,uptime,level,tags:filecount=10,filesize=100M
```
- `gc*` 覆盖 GC 周期、阶段和堆变化，`safepoint` 帮助区分 GC 暂停与其他 VM 操作暂停。
- `time/uptime/level/tags` 让多实例、重启和事件关联更可靠；文件轮转防止磁盘被无限占满。
- 更细日志会增加 I/O 与体积，临时诊断后应回收过高 verbosity。
- `-XX:+PrintGCDetails` 等旧参数属于旧日志体系，阅读历史日志时可识别，但新配置应优先 `-Xlog`。

## 04-读懂一次GC
Q: 分析 GC 日志时应按什么顺序建立因果链？
A:
1. 识别收集器、GC 类型和触发原因：allocation failure、metadata threshold、System.gc、humongous 等。
2. 比较 GC 前后 used、committed 和 live set，判断本轮释放量与长期存活集。
3. 看暂停各阶段耗时、worker CPU 与墙钟差异，识别扫描、复制、引用处理或调度问题。
4. 计算 allocation rate、晋升速率和周期频率，判断应用产生垃圾的速度是否超过回收能力。
5. 联合请求 p99、CPU throttle、磁盘、容器内存和发布事件；单条 GC 记录很少能独立证明根因。

## 05-G1诊断
Q: G1 日志中哪些信号意味着需要优先排查应用而不是继续调参数？
A:
- Young GC 极频繁且回收后占用很低：分配速率高，先定位临时对象、序列化和批量数据处理。
- Mixed GC 后老年代下降有限：live set/缓存真实过大，或并发标记启动太晚，需要容量和对象生命周期分析。
- Humongous Region 持续增长：检查大数组、大 JSON/ByteBuffer、批量查询结果和 Region 尺寸关系。
- To-space exhausted、evacuation failure 或 Full GC：疏散余量不足，可能由晋升突增、堆过紧或 CPU 跟不上引起。
- RSet/卡处理时间高：跨区引用写密集；需要看对象图和写入模式，而不是只调暂停目标。

## 06-ZGC诊断
Q: ZGC 重点看哪些指标？为什么暂停很短仍可能请求变慢？
A:
- 看 allocation rate、live set、GC cycle duration、并发 GC CPU 和 allocation stall，而不只看 pause。
- 并发 GC 与业务争抢 CPU 时，请求延迟可上升但 GC pause 仍很短；容器 throttle 会放大这种现象。
- 堆余量不足时应用可能等待 GC 腾出空间，形成 allocation stall。
- Generational ZGC 还应观察年轻/老年代行为和晋升压力，不能套用非分代 ZGC 的旧图景。
- 低暂停指标只说明 VM 停顿短，不代表端到端延迟一定低。

## 07-OOM与现场保全
Q: 线上发生 OOM 时怎样保全现场而不制造二次故障？
A:
- 可配置 `-XX:+HeapDumpOnOutOfMemoryError` 和可控的 dump 路径，但必须评估文件大小、磁盘空间和写盘时间。
- `HeapDumpPath` 指向有容量、权限和采集流程的持久卷；不要默认写满容器根盘。
- heap dump 适合堆对象问题；Metaspace/线程/native 问题还需要 classloader stats、thread dump、NMT 和系统指标。
- 明确 OOM 后是否退出并由编排系统重启；半失效进程继续接流量通常比快速失败更危险。
- dump 可能包含用户数据、密钥和业务内容，传输、存储与访问必须按敏感数据治理。

## 08-正确性审查
Q: JVM 调优中哪些动作风险最高？
A:
- 不理解就复制几十个 `-XX` 参数，会冻结旧版本经验并干扰新 JDK 自适应策略。
- 只看平均暂停，忽略 p99/p999、GC CPU、allocation stall 和业务吞吐。
- 看到 OOM 就增加堆，可能挤压 native memory 并延长最坏停顿。
- 继续教授 `UseConcMarkSweepGC`、`CMSInitiatingOccupancyFraction` 等 CMS 参数作为当前方案。
- 没有压测与回滚基线就一次修改多项参数，最终无法判断哪个变化产生效果。
