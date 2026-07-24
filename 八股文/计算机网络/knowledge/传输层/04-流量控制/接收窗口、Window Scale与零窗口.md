# 接收窗口、Window Scale 与零窗口

## 01-rwnd
Q: TCP receive window 解决什么问题？
A:
- 接收端用 ACK Window 字段通告从 ack number 起还能接收多少字节，避免发送端淹没接收缓冲。
- 发送端可用窗口受 `min(rwnd,cwnd)` 限制：rwnd 是接收能力，cwnd 是网络拥塞能力。
- 应用读得慢会让接收缓冲占用升高、rwnd 缩小，形成端到端背压。
- ACK 到达只表示内核接收，不表示业务消费，rwnd 正是连接这两层速度差的机制。

## 02-WindowScale
Q: 为什么需要 Window Scale option？
A:
- TCP 头窗口字段只有 16 位，不扩展最大约 64KiB；高 BDP 链路无法填满。
- 握手中双方分别协商 scale，后续窗口字段左移对应位数得到实际窗口。
- scale 只在 SYN 阶段协商，抓中途流量若不知道握手会误读窗口。
- 扩大 rwnd 需相应 socket buffer 和应用处理能力，否则只增加排队内存。

## 03-零窗口
Q: 接收端通告 zero window 后连接如何恢复？
A:
- 发送端停止新数据但保留连接，启动 persist timer，周期发送 window probe 防止窗口更新 ACK 丢失后永久死锁。
- 接收应用读走数据后，内核发送 window update；发送端据新 rwnd 继续。
- 长时间 zero window 常表示接收应用卡住、GC/线程池阻塞或 buffer 太小，不一定是网络拥塞。
- 抓包中的 ZeroWindow、WindowFull 与重传应结合 socket queue 和进程栈分析。

## 04-SillyWindow
Q: Silly Window Syndrome 如何产生，怎样避免？
A:
- 接收端频繁通告极小窗口，或发送应用不断写很小数据，导致大量小 segment 和高头部/处理开销。
- 接收端可等释放足够空间再更新窗口；发送端 Nagle/聚合可减少小包。
- 低延迟交互可能主动禁用 Nagle，但应让协议批量与 framing 设计承担成本。
- 避免 SWS 是吞吐优化，不应因此让应用等待无限时间。

## 05-Autotuning
Q: socket buffer autotuning 为什么仍可能需要人工检查？
A:
- 内核根据 RTT、吞吐和内存压力动态扩大接收/发送缓冲，以适应不同 BDP。
- 系统级 max、容器限制、应用 SO_RCVBUF/SO_SNDBUF 和内存压力可能限制最终容量。
- 大量连接每个大 buffer 会消耗巨大内存，配置应按活跃连接与流量分布评估。
- `ss -ti` 的窗口、cwnd、rtt、send/recv queue 比只看 sysctl 更能说明单连接瓶颈。

## 06-与拥塞控制
Q: 流量控制和拥塞控制为什么不能混为一谈？
A:
- 流量控制保护接收主机，由 rwnd/应用消费驱动；拥塞控制保护网络，由丢包、ECN、RTT/带宽信号驱动。
- 最终发送量同时受两者约束，`rwnd<cwnd` 是 receiver-limited，反之可能 congestion/application-limited。
- 增大接收窗口无法修复路径丢包，增大 cwnd 也无法让卡住的接收应用变快。
- 排障要分别看 receiver window、congestion state、发送队列和应用写入速率。
