# TCP 序号、ACK、重传与 SACK

## 01-字节序号
Q: TCP 序号为什么按字节而不是按报文计数？
A:
- TCP 向应用提供连续字节流，segment 边界可因 MSS、TSO、重传而变化，字节序号保持语义稳定。
- Sequence Number 指本 segment 第一个数据字节；SYN/FIN 各占一个序号空间位置。
- 接收端可按序号重组乱序片段、去重重传，并只向应用交付连续前缀。
- 应用消息边界必须自行用长度、分隔符或固定格式定义，不能依赖一次 send 对应一次 recv。

## 02-累计确认
Q: TCP cumulative ACK 的 ack number 表示什么？
A:
- ACK=N 表示 N 之前所有字节已连续收到，下一期待字节是 N；不直接证明 N 之后乱序数据不存在。
- 累计确认使某些 ACK 丢失也无须重传，后续更大 ACK 可覆盖。
- 中间缺口会让接收端重复 ACK 同一 N，即使后面数据已到；这给快速重传提供信号。
- ACK 表示进入接收协议栈缓冲，不等于对端应用已经处理或持久化。

## 03-RTO
Q: TCP Retransmission Timeout 怎样根据 RTT 动态估计？
A:
- 维护平滑 RTT 与 RTT variance，RTO 结合两者并受最小/最大值限制，适应路径抖动。
- 重传后的 ACK 无法判断确认原包还是重传包，Karn 思路避免用歧义样本更新 RTT；timestamp 可改善测量。
- 超时后重传并指数退避，防止拥塞时高频重发进一步压垮网络。
- 固定应用超时不能代替 TCP RTO；应用可能在内核仍重传时先放弃请求。

## 04-快速重传
Q: Duplicate ACK 如何触发 Fast Retransmit？
A:
- 某 segment 丢失但后续 segment 到达，接收端因缺口持续 ACK 同一 next expected sequence。
- 发送端收到若干 dupACK 后不等 RTO，推断缺口并重传，显著降低单包丢失恢复时间。
- 包乱序也会产生 dupACK，所以阈值是误判与恢复速度折中；现代算法还结合 SACK/RACK。
- 若窗口内后续包太少，无法产生足够 dupACK，仍可能依赖 tail loss probe 或 RTO。

## 05-SACK
Q: SACK option 相比累计 ACK 多提供什么信息？
A:
- 接收端用区间报告已收到的非连续字节块，让发送端知道缺哪些洞而不是重复发送整个后缀。
- 握手协商 SACK permitted，后续 ACK 携带有限数量 block；累计 ACK 仍作为主前缀边界。
- 多包丢失时 SACK 显著提高恢复效率，scoreboard 跟踪已确认区间。
- SACK 不改变 TCP 有序交付，缺口未补齐前后续字节仍不能交给同一流应用。

## 06-重复与乱序
Q: TCP 如何处理重复、乱序和 checksum 错误 segment？
A:
- checksum 错误通常直接丢弃不 ACK；发送端最终通过重复 ACK/超时重传。
- 乱序数据在接收缓存排队并 SACK/重复 ACK，缺口补齐后合并交付；缓冲和策略有限。
- 已确认范围的重复 segment 被识别并再次 ACK，不会把字节重复交给应用。
- TCP 保证单连接字节顺序，不保证应用操作幂等；超时重试新连接仍可能重复业务请求。

