# 逻辑改写、子查询与 Semijoin

## 结构定位
Q: MySQL 优化器在选择索引前会做哪些逻辑等价改写？
A:
- 常量/等值传播、恒真恒假消除、谓词下推、外连接转内连接、视图/派生表 merge 等。
- `IN/EXISTS` 子查询可转 semijoin，避免为外表每行完整重复执行子查询。
- CTE/derived 可 merge 或 materialize，取决于语义限制和成本。
- 改写必须保持 NULL、重复行、外连接和聚合语义，不能按直觉随意交换。

## Semijoin策略
Q: FirstMatch、DuplicateWeedout、LooseScan、Materialization 各在做什么？
A:
- FirstMatch 找到首个内表匹配后停止，适合只关心存在性。
- DuplicateWeedout 用临时结构去除连接产生的重复外行。
- LooseScan 利用索引分组跳跃，每组选择代表 key。
- Materialization 先把子查询结果构造成带索引临时表，再做查找；具体候选受 SQL 形态限制。

## 改写流程
Q: 一个 `WHERE outer.a IN (SELECT inner.b...)` 可能如何执行？
A:
1. 预处理判断相关性、NULL 语义和是否满足 semijoin 条件。
2. 将子查询表并入候选连接图或选择物化。
3. 比较各 semijoin strategy、访问路径和连接顺序成本。
4. 生成 iterator 树；EXPLAIN TREE/optimizer_trace 可见改写而传统表格可能不直观。

## 边界与代价
Q: 为什么“EXISTS 一定比 IN 快”是过时口诀？
A:
- 现代优化器常把二者改写到相同 semijoin 计划；性能由数据、索引、相关性与 NULL 语义决定。
- `NOT IN` 遇 NULL 是 UNKNOWN，和 `NOT EXISTS` 语义不同，不能只为性能机械替换。
- 物化可避免重复计算，但大结果会占内存/磁盘临时表。
- 优化器 hint 可控制策略用于验证，但不应掩盖统计或 SQL 设计问题。

## 验证
Q: 如何确认子查询被怎样改写？
A:
- 用 `EXPLAIN FORMAT=TREE/JSON` 看 materialize、semijoin、dependent subquery 等节点。
- 开 optimizer_trace 查看 transformation 候选与拒绝原因。
- 用 ANALYZE 比较 actual rows/loops；相关子查询 loops 巨大通常是关键证据。
- 测试含 NULL、重复值和空集的正确性，性能改写不能破坏结果。
