# 网络、端口、DNS 与系统调用诊断

> 基线：从应用错误码出发，按名字解析、路由、连接、传输、socket 队列和业务协议逐层验证，避免“先抓包再说”。

## 01-端口监听
Q: 怎样确认服务是否真的在目标地址和端口监听？
A:
- `ss -lntp` 查看 LISTEN socket、本地地址、端口、进程和 namespace，`0.0.0.0`、`::` 与 loopback 语义不同。
- 在容器内外分别检查 network namespace，宿主端口映射不代表容器进程直接监听宿主地址。
- 查看服务启动日志、fd 与 systemd socket activation，确认监听者不是旧进程或代理。
- 本机 LISTEN 仍不证明远端可达，后续还需路由、防火墙、LB 和安全组。

## 02-connect错误
Q: `ECONNREFUSED`、timeout、`ENETUNREACH` 分别优先指向什么？
A:
- refused 常表示目标返回 RST，端口无监听或防火墙主动拒绝；也可能连接 backlog/代理策略导致。
- timeout 表示在期限内未完成，可能包被丢、路由黑洞、对端过载或握手重传。
- ENETUNREACH/EHOSTUNREACH 指向本地路由、邻居或网络不可达判断，应先查 `ip route get`。
- 应保存目标解析 IP、源 namespace、errno 和耗时；只记录“连接失败”会丢失最重要分层证据。

## 03-DNS链路
Q: Linux 应用域名解析可能经过哪些层？
A:
- libc `getaddrinfo` 按 `/etc/nsswitch.conf` 选择 files、dns、systemd-resolved、LDAP 等 NSS source。
- DNS stub 依据 `/etc/resolv.conf` 的 nameserver、search、ndots、timeout/attempts 发送查询，容器可能使用独立配置。
- 本地缓存、NodeLocal DNS、企业递归服务器和权威服务器分别可能超时或返回旧记录。
- `dig` 直接查询某服务器不一定复现应用 NSS/search 行为，必要时 strace/getent 与抓包结合。

## 04-SendQ与RecvQ
Q: `ss` 中 Send-Q/Recv-Q 持续很大说明什么？
A:
- 已连接 TCP 的 Recv-Q 大表示数据已到本机 socket 但应用读取慢，可能线程阻塞或协议处理跟不上。
- Send-Q 大表示已写入但尚未被对端 ACK 的数据多，可能对端读取慢、网络丢包、拥塞或窗口受限。
- LISTEN socket 上队列字段语义不同，可用于观察 accept backlog 当前/上限，需按 ss 输出版本解释。
- 队列只给现象，`ss -ti/m` 的 cwnd、rtt、retrans、window、buffer 与应用线程共同定位根因。

## 05-TCP状态
Q: TIME_WAIT、CLOSE_WAIT 大量出现分别通常说明什么？
A:
- TIME_WAIT 多在主动关闭方，保证旧报文过期和最终 ACK 重传；短连接高并发会自然积累。
- CLOSE_WAIT 表示已收到对端 FIN，但本地应用尚未 close，持续增长通常是连接/异常路径泄漏。
- SYN_SENT/SYN_RECV 积累分别提示出站握手无响应或服务端半连接压力。
- 不能通过粗暴缩短所有内核超时掩盖应用连接模型，应先确认角色、速率和端口空间。

## 06-临时端口
Q: 客户端为什么会耗尽 ephemeral port？
A:
- 每个出站连接使用源 IP、源端口、目标四元组；大量同目标短连接和 TIME_WAIT 会占用可用组合。
- NAT/SNAT 可能让很多容器共享少量出口 IP，把端口瓶颈集中到节点或网关。
- 连接池、HTTP keep-alive、多出口 IP 和合理并发比盲目扩大端口范围更根本。
- `EADDRNOTAVAIL`、conntrack 和 ss 四元组统计可验证，不能只看进程 fd 数。

## 07-丢包层次
Q: 怎样从网卡到 socket 分层查丢包？
A:
- `ethtool -S` 检查 NIC/ring drop、CRC 和队列错误，`/proc/net/softnet_stat` 看 softnet backlog/drop。
- `nstat`、SNMP 计数检查 IP/TCP 重传、listen overflow，qdisc 统计检查排队丢弃。
- `ss -m` 与 UDP 统计检查 socket buffer，应用日志检查未及时读取。
- 计数器命名依驱动，必须做前后差值和流量对齐，单个累计大数没有时间意义。

## 08-tcpdump
Q: 抓包前应怎样选择位置和过滤条件？
A:
- 明确源/目标、协议、端口、时间窗口和故障请求 ID，避免全量抓包造成性能和隐私风险。
- 容器 veth、bridge、宿主物理口、LB 两侧看到的地址、NAT 和 offload 视图不同。
- 使用 snaplen、ring buffer、文件轮转和最小权限，敏感 payload 应脱敏或仅抓头部。
- 抓不到包可能是抓错 namespace/接口、硬件 offload 或流量未到，不等于网络没有事件。

## 09-strace
Q: strace 适合回答哪些问题，使用时有什么代价？
A:
- 它能显示实际 syscall、参数、返回值、errno、信号和耗时，快速验证文件、网络、DNS 与阻塞点。
- `-f` 跟踪线程/子进程，`-ttT` 带时间与耗时，`-e trace=` 缩小范围，`-p` 可附加运行进程。
- ptrace 跟踪会增加每次 syscall 停顿，高 syscall 服务可能明显受影响，生产应限时限过滤。
- strace 显示系统调用边界，不直接解释用户态 CPU 热点或内核内部等待原因。

## 10-perf与eBPF
Q: perf、ftrace、eBPF 在系统排障中如何分工？
A:
- perf 适合 CPU 采样、硬件计数器和调度分析；ftrace/tracepoint 适合内核预定义事件和函数路径。
- eBPF 可按 PID、cgroup、路径、延迟和调用栈动态聚合 syscall、网络、块 IO 等事件，降低全量日志量。
- kprobe 对内部函数和参数依内核版本变化，优先使用稳定 tracepoint/BTF，并验证丢事件。
- 观测程序也会消耗 CPU/内存和放大热点，上线前要限制采样、map 大小和运行时间。

## 11-dmesg与时钟
Q: 为什么系统日志时间线经常对不上应用日志？
A:
- dmesg 默认可能使用开机后的 monotonic 时间，应用日志使用 wall clock；NTP 调整和容器时区也会影响。
- `dmesg -T` 的转换可能基于当前偏移，不一定精确反映历史时钟跳变。
- 事故记录应保留 monotonic/boot time、UTC wall time、主机和容器时区，并用事件关联而非只看字符串时间。
- 内核 reset、OOM、文件系统和网卡错误必须与应用延迟同一时间轴比较。

## 12-排障顺序
Q: 一个“域名偶发请求超时”应怎样按层排查？
A:
1. 从应用日志确认是 DNS、connect、TLS、首字节还是读写超时，并保存目标 IP 与 deadline。
2. 用 getent/strace 验证 NSS/DNS，`ip route get` 验证路由，ss 检查 socket 队列与 TCP 指标。
3. 比较客户端、服务端、DNS、LB 和节点监控，在正确 namespace/接口做有限抓包。
4. 最后用 eBPF/perf 下钻内核延迟；不要一开始修改 tcp 参数或重启 DNS 清除现场。

## 13-正确性审查
Q: 网络排障中哪些常见判断需要纠正？
A:
- “能 ping 通就说明应用端口正常”错误；ICMP、TCP 端口、TLS 和业务协议是不同层。
- “dig 正常就证明应用 DNS 正常”错误；应用可能经过 NSS、search domain、本地缓存和不同 namespace。
- “TIME_WAIT 多就是服务端代码没 close”错误；它常属于主动关闭方，CLOSE_WAIT 更直接指向本地未 close。
- “抓不到包说明对端没发”错误；也可能抓错接口、namespace、方向或受 offload 影响。
