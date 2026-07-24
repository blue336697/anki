# TCP 握手、挥手与状态机

## 01-三次握手
Q: TCP 三次握手分别确认什么？
A:
- 客户端 SYN 携带初始序号 x 和 options；服务端 SYN-ACK 确认 x+1 并给出自己的 y/options。
- 客户端 ACK y+1 后，双方都确认双向收发能力、序号空间和协商参数，连接进入 ESTABLISHED。
- SYN 本身消耗一个序号，数据可在特定扩展下提前携带，但经典模型先握手后数据。
- 两次不足以让服务端确认其 SYN 到达客户端，也更难排除历史重复连接。

## 02-ISN与旧包
Q: Initial Sequence Number 为什么不能固定为 0？
A:
- ISN 随时间/连接 tuple 变化，降低旧连接残留 segment 被新同四元组连接误接受的概率。
- 难预测 ISN 也提高伪造 TCP segment 的门槛，但不是加密认证。
- 接收窗口和 PAWS timestamp 等进一步限制旧包；TIME_WAIT 阻止四元组过早复用。
- 序号是 32 位模空间，比较必须考虑窗口范围而非普通整数大小。

## 03-SYNBacklog
Q: 服务端收到 SYN 后，半连接队列和 accept 队列分别保存什么？
A:
- SYN backlog 保存握手未完成请求及重传状态；最终 ACK 到达后建立完整 child socket。
- 完成连接进入 accept queue，等待应用 accept；其容量和耗尽行为依内核实现与配置。
- backlog 参数不是简单“最大连接数”，会被内核上限、syncookies 和队列语义共同影响。
- 半连接溢出与应用 accept 太慢是两类问题，应看 SYN_RECV、ListenOverflows/Drops 和队列。

## 04-SYNCookie
Q: SYN Cookie 如何缓解 SYN flood，有什么代价？
A:
- 服务端不为初始 SYN 保存完整状态，把必要信息编码进 SYN-ACK 的序号；合法 ACK 返回后再重建连接。
- 它避免大量伪造源 SYN 占满半连接内存，通常在队列压力时启用。
- 可编码的 options 信息有限，现代实现虽有扩展，仍不是替代防火墙、限速和容量治理的万能方案。
- Cookie 只保护握手状态，真实源完成握手后的连接/应用资源攻击仍存在。

## 05-四次挥手
Q: TCP 关闭为什么通常是四个 segment，半关闭是什么？
A:
- TCP 双向字节流独立关闭；一方 FIN 表示“我不再发送”，对方 ACK 后仍可继续发送剩余数据。
- 对方完成发送再发 FIN，初始方 ACK；ACK 与 FIN 若时机相邻也可合并，所以抓包不一定严格四包。
- `shutdown(SHUT_WR)` 触发半关闭而仍可读，适合用 EOF 表示请求结束的协议。
- `close` 的实际 FIN 时机还受发送缓冲、linger、引用和进程行为影响。

## 06-异常关闭
Q: FIN、RST、超时分别代表怎样的连接终止？
A:
- FIN 是有序关闭，之前字节仍应被接收；应用 read 返回 EOF 表示对端发送方向结束。
- RST 立即中止，未读/未确认数据可能丢失，常见于无监听端口、非法 segment 或 abortive close。
- 网络静默断开没有 FIN/RST，只能靠重传耗尽、keepalive 或应用 heartbeat 超时发现。
- 收到 RST 不应笼统归因“网络断了”，需看谁发送及前一个包为何触发。

