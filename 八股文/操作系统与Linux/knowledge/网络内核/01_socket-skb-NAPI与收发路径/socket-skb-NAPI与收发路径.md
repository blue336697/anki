# Linux socket、sk_buff、NAPI 与网络收发路径

> 基线：本主题关注操作系统实现，不重复 TCP 协议状态机细节。驱动、XDP、offload 和内核版本会改变具体路径。

## 01-socket对象
Q: 用户 fd、`struct socket` 和 `struct sock` 有什么关系？
A:
- socket 系统调用创建 VFS file，用户得到整数 fd；file_operations 把 read/write/poll 等分派到 socket 层。
- `struct socket` 是 BSD socket/VFS 接口对象，保存类型、状态和协议操作表。
- `struct sock` 是网络协议核心状态，TCP 会嵌入/扩展为 tcp_sock，保存队列、窗口、定时器和拥塞控制状态。
- 一个连接不是只存在于 fd 数字中；关闭 fd 后协议对象还可能因 FIN、TIME_WAIT 或引用继续存在。

## 02-send路径
Q: 应用 `send()` TCP 数据后到网卡的主要路径是什么？
A:
1. 系统调用从用户 buffer 复制或引用数据，按 socket send buffer 和协议限制构建 skb。
2. TCP 分段/排队、拥塞与流量控制决定哪些数据可发送，IP 层完成路由和网络层处理。
3. qdisc/traffic control 排队后进入网卡驱动 `ndo_start_xmit`，映射 DMA 描述符并交给硬件队列。
4. 网卡完成发送后产生 completion，驱动释放 skb/页引用并唤醒受 send buffer 限制的写者。

## 03-send返回
Q: `send()` 返回成功为什么不代表对端应用已经收到？
A:
- 返回字节数通常表示数据已被本机 socket 发送缓冲接受，不等于已经离开网卡。
- TCP ACK 只证明对端 TCP 栈接收并确认序列空间，不代表对端用户进程 read 或业务提交。
- 网络断开后，部分已返回成功的数据仍可能因重传失败而最终丢失连接。
- 端到端业务确认需要应用协议响应、幂等和超时状态机，不能用 send 返回代替。

## 04-send-backpressure
Q: socket send buffer 满时阻塞和非阻塞调用分别怎样表现？
A:
- 阻塞 socket 会让任务睡眠等待 ACK/发送完成释放缓冲，或直到超时、信号和连接错误。
- 非阻塞 socket 返回 EAGAIN，事件循环在 EPOLLOUT 就绪后继续发送剩余数据。
- 一直监听 EPOLLOUT 常因 socket 大部分时间可写造成事件风暴，通常仅在有待发送数据且遇到 EAGAIN 后启用。
- 应用还要有自己的有界发送队列，否则只是把内核背压转移成用户堆内存膨胀。

## 05-RX硬件入口
Q: 网卡收到数据后为什么不在每个硬中断里处理完整协议栈？
A:
- 网卡 DMA 把包写入预先提供的 receive ring buffer，并触发 MSI-X 等中断通知 CPU。
- 驱动硬中断处理器确认状态、屏蔽/节制该队列中断并调度对应 NAPI poll。
- NAPI 在 budget 内批量收包和处理完成，队列清空后重新启用中断。
- 这把高包速率下的每包中断转为“中断触发 + 批量轮询”，避免 interrupt livelock。

## 06-NAPI
Q: NAPI budget 和 `ksoftirqd` 如何影响网络延迟？
A:
- NAPI poll 每轮最多处理给定 budget 的接收包，防止一个网卡队列长期独占 CPU。
- 常规处理多在 NET_RX softirq 上下文；软中断工作过多时会转由 `ksoftirqd/N` 线程继续。
- budget 太小增加调度/中断开销，太大可能延迟其他任务；高负载下 ksoftirqd 满核通常说明网络处理压力。
- 某些现代配置支持 threaded NAPI 或 busy polling，必须按网卡、内核与延迟目标验证。

## 07-sk_buff
Q: `sk_buff` 的结构为什么把 metadata 和 packet data 分开？
A:
- skb 本身保存协议头位置、设备、路由、校验、队列和引用等 metadata，数据位于 head buffer、page fragments 或 frag_list。
- `data/tail/end` 指针允许协议层 prepend/consume header，而不必每层重新分配整个包。
- clone 可复制 metadata 并共享只读数据页，写入前再处理 COW，降低转发和重传复制。
- 灵活结构代价是 metadata、引用和 cache miss；XDP 等快速路径会在更早阶段用更轻量表示。

## 08-RX协议路径
Q: 一个 TCP 包从 NAPI 到应用 recv queue 经过什么？
A:
- 驱动构建或附加 skb，GRO 可能聚合同流包，然后交给以太网、IP 层做协议、路由、过滤和分片处理。
- TCP 根据四元组查找 sock，校验序列、ACK 与状态，把有序 payload 排入 socket receive queue。
- 数据到达使等待队列就绪，唤醒阻塞 recv 或触发 epoll poll callback 把 fd 加入 ready list。
- 应用 recv 再从 socket queue 复制到用户 buffer；慢应用会让 receive buffer/窗口收缩并向对端施加背压。

## 09-GRO-GSO-TSO
Q: GRO、GSO、TSO 分别优化什么？
A:
- GRO 在接收侧把同流多个包合并为较大 skb，减少协议栈逐包处理开销。
- GSO 允许协议栈用大 skb 表示待发送数据，在较低层再软件或硬件分段。
- TSO 由网卡根据大 skb 和头部信息完成 TCP 分段，减少 CPU 构包与 DMA 描述符处理。
- 抓包点不同会看到“超 MTU 大包”或校验未完成，这是 offload 视图，不一定代表线上异常帧。

## 10-listen队列
Q: TCP listen socket 的 SYN 队列和 accept 队列分别存什么？
A:
- SYN backlog 保存握手尚未完成的半连接请求及重传状态，SYN cookie 可在压力下减少状态分配。
- 握手完成后连接进入 accept queue，等待应用调用 accept 取得新的 connected socket fd。
- 应用 accept 太慢会让完成队列溢出，即使网络和 CPU 看似正常也会出现连接失败或重传。
- backlog 参数还受 `somaxconn`、`tcp_max_syn_backlog` 和内核截断语义影响，不能只改应用一个数字。

## 11-多队列与亲和性
Q: RSS、RPS、RFS、XPS 和 IRQ affinity 分别在解决什么？
A:
- 网卡 RSS 按流 hash 把接收包分到硬件 RX queue；每队列 IRQ 可绑定 CPU，形成并行入口。
- RPS 在软件层把接收处理分发到其他 CPU，RFS进一步考虑处理该流的应用 CPU，提高 cache 亲和。
- XPS 为发送选择合适 TX queue/CPU 映射，减少队列锁和跨核 cache 迁移。
- 配置不匹配 NUMA、应用绑核或队列数会制造单核 softirq 热点，需结合 `/proc/interrupts` 和队列统计调优。

## 12-drop定位
Q: Linux 网络丢包可能发生在哪些层？
A:
- 网卡 ring 来不及回收会发生 hardware/driver drop；NAPI/softnet backlog 溢出会在协议栈入口丢。
- qdisc 队列满、traffic control、路由/防火墙、邻居表和内存分配失败都可能丢包。
- socket receive buffer 满说明应用读取慢，UDP 会直接丢，TCP 则通过窗口/重传表现为延迟。
- `ethtool -S`、`/proc/net/softnet_stat`、`ss -m/-i`、nstat、drop tracepoint 要按层对齐，不能只看一个网卡计数。

## 13-正确性审查
Q: 关于 Linux 网络栈，哪些说法需要纠正？
A:
- “网卡每收一个包都完整执行一次硬中断协议栈”错误；现代 Linux 主要用 NAPI 批量处理。
- “send 成功表示对端业务收到”错误；通常只进入本机发送缓冲。
- “epoll 可读说明一次 read 能拿到完整业务包”错误；TCP 是字节流，应用仍需协议拆包。
- “抓包看到大于 MTU 就一定网络发了巨帧”错误；可能是 GRO/GSO/TSO 抓包视角。
