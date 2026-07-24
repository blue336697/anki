# Record、Gap、Next-Key 与 Insert Intention Lock

## 结构定位
Q: record、gap、next-key lock 分别覆盖什么区间？
A:
- record lock 只锁某个索引记录；gap lock 只锁两个索引 key 之间或边界的空隙，不锁记录本身。
- next-key lock = record + 其前方 gap，若 key 序列 10、20，则记录 20 的 next-key 常表示 `(10,20]`。
- supremum 伪记录的 next-key 可表示最后 key 之后的 gap。
- 这些都是索引级范围保护，具体区间由实际扫描路径决定。

## 兼容语义
Q: 为什么 gap S 与 gap X 之间可以兼容，却都能阻止 INSERT？
A:
- gap lock 的目的主要是禁止向间隙插入，而不是保护某个已有值的读写，因此不同事务 gap 锁可共存。
- 记录被 purge 合并时多个事务的 gap 保护都需保留，促成这种兼容设计。
- INSERT intention 是特殊 gap 请求，多个插入不同位置的事务通常兼容，但会被覆盖该 gap 的普通 gap/next-key 阻塞。
- 最终新记录插入还需记录级 X 语义和唯一检查。

## 加锁算法
Q: RR 下范围 `WHERE k BETWEEN 10 AND 20 FOR UPDATE` 通常怎样加锁？
A:
1. 沿执行计划所选索引定位下界并顺序扫描。
2. 对命中记录及其前 gap 申请 next-key X，覆盖查询范围内现有记录与可插入位置。
3. 为确认上界，扫描可能触及首个超界记录，其锁边界需结合实际计划与版本验证。
4. 若 k 是唯一索引且完整等值命中，则可优化为纯 record lock，不需要 gap。

## 隔离与边界
Q: RC 下是否完全没有 gap lock？
A:
- RC 对普通搜索/索引扫描通常禁用 gap locking，并释放不匹配记录锁以提高并发。
- 外键约束检查、重复键检查等仍可能使用 gap 保护，所以“RC 无 gap lock”过度绝对。
- RR 的一致性普通 SELECT 不加这些锁；next-key 主要用于锁定读和写操作。
- binlog 格式与历史版本曾影响 RC 锁行为，面试应声明基线版本。

## 验证与实践
Q: 怎样精确画出某条 SQL 的锁区间？
A:
- 先列索引有序 key，包括 infimum/supremum，再用 EXPLAIN 确定真实访问索引和扫描方向。
- 双会话在各 gap 尝试 INSERT，用 data_locks/data_lock_waits 记录阻塞位置。
- WHERE 结果集不足以推断锁集：执行器为判断条件可能扫描未返回记录。
- 缺索引时应先优化扫描，否则讨论精细 gap 边界对生产治理意义有限。
