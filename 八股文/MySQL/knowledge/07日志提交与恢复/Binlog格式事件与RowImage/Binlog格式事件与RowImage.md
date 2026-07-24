# Binlog 格式、事件与 Row Image

## 结构定位
Q: Binlog 与 InnoDB redo 的职责和层次有什么不同？
A:
- redo 是 InnoDB 页变化与 crash recovery 日志；binlog 是 MySQL Server 事务变更流，用于复制、PITR、审计/CDC。
- redo 循环复用，binlog 按文件顺序保留并轮转；binlog 与存储引擎无关层次更高。
- 同一事务两套日志必须通过提交协调保持一致，否则主库恢复与副本数据会分叉。
- binlog cache 按会话缓存事务事件，提交时写入公共 binlog。

## 格式结构
Q: STATEMENT、ROW、MIXED 三种格式分别记录什么？
A:
- STATEMENT 记录 SQL，体积可小但非确定函数、并发顺序和环境差异可能导致副本结果不同。
- ROW 记录行变更事件，重放确定性更高并利于 CDC，但批量更新可能事件量大。
- MIXED 由服务端在 statement/row 间选择，运维与 CDC 推理更复杂。
- 现代高可靠复制通常优先 ROW；具体默认与版本/发行版应查询 `binlog_format`。

## 事件链
Q: 一个 ROW 事务在 binlog 中怎样表达？
A:
1. GTID/anonymous transaction 与 BEGIN 类事件标识事务上下文。
2. Table_map_event 把 table id 映射到库表和列元数据。
3. Write/Update/Delete_rows_event 保存行镜像；update 通常含 before/after bitmap。
4. Xid_event 或提交事件结束事务，完整性用于恢复和两阶段提交判定。

## RowImage边界
Q: `binlog_row_image=MINIMAL` 的收益与风险是什么？
A:
- MINIMAL 只记录定位和实际改变所需列，减少 binlog、网络和副本 I/O。
- CDC 若希望拿到完整前后行，可能需要回查主库或维护状态；schema 演进和回查一致性变复杂。
- 唯一定位依赖主键/唯一键；无主键大表的 ROW 复制在副本查找行时可能很慢。
- FULL 更自包含但写放大更大，应按恢复、CDC 和带宽要求选择。

## 验证与实践
Q: 如何安全检查 binlog 中真正记录了什么？
A:
- 用 `mysqlbinlog --base64-output=DECODE-ROWS -vv` 离线解码副本文件，避免直接修改线上日志。
- 核对 GTID、table_map、行事件、提交边界和时间，不把 event timestamp 当精确业务提交时钟。
- 监控 binlog bytes、cache disk use、rotate/purge 与磁盘余量。
- 配置过短保留会破坏副本追赶和 PITR 窗口；清理前核对所有副本与备份位点。
