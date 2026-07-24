# IPv6、OSPF 与 BGP 边界

## 01-IPv6头部
Q: IPv6 基础头相对 IPv4 有哪些关键变化？
A:
- 固定 40 字节基础头，移除 header checksum 和路由器分片字段，扩展功能通过 Next Header 链接扩展头。
- Hop Limit 对应 TTL，Traffic Class/Flow Label 支持分类；地址扩到 128 位。
- 路由器不分片，源端根据 PMTUD 决定大小；必要分片由源加入 Fragment extension。
- 扩展头过长或中间盒支持不佳会带来可达性与安全问题。

## 02-地址与配置
Q: IPv6 link-local、global、ULA 和 SLAAC 分别是什么？
A:
- link-local `fe80::/10` 只在链路内使用，NDP/路由邻居依赖它；global unicast 用于全球路由。
- ULA `fc00::/7` 类似内部唯一地址但不应简单等同 IPv4 私网 NAT 模式。
- SLAAC 根据 Router Advertisement 前缀生成地址和默认路由，DHCPv6 可提供有状态地址或其他参数。
- 接口可同时有多个 IPv6/IPv4 地址，源地址选择和 Happy Eyeballs 会影响实际连接。

## 03-IPv6不是无NAT
Q: IPv6 地址充足后，为什么仍不能说“安全问题由 NAT 解决/消失”？
A:
- 端到端可寻址不等于端口默认开放，stateful firewall 仍应按连接与策略过滤入站。
- NAT66 并非技术上不存在，但通常不需用它缓解地址短缺；前缀转换和多宿主有专门方案。
- IPv6 仍有扫描、伪造、RA/NDP 攻击和隐私地址跟踪等风险。
- 双栈最常见问题是只防 IPv4、IPv6 路径未监控，形成策略旁路。

## 04-OSPF
Q: OSPF 作为链路状态 IGP 怎样形成路由？
A:
- 邻居建立 adjacency，泛洪 LSA 让区域内路由器获得一致拓扑数据库，各自运行 SPF 计算最短路径。
- cost 常与带宽配置相关，area 分层减少泛洪/计算范围，ABR 汇总区域间信息。
- 变更需传播和重新收敛，错误 LSA/邻居抖动会造成 CPU 与路由震荡。
- OSPF 适合单一自治系统内部，不负责互联网跨组织策略。

## 05-BGP
Q: BGP 为什么称路径向量协议，它选路不只看最短路径？
A:
- BGP 宣告 prefix 及 AS_PATH、NEXT_HOP、LOCAL_PREF、MED、community 等属性，AS_PATH 也用于环路检测。
- 选路强调策略和商业关系，LOCAL_PREF 等属性可优先于 AS_PATH 长度，因此不是纯最短路。
- eBGP 连接自治系统，iBGP 在 AS 内传播外部路由；route reflector 缓解全互联规模。
- 控制面收敛较慢，数据面仍按下发 FIB 逐包 LPM。

## 06-正确性审查
Q: 后端工程师需要把 OSPF/BGP 掌握到什么边界？
A:
- 应能区分 IGP/EGP、控制面/FIB、ECMP、收敛和路由泄漏，解释跨机房绕路与单向可达。
- 不必背厂商全部选路 tie-break，但要知道 BGP 策略优先、最长前缀在数据面最终生效。
- “BGP 总选 AS_PATH 最短”和“OSPF 每包计算最短路”都错误。
- 排障应向网络侧提供源/目的、时间、前后路径、丢包点和前缀信息，而非只说网络抖了。
