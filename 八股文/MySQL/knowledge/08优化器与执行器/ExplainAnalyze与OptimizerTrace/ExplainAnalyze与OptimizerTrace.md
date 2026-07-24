# EXPLAIN ANALYZE、TREE 与 Optimizer Trace

## 结构定位
Q: EXPLAIN、EXPLAIN ANALYZE 和 optimizer_trace 分别回答什么？
A:
- EXPLAIN 展示优化器计划与估算，不真实完成 SELECT。
- EXPLAIN ANALYZE 真实执行并为 iterator 给出 actual time、rows、loops，可验证估算。
- optimizer_trace 展示优化阶段的改写、候选路径、成本与拒绝原因，格式是版本相关诊断接口。
- Performance Schema 再补充等待、statement 聚合和历史样本。

## 指标含义
Q: ANALYZE 中 `actual time=a..b rows=r loops=n` 怎样解读？
A:
- a 近似首次产出行前时间，b 为该 iterator 一次/累计语义下的结束时间，具体显示需结合 loops。
- rows 通常是每 loop 平均或节点显示定义下的输出，估算总工作量要结合 loops。
- 父节点时间包含对子节点调用，不能把所有节点时间直接相加。
- 首个 estimated 与 actual 严重偏离的底层节点通常最值得修。

## 诊断算法
Q: 用执行计划定位慢 SQL 的标准顺序是什么？
A:
1. 确认 SQL、参数、事务与数据分布，先看 TREE 理解算子树。
2. 用 ANALYZE 从叶到根比较 rows/loops，找扫描放大、回表、join 爆炸、sort/materialize。
3. 用 trace 解释为何选择该路径，再核对统计、索引和成本。
4. 修改一个变量后重跑代表性参数和并发压测，验证尾延迟与写代价。

## 风险边界
Q: 哪些语句不能在生产随意 EXPLAIN ANALYZE？
A:
- ANALYZE 会真实执行；对 UPDATE/DELETE/INSERT 可产生真实修改，不能当只读工具。
- 即使 SELECT 也可能全表扫描、加锁函数、调用 UDF 或产生巨大临时表。
- 生产先用普通 EXPLAIN、历史事件和副本；必要时设置资源/时间限制。
- 计划里的时间会受缓存热度、并发和仪器开销影响，不能视为稳定基准。

## 工程实践
Q: 如何建立可回归的 SQL 性能证据？
A:
- 保存 schema、统计、变量、版本、参数分布、TREE/JSON 和 ANALYZE 结果。
- 记录逻辑/物理读、锁等待、临时表、redo/binlog 与 p50/p99。
- 升级、ANALYZE、加索引前后在同数据快照做对照。
- 不只固定 plan；建立自动发现 estimated/actual 偏差与延迟回归的机制。
