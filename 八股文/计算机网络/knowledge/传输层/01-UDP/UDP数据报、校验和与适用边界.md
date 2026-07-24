# UDP 数据报、校验和与适用边界

## 01-报文结构
Q: UDP 头部有哪些字段，为什么只有 8 字节？
A:
- Source Port、Destination Port 用于进程复用，Length 覆盖头与数据，Checksum 检测传输错误。
- UDP 不保存序号、确认、窗口和连接状态，所以头短、协议栈处理简单。
- 一次 send 通常对应一个 datagram，接收端一次 recv 得到一条消息或被缓冲区截断，不是字节流。
- “无连接”指无握手和协议连接状态，不代表 socket 不能调用 connect 固定对端。

## 02-校验和
Q: UDP checksum 为什么包含 IP 伪首部？
A:
- 伪首部包含源/目的 IP、协议号和 UDP 长度，防止数据正确却被交给错误地址/协议。
- IPv4 中 UDP checksum 可按规则为 0 表示未使用，IPv6 中通常是必需的。
- checksum 主要检测随机传输错误，不提供密码学完整性，攻击者可重新计算。
- 网卡 offload 会让发送端本机抓包显示未完成校验，需结合抓包位置判断。

## 03-无可靠机制
Q: UDP 不提供哪些 TCP 能力，应用如何按需补齐？
A:
- 不保证到达、顺序、去重、流量控制和拥塞控制；datagram 还可能因 MTU 过大分片丢失。
- 实时媒体可接受丢包并用序号/抖动缓冲/FEC；RPC 可加 request ID、超时、重试和幂等。
- 自研可靠 UDP 还必须处理拥塞与公平性，否则会在网络过载时放大故障。
- QUIC 正是在 UDP 之上实现加密、可靠流、多路复用与拥塞控制的标准化传输。

## 04-ConnectUDP
Q: 对 UDP socket 调用 connect 有什么效果？
A:
- 内核记录默认对端，send/recv 可省地址参数，并通常只接收该 peer 的 datagram。
- 路由/源地址可提前确定，异步 ICMP 错误更容易映射给该 socket；它不发送握手包。
- 对端不存在时首次 send 仍可能成功，稍后收到 Port Unreachable 才在调用中体现。
- UDP connect 不创建双方共享状态，也不保证 NAT 映射长期存在。

## 05-放大与分片
Q: UDP 为什么常用于反射放大攻击，怎样缓解？
A:
- 攻击者伪造受害者源 IP 向公开 UDP 服务发小请求，服务把更大响应发给受害者。
- 无握手让服务难以先验证源地址可达；DNS/NTP 等曾产生高 amplification factor。
- 部署源地址反欺骗、响应速率限制、cookie/challenge、关闭开放递归并控制响应大小。
- 应用 datagram 尽量小于路径 MTU，分片会提高丢失和防火墙绕过风险。

## 06-选型
Q: 何时选择 UDP 而不是 TCP？
A:
- 消息边界重要、允许部分丢失、低延迟优先或需要 multicast/broadcast 时可考虑 UDP。
- 若应用最终又实现复杂可靠、有序和拥塞控制，应优先成熟 TCP/QUIC，避免重复造协议。
- DNS 不等于永远 UDP，响应截断、DNSSEC 和 zone transfer 会用 TCP，现代也有 DoT/DoH。
- 选择应基于语义和网络环境，不是“UDP 一定快、TCP 一定慢”。

