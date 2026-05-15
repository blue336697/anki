![MVCC ReadView可见性判断](knowledge/事务/MVCC与ReadView/mvcc_readview.svg)

# MVCC与ReadView

## MVCC卡
Q: InnoDB MVCC 解决什么问题？
A:
- MVCC 让读操作在很多场景下不阻塞写，写也不阻塞普通一致性读
- InnoDB 通过隐藏列 `trx_id`、`roll_pointer` 和 undo 版本链实现多版本
- 查询根据 ReadView 判断哪个版本对当前事务可见
- 它主要服务一致性读，不等于所有读都不加锁
- 面试表达：MVCC 是用多版本换并发读性能，不是替代锁的全部机制

## ReadView卡
Q: ReadView 如何判断一个记录版本是否可见？
A:
- ReadView 记录创建时活跃事务 ID 集合和边界
- 如果版本 `trx_id` 小于低水位，通常可见
- 如果版本 `trx_id` 属于活跃事务集合，通常不可见
- 如果版本来自未来事务，通常不可见
- 当前版本不可见时，沿 `roll_pointer` 找 undo 版本链中的旧版本

## RCRC卡
Q: READ COMMITTED 和 REPEATABLE READ 下 ReadView 有什么区别？
A:
- RC 隔离级别下，每次一致性读都会生成新的 ReadView
- RR 隔离级别下，事务第一次一致性读生成 ReadView，后续复用
- 因此 RC 下同一事务两次读可能看到其他事务已提交的新版本
- RR 下同一事务多次一致性读通常结果稳定
- 面试边界：锁定读和当前读不走普通快照读语义

## 正确性审查卡
Q: MVCC 有哪些常见误区？
A:
- “MVCC 不需要 undo”：错误。历史版本来自 undo 版本链
- “RR 下所有读都不会变”：不完整。当前读、锁定读和写操作语义不同
- “MVCC 能解决所有幻读”：不完整。快照读和当前读要区分
- “ReadView 是全局唯一”：错误。它和事务隔离级别及读时机相关
- “版本链无限保留”：错误。purge 会清理不再需要的历史版本
