# 网卡收发、NAPI、零拷贝与 io_uring
## 01-收包路径
Q: 网卡收到一个包后如何到达 socket 接收队列？
A:
- 网卡 DMA 写 RX ring buffer，MSI-X/中断触发 NAPI；驱动批量 poll descriptor 并构造 skb。
- 二层/IP/TCP 依次校验、路由/重组和查 socket，TCP 按序放接收队列并唤醒等待者。
- RSS 把 flow hash 到不同硬件队列/CPU，RPS/RFS 可软件调整，亲和性影响缓存局部性。
- backlog、softirq budget 或 socket buffer 满都可能在不同位置丢包。
## 02-发包路径
Q: 应用 write 到网卡发出之间经过什么？
A:
- 字节进入 socket send buffer，TCP 分段/排队并受拥塞、窗口和 pacing 控制。
- IP 选路与邻居，qdisc 排队调度；驱动填 TX descriptor，网卡 DMA 读取并发送。
- TSO/GSO 可让内核保留大 skb，网卡/后段再分 segment，降低每包 CPU。
- write 返回不等于已上网线，qdisc、驱动 ring 和网卡仍可能排队。
## 03-NAPI
Q: NAPI 为什么在高包率下从中断转为轮询？
A:
- 每包中断会形成中断风暴；首次中断调度 poll 后暂时屏蔽队列中断，批量收包。
- 在 budget 内处理，未清空则由 softirq 继续；清空后重新启用中断，兼顾低负载省 CPU。
- budget/backlog 太小会丢包或 ksoftirqd 升高，太大则占用 CPU 拉高其他任务延迟。
- NAPI 是驱动/内核机制，不等同用户态 busy polling。
## 04-零拷贝
Q: sendfile、mmap 与 MSG_ZEROCOPY 各减少哪段复制？
A:
- sendfile 让文件页缓存直接进入 socket 发送路径，省去用户缓冲往返；mmap 共享页映射减少 read copy。
- MSG_ZEROCOPY 可让发送路径引用用户页并异步通知完成，适合大数据，页固定与完成管理有成本。
- DMA 仍搬运设备与内存，协议头、加密或修改可能产生复制；“零”是特定 CPU copy。
- 小消息可能因 pin/map/通知开销反而更慢，必须按大小压测。
## 05-io_uring
Q: io_uring 的 SQ/CQ 共享环怎样降低系统调用成本？
A:
- 用户把操作描述放 SQ，内核消费并把完成写 CQ；批量提交/收割减少逐操作 syscall。
- 注册 buffer/file、SQPOLL 等可减少映射、引用和入口成本，具体安全与权限需配置。
- 它是 completion 模型且支持网络、文件、超时和链接操作，但不是所有操作都永不阻塞/零拷贝。
- 队列深度、取消、超时和 backpressure 仍要由应用状态机正确管理。
## 06-排障
Q: 收包丢失应怎样定位 NIC、softirq、协议栈还是 socket？
A:
- 对比网卡 ethtool counters、RX ring/no-buffer、`/proc/net/softnet_stat`、qdisc 和协议统计。
- 看 IRQ/RSS 分布、softirq CPU、应用 Recv-Q 与 socket drops，确定最早增长的丢弃点。
- 两端抓包可区分线上没到、主机收到未交付、应用没读；offload 会改变包形态。
- 直接增大所有 buffer 可能只把丢包变长排队，应同时解决处理率和亲和性。

