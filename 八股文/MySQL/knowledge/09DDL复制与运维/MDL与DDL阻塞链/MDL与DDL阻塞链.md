# Metadata Lock 与 DDL 阻塞链

## 结构定位
Q: MySQL MDL 保护什么，为什么普通 SELECT 也会持有？
A:
- MDL 保护表、schema、routine 等元数据定义与正在执行语句/事务的一致性，属于 Server 层。
- SELECT 打开表时取得共享 MDL，保证执行期间列和表定义不会被并发 DDL 改掉。
- DDL 通常需要排他 MDL；它可能等待旧事务，而新到共享请求又受队列公平策略影响，形成“DDL 堵住后续查询”。
- MDL 与 InnoDB record lock 独立，`SHOW ENGINE INNODB STATUS` 不足以看到完整 MDL 链。

## 生命周期
Q: 为什么一个执行完 SELECT 后处于 Sleep 的连接仍能阻塞 ALTER TABLE？
A:
- 在显式事务中，语句取得的事务级 MDL 通常保持到 COMMIT/ROLLBACK，而非结果返回即释放。
- 连接 Sleep 只表示当前未执行命令，不表示没有开放事务或锁。
- DDL 排他请求在队列等待，随后业务查询可能排在它后面，连接数快速堆积。
- autocommit 单语句完成后通常更快释放，但框架事务边界必须确认。

## 阻塞算法
Q: 一次在线 DDL 开始和结束为什么都可能需要短暂排他 MDL？
A:
1. 开始阶段取得/升级 MDL，校验定义并建立 DDL 上下文。
2. 执行 INSTANT 元数据更新，或 INPLACE/COPY 的扫描构建；支持时允许并发 DML。
3. 收尾阶段应用 online log、切换字典/表对象，通常需要再次获得排他窗口。
4. 若长事务迟迟不释放共享 MDL，开始或收尾都会卡住。

## 边界与代价
Q: `LOCK=NONE` 是否保证 DDL 完全不阻塞业务？
A:
- 不保证。它描述主要执行阶段允许并发 DML，元数据切换仍需 MDL。
- DDL 还会消耗 I/O、CPU、redo/binlog、Buffer Pool，并可能造成复制延迟。
- 不支持请求算法/锁级别时，是否报错或降级取决于显式 ALGORITHM/LOCK 与语句。
- 应显式指定期望算法，让不满足条件时失败而非意外 COPY。

## 验证与治理
Q: DDL 卡住时怎样找真正 blocker？
A:
- 查 `performance_schema.metadata_locks`、threads、events_statements_current，或 `sys.schema_table_lock_waits`。
- 沿 OWNER_THREAD_ID 找事务开始时间和会话来源；不要只 kill 最前面的 DDL。
- 设置合理 `lock_wait_timeout`，在变更前清理长事务并监控 DDL 阶段。
- 终止等待 DDL 可解除队列放大，但根因仍是事务治理和变更流程。
