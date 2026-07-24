# Read View 字段与可见性算法

## 结构定位
Q: InnoDB Read View 保存哪些边界，分别代表什么？
A:
- `m_creator_trx_id` 标识创建视图的事务，使事务能看到自己的修改。
- `m_low_limit_id` 是创建时尚未分配的下一个事务 id，`trx_id >=` 它必然在快照后启动。
- `m_up_limit_id` 是活跃读写事务集合中的最小 id；更小的事务通常已在视图前结束。
- `m_ids` 保存创建时仍活跃的读写事务 id；`m_low_limit_no` 还用于 purge 边界，不要与可见性 low_limit_id 混淆。

## 可见性规则
Q: 给定记录版本的 `trx_id`，Read View 怎样判断可见？
A:
- 若是 creator 自己的事务 id，可见。
- 若 `trx_id < up_limit_id`，说明在视图建立前已提交，可见。
- 若 `trx_id >= low_limit_id`，说明快照后才分配，不可见。
- 位于两者之间时，若在 `m_ids` 活跃集合中则不可见，否则表示创建视图前已提交而可见。

## 版本回溯
Q: 当前记录版本对 Read View 不可见时，引擎做什么？
A:
1. 从聚簇记录读取 `DB_ROLL_PTR`，定位对应 update undo。
2. 在内存记录副本上恢复旧列与旧 `DB_TRX_ID/ROLL_PTR`。
3. 对恢复出的前一版本再次运行可见性判断。
4. 直到找到可见版本、版本链结束或确认记录在快照时尚不存在。

## 快照时点
Q: REPEATABLE READ 的快照是在 BEGIN 时创建吗？
A:
- 普通 `START TRANSACTION` 通常在第一次一致性读时创建 Read View，不是 BEGIN 文本执行瞬间。
- `START TRANSACTION WITH CONSISTENT SNAPSHOT` 可在支持的隔离级别立即建立一致性快照。
- 事务在首次快照前执行当前读/写后，再做一致性读可能出现“自己新版本 + 他人旧快照”的组合。
- READ COMMITTED 通常每条一致性读创建新 Read View，因而能看到语句开始前新提交。

## 验证与边界
Q: 怎样用并发实验真正理解 Read View，而不是背四个字段？
A:
- 三会话安排 T1 长事务、T2 在快照前后提交更新、T3 观察当前值，分别在 RR/RC 执行相同 SELECT。
- 同时让 T1 更新一行，验证“一致性读可见自己的写”与其他行仍按旧快照。
- 用 `INNODB_TRX` 记录事务 id/开始时间，用 undo/history 指标观察长视图影响。
- Read View 只解决行版本可见性，不保护业务谓词不被他人写入；当前读与写仍依赖锁。
