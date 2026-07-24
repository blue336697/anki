# TLS 1.3 握手、证书与会话恢复
## 01-安全目标
Q: TLS 分别怎样提供机密性、完整性和身份认证？
A:
- 握手协商版本/算法并通过 (EC)DHE 形成共享密钥；记录层 AEAD 加密并认证数据。
- 服务端证书链把域名公钥绑定到受信 CA，签名握手 transcript 证明持有私钥。
- 完整性阻止中途静默篡改，序号/nonce 规则也防记录重放；客户端证书可提供双向认证。
- TLS 不保证服务业务诚实，也不隐藏 IP 和全部流量特征。
## 02-握手链
Q: TLS 1.3 首次完整握手的关键消息和密钥演进是什么？
A:
- ClientHello 提供版本、cipher suites、key share、SNI/ALPN；ServerHello 选择参数并给 key share。
- 双方由 ECDHE 经 HKDF 派生 handshake keys，后续 EncryptedExtensions、Certificate、CertificateVerify、Finished 被加密。
- 验证 Finished 后派生 application traffic keys，握手 transcript 绑定所有协商防降级/篡改。
- TLS1.3 通常 1-RTT；与 TCP 建连时总延迟还包括 TCP RTT。
## 03-证书验证
Q: 客户端验证证书链时检查什么？
A:
- 从叶证书沿 issuer/signature 到本地 trust anchor，检查签名、有效期、Basic Constraints/Key Usage。
- 用 SAN 匹配访问主机名，不能只看 CN；还需检查吊销策略和算法安全要求。
- 缺中间证书、时间错误、SNI 选错证书和信任库差异都是常见失败。
- 证书“合法”只表示链与名称满足策略，不表示域名业务无恶意。
## 04-ECDHE与前向保密
Q: ECDHE 为什么提供 forward secrecy？
A:
- 每次握手使用临时密钥，长期证书私钥只签名握手而不直接加密会话密钥。
- 日后证书私钥泄漏，攻击者也不能仅凭历史抓包恢复当时临时共享秘密。
- 若端点运行时会话密钥/随机数已泄漏，前向保密不能挽救该会话。
- TLS1.3 移除传统 RSA key exchange，简化为满足现代安全目标的套件。
## 05-恢复与0RTT
Q: Session resumption 和 0-RTT 有什么收益与风险？
A:
- 服务端签发 PSK ticket，后续客户端证明持有可减少完整证书/密钥交换成本。
- 0-RTT 允许 ClientHello 后立即发 early data，但它可被网络重放且缺少完整前向保密。
- 只应用于幂等、可防重放操作；服务端可拒绝 early data，客户端必须能重发。
- ticket 密钥轮换、共享和生命周期影响集群恢复命中与安全。
## 06-排障
Q: TLS 握手失败应按什么顺序定位？
A:
- 先确认 TCP/QUIC 可达，再看 ClientHello 是否带正确 SNI/ALPN、双方版本/cipher/key share 是否有交集。
- 检查证书链、SAN、有效期、信任库与中间证书；代理/mTLS 还要检查客户端证书。
- 抓 alert 和服务日志，区分 handshake_failure、unknown_ca、bad_certificate 与超时。
- 不要用关闭验证作为生产修复，它只掩盖身份攻击和配置错误。
