# Lock Sys、记录锁对象与位图

## 结构定位
Q: InnoDB 所谓“行锁”在内存里为什么不是每行一个独立对象？
A:
- `lock_sys` 维护全局锁哈希与等待图；同一事务、同一索引页、同一模式的多个记录锁可合并进一个 `lock_t`。
- record lock key 包含 space id、page no，位图中的 bit 对应页内记录 `heap_no`，因此一个锁对象可表示页内多条记录。
- 锁模式字段组合 S/X 与 REC_NOT_GAP、GAP、INSERT_INTENTION 等标志。
- 源码锚点：`lock0lock.h/.cc`、`lock0priv.h`、Performance Schema data_locks。

## 对象关系
Q: 一个等待中的记录锁如何关联事务、被阻塞锁和等待线程？
A:
- `trx_t` 持有自身 lock list 与当前 wait lock；锁对象反向指向拥有/请求它的事务。
- 冲突检查在同一页/表的锁队列中判断模式、记录 bit 与 gap 语义，不能只比较 S/X。
- 请求不能授予时标记 WAIT，事务进入锁等待；等待图边表示“请求事务依赖持有事务”。
- 对方释放或锁队列变化后唤醒并重新检查，不保证按简单 FIFO 绝对公平。

## 加锁算法
Q: InnoDB 给一条索引记录加 X 锁的大致步骤是什么？
A:
1. B-tree 游标定位记录，得到 index、page id 和 heap_no。
2. 检查同事务是否已有更强/相同锁，能复用则更新位图。
3. 扫描相关锁队列判断冲突；无冲突时授予并挂入事务锁链。
4. 有冲突则创建等待请求、构建 wait-for 边并做死锁检测或等待超时。

## 内存与性能
Q: 锁很多为什么会消耗大量内存和 CPU，即使锁没有写入磁盘？
A:
- 大范围更新在许多页创建锁对象/位图并挂事务链，消耗内存。
- 每次冲突检测、释放、死锁图遍历都增加 CPU；热点页锁队列长会放大复杂度。
- 锁是运行时状态，崩溃后不恢复；redo/undo 恢复数据一致性后事务锁重新为空。
- `rows_locked` 是逻辑规模指标，不等于 lock_t 对象数。

## 验证与误区
Q: 如何从 data_locks 判断锁住的是记录还是 gap？
A:
- 查看 ENGINE_LOCK_ID、OBJECT、INDEX_NAME、LOCK_TYPE、LOCK_MODE、LOCK_DATA，并关联 data_lock_waits。
- LOCK_MODE 中 `REC_NOT_GAP` 表示纯记录，`GAP`/`INSERT_INTENTION`体现间隙语义；显示格式依版本而异。
- LOCK_DATA 可能是索引 key 或页信息，不等同于业务整行；没有主键时定位更困难。
- “InnoDB 行锁锁在数据行上”应改为“锁在索引记录/间隙上，由页内 heap_no 位图表达”。
