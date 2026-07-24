# Multi-Range Read 与 Batched Key Access

## 结构定位
Q: MRR 和 BKA 分别解决什么随机访问问题？
A:
- MRR 将多个二级索引范围/主键定位请求批量化，并按聚簇主键或页局部性重排，减少随机回表。
- BKA 是连接算法：先从外表收集一批连接 key，借助 MRR 批量访问内表。
- 二者用更多缓冲与延迟换取 I/O 局部性，主要在大批量、非覆盖二级访问和冷数据上有价值。
- 相关控制包括 `optimizer_switch` 的 mrr/batched_key_access 与 join buffer。

## 缓冲结构
Q: MRR 为什么不能简单理解成“把结果排序后返回”？
A:
- 它重排的是底层行访问请求，不应改变 SQL 层最终无 ORDER BY 的语义契约。
- range 层先产生 rowid/主键，缓冲区分批排序或调度，再读取基表行。
- 缓冲有限时分多批，批越小局部性收益越弱；批越大占用执行期内存。
- 若索引覆盖无需回表，MRR 反而可能增加收集和排序成本。

## BKA算法
Q: BKA join 的执行链路是什么？
A:
1. 扫描外表，把若干外行及连接 key 写入 join buffer。
2. 合并相同/相邻内表查找请求，调用内表 MRR 接口批量读取。
3. 将返回的内表行与缓冲中的外行匹配，再执行剩余 join condition。
4. 重复批次直到外表结束；LEFT JOIN 等还需处理未匹配外行。

## 成本与边界
Q: 为什么优化器可能不启用 MRR/BKA？
A:
- 数据全在 Buffer Pool、点查很少或索引覆盖时，重排收益不足以抵消 CPU 和缓冲开销。
- LIMIT 很小需要尽快返回首行时，批处理可能增加延迟。
- 成本模型依赖行数、随机 I/O 估值和 buffer 大小，统计错误会影响决策。
- Hash Join、普通 nested loop 或合适联合索引可能从根源上减少内表访问。

## 验证与工程实践
Q: 如何证明 MRR/BKA 对某条 SQL 有效？
A:
- 用 EXPLAIN/TREE 看访问路径提示，在隔离压测中开关对应 optimizer_switch 做 A/B。
- 同时比较实际 rows、随机读 IOPS、Buffer Pool miss、CPU、内存和 p95，而不只看一次耗时。
- 若根因是缺失联合索引或连接输出爆炸，强制 BKA 只是缓解症状。
- 优化器 hint 应作为验证和临时止血，长期仍需修正统计、索引或 SQL。
