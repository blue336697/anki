# HTTP/1、HTTP/2 与 HTTP/3
## 01-HTTP1连接
Q: HTTP/1.1 keep-alive 和 pipelining 各解决什么？
A:
- 持久连接复用 TCP，省握手/TLS/慢启动；请求仍是文本头和顺序解析的消息。
- pipelining 可连续发多个请求但响应必须按请求顺序返回，前一慢响应阻塞后续，生态支持较差。
- 浏览器常开多个 TCP 连接增加并行，却增加握手、拥塞窗口和服务端状态。
- 长连接需处理空闲超时、半开、请求数上限和优雅关闭。
## 02-HTTP2帧
Q: HTTP/2 如何在一条 TCP 连接上多路复用？
A:
- 把消息拆为带 stream ID 的二进制 frame，多个 stream frame 可交错发送并独立表达请求响应。
- SETTINGS、WINDOW_UPDATE、RST_STREAM、GOAWAY 管理连接/流；优先级支持在实现中已多次演进。
- 减少多 TCP 连接和 HTTP 层队头阻塞，但底层 TCP 丢一个 segment 会阻塞所有 stream 字节交付。
- 服务器 push 实际收益有限且浏览器支持变化，不应当核心优势背诵。
## 03-HPACK
Q: HPACK 为什么需要动态表，带来什么边界？
A:
- 重复 header 用静态/动态索引与 Huffman 压缩，减少 cookie 等冗余。
- 编解码两端维护同步动态表，表大小受 SETTINGS 限制；错误索引会成为连接级压缩错误。
- 动态状态和长度解析曾带来内存/CPU 攻击面，服务端必须限制 header list 和解码资源。
- HTTP/3 使用 QPACK 适应 QUIC stream，避免压缩状态造成过强阻塞。
## 04-HTTP2流控
Q: HTTP/2 为什么还有 stream 与 connection 两级流量控制？
A:
- TCP 只保护整连接接收缓冲，不知道哪个 HTTP stream 消费慢。
- 每 stream window 防单流淹没，connection window 限制总数据；接收消费后发送 WINDOW_UPDATE。
- 控制帧和 headers 规则不同，窗口更新错误会让吞吐卡住或内存失控。
- HTTP/2 flow control 不替代 TCP congestion control，分别保护应用接收和网络。
## 05-HTTP3
Q: HTTP/3 相比 HTTP/2 的核心变化是什么？
A:
- HTTP 语义映射到 QUIC stream，连接内某 stream 丢包不阻塞其他 stream 的有序交付。
- TLS 1.3 与 QUIC 握手集成，支持连接迁移；QPACK 处理 header 压缩。
- UDP 路径、用户态 CPU、可观测性和中间盒兼容是部署代价，通常保留 Alt-Svc/回退。
- 不是“HTTP/2+换 UDP”一句话，传输可靠性、packet number 和流管理都由 QUIC 重做。
## 06-选型排障
Q: 如何判断 HTTP/2/3 没带来预期收益？
A:
- 检查实际 ALPN 协商、连接复用率、并发 stream、丢包/RTT、header 大小和 server limits。
- 单请求大文件受带宽/拥塞而非多路复用；服务处理串行也不会因协议版本自动并行。
- HTTP/2 单 TCP 高丢包可能全连接停顿，HTTP/3 UDP 被限速则可能更差。
- 必须按版本分组观察 TTFB、下载、CPU、重试和 fallback，而非只看总平均。

