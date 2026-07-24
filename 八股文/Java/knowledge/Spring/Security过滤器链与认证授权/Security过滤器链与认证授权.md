# Spring Security 过滤器链、认证与授权

> 基线：Spring Security 6/7，组件式 `SecurityFilterChain` 配置。

## 01-FilterChainProxy
Q: 一次 HTTP 请求怎样进入 Spring Security 过滤器链？
A:
- Servlet 容器先进入 DelegatingFilterProxy，它把调用委派给 Spring 容器中的 security filter bean。
- FilterChainProxy 按 RequestMatcher 选择第一个匹配的 SecurityFilterChain。
- 链内不同过滤器完成安全上下文加载、认证、异常转换、授权等职责。
- 多条链顺序错误可能让更宽泛 matcher 抢先匹配，导致 API 使用了错误安全策略。
- `permitAll` 只是授权允许，前面的过滤器链仍可能执行。

## 02-认证链
Q: AuthenticationManager、ProviderManager、AuthenticationProvider 怎样协作？
A:
- 认证过滤器从请求提取凭据，构造未认证 Authentication 并交给 AuthenticationManager。
- ProviderManager 遍历支持该 token 类型的 AuthenticationProvider。
- Provider 校验用户、密码/令牌及账户状态，成功后返回已认证 Authentication 和 authorities。
- 结果存入 SecurityContext，后续授权读取；无状态 API 可每请求重建而不写 session。
- 认证失败由 failure handler/entry point 转换响应，不应把具体账号存在性泄露给攻击者。

## 03-授权
Q: 认证和授权有什么区别？方法授权为什么不能只靠 URL 规则替代？
A:
- 认证回答“你是谁/凭据是否可信”，授权回答“这个主体能否执行当前操作”。
- URL 规则保护入口路径；方法授权更接近业务操作，能覆盖内部调用入口和参数级规则。
- authority/role 是权限表示，`ROLE_` 前缀是常见约定，不等于完整 RBAC 模型。
- 仅在前端隐藏按钮不构成授权，服务端必须执行。
- 数据权限通常依赖租户、资源所有者和上下文，不能只用静态角色解决。

## 04-SecurityContext传播
Q: SecurityContext 在线程切换和异步任务中为什么会丢失？
A:
- 默认上下文常与当前线程关联，切换到线程池后不会自动安全传播。
- 可使用框架提供的 delegating executor/context propagation 机制显式捕获和恢复。
- InheritableThreadLocal 在线程池和虚拟线程环境存在复用/复制风险，不应作为通用答案。
- 传播后必须在任务结束清理，避免身份串到下一任务。
- 对消息消费和批处理更推荐从可信消息/任务元数据重建主体，而不是复制 Web 线程上下文。

## 05-密码存储
Q: 为什么密码不能加密后可逆保存？PasswordEncoder 应怎样使用？
A:
- 密码验证需要抗离线破解的单向自适应哈希，不需要恢复明文。
- 使用带随机 salt、可调成本的 bcrypt、scrypt、PBKDF2 或 Argon2 等算法；普通 SHA/MD5 太快。
- DelegatingPasswordEncoder 可在存储值中标识算法，支持逐步升级。
- 登录成功时可检测旧成本并重哈希，避免一次性强制所有用户改密。
- 限流、多因素认证、泄漏密码检查和安全重置流程同样重要。

## 06-正确性审查
Q: Spring Security 有哪些常见错误说法？
A:
- “配置 permitAll 就完全不经过过滤器”：错误。
- “JWT 无状态所以不需要任何服务端安全状态”：撤销、密钥轮换、风控和权限变化仍需要治理。
- “认证成功就拥有所有权限”：错误，授权是独立阶段。
- “角色判断放前端即可”：错误，服务端必须执行授权。
- “密码用 SHA-256 加盐就安全”：普通快速哈希仍不适合密码存储。
