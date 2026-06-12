# 决策质量监控系统建设方案

## Context

IRP 系统目前有完善的数据采集管道（14个 RocketMQ Topic → 多个监控表），但完全缺失三层关键能力：
1. **实时指标聚合** — 数据在 MySQL 里，没人算
2. **可视化监控大盘** — 没有 Grafana，SkyWalking 只能看单次 trace
3. **异常告警** — 没有决策通过率突变、模型衰退等关键告警

此方案基于现有数据管道，设计一套完整的决策质量监控体系。

---

## 一、指标体系设计

### 1.1 决策效能指标（Decision Effectiveness）

| 指标 | 计算方式 | 时间窗口 | 告警阈值 |
|------|---------|---------|---------|
| 决策量（QPS） | COUNT(1) | 1min/5min/1h | 环比跌50% 或 涨200% |
| 通过率 | COUNT(result=通过) / 总量 | 5min | 环比变化 >10pp |
| 拒绝率 | COUNT(result=拒绝) / 总量 | 5min | 环比变化 >10pp |
| 人工审核率 | COUNT(result=人工审核) / 总量 | 5min | 突增 >20% |
| 空结果率 | COUNT(hitRules=空) / 总量 | 5min | >5%（规则全部miss） |
| 入站异常率 | COUNT(exception) / 总量 | 5min | >1% |

### 1.2 性能指标（Performance）

| 指标 | 计算方式 | 告警阈值 |
|------|---------|---------|
| P50/P90/P95/P99 延迟 | 按时间窗口分位值 | P99 > 3s 或 环比恶化50% |
| 各服务耗时占比 | Tamer%/Peregrine%/Owl%/Raptor%/外部API% | 外部API占比 >80% |
| 外部数据源调用成功率 | COUNT(success)/COUNT(total) per source | <95% |
| 外部数据源缓存命中率 | COUNT(hit=1)/COUNT(total) per source | <70%（成本暴增） |
| Raptor KnowledgeBase 缓存命中率 | caffeineCache.stats().hitRate() | <80%（冷编译发生） |

### 1.3 规则质量指标（Rule Quality）

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 每条规则的命中率 | COUNT(ruleHit) / 总决策量 | 发现僵尸规则（命中率 <1% 持续7天） |
| 规则命中数分布 | 直方图：每次决策命中几条规则 | 发现连坐（命中数过多）或空跑 |
| 开关节点流量分配 | GROUP BY toNode, COUNT(*) | AB测试分流是否均匀 |
| 规则命中稳定性 | 规则命中率的日环比变化 | 某规则突然失效或被绕过 |

### 1.4 模型质量指标（Model Quality，线上）

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| PSI（模型评分分布稳定性） | Σ(实际% - 预期%) × ln(实际%/预期%) | PSI > 0.25 → 模型衰退告警 |
| KS（线上样本区分度） | 有 label 数据时计算 | KS 在线下训练值 vs 线上值的偏离 |
| 模型分数分布 | 每日评分直方图 | 偏离训练基线即告警 |
| 模型调用量/占比 | 模型决策占总决策的比例 | 模型被绕过未使用 |

### 1.5 AB测试指标（A/B Test）

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 分流比例 | COUNT(A) / COUNT(B) | 偏离配置比例告警 |
| 各组通过率差异 | 实验组通过率 - 对照组通过率 | 统计显著性 |
| 各组延迟差异 | avg(P99_A) vs avg(P99_B) | 新策略是否引入性能退化 |
| 样本量累计 | 每组累计决策量 | 样本量不足无法判断显著性 |

### 1.6 外部数据源成本指标

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 各数据源每分钟调用量 | COUNT(1) GROUP BY source | 发现调用量异常暴增 |
| 各数据源日均费用 | SUM(price × callCount) | 成本账单 |
| 数据源响应延迟 | P90(responseTime) per source | 慢数据源拖垮全链路 |
| 缓存命中率趋势 | hitRate 日环比 | 缓存配置是否生效 |

---

## 二、数据管道方案

现有数据已通过 RocketMQ 采集，但缺少实时聚合层。有三种方案：

### 方案A：Flink 实时计算（推荐）

```
RocketMQ (risk-report-common-topic)
  → Flink Streaming Job (滑动窗口聚合)
    → ClickHouse/TDengine (时序指标存储)
      → Grafana (可视化)
      → AlertManager (告警)
```

- **优势**：毫秒-秒级实时，窗口聚合精确，状态管理成熟
- **成本**：需部署 Flink 集群 + ClickHouse 集群
- **适用**：决策链路核心指标（QPS、延迟、通过率）

### 方案B：定时任务 + MySQL 聚合（轻量）

```
Kestrel 零调度器模块 (新增定时任务)
  → 每分钟从监控表聚合数据
    → 写入专用指标表 (t_monitor_metrics)
      → Spring Boot Actuator + Micrometer 暴露 /actuator/metrics
        → Prometheus 拉取 → Grafana
```

- **优势**：零外部依赖，复用现有 Spring Boot 体系
- **劣势**：分钟级延迟，窗口计算不精确（跨分钟边界问题），高基数标签下性能差
- **适用**：日报/小时报级别的非实时指标；模型质量指标

### 方案C：混合方案（渐进式，推荐分阶段采用）

```
阶段一：方案B 快速落地（1-2周），让大盘先跑起来
阶段二：核心指标切到方案A (Flink)，非核心指标保持方案B
阶段三：接入告警引擎
```

---

## 三、存储方案

### 3.1 指标表设计（MySQL，方案B初期使用）

```sql
-- 指标定义表
CREATE TABLE t_monitor_metric_def (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    metric_code VARCHAR(64) NOT NULL COMMENT '指标编码: decision_qps',
    metric_name VARCHAR(128) COMMENT '指标名称: 决策量',
    metric_category VARCHAR(32) COMMENT '类别: effectiveness/performance/rule/model/abtest/cost',
    aggregation_type VARCHAR(16) COMMENT '聚合类型: count/sum/avg/p50/p90/p95/p99/rate',
    time_window VARCHAR(8) COMMENT '时间窗口: 1m/5m/1h/1d',
    dimension_keys VARCHAR(256) COMMENT '可用维度: tenantCode,strategyId,ruleCode,sourceId',
    unit VARCHAR(32) COMMENT '单位: qps/ms/percent',
    alert_threshold JSON COMMENT '告警阈值配置',
    enabled TINYINT DEFAULT 1,
    INDEX idx_category (metric_category)
);

-- 指标数据表（时序）
CREATE TABLE t_monitor_metric_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    metric_code VARCHAR(64) NOT NULL,
    time_bucket DATETIME(3) NOT NULL COMMENT '时间桶起始时间',
    time_window VARCHAR(8) COMMENT '聚合窗口: 1m/5m/1h/1d',
    dimensions JSON COMMENT '维度KV: {"tenantCode":"T001","strategyId":"1"}',
    value DOUBLE COMMENT '指标值',
    extra JSON COMMENT '扩展数据: {p90:xxx, p99:xxx}',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_time (metric_code, time_bucket),
    INDEX idx_dimension ((CAST(dimensions->>'$.tenantCode' AS CHAR(64))))
);

-- 告警事件表
CREATE TABLE t_monitor_alert_event (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    alert_code VARCHAR(64) NOT NULL COMMENT '告警编码',
    metric_code VARCHAR(64) NOT NULL COMMENT '关联指标',
    alert_level VARCHAR(16) COMMENT 'P0/P1/P2/P3',
    alert_title VARCHAR(256) COMMENT '告警标题',
    alert_detail TEXT COMMENT '告警详情JSON',
    current_value DOUBLE COMMENT '当前值',
    threshold_value DOUBLE COMMENT '阈值',
    status VARCHAR(16) COMMENT 'firing/resolved/suppressed',
    fire_time DATETIME COMMENT '触发时间',
    resolve_time DATETIME COMMENT '恢复时间',
    INDEX idx_alert_code (alert_code),
    INDEX idx_status (status)
);
```

### 3.2 时序数据库（方案A使用）

| 选项 | 优势 | 劣势 |
|------|------|------|
| **ClickHouse** | 批量写入极快，支持复杂聚合 SQL，列式压缩 | 运维复杂度高，需独立集群 |
| **TDengine** | 专为时序优化，超级表天然支持多维度，运维简单 | 生态不如 ClickHouse |
| **Prometheus TSDB** | 紧耦合 Grafana，告警内置 | 不适合长期存储，高基数标签性能差 |
| **VictoriaMetrics** | Prometheus 兼容 + 更高性能 + 更低资源 | 需额外运维 |

**推荐**：初期用 Prometheus（零额外运维），长期切 TDengine 或 ClickHouse。

---

## 四、可视化大盘（Grafana）

### 4.1 大盘分层

**L1 — 全局概览大盘（决策指挥中心）**

适用角色：风控总监、运营负责人
刷新频率：1分钟

```
┌─────────────────────────────────────────────────────────┐
│  决策总量（今日）：128,451  ↑12% vs 昨日               │
│  通过率：72.3%  ↓3.2pp  |  拒绝率：18.5%  |  人工：9.2% │
│  P99延迟：1,234ms  ↓200ms  |  成功率：99.87%            │
├──────────────────────────┬──────────────────────────────┤
│  决策量趋势（24h折线）     │  通过率趋势（24h折线）        │
│  - 当前值 + 基线±3σ       │  - AB两组各一根线             │
├──────────────────────────┼──────────────────────────────┤
│  拒绝原因 TOP5（条形图）   │  外部数据源调用量（24h堆叠）  │
│  - 规则1: 2,341           │  - 设备指纹 ████████ 45%     │
│  - 规则2: 1,892           │  - 征信查询 ████ 22%         │
│  - 规则3: 1,203           │  - IP风险库 ███ 15%          │
└──────────────────────────┴──────────────────────────────┘
```

**L2 — 策略详情大盘**

适用角色：策略分析师
按策略/规则分组展示，支持多策略横向对比

**L3 — 模型监控大盘**

适用角色：模型工程师
PSI趋势图、分数分布直方图、KS线上vs训练对比

**L4 — 技术性能大盘**

适用角色：SRE/后端工程师
各服务延迟瀑布图、外部API调用热力图、JVM GC监控

### 4.2 Grafana Panel 设计要点

- 所有折线图加**基线带**（过去7天均值 ± 2σ）
- P0级指标用**红色虚线**标注告警线
- 支持 `$tenantCode`、`$strategyId`、`$ruleCode` 等 Grafana 变量下钻
- 大屏自动轮播模式（每30秒切换到 L2/L3/L4）

---

## 五、告警体系

### 5.1 告警分级

| 级别 | 定义 | 响应要求 | 通知方式 | 示例 |
|------|------|---------|---------|------|
| **P0 — 致命** | 决策服务不可用、拒绝率 100%、成功率 < 90% | 5分钟内处理 | 电话 + 钉钉 + 短信 | 规则引擎全部返回 null |
| **P1 — 严重** | 核心指标严重偏离基线、外部数据源全部超时 | 15分钟内处理 | 钉钉 + 短信 | 通过率从70%跌到40% |
| **P2 — 警告** | 单项指标异常、模型PSI超标 | 1小时内关注 | 钉钉群 | 某规则命中率异常跳变 |
| **P3 — 提醒** | 趋势性变化、预设阈值逼近 | 当日关注 | 钉钉群/邮件 | 外部数据源成本逼近预算 |

### 5.2 告警规则设计

告警规则基于**动态基线**而非固定阈值：

```
当前值偏离基线 >3σ 且持续 >2个窗口 → 触发告警
动态基线 = 过去7天同一时间段（周同比）的均值
σ = 过去7天同期标准差

特殊规则:
  - 决策量 = 0 → 直接P0（服务挂了）
  - 成功率 < 90% → 直接P0
  - 拒绝率 = 100% → 直接P0（规则可能配置错误）
  - 空结果率 > 50% → 直接P1（所有规则miss，可能变量映射错了）
```

### 5.3 告警收敛

- 同一告警 5 分钟内不重复发送
- P0 告警持续 firing 时，每 15 分钟升级一次（钉钉→电话→值班经理）
- 同一根因的衍生告警合并为一条（如"决策量下降"引发的"通过率下降"合并不再单独发）

---

## 六、分阶段实施路线

### 阶段一：快速见效（Sprint 1-2，2周）

**目标**：大盘先亮起来，覆盖 L1 全局概览

1. **引入 Micrometer + Prometheus 依赖**
   - 各服务 pom.xml 加 `micrometer-registry-prometheus`
   - 每个服务暴露 `/actuator/prometheus`

2. **新增 kestrel `MonitorMetricService`**
   - 每分钟定时任务从 `t_zero_trade_strategy_monitor` 聚合：
     - 决策总量、通过率、拒绝率、异常率
     - P50/P90/P99 延迟
   - 写入 `t_monitor_metric_data`
   - 暴露为 Micrometer Gauge

3. **部署 Prometheus + Grafana（单机即可）**
   - Prometheus 拉取各服务 `/actuator/prometheus`
   - Grafana 导入 L1 大盘 JSON

4. **新增 `MonitorMetricController`**
   - `GET /api/monitor/metrics/latest?metricCode=decision_qps`
   - 供前端直接查询当前指标值

**产出**：1 个全局大盘 + 7个核心指标 + 基础告警（钉钉 webhook）

### 阶段二：业务纵深（Sprint 3-4，2周）

**目标**：细化到规则级别 + 模型监控

1. **规则命中率指标**
   - 从 `t_zero_trade_strategy_hit_rule` 按 ruleDetailCode 聚合
   - 新增僵尸规则检测（7天命中率 <1% 自动标记）

2. **模型 PSI 监控**
   - 新增 `ModelMonitorService` 定时计算
   - 从 `t_zero_trade_strategy_monitor` 读取模型分数字段
   - 比较线上分数分布 vs 训练集基线（基线从 Merlin 模型报告 JSON 提取）
   - PSI > 0.25 触发 P2 告警

3. **外部数据源成本监控**
   - 从 `t_zero_data_service_pub_call_record` 聚合
   - 按数据源维度展示调用量/成功率/命中率/延迟
   - 新增费用预估（dataSource × unitPrice × callCount）

4. **L2/L3/L4 大盘**

**产出**：4 个层级大盘全覆盖 + 模型衰退告警 + 成本报表

### 阶段三：实时化 + 智能化（Sprint 5-6，2周）

**目标**：核心指标秒级实时 + 动态基线 + AB测试统计显著性

1. **Flink 实时计算接入**
   - Flink 消费 `risk-report-common-topic`
   - 5秒滑动窗口计算 QPS、延迟分位值、通过率
   - 写入 ClickHouse/TDengine

2. **动态基线**
   - 7天周同比基线自动计算
   - 异常检测从固定阈值切换为 3σ 动态基线

3. **AB 测试统计显著性**
   - 卡方检验判断两组通过率差异是否显著
   - 样本量不足时提示"需继续采集"

4. **告警收敛 + 值班轮转**
   - AlertManager 配置告警路由规则
   - 接入值班表 API（如 PagerDuty / 钉钉排班）

**产出**：秒级实时大盘 + 智能告警 + AB测试显著性

---

## 七、需要新增的代码模块

### 7.1 kestrel 新增模块

```
kestrel/
├── kestrel-monitor/           ← 新增模块
│   ├── pom.xml
│   └── src/main/java/tech/kestrel/monitor/
│       ├── config/
│       │   └── MonitorConfig.java            ← 线程池、Micrometer注册
│       ├── scheduler/
│       │   ├── MetricAggregationScheduler.java ← 定时聚合任务（每分钟）
│       │   ├── ModelPsiScheduler.java          ← 模型PSI计算（每小时）
│       │   └── RuleQualityScheduler.java       ← 规则质量检测（每天）
│       ├── service/
│       │   ├── MonitorMetricService.java       ← 指标计算核心
│       │   ├── ModelMonitorService.java        ← 模型监控
│       │   ├── AlertService.java               ← 告警判断+发送
│       │   └── BaselineService.java            ← 动态基线计算
│       ├── domain/
│       │   ├── MetricDefinition.java           ← 指标定义实体
│       │   ├── MetricDataPoint.java            ← 指标数据点
│       │   └── AlertEvent.java                 ← 告警事件
│       └── controller/
│           ├── MonitorMetricController.java    ← 指标查询API
│           └── MonitorAlertController.java     ← 告警查询/处理API
```

### 7.2 各服务 pom.xml 改动

每个服务添加：
```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

### 7.3 各服务暴露关键业务指标

| 服务 | 暴露指标 |
|------|---------|
| **Raptor** | `raptor_kb_cache_hit_rate`, `raptor_kb_compile_count`, `raptor_rule_fire_count` |
| **Owl-execution** | `owl_flow_execute_count`, `owl_data_source_call_count`, `owl_data_source_call_latency` |
| **Peregrine** | `peregrine_inbound_count`, `peregrine_strategy_match_count` |
| **Seagull-web** | `seagull_var_execute_count`, `seagull_var_execute_latency`, `seagull_janino_compile_count` |

---

## 八、基础设施需求

| 组件 | 阶段一（最小） | 阶段三（完整） | 备注 |
|------|-------------|-------------|------|
| Prometheus | 1台 2C4G，本地磁盘 100G | 2台 HA | 数据保留15天 |
| Grafana | 复用 Prometheus 机器 | 独立 1台 2C4G | 或使用公司已有 Grafana |
| AlertManager | 复用 Prometheus 机器 | 独立部署 | 告警去重+路由 |
| ClickHouse | 不需要 | 3节点 4C8G 500G SSD | 阶段二可先不用 |
| Flink | 不需要 | 2 JM + 3 TM 4C8G | 阶段二可先用定时任务 |

---

## 九、验证方案

### 阶段一验证
1. `curl http://kestrel:port/actuator/prometheus` 能看到自定义指标
2. Grafana 大盘出现数字（即使只有定时计算的分钟级数据）
3. 手动把某个策略拒绝率设为100%，钉钉收到告警

### 阶段二验证
1. Grafana L1-L4 四个大盘均可切换查看
2. 压测期间大盘实时反映 QPS 和延迟变化（Q26 压测报告可做对比基准）
3. 僵尸规则检测能发现命中率为0的规则

### 阶段三验证
1. Flink 计算的 QPS 与定时任务计算的 QPS 误差 <5%
2. PSI > 0.25 触发告警
3. AB测试统计显著性计算与在线计算器结果一致

---

## 十、不做的事情

- **不替换 SkyWalking**：SkyWalking 继续负责分布式链路追踪，监控系统负责业务指标聚合，两者互补
- **不在阶段一走 Flink 全量方案**：投入太大，先用定时任务验证指标体系是否正确
- **不做用户行为分析**：如"用户在审批页面停留多久"，属于产品分析范畴
- **不做实时 OLAP 查询**：不对原始明细数据做即席聚合查询，全部走预聚合
