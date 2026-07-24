# OOM、内存泄漏与 Native Memory 排障

## 01-泄漏定义
Q: GC 语言为什么仍会发生内存泄漏？
A:
- GC 只能回收不可达对象；业务不再需要但仍被引用的对象对 GC 来说仍然存活。
- 常见根因包括无界缓存、监听器未注销、ThreadLocal 未清理、静态集合、ClassLoader 残留和任务队列堆积。
- 容量不足表现为所有对象都合理但总需求超过预算；泄漏表现为不应长期存活的对象持续增长。
- 两者可能同时存在，必须通过多时点 live set、对象年龄和引用链区分。
- 只看一次 heap dump 容易把正常峰值误判为泄漏。

## 02-堆排障链
Q: Java heap 持续增长时怎样建立证据链？
A:
1. 确认 GC 后 live set 是否跨周期单调增长，而不是仅看进程 RSS。
2. 用 class histogram 比较多个时间点的类数量和字节增长。
3. 在可控时机获取 heap dump，使用 dominator tree、retained size 和 path to GC roots。
4. 回到业务所有权：谁应释放、何时释放、为什么 Root 链仍存在。
5. 修复后用相同流量和时间窗口验证 live set 稳定，而不只验证 OOM 不再立即出现。

## 03-Metaspace泄漏
Q: Metaspace 持续增长为什么常与 ClassLoader 有关？
A:
- 类元数据生命周期通常绑定定义它的 ClassLoader；加载器可达时，其定义的类难以卸载。
- 热部署、脚本引擎、动态代理和字节码生成会创建大量类或加载器。
- ThreadLocal、线程上下文加载器、JDBC Driver、定时任务和框架全局缓存可能保留旧加载器。
- 用 `jcmd VM.classloader_stats`、class histogram、JFR 和 heap dump 找加载器数量及引用链。
- 只增加 MaxMetaspaceSize 会延迟故障，不能解决加载器泄漏。

## 04-NativeMemory
Q: Heap 正常但 RSS 持续增长，应检查哪些 native memory？
A:
- Metaspace/Compressed Class Space、Code Cache、线程栈、DirectByteBuffer、GC 辅助结构、JNI 和 native 库分配。
- glibc arena 和 allocator 碎片可能让已释放内存未立即归还操作系统。
- 开启 NMT 有运行成本，通常在可接受级别使用 summary，问题复现时做 baseline/diff。
- 将 `jcmd VM.native_memory summary` 与 `/proc`、容器 RSS、线程数和 direct buffer pool 对齐。
- heap dump 不包含大部分 native 分配，不能用“dump 很小”证明没有内存问题。

## 05-线程与队列泄漏
Q: 为什么线程池问题既可能表现为内存泄漏，也可能表现为 native OOM？
A:
- 无界工作队列会保留任务、参数和上下文，形成 Java heap 增长。
- 无界创建平台线程会消耗 native stack、地址空间和系统线程配额，最终无法创建线程。
- ThreadLocal value 生命周期可能跟随池线程，任务结束后仍被长生命周期线程引用。
- 阻塞任务占满线程后，上游继续提交会形成队列堆积和级联超时。
- 监控 active、pool size、queue size、oldest task age、reject 和 thread count，而不只看 CPU。

## 06-正确性审查
Q: OOM 排障有哪些错误捷径？
A:
- “有 GC 就不会泄漏”：错误，可达但无用对象不会被回收。
- “RSS 高就是 Java 堆高”：错误，native memory 可能占主要部分。
- “加大 Xmx 能解决 OOM”：可能挤压 native 余量或延后泄漏。
- “heap dump 最大对象就是根因”：应看 retained size、Root 链和业务生命周期。
- “OOMKill 一定有 Java OOM 日志”：错误，容器可能直接终止进程。
