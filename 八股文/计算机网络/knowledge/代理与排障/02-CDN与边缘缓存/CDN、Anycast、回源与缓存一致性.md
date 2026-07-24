# CDN、Anycast、回源与缓存一致性
## 01-CDN路径
Q: CDN 如何把用户请求引到边缘节点？
A:
- 权威 DNS/CNAME 根据 resolver、地域和健康返回边缘地址，或用 Anycast 让多个站点宣告同一 IP。
- DNS 调度受递归 resolver 位置与 TTL 缓存影响，未必精确代表用户；Anycast 由 BGP 路由选择站点。
- 边缘终止 TLS/HTTP，命中直接返回，miss 通过区域/源站链回源。
- CDN 是分布式代理和缓存体系，不只是“多放几台静态服务器”。
## 02-缓存Key
Q: CDN cache key 应包含哪些维度，错误设计会怎样？
A:
- 基本包含 scheme/host/path/query，并按策略加入 Vary header、设备、语言或授权维度。
- 漏掉影响响应的 cookie/header 会把用户内容串给他人；维度过多则碎片化、命中率低。
- query 排序、大小写、默认端口和 URL 规范化必须与源站语义一致。
- 个性化/鉴权响应默认不应共享缓存，除非明确分区和权限验证。
## 03-新鲜与回源
Q: CDN 如何判断缓存新鲜并避免同时大量回源？
A:
- Cache-Control/Expires 定义 TTL，过期后可用 ETag/Last-Modified 条件验证。
- stale-while-revalidate 可先返回旧值后台更新，stale-if-error 在源故障时提供旧内容。
- request collapsing/singleflight 让同一 key 的并发 miss 共享一次回源，防 cache stampede。
- 需限制旧数据可接受窗口，动态配置/权限不能随意 stale。
## 04-Purge
Q: 为什么 CDN purge/invalidation 很难做到瞬时强一致？
A:
- 多层多地域节点和离线边缘需接收失效事件，传播有延迟且可能失败。
- versioned URL/content hash 让新内容使用新 key，避免依赖全网立即删除，最适合不可变静态资源。
- purge by prefix/tag 范围大、成本高，API 成功也应监控实际边缘版本。
- 强一致动态数据通常不应依赖共享 CDN 缓存承担真值。
## 05-源站保护
Q: CDN miss storm 如何压垮源站，怎样保护？
A:
- 热 key 到期、节点冷启动或 purge 会让许多边缘同时回源，流量瞬间远大于平时。
- 分层缓存、TTL jitter、request collapse、origin shield、回源限流和预热可削峰。
- 源站也需缓存、容量和拒绝策略，不能默认 CDN 永远命中。
- 监控 hit ratio 还要按 bytes/requests/status/key 分组，平均命中会掩盖大对象 miss。
## 06-排障
Q: 用户拿到旧内容或某地域失败时如何定位 CDN？
A:
- 记录响应 Age、Via/X-Cache、ETag、边缘 POP、DNS 答案和 request ID，对比直连源站。
- 检查 cache key/Vary、TTL、purge 传播、边缘证书与回源 Host/SNI。
- 某地域失败可能是 DNS/Anycast 路由、POP 回源或当地运营商，不应只重启源站。
- 用多个地域探针并保留时间线，避免测试请求本身命中不同缓存层。

