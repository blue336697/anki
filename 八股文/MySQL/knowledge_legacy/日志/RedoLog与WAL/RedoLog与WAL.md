# RedoLog与WAL

## Redo卡
Q: InnoDB redo log 解决什么问题？
A:
- redo log 记录页级物理修改，用于崩溃恢复
- 事务提交时不必立即把所有数据页刷盘，只要 redo 满足持久化策略
- 崩溃后可通过 redo 重放已提交或已持久化日志对应的页面修改
- redo log 是 InnoDB 层日志，区别于 Server 层 binlog
- 面试表达：redo 保障 InnoDB 的崩溃恢复能力

## WAL卡
Q: WAL 在 MySQL redo 中如何体现？
A:
- Write-Ahead Logging 要求数据页刷盘前，对应 redo 日志先持久化
- 这样即使数据页没刷盘，崩溃后也能通过 redo 恢复
- redo 顺序写日志，比随机刷大量数据页更高效
- checkpoint 推进后，旧 redo 空间可以复用
- WAL 是性能和持久性的共同基础

## 参数卡
Q: innodb_flush_log_at_trx_commit 参数如何影响持久性？
A:
- `1`：每次提交写 log buffer 并 fsync，持久性最强，默认推荐
- `2`：每次提交写到 OS cache，通常每秒 fsync，宕机可能丢数据
- `0`：每秒写和 fsync，MySQL 崩溃可能丢最近事务
- 它影响 redo 持久化，不等同于 binlog 刷盘参数
- 生产要结合可靠性要求、磁盘能力和主从复制策略选择

## 正确性审查卡
Q: redo log 有哪些常见误区？
A:
- “redo 记录 SQL”：错误。redo 主要记录 InnoDB 页修改
- “redo 和 binlog 一样”：错误。层级、内容和用途不同
- “提交必须刷数据页”：不需要，WAL 允许先刷日志
- “checkpoint 是删除数据”：错误。它推进可复用的 redo 边界
- “参数调成 0 一定没事”：危险。崩溃时可能丢已提交事务
