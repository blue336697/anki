# IPv4 头部、分片与 PMTUD

## 01-头部字段
Q: IPv4 头部哪些字段直接参与转发和交付？
A:
- Version/IHL 定义格式长度，Total Length 定义整个 datagram；Protocol 指示 TCP、UDP、ICMP 等上层。
- Source/Destination 用于寻址，TTL 每跳减一，归零时丢弃并通常返回 ICMP Time Exceeded。
- Header checksum 只覆盖 IPv4 头，每跳因 TTL 变化需更新；TCP/UDP 校验还覆盖 payload 和伪首部。
- DSCP/ECN 用于服务分类和拥塞通知，但是否生效取决于整条路径策略。

## 02-尽力而为
Q: IP 的 best-effort 具体不保证什么？
A:
- IP 不保证到达、顺序、唯一、时延和带宽，路由器可因拥塞、MTU、ACL、TTL 或故障丢包。
- 每个 datagram 独立转发，路径可变化；可靠性、重组和业务幂等由传输层/应用承担。
- best-effort 不等于随机或无质量，运营网络仍通过路由、队列、冗余和 QoS 提供工程目标。
- TCP 的可靠字节流建立在这个不可靠 datagram 服务之上。

## 03-分片字段
Q: IPv4 分片怎样用 Identification、MF 和 Fragment Offset 重组？
A:
- 源或路由器把过大 datagram 切片，各片共享 Identification，MF 表示后面还有片，offset 以 8 字节为单位。
- 目的主机按源/目的/protocol/ID 等重组；任一片丢失通常导致整个原报文超时丢弃。
- 每片有独立 IP 头，放大带宽、CPU 和攻击面；中间 NAT/防火墙也更难检查后续片。
- TCP 通常通过 MSS/PMTUD 避免 IP 分片，应用也应控制 UDP datagram。

## 04-DF与PMTUD
Q: IPv4 DF 与 Path MTU Discovery 如何避免中间分片？
A:
- 发送端设置 DF，若下一跳 MTU 太小，路由器丢包并发送 ICMP Fragmentation Needed，携带可用 MTU。
- 主机降低分组尺寸/MSS 后重试，并为目的路径缓存 PMTU；路径变化后需要重新发现。
- ICMP 被过滤会形成大包黑洞：握手/小请求成功，传输大响应卡住并重传。
- PLPMTUD 在传输层用探测与确认推断可用大小，降低对 ICMP 完整可达的依赖。

## 05-校验卸载
Q: 为什么本机 tcpdump 可能显示 IPv4/TCP checksum incorrect？
A:
- 发送抓包点可能位于网卡完成 checksum offload 之前，内存 skb 中校验字段尚未最终填写。
- 接收端也可能由网卡验证并用元数据告诉内核，抓包工具显示方式依位置和驱动。
- 若对端实际接收正常且线上抓包校验正确，本机“bad checksum”不代表网络损坏。
- 排障应同时检查 offload 配置、不同抓包点和网卡错误计数。

## 06-正确性审查
Q: 关于 IPv4 分片最常见的错误说法是什么？
A:
- “超过 MTU 一定由路由器分片”错误：DF、IPv6、隧道和设备策略可能直接丢弃。
- “分片丢一个只重传那一片”错误：IP 无可靠重传，TCP 最终通常重传相关完整 segment 数据。
- “MTU=TCP payload”错误：还要扣除 IP/TCP/options/隧道头，MSS 才是 TCP payload 上限。
- “ping 小包通即 MTU 正常”错误，应使用 DF 与不同 payload 专门探测。

