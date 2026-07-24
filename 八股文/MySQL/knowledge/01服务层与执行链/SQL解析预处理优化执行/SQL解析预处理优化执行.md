# SQL 解析、预处理、优化与执行

## 阶段定位
Q: 一条 SELECT 在 MySQL 服务层经历哪些阶段，各阶段产物是什么？
A:
- 解析器把 token 按语法规则构造成 `LEX`、`Query_block` 与 Item 表达式树，只保证语法结构成立。
- 预处理阶段解析表和列、展开星号、检查聚合与分组语义、权限并做类型推导；“列不存在”通常在这里暴露。
- 优化器执行等价改写、访问路径与连接顺序搜索，最终产生访问路径树或执行计划。
- 执行器初始化 iterator，按 `Init()/Read()` 拉取行，经表达式计算、排序、聚合后通过协议返回。

## 核心结构
Q: MySQL 8.x 执行计划内部为什么更接近一棵 iterator 树，而不是 EXPLAIN 的表格？
A:
- `AccessPath` 描述 table scan、index range、nested loop、hash join、sort、aggregate 等算子及成本、行数。
- 优化结束后访问路径被物化为 `RowIterator` 树；父算子通过 `Read()` 从子算子逐行拉取。
- EXPLAIN TRADITIONAL 把树压平成表格，会隐藏 materialize、weedout、hash join 等层次；TREE/JSON 更接近真实结构。
- 源码锚点：`sql/join_optimizer/access_path.h`、`sql/iterators/`、`sql/sql_executor.cc`。

## 优化执行链
Q: 为什么同一条 SQL 从逻辑正确到物理执行还要经过多次变换？
A:
1. 逻辑层先做常量传播、条件化简、外连接消除、子查询到 semijoin/derived 的变换。
2. 优化器枚举可用索引、range、ref、scan 及连接顺序，以估算行数乘单位成本比较候选。
3. 需要排序、去重、窗口或物化时插入额外算子，并考虑是否能用索引顺序避免它们。
4. 执行阶段根据真实数据逐行运行；传统优化器通常不会因中途估算错误自动重优化，所以估算偏差会贯穿整棵计划。

## 缓存与版本
Q: MySQL 8.4 还存在“SQL 查询缓存命中就不解析执行”吗？
A:
- 不存在。旧 Query Cache 在 MySQL 8.0 已移除，不能再把它画进现代查询链路。
- Prepared Statement 缓存的是服务端预处理语句结构及参数位，不是结果集；元数据变化可能触发重新准备。
- InnoDB Buffer Pool 缓存数据页，和 SQL 结果缓存是不同层次；命中 Buffer Pool 仍需权限、优化与执行。
- 应用或代理层可以缓存结果，但必须自行处理键设计、失效、一致性与权限隔离。

## 边界与验证
Q: 怎样证明慢 SQL 慢在优化阶段还是执行阶段？
A:
- `EXPLAIN ANALYZE` 实际执行并给出各 iterator 的估算行数、真实行数、loops 和耗时，可定位放大点。
- `optimizer_trace` 适合看候选访问路径、成本和改写决策，但格式是版本相关的诊断接口。
- Performance Schema 的 statement stage/wait 可区分解析、优化、锁等待、I/O 和发送结果；不要只看总时长。
- 对 DML 使用 `EXPLAIN ANALYZE` 要意识到它会真实修改数据；应在可回滚或隔离环境验证。
