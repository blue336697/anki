# Crash Recovery、Checkpoint 与未提交事务

## 结构定位
Q: InnoDB crash recovery 的总体目标和主要阶段是什么？
A:
- 从最近 checkpoint 开始扫描 redo，重做崩溃前已记录但数据页尚未落盘的结构变化。
- redo 会把已提交和未提交事务的页变化都前滚，因为日志先保证物理结构可达一致。
- 随后识别未完成事务并利用 undo 回滚，提交事务保持。
- 恢复还需处理 doublewrite 修复、change buffer merge、prepared transaction 等状态。

## Checkpoint结构
Q: Checkpoint 保存什么，为什么不是把所有脏页一次刷干净？
A:
- 保存可安全开始恢复的 LSN 和日志元数据；推进条件是更早修改对应的脏页已落盘。
- Fuzzy checkpoint 允许系统持续有脏页，只要维护 WAL 与 oldest modification 边界。
- 若每次 checkpoint 强制全池干净，会造成周期性 I/O 停顿，失去后台平滑刷脏的意义。
- 正常关闭可做更完整清理，但 crash recovery 不能依赖正常关闭。

## 恢复算法
Q: 崩溃发生在事务 prepare、binlog fsync、InnoDB commit 之间时如何判定提交？
A:
1. 恢复 redo 得到 InnoDB prepared/committed 状态。
2. Server 扫描 binlog，识别具有完整事务/XID 的提交记录。
3. 对已 prepare 且 binlog 完整的内部 XA 事务提交；binlog 不完整的回滚。
4. 这正是 redo-binlog 两阶段提交用于避免两套日志分叉的核心。

## 恢复代价
Q: 什么决定 crash recovery 时间？
A:
- checkpoint age、redo 量、脏页/随机页分布、存储读写吞吐和 CPU 校验。
- 未提交大事务的 undo 回滚量可能在服务启动后继续消耗很久。
- change buffer debt、表空间数量和损坏检测也会拉长过程。
- Redo capacity 是上限因素之一，但“日志大就必然全量重放”不准确，实际从 checkpoint 开始。

## 验证与演练
Q: 怎样验证数据库真正满足恢复目标，而不是只看配置？
A:
- 在隔离环境做 kill -9/掉电模拟，覆盖高写入、DDL、大事务和复制场景，记录恢复时长与数据校验。
- 核对错误日志中的 scan/checkpoint/recovery 进度，恢复后做业务不变量和副本一致性检查。
- 测试备份恢复与 PITR；crash recovery 只处理本机日志，不替代误删/介质灾难恢复。
- 不在生产随意使用 `innodb_force_recovery`，它是救援导出工具且高等级可能破坏可写安全。
