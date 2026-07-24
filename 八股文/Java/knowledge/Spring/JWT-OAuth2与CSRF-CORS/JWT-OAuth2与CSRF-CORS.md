# JWT、OAuth2、CSRF 与 CORS

## 01-JWT结构
Q: JWT 的 header、payload、signature 分别解决什么？签名是否等于加密？
A:
- Header 描述算法和 key id 等元数据；Payload 保存 claims；Signature 防止内容被未授权篡改。
- 常见 JWS 只签名不加密，payload 可被读取，不能放密码或敏感明文。
- 验证必须固定允许算法、校验签名、issuer、audience、时间和业务约束，不能只成功解码。
- `kid` 用于选择密钥，但取钥地址和缓存必须受信任，防止注入。
- JWT 是令牌格式，不自动解决授权模型、撤销、存储和传输安全。

## 02-过期与撤销
Q: 无状态 JWT 怎样处理退出登录、权限变更和密钥泄漏？
A:
- 短 access token 缩小风险窗口，refresh token 负责续期并需要更严格存储与轮换。
- 强制撤销可使用 denylist、用户 token version、会话记录或缩短有效期，都会重新引入服务端状态。
- 权限变化是否立即生效取决于 claims 是否内嵌、资源服务器是否实时查询权限。
- 密钥轮换通过 kid、重叠验证窗口和安全分发完成；泄漏时要有紧急撤销方案。
- “完全无状态”和“实时撤销”存在天然权衡，必须明确 SLO。

## 03-OAuth2角色
Q: OAuth2/OIDC 中常见角色和 Authorization Code + PKCE 流程是什么？
A:
- Resource Owner、Client、Authorization Server、Resource Server 分别代表用户、应用、授权端和 API。
- 客户端把用户导向授权端，用户完成认证授权后获得短期 code。
- 客户端携带 code verifier 交换 token，PKCE 防止截获 code 后直接兑换。
- OAuth2 主要是授权框架；OIDC 在其上增加 identity token 和用户身份语义。
- 后端不能把任意第三方 access token 当作本系统登录态，必须校验 issuer/audience 和信任边界。

## 04-CSRF
Q: 哪些请求容易受 CSRF？无状态 API 是否一定不需要防护？
A:
- 浏览器会自动携带 Cookie、HTTP 认证等凭据，攻击站点可诱导浏览器向目标站发有副作用请求。
- CSRF 防护常使用同步 token、SameSite Cookie、Origin/Referer 校验并限制危险方法。
- 若认证只通过 JavaScript 显式放入 Authorization header，第三方站点通常无法凭空读取并设置该 token，风险模型不同。
- 但把 JWT 放 Cookie 后仍会自动携带，不能因为令牌格式是 JWT 就关闭 CSRF。
- XSS 可直接窃取/使用令牌，是另一威胁；CSRF 防护不替代 XSS 防护。

## 05-CORS
Q: CORS 和 CSRF 有什么区别？为什么 CORS 不是服务端鉴权？
A:
- CORS 是浏览器对跨源脚本读取响应的约束，通过预检和响应头决定是否暴露结果。
- 它不阻止非浏览器客户端请求，也不自动阻止某些简单跨源请求被发送。
- CSRF 利用浏览器自动携带身份执行副作用；CORS 与 CSRF 关注点不同。
- 允许 credentials 时不能随意使用通配 origin，应维护精确可信来源。
- 服务端仍必须认证、授权和校验业务输入，不能把 Origin 当身份。

## 06-正确性审查
Q: JWT/OAuth2 安全有哪些高频误区？
A:
- “JWT 有签名所以内容保密”：错误，签名不等于加密。
- “JWT 无状态所以可立即注销”：错误，需要额外撤销机制或等待过期。
- “OAuth2 就是登录协议”：不完整，身份层通常是 OIDC。
- “用了 JWT 就没有 CSRF”：取决于凭据如何存储和自动携带。
- “配置 CORS 就完成安全控制”：错误，CORS 是浏览器跨源策略，不是鉴权。
