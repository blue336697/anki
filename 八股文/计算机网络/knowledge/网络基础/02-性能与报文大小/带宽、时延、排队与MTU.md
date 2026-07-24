# 带宽、时延、排队与 MTU

## 01-四类时延
Q: 一个分组的总时延由哪些部分组成？
A:
- 处理时延用于解析头和查表；排队时延取决于到达流量和队列；发送时延为报文长度/链路带宽。
- 传播时延约为距离/介质传播速度，与报文大小无关；跨洲 RTT 即使带宽很高也不会消失。
- 端到端还包括主机协议栈、调度、TLS 和应用处理，网络 RTT 不是请求总延迟。
- 排队接近饱和时会非线性增长，是 P99 抖动的常见来源。

## 02-带宽时延积
Q: Bandwidth-Delay Product 为什么决定“在途数据”规模？
A:
- BDP=瓶颈带宽×RTT，表示填满管道时尚未确认的字节量；高带宽长 RTT 链路需要较大窗口。
- TCP 发送窗口若小于 BDP，即使链路空闲也会因等待 ACK 不能继续发，吞吐受窗口/RTT 限制。
- socket buffer、receive window scaling 和 congestion window 都可能成为上限。
- 增大 buffer 不是无限有益，过量排队会造成 bufferbloat 和更差尾延迟。

## 03-吞吐与好吞吐
Q: throughput、goodput、PPS 和连接数为什么不能互相替代？
A:
- throughput 包含协议头与重传，goodput 只计算应用有效载荷；同样带宽下小包头部占比更高。
- PPS 衡量每秒分组数，小包可能未满带宽却先耗尽网卡/CPU 包处理能力。
- 连接数描述状态规模，不表示活跃请求率；大量空闲连接主要消耗内存和 keepalive 管理。
- 压测必须同时报告请求大小、并发、PPS、带宽、错误和延迟分位数。

## 04-MTU与MSS
Q: MTU、IP 报文长度和 TCP MSS 有什么关系？
A:
- MTU 是一条链路可承载的最大网络层报文大小，常见 Ethernet MTU 1500 但隧道/巨帧会变化。
- TCP MSS 是单个 segment 的最大 TCP payload，通常由 MTU 减 IP/TCP 基础头并在握手中通告。
- TCP options、IPv6 扩展头和隧道封装会改变有效空间；MSS clamping 常用于隧道边界。
- UDP 没有 MSS，应用要自行控制 datagram，过大可能触发 IP 分片或发送失败。

## 05-PMTUD黑洞
Q: Path MTU Discovery 如何工作，为什么会出现 MTU black hole？
A:
- IPv4 发送 DF 报文，路由器遇更小 MTU 丢弃并返回 ICMP fragmentation needed；IPv6 路由器本就不分片并返回 Packet Too Big。
- 发送端降低报文大小并缓存路径 MTU；PLPMTUD 可通过传输层探测减少对 ICMP 的依赖。
- 若防火墙错误丢弃必要 ICMP，大包无响应而小包正常，TCP 可能握手成功却传输卡住。
- 排障应比较不同 payload、抓 ICMP/PTB 并检查隧道额外头，不要只调应用超时。

## 06-排队与丢包
Q: 为什么“零丢包的大缓冲”可能比适度丢包更差？
A:
- 大 FIFO 在过载时保存大量旧包，RTT 和 P99 飙升；TCP 反馈变慢，应用超时后还继续处理过期请求。
- Drop-tail 只有队列满才突发丢包，可能让多个 TCP 同步降窗；AQM 提前标记/丢弃以控制排队。
- ECN 可在不丢包时显式通知拥塞，但要求端点和路径支持并正确配置。
- 稳定系统必须让长期到达率不超过服务率，队列只能吸收短时突发。

