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

> 文档生成日期：2026-06-02
> 基于 IRP 系统代码分析 + 智能风控行业知识综合编写
