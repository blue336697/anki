# Handler 接口与存储引擎边界

## 结构定位
Q: MySQL 服务层与 InnoDB 通过什么边界协作，为什么说优化器不直接操作 B+ 树？
A:
- SQL 层负责协议、语法、权限、逻辑优化、跨表计划和结果计算；存储引擎负责行存储、索引访问、事务、锁和恢复。
- 每张打开的表在 SQL 层有 `TABLE`，其 `file` 指向具体 `handler`；InnoDB 实现是 `ha_innobase`。
- 优化器调用 handler 的统计与成本接口评估路径，执行器再调用 `index_read`、`read_range_first`、`rnd_next`、`write_row` 等访问行。
- 源码锚点：`sql/handler.h`、`storage/innobase/handler/ha_innodb.cc`。

## 对象关系
Q: TABLE、TABLE_SHARE、handler、dict_table_t 与 trx_t 分别处在哪一层？
A:
- `TABLE_SHARE` 是可跨会话共享的表定义缓存对象，`TABLE` 是一次打开实例，含字段、位图和执行期状态。
- `handler` 嵌在 `TABLE` 侧，保存当前索引、游标和引擎能力，是 SQL 层调用引擎的多态入口。
- InnoDB 内部 `dict_table_t/dict_index_t` 描述字典与索引，`row_prebuilt_t` 缓存 handler 与行层之间的执行状态。
- `trx_t` 属于 InnoDB 事务系统，通过 THD 关联；MDL 属于服务层，记录锁属于 InnoDB，二者不能混为一种锁。

## 调用链
Q: 执行器通过二级索引读取一行时，handler 边界内外分别做什么？
A:
1. SQL 层根据计划设置读列位图和条件，选择索引并调用 handler 定位 key/range。
2. InnoDB B-tree 游标搜索二级索引叶子记录，必要时根据主键回到聚簇索引。
3. InnoDB 做 MVCC 可见性或加锁判断，将物理记录转换为 MySQL 行格式；ICP 可把部分条件下推到引擎减少回表。
4. SQL 层继续执行剩余谓词、表达式、连接、聚合和发送结果。

## 能力与成本
Q: 为什么不同存储引擎会影响 SQL 的语义与优化计划？
A:
- handler 通过 capability flags 声明事务、外键、索引顺序、全文、空间、online DDL 等能力；SQL 层据此限制语法和选择算法。
- 引擎提供基数、页数、range 行数和 I/O 成本估算；统计误差会让服务层选择错误的连接顺序或访问方法。
- InnoDB 支持事务和行锁，MyISAM 主要是表锁且无崩溃安全事务；不能只把引擎差异理解成“文件格式不同”。
- 跨多个事务引擎提交时，服务层 transaction coordinator 还要协调 prepare/commit。

## 边界与验证
Q: 面试中怎样避免把服务层、InnoDB 和操作系统责任混在一起？
A:
- 先按层回答：SQL 语义/计划属于 server，页/索引/MVCC 属于 InnoDB，page cache/fsync/块设备属于 OS 与存储。
- `EXPLAIN` 主要反映优化器计划；`SHOW ENGINE INNODB STATUS`、`INNODB_METRICS` 反映引擎内部；系统工具反映真实 I/O。
- “Using where”不代表条件都在 server 执行，“Using index condition”才表示 ICP；“数据在内存”也不等于没有 redo fsync。
- 排障时为每个假设找对应层的指标，避免用单一 QPS 或 Buffer Pool 命中率解释所有问题。
