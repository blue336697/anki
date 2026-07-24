# 事务对象、状态机与 ACID 分层

## 结构定位
Q: SQL 层事务与 InnoDB `trx_t` 怎样关联，事务何时真正开始？
A:
- THD 保存 server transaction context，InnoDB 为其创建/关联 `trx_t`，记录 id、state、read view、undo、lock list 和隔离级别。
- `START TRANSACTION` 建立显式事务语义，但 InnoDB 事务 id 常在首次需要写入/加锁时才分配；只读事务可避免部分开销。
- autocommit=1 的单条语句通常是一个事务；显式事务中多条语句共享提交边界。
- 源码锚点：`trx0trx.h/.cc`、`handler.cc`、`transaction.cc`。

## ACID分层
Q: InnoDB 的 ACID 分别由哪些机制共同实现？
A:
- Atomicity：undo 支持语句/事务回滚，事务状态与恢复决定全部提交或撤销。
- Consistency 不是单一模块：约束、日志恢复、锁/MVCC 和正确应用逻辑共同维持不变量。
- Isolation：隔离级别、MVCC、记录/间隙锁与 MDL 协作。
- Durability：redo WAL、fsync、doublewrite、binlog 两阶段提交及底层存储共同决定。

## 状态转换
Q: 一个更新事务从 ACTIVE 到 COMMITTED 的关键状态链是什么？
A:
1. ACTIVE 中执行 DML，生成 undo/redo并持有记录锁；需要 binlog 时 server 缓存事件。
2. 提交协调器让 InnoDB prepare，写 prepare redo；随后写/刷 binlog。
3. InnoDB commit 写提交标记并按策略刷 redo，释放事务锁，使版本对新 Read View 可见。
4. undo 不一定立即删除，进入 history 等待 purge；提交返回时后台清理可能尚未完成。

## 隔离与代价
Q: 为什么长事务即使 QPS 很低也可能拖垮系统？
A:
- 长 Read View 阻止 purge 回收旧版本，history list、undo tablespace 和二级 delete-mark 累积。
- 长写事务持有锁、undo 和 binlog cache，提交时产生突发 fsync/复制事件。
- 连接断开或应用超时不总能立即结束服务端事务，必须核对 `INNODB_TRX`。
- 大事务还拉长故障恢复、复制应用和回滚时间。

## 验证与边界
Q: 排查“事务没提交”应看哪些证据？
A:
- `information_schema.innodb_trx` 看开始时间、state、rows_locked/modified、query；结合 `performance_schema.threads` 找会话。
- `performance_schema.data_locks/data_lock_waits` 看锁链，history list 看旧版本积压。
- 检查驱动 autocommit、框架传播、异常分支和连接池归还逻辑；SQL 日志只有 BEGIN 没有 COMMIT 是线索。
- kill 前评估回滚量；大事务 kill 后仍可能长时间处于 rollback，不能反复重启逃避。
