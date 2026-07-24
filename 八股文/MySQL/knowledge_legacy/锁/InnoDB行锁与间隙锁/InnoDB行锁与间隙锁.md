# InnoDB行锁与间隙锁

## 锁类型卡
Q: InnoDB 常见行级锁有哪些？
A:
- Record Lock 锁住具体索引记录
- Gap Lock 锁住两个索引记录之间的间隙
- Next-Key Lock 是 Record Lock + Gap Lock，锁住左开右闭区间
- Insert Intention Lock 表示事务准备向某个 gap 插入
- 行锁本质上加在索引上，没有合适索引时可能锁范围很大

## 当前读卡
Q: 一致性读和锁定读有什么区别？
A:
- 一致性读是普通快照读，通常通过 MVCC 读取可见版本
- 锁定读读取当前最新数据，并对读取范围加锁
- `select ... for update` 加排他锁，`lock in share mode` 或 `for share` 加共享锁
- update/delete/insert 也属于当前读相关写操作
- 面试表达：普通 select 和 for update 不是同一种读语义

## 间隙锁卡
Q: InnoDB 为什么需要 gap lock 和 next-key lock？
A:
- 它们用于锁住索引记录之间的范围，阻止其他事务插入新记录
- 在 RR 隔离级别下，next-key lock 可用于解决当前读场景的幻读
- 唯一索引等值命中已有记录时，可能退化为 record lock
- 范围查询、未命中查询或非唯一索引更容易产生 gap/next-key lock
- 代价是锁范围变大，可能降低并发甚至引发死锁

## 正确性审查卡
Q: InnoDB 行锁有哪些常见误区？
A:
- “InnoDB 行锁一定只锁一行”：错误。范围查询可能锁 gap 或 next-key
- “没有索引也能精准行锁”：错误。可能扫描并锁住更多记录
- “间隙锁锁的是已有记录”：错误。它锁的是记录之间的可插入范围
- “普通 select 会加锁”：普通一致性读通常不加行锁
- “for update 只锁查询结果”：不完整。它可能锁扫描范围
