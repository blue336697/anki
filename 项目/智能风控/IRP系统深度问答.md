# IRP 智能风控系统深度问答

> 以智能风控专家视角，对 IRP 系统进行深度剖析。每个问题包含两部分：(1) 系统写实——IRP 当前如何实现；(2) 业内做法——主流方案或更佳实践。

---

## Q1: 智能风控的架构是什么？

### 一、IRP 系统写实

IRP 采用**微服务同步调用链 + 异步消息**的混合架构，核心服务链路为：

```
Tamer(网关) → Peregrine(策略) → Owl(编排) → Raptor(规则) + Seagull-web(指标)
                  ↑
              Nest(用户/权限)
              Kestrel(运营管理)
              Merlin(模型管理) → algo-service(ML训练)
```

**分层职责：**

| 层级 | 服务 | 核心能力 |
|------|------|----------|
| 接入层 | Tamer | API 网关，RSA+AES 混合加解密，JWT 鉴权，路由转发 |
| 策略层 | Peregrine | 策略编排，双层变量体系（策略变量+决策变量），数据产品，AB 测试 |
| 编排层 | Owl | LiteFlow 流程编排，Aviator/Janino/Python 三引擎表达式计算，指标查询 |
| 规则层 | Raptor | 自研 URule（Rete 算法），6 种决策插件（评分卡/决策树/决策表/规则集/规则流/PMLL），规则热更新 |
| 数据层 | Seagull-web | 指标计算引擎，Aviator 解释执行 + Janino 编译执行 |
| 支撑层 | Nest/Kestrel/Merlin | 用户权限 RBAC、Flowable 审批流、名单管理、模型全生命周期 |

**关键架构特征：**
- **同步调用链**：Tamer → Peregrine → Owl → Raptor，每层通过 Feign HTTP 同步调用，链路埋点依靠 SkyWalking `@Trace`
- **异步消息**：RocketMQ 14 个 Topic，BROADCASTING 模式做缓存同步，CLUSTERING 模式做业务消息和监控埋点
- **多租户**：共享数据库 + 行级隔离，MyBatis-Plus InnerInterceptor 自动注入 `AND tenant_code = '{current}'`
- **表达式引擎**：Aviator（解释执行，灵活）、Janino（编译为字节码，高性能）、Python（跨进程 HTTP 调用，支持复杂 ML 表达式）

### 二、业内做法对比

IRP 的微服务同步链架构在中小规模场景可行，但业内头部风控平台更多采用**事件驱动 + 异步化**架构：

| 维度 | IRP 当前 | 业内主流 |
|------|----------|----------|
| 调用模式 | 同步 Feign 链 | 事件驱动，Kafka/Pulsar 异步解耦 |
| 规则执行 | 中心化规则引擎 | 规则引擎 + 边缘计算（SDK 嵌入业务端） |
| 数据获取 | 实时查询外部数据源 | Data Mesh 预聚合 + 特征平台（Feature Store） |
| 容错降级 | 无熔断/限流 | Sentinel/Resilience4j + 多级降级策略 |
| 可观测性 | SkyWalking 链路追踪 | OpenTelemetry + Prometheus + Grafana + ELK |
| 决策时效 | 同步等返回 | 准实时 + 离线批量双通道 |
| 多租户 | 共享 DB 行级隔离 | 大租户独立 Schema/库，小租户共享 |

**具体例子：** 蚂蚁的风控架构中，进件请求写入 Kafka，风控引擎异步消费，结果通过回调通知业务方。好处是削峰填谷，业务方不阻塞等待。对于需要实时决策的场景（如支付风控），引擎 SDK 嵌入业务进程本地调用，延迟 < 1ms。

---

## Q2: 智能风控的业务是什么，具体怎么运作的？

### 一、IRP 系统写实——以信用卡申请反欺诈为例

**业务场景：** 某银行信用卡线上申请，需要在 500ms 内判断该申请是否存在欺诈风险。

**Step 1: 进件（Tamer 网关，~10ms）**
- 用户填写姓名、身份证号、手机号、单位、收入等信息提交申请
- 前端 RSA 加密敏感字段（身份证、手机号），请求经 Tamer 网关 RSA 解密 + JWT 验签
- Tamer 提取租户 code，注入请求头，路由到 Peregrine

**Step 2: 策略匹配（Peregrine，~20ms）**
- Peregrine 根据进件产品码（如 `CREDIT_CARD_APPLY`）找到绑定的策略版本
- 加载策略变量：从 Redis 读取预热的变量缓存（3 天 TTL），如该产品审批通过率阈值、黑名单版本号
- 调用 Owl 执行决策流程

**Step 3: 流程编排（Owl，~50ms）**
- LiteFlow 执行决策链：`数据准备 → 名单检查 → 规则执行 → 评分计算 → 结果决策`
- 每个节点是独立的 Component，按 EL 表达式定义的 DAG 执行
- 数据准备节点：拉取进件相关的指标数据（近 30 天申请次数、设备指纹关联数等）
- 名单检查节点：调用 Kestrel 名单服务，查此人是否在白/黑/灰名单中

**Step 4: 规则执行（Raptor，~100ms）**
- URule 规则引擎执行反欺诈规则集（Rete 算法）：
  - 规则 1：身份证号是否在黑名单？→ 命中则直接拒绝（score=0）
  - 规则 2：手机号关联设备数 > 5？→ 加 30 分风险分
  - 规则 3：近 7 天同 IP 申请次数 > 10？→ 加 20 分风险分
  - 规则 4：单位名称是否命中高风险行业库？→ 加 15 分风险分
  - 规则 5：年龄 < 22 且收入 < 5000？→ 加 10 分风险分
- 决策表：根据总分映射决策结果（0-30 通过，31-60 人工审核，61+ 拒绝）
- PMML 模型：加载训练好的 XGBoost 反欺诈模型，输出欺诈概率（0-1）

**Step 5: 外部数据调用（关键环节）**
在规则执行过程中，以下场景触发外部数据拉取：
- **身份核验**：调用银联/公安部接口验证姓名+身份证号真实性（必需，每次调用）
- **设备指纹**：调用数美/同盾设备指纹 SDK，获取设备关联的历史风险标签
- **多头借贷**：调用百行征信/朴道征信，查询该用户在其他机构的借贷记录（需用户授权）
- **手机号风险**：调用运营商数据（如天御），查询手机号实名认证状态、在网时长
- **IP 风险**：调用 IP 情报库（如威胁猎人），查询 IP 是否为代理/VPN/黑产机房

**Step 6: 指标计算（Seagull-web，~30ms）**
- 查询实时指标：近 24h 同设备申请量、近 1h 同 IP 申请量
- Aviator 表达式动态计算：`risk_score = count_24h * 0.3 + device_risk * 0.5 + ip_risk * 0.2`
- Janino 编译执行的预编译表达式热点缓存 15 天（Caffeine，maxSize 100K）

**Step 7: 决策返回**
- Raptor 汇总规则命中 + 模型分数 + 指标计算结果，返回最终决策（通过/人工/拒绝）
- 决策结果通过 RocketMQ 发送到监控 Topic，触发 BI 看板实时刷新
- 异步写入决策日志到 MySQL，供后续分析和模型迭代

### 二、业内做法对比

**数据预聚合（Feature Store）：**
IRP 每次进件实时查询外部数据，业内头部平台（如字节、蚂蚁）使用 Feature Store 模式：离线将外部数据预计算为特征，存入特征平台（如 Feast/Feathr），在线决策时只需查特征平台（<5ms），无需逐次调用外部 API。

**DAG 并行化：**
IRP 的 LiteFlow 支持 DAG，但外部数据调用是串行的。业内做法是将互相独立的外部数据调用并行化，如身份核验、设备指纹、多头借贷三者同时发出，总延迟 = max(单个延迟)，而非 sum(所有延迟)。

**具体例子：** 某互联网金融平台的风控决策流程中，所有外部数据调用通过 CompletableFuture 并行发出，3 个调用各需 100ms，并行后总耗时 100ms（而非 300ms）。通过 Feature Store 预聚合 80% 的外部数据查询，仅 20% 需要实时回补。

---

## Q3: RocketMQ 在系统中怎么用的，推模式和拉模式你怎么理解？

### 一、IRP 系统写实

IRP 使用 RocketMQ 2.3.1，共 14 个 Topic，分为两大类：

**BROADCASTING 模式（缓存同步类）——核心场景：**

| Topic | 用途 | 生产者 | 消费者 |
|-------|------|--------|--------|
| `RAPTOR_CACHE_SYNC` | 规则缓存同步 | Raptor 管理后台 | 所有 Raptor 实例 |
| `PEREGRINE_CACHE_SYNC` | 策略变量缓存同步 | Peregrine 管理后台 | 所有 Peregrine 实例 |
| `NEST_CACHE_SYNC` | 用户权限缓存同步 | Nest 管理后台 | 所有服务实例 |

广播模式的语义：一个消息被**所有**订阅者消费。当管理员在后台修改了一条规则，消息广播到所有 Raptor 实例，每个实例各自刷新本地 Caffeine 缓存。

**CLUSTERING 模式（业务/监控类）——核心场景：**

| Topic | 用途 |
|-------|------|
| `DECISION_LOG` | 决策日志异步写入 |
| `MONITOR_METRIC` | 监控指标上报 |
| `ALARM_EVENT` | 告警事件通知 |
| `MODEL_TRAINING` | 模型训练任务触发 |

集群模式的语义：一个消息被**一个**消费者消费。决策日志只需一个实例写入数据库，避免重复。

**代码层面（关键实现）：**

```java
// raptor-core/.../consumer/BaseCacheConsumer.java
// 消费缓存同步消息时，从 ConsumerMessageDto 恢复租户上下文
CurrentUser.set(currentUser);  // 设置 ThreadLocal
// 然后刷新本地缓存
```

消息体中携带 `ConsumerMessageDto`（含 tenantCode、userName），确保跨服务的租户上下文不丢失。

### 二、推模式 vs 拉模式理解

**Push（推模式）：**
- Broker 主动向 Consumer 推送消息
- RocketMQ 默认使用**长轮询（Long Polling）**——Consumer 发起请求，Broker 有新消息时立即返回，没有时 hold 住请求 15s 后返回空
- 优点：实时性好，消息到达即消费
- 缺点：Consumer 处理能力不均时，慢消费者会被压垮

**Pull（拉模式）：**
- Consumer 主动去 Broker 拉取消息
- 优点：Consumer 根据自身能力控制消费速率，不会被打垮
- 缺点：拉取间隔设置不当会增大延迟

**IRP 当前使用的是 RocketMQ 默认的 Push 模式（实际是长轮询封装）。**

### 三、业内做法对比

| 维度 | IRP 当前 | 业内建议 |
|------|----------|----------|
| 缓存同步 | BROADCASTING 模式 | 改用 CLUSTERING + Redis Pub/Sub，避免广播模式下某实例消费失败导致缓存不一致 |
| 关键消息可靠性 | 无特殊处理 | 对 DECISION_LOG 等关键消息使用同步刷盘 + 重试队列 |
| 消息回溯 | 未使用 | Kafka 的消息可回溯性更强，适合审计场景 |
| Push vs Pull | Push（长轮询） | 关键路径用 Pull 模式 + 手动 offset 提交，避免自动提交导致消息丢失 |

**具体例子：** 某支付公司的风控决策日志传递使用 Kafka，因为 Kafka 支持按时间戳回溯消息（比如回溯过去 2 小时的所有决策记录用于复盘），而 RocketMQ 的消息回溯能力相对弱。同时他们使用 Pull 模式消费，每消费 100 条手动 commit 一次 offset，确保不丢不重。

---

## Q4: Redis 在系统中怎么用的？

### 一、IRP 系统写实

IRP 使用 Redis/Redisson 3.22.0 + Caffeine 两级缓存。具体 6 种使用模式：

**1. 用户 Session 缓存（Nest）**
```
Key: nest:user:token:{token}
Value: UserInfo JSON
TTL: 30 分钟（滑动过期）
```
每次请求 Tamer 网关从 Redis 校验 JWT token 并刷新过期时间。支持 ZSet 记录用户多端登录。

**2. 策略变量缓存（Peregrine）**
```
Key: peregrine:var:{varId}:{updateTime}
Value: 变量值
TTL: 3 天
```
策略变量在管理后台修改后，通过 BROADCASTING 消息通知所有实例刷新。缓存 key 带 updateTime 版本号，实现无感热更新。

**3. 分布式锁（Redisson，Kestrel/Raptor）**
```java
// kestrel/zero-service/.../AlarmCronService.java
// 告警引擎使用 SETNX 分布式锁（1s TTL），防止多实例重复执行定时任务
RLock lock = redissonClient.getLock("alarm:cron:lock");
lock.lock(1, TimeUnit.SECONDS);
```

**4. 原子计数器（Owl）**
```
Key: owl:ds:roundrobin:{graphCode}
Value: 递增整数
```
Owl 的 LoadBalanceNode 使用 Redis 计数器实现数据源轮询（`DsRoundRobin:{graphCode}`）。

**5. Pub/Sub 缓存失效（Nest）**
```
Channel: nest:cache:invalidate
Message: {cacheType, cacheKey}
```
当用户/权限数据变更时，通过 Redis Pub/Sub 通知所有实例清除本地 Caffeine 缓存。

**6. ZSet 多端登录控制（Nest）**
```
Key: nest:user:sessions:{userId}
Member: {deviceId}
Score: loginTimestamp
```
记录用户所有登录设备，支持强制踢出特定设备（删除对应 member）。

**本地缓存 Caffeine：**
```
maxSize: 100K
expireAfterWrite: 15 天
```
用于热点数据本地化，减少 Redis 网络开销。配合 Redis Pub/Sub 做缓存失效。

### 二、业内做法对比

| 维度 | IRP 当前 | 业内做法 |
|------|----------|----------|
| 分布式锁 | SETNX 简单锁（1s TTL） | Redlock 算法（多节点投票），防止单点 Redis 故障导致锁失效 |
| 缓存穿透 | 未明确处理 | 布隆过滤器（Bloom Filter）预判 key 是否存在，防止恶意查询穿透到 DB |
| 缓存一致性 | 广播消息 + 手动刷新 | Write-Through / Write-Behind 策略，或 Canal + Binlog 异步更新 |
| ID 生成 | 无（猜用 DB 自增） | Redis Lua 脚本生成分布式 Snowflake ID |
| Session 管理 | Redis 集中存储 | JWT 无状态方案（减少 Redis 依赖），或 Redis Cluster 高可用部署 |
| 限流 | 未实现 | Redis 滑动窗口限流器 |

**具体例子：** 某电商风控平台使用 Redis Bloom Filter 做黑名单预筛：10 亿级黑名单通过布隆过滤器压缩到 1GB 内存，99.9% 的正常用户无需查 DB，仅 0.1% 的疑似命中需要回源 DB 确认，将黑名单检查延迟从 50ms 降到 0.1ms。

---

## Q5: 多租户是什么架构，如何埋点监控？

### 一、IRP 系统写实

**多租户架构：共享数据库 + 行级隔离**

IRP 采用**共享数据库、共享表、行级 Tenant 隔离**模式：

```sql
-- MyBatis-Plus InnerInterceptor 自动注入
SELECT * FROM risk_rule WHERE deleted = 0 AND tenant_code = 'icbc'
```

所有业务表包含 `tenant_code` 字段。通过 MyBatis-Plus 的 `DataPermissionInterceptor` 自动在 SQL 的 WHERE 条件中追加租户过滤。

**租户上下文传递机制：**

```
HTTP 请求 → Tamer 网关（提取 tenant_code）
  → Peregrine（ThreadLocal 存储 CurrentUser）
    → Owl（Feign RequestInterceptor 透传 HTTP Headers）
      → Raptor（ThreadLocal 恢复 CurrentUser）
        → RocketMQ（ConsumerMessageDto 携带 tenantCode）
```

关键代码路径：
- `nest/nest-user-spring-boot-starter/.../CurrentUser.java` — ThreadLocal 用户上下文
- `nest/nest-user-spring-boot-starter/.../NestCurUserFeignRequestInterceptor.java` — Feign 调用时复制所有 HTTP Headers
- `raptor-core/.../consumer/BaseCacheConsumer.java` — 消费 MQ 消息时从 ConsumerMessageDto 恢复 CurrentUser
- `raptor-common/.../RaptorDataFilterInterceptor.java` — 使用 `auth_code`（tenantCode_organizeCode）过滤

**权限粒度：**
```
租户 → 组织 → 角色 → 用户
```
RBAC 模型，通过 `PermissionUtils`（TransmittableThreadLocal）控制数据权限和脱敏跳过。

### 二、监控埋点——当前缺失严重

**IRP 当前监控现状：**
- SkyWalking 链路追踪（`@Trace` 注解在 `KnowledgeSessionImpl.fireRules()` 等关键方法）
- RocketMQ 监控 Topic 上报决策次数、耗时
- 无 Prometheus/Micrometer 指标暴露
- 无 Actuator health check 端点
- 无 Grafana 看板

**IRP 当前缺失的关键监控：**
- **租户级别 SLA**：哪个租户的决策延迟高？哪个租户的规则命中率异常？
- **租户资源配额**：某租户是否占用了过多线程资源？
- **缓存命中率**：Redis/Caffeine 命中率按租户维度拆分

### 三、业内做法

**多租户：**
| 层级 | 小租户 | 大租户 |
|------|--------|--------|
| 数据库 | 共享 DB + 行级隔离（IRP 当前方案） | 独立 Schema 或独立数据库 |
| 线程池 | 共享 | 独立线程池（Bulkhead 模式） |
| 缓存 | 共享 | 独立缓存分片 |
| 限流 | 共享 | 独立限流阈值 |

**监控 — 黄金信号（Golden Signals）：**

1. **延迟（Latency）**：决策 P50/P99 耗时，按租户、产品码、规则集拆分
2. **流量（Traffic）**：每秒决策量（TPS），按租户拆分
3. **错误（Errors）**：决策失败率、外部数据调用超时率、规则编译失败数
4. **饱和度（Saturation）**：线程池使用率、Redis 连接池使用率、MQ 消息堆积量

**具体例子：** 某 SaaS 风控平台为每个大客户（日决策量 > 1000 万）分配独立 Schema + 独立线程池（核心 10 线程），小客户共享资源。Prometheus 按 `tenant_code` label 打标，Grafana 看板可按租户筛选，租户 SLA 告警（如某租户 P99 > 1s 触发告警）。

---

## Q6: 线上出现问题，你的常规处理流程是什么？

### 一、IRP 系统当前可用的排查手段

**立即可用的工具链：**
1. **SkyWalking 链路追踪**：查看某次决策的完整调用链（Tamer → Peregrine → Owl → Raptor），定位哪个环节超时
2. **应用日志**：ELK 检索（如有配置），按 traceId 串联
3. **数据库慢查询日志**：MySQL slow query log + EXPLAIN 分析
4. **Redis 监控**：Redis 命令耗时、内存使用率、连接数
5. **RocketMQ 控制台**：查看消息堆积量、消费延迟

**IRP 缺失的应急能力：**
- 无 Actuator 健康检查 → 无法快速确认服务是否存活
- 无 Sentinel 熔断 → 外部数据源超时时无法自动降级
- 无 Prometheus 告警 → 被动发现问题而非主动告警
- 无灰度发布 → 无法快速回滚到上一个版本
- 无开关配置 → 无法运行时动态关闭某个规则/数据源

### 二、业内标准应急处理流程

**四阶段应急响应（L0 → L4）：**

**L0: 发现（Detection）**
- Prometheus 告警触发：P99 延迟 > 1s / 错误率 > 1% / TPS 骤降
- 告警分级：P0（全链路挂）→ 5min 响应；P1（某服务异常）→ 15min；P2（非核心异常）→ 1h

**L1: 止损（Mitigation）——第一优先级**
- 切换到备用数据源（如主数据源超时，切换备用）
- 动态配置中心关闭问题规则（Feature Flag / Nacos 配置热更新）
- 服务降级：跳过非关键检查（如设备指纹），仅保留核心规则
- 限流：如果流量突发导致雪崩，触发限流
- 重启/回滚：单机问题则重启，代码问题则回滚

**L2: 定位（Diagnosis）**
- 按 traceId 在 ELK 中串联全链路日志
- Grafana 对比事发时间点的各指标变化
- Arthas/JProfiler 在线诊断（CPU 火焰图、线程 dump）
- 数据库慢查询分析 + 索引检查

**L3: 修复（Remediation）**
- 代码修复 → Code Review → 灰度验证 → 全量发布
- 配置修复 → 通过 Nacos 直接生效
- 基础设施修复 → 扩容 / 索引优化 / 连接池调参

**L4: 复盘（Postmortem）**
- 故障时间线梳理
- 根因分析（5 Why）
- 改进措施 + 责任人 + 截止日期
- 回归测试用例补充
- 监控告警规则补充

**具体例子：** 某风控平台支付决策 P99 飙升（200ms → 3000ms），处理流程：
1. P0 告警触发（L0）
2. 值班人确认异常，切流量到备用集群（L1，5 分钟）
3. 通过 traceId 找到慢调用链，发现外调人行征信接口超时（正常 50ms，当时 2000ms）（L2）
4. 将征信查询改为异步 + 降级：超时 500ms 则跳过征信，仅用其他规则评分（L3）
5. 复盘：征信接口无熔断保护 → 加 Sentinel 熔断 + 降级逻辑；征信调用无超时设置 → 加 500ms 超时（L4）

---

## Q7: 分享一个你处理过的典型线上 Bug 案例

### 基于 IRP 代码分析发现的潜在 Bug（具有典型性）

**案例一：Owl invokeAPi() 无超时 → 线程池耗尽**

`owl-execution/.../OwlFlowExecServiceImpl.java:29-48` 中，外部 API 调用（`invokeAPi()`）没有配置 connect timeout 和 read timeout。一旦外部数据源（如人行征信、设备指纹）响应变慢，HTTP 连接会一直挂起。

连锁反应：
```
invokeAPi() 挂起 → Owl 工作线程阻塞 → 线程池队列满
→ CustomThreadBuilder（core=2, max=10, queue=10, AbortPolicy）
→ 新任务被拒绝，抛 RejectedExecutionException → 决策全线失败
```

这是典型的**级联故障**——一个外部依赖变慢，拖垮整个决策链路。

**修复方向：** Feign 配置 connectTimeout=1000, readTimeout=3000；添加 Sentinel 熔断（错误率 > 50% 时熔断 60s）；降级逻辑：超时时跳过该数据源。

**案例二：BROADCASTING 模式下缓存不一致**

当 Raptor 某实例消费 RAPTOR_CACHE_SYNC 消息失败（如 OOM、网络闪断），该实例的缓存不会更新。但由于是广播模式，没有消费进度追踪，运维无法知道哪个实例缓存过期。

具体场景：运营人员更新了一条黑名单规则，广播消息发出。3 个实例中 2 个成功刷新缓存，1 个因 Full GC 暂停错过了消息（广播模式下消息不重投）。之后 30% 的请求路由到该实例 → 黑名单规则不生效 → 漏过欺诈申请。

**修复方向：** 改为 CLUSTERING 模式 + 消费成功后写 Redis，所有实例定时（每 10s）对比 Redis 版本号与本地缓存版本号，不一致则主动刷新。

**案例三：contains() 直接查 MySQL**

`kestrel/roster-app/.../RosterDetailService.java:198-207` 中，名单检查（白/黑/灰名单）使用 `contains()` 直接查询 MySQL，无 Redis 缓存。在高并发场景下，每次决策都查一次 MySQL 名单表，P99 延迟飙升。

**修复方向：** 名单数据加 Redis 缓存（TTL 5min），通过 Canal 监听 MySQL binlog 实时更新缓存。

### 业内经典 Bug 案例

**案例：缓存雪崩导致风控全线降级**

某消费金融公司，所有黑名单缓存在同一时间点过期（TTL 均为 24h），瞬间百万请求直接打到 MySQL，数据库 CPU 100%，决策超时。最终被迫关闭所有风控规则（裸奔状态 15 分钟），期间通过了 200+ 笔欺诈申请。

**根因：** 缓存 TTL 没有加随机抖动（jitter）。

**预防：** TTL = 24h + random(0, 3600s)，确保不同 key 的过期时间分散。

---

## Q8: 针对线上故障，有哪些事前预防和应急保障手段？

### 一、IRP 当前已有的保障措施

| 措施 | 实现情况 |
|------|----------|
| 多实例部署 | ✓ 各服务均为多实例部署（核心路径 3+ 实例） |
| Nacos 配置中心 | ✓ 配置热更新，无需重启 |
| SkyWalking 链路追踪 | ✓ `@Trace` 注解关键方法 |
| 分布式锁 | ✓ Redisson 防止定时任务重复执行 |
| RocketMQ 消息队列 | ✓ 削峰解耦 |
| 多数据源 | ✓ Dynamic Datasource 支持数据源切换 |
| 本地缓存 | ✓ Caffeine（100K，15d）降低 Redis 压力 |

### 二、IRP 当前缺失的保障手段

| 缺失项 | 风险 | 业内方案 |
|--------|------|----------|
| 熔断降级 | 外部依赖故障拖垮全链路 | Sentinel / Resilience4j |
| 限流 | 流量突发导致服务过载 | Sentinel 集群限流 |
| 灰度发布 | 全量发布 → 故障影响 100% 用户 | Nacos 灰度配置 / 蓝绿部署 |
| 健康检查 | 无法自动摘除问题实例 | Spring Boot Actuator + K8s Probe |
| 指标监控 | 被动等用户上报问题 | Prometheus + Grafana + AlertManager |
| 日志聚合 | 多实例日志分散，排查困难 | ELK / Loki |
| 压测 | 不清楚系统容量上限 | JMeter / wrk 定期全链路压测 |
| 混沌工程 | 不清楚各组件的容错能力 | ChaosBlade 注入故障验证 |
| 开关配置 | 无法运行时关闭问题功能 | Feature Flag / Nacos 开关 |
| 回滚机制 | 发版出问题只能等修复 | 发布时保留上一版本，支持一键回滚 |

### 三、业内标准预防+应急体系

**事前预防：**

1. **代码层面**
   - 所有外部调用必须有超时（connect + read）
   - 所有外部调用必须有熔断（Sentinel）
   - 所有线程池必须有拒绝策略 + 监控告警
   - 数据库查询必须有索引 + 分页
   - 缓存 TTL 必须加随机抖动避免雪崩

2. **发布层面**
   - 灰度发布：先 1 台 → 观察 10min → 10% → 观察 → 100%
   - Feature Flag：新功能上线用开关控制，出问题秒级关闭
   - 回滚预案：每次发布前确认回滚步骤，准备回滚脚本

3. **容量层面**
   - 每月全链路压测，建立容量模型
   - 自动扩容（K8s HPA 基于 CPU/Memory + 自定义指标）
   - 大促前 3 倍容量储备

**事中应急（四件套）：**

| 手段 | 说明 |
|------|------|
| 限流 | 入口限流，保护系统不被冲垮 |
| 熔断 | 外部依赖异常时快速失败，避免线程堆积 |
| 降级 | 关闭非关键功能（如设备指纹），保证核心链路可用 |
| 隔离 | 线程池/信号量隔离，保证一个功能故障不影响其他 |

**事后复盘：**
- 故障时间线 + 影响面积 + 根因分析 + 改进计划
- 每个改进项分配责任人和截止日期
- 补充监控告警和回归测试
- 季度汇总复盘，发现系统性风险

**具体例子：** 某头部互联网公司的风控平台保障体系：
- 每次发布 5 级灰度（1% → 5% → 20% → 50% → 100%，每级观察 10min）
- 全链路 3 倍容量压测（预期 TPS 1 万 → 压测 3 万）
- 30+ 个 Sentinel 熔断规则覆盖所有外部依赖
- 线上 500+ Prometheus 指标 + 50+ Grafana 看板 + 100+ AlertManager 规则
- 每年 4 次混沌工程演练（随机杀 Pod / 断网 / 磁盘满）

---

## Q9: 你们公司目前 AI 的应用情况如何？

### 一、IRP 系统 AI 应用现状

**1. 机器学习模型训练（algo-service + Merlin）**

IRP 有一套完整的 ML 模型全生命周期管理体系：

```
Merlin(Java) ──Feign──→ algo-service(Python FastAPI)
                           ├── AutoML 训练（XGBoost + Optuna 超参优化）
                           ├── 评分卡建模（WOE/IV 分箱）
                           ├── 决策树策略学习
                           └── Celery 异步任务队列
```

- **AutoML 自动训练**：Optuna 做超参数优化（learning_rate、max_depth、n_estimators 等），自动搜索最优参数组合
- **模型版本管理**：Merlin 管理模型元数据（训练人、训练时间、数据集版本、评估指标），支持模型注册 → 审批 → 部署全流程
- **模型部署**：训练完成后 PMML 格式导出，推送到 Raptor 的 PMML 插件加载
- **模型评估**：KS/AUC/PSI 指标监控，模型衰退自动提醒

**2. LLM 辅助决策树生成（algo-service/llm_decision_train.py）**

这是一个 8 阶段的 LLM 辅助决策树训练 Pipeline：

1. 数据加载 + 预处理
2. 特征工程（LLM 辅助特征筛选和组合）
3. 初始决策树生成（CART 算法）
4. LLM 节点语义分析（将树节点的规则条件转化为可读的业务描述）
5. LLM 规则优化（合并相似节点、简化冗余条件）
6. 规则验证（测试集评估准确率/召回率）
7. 可视化输出（决策树图形化）
8. PMML 导出（部署到 Raptor）

**3. AI 应用在 IRP 中的定位**

AI 在 IRP 中属于**规则引擎的补充**，不是替代：

- 规则引擎：处理确定性的、可解释的决策（命中黑名单 → 直接拒绝）
- ML 模型：处理概率性的、复杂的模式识别（欺诈概率 = 0.73）
- LLM：辅助人工建模（降低决策树设计的门槛）

### 二、业内 AI 在风控中的应用阶段

**第一阶：规则为主（传统风控，IRP 核心模式）**
- 专家经验 → 人工配置规则
- 优点：可解释性好，改动快
- 缺点：规则爆炸（几百上千条），维护成本高，无法发现新模式

**第二阶：规则 + 模型（当前主流，IRP 已达到）**
- 规则处理确定场景 + ML 模型处理概率场景
- XGBoost/LightGBM 做评分卡，NN 做复杂特征交叉
- 典型场景：信用评分（模型打分 + 规则兜底）

**第三阶：AI 原生风控（头部公司当前阶段）**
- 端到端深度学习模型做主决策，规则仅做安全兜底
- 图神经网络（GNN）做关联图谱反欺诈
- NLP 模型做文本风控（合同/聊天记录风险识别）
- CV 模型做图像风控（身份证明伪、PS 检测）
- 特征自动生成（AutoFE）+ 模型自动搜索（NAS）

**第四阶：LLM Agent 风控（前沿探索）**
- LLM 作为风控分析师的 Copilot——自然语言提问，自动生成风控报告
- LLM Agent 自主决策：从进件数据 → 分析推理 → 给出决策 + 解释
- 风险：幻觉（Hallucination）、不可解释性、延迟高（秒级 vs 毫秒级）
- 适用场景：复杂案件人工审核辅助，非实时决策

**具体例子：** 蚂蚁的风控 AI 应用：
- 图神经网络（GNN）构建 10 亿节点 + 100 亿边的关联网络，识别团伙欺诈
- 强化学习做动态定价（不同风险等级不同利率）
- LLM 做反洗钱可疑交易报告的自动生成（SAR 报告）
- 实时决策延迟 < 10ms（模型推理用 TensorRT + FPGA 加速）

**IRP 的 AI 发展建议路径：**
```
当前（规则+ML）→ 引入 GNN 做关联反欺诈 → 引入 LLM 做人工审核辅助
→ AutoFE 自动特征工程 → 端到端深度学习（仅在模型可解释性过关的低风险场景）
```

---

## Q10: Rete 网络具体是怎么构建的？全量重建还是增量更新？编译失败怎么处理？

### 一、IRP 系统写实

#### 编译管线

Raptor 的 Rete 网络编译是**全量重建**，没有增量更新机制：

```
XML (GZIP+Base64，存储在 t_rule_details.ruleExecuteData)
  → GzipUtil.decompressStr() 解压
  → DocumentHelper.parseText() → dom4j Element
  → AbstractBuilder.parseResource() → 按根节点类型分流到 5 种 ResourceBuilder：
      ├── RuleSetResourceBuilder     → 规则集（标准 if-then 规则）
      ├── DecisionTableResourceBuilder → 决策表（二维矩阵展开为规则）
      ├── DecisionTreeResourceBuilder  → 决策树（递归展开为规则）
      ├── ScorecardResourceBuilder    → 评分卡（每个评分项一个规则）
      └── CrosstabResourceBuilder     → 交叉表
  → RulesRebuilder.convertNamedJunctions() → 展开命名连接点
  → ReteBuilder.buildRete() → 构建 Rete 网络
      ├── 为每条有 LHS 的规则调用 buildBranch() → 依次构建每个条件的 CriterionNode
      ├── CriterionBuilder.buildCriteria() → Alpha 节点共享（同类型条件复用节点）
      ├── 无 LHS 规则分离到 noLhsRules 列表
      └── activationGroup 规则：单独构建互斥 Rete 子网络，按 salience 降序排序
  → KnowledgeBase（包装 Rete + ResourceLibrary + FlowMap）
  → KnowledgePackage（双重检查锁定懒加载）
  → KnowledgeSession
```

**全量重建的细节：**

`KnowledgeBuilder.newBuildKnowledgeBase()` 每次收到 XML 字符串时：
1. 解析 dom4j `Element`
2. 根据 `ruleType` 和 `runType` 决定编译策略
3. 当 `ruleType == "rule-set" && runType == "1"`（顺序模式）时，**每条规则独立创建一个 KnowledgeBase**，按 salience 排序
4. 其他情况下，所有规则共享一个 KnowledgeBase
5. 调用 `ReteBuilder.buildRete()` 从零构建 ObjectTypeNode → CriteriaNode → JunctionNode → TerminalNode

**Alpha 节点共享：** `CriterionBuilder.fetchSameCriteriaNode()` 检查同类型条件节点是否已存在——如果规则 A 和规则 B 都有 `age > 18` 这个条件，它们共享同一个 CriteriaNode。但注意：这只是**单次编译内的共享**，重新编译时一切从头开始。

#### 编译失败处理

| 失败环节 | 触发条件 | 异常 |
|----------|----------|------|
| XML 解析 | `DocumentHelper.parseText()` 失败 | `RuleException` |
| 找不到条件构造器 | `CriterionBuilder` 不支持该条件类型 | `RuleException(URuleExceptionEnum.URULE_ERROR_133033)` |
| 规则流引用自身 | `RuleFlowService.checkRuleFlowReference()` DFS 检测到环 | `ServiceException(ResultEnum.REFERENCE_ERROR)` |
| 规则流嵌套过深 | `CacheService.doBuildKnowledge2()` 递归超 3000 层 | `RuntimeException(ResultEnum.REFERENCE_ERROR)` |

**编译失败的关键保护：** `KnowledgeBuilder.newBuildKnowledgeBase()` 用 `try-finally` 包裹 `localThreadCacheUtil` 资源，确保异常时清理。但编译失败**不影响正在运行的 KnowledgeSession**——已缓存的旧 KnowledgeBase 继续服务，直到新版本编译成功并替换缓存。

#### 运行时 → 缓存的路径

编译后的 KnowledgeBase 存入 Caffeine 缓存（Key: `LOCAL:CHAIN:{strategyId}:{ruleCode}:{ruleVersion}`），15 天有效。CacheController 暴露 `GET /api/core/cache/buildKnowledge` 端点可手动触发重建。

### 二、业内做法对比

| 维度 | IRP 当前 | 业内做法 |
|------|----------|----------|
| 编译方式 | 全量重建 | Red Hat Drools：支持增量 KieBase 更新；规则变更时仅 recompile 受影响的规则 |
| Alpha 节点共享 | 单次编译内共享 | Drools：跨编译周期的节点池，compile-time 和 runtime 都用同一个 NodeFactory |
| 编译失败隔离 | 旧缓存继续服务 | 编译沙箱（Sandbox Compilation）：新版本先在沙箱里编译+验证，通过后原子替换 |
| 编译产物持久化 | 每次从 XML 重新编译 | 预编译：将 KnowledgeBase 序列化为二进制（如 Drools 的 serialized KieBase），启动时直接加载 |
| 编译性能 | 解析+编译+缓存 | 预编译 + 冷启动直接反序列化（无需解析 XML），启动时间从几十秒降到几百毫秒 |

**具体例子：** 某银行的 Drools 规则引擎有 800+ 条规则，每次修改一条规则就重新编译全部 800 条需要 8 秒。改用 Drools 的增量 KieBase 更新后，单个规则的变更仅需 200ms。同时他们预编译 KieBase 为二进制（`kieBase.toByteArray()`），服务重启时直接反序列化（200ms），而非从 DRL 文件重新解析编译（15s）。

---

## Q11: 规则冲突是怎么检测和解决的？

### 一、IRP 系统写实

IRP **没有编译时的规则冲突静态分析**，完全依赖运行时的 Agenda 三层机制来解决。

#### Agenda 三层 RuleBox 层次

```
Agenda.execute()
  │
  ├── 第 1 层: AgendaGroupRuleBox（执行组）
  │   ├── 规则按 agenda-group 属性分组
  │   ├── 只有被 focus() 激活的组才执行
  │   ├── 组内规则按 salience 排序
  │   └── 一组执行完标记 executed=true，永不再次执行
  │
  ├── 第 2 层: ActivationGroupRuleBox（互斥组）
  │   ├── 规则按 activation-group 属性分组
  │   ├── 每个组内：命中一条规则后，整个组标记 executed=true，
  │   │   组内其他激活全部清除（activations.clear()）
  │   └── 编译时组内规则已按 salience 降序排序
  │
  └── 第 3 层: ActivationRuleBox（默认）
      ├── 没有 agenda-group 和 activation-group 的规则
      └── 所有激活按 salience 排序后依次执行
```

#### 优先级（Salience）机制

`ActivationImpl.compareTo()` 中实现：

```java
public int compareTo(Activation o) {
    Integer o1 = o.getRule().getSalience();  // 另一条规则的 salience
    Integer o2 = this.rule.getSalience();    // 本规则的 salience
    if (o1 != null && o2 != null) return o1 - o2;  // 高 salience 排前面
    ...
}
```

**两处排序：**
1. 编译时：`ReteBuilder.buildActivationRetesMap()` 对互斥组内的规则按 salience 排序
2. 运行时：`AbstractRuleBox.addActivation()` 每次添加激活时 `Collections.sort(list)`

#### 规则冲突检测的缺失

**没有**类似 Drools 的 `enabled` / `no-loop` / `lock-on-active` 等冲突控制属性。没有规则条件重叠分析（"规则 A 的条件是 `age>18`，规则 B 的条件是 `age>20`——当 `age=25` 时两条都会命中，这是冲突还是合理设计？"系统不区分）。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 冲突检测 | 无编译时检测 | Drools 支持规则分析（`drools-verifier`）：检测条件冗余、条件重叠、冲突规则对 |
| 规则优先级 | salience 数值 | 多维度：salience + rule-flow-group + lock-on-active + no-loop + enabled |
| 互斥组 | ActivationGroup（一次执行） | Drools 的 ruleflow-group / agenda-group 更灵活，支持条件性重新激活 |
| 规则条件分析 | 无 | 决策表逻辑完整性检查（Gap Analysis）：某些输入组合是否漏掉了规则覆盖 |

**具体例子：** 某保险公司的 1200 条理赔规则中，用 Drools-verifier 扫描出 47 对条件重叠规则（如"金额>10万 拒"和"金额>5万 且 出险次数>3 拒"），其中 12 对是真正的冲突（相同条件不同结论）。人工审查 1200 条规则根本不可能逐个比对。

---

## Q12: 规则流嵌套深度与死循环怎么防范？

### 一、IRP 系统写实

IRP 有**四层**递归/循环保护机制，但质量参差不齐。

#### 第 1 层：保存时编译检查（有效）

`RuleFlowService.checkRuleFlowReference()`：

```java
// DFS 深度优先搜索检测环
private void recursionRuleFlowRefer(String ruleDetailCode, 
    Set<String> visited, List<String> currentPath) {
    if (currentPath.contains(ruleDetailCode)) {
        throw new ServiceException(ResultEnum.REFERENCE_ERROR.getMessage());
    }
    if (visited.contains(ruleDetailCode)) {
        return;  // 不同路径已访问过，OK
    }
    currentPath.add(ruleDetailCode);
    visited.add(ruleDetailCode);
    // 递归遍历所有子节点中的 RULE_FLOW 类型节点
    for (RuleFlowVariable child : ...) {
        if (RuleTypeEnum.RULE_FLOW.getCode().equals(child.getRuleType())) {
            recursionRuleFlowRefer(child.getRuleTargetCode(), visited, currentPath);
        }
    }
    currentPath.remove(ruleDetailCode);  // 回溯
}
```

**这是最靠谱的一层。** 标准的 DFS + path 判环算法，在规则保存时触发。如果检测到 A→B→C→A 这样的环，直接抛异常禁止保存。

#### 第 2 层：运行时构建保护（有但粗糙）

`CacheService.doBuildKnowledge2()`：

```java
if (recursionCount > 3000) {
    throw new RuntimeException(ResultEnum.REFERENCE_ERROR.getMessage());
}
```

只靠一个 3000 的深度计数器。**不是真正的环检测**——如果真的有环，递归会一直跑到 3000 才被发现。

#### 第 3 层：定时器刷新保护（有 Bug）

`RefreshCacheTimer.getSubDetailCode()` 中同样的 3000 深度限制，但递归调用时**没有递增 `recursionCount`**：

```java
// 递归调用时传的是原值，没有 +1
this.getSubDetailCode(ruleDetailsCode, flowSet, ... , recursionCount);
```

所以这个检查**永远不会触发**——`recursionCount` 保持不变，除非最初传入 >3000（不会发生）。

#### 第 4 层：规则代码收集（无保护）

`CacheService.doGetAllRuleCode()` 递归遍历规则流收集所有子规则代码，**没有任何深度限制或环检测**。如果编译时检查被绕过（比如通过直接写 DB 的方式插入数据），这个方法会无限递归直到栈溢出。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 环检测 | 保存时 DFS（有效）、运行时计数（粗糙） | 编译时构建有向图，检测强连通分量（Tarjan 算法），一次找出所有环 |
| 递归上限 | 3000 硬限制 | 通常 50-100 即警告，因为规则流嵌套超过 10 层已经很难维护 |
| 保护一致性 | 4 个递归方法中 2 个有保护、1 个有 bug、1 个无保护 | 统一用 AOP 或递归工具类，所有递归入口统一拦截 |
| 规则流复杂度 | 无限制 | 规则流复杂度评分（圈复杂度），超过阈值拒绝上线 |

---

## Q13: 一次决策的完整 Audit Trail 是怎么设计的？

### 一、IRP 系统写实

IRP 有三层审计日志，但没有统一的端到端还原能力。

#### 第 1 层：Tamer 网关入口日志

`TraceFilter.java` 为每个请求生成 `traceId`（UUID），MDC 存放，注入请求头 `Tamer-Request-Id` 透传全链路。`AuditLogsMqDTO` 包含 21 个字段：租户信息、用户信息、请求 URL/参数/Headers、响应体、耗时、traceId。通过 RocketMQ 发送到 Nest 服务存入 `t_nest_audit_logs` 表。

#### 第 2 层：Owl 执行日志

`OwlLogAdvice.java` 用 Spring AOP 拦截 `OwlExecController.*`：
- 记录 `OwlDataExecDTO`（完整请求参数 JSON）
- 记录整次决策耗时 `requestTime`（StopWatch.totalTimeMillis）
- 写入 `t_dc_visit_record` 表（字段：`dataServicePubCode`、`applyNo`、`requestParam`、`result`、`requestTime`、`requestId`、`tenantCode`、`organizeCode`）

`OwlCallResultAdvice.java` 额外通过 RocketMQ 发送监控数据，包含每个外部数据源的调用详情（`DataSchemeCallRecordParam`）。

#### 第 3 层：Raptor 执行详情（最富信息，但可选）

`ChainService.getRuleOutputContent()` **当 `executeDeatilFlag=true` 时**输出极为详细的执行追踪：

```java
LiteflowRuleContext 包含：
- executeVarCateMap    // 每个节点的变量在"执行前"和"执行后"的完整状态
- matchNodes           // 流程中所有遍历过的节点（线程安全列表）
- ruleRespMap          // 每个执行节点的规则引擎原始响应
- flowMatchRuleDetailList  // 命中的规则列表，含每条规则的变量名→值映射
- allTempResultMap     // 每个规则的中间计算结果
```

- **`ExecuteDetailNode`**：每个流程节点的 `nodeId`、`ruleDetailCode`、`timeSpent`、`ruleName`、`ruleVersion`、`ruleType`，以及执行前后变量值的变化
- **`MatchRuleDetailInfo`**：每条命中规则的 `ruleDetailCode`、`ruleName`、`ruleType`、`toNodeInfo`（决策路由）、`ruleDetailInfo`（包含所有输出变量及运行时实际值）
- **`NodeInfoItemVo`**：流程中所有遍历节点的列表
- **`highLightList`**：流程图中高亮的边（决策走的是哪条分支）

#### 能还原到什么程度？

| 能回答的问题 | 能回答吗 | 依据 |
|-------------|----------|------|
| 这笔进件走了哪条策略？ | ✓ | `VisitRecordEntity.dataServicePubCode` |
| 耗时多少？ | ✓ | `VisitRecordEntity.requestTime` |
| flow 里走了哪些节点？ | ✓ | `matchNodes`（需 executeDeatilFlag=true） |
| 命中了哪些规则？ | ✓ | `flowMatchRuleDetailList` |
| 每条规则用了什么数据？ | ✓ | `ruleDetailInfo` 里的变量名→值映射 |
| 该数据是几点几分几秒的值？ | ✗ | 没有数据时间戳 |
| 当时外部数据源返回了什么？ | 部分 | 外部调用日志存在 MQ 监控数据中，不与决策记录关联存储 |
| 规则条件为什么匹配/不匹配？ | ✗ | 命中列表里只记录"命中了"，不记录每个条件的评估过程 |

**关键问题：** 最详细的 trace（`executeDeatilFlag=true`）只在 `RuleContentResp` 中返回，**不是每次都持久化到数据库**。`t_dc_visit_record.result` 字段只存了最终结果 JSON，不含执行细节。这意味着事后详细回溯依赖当时请求是否开启了详细模式。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 审计数据生命周期 | executeDeatil 可选、不强制持久化 | 所有生产流量 100% 存储完整执行 trace（至少保留 90 天） |
| 数据时间戳 | 无 | 每个变量值附带 `dataTimestamp`，明确数据是几时几分几秒的快照 |
| 决策快照 | 无 | Decision Snapshot：把一次决策的全部上下文（输入、中间变量、规则匹配、输出）打包为一个不可变 JSON → S3/OSS 永久存储 |
| 可回溯性 | 靠多个表的 JSON 字段手动拼 | Event Sourcing：每个决策事件（`DecisionRequested`→`RuleMatched`→`DecisionMade`）是独立事件，完整 replayable |

**具体例子：** 某支付公司因监管要求，每笔风控决策的完整 trace 必须保存 5 年。他们用 Decision Snapshot 模式：一次决策产生一个完整 JSON（~50KB），写入 S3，MySQL 只存 S3 key 和元数据。5 年内任何时间可以通过 traceId 还原完整决策过程到变量级别。

---

## Q14: ML 模型（PMML/XGBoost）的决策结果怎么向业务方解释？

### 一、IRP 系统写实

**在线运行时完全不提供模型可解释性。**

`ModelLearnPlugin.pmmlExecute()` 的运行时流程：

```java
// 1. 从 RuleDetails.ruleExecuteData 读取 PMML XML 字节流
// 2. 用 JPMML 库解析 → ModelEvaluator
// 3. 构造参数 Map → modelEvaluator.evaluate(argumentMap)
// 4. 根据 respMap 过滤输出
// 5. 返回结果映射：outputVariable.setValue(modelOutput)
```

**没有 SHAP、没有 LIME、没有特征归因。** 模型只输出一个分数（如 `fraud_probability = 0.73`），没有任何关于"这个分数怎么来的"的解释。

**离线训练端有，但不传到在线：**
- `algo_service/train_service/reporter/feature_explain_report.py`：`explain_feat()` 使用 `shap.TreeExplainer(model)` 计算全局 SHAP 值
- `algo_service/core/metric/var_detail_metric.py`：计算边际贡献（`_calc_marginal_contribution()`），按优先级尝试 `shap.Explainer` → `shap.LinearExplainer` → `shap.TreeExplainer`
- `algo_service/train_service/train/trainers/trainer.py`：`get_feature_importance()` 提取 `feature_importances_`
- 但这些结果仅用于**训练报告和离线分析**，没有持久化到模型文件（PMML）中，也不传递给在线引擎

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 解释粒度 | 无（只有一个分数） | 逐特征贡献分解：`Score=0.73 = base(0.5) + age(+0.08) + credit_history(+0.10) + device_count(+0.05)` |
| 解释延迟 | — | SHAP 预计算特征归因矩阵 + 在线查表（<1ms 附加延迟） |
| 面向业务 | 无 | 生成人类可读解释文本："该申请风险较高的原因是：①近7天申请次数过多(12次) ②设备关联多个风险账号" |
| 合规 | 不满足 | 银保监会《商业银行互联网贷款管理暂行办法》要求自动化决策给出明确拒绝理由 |

**具体例子：** 某银行的信用评分模型上线时，监管要求每笔拒绝必须附带"拒绝原因"。他们的做法是：离线用 SHAP 为每个特征训练一个分段解释函数（如"年收入 < 3 万 → +15 分风险分"），在线时查出每个特征贡献的 TOP 3 作为拒绝理由，随决策结果一起返回。对 0.73 的欺诈分，自动生成解释："风险较高（73%），主因：设备关联多个风险账号（+12%）、近30天借贷申请次数异常（+8%）、手机号在网时长不足（+5%）"。

---

## Q15: 进件数据有没有质量校验层？

### 一、IRP 系统写实

**答案：有一层，但远不完整。**

#### Tamer 网关：不做业务校验

Tamer 只做 RSA+AES 解密和 JWT 认证，对业务字段（身份证号、手机号、金额）**零校验**。`StrUtils.java` 里定义了 `MOBILE_CHECKER = Pattern.compile("^1\\d{10}$")`，但这个 Pattern **没有被任何过滤器或控制器调用**——写了，但没人用。

#### Peregrine：运行时必填+正则校验

`StrategyVariableService.checkRequiredParams()`：
- 基于 `isRequired=true` 的变量定义，检查每个必填字段是否有值
- 如果有缺失，返回缺失变量的列表（而非直接拒绝）

`StrategyVariableService.checkRegexValidation()`：
- 对值非空的字段按配置的正则表达式校验
- **但空值直接通过正则校验**（`StringUtils.isNotBlank(curValue)` 为 false 时跳过）

#### Seagull-web：静默跳过

`AviatorWorker.execResultBySqlLogic()`：
```java
if (!param.containsKey(vcVarParamVo.getParamCode())) {
    hasNullValue = true;
    break;  // 整个表达式跳过计算
}
if (hasNullValue) { 
    return varExecuteResult;  // 返回 null，无日志（除非耗时 > 20ms）
}
```

如果计算一个指标需要 3 个参数但其中 1 个缺失，这个指标**根本不算**。没有报错、没有警告（除非耗时超过 20ms）、没有降级默认值。`JaninoWorker` 使用完全相同的静默跳过策略。

#### Raptor：null 传播

`ValueCompute.fetchValue()`：当变量的分类对象找不到时返回 null，null 在算术表达式中被转换为字符串 `"null"` 参与计算。

#### 缺失值处理总结

| 场景 | IRP 当前行为 | 风险 |
|------|-------------|------|
| 必填字段缺失 | Peregrine 检测并返回缺失列表 | 低 |
| 非必填字段缺失 | 没有任何默认值填充 | 高——null 静默传播 |
| 指标计算参数缺失 | Seagull 跳过该指标，无报错 | **高**——下游规则悄悄拿到更少的数据 |
| 数据格式不正确 | 仅通过正则校验的字段；空值跳过正则 | 中 |
| 表达式执行异常 | 被 catch，仅慢操作（>20ms）才记日志 | **高**——正常速度下的错误完全不可见 |

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 入站校验 | 仅必填+正则 | 多层校验：格式校验→业务规则校验→外部数据交叉验证 |
| 缺失值策略 | 静默跳过 | 三级策略：默认值填充（指定fallback值）→ 标记忽略（规则跳过该变量）→ 拒绝进件（关键字段缺失必须人工补全） |
| 数据质量监控 | 无 | 实时数据漂移检测：突然 30% 进件某个字段为空 → 告警 |
| 校验失败可观测 | Seagull 异常被静默吞 | 所有校验失败计数为 Prometheus 指标，Grafana 看板可视化 |

**具体例子：** 某互联网银行的风控入站校验层包含：身份证号 Luhn 算法校验 + 公安部实名认证 API → 手机号运营商三要素验证 → 银行卡号 BIN 码校验 + 银联无卡认证。任何一步校验失败都产生一个 `DataQualityEvent` 写入 Kafka，实时聚合到 DataDog 看板。

---

## Q16: 规则修改了 Fact 后，后续规则看到的是旧值还是新值？

### 一、IRP 系统写实

这个问题很关键——直接关系到规则执行结果的一致性。

#### 默认执行模式：单通道评估 + 共享引用

`KnowledgeSessionImpl.execute()`：

```java
// 1. 一次性 Rete 匹配：所有 facts 遍历 Rete 网络
for (Object fact : facts) {
    evaluationRete(fact);   // 确定所有匹配路径
}
// 2. 构建 Else 规则和无 LHS 规则
agenda.buildElseRules();
agenda.buildNoLhsRules();
// 3. 执行 Agenda（一次）
agenda.execute(filter, max);
// 4. 重置网络，清除 facts
reset();
```

关键事实：**`evaluationRete()` 和 `agenda.execute()` 之间没有重新评估。** 所有匹配都在第一遍完成，然后按顺序执行命中的规则。

#### 变量修改的三种路径

| 修改方式 | 代码位置 | 后续规则是否可见 | 机制 |
|----------|----------|-----------------|------|
| `VariableAssignAction` 修改 parameterMap | VariableAssignAction.java | **是** | 获取的是同一个 `HashMap` 引用（`context.getWorkingMemory().getParameters()`），就地修改。后续规则调用 `getParameter(key)` 时读到新值 |
| `VariableAssignAction` 修改 NamedReference | VariableAssignAction.java | **是** | 从规则的 `variableMap` 获取同一个 Java 对象引用，`Utils.setObjectProperty()` 就地修改 |
| 规则 RHS 调用 `session.update(fact)` | KnowledgeSessionImpl.java | **是（立即重新评估）** | `update()` 立即调用 `reevaluate(obj)`，重新评估所有激活并触发新匹配 |

#### 关键约束：条件匹配 vs Action 读取的可见性差异

```
帧 1: evaluationRete() —— 确定所有匹配
帧 2: agenda.execute() 开始
  帧 2a: 规则 A 的 Activation.execute() → VariableAssignAction 修改 paramMap 的某个值
  帧 2b: 规则 B 的 Activation.execute() → 从 paramMap 读该值 → 看到的是 A 修改后的值
  帧 2c: 规则 C（条件依赖该字段）的 Activation → 条件判断基于 Rete 匹配时的旧值，
         不是 B 看到的新值！因为 Rete 匹配已经完成，不会重新匹配
```

**结论：** 值修改后，后续规则的行为取决于它是通过条件匹配（基于旧值）还是 Action 内读取（基于新值）。这种不一致是一个潜在的隐蔽 Bug 来源。

#### 特殊情况：顺序模式（`runType="1"`）

当 `runType="1"` 时，每条规则有独立的 KnowledgeBase，规则逐一执行。**此时前一条规则的修正确实会影响后一条规则的条件匹配**（因为后一条规则有独立的 Rete 匹配过程）。但这是特例。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| Fact 修改模型 | 就地修改 + 隐式依赖 | 不可变 Fact 模型：修改动作产生新 Fact 实例，原有实例不变，显式管理依赖 |
| 重新评估控制 | 单通道 + 手动 `update()`/`retract()` | Drools 的 `modify()` 自动触发增量匹配（只重新评估受影响的节点，不是全部重来） |
| 规则执行可见性 | 规则值修改对后续规则的 Action 可见但对条件匹配不可见 | Drools 保证 StatefulKnowledgeSession 中所有修改立即反映到条件匹配中 |

**具体例子：** Drools 中调用 `modify($fact) { setAge(30) }` 后，引擎自动触发 `updateToFacts()` → 只重新评估事实匹配网络中被该字段类型影响的节点 → 后续规则的 LHS 条件自动基于新值匹配。整个过程是增量且一致的，不会出现"条件匹配用旧值、Action 读取用新值"的不一致。

---

## Q17: 离线特征怎么同步到在线引擎？

### 一、IRP 系统写实

IRP **没有实时流特征存储（Feature Store）**，离线特征同步走的是**批量回溯系统 Owl-baffle**。

#### Baffle 回溯系统

`VcVarBackService.java`（2240 行）支持 4 种回溯类型：

| 类型 | 导入方式 | 说明 |
|------|----------|------|
| `FILE` | ZIP/JSON/XML/Excel 上传 | 业务方把离线数据打包上传 |
| `API_UPLOAD` | HTTP API 批量提交 | 其他系统通过 API 推送数据 |
| `API_DB` | 外部数据库直接查询 | Baffle 直连外部 DB 拉数据 |
| `DATABASE` | 内部 MySQL 查询 | 从 IRP 自己的库拉历史数据 |

支持 2 种触发模式：
- **`MANUAL`**：人工上传文件 → 触发回溯
- **`TIME`**：Quartz cron 表达式定时执行

#### 回溯机制的问题

1. **这不是实时同步，是批量重放**。一个"近 30 天逾期次数"的特征不会实时更新；它依赖上游系统定期打包数据上传
2. **文件级别的安全校验存在**：ZIP 炸弹检测（压缩比）、路径回溯防护（`validateAndSanitizeZipEntryName()`）、Excel 表头一致性校验，但这些都是文件格式层面的，不是数据质量层面的
3. **变量系统的割裂**：Peregrine 维护一套变量（公共变量 + 策略变量），Raptor 序列化为自己的 XML 格式，Seagull-web 又有独立的 `t_vc_var_base_def` 表——三套系统，通过 RocketMQ 弱一致性同步

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 特征同步 | 批量文件上传 + 重放 | Feature Store（Feast/Feathr）：离线特征离线计算→存入特征平台→在线引擎低延迟读取（<5ms） |
| 一致性 | 弱最终一致（MQ 广播无 ACK） | T+1 批量写入 Redis/自研 KV + 版本号校验 |
| 特征时间旅行 | 不支持 | 支持 Point-in-time Query："给我看看 2026-01-01 这个 user 的特征值（用于训练数据构造）" |
| 特征血缘 | 无（三套独立的变量系统） | 元数据中心记录每个特征的来源、计算逻辑、依赖关系 |

**具体例子：** 字节跳动的风控 Feature Store 架构：离线 Spark/Flink 任务每天凌晨计算 5000+ 特征 → 存入自研 ByteKV（基于 RocksDB）→ 在线引擎通过 SDK 低延迟读取（P99 < 1ms）。特征版本化，训练时点 Time-travel Query 保证训练/在线特征一致性（不会出现"训练时用的是 T+1 特征，在线用的是 T+0 特征"的偏移）。

---

## Q18: 模型从训练到上线的完整流程和耗时？

### 一、IRP 系统写实

#### 完整流水线

```
Step 1: Merlin 配置并启动训练
  MerlinModelTrainingVersionServiceImpl.save() → 创建训练版本 (v1.0)
  → startTraining() → Feign → algo-service /api/v1/algo/train
  → 状态 = WAIT_PROCESS

Step 2: algo-service 异步训练
  Celery Worker 消费任务
  → 数据加载 → 预处理 → Optuna 超参搜索 → XGBoost/LightGBM 训练
  → 评估 (KS/AUC/PSI) → 报告生成 → PMML 导出
  → 状态回调 Merlin: SUCCESS

Step 3: 审批流
  Flowable BPMN 流程: 注册 → 审核 → 审批
  ModelStageStateMachine 管理状态转换
  PENDING_REGISTRATION → REGISTRATION_COMPLETED
  → PENDING_REVIEW → REVIEW_COMPLETED → 可部署

Step 4: 部署到 Raptor
  MachineLearningService.uploadModel()
  → 分析 PMML (ModelAnalyseService.analysisPMMlModelFile())
  → 提取 InputField/OutputField
  → GZIP+Base64 存入 t_rule_details.ruleExecuteData
  → 创建 StrategyVariable（模型输出变量映射）
  → RocketMQ 广播 → 所有 Raptor 实例刷新缓存
```

#### 时间估算

| 环节 | 耗时 | 操作方 |
|------|------|--------|
| 训练+评估 | 几分钟到几小时（取决于数据量和 Optuna trials） | algo-service 自动 |
| 注册+审核+审批 | **不确定（人工瓶颈）** | 人工 Flowable |
| PMML 上传+分析 | < 1 分钟 | 自动 |
| 缓存生效 | < 30 秒（RocketMQ 广播延迟） | 自动 |
| **总计** | **从几分钟到几天（人工审批是瓶颈）** | — |

#### 版本切换方式

**瞬间切换，非灰度。** 当策略引用的模型版本更新后，RocketMQ 广播 → 所有 Raptor 实例 `CacheService.delLibrary() + doBuildKnowledge()` → 下一次请求自动加载新模型。没有新旧模型并行运行的过渡期。`ModelLearnPlugin.pmmlExecute()` 每次调用都重新解析 PMML（没有缓存编译后的 ModelEvaluator，每次都解析 XML），这意味着切换是实时生效的。

#### 模型回滚

**没有一个"一键回滚到上一版本"的机制。** Merlin 的 `ModelStageStateMachine.onActivityCancelled()` 只处理 Flowable 审批流的回退（回到上一审批状态），不涉及已部署模型的替换。"回滚"需要人工在 Peregrine 中将策略版本指回旧模型。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 部署方式 | 瞬间全量切换 | 模型灰度：新旧模型并行运行，按流量比例切换（5%→20%→50%→100%） |
| 回滚 | 需人工操作 | 一键回滚：模型版本号指针切换，秒级生效 |
| 在线/离线一致性 | PMML 纯文本传输 | 模型注册表（Model Registry）：MLflow / Seldon，版本化模型+环境+参数 |
| PMML 编译缓存 | 每次请求重新解析 | 预编译 + 缓存 ModelEvaluator，首次加载后 < 1ms |
| 审批流自动化 | 完全人工 | 自动验收门禁：新模型 A/B 测试指标（PSI < 0.1, KS drop < 5%）达标才自动推进到审批 |

**具体例子：** 某银行的 ML 平台用 MLflow Model Registry 管理 200+ 个模型。新模型上线是 MLflow 的 `transition_model_version_stage("Production")` 一个 API 调用。网关侧根据模型版本号路由流量，10% 走新模型，90% 走旧模型。自动比对 1 小时内的拒绝率/通过率，如果偏差 < 5% 且 PSI 稳定，自动将新模型提升到 50% → 100%。

---

## Q19: 模型衰退（Model Drift）是怎么监控的？

### 一、IRP 系统写实

**答案：没有在线模型衰退监控。**

PSI、KS、AUC 等指标的计算发生在 algo-service 的**训练期间**：

- `ScoreStabilityMetric`：训练时计算 PSI（模型对训练集和测试集的评分分布差异）
- `KSSummaryMetric`、`AUCMetric`、`SummaryMetric`：训练时计算 KS、AUC、准确率
- 这些指标写入 `MerlinModelTrainingReport`（训练报告），保存在 Merlin 的数据库中

**这些是模型版本级别的评估，不是持续监控。** 模型部署后，IRP 不会持续跟踪：
- 在线特征的分布是否偏离训练集分布（Feature Drift）
- 在线评分分布是否随时间漂移（Score Drift）
- 模型的拒绝率/通过率分布是否异常变化

**唯一相关的机制：** `ModelBackConfigService.modelBackAnalysis()` 可以手动触发历史数据回溯，对比"旧策略+旧模型"和"旧策略+新模型"的决策差异。但这是按需操作，不是持续监控告警。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| PSI 实时监控 | 无（仅训练时） | 每日/每小时计算在线评分 PSI，PSI > 0.25 触发告警 |
| 特征漂移 | 无 | 每个特征的在线值分布 vs 训练集分布，Jensen-Shannon 散度 / Wasserstein 距离 |
| 自动衰退告警 | 无 | Prometheus 指标 + AlertManager："模型 M123 的 PSI(7d) = 0.31，建议重训练" |
| 自动重训练 | 不支持 | 衰退触发自动重训练 Pipeline（更新数据→重训练→评估→如指标达标→灰度上线） |

**具体例子：** 某消费金融公司的风控模型监控体系：每天凌晨 2 点计算昨日所有模型的 PSI（按分数分 20 个 bin）、特征 KS 值（TOP 20 特征）。PSI > 0.25 → P2 告警（1 周内需重训练），PSI > 0.35 → P1 告警（24h 内需重训练），同时自动启动重训练 Pipeline。整套监控的看板放在 Grafana 上，PM 也能看到哪些模型需要"保养"。

---

## Q20: AB 测试具体是怎么做的？

### 一、IRP 系统写实

Peregrine 有完整的 AB 测试框架。

#### 两种实验模式

| 模式 | 引擎 | 做法 |
|------|------|------|
| **AB Test** | `AbtestRunExecuteEvent` | A 和 B **都跑**，对比结果 |
| **Champion-Challenger** | `CcRunExecuteEvent` | **只跑一个**，按权重选 |

#### AB Test 执行逻辑

```
Step 1: 执行 A（Champion）
  → runService.execute() 同步调用 → 保存 A 结果（CHAMPION 标识）

Step 2: 判断是否需要执行 B（Challenger）
  → 两种过滤模式：
    - RATIO: RouteUtil.weightedRoundRobinOne() → random(1,100) < percent → 执行 B
    - AVIATOR: 用 Aviator 表达式条件过滤（如仅某产品/某租户 → 执行 B）

Step 3: 执行 B（Challenger）
  → defaultPool.execute() 异步 → raptorOpenApiFeign.strategyExecute(B 策略配置)
  → 保存 B 结果（CHALLENGER_1 标识）

Step 4: 流量计数
  → Redis INCR(REDIS_OPTIMIZE_BTEST_TOTAL_PREFIX + batchId)
```

**关键设计：**
- A 是**同步**执行的，确保主流程不受影响（返回给客户的是 A 的结果）
- B 是**异步**执行的（线程池），B 的延迟不影响客户体验
- B 的流量通过配置的比例控制（比如 30% 的进件触发 B）

#### Champion-Challenger 执行逻辑

```
Step 1: 加权随机选一个策略
  → RouteUtil.weightedRoundRobin(ss) → 按配置权重选择 A 或 B
  → 只有被选中的策略执行，不比对 A 和 B
```

**Champion-Challenger 本质上是灰度发布，不是实验分析。**

#### 实验结果评估

```
对 A 和 B 的结果分组统计：
- 每组各决策结果的计数（通过数、拒绝数、人工审核数）
- 各决策结果的百分比（通过率、拒绝率）
- 环比（Ring Ratio）: calculateRingRatio() → (B_pct - A_pct) / A_pct * 100
- 方向指示: "up"、"down"、"equal"
```

**没有显著性检验。** 环比计算是纯算术的，不涉及置信区间、p 值或统计显著性判断。"B 的通过率比 A 高 5%"可能只是随机波动，但 IRP 不做这种区分。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 实验分析 | 仅环比 | 显著性检验（t-test / chi-square）+ 置信区间 + 最小检测效应（MDE） |
| 分流 | 随机百分比或 Aviator 表达式 | 哈希分流（基于 User ID / Device ID MD5 → 取模），保证同一用户始终进同一组 |
| 同时跑两组 | AB Test 是（A 同步 + B 异步） | 拦截分流：在 Tamer 网关层分流，A 和 B 完全独立执行，互不影响 |
| 实验时长 | 配置固定截止日期或进件量 | 基于统计功效自动计算所需样本量（Power Analysis），达标后自动结束 |
| 监控 | 基本计数（Redis INCR） | 实时实验仪表盘 + SRM 校验（Sample Ratio Mismatch 检测分流偏差） |

**具体例子：** 字节跳动的风控 AB 实验平台：基于 `device_id MD5` 的前 2 位做 0-99 的分桶，实验配置 10 个桶给 B（10% 流量），90 个桶给 A。每天凌晨自动计算 t-test p-value 和置信区间，当 B 的某指标（如拒绝率）p < 0.05 且实验进行超过 7 天，自动推送给 PM "实验达到统计显著性，B 拒绝率提升 12.3%（95% CI: 8.1%-16.5%）"。

---

## Q21: 新策略在 AB 实验效果好，怎么推到全量？

### 一、IRP 系统写实

**没有自动灰度推进机制。** 完全依赖人工操作。

#### Champion-Challenger 作为灰度工具

CC 模式可以模仿灰度发布：

```
初始: Champion 90% × Challenger 10%
 ↓ 观察几天，效果 OK
配置更新: Champion 70% × Challenger 30%
 ↓ 再观察
配置更新: Champion 50% × Challenger 50%
 ↓
配置更新: Champion 0% × Challenger 100%  ← 新策略上位
```

但**权重调整完全是手动的**——运营人员在 Peregrine 管理后台修改配置百分比，没有自动级进。

#### 策略版本切换

策略上线还有一个额外的机制：Peregrine 的 `StrategyVersionService`。策略版本切换通过 RocketMQ 广播（`peregrine_strategy_change` Topic）通知 Owl 和 Raptor 刷新缓存。但这也不是灰度——是版本指针的瞬间全量切换。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 灰度推进 | 手动调整权重 | 自动化灰度 Pipeline：1%→5%→20%→50%→100%，每步自动观察 10min-1h |
| 自动回滚 | 无 | 任何一步检测到指标异常（错误率/拒绝率 P 值异常）→ 自动回滚到上一级 |
| 审批流程 | 完全的 Flowable 工作流（慢） | 基于指标的自动门禁 + 人工一键审批（快） |
| 回滚速度 | 需人工改配置 | 一键回滚 / API 调用，秒级生效 |

**具体例子：** 某 SaaS 风控平台的自动灰度流程：选择"启动灰度" → 平台自动执行 5%→20%→50%→100%，每级运行 30min。每级结束时自动检查：错误率 < 0.1%、P99 延迟 < 120% 基线、拒绝率变化 < 20%（vs 对照组）。任何一级不通过 → 自动回滚到上一级并告警。整个过程无需人工干预。

---

## Q22: 单次决策的 P99 延迟和性能基线？

### 一、IRP 系统写实

**没有系统性的性能基线和回归检测。**

#### 现有的性能测量

| 测量点 | 工具 | 记录位置 |
|--------|------|----------|
| Owl 整次决策 | `org.springframework.util.StopWatch` | `VisitRecordEntity.requestTime` (DB) |
| 每个外部 API 调用 | `StopWatch` 单独计时 | RocketMQ 监控数据 |
| Raptor 规则执行 | LiteFlow `CmpStep.timeSpent` | `ExecuteDetailNode` (仅详细模式) |
| Raptor 每个组件 | `System.currentTimeMillis() - start` | 日志 |
| Seagull 指标计算 | `StopWatch`（仅慢查询 > 20ms） | 日志 |

**注意：** CLAUDE.md 中提到 SkyWalking `@Trace`，但实际代码中主链路是 `StopWatch` 计时——说明 SkyWalking 的集成不完整或只用于链路追踪（traceId 级联），没有用于性能指标收集。

#### 关键线程池配置

| 服务 | 关键线程池 | Core/Max | 风险 |
|------|-----------|----------|------|
| owl-execution LiteFlow | CustomThreadBuilder | 2/10, Queue=10, **AbortPolicy** | 队列满就抛异常 |
| owl-execution Tomcat | server.tomcat | min-spare=100, max=800 | — |
| peregrine 主业务 | commonExternalExecutor | 30/30, Queue=10000, CallerRunsPolicy | — |
| raptor 知识编译 | doBuildKnowThreadPoolTask | 10/20, Queue=1000, CallerRunsPolicy | — |

**最大的性能风险点：**
1. **owl-execution 的 LiteFlow 并行池**：`CustomThreadBuilder`（Core=2, Max=10, Queue=10, **AbortPolicy**）——这是链路核心，一旦队列满（仅 10 个排队），直接抛 `RejectedExecutionException`，导致决策中断
2. **owl-execution 的 per-request 线程池**：`OwlExecBO.createExecutorService()` 为每个请求创建一个线程池，`leafCnt`（树的最大宽度）个线程——高并发时可能创建大量线程
3. **所有外部 HTTP 调用无熔断**：外部数据源变慢直接拖垮调用线程

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 性能基线 | 无 | 每次发版前全链路压测，P50/P99/P999 作为性能基线写入版本发布 check list |
| 性能回归检测 | 无 | CI/CD 集成性能测试（JMH 微基准 + Gatling 全链路），P99 退化 > 10% 阻止发布 |
| 分布式追踪 | 仅链路传播（traceId），无 APM 指标 | SkyWalking/Jaeger + OpenTelemetry → 自动采集 P99 分布 |
| 线程池监控 | 无（无 Actuator + Micrometer） | Spring Boot Actuator + Micrometer → Prometheus → Grafana 线程池仪表盘 |

**具体例子：** 某风控系统的性能 CI Pipeline：每次 PR 合并触发 Gatling 压测（模拟 2000 QPS），自动对比基线的 P99/P999。如果 P99 从 120ms 涨到 150ms（+25%），Pipeline 标记为 WARN；如果涨到 200ms（+67%），禁止合并。这让他们在过去一年阻止了 14 次性能退化。

---

## Q23: 大促扩容方案和瓶颈在哪？

### 一、IRP 系统写实

**没有容量规划文档、没有压测脚本、没有自动扩容配置。**

#### 现有资源池配置

| 资源 | 配置 | 瓶颈风险 |
|------|------|----------|
| Tomcat 线程 | owl-execution: max 800, accept 1000 | 中等——800 线程在 4C8G 机器上偏多但够用 |
| MySQL 连接池 | owl-execution: max 50, raptor-core: max 50 | 高——连接池小，高 QPS 时易耗尽 |
| Redis 连接池 | 所有服务: max-active=20, max-idle=10 | 高——如果大量缓存穿透，20 个连接不够 |
| HTTP 连接池 | RestTemplate: maxTotal=200, maxPerRoute=20; brConfig: maxTotal=800 | 中 |
| Caffeine 缓存 | raptor: maxSize=100K, 15天 | 中——100K 条目如果存了太多不用的规则 |
| RocketMQ Producer | sendMsgTimeout=60s, retry=3次 | 低 |

#### 扩容的核心问题：Raptor 冷启动

Raptor 新实例启动 → Caffeine 缓存为空 → 第一个请求需要 `doBuildKnowledge()` 全量编译：
- 递归遍历整个规则流树（含嵌套）
- 从 DB 加载所有 StrategyVariable
- 编译 Rete 网络
- 构建 LiteFlow 链

**这个过程的耗时取决于规则复杂度**——简单规则几十 ms，嵌套很深的规则流可能需要几秒。在这期间，第一个命中该规则的请求会等几秒（或超时）。

#### IRP 如果能扩容，步骤是：

```
1. 启动新实例 → 等待 Spring Boot 启动完成（~30s）
2. 向 Nacos 注册（~5s 生效）
3. Tamer 开始路由流量到新实例
4. 新实例的第一个请求触发缓存 miss → 编译规则（可能几百 ms）
5. 后续请求命中缓存 → 正常
```

**关键：** Raptor 本质上接近无状态（规则编译产物在 Caffeine 里，可通过 MQ 广播同步），所以可以水平扩容。但冷启动的缓存预热没有自动化——目前需要等自然请求触发编译，或手动调 `CacheController.buildKnowledge()` API。

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 扩容 | 手动启动 + 手动注册 Nacos | K8s HPA：基于 CPU/Memory/自定义指标（决策 QPS/P99）自动扩缩 |
| 冷启动 | 自然预热（请求触发编译） | 预编译 + 二进制序列化 + 启动时自动预热缓存（Eager Loading） |
| 容量规划 | 无 | 每月全链路压测，确定单机 QPS 上限 → 大促前按 3x 扩容 |
| 自动降级 | 无 | 排队过深时自动开启降级（跳过非关键外部调用） |

**具体例子：** 某支付公司的风控扩容体系：全链路压测确定单机最大 1500 QPS，大促预期 15000 QPS → 扩到 12 台（15000/1500 * 1.2 安全系数）。K8s HPA 基于 Prometheus 自定义指标 `decision_qps_per_pod` 自动扩缩。新 Pod 启动后 10s 内完成缓存预热（从共享 Redis 拉取预编译的 KnowledgeBase 二进制），然后通过 Readiness Probe 后才接流量。

---

## Q24: 外部数据源调用成本怎么优化？

### 一、IRP 系统写实

#### 现有的优化措施

**1. 同请求内去重：** `OwlExecBO.removeDuplicateParents()` 在构建执行树时移除重复的父节点——同一外部数据源在同一个执行流程中不会重复调用。

**2. 跨请求缓存：** `ApiInvokeServiceImpl` 三级策略：
```
isCallLocalDataOnly() → true: 仅查本地 DB 缓存表
isCache=0 → 每次都调用外部 API
isCache=1 → 先查 t_ds_service_calll_result 表（按 cacheKey），miss 再调用
```

缓存 key 由 `ServiceInputParamEntity.cacheKeySort` 控制的参数排序拼接后 Base64。缓存过期时间按数据源配置（`cacheTimeOut` + `cacheTimeType`，小时/天）。

**3. Auth Token 缓存：** `URLConfigPatcher` 用 Redisson `RBucket` 缓存外部数据源的认证 token（如 OAuth2 access token），避免每次调用都重新认证。

#### 缺失的优化

| 缺失项 | 说明 |
|--------|------|
| 调用量监控 | 没有按数据源、按租户维度的调用次数/费用统计 |
| 重复调用检测 | 跨**不同决策流**间没有去重——流 A 和流 B 如果都查同一个设备指纹，各查各的 |
| 成本分摊 | 无法按租户拆分每个外部数据源的调用费用 |
| 调用量预警 | 没有"某数据源今日调用量已达配额的 90%"的告警 |
| 批量查询优化 | 单笔进件的多个外部数据查询是否可以合并为一个批量请求 |

### 二、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 调用量监控 | 无 | 每个数据源的每次调用都计入 Prometheus Counter（按 supplier + API + tenant 打标） |
| 费用归因 | 无 | 每个决策的外部数据成本 = Σ(每个数据源单价 × 是否命中缓存)，按租户出费用报表 |
| 全局去重 | 仅同流内 | 分布式去重缓存（Redis Set + TTL）：同一 device_id 在 TTL 内只查一次设备指纹 |
| 智能降级 | 无 | 按数据源价值分级：一级数据源（身份证验证）必须调用；二级数据源（社交画像）成本超预算时降级跳过 |
| 成本优化 | 无动态策略 | 动态路由：低成本数据源先行→判断风险已足够高/低→跳过高成本数据源 |

**具体例子：** 某互联网金融公司的外部数据调用成本优化：每月外部数据费用 200 万+，分析发现 30% 的设备指纹查询是重复的（同一设备短时间内多次查询）。引入 Redis 去重缓存（key = `device:{deviceId}`, TTL = 5min），缓存命中即免调，年省 70 万。进一步引入动态路由——先调便宜的（IP 风险库，免费），如果风险分已 > 80 或 < 20 就直接决策，不再调贵的人行征信（每次 1 元），年省 50 万。

---

## Q25: 冷启动、预编译、预热、热更新这几个概念怎么区分？IRP 里各服务分别用到了哪些？

### 一、概念区分

这四个词经常被混在一起讨论，但它们本质上解决的是不同问题，发生在不同时间点：

| 概念 | 发生时机 | 本质 | 解决什么问题 |
|------|---------|------|-------------|
| **冷启动** | 服务刚启动 | 是**问题状态**（缓存空、规则未加载），不是解决方案 | 首批请求延迟高，需要等加载完成 |
| **预编译** | 启动时 / 规则变更时 | 将规则/表达式提前编译为可执行形式，剥离编译开销 | 避免首次执行时的编译延迟（如 Aviator→字节码、URule XML→Rete 网络） |
| **预热** | 启动后、接流量前 | 主动触发加载，解决冷启动问题 | 服务启动后即处于热状态，首批请求延迟与稳态一致 |
| **热更新** | 运行期间 | 不重启、不中断流量，运行时替换规则/配置/开关 | 规则变更不停机生效 |

**关系一句话总结：冷启动是病，预编译和预热是治病的药，热更新是运行期间换药方不停诊。**

具体来说：

- **预编译 vs 预热**：预编译只解决"编译慢"的问题；预热解决所有初始化开销（编译 + 缓存加载 + 连接池填充等）。预编译是预热的一种手段。
- **预热 vs 热更新**：预热是一次性的（启动时），热更新是持续性的（运行时）。预热让服务"从冷变热"，热更新让服务"热着换东西"。
- **为什么经常一起讨论**：如果一个系统规则变更需要重启，那每次重启都是一次冷启动，预热就显得至关重要；如果系统支持热更新，冷启动的频率就大大降低。

### 二、IRP 各服务实际使用情况

#### 预编译（Pre-compilation）—— 使用最广泛

**Raptor — URule 规则 XML→Rete 网络编译**
- 入口：`CacheService.doBuildKnowledge()` → `KnowledgeBuilder.newBuildKnowledgeBase()`
- 过程：DB 读取规则 XML → Base64 解码 → GZIP 解压 → XML 解析 → 构建 Rete（Alpha/Beta 节点）→ 生成 `KnowledgeBase[]` → 存入 Caffeine
- 支持递归编译规则流（`doBuildKnowledge2`，递归深度上限 3000）
- 6 种规则类型各自有独立的 `ResourceBuilder`：`DecisionTreeResourceBuilder`、`ScorecardResourceBuilder`、`DecisionTableResourceBuilder`、`RuleSetResourceBuilder`、`FlowResourceBuilder`、`CrosstabResourceBuilder`

**Seagull-web — Janino 表达式→Java 字节码编译**
- `JaninoScriptCompiler.compile()` 将指标表达式动态编译为 `.class` 字节码，`CompiledJavaScript` 缓存在内存 Map 中
- `AviatorToJaninoConverter` 负责将 Aviator 表达式语法转为 Janino Java 代码
- 配置项 `precompile-enabled: true`、`precompile-count: 20`，启动时预编译前 20 个热点变量
- 通过 `cacheHitCount` / `compilationCount` 统计命中率

**Seagull-web — Groovy 脚本预编译**
- 配置 `groovy.precompile-enabled: true`、`groovy.cache-size: 11000`
- 编译产物写入 `${java.io.tmpdir}/groovy-compiled`

**Seagull-common — 正则表达式静态预编译**
- `ValueCompile` 类中日期格式、变量匹配等正则表达式在 JVM 类加载时即完成 `Pattern.compile()`

#### 预热（Warm-up）—— Nest 完善，Raptor 缺失

**Nest — 启动时全量预热（做得最好）**
- `AllCacheInit` 聚合所有缓存初始化器，统一在服务启动时执行
- 各初始化器继承 `AbstractNestCachInit`，通过 `@Order` 控制执行顺序，通过 Redis 分布式锁防止多实例同时预热冲突：

| 初始化器 | 预热内容 | 加载方式 |
|----------|---------|---------|
| `NestOrgCacheInit` | 组织架构树（所有租户） | 分页查 DB → 构建父子关系 Map → 写入 Redis |
| `I18nCacheInit` | 国际化消息配置 | 分页查 DB → 按 appName+locale 分组 → 写入 Redis Hash |
| `NestPermissionCacheInit` | 权限/菜单数据 | 查 DB → 写入 Redis |
| `NestRoleCacheInit` | 角色数据 | 查 DB → 写入 Redis |
| `NestDicRdInit` | 字典数据 | 查 DB → 写入 Redis |

**Raptor — 无自动预热（已知痛点）**
- 文档明确指出：「冷启动的缓存预热没有自动化——目前需要等自然请求触发编译，或手动调 `CacheController.buildKnowledge()` API」
- 新实例启动时 Caffeine 缓存为空，第一个请求需要 `doBuildKnowledge()` 全量编译，延迟显著高于稳态
- API `GET /api/core/cache/buildKnowledge` 是当前唯一的手动预热入口，需要知道具体的 `strategyId`、`ruleCode`、`ruleVersion`

#### 热更新（Hot Update）—— 多服务使用，但 Raptor 的未启用

**Tamer — 网关开关热更新（Redis Pub/Sub）**
- `TamerSwitchService` 提供 5 个开关：登录鉴权、URL 权限、用户级 URL 权限、租户级 URL 权限、审计日志
- 修改流程：`setXxxSwitch(value)` → 写入 Redis value → `convertAndSend(channel, value)` 广播
- `TamerSwitchRedisMessageListener` 订阅 Redis channel，收到消息后反射更新 `TamerSwitch` 静态字段，**不重启、不停流量**

**Peregrine — 策略变量热更新（RocketMQ BROADCASTING）**
- 策略变量在管理后台修改后，通过 RocketMQ BROADCASTING 模式通知所有实例刷新缓存
- 变量缓存 key 带 `updateTime` 版本号，新版本写入后旧版本自然过期，实现无感切换
- 变量缓存 TTL 为 3 天

**Nest — 国际化缓存热更新（Redis Pub/Sub）**
- `I18nCacheInit.setCache()` 写入 Redis 后通过 `convertAndSend(STURNUS_I18N_PUBSUB_KEY)` 通知所有实例
- `I18nCacheInit.remove()` 支持单条缓存删除并广播

**Raptor — 规则缓存热更新（设计了但未启用）**
- `CacheMessageListener` 实现了 `MessageListener` 接口，`onMessage` → `CacheStrategy.updateLocalCache()`
- 但 `redisMessageListenerContainer()` 中 `container.addMessageListener(...)` 被注释掉了（`CacheMessageListener.java:65`），意味着 Redis Pub/Sub 热更新通道**实际未工作**
- 当前规则变更后的生效方式是：手动调 buildKnowledge API，或等旧缓存自然过期后被新请求触发重新编译

**Algo-service — Python Graph 组件热更新（importlib reload）**
- 通过 `importlib.import_module` → `reload` 动态重新加载 Python 模块，注入新的 Pipeline 组件
- `@pipeline_sidecar` 装饰器注册组件到 sklearn Pipeline，无需重启 Flask 服务

#### 冷启动（Cold Start）—— Raptor 的核心痛点

**Raptor 冷启动问题详细分析：**

```
新实例启动 → Caffeine 缓存为空
  → 第一个请求到达
    → DB 查询 RuleDetails + RuleConfig
    → KnowledgeBuilder.newBuildKnowledgeBase()
      → XML 解析
      → Rete 网络构建（CPU 密集，800+ 条规则可能需要数秒到数十秒）
      → 写入 Caffeine
    → 后续请求命中缓存，延迟正常
```

**为什么严重**：
- Raptor 是一个规则对应一个 `KnowledgeBase`，不是全局一份——有多少个已发布的决策节点/规则流，就需要编译多少次
- 每个 KnowledgeBase 的编译是独立的、CPU 密集的，多线程并发编译会争抢 CPU
- 冷启动期间首批请求的 P99 可能从稳态的 ~20ms 飙升至数秒

**Nacos 配置热更新带来额外冷启动**：
- Raptor 不需要冷启动之外的额外 Nacos 热更新机制，因为规则编译产物的生命周期由 Caffeine TTL 控制
- 但 Nacos 配置变更（如数据源切换）会让相关 Bean 重新初始化，间接触发局部缓存失效

### 三、对比总结

| 机制 | Raptor | Seagull-web | Nest | Tamer | Peregrine | Algo-service |
|------|--------|-------------|------|-------|-----------|-------------|
| **预编译** | URule→Rete（核心） | Janino字节码 + Groovy字节码 + 正则Pattern | — | — | — | — |
| **预热** | 手动 API（无自动化） | Groovy 预编译 20 个热点变量 | 5 个 CacheInit 启动时全量加载 | — | — | — |
| **热更新** | Redis Pub/Sub（已实现但未启用） | — | Redis Pub/Sub（国际化） | Redis Pub/Sub（5个开关） | RocketMQ 广播（策略变量） | importlib reload |
| **冷启动问题** | **存在，是核心痛点** | 部分缓解（预编译热点） | 已解决（启动预热完全覆盖） | — | — | — |

### 四、业内做法

| 维度 | IRP 当前 | 业内 |
|------|----------|------|
| 预编译粒度 | 每次从 XML 重新编译 | 预编译 + 编译产物序列化（如 Drools 的 `KieBase.toByteArray()`），启动时反序列化（200ms vs 15s） |
| 预热自动化 | Raptor 无自动预热 | K8s Pod 启动 → 自动从 Redis 加载预编译 KnowledgeBase 二进制 → Readiness Probe 通过 → 才注册到 Nacos 接流量 |
| 热更新原子性 | 规则变更后手动触发/自然过期 | 规则新版本先在沙箱编译验证 → 验证通过后原子替换本地 KnowledgeBase 引用 → 旧版本延迟 GC |
| 冷启动优化 | 无 | ① 增量编译（只变更的规则重新编译）；② 共享节点池（Drools NodeFactory 跨编译周期复用）；③ 快照预热（定期将全量 KnowledgeBase 序列化到 Redis，新实例启动直接加载） |

**具体例子：** 某银行的 Drools 规则引擎有 800+ 条规则，每次修改一条规则就重新编译全部 800 条需要 8 秒。改用 Drools 增量 KieBase 更新后，单个规则的变更仅需 200ms。同时预编译 KieBase 为二进制（`kieBase.toByteArray()`），服务重启时直接反序列化（200ms），而非从 DRL 文件重新解析编译（15s）。

---

## Q26: 这份压测报告怎么解读？水平如何？瓶颈在哪？怎么优化？

### 一、压测数据

```
测试名称: 小雨点性能测试_20260424_211054
并发用户: 100
执行时长: 1分9秒

平均 TPS:    98.13      峰值 TPS:  117.76
平均 QPS:    98.13      峰值 QPS:  117.76
总请求:      6771       成功: 6678 | 失败: 93
成功率:      98.63%

平均响应时间: 854.53 ms      范围: 66.00 ~ 7954.00 ms
P50:          703.00 ms
P90:          1532.00 ms
P95:          2068.50 ms
P99:          3151.90 ms
```

### 二、水平评价：中等偏下，有明显优化空间

对于 **100 并发、单链路同步调用** 的风控决策场景：

| 指标 | 实测值 | 及格线 | 良好 | 优秀 |
|------|--------|--------|------|------|
| 平均 TPS | 98 | 100 | 300-500 | 1000+ |
| 平均响应时间 | 854ms | <500ms | <200ms | <100ms |
| P99 | 3152ms | <2000ms | <500ms | <200ms |
| 成功率 | 98.63% | >99.9% | >99.99% | 100% |
| 响应时间跨度 | 66~7954ms（120倍） | — | — | — |

**结论：能用，但不够好。** 三个致命信号：

1. **P99 是平均值的 3.7 倍**（3152 vs 854）——存在严重的**长尾延迟**，少量慢请求拖垮了整体 P99
2. **93 次失败（1.37%）**在风控场景不可接受——一次失败可能意味着该笔业务被超时放过或拒绝，业务损失比技术指标更严重
3. **响应时间跨度 120 倍**（66ms~8s）——系统行为极不稳定，大概率存在冷编译/缓存未命中/GC 停顿

### 三、瓶颈排查（按 IRP 调用链逐层分析）

IRP 的同步调用链：`Tamer → Peregrine → Owl-execution → Raptor + Seagull-web + 外部API`

#### 可能性最高：Raptor 规则冷编译

**现象匹配度：极高。** P99=3152ms、最大值=7954ms、响应时间方差巨大，这些完全符合"部分请求触发编译、部分命中缓存"的模式。

**原因**：压测前如果没手动预热（调 `/api/core/cache/buildKnowledge`），首批请求会触发 `CacheService.doBuildKnowledge()` → XML 解析 → Rete 网络构建。单次编译耗时 1-5 秒，这直接解释了 P99 的 3152ms 和 7954ms 的最大值。

**验证方法**：
```bash
# 看 Raptor 缓存命中率
curl http://raptor:9034/api/core/cache/stats
# hitRate 如果偏低，说明大量请求 miss 触发了编译

# SkyWalking 中看 Raptor 节点的耗时分布
# 如果前几十秒 P99 极高、后面逐渐稳定，就是冷编译
```

#### 可能性次高：外部数据源调用超时

**现象匹配度：高。** 最大值 7954ms 符合外部 HTTP 调用的典型超时模式（默认连接超时 + 读取超时会累积到 8 秒左右）。

**原因**：Owl-execution 调用外部 API（设备指纹、征信等），外部服务响应慢或超时直接拖长整个决策链路。

**验证方法**：
```sql
-- 查看外调记录表的耗时分布
SELECT call_time, response_time, TIMESTAMPDIFF(ms, call_time, response_time) AS latency
FROM t_ds_service_calll_result
WHERE call_time > '2026-04-24 21:10:00'
ORDER BY latency DESC LIMIT 20;
```
或在 SkyWalking 中看 `ApiInvokeServiceImpl` span 的耗时。

#### 可能性第三：DB 连接池/慢查询

**现象匹配度：中等。** 如果缓存 miss 后触发了 DB 查询，且 DB 连接池不够大，请求会排队等连接。

**验证方法**：
```bash
# 压测期间看 Druid 监控
curl http://<service>:<port>/druid/datasource.html
# 关注 ActiveConnections / WaitThreadCount
```

#### 可能性第四：Feign 连接池/线程池耗尽

**现象匹配度：中低。** 100 并发不算高，Tomcat 默认 200 线程通常足够。但如果单请求占用线程 3 秒+，200 线程在 100 并发下 2 秒就会耗尽。

**验证方法**：
```bash
# 压测期间执行
jstack <pid> | grep -E "BLOCKED|WAITING|http-nio" | sort | uniq -c | sort -rn
# 看 http-nio 线程是否大量处于 BLOCKED/TIMED_WAITING
```

#### 93 次失败必须定位

失败可能是两类完全不同的原因：
- **连接拒绝（Connection Refused）**：线程池满了，请求根本没进去 → 需要增大线程池
- **响应超时（Read Timeout）**：请求进去了但处理太慢，超过了 JMeter 的 timeout → 需要优化业务逻辑

**验证方法**：看 JMeter 的 jtl 原始结果中 93 个失败请求的 `responseCode` 和 `responseMessage` 字段，区分是连接层还是业务层错误。再看 SkyWalking 中对应时间点的 trace 是否完整（有 trace 说明进入了服务，无 trace 说明被拒绝在网关/OS 层面）。

### 四、优化方案（按投入产出比排序）

#### 立即见效（不改代码，压测前操作）

**1. 压测前手动预热 Raptor 规则**
```bash
# 对每个已发布的策略/规则调用 buildKnowledge
curl "http://raptor:9034/api/core/cache/buildKnowledge?strategyId=1&ruleCode=CREDIT_RISK&ruleVersion=v1.0"
```
消除冷编译带来的长尾延迟。预期效果：P99 可降低 50%+。

**2. 增大 Tomcat 线程池**
```yaml
server:
  tomcat:
    threads:
      max: 500        # 默认 200
      min-spare: 50
    accept-count: 200
```
100 并发 × 同步链 4 跳（Tamer→Peregrine→Owl→Raptor），最坏情况下需要 400 个线程同时工作。

**3. 确认 JMeter 超时配置**
如果 JMeter 的 connect/response timeout 设得太短（如 3 秒），部分正常慢请求会被算作失败。确保 JMeter timeout ≥ 10 秒，再逐步收紧。

#### 短期改进（小改动，1-3 天）

**4. Raptor 启动时自动预热**
```java
@PostConstruct
public void warmUp() {
    List<RuleDetails> publishedRules = ruleDetailsService.queryAllPublished();
    for (RuleDetails rule : publishedRules) {
        doBuildKnowledge(rule.getRuleCode(), rule.getRuleVersion(), 0);
    }
}
```
新增 `RaptorWarmUpRunner` 实现 `ApplicationRunner`，服务启动后自动预编译所有已发布规则。预期：新实例启动后首次请求延迟与稳态一致。

**5. 外部数据源调用加超时和降级**
```java
// Feign 配置
feign:
  client:
    config:
      default:
        connectTimeout: 1000   # 连接超时 1 秒
        readTimeout: 3000      # 读取超时 3 秒
```
外部调用超时后，用本地缓存数据兜底，不要让一次外部超时拖垮整笔决策。

**6. 启用 Raptor Redis Pub/Sub 热更新**
取消 `CacheMessageListener.java:65` 的注释，让规则缓存支持热更新。减少因缓存过期导致的重新编译频率。

#### 中期重构（较大改动，1-2 周）

**7. 外部 API 调用异步并行化**
Owl-execution 中对同一笔决策的多个外部数据源调用改为 `CompletableFuture.allOf()` 并行执行：
```
当前（串行）: 查设备指纹(800ms) → 查IP风险(600ms) → 查征信(1000ms) = 2400ms
优化（并行）: max(800, 600, 1000) = 1000ms  节省 58%
```

**8. KnowledgeBase 序列化到 Redis**
```java
// 编译后序列化到 Redis，7 天有效
byte[] data = serialize(knowledgeBase);
redis.set("kb:" + ruleCode + ":" + ruleVersion, data, 7, TimeUnit.DAYS);

// 启动时直接从 Redis 反序列化
byte[] data = redis.get("kb:" + ruleCode + ":" + ruleVersion);
KnowledgeBase kb = deserialize(data);
```
预期：冷启动从几十秒降到几百毫秒。这是 Q25 中提到的业内标准做法。

**9. 增加 Readiness Probe**
K8s 或部署脚本中增加健康检查，只有 `CacheService.isWarmUpComplete()` 返回 true 后才将实例注册到 Nacos 接流量。防止未预热的实例被流量打挂。

### 五、优化后预期效果

| 指标 | 优化前 | 第1-3项后 | 第4-6项后 | 第7-9项后 |
|------|--------|----------|----------|----------|
| 平均 TPS | 98 | 120-150 | 200-300 | 500+ |
| 平均响应时间 | 854ms | 400-600ms | 200-300ms | <150ms |
| P99 | 3152ms | 1500-2000ms | 500-800ms | <300ms |
| 成功率 | 98.63% | >99.5% | >99.9% | >99.99% |
| 响应时间方差 | 120x | 10-20x | 5-10x | <5x |

### 六、一句话总结

这份压测报告的水平在风控决策系统中**属于一般偏下**，核心问题是**Raptor 规则冷编译导致的长尾延迟**加上**外部数据源超时**共同造成的 P99=3.1s 和 93 次失败。最快的验证方式是看 SkyWalking 中各跳耗时分布和 Raptor 缓存命中率——如果确认是冷编译，压测前手动预热就能让 P99 下降 50% 以上。长期来看，KnowledgeBase 序列化 + 启动自动预热 + 外部调用异步并行化是三个最值得投入的优化方向。

---

## Q27: Rete 算法有什么缺点？适用哪些场景？还有没有其他规则引擎算法，各有什么优劣？

### 一、Rete 算法的先天不足

Rete 算法由 Charles Forgy 于 1974 年提出，核心思想是用**空间换时间**——通过构建 Alpha/Beta 节点网络来复用条件匹配结果，避免每次重复评估所有规则。但这个设计本身就带来了几个不可消除的劣势：

| 缺点 | 本质原因 | 触发条件 | 严重程度 |
|------|---------|---------|---------|
| **内存膨胀** | 整个 Alpha/Beta 网络 + 工作内存（Working Memory）常驻内存，中间 token 数量可能远超规则数 | 事实对象数量多（万级+）、事实类型多、join 节点多 | ★★★★★ |
| **事实变更开销大** | 增/删/改任意事实都需要从 Root Node 开始传播 token 遍历整个网络，修改一个属性等于触发一次全网传播 | 同一决策周期内频繁修改事实、大量事实的批量插入 | ★★★★ |
| **修改规则 = 重建网络** | 任何一条规则的条件变更都可能导致 Alpha/Beta 节点布局变化，难以增量局部更新 | 规则频繁变更、规则迭代快 | ★★★★ |
| **小规模场景反而更慢** | 构建 Rete 网络本身有开销（编译、节点分配、共享检测），简单 if-else 直接执行比构建网络再匹配更快 | 规则数量 <20、条件简单、单一事实类型 | ★★★ |
| **并行化天然困难** | Token 在 Alpha/Beta 节点间串行传播形成依赖链，节点 A 的输出是节点 B 的输入 | 需要极致低延迟的高并发场景 | ★★★ |
| **调试困难** | 内部状态黑盒——哪个 token 走了哪条路径、为什么某个规则没触发，难以观测 | 规则冲突排查、规则上线前验证 | ★★ |

**Rete 适用场景的判断标准：**

```
适合 Rete 的特征（越多越适合）:
  ✓ 规则数量 >50，且有大量条件重叠（共享 Alpha 节点收益高）
  ✓ 事实对象数量适中（单次决策 <1000个事实）
  ✓ 事实在决策期间不频繁修改（一次性插入后只匹配不修改）
  ✓ 规则变更频率低（一天改几次，不是每分钟改）
  ✓ 需要高吞吐的模式匹配

不适合 Rete 的特征（任一就要考虑替代方案）:
  ✗ 规则 <20条——直接用表达式引擎或决策表更简单
  ✗ 事实数量 >10000——内存会炸，考虑流式处理
  ✗ 事实频繁修改——每次修改都遍历网络，考虑 Phreak 或无状态评估
  ✗ 规则每天改几十次——重建开销太大，考虑表达式引擎
  ✗ 条件简单无共享——Rete 共享收益为零，用决策树
```

**IRP 为什么选 Rete 是对的：** 风控场景的典型特征是规则多（50-200+条）、事实相对稳定（一次进件的事实集不变）、规则有大量共享条件（如多个规则都检查 `amount > 10000`），这正是 Rete 的甜点区。

### 二、其他规则引擎算法对比

#### 1. Phreak（Drools 6+ 默认算法）

**特点：** Rete 的进化版，保留了 Rete 的 Alpha 网络，但 Beta 部分改用基于规则优先级（salience）的延迟执行，结合了 LEAPS 的懒惰求值思想。不主动传播 token，而是由规则"拉取"所需事实。

| 优点 | 缺点 |
|------|------|
| 内存效率比 Rete 高 30-50%（不需要 Beta Memory 存全部中间 token） | 首次触发延迟比 Rete 略高（需要遍历"拉取"过程） |
| 支持增量规则更新（`KieScanner` 热加载），只重建受影响的子网 | 规则间依赖关系复杂时，延迟执行的顺序可能难以预测 |
| 规则冲突更容易预测（按 salience 定序，同一优先级按 LIFO） | 社区和文档远不如 Rete 丰富，调优资料少 |
| 可以和 Rete 共存——Drools 允许在部分规则集上使用 Phreak | 仅 Drools 支持，不像 Rete 有多个独立实现 |

**适用场景：** 需要运行时动态增删规则的生产系统；需要热更新能力且不希望触发全量重建的场合；内存受限的大规模规则集。

---

#### 2. LEAPS（Lazy Evaluation Algorithm for Production Systems）

**特点：** 基于栈的懒惰求值策略。不构建固定的 Beta 网络，而是在匹配时动态搜索——从一个"种子事实"出发，按规则条件逐步反向查找其他事实。只在需要时才计算，算完即丢弃。

| 优点 | 缺点 |
|------|------|
| 启动极快：不需要预编译 Rete 网络，规则加载后立即可用 | 大量事实时性能比 Rete 差——每个规则都要独立搜索，复杂度 O(n×m) |
| 内存极省：不存 Alpha/Beta 网络，无中间 token | 多条规则之间无任何条件共享，重复计算多 |
| 事实增删无代价：不需要传播 token，下一个触发周期自然体现 | 事实优先匹配（seed-fact-driven），一个事实可能被多个规则重复查找 |

**适用场景：** 事实量小、规则频繁变更的原型开发阶段；规则集经常动态变化、启动速度优先于吞吐量的场景；单次决策事实少（<10）、规则中等（<50）的小型决策系统。

---

#### 3. Treat Algorithm

**特点：** Rete 的简化版——保留 Alpha 网络做条件过滤，但**去掉 Beta Memory**。冲突解决时不是从缓存读取匹配集合，而是每次重新遍历 Alpha 网络结果来计算。

| 优点 | 缺点 |
|------|------|
| 内存占用明显低于 Rete（Beta Memory 是 Rete 最大的内存开销） | 冲突解决时需要重新计算，频繁触发规则时效率不如 Rete |
| 实现比 Rete 简单，工程维护成本低 | 规则冲突频繁的场景下，重复计算抵消了 Alpha 共享的优势 |
| Alpha 节点共享仍然保留，条件过滤并不重复 | 学术气息重，工业界几乎无成熟实现 |

**适用场景：** 内存非常受限的嵌入式设备；规则冲突频率很低（多数请求只命中 1-2 条规则）。

---

#### 4. 表达式规则引擎（Expression Engine）

**特点：** 每条规则就是一个字符串表达式（Aviator / MVEL / Groovy / SpEL），引擎逐个解释执行或编译执行。IRP 中 Seagull-web 的 Aviator 引擎即属此类。

```
// 规则就是一个表达式
rule_1: device_risk_score > 80 && amount > 5000 → reject
rule_2: ip_hit_count_24h > 10 && hour < 6 → manual_review
rule_3: user_credit_score < 400 → reject

// 执行：遍历所有规则，逐个 evaluate(expr, context)
```

| 优点 | 缺点 |
|------|------|
| 零编译开销：表达式当作字符串存储，直接执行或热编译 | 无规则间条件复用——N 条规则 = N 次 evaluate，CPU 线性增长 |
| 灵活度极高：表达式语法灵活，支持任意复杂逻辑组合 | 规则多（100+）时性能随规则数线性衰减，不如 Rete 的 O(1) 条件匹配 |
| 热更新天然支持：改表达式 = 改一行字符串，无需重建任何网络 | 表达式内数据类型错误要到运行时才能发现 |
| 业务人员可读：`amount > 5000` 比 Rete 的节点网络直观得多 | 缺乏冲突检测和交叉验证能力 |

**适用场景：** 规则数量 <50、规则逻辑频繁变更、灵活性优先于极致性能；AB 实验开关、动态阈值配置等简单条件控制；需要热更新且不想引入规则引擎重依赖的微服务。IRP 中 Owl 的 SwitchNode 条件判断和 Peregrine 的 AB 测试分流均用 Aviator。

---

#### 5. 决策树（Decision Tree）

**特点：** 二叉树或多叉树，每个内部节点是一个条件判断，叶子节点是决策结果。一次决策从根走到叶，路径即规则。

```
                amount > 10000?
                /            \
            YES              NO
            /                  \
    credit_score > 600?    amount > 5000?
       /        \            /        \
   reject    approve      reject    approve
```

| 优点 | 缺点 |
|------|------|
| 可解释性极强：每笔决策都能展示"走了哪条路径、为什么得出这个结论" | 条件深度大时树会指数级膨胀 |
| 天然支持 PMML，XGBoost/随机森林等 ML 模型可直接导出为决策树 | 不擅长处理离散条件组合（如 "A=1 and B=2" 这类交叉条件） |
| 不需要预编译，树结构即规则，加载即用 | 树一旦建好，修改单个节点条件可能影响所有子树 |
| 分类结果可附带概率（叶子节点的样本分布） | 条件之间有隐含优先级（靠近根的条件权重高），不太直观 |

**适用场景：** 条件之间存在天然层级关系（如先判断金额、再判断信用分）；ML 模型要导出为可解释规则——IRP 中 `XGBTreeAdapter` 就是把 XGBoost 树模型转换为决策树规则；需要监管合规解释的场景（如信贷审批结果的申诉回溯）。

---

#### 6. 决策表（Decision Table）

**特点：** 二维矩阵，行是规则，列是条件维度，交叉点做条件匹配。所有规则扁平排列，无层级关系。

```
| 规则 | 金额>10000 | 信用分<500 | 时间在0-6点 | 结果    |
|------|-----------|-----------|------------|---------|
| R1   | Y         | Y         | -          | reject  |
| R2   | Y         | N         | Y          | manual  |
| R3   | N         | -         | Y          | reject  |
| R4   | N         | -         | N          | approve |
```

| 优点 | 缺点 |
|------|------|
| 业务人员可直接在 Excel 中编辑和维护 | 条件维度多（5+）时组合爆炸——N 维 × M 取值 = N^M 行 |
| 条件覆盖一目了然，容易发现遗漏的组合 | 只适合离散条件，连续值（如金额、年龄）需要预先分箱 |
| 规则无优先级问题——有冲突时表格直观可见 | 条件之间有交互关系时（如 "A=Y时的权重取决于B"），表格难以表达 |

**适用场景：** 条件维度少（2-4 个）、取值离散的枚举型决策（如根据产品类型+客户等级+地区决定费率）；需要业务人员直接维护规则的场合。IRP Raptor 把决策表作为一种规则插件（`DecisionTableResourceBuilder`），展开为 Rete 规则后执行。

---

#### 7. 评分卡（Scorecard）

**特点：** 每个特征按不同取值区间给分，各特征分数加权求和，总分与阈值比较。线性模型，无交互项。

```
特征               取值区间        分数
credit_score       <400             -30
credit_score       400-600           +10
credit_score       >600              +40
age                <25               -15
age                25-50             +20
age                >50               +5
income             <5000             -20
income             5000-20000        +15
income             >20000            +35

总分 = Σ(各特征分 × 权重)
决策: total_score > 60 → approve
```

| 优点 | 缺点 |
|------|------|
| 极度可解释——每笔决策能展示各变量的贡献分，"为什么拒绝？因为信用分贡献只有 -30" | 只能做线性加权，无法表达条件组合（如 "信用低 AND 收入低" 的双重风险） |
| 生成速度极快——就是 N 个查表 + 加权求和 | 变量间无交互，现实中的非线性关系建模不出来 |
| 监管友好——金融监管机构（银保监）认可评分卡贷前审批模型 | 分箱边界敏感——连续值 599 和 601 可能分到不同箱，跳跃过大 |
| PMML 标准化，Logistic 回归评分卡可跨语言/平台加载 | 特征工程依赖人工分箱，不如树模型自动学习切分点 |

**适用场景：** 信贷审批、反欺诈评分等需要清晰解释每个变量贡献的场景；需要满足监管合规要求（如 GDPR 的 "解释权"）；IRP 中 Raptor 有 `ScorecardResourceBuilder` + `ComplexScorecardResourceBuilder`，Merlin 的 `LogisticRegressionScorecard` + `BinningTransformer` 可自动训练评分卡。

---

#### 8. 决策流（Decision Flow / Rule Flow）

**特点：** 不关心单个规则怎么匹配，而是定义"按什么顺序执行哪些规则组"。像工作流引擎——规则只是图中的节点，流决定了规则之间的调用关系、分支和聚合。

```
[数据预处理] → [黑名单检查] → hit? → YES → [拒绝]
                                    ↓ NO
                              [反欺诈评分] → score < 40? → YES → [通过]
                                    ↓ NO
                              [人工审核]
```

| 优点 | 缺点 |
|------|------|
| 规则间的关系（顺序、并行、条件分支）可视化强 | 本身不解决规则匹配效率问题——每个节点内通常还是用 Rete 或表达式引擎 |
| 支持子流程递归和局部回退——复杂的业务审批流天然适合 | 流太复杂时调度开销不可忽略 |
| 分段独立——某个决策节点失败不影响其他节点 | 调试流中的问题需要看全局上下文，比单规则调试更难 |
| 节点内可以混合不同引擎（Rete 做规则匹配、Aviator 做条件分支） | 流程变更需要审批——与业务耦合度高 |

**适用场景：** 需要严格按步骤执行的复杂审批流程；IRP 中 Owl 的 LiteFlow 即决策流编排（800+ 条链），Raptor 的规则流插件（`FlowResourceBuilder`）是流+规则的混合体；保险理赔、贷款审批等多步决策。

---

### 三、总览对比表

| 算法 | 核心思想 | 内存 | 编译开销 | 增量更新 | 大数据量 | 可解释性 | 灵活性 | 代表实现 |
|------|---------|------|---------|---------|---------|---------|--------|---------|
| **Rete** | Alpha/Beta 网络 + 条件共享 | 高 | 高 | 弱 | ★★★★★ | ★★ | ★★★ | Raptor(自研), Drools(旧版), Jess |
| **Phreak** | Rete + 懒惰求值 + 延迟执行 | 中 | 中 | 中 | ★★★★ | ★★ | ★★★ | Drools 6+ |
| **LEAPS** | 栈式懒惰求值，按需搜索 | 低 | 无 | 强 | ★★ | ★★ | ★★★★★ | 学术原型, OPSJ |
| **Treat** | Rete - Beta Memory | 中 | 中 | 弱 | ★★★ | ★★ | ★★★ | 无成熟工业实现 |
| **表达式引擎** | 逐条解释/编译执行 | 低 | 无/轻 | 强 | ★ | ★★★★ | ★★★★★ | Aviator, MVEL, Groovy |
| **决策树** | 树节点二分查找 | 低 | 无 | 中 | ★★★ | ★★★★★ | ★★ | XGBoost树, sklearn |
| **决策表** | 二维矩阵查表 | 低 | 无 | 强 | ★★★ | ★★★★★ | ★ | Excel 规则表 |
| **评分卡** | 分箱 + 线性加权 | 低 | 无 | 强 | ★★★★ | ★★★★★ | ★ | PMML Scorecard |
| **决策流** | DAG 编排 + 内置引擎 | 取决于节点引擎 | 取决于节点引擎 | 取决于节点引擎 | ★★★ | ★★★★ | ★★★★ | LiteFlow, Flowable |

### 四、选型决策树

```
规则数量 > 50 且有大量共享条件？
  ├── YES → 事实量是否 > 10000?
  │         ├── YES → Phreak（Drools）或 Rete + 流式分批
  │         └── NO → Rete
  └── NO → 条件是否有天然层级关系？
            ├── YES → 决策树
            └── NO → 条件维度 <5 且离散？
                      ├── YES → 决策表
                      └── NO → 需要线性可解释？
                                ├── YES → 评分卡
                                └── NO → 表达式引擎
```

**IRP 的实际情况：** Raptor用 Rete 做规则匹配（甜点区），Seagull-web 用 Janino/Aviator 做指标表达式计算（轻量灵活），Owl 用 LiteFlow 做决策流编排（混合引擎），三种场景三种算法，选型是合理的。

---

> 文档更新日期：2026-06-11
> 基于 IRP 系统代码分析 + 智能风控行业知识综合编写
