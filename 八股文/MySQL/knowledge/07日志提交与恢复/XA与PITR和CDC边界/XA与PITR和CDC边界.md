# XA、PITR 与 CDC 的一致性边界

## 结构定位
Q: MySQL 内部 XA 和用户 `XA START` 分别解决什么问题？
A:
- 内部 XA 协调 InnoDB redo 与 server binlog，是单实例两日志提交协议。
- 外部 XA 让一个全局事务跨多个 XA resource manager，由外部 coordinator 执行 prepare/commit。
- 两者都用 prepare 状态，但故障域和运维责任不同；外部 XA 可能产生长期 prepared transaction。
- 微服务场景使用 XA 前要评估协调器可用性、锁持有时间和启发式恢复。

## PITR结构
Q: 一次可靠 Point-in-Time Recovery 需要哪些材料？
A:
- 一份一致的全量/物理备份及其起始 GTID/binlog position。
- 从该位置开始连续、未损坏且包含目标时刻的 binlog。
- 相同或兼容 schema/版本、密钥和恢复配置，以及明确的截止 GTID/时间/事件。
- 恢复流程是先还原基线，再按事务边界重放 binlog，最后做一致性验证和切换。

## CDC算法
Q: CDC 消费 ROW binlog 如何保证至少一次并维护事务边界？
A:
1. 按 file/position 或 GTID 顺序读取事件，缓存一个事务直到 XID/commit。
2. 原子地写下游变更与消费位点，或用幂等主键去重后再推进 checkpoint。
3. 故障重启从已确认位点重读，允许重复但不能静默跳过。
4. DDL、表映射、row image、字符集和 schema evolution 必须与 DML 一起处理。

## 一致性边界
Q: Binlog CDC 为什么天然不等于端到端 exactly-once？
A:
- MySQL commit 与下游消息/存储 commit 是两个系统；消费者可能已写下游但未保存位点。
- GTID/position 能唯一标识上游顺序，不自动让下游副作用幂等。
- MINIMAL row image、无主键、DDL 和数据回填会增加重放歧义。
- 需要下游事务、幂等键、outbox/inbox 或事务消息协议建立端到端语义。

## 验证与演练
Q: 怎样验证 PITR/CDC 不是“有 binlog 就行”？
A:
- 定期从备份在隔离环境恢复到指定 GTID/时刻，核对行数、校验和与业务不变量。
- 演练 binlog 缺段、重复事件、DDL、超大事务、消费者崩溃和位点回退。
- 监控最老未消费位点与 binlog 过期窗口，确保保留时间覆盖最长故障。
- 对误删恢复先在旁路实例重放并导出目标数据，避免直接在生产反向执行不可靠 SQL。
