# ACL与TLS安全边界

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-ACL规则

Q: Redis ACL 用户规则由哪些维度组成？

A:
- 用户开关 on/off、一个或多个密码/无密码设置。
- command 规则：`+cmd/-cmd`、`+@category`、allcommands/nocommands。
- key pattern：`~pattern` 控制可访问 key；channel pattern：`&pattern` 控制 Pub/Sub。
- ACL 是命令入口授权，不会自动隔离 CPU、内存和 key 数配额；多租户资源隔离仍需实例/代理层。

## 02-最小权限

Q: 为什么只设置 requirepass 不是完整安全方案？

A:
- requirepass/默认用户给所有通过者近似同一权限，凭证泄露后可执行危险管理命令。
- ACL 可为应用、只读任务、运维分别限制命令类别和 key/channel 前缀。
- 应关闭或严格限制 CONFIG、MODULE、DEBUG、FLUSH、KEYS 等高风险能力，并轮换凭证。
- Redis 不应直接暴露公网；网络 ACL、私网、TLS 和主机权限同样必要。

## 03-TLS链路

Q: TLS 在 Redis 中保护什么，不保护什么？

A:
- TLS 保护客户端/节点链路的机密性、完整性，并可用证书验证服务端或双向认证客户端。
- 不保护 Redis 进程内明文、日志、RDB/AOF 静态文件和已授权用户的恶意命令。
- Cluster 需考虑 tls-cluster，复制/Sentinel 也要配置对应 TLS；端口与 announce 信息必须匹配。
- 加密增加握手和 CPU 成本，可用连接复用、会话恢复和硬件能力压测。

## 04-ACL执行位置

Q: ACL 检查在命令执行链的什么位置，Lua/事务会绕过吗？

A:
- processCommand 阶段先按认证用户检查命令、key 和 channel 权限，未通过则不调用命令实现。
- MULTI 排队与 EXEC 时还要处理权限变化，避免排队后管理员撤权却继续执行。
- 脚本/Functions 调用 Redis 命令仍受相应脚本与 ACL 规则约束；不能把 EVAL 当通用绕过入口。
- ACL LOG 可审计最近拒绝事件，但容量有限，不替代集中安全日志。

## 05-危险操作治理

Q: 生产如何治理 FLUSHALL、CONFIG、DEBUG、MODULE 等危险命令？

A:
- 优先 ACL deny 和独立运维身份，而非只用 rename-command；后者影响工具兼容且不是完整授权模型。
- 管理面网络与业务面分离，变更需审计/审批，备份与恢复权限分离。
- 对 FLUSH/大范围删除设置 runbook、目标实例校验和维护窗口；Cluster 要确认作用范围。
- 安全事件后轮换 ACL 密码/证书，检查 ACL LOG、配置与持久化文件访问。
