# ARP、NDP 与邻居状态机

## 01-下一跳解析
Q: 主机发送 IP 包时为什么需要解析下一跳链路地址？
A:
- 路由表先决定出接口和 next-hop IP；Ethernet 帧还必须填写该链路上下一跳 MAC。
- 同网段目的通常解析目标本身，跨网段解析默认网关，绝不是跨路由直接查询最终主机 MAC。
- 解析结果缓存为邻居表项，避免每个包都广播；缓存有超时和可达性状态。
- 点到点或其他链路类型可能不使用 MAC/ARP，过程依链路技术。

## 02-ARP流程
Q: IPv4 ARP request/reply 的完整流程是什么？
A:
- 主机在本 VLAN 广播“谁拥有 target IP”，报文携带 sender IP/MAC；目标或代理设备单播/广播回复 MAC。
- 发送方更新邻居缓存并把排队的 IP 包封装发送；其他主机也可能从 request 学到源映射。
- ARP 只在本广播域有效，路由器不会转发普通 ARP 广播。
- 同一 IP 多个回复、MAC 快速变化可能是漂移、代理、VRRP 或欺骗，需要结合网络设计判断。

## 03-邻居状态
Q: Linux 邻居项为什么不只是“有/无”两种状态？
A:
- REACHABLE 表示近期确认可达，STALE 表示映射仍可用但需在下次使用时验证。
- DELAY/PROBE 通过上层确认或单播探测验证，FAILED 表示解析失败；INCOMPLETE 正等待回复。
- 这种 NUD 状态机避免固定周期广播，同时能发现主机迁移和网关失效。
- 应用看到 connect/send 延迟可能来自邻居解析排队，而非 TCP 本身。

## 04-IPv6NDP
Q: IPv6 NDP 与 IPv4 ARP 有哪些关键差异？
A:
- NDP 使用 ICMPv6 Neighbor Solicitation/Advertisement，不使用 ARP；请求发往 solicited-node multicast 而非全广播。
- 它还承担 Router Solicitation/Advertisement、前缀发现、默认路由和 Duplicate Address Detection。
- ICMPv6 是 IPv6 基础组成，粗暴屏蔽会破坏邻居发现和 PMTUD。
- NDP 仍可能被伪造，需要 RA Guard、SEND 或交换网络安全策略配合。

## 05-代理ARP与Gratuitous
Q: Proxy ARP 和 Gratuitous ARP 分别解决什么？
A:
- Proxy ARP 由路由器替另一目标回应自己的 MAC，使发送方误以为目标在本链路，随后由代理转发。
- Gratuitous ARP 主动通告“本 IP 对应本 MAC”，可检测地址冲突、刷新交换机/主机缓存和支持 VIP 漂移。
- HA 切换后若邻居缓存未更新，流量仍会发往旧设备；重复通告与交换机学习共同加速收敛。
- 它们是运维机制也扩大欺骗面，不能把任意未经验证的 ARP 更新视为可信。

## 06-安全与排障
Q: ARP spoofing 为什么可实施中间人，怎样防护和验证？
A:
- ARP 本身缺少认证，攻击者发送伪造映射让网关/主机把帧交给自己，再选择转发或丢弃。
- DHCP Snooping+Dynamic ARP Inspection、静态绑定、端口隔离和加密上层协议可降低风险。
- 排查看邻居表 MAC 是否异常、交换机 FDB 所在端口、是否有重复 IP 与大量 unsolicited reply。
- HTTPS 能保护内容与身份，但攻击者仍可造成拒绝服务或分析元数据。
