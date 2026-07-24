# TIME_WAIT、Keepalive、Nagle 与 Delayed ACK

## 01-TIMEWAIT
Q: 主动关闭方为什么进入 TIME_WAIT？
A:
- 保留约 2MSL 时间吸收旧 segment，防止相同四元组新连接误收历史包。
- 若最后 ACK 丢失，对端会重发 FIN，TIME_WAIT 端可再次 ACK，保证可靠关闭。
- 它占用四元组/内核状态但通常不是服务端并发连接本身，是否集中取决于谁主动关闭。
- 粗暴复用/缩短可能引入旧包污染，应优先连接复用和扩展端口/IP。

## 02-Keepalive
Q: TCP keepalive 与应用 heartbeat 有何区别？
A:
- TCP keepalive 在连接长时间空闲后发探测，检测对端/路径是否仍可达，默认间隔常很长。
- 应用 heartbeat 可携带业务状态、按 SLO 更快判断，并区分“进程活着但业务卡死”。
- 两者都会受 NAT idle timeout、移动网络和临时抖动影响，参数过短会制造流量与误杀。
- 无业务流量不代表连接死亡，最终策略应结合重连幂等。

## 03-Nagle
Q: Nagle 算法怎样减少小包，为什么会增加交互延迟？
A:
- 有未确认小数据时暂缓继续发送小 segment，等待 ACK 或积累到 MSS，减少 tinygram。
- 对逐字节/小 RPC 可与 delayed ACK 相互等待，形成数十毫秒延迟。
- TCP_NODELAY 禁用 Nagle 但不保证每次 write 一个包，栈仍可能合并、分段和受 cwnd 限制。
- 更好的协议是应用层批量/明确 flush，而非盲目对所有连接切开关。

## 04-DelayedACK
Q: 接收端为什么延迟 ACK，何时会立即确认？
A:
- 稍等可让 ACK 搭载反向数据或一次确认多个 segment，减少纯 ACK 数量。
- 到达第二个满尺寸 segment、乱序/缺口、定时器到期等条件常触发立即 ACK，细节依实现。
- ACK 过慢会抑制小窗口/慢启动发送，协议栈有 quickack 等启发式缓解。
- Delayed ACK 不是应用层延迟响应，抓包应区分数据何时到和 ACK 何时发。

## 05-TCPUserTimeout
Q: RTO、keepalive、应用超时和 TCP_USER_TIMEOUT 分别控制什么？
A:
- RTO 控制单连接数据重传节奏；keepalive 只针对长期空闲探测；应用超时决定业务愿意等待多久。
- TCP_USER_TIMEOUT 可限制已发送未确认数据允许存在的时间，影响何时让 socket 失败。
- 应用超时后请求可能仍在内核/服务端执行，重试必须有 request ID 和幂等保障。
- 多层超时应由内到外递增并留预算，否则上层先超时造成重试风暴。

## 06-正确性审查
Q: 关于 TCP 定时器最常见的错误优化是什么？
A:
- 把大量 TIME_WAIT 当“泄漏”直接调危险复用，而不查短连接、主动关闭方和端口容量。
- 用 TCP keepalive 代替业务健康检查，无法发现线程池/依赖卡死。
- 认为 TCP_NODELAY 永远更快，忽略 PPS、头部和拥塞成本。
- 只调大超时会把故障转成更长排队，必须配合 deadline、取消和背压。

