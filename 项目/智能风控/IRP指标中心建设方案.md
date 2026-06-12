# IRP 指标中心（Feature Store）建设方案

## Context

IRP 当前的指标/变量体系是分散的——Seagull-web 管 derive 变量，Raptor 管决策变量，Peregrine 管策略变量，外部数据源散落在 Owl-execution 的 `t_ds_service_calll_result` 里。没有一个统一的"指标"概念：谁定义了这个指标、它依赖哪些数据源、它的计算逻辑是什么版本、它现在的数据质量怎么样——这些信息需要跨多个服务才能拼凑出来。

对内公司内部场景，一般有大量部门定义各自的指标体系，指标间相互依赖衍生，部分在线计算、部分离线跑批。这本质上就是业内所谓的 **Feature Store（特征平台）**。

---

## 一、什么是 Feature Store

Feature Store 不是一个新的存储系统，而是一个**管理特征的平台层**，它统一解决了四个问题：

| 问题 | 没有 Feature Store | 有 Feature Store |
|------|-------------------|-----------------|
| 特征在哪？ | 散落在各个服务的代码/DB/缓存里，需要翻代码才知道 | 特征注册在一张表里，metadata 可检索 |
| 在线怎么取？ | 每个服务自己写查询逻辑、做缓存 | 统一的 Online Serving API，SDK 一行调用 |
| 离线怎么算？ | 数据分析师手写 SQL，模型工程师手写 Python，各算各的 | 统一的 Offline SDK，注册一次逻辑，在线离线同源 |
| 特征变了对模型有什么影响？ | 不知道，上线后发现模型效果变了才排查 | Feature Lineage 追溯 + 分布监控自动检测漂移 |

**Feature Store 不是替代 Seagull-web 或 Raptor 变量库**，而是在它们之上加了一层抽象——把"变量"升级为"可治理的特征资产"。

---

## 二、核心概念：一条特征的完整画像

```
特征: user_24h_transaction_count
│
├─ 定义元数据
│   ├─ name: user_24h_transaction_count
│   ├─ display_name: 用户近24小时交易笔数
│   ├─ description: 统计用户在过去24小时内的成功交易总笔数
│   ├─ domain: risk_control / anti_fraud
│   ├─ owner_team: 风控策略组
│   ├─ owner_email: antifraud@company.com
│   └─ tags: [风控, 反欺诈, 实时, 交易]
│
├─ 计算定义
│   ├─ feature_type: window_aggregate
│   ├─ source: kafka.trade_events
│   ├─ aggregation: COUNT(*)
│   ├─ window: 24h sliding
│   ├─ group_by: [user_id]
│   ├─ filter: status = 'SUCCESS'
│   └─ freshness_sla: 1min
│
├─ 存储
│   ├─ online_store: Redis, key=ft:user_24h_txn:{user_id}, TTL=48h
│   ├─ offline_store: Hive, table=dwd.ft_user_24h_txn, partition=dt
│   └─ entity: user_id (关联的实体键)
│
├─ 版本
│   ├─ v1.0 (2025-03-01): 初始版本，统计所有交易
│   ├─ v1.1 (2025-06-15): 排除冲正交易，filter加上 status != 'REVERSED'
│   └─ v1.2 (current): 当前版本
│
├─ 血缘
│   ├─ 上游数据源: kafka.topic.trade_events (MySQL binlog → Kafka CDC)
│   ├─ 依赖特征: 无
│   └─ 下游消费者:
│       ├─ 规则: rule_fraud_detection (Raptor)
│       ├─ 模型: model_xgboost_risk_v3 (algo-service)
│       └─ 报表: daily_risk_report
│
└─ 质量
    ├─ 数据量: 日均 500万条，覆盖率 99.2%
    ├─ 空值率: 0.8% (新用户无历史交易)
    ├─ 分布: median=3.2, p99=47, max=892
    ├─ 新鲜度: p99延迟 1.2s
    └─ 漂移检测: PSI vs 7天前 = 0.08 (正常)
```

---

## 三、整体架构

```
                              ┌─────────────────────────────────┐
                              │       Feature Registry            │
                              │  (MySQL/PostgreSQL, 元数据中心)    │
                              │  - 特征定义、版本、血缘、owner      │
                              └──────────────┬──────────────────┘
                                             │ 统一元数据
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
        │   Online Serving     │ │   Offline Compute   │ │   Nearline Compute  │
        │   (在线服务层)        │ │   (离线计算层)       │ │   (准实时计算层)     │
        ├─────────────────────┤ ├─────────────────────┤ ├─────────────────────┤
        │ 延迟: <10ms          │ │ 延迟: 小时/天级      │ │ 延迟: 秒级           │
        │ 场景: 实时决策        │ │ 场景: 模型训练/回溯   │ │ 场景: 滑动窗口聚合    │
        │                      │ │                      │ │                      │
        │ ┌─────────────────┐  │ │ ┌─────────────────┐  │ │ ┌─────────────────┐  │
        │ │Feature Serving  │  │ │ │Spark/Flink ETL  │  │ │ │Flink Streaming  │  │
        │ │   API (REST)    │  │ │ │  (T+1 批量)      │  │ │ │  (滑动窗口)      │  │
        │ └────────┬────────┘  │ │ └────────┬────────┘  │ │ └────────┬────────┘  │
        │          │           │ │          │           │ │          │           │
        │ ┌────────▼────────┐  │ │ ┌────────▼────────┐  │ │ ┌────────▼────────┐  │
        │ │  Online Store   │  │ │ │  Offline Store  │  │ │ │  Nearline Store │  │
        │ │  Redis/HBase    │  │ │ │  Hive/Iceberg   │  │ │ │  Kafka + Redis  │  │
        │ │  热点特征缓存    │  │ │ │  全量历史快照    │  │ │ │  窗口状态存储    │  │
        │ └─────────────────┘  │ │ └─────────────────┘  │ │ └─────────────────┘  │
        └─────────────────────┘ └─────────────────────┘ └─────────────────────┘
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Feature Quality │
                                    │  & Monitoring    │
                                    ├─────────────────┤
                                    │  - 分布漂移(PSI) │
                                    │  - 新鲜度SLA     │
                                    │  - 覆盖率/空值率 │
                                    │  - 异常告警       │
                                    └─────────────────┘
```

---

## 四、Feature Registry（特征注册中心）

Feature Registry 是所有特征元数据的唯一真相源（Single Source of Truth），不是特征值本身，而是"特征的定义"。

### 4.1 核心表结构

```sql
-- 特征定义主表
CREATE TABLE t_feature_def (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    feature_code VARCHAR(128) NOT NULL UNIQUE COMMENT '特征编码: user_24h_txn_count',
    feature_name VARCHAR(256) NOT NULL COMMENT '特征中文名',
    feature_type VARCHAR(32) NOT NULL COMMENT '特征类型: atomic/derived/window_aggregate/external/ml_prediction',
    entity_type VARCHAR(64) NOT NULL COMMENT '关联实体: user/device/merchant/order',
    entity_key_field VARCHAR(64) NOT NULL COMMENT '实体键字段: user_id/device_id',

    -- 计算定义
    computation_config JSON NOT NULL COMMENT '计算配置JSON，按feature_type不同结构不同',
    computation_engine VARCHAR(32) COMMENT '计算引擎: sql/flink/aviator/python/spark',

    -- 存储配置
    online_store_type VARCHAR(32) COMMENT '在线存储类型: redis/hbase/none',
    online_store_config JSON COMMENT '在线存储配置: {key_pattern, ttl, cluster}',
    offline_store_type VARCHAR(32) COMMENT '离线存储类型: hive/clickhouse/none',
    offline_store_config JSON COMMENT '离线存储配置: {table, partition_col, format}',

    -- 质量SLA
    freshness_sla_seconds INT COMMENT '新鲜度SLA(秒): 60=1分钟, 3600=1小时, 86400=1天',
    coverage_threshold DECIMAL(5,4) COMMENT '覆盖率阈值: 0.95=95%',
    null_rate_threshold DECIMAL(5,4) COMMENT '空值率阈值: 0.05=5%',

    -- 治理
    domain VARCHAR(64) COMMENT '业务域: risk_control/marketing/credit/operations',
    owner_team VARCHAR(128) COMMENT '负责团队',
    owner_email VARCHAR(256) COMMENT '负责人邮箱',
    sensitivity_level VARCHAR(16) COMMENT '敏感等级: public/internal/confidential/restricted',
    lifecycle_status VARCHAR(16) DEFAULT 'draft' COMMENT '生命周期: draft/testing/production/deprecated/archived',
    deprecation_date DATE COMMENT '计划废弃日期',

    -- 审计
    version INT DEFAULT 1 COMMENT '当前版本号',
    created_by VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_domain (domain),
    INDEX idx_entity (entity_type),
    INDEX idx_lifecycle (lifecycle_status),
    INDEX idx_owner (owner_team)
);

-- 特征版本历史表（不可变，append only）
CREATE TABLE t_feature_version (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    feature_code VARCHAR(128) NOT NULL,
    version INT NOT NULL,
    computation_config JSON NOT NULL COMMENT '该版本的完整计算配置快照',
    change_description TEXT COMMENT '变更说明: 排除冲正交易',
    change_type VARCHAR(32) COMMENT '变更类型: config_change/logic_change/rollback',
    created_by VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_feature_version (feature_code, version)
);

-- 特征数据源绑定表
CREATE TABLE t_feature_source (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    feature_code VARCHAR(128) NOT NULL,
    source_type VARCHAR(32) NOT NULL COMMENT '数据源类型: kafka/mysql/hive/external_api/hbase',
    source_identifier VARCHAR(512) NOT NULL COMMENT '数据源标识: kafka.topic.xxx / mysql.db.table / http://api.xxx',
    source_config JSON COMMENT '连接配置: {bootstrap_servers, auth, timeout}',
    is_primary TINYINT DEFAULT 1 COMMENT '是否主数据源',
    INDEX idx_feature (feature_code)
);

-- 特征血缘关系表（DAG 边）
CREATE TABLE t_feature_lineage (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    upstream_feature_code VARCHAR(128) COMMENT '上游特征（被依赖方），NULL表示原始数据源',
    upstream_source_id BIGINT COMMENT '上游数据源ID（非特征依赖时使用）',
    downstream_feature_code VARCHAR(128) NOT NULL COMMENT '下游特征（依赖方）',
    dependency_type VARCHAR(32) COMMENT '依赖类型: direct_transform/join/aggregate/filter',
    INDEX idx_upstream (upstream_feature_code),
    INDEX idx_downstream (downstream_feature_code)
);

-- 特征标签/分类
CREATE TABLE t_feature_domain (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    domain_code VARCHAR(64) NOT NULL UNIQUE,
    domain_name VARCHAR(128) COMMENT '业务域名称',
    parent_domain_code VARCHAR(64) COMMENT '父域，支持多级分类',
    description TEXT,
    INDEX idx_parent (parent_domain_code)
);
```

### 4.2 computation_config 的设计

`computation_config` 是一个 JSON 字段，不同类型的特征有不同的结构：

```json
// 类型1: atomic (原子特征——直接从数据源提取)
{
  "type": "atomic",
  "source_ref": "mysql.user_profile",
  "extract_sql": "SELECT credit_score FROM user_profile WHERE user_id = :user_id",
  "field": "credit_score",
  "default_value": null
}

// 类型2: derived (衍生特征——基于其他特征计算)
{
  "type": "derived",
  "expression": "total_debt / monthly_income",
  "dependencies": ["user_total_debt", "user_monthly_income"],
  "default_value": 0.0
}

// 类型3: window_aggregate (窗口聚合——时间窗口内统计)
{
  "type": "window_aggregate",
  "source_ref": "kafka.trade_events",
  "aggregation": "COUNT(*)",
  "window": {"size": 24, "unit": "hour", "type": "sliding", "slide": 60},
  "group_by": ["user_id"],
  "filter": "status = 'SUCCESS'",
  "watermark": "event_time - INTERVAL 5 MINUTE"
}

// 类型4: external (外部数据源——第三方API)
{
  "type": "external",
  "api_endpoint": "https://device-fingerprint.api/score",
  "request_template": "{\"device_id\": \"${device_id}\", \"timestamp\": \"${now}\"}",
  "response_path": "$.data.risk_score",
  "cache_ttl_seconds": 3600,
  "timeout_ms": 3000,
  "fallback_value": -1
}

// 类型5: ml_prediction (ML模型预测——模型作为特征)
{
  "type": "ml_prediction",
  "model_code": "model_xgboost_risk_v3",
  "model_version": "v3.2",
  "feature_vector": ["user_24h_txn_count", "user_credit_score", "device_risk_score"],
  "pmml_uri": "oss://models/xgboost_risk_v3.2.pmml"
}
```

---

## 五、Online Serving（在线服务层）

这是整个 Feature Store 中延迟要求最严苛的部分——风控决策场景要求单个特征获取 <10ms。

### 5.1 Online Store 的分层设计

```
决策请求到达
  │
  ▼
┌──────────────────────────────────────────────────┐
│          Feature Serving API (REST/gRPC)           │
│  POST /api/v1/features/batch                       │
│  {                                                 │
│    "entity_type": "user",                          │
│    "entity_ids": ["U001", "U002"],                 │
│    "feature_codes": ["user_credit_score",          │
│                      "user_24h_txn_count",          │
│                      "device_risk_score"]           │
│  }                                                 │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│              Feature Router (路由层)               │
│  根据 feature_code → 查 Registry 确定去哪取        │
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ L1 Cache │  │ L2 Cache │  │ Compute  │         │
│  │ Caffeine │  │  Redis   │  │ On-Demand│         │
│  │ (JVM堆内)│  │(分布式KV) │  │ (实时计算)│         │
│  └──────────┘  └──────────┘  └──────────┘         │
└──────────────────────────────────────────────────┘
```

### 5.2 三种特征获取路径

| 场景 | 路径 | 延迟 | 适用特征 |
|------|------|------|---------|
| **纯缓存** | 特征已预计算在 Redis 中 → 直接返回 | <1ms | 离线预计算的用户画像特征 |
| **缓存+计算** | 基值在 Redis + 实时增量在 Flink state → 合并返回 | <5ms | 滑动窗口特征（如24h交易笔数） |
| **纯计算** | 触发时实时调外部 API 或运行表达式 | 10-500ms | 外部数据源、复杂衍生特征 |

### 5.3 Feature Serving API 设计

```java
// 批量获取（最常见场景：一次决策需要N个特征）
POST /api/v1/features/batch
Request: {
  "entity_type": "user",
  "entity_ids": ["U12345"],
  "feature_codes": ["user_credit_score", "user_24h_txn_count", "device_risk_score"],
  "context": {                              // 可选：用于实时计算特征的上下文
    "transaction_amount": 15000,
    "device_id": "D67890",
    "ip_address": "10.0.0.1"
  }
}
Response: {
  "features": {
    "U12345": {
      "user_credit_score": 680,
      "user_24h_txn_count": 12,
      "device_risk_score": 85
    }
  },
  "meta": {
    "fetch_time_ms": 3.2,
    "cache_hit_rate": 0.67,
    "computed_on_demand": ["device_risk_score"]
  }
}

// Point-in-time 查询（模型训练场景：获取历史某时刻的特征值）
POST /api/v1/features/point-in-time
Request: {
  "entity_type": "user",
  "entity_ids": ["U12345"],
  "feature_codes": ["user_credit_score"],
  "timestamp": "2025-06-01T12:00:00Z"       // 关键：历史时间点
}
```

### 5.4 在线特征注册流程

```
1. 用户在 Registry UI 注册新特征
2. 指定 computation_config
3. 系统发布到 Online Store + Offline Store 的写入管道
   ├─ 在线: 注册 Redis key pattern
   ├─ 准实时: 注册 Flink job
   └─ 离线: 注册 Spark ETL task
4. 如果 computation_config 中有 dependencies → 自动构建血缘 DAG
5. 特征数据开始写入
6. 下游消费者可通过 API 或 SDK 获取
```

---

## 六、Offline Compute（离线计算层）

离线层负责三件事：**模型训练数据生成**（Point-in-time Join）、**历史数据回填**（Backfill）、**周期性批量跑批**。

### 6.1 Point-in-time Correct Join（最难的问题）

假设你要训练一个风控模型，训练数据的 label 是"用户在 2025-03-15 的这笔交易是否欺诈"。当时用户近24小时交易笔数应该是"截至 2025-03-15 那一刻的前24小时统计"，而不是"现在的近24小时交易笔数"。如果用现在的特征值去训练，就会产生 **training-serving skew**。

```
错误做法（数据泄漏）:
  训练数据: user_id=U001, label=欺诈, feature(24h_txn_count)=当前值(15笔)
  → 但2025年3月15日那天这个用户可能只有3笔交易
  → 模型学到的是未来的信息，上线后效果大幅下降

正确做法（Point-in-time Join）:
  训练数据: user_id=U001, label=欺诈, timestamp=2025-03-15T14:23:00
  → 去 Offline Store 查 user_24h_txn_count 在 2025-03-15T14:23:00 时刻的快照
  → 或者从原始事件表重新计算
```

**实现方案：**

```sql
-- 方案1: Offline Store 按日分区存储每日快照
-- 特征 user_24h_txn_count 每天凌晨生成一份全量快照
-- 训练时取 label_timestamp 之前最近的一个快照

SELECT
    t.user_id,
    t.transaction_amount,
    t.label,
    f.user_24h_txn_count AS feature_value,
    f.snapshot_date
FROM training_labels t
LEFT JOIN dwd.ft_user_24h_txn f
    ON t.user_id = f.user_id
    AND f.snapshot_date = (
        SELECT MAX(snapshot_date)
        FROM dwd.ft_user_24h_txn
        WHERE user_id = t.user_id
          AND snapshot_date <= DATE(t.label_timestamp)
    );

-- 方案2: 使用 Iceberg/Delta Lake 的时间旅行（Time Travel）
SELECT * FROM dwd.ft_user_24h_txn
FOR SYSTEM_TIME AS OF '2025-03-15 14:23:00';
```

### 6.2 离线特征生成管道

```
┌─────────────────────────────────────────────────┐
│              Offline Feature Pipeline             │
│                                                  │
│  数据源层                                        │
│  ├─ MySQL binlog (CDC → Kafka → Hive ODS层)      │
│  ├─ 业务埋点日志 (Flume → HDFS)                  │
│  └─ 外部数据 (API → Kafka → Hive)                │
│              │                                   │
│              ▼                                   │
│  ODS 层 (原始数据，Hive external table)           │
│              │                                   │
│              ▼                                   │
│  DWD 层                                           │
│  ├─ Spark ETL (T+1): 清洗/去重/关联/标准化       │
│  └─ Spark Feature Engineering:                   │
│       ├─ 原子特征: 直接 SELECT 字段              │
│       ├─ 衍生特征: Spark SQL 表达式              │
│       ├─ 窗口特征: Spark SQL window functions    │
│       └─ 外部特征: 批量调API并缓存               │
│              │                                   │
│              ▼                                   │
│  Feature Table (特征宽表，Hive/Iceberg)           │
│  ├─ 按日期分区 (dt=yyyy-MM-dd)                   │
│  ├─ entity_type + entity_id + dt 做主键          │
│  ├─ 可选: 列式存储 (Parquet/ORC + Snappy)        │
│  └─ 每天凌晨全量/增量更新                         │
│              │                                   │
│              ▼                                   │
│  同步到 Online Store: Spark → Redis Pipeline      │
│  (只同步当前最新快照，不推送历史数据)             │
└─────────────────────────────────────────────────┘
```

### 6.3 回填（Backfill）机制

当新增一个特征或修改了计算逻辑后，需要对历史数据进行回填：

```java
// 回填任务定义
{
  "feature_code": "user_24h_txn_count",
  "backfill_type": "full",             // full=全量, incremental=增量, logic_change=逻辑变更
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-06-30"
  },
  "engine": "spark",
  "parallelism": 20,
  "estimated_records": 500_000_000,     // 预估数据量，用于资源规划
  "retry_on_failure": true,
  "max_retries": 3
}

// 回填执行流程
POST /api/v1/features/{featureCode}/backfill
→ 创建回填任务记录
→ Spark job 按天分区并行跑
→ 每天跑完校验数据量是否合理（vs 前一天数据量 ±30% 告警）
→ 全部完成后自动更新 feature_version
→ 发布到 Online Store
```

---

## 七、Feature Quality & Monitoring（特征质量监控）

### 7.1 监控指标

不同于第五章的决策质量监控大盘，这里是**特征级别的质量监控**——关注的是"这个特征本身数据对不对"，而不是"用了这个特征后决策好不好"。

| 维度 | 指标 | 计算方式 | 告警条件 |
|------|------|---------|---------|
| **覆盖率** | 该特征非空值的比例 | COUNT(val IS NOT NULL)/COUNT(*) | < coverage_threshold |
| **新鲜度** | 特征值的时效性 | NOW() - MAX(update_time) | > freshness_sla_seconds × 2 |
| **分布漂移** | PSI (Population Stability Index) | 当前分布 vs 7天前基线 | PSI > 0.25 (显著漂移) |
| **数据量** | 每日特征产出量 | COUNT(*) per day | 环比变化 >50% |
| **值范围** | 最大值/最小值/均值/标准差 | 按日聚合 | 超出自定义范围 |
| **类别分布** | 枚举特征的类别占比 | GROUP BY category | 新类别出现或类别消失 |

### 7.2 分布漂移检测

```
基线: 取过去 7 天每天的特征值分布，按分箱统计占比
当前: 今天的分布

PSI = Σ(actual_i - expected_i) × ln(actual_i / expected_i)

PSI < 0.1: 正常
PSI 0.1-0.25: 轻微漂移，需要关注
PSI > 0.25: 显著漂移，依赖此特征的模型可能受影响 → P1 告警

示例:
特征 user_credit_score 的分布:
分箱       基线(7天均值)   今日      PSI贡献
[0-300]    5.2%          14.8%     +0.103
[300-600]  35.1%         32.3%     +0.002
[600-700]  42.3%         38.5%     +0.003
[700-850]  17.4%         14.4%     +0.005
─────────────────────────────────────────
总PSI = 0.113 → 轻微漂移 (可能上游征信数据源切换了)
```

### 7.3 质量表结构

```sql
CREATE TABLE t_feature_quality_snapshot (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    feature_code VARCHAR(128) NOT NULL,
    snapshot_date DATE NOT NULL,
    -- 分布统计
    distribution_stats JSON COMMENT '分箱分布: [{bin, count, rate}]',
    psi_vs_baseline DECIMAL(8,4) COMMENT 'vs 7天基线的PSI',
    -- 基本统计
    total_count BIGINT COMMENT '总记录数',
    null_count BIGINT COMMENT '空值数',
    null_rate DECIMAL(8,6) COMMENT '空值率',
    zero_count BIGINT COMMENT '零值数',
    -- 数值统计 (数值型特征)
    min_val DOUBLE,
    max_val DOUBLE,
    mean_val DOUBLE,
    stddev_val DOUBLE,
    p50_val DOUBLE,
    p95_val DOUBLE,
    p99_val DOUBLE,
    -- 类别统计 (分类型特征)
    category_distribution JSON COMMENT '类别分布: {category: count}',
    new_categories JSON COMMENT '新出现的类别',
    disappeared_categories JSON COMMENT '消失的类别',
    -- 新鲜度
    freshness_p50_seconds INT COMMENT '中位延迟',
    freshness_p99_seconds INT COMMENT 'P99延迟',
    data_ready_time DATETIME COMMENT '当日数据就绪时间',
    -- 质量标记
    quality_level VARCHAR(16) COMMENT '质量等级: good/warning/bad',
    issue_flags JSON COMMENT '问题标记: [high_null_rate, psi_drift, data_delay]',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_feature_date (feature_code, snapshot_date)
);
```

---

## 八、Feature Lineage（特征血缘）

### 8.1 血缘的层次

当一条特征出问题时（比如 user_credit_score 突然全是 null），需要快速回答：
- **上游追溯**：这个特征依赖了哪些数据源/特征？问题出在第几层？
- **下游影响**：哪些规则/模型/报表依赖了这个特征？影响范围多大？

```
                    MySQL.user_profile              外部征信API
                         │                              │
                         ▼                              ▼
                    user_basic_info              ext_credit_score
                    (原子特征)                    (外部特征)
                         │                              │
                         └──────────┬───────────────────┘
                                    │
                                    ▼
                            user_credit_score
                            (衍生特征: coalesce(user_basic_info.credit_score,
                                                 ext_credit_score, 600))
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            rule_high_risk    model_xgboost    daily_report
            (Raptor规则)      (ML模型)          (日报)
```

### 8.2 血缘自动构建

```
当用户在 Registry 创建/修改特征时:
  1. 解析 computation_config
  2. 提取 dependencies 列表
  3. 在 t_feature_lineage 中创建边
  4. 检查是否存在循环依赖 (DFS)
  5. 版本变更时自动记录新旧血缘差异

当用户要废弃一个特征时:
  1. 查询 t_feature_lineage 中所有 downstream 特征
  2. 标记 impact_analysis → 通知所有下游 owner
  3. 提供替代特征建议
```

---

## 九、与 IRP 当前架构的对照关系

| Feature Store 组件 | IRP 当前对应 | 差距 | 优先级 |
|-------------------|-------------|------|--------|
| Feature Registry | 无。特征定义散落在 `t_vc_var_base_def`(Seagull)、`t_rule_details`(Raptor)、Peregrine 策略变量表中 | 需要统一注册中心，含版本、owner、血缘 | P0 |
| Online Serving API | `QueryDataService.varQuery()` 通过 graphNodeCode 批量查询；每个服务自己封装外部API调用 | 缺失统一的 point-in-time API 和实体键查询 | P0 |
| Online Store | Redis（变量缓存 3天TTL）、Caffeine（Janino编译缓存 15天）、Guava（VarDomainCache 200条 5天） | 缓存层次不统一，无特征级别的 TTL/一致性管理 | P1 |
| Offline Compute | 无标准化管道。变量回溯(baffle)是离线的但只做回放不做聚合 | 缺失批量特征生成和 point-in-time join | P1 |
| Feature Quality | 无 | 完全缺失 | P2 |
| Feature Lineage | 无，只有 VarDomain↔VcVarBaseDef↔FlowNode 的隐式关联 | 需要显式构建血缘 DAG | P2 |
| Feature Engineering DSL | Seagull-web 的 Aviator/Janino/Python 三引擎 | 已有基础，需抽象为统一的 computation_config | P1 |

---

## 十、建设路线

### 阶段一：统一注册中心（Sprint 1-3，3周）

**目标**：把所有现有的"变量/指标"统一收拢到一个 Registry 里，先治理后建设。

- 建立 `t_feature_def` + `t_feature_version` 核心表
- 迁移现有数据：Seagull `t_vc_var_base_def` → Feature Registry（至少迁移 varName、varContent、varLang、graphNodeCode 映射）
- 迁移 Raptor 变量库中策略变量 + Peregrine 策略变量
- 提供 Web UI：特征列表、搜索、查看详情、版本历史

**产出**：一个集中式的特征目录，能查到"系统里一共有多少特征、分别是谁负责的"

### 阶段二：统一 Online Serving（Sprint 4-6，3周）

**目标**：统一所有在线特征的获取入口，不再各自写查询逻辑。

- 实现 `POST /api/v1/features/batch` 统一 API
- Feature Router：根据 computation_config 路由到 Redis/外部API/实时计算
- 集成现有 Seagull-web 执行引擎（Aviator/Janino/Python 复用）
- 在 Peregrine/Raptor 决策链路中切入 Feature Serving API（替代直连 Seagull-web）

**产出**：一次 API 调用获取所有需要的特征

### 阶段三：离线管道（Sprint 7-9，3周）

**目标**：建模和回溯不再手写 SQL 到处取数。

- Spark ETL 管道：每日自动生成特征宽表 → Hive
- Point-in-time Join SDK：训练数据生成一步到位
- 回填机制：支持全量回填和增量更新
- 同步管道：离线计算结果 → Redis Online Store（只同步最新快照）

**产出**：模型工程师可以用 SDK 一行代码生成训练特征

### 阶段四：质量+血缘（Sprint 10-11，2周）

**目标**：特征出问题能自动发现、能追溯根因。

- 每日特征质量快照
- PSI 分布漂移检测 + 告警
- 血缘 DAG 自动构建 + 影响分析
- 特征废弃审批流程（通知所有下游）

**产出**：特征质量的"健康分" + 出问题时的"爆破半径"

---

## 十一、技术选型建议

| 组件 | 推荐 | 替代方案 | 理由 |
|------|------|---------|------|
| Feature Registry | MySQL（已有）+ Web Backend | Feast Registry (gRPC) | 前期不需要引入 Feast 的复杂度，MySQL 足够存几万条特征元数据 |
| Online Store | Redis Cluster（已有） | HBase, Cassandra | 已有 Redis 基础设施，扩展 Cluster 模式即可 |
| Offline Store | Hive + Iceberg（内部已有Hadoop） | ClickHouse, Delta Lake | 复用已有大数据平台，Iceberg 支持 time travel |
| Offline Compute | Spark（内部已有） | Flink batch mode | 复用已有 Spark 集群 |
| Nearline Compute | Flink（内部已有） | Kafka Streams, KSQL | 复用已有 Flink 集群 |
| Feature Quality | 自研 scheduler + PSI 计算 | Great Expectations, Deequ | 轻量级，指标定义灵活 |
| Serving API | Spring Boot REST（复用） | gRPC, Feast Serving | 性能足够（<5ms），生态统一 |

---

## 十二、当前不做的事情

- **不引入 Feast/Tecton 等重量级开源方案**：IRP 已有 Redis/Spark/Flink/Hive 等核心组件，用自研 Registry + Serving API 的成本远低于适配开源方案的复杂度
- **不做实时特征训练在线更新（Online Learning）**：离线训练 → 在线推理的范式已经够用，在线学习引入的工程复杂度（模型回滚、特征实时一致性）收益有限
- **不做特征市场（Feature Marketplace）跨团队交易**：一期是单一风控部门内部使用，不需要租户隔离、计费、SLA 合同等
- **不做 Auto Feature Engineering**：自动化特征生成（Featuretools 等）在风控场景效果有限，风控特征的业务可解释性比自动生成更重要

---

> 此方案与 `IRP决策质量监控系统建设方案.md` 互补：
> - **指标中心（本文）**：管的是"决策要用什么特征"——特征的定义、计算、存储、质量
> - **监控大盘（前文）**：管的是"决策做得怎么样"——决策的通过率、延迟、模型效果
> - 两者共同构成完整的风控 MLOps 体系
