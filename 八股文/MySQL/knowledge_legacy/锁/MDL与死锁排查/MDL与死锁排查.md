# MDL与死锁排查

## MDL卡
Q: MySQL MDL 元数据锁解决什么问题？
A:
- MDL 保护表结构元数据，避免查询过程中表结构被并发修改
- 普通 DML/查询会持有 MDL 读锁
- DDL 需要 MDL 写锁，会等待已有读锁释放
- 长事务持有 MDL 读锁时，后续 DDL 可能阻塞，再阻塞新的查询
- 面试表达：线上 alter 表卡住，常常不是 DDL 本身慢，而是在等 MDL

## 死锁卡
Q: InnoDB 死锁通常如何产生和处理？
A:
- 多个事务以不同顺序持有并等待对方需要的锁会产生死锁
- InnoDB 可通过等待图检测死锁
- 检测到死锁后会回滚其中一个事务作为牺牲者
- 应用层要能识别死锁错误并做有限重试
- 工程上要统一访问顺序、缩短事务、减少范围锁

## 排查卡
Q: 线上遇到锁等待或死锁如何排查？
A:
- 查看 `show processlist` 判断线程状态和阻塞 SQL
- 查看 `information_schema.innodb_trx/innodb_locks/innodb_lock_waits` 或 performance_schema
- 使用 `show engine innodb status` 查看最近死锁信息
- 关注长事务、未提交事务、DDL 等待和大范围 update/delete
- 必要时先止血 kill 阻塞源，再回头优化事务和索引

## 正确性审查卡
Q: MDL 和死锁有哪些常见误区？
A:
- “select 不会影响 DDL”：错误。select 所在事务也可能持有 MDL 读锁
- “死锁都是数据库 bug”：错误。多数来自业务并发访问顺序
- “kill SQL 一定立刻释放锁”：不一定。回滚也需要时间
- “只要有索引就不会死锁”：错误。索引只能减少锁范围，不能消除等待环
- “DDL 低峰执行就一定安全”：不完整。仍需检查长事务和变更方案
