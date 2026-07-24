![两阶段提交](knowledge/日志/Binlog与两阶段提交/two_phase_commit.svg)

# Binlog与两阶段提交

## Binlog卡
Q: binlog 和 redo log 有什么区别？
A:
- binlog 是 Server 层日志，记录逻辑变更，用于复制和恢复
- redo log 是 InnoDB 层日志，记录页修改，用于崩溃恢复
- binlog 有 statement、row、mixed 等格式
- redo 是循环写，binlog 通常追加写
- 面试表达：redo 保证存储引擎崩溃恢复，binlog 支撑主从复制和点位恢复

## 两阶段提交卡
Q: MySQL 为什么需要 redo 和 binlog 的两阶段提交？
A:
- 一个事务同时要写 InnoDB redo 和 Server binlog
- 如果二者提交顺序不一致，崩溃后可能出现主库数据和 binlog 不一致
- 两阶段提交先 prepare redo，再写 binlog，最后 commit redo
- 崩溃恢复时根据 redo 状态和 binlog 是否完整决定提交或回滚
- 核心目标是保证事务提交和复制日志的一致性

## 格式卡
Q: statement、row、mixed binlog 格式如何取舍？
A:
- statement 记录 SQL，日志小，但遇到非确定函数或环境差异可能不安全
- row 记录行变化，复制更准确，但日志可能更大
- mixed 根据场景在 statement 和 row 之间切换
- 生产中 row 更常用于保证复制正确性和数据恢复精确性
- row 格式也更利于基于 binlog 的数据订阅和审计

## 正确性审查卡
Q: binlog 和两阶段提交有哪些常见误区？
A:
- “有 redo 就能做主从复制”：错误。复制依赖 binlog
- “binlog 和 redo 写一个就行”：错误。用途不同
- “statement 一定更好因为日志小”：不完整。正确性风险更高
- “两阶段提交是分布式事务”：不是，它是 MySQL 内部协调 redo/binlog 的提交协议
- “sync_binlog 不重要”：错误。它影响 binlog 持久性和故障丢失窗口
