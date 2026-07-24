# Change Buffer 与 Adaptive Hash Index

## 结构定位
Q: Change Buffer 缓冲什么，为什么只针对部分二级索引页修改？
A:
- 当非唯一二级索引目标页不在 Buffer Pool 时，可先把 insert/delete-mark/purge 变更记入 change buffer，避免立即随机读页。
- 目标页以后因查询或后台合并读入时，再把 buffered changes 应用到真实二级页。
- 唯一索引必须先读页检查唯一性，通常不能这样延迟；聚簇索引写入也不能被简单缓冲。
- Change Buffer 自身是系统表空间中的持久 B+ 树，并有 bitmap 标记页状态，崩溃恢复后仍可合并。

## AHI结构
Q: Adaptive Hash Index 与普通显式 Hash 索引有什么不同？
A:
- AHI 根据热点 B+ 树访问模式在内存自动建立 hash 前缀到页/记录的映射，加速某些等值查找。
- 它不是用户可定义索引，不持久化，底层正确性仍依赖 B+ 树。
- B-tree 页分裂、删除和淘汰时要维护/失效 hash 条目；高并发可能产生分区 latch 竞争。
- 8.x 可动态关闭 AHI；是否受益取决于热点与竞争，不能把它当通用加速器。

## ChangeBuffer算法
Q: 一次未命中缓存的非唯一二级 INSERT 如何走 Change Buffer？
A:
1. 聚簇记录正常写入并生成 undo/redo；处理二级索引时发现目标页不在池中。
2. 检查页面是否适合缓冲及剩余空间估计，把变更写入 change buffer 并标 bitmap。
3. 事务提交不要求目标二级页立刻读入；change buffer 记录本身已受 redo/恢复保护。
4. 后续读取该页或后台线程执行 merge，把变更应用并清理缓冲条目。

## 代价与边界
Q: Change Buffer 为什么可能从优化变成债务？
A:
- 写密集且目标页长期不读时缓冲快速增长，占系统表空间和 Buffer Pool，并把 I/O 延迟到 merge。
- 查询突然触碰这些页会在读路径承担 merge 延迟。
- SSD 随机读成本下降后收益可能减少，但高写放大 workload 仍需实测。
- AHI 同样有维护成本；命中低或 latch 等待高时关闭可能更好。

## 验证与调优
Q: 怎样分别判断 Change Buffer 和 AHI 是否健康？
A:
- Change Buffer 看 `SHOW ENGINE INNODB STATUS` 的 Ibuf、`INNODB_METRICS` 中 ibuf size/merges，以及系统表空间增长。
- AHI 看 hash searches、non-hash searches 和相关 latch waits，做开关 A/B 压测。
- 若唯一索引过多、二级索引冗余，先减索引；调大 change buffer 不能消除根本写放大。
- 所有判断应包含写吞吐、读 p99、恢复时间与空间，而不只看命中计数。
