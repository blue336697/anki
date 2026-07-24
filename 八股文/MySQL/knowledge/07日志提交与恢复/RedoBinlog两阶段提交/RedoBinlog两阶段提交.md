# Redo 与 Binlog 两阶段提交

## 结构定位
Q: 为什么 MySQL 必须协调 redo 和 binlog，单纯“先后各写一次”不够？
A:
- redo 决定主库崩溃恢复是否保留事务，binlog 决定副本/PITR 是否能看到事务。
- 若先 redo commit 后 binlog 失败，主库有而副本无；若先 binlog 完整后 redo 未记录且主库回滚，副本有而主库无。
- 内部 XA 让 InnoDB 先 prepare，再以完整 binlog 作为提交裁决依据，恢复时可统一决定。
- 这解决本机两日志原子性，不等于分布式业务事务。

## 状态与标识
Q: prepare redo、Xid_event 和 commit redo 在恢复中怎样配合？
A:
- InnoDB prepare 把事务置为 PREPARED 并使相关 redo 可恢复。
- Server 将 binlog cache 写入 binlog，事务以 Xid_event/完整边界落盘。
- 随后 InnoDB commit 标记事务完成；正常执行中提交顺序还会参与组提交优化。
- 崩溃恢复若看到 prepared 事务，就查 binlog 是否含完整 XID 来决定 commit/rollback。

## 提交算法
Q: 一次开启 binlog 的 InnoDB 事务提交链如何描述？
A:
1. prepare：InnoDB 写 prepare 状态与 redo。
2. flush/sync binlog：事务事件进入 binlog，并按 `sync_binlog` 策略持久化。
3. commit：通知 InnoDB 提交，写提交状态并按 redo flush 策略处理。
4. 返回客户端；组提交会让多个事务共享各阶段昂贵 I/O，而不改变每个事务顺序约束。

## 故障边界
Q: 两阶段提交是否保证客户端收到错误就一定没提交？
A:
- 不保证。服务器可能已持久提交但在返回 ACK 前网络断开，客户端看到超时而提交结果未知。
- 应用必须使用业务幂等键/唯一约束和查询确认，不能对超时直接无脑重放非幂等事务。
- 两阶段提交保护日志一致性，不解决客户端与服务器之间的 exactly-once。
- 外部 XA 还涉及资源管理器、协调器日志和悬挂事务，故障面更大。

## 验证与误区
Q: 如何验证 redo-binlog 一致性配置？
A:
- 检查 `innodb_flush_log_at_trx_commit`、`sync_binlog`、binlog 开启、底层 fsync 语义，并做崩溃测试。
- 常用最强持久组合是 redo=1、sync_binlog=1，但仍依赖可靠存储和双日志协议。
- `SHOW MASTER STATUS` 类旧术语在 8.4 有替代命令趋势，运维脚本需核对版本。
- 不要把“双1”解释成绝不丢任何外部可见操作；客户端未知结果和硬件谎报仍需业务处理。
