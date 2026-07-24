# DNS 递归、缓存、负载与安全
## 01-解析链
Q: Stub resolver 查询一个未缓存域名时发生什么？
A:
- 本机 stub 向递归 resolver 请求；递归器若未缓存，从 root 得 TLD referral，再向权威链查询最终记录。
- 迭代查询由递归器完成，客户端通常只面对递归服务；CNAME 会引入额外名称解析。
- resolver 缓存正/负结果并按 TTL 过期，权威负责 zone 数据而非替所有客户端递归。
- 实际还受 hosts、搜索域、nss、DoH/DoT 和应用自身缓存影响。
## 02-记录类型
Q: A、AAAA、CNAME、NS、MX、TXT、SRV 分别表达什么？
A:
- A/AAAA 映射 IPv4/IPv6；CNAME 给别名指向规范名；NS 指定 zone 权威服务器。
- MX 指邮件交换并带优先级；TXT 承载验证/策略；SRV 同时表达服务目标、端口、优先级和权重。
- CNAME 通常不能与同名其他数据共存，zone apex 使用受限，云厂商 ALIAS/ANAME 是扩展。
- DNS 返回多个地址不等于健康负载均衡，客户端缓存和选择会造成不均。
## 03-TTL
Q: DNS TTL 如何影响变更和故障切换？
A:
- 缓存可在 TTL 内继续使用旧记录，权威修改不会立即全球生效；还存在本地/应用最小最大缓存策略。
- 降 TTL 应在变更前至少一个旧 TTL 周期完成，变更后再恢复以减少查询压力。
- 极短 TTL 增加权威/递归负载且客户端未必严格遵守，不能保证秒级切换。
- 连接复用还会继续使用旧 IP，即使 DNS 已刷新。
## 04-UDP与TCP
Q: DNS 何时从 UDP 转 TCP，EDNS0 有什么作用？
A:
- 传统 UDP payload 小，响应截断置 TC 后客户端用 TCP 重试；zone transfer 使用 TCP。
- EDNS0 扩大 UDP 能力并携带扩展选项，但过大 datagram 会分片，现代实践控制响应大小。
- DoT 在 TLS/TCP 上，DoH 在 HTTPS 上，改变隐私和中间可见性但不改变权威数据语义。
- 防火墙只放 UDP/53 会导致大响应和 fallback 失败。
## 05-DNSSEC
Q: DNSSEC 能保证什么，不能保证什么？
A:
- 权威 zone 对 RRset 签名，验证链从信任锚经 DS/DNSKEY 到记录，检测伪造和篡改。
- 它不加密查询，也不保证目标服务可信/在线；隐私需 DoT/DoH，应用身份仍需 TLS。
- 签名增大响应和运维复杂度，过期、链断或时间错误会导致 SERVFAIL。
- DNSSEC 验证通常由递归 resolver 完成，客户端需信任该 resolver。
## 06-排障
Q: DNS 慢或偶发失败应收集哪些证据？
A:
- 分别向本机递归器、指定公共/内部递归器和权威查询，记录 rcode、answer、authority、TTL 与耗时。
- 检查 UDP 是否截断、TCP fallback、IPv6、搜索域和缓存；SERVFAIL/NXDOMAIN/timeout 含义不同。
- 用 trace 定位 delegation/DS/lame server，确认多权威数据一致。
- 应用日志要记录解析结果和缓存命中，不能只看到 connect timeout 就归因 DNS。

