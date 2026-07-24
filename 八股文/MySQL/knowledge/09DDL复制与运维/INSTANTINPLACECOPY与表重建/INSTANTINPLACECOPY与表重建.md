# INSTANT、INPLACE、COPY 与 Online DDL

## 结构定位
Q: MySQL Online DDL 的 INSTANT、INPLACE、COPY 各表示什么？
A:
- INSTANT 主要修改元数据，不扫描/重写现有行，通常最快，但支持范围和内部版本数量有限。
- INPLACE 表示由 InnoDB 原地执行，不使用 server COPY 算法；仍可能重建整表或索引。
- COPY 创建新表、复制所有行、切换名称，耗时和额外空间最大，通常限制并发 DML。
- “INPLACE”不等于“不重建”，“online”也不等于“无锁”。

## 内部结构
Q: INPLACE 创建二级索引时怎样允许并发 DML？
A:
- DDL 扫描聚簇索引并排序/构建新二级 B+ 树。
- 并发 DML 的相关变化写入 online DDL log，而非遗漏。
- 构建结束后回放 online log，校验唯一性并在 MDL 窗口内切换字典。
- 若 online log 超限、磁盘不足或出现重复键，DDL 可失败并清理临时对象。

## INSTANT算法
Q: INSTANT ADD COLUMN 为什么无需改写旧记录，读取旧行如何得到新列？
A:
1. 数据字典记录列版本、默认值和逻辑列位置等 instant metadata。
2. 旧物理记录没有新字段，读取时根据记录/表版本补出默认值。
3. 新写记录按新定义编码；引擎同时识别多版本记录布局。
4. 后续某些重建会把逻辑差异物化并重置内部负担；支持细节以 8.4 DDL 矩阵为准。

## 资源与边界
Q: 评估大表 DDL 需要计算哪些资源？
A:
- 新表/索引空间、临时排序空间、online log、redo/binlog、备份和副本额外空间。
- 全表读取与排序 I/O、Buffer Pool 污染、CPU、主库 p99 和复制 apply 能力。
- MDL 开始/收尾窗口、失败回滚/清理时间以及磁盘水位。
- 分区表、外键、全文/空间索引和 instant 历史都有额外限制。

## 验证与实践
Q: 如何安全执行生产大表 DDL？
A:
- 在相同版本副本用真实数据验证 `EXPLAIN ALTER TABLE`/支持矩阵、耗时、空间与复制影响。
- 显式指定 `ALGORITHM` 和 `LOCK`，设置 MDL 超时，低峰灰度并持续监控。
- 原生能力不满足时评估 gh-ost/pt-online-schema-change，但触发器/复制拓扑/外键各有风险。
- 准备停止和回退条件；“可以 cancel”不代表临时空间会瞬间释放。
