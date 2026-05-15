# BufferPool与页面置换

## 核心作用卡
Q: Buffer Pool 在数据库中承担什么角色？
A:
- Buffer Pool 是磁盘 page 在内存中的缓存层
- 查询和更新先通过 Buffer Pool 获取 page，减少重复磁盘 IO
- 它负责 page pin/unpin、dirty 标记、刷盘和替换策略
- 事务、锁、日志恢复也常围绕 Buffer Pool 中的 page 状态协同
- 面试表达：Buffer Pool 是存储引擎性能和一致性的关键交汇点

## DirtyPage卡
Q: dirty page 是什么？为什么不能随便刷盘？
A:
- dirty page 表示内存中的 page 已被修改但尚未持久化到磁盘
- 刷盘前要满足 WAL 约束：对应日志必须先落盘
- 未提交事务修改的 dirty page 如果刷盘，需要依赖日志支持回滚
- 页面刷盘策略影响性能、恢复时间和检查点设计
- 面试边界：刷 dirty page 不是简单写文件，要和日志、事务状态配合

## 替换策略卡
Q: Buffer Pool 页面置换常见策略有哪些？如何取舍？
A:
- LRU 根据最近访问淘汰，适合局部性较强的访问
- Clock 用引用位近似 LRU，开销更低
- 顺序扫描可能污染 LRU，导致热点页被淘汰
- 数据库可能使用 LRU-K、分区 Buffer、预读和扫描旁路优化
- 置换时通常不能淘汰 pinned page，dirty page 淘汰前要刷盘

## 正确性审查卡
Q: Buffer Pool 有哪些常见误区？
A:
- “缓存命中率高就一定快”：不完整。锁等待、日志刷盘、CPU 执行也会影响延迟
- “LRU 永远适合数据库”：错误。大范围扫描会污染缓存
- “dirty page 越早刷越好”：不一定。过早刷盘增加 IO，过晚会拉长恢复时间
- “Buffer Pool 只影响查询”：错误。写入、事务和恢复都依赖它
- “淘汰任意 page 都可以”：错误。pinned 或被锁定的 page 不能随便淘汰
