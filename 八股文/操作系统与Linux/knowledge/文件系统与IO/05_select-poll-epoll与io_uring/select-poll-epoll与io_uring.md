# select、poll、epoll 与 io_uring

> 基线：select/poll/epoll 主要是 readiness 模型；io_uring 是提交/完成模型。非阻塞、同步、异步和多路复用要分开描述。

## 01-阻塞与非阻塞
Q: blocking fd 和 `O_NONBLOCK` 改变什么？
A:
- 阻塞调用在当前无法完成时让 task 睡眠，事件到来后唤醒并继续。
- 非阻塞调用不等待，当前无数据/空间时返回 `EAGAIN/EWOULDBLOCK`，应用决定稍后重试。
- 非阻塞并不自动通知何时重试，忙循环会浪费 CPU，通常结合 poll/epoll readiness。
- 普通磁盘文件即使设置 O_NONBLOCK，也可能因缺页、文件系统或设备路径阻塞，语义主要对 socket/pipe 等明显。

## 02-readiness与completion
Q: readiness I/O 和 completion I/O 有什么本质区别？
A:
- readiness 通知“现在执行 read/write 很可能不会因等待该事件而阻塞”，应用仍需自己调用 IO。
- completion 模型先提交具体 read/write 操作，系统在操作完成后返回结果和字节数。
- epoll 管理 fd 事件就绪，io_uring 的 SQE/CQE 管理异步操作请求与完成。
- readiness 之后仍可能因多线程竞争、边缘状态变化或其他内核工作返回 EAGAIN，必须循环处理。

## 03-select
Q: select 的主要工作方式和限制是什么？
A:
- 用户每次传入读写异常 fd_set，内核扫描集合、把当前 ready 位写回，再返回就绪数量。
- fd_set 通常受 `FD_SETSIZE` 和位图表示限制，调用后集合被修改，下一轮需重新构造。
- 每次复制整个位图并线性扫描到最大 fd，在大量连接但少量活跃时开销明显。
- 它具备广泛可移植性，少量 fd 场景仍可用，不应只用 O(n) 标签否定所有使用。

## 04-poll
Q: poll 相比 select 改进和未改进什么？
A:
- poll 使用 `pollfd` 数组，没有固定 fd 位图上限，并为每个条目返回 revents。
- 但每次调用仍需把数组交给内核并线性检查，内核也不长期保存应用 interest set。
- 大量稳定连接每轮重复注册/扫描，稀疏活跃场景扩展性仍有限。
- select/poll 返回后应用都要遍历找 ready 项，复杂度与监控集合相关。

## 05-epoll结构
Q: epoll 为什么适合大量长连接？
A:
- `epoll_ctl` 把 interest 长期注册到内核 epoll 对象，概念上以树等结构管理监控项，不必每次传全量集合。
- 目标 fd 状态变化时，其 poll wait 回调把 epitem 加入 ready list，并唤醒等待 epoll_wait 的任务。
- `epoll_wait` 主要取 ready list 中事件，成本更接近活跃 fd 数量，而非每轮扫描所有连接。
- 注册、修改、删除、回调和多线程并发仍有锁与生命周期成本，epoll 不是严格 O(1) 魔法。

## 06-LT与ET
Q: epoll level-triggered 和 edge-triggered 有什么差别？
A:
- LT 只要条件仍满足就可重复报告，应用一次没有读完，下次 wait 仍能得到事件，逻辑容错更高。
- ET 主要在状态从未就绪变为就绪的边缘通知，应用通常需非阻塞循环读/写直到 EAGAIN。
- ET 若只读一次就返回事件循环，缓冲仍有数据但没有新边缘，连接可能永久停滞。
- ET 减少重复通知不保证一定更快；批量大小、系统调用和应用状态机决定实际收益。

## 07-EPOLLONESHOT
Q: 多线程事件循环为什么使用 EPOLLONESHOT？
A:
- 一个 fd 就绪时可能被多个 worker 观察，两个线程同时读写同一连接会破坏协议状态。
- ONESHOT 在交付一次事件后暂时禁用该监控项，处理线程完成并更新兴趣后显式 rearm。
- 它简化同连接串行处理，但忘记 rearm 会让连接再也没有事件。
- 也可用连接所有权分片、单 event loop 等模型避免并发，ONESHOT 不是唯一方案。

## 08-惊群
Q: 多个进程/线程等待同一监听 socket 时怎样减少惊群？
A:
- 如果一次连接到来唤醒大量 waiter，只有一个 accept 成功，其余线程被无效唤醒并争锁。
- epoll 的独占唤醒选项、SO_REUSEPORT 多监听队列、accept mutex 或单 acceptor 分发可降低竞争。
- 现代内核已在多处优化唤醒，但应用拓扑仍决定 cache 和负载均衡效果。
- “epoll 自动彻底消除惊群”过于绝对，必须说明是否共享 epoll 实例和监听 fd。

## 09-io_uring结构
Q: io_uring 的 SQ、CQ、SQE、CQE 分别是什么？
A:
- Submission Queue 指向应用准备的 SQE，每个 SQE 描述 read、write、accept、timeout 等一个操作。
- 内核消费提交并执行，完成后把结果写入 Completion Queue 的 CQE，应用按 user_data 关联请求。
- 环形队列通过 mmap 与用户空间共享头尾索引，可批量提交/收割，减少系统调用和对象复制。
- 共享 ring 仍需正确内存序、容量与生命周期管理，不能在 CQ 满或 buffer 被复用时继续覆盖。

## 10-io_uring优化
Q: fixed file、registered buffer 和 SQPOLL 分别优化什么？
A:
- 注册文件把 fd 解析和引用预先固定，减少每个请求查表；注册 buffer 固定/映射内存，降低重复 pin 和映射开销。
- SQPOLL 使用内核线程轮询 submission queue，一段时间内应用提交可不发系统调用，但会消耗 CPU。
- buffer selection、多 shot 操作和 linked SQE 可进一步减少往返，但错误取消和资源回收更复杂。
- 功能、限制和安全修复随内核快速演进，生产必须确认发行版内核与 liburing 版本。

## 11-backpressure
Q: 高性能异步 I/O 为什么必须设计背压？
A:
- 提交速度超过设备/下游完成速度时，SQ、内核请求、buffer、连接状态和 CQ 会持续占用资源。
- 只追求最大 queue depth 会放大尾延迟和超时取消成本，并让故障恢复同时完成大量过期请求。
- 应限制每连接和全局在途数，CQ 接近容量时停止提交，按 deadline 取消并安全处理迟到 completion。
- user_data 标识必须防止对象释放后 CQE 到达造成 use-after-free。

## 12-正确性审查
Q: 关于 epoll 和 io_uring，哪些说法需要纠正？
A:
- “epoll 是异步 IO”不准确；它主要报告 readiness，实际 read/write 仍由应用发起。
- “ET 一定比 LT 高性能”错误；ET 更依赖正确 drain 状态机，业务模式决定收益。
- “epoll 完全没有遍历”错误；它避免每轮扫描全部 interest，但仍处理 ready list 和用户事件数组。
- “io_uring 完全零系统调用、零拷贝”错误；可批量/轮询降低调用，数据复制取决于具体操作与 buffer 策略。
