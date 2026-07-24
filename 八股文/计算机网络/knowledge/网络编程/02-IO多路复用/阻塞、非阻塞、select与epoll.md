# 阻塞、非阻塞、select 与 epoll
## 01-四组概念
Q: blocking/nonblocking 与 synchronous/asynchronous 为什么不是同一维度？
A:
- 阻塞描述调用在条件未满足时是否挂起线程；同步描述完成工作是否仍由调用线程推进并获取结果。
- 非阻塞 read 返回 EAGAIN 只是“现在没数据”，通常配合 readiness multiplexer。
- epoll 通知就绪后应用仍同步 read/write；真正异步接口提交操作后由完成事件通知。
- Java NIO、Linux AIO/io_uring 和理论术语要按具体 API 语义说明。
## 02-selectpoll
Q: select/poll 每轮调用的主要成本是什么？
A:
- select 复制并扫描 fd_set，受固定 fd 上限/位图影响；poll 传数组并线性扫描 revents。
- 每次通常把关注集合从用户态交给内核，再遍历找 ready，连接多而活跃少时成本高。
- 它们接口可移植且小规模足够，复杂度并不意味着任何场景都比 epoll 慢。
- fd 被关闭/复用和多线程修改监听集合仍需生命周期同步。
## 03-epoll内部
Q: epoll 为什么适合大量连接？
A:
- `epoll_ctl` 把关注 fd 注册在内核 epoll 实例，事件发生时回调把条目放 ready list。
- `epoll_wait` 主要取得就绪项，无需每轮线性扫描全部注册 fd，适合大量空闲连接。
- 注册结构和 ready queue 仍占内存，热点 fd、惊群与事件处理成本不会消失。
- epoll 提供 readiness，不缓存业务消息，也不自动读取 socket。
## 04-LTET
Q: Level Trigger 与 Edge Trigger 的处理规则是什么？
A:
- LT 只要条件仍满足会重复通知，容错直观；ET 通常只在状态由未就绪变就绪时通知。
- ET 必须非阻塞并循环 read/accept 到 EAGAIN，否则剩余数据可能没有新边沿而长期滞留。
- 写事件不应永久注册，否则缓冲常可写会造成 busy loop，应只在有未写数据时关注。
- ONESHOT 多线程处理后需显式 rearm，避免同 fd 并发处理。
## 05-就绪竞态
Q: 为什么 epoll 通知可读后 read 仍可能 EAGAIN？
A:
- 另一线程/回调可能已读走数据，RST/错误/关闭也会改变状态；ready 是瞬时观察而非资源预留。
- 非阻塞调用必须把 EAGAIN 当正常竞态，循环状态机不能假设一次事件对应一次成功 IO。
- fd number 关闭后可被复用，新对象误继承旧业务映射会产生严重 bug，应使用 generation/对象生命周期。
- EPOLLERR/HUP 即使未显式注册也需处理，并继续读取 SO_ERROR/剩余数据。
## 06-线程模型
Q: Reactor 如何把 epoll 与业务线程池组合而不被慢任务拖死？
A:
- event loop 只做 accept、非阻塞收发、协议解析与任务分发，避免阻塞磁盘/远程调用。
- 每连接状态机保存半包、待写队列和 backpressure；业务完成再安全回到所属 event loop。
- 线程池无界队列会把过载变成延迟/OOM，应限制在途请求并暂停读或拒绝。
- 多 reactor 可按 fd/连接分片到 CPU，减少共享锁但要处理跨线程唤醒。

