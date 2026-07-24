# HTTP 方法、状态码、缓存与 Cookie
## 01-报文语义
Q: HTTP 请求和响应的核心组成是什么？
A:
- 请求含 method、target、version/协议帧、headers 和可选 body；响应含 status、headers 和 body。
- HTTP 定义资源操作语义，不规定业务内部实现；header 名大小写/连接管理依版本。
- Content-Type 描述表示格式，Content-Length/分块/帧定义边界，Content-Encoding 表示压缩。
- TCP 是字节流，HTTP/1 解析必须严格处理长度以防请求走私。
## 02-安全与幂等
Q: safe、idempotent 与“不会重复执行”有什么区别？
A:
- safe 方法语义上只读；idempotent 表示重复相同请求的预期效果与一次相同，如 PUT/DELETE。
- 网络超时无法知道服务是否已执行，客户端/代理可能重试；POST 也可用 idempotency key 实现业务幂等。
- 幂等不代表响应完全相同，也不表示无日志/计数等副作用。
- 重试策略必须结合方法、状态码、请求体可重放和 deadline。
## 03-状态码
Q: 2xx、3xx、4xx、5xx 应怎样解释故障责任？
A:
- 2xx 表示协议层成功但业务仍可能在 body 失败；3xx 指示重定向/缓存验证。
- 4xx 表示当前请求无法按客户端语义处理，429/408 常可在退避条件下重试。
- 5xx 表示服务器/网关失败，502/503/504 分别常指上游无效、不可用和超时，但实现可不同。
- 不能以“非 200 都重试”，否则永久 4xx 和过载会被放大。
## 04-缓存验证
Q: Cache-Control、ETag 和 Last-Modified 如何协作？
A:
- max-age/s-maxage 定义新鲜期，public/private/no-store 等约束共享与存储；Age 反映缓存驻留。
- 过期后客户端用 If-None-Match/If-Modified-Since 条件请求，未变返回 304 不带完整 body。
- ETag 可表达内容版本，Last-Modified 粒度较粗；ETag 强弱比较语义不同。
- Vary 把请求头纳入 cache key，遗漏会串内容，过多会降低命中。
## 05-Cookie
Q: Cookie 的 Domain、Path、Secure、HttpOnly、SameSite 分别控制什么？
A:
- Domain/Path 控制发送范围但不是强安全隔离；Secure 只随 HTTPS，HttpOnly 阻止脚本读取。
- SameSite 限制跨站请求携带，缓解 CSRF；None 通常要求 Secure。
- Cookie 每请求自动携带，过大增加带宽；session ID 泄漏可劫持会话，应短期、轮换和服务端失效。
- 跨域 CORS 控制浏览器脚本读响应，不等同 Cookie 发送与 CSRF 防护。
## 06-正确性审查
Q: HTTP 常见的错误表述有哪些？
A:
- “HTTP 无状态所以服务不能有 session”错误：协议请求独立，应用可用 cookie/token 关联状态。
- “GET 没有 body/POST 不可缓存”过度绝对：规范语义、实现兼容和缓存显式规则需区分。
- “HTTPS 后 URL 全隐藏”错误：IP、流量特征仍可见，DNS/SNI 可见性取决于加密方案。
- “304 没走服务端”错误：可能经过验证，只是复用缓存 body。

