# QUIC 连接、Stream、恢复与迁移

## 01-协议位置
Q: QUIC 为什么运行在 UDP 之上却仍是可靠传输？
A:
- UDP 只提供可部署的数据报承载，QUIC 用户态实现连接、ACK、重传、拥塞控制和多路 Stream。
- TLS 1.3 加密集成进握手，几乎所有传输元数据也受保护，HTTP/3 运行其上。
- 中间设备只需转发 UDP，协议可在用户态更快演进；UDP 被阻断时需回退。
- “UDP 不可靠所以 QUIC 不可靠”混淆了承载层和 QUIC 自身语义。

## 02-握手
Q: QUIC 如何减少建连时延？
A:
- 首次连接把传输参数与 TLS 1.3 握手结合，通常 1-RTT 建立安全连接并发送应用数据。
- 恢复连接可使用 0-RTT 提前数据，但存在重放风险，只适合幂等操作并由服务端策略接受。
- TCP+TLS1.3 也可优化，实际收益取决于连接复用、网络和证书链。
- 地址验证 token/Retry 用于防源地址伪造和放大，不应被当普通重定向。

## 03-多路Stream
Q: QUIC 怎样避免 HTTP/2 的连接级队头阻塞？
A:
- 每个 stream 有独立 offset 和有序交付，某 stream 丢包只阻塞该 stream 的缺口。
- UDP datagram 内可混合多个 stream frame，连接共享拥塞控制但不共享 TCP 字节序号。
- 网络层丢包仍降低整个连接可用带宽，不能说“完全没有 HOL”。
- stream/connection 两级流量控制防止接收内存被单流或总量耗尽。

## 04-恢复
Q: QUIC 丢包恢复为何使用 Packet Number Space 和 ACK range？
A:
- packet number 单调且不因重传复用，接收端 ACK ranges 精确报告已收区间，减少 TCP 重传歧义。
- 丢失 packet 中的 frame 可重新装入新 packet number，重传的是数据/控制 frame 而非原包副本。
- Initial、Handshake、Application 使用不同 packet number space，隔离密钥阶段。
- 加密使普通中间抓包难直接解析，需端点 key log 和 QUIC-aware 工具。

## 05-连接迁移
Q: QUIC Connection ID 如何支持客户端换 IP/端口？
A:
- 连接由不直接绑定五元组的 Connection ID 标识，移动网络/NAT rebind 后可继续关联原连接。
- 端点对新 path 做 PATH_CHALLENGE/RESPONSE 验证，防止把流量反射到伪造地址。
- 新路径 RTT/拥塞状态需重新评估，迁移不是无缝零成本。
- 负载均衡器需能按 CID 路由或编码后端信息，同时保护 CID 隐私和密钥。

## 06-边界
Q: QUIC 相比 TCP 的代价和部署风险是什么？
A:
- 用户态加密与包处理可能增加 CPU，虽可批量、GSO 和硬件卸载优化；内核 TCP 生态仍更成熟。
- 企业网络可能限速/屏蔽 UDP，路径 MTU、中间盒和可观测性工具支持也不同。
- HTTP/3 收益在高丢包、多路和移动场景更明显，稳定低 RTT 内网未必显著。
- 应做 TCP/QUIC 双栈回退、版本与指标分组，而非一次性替换。
