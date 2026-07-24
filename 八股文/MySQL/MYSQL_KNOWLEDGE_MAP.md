# MySQL 8.4 源码机制级知识地图

> 主基线：MySQL 8.4 LTS / InnoDB。  
> `knowledge/` 是唯一知识源；原 19 个宽主题归档在 `knowledge_legacy/`，不参与构建。  
> 面试中常见的 MySQL 5.7、8.0 旧说法在卡片中按版本显式纠正。

## 制卡标准

每个主题固定 5 张连续追问卡：

1. 结构定位：对象属于 Server、InnoDB、操作系统中的哪一层。
2. 字段与布局：核心结构体、页/记录字节、链表、位图或状态字段。
3. 执行算法：沿真实调用或状态转换说明步骤。
4. 复杂度与边界：I/O、锁、空间、阈值和版本差异。
5. 故障验证：使用 EXPLAIN ANALYZE、Performance Schema、InnoDB 指标或恢复演练验证。

## 全量覆盖

| 模块 | 主题 | 卡片 |
|---|---:|---:|
| 01 服务层与执行链 | 5 | 25 |
| 02 表空间、页与记录 | 7 | 35 |
| 03 B+ 树索引算法 | 7 | 35 |
| 04 Buffer Pool 与 I/O | 6 | 30 |
| 05 事务与 MVCC | 6 | 30 |
| 06 锁与并发 | 6 | 30 |
| 07 日志、提交与恢复 | 7 | 35 |
| 08 优化器与执行器 | 8 | 40 |
| 09 DDL、复制与运维 | 8 | 40 |
| **合计** | **60** | **300** |

## 重点源码锚点

- Server/执行器：`sql/sql_class.h`、`sql/handler.h`、`sql/join_optimizer/`、`sql/iterators/`
- 页与记录：`storage/innobase/include/fil0fil.h`、`page0page.h`、`rem0rec.h`
- B+ 树：`btr0cur.*`、`btr0pcur.*`、`page0cur.*`
- Buffer Pool：`buf0buf.*`、`buf0lru.*`、`buf0flu.*`
- 事务/MVCC：`trx0trx.*`、`trx0rec.*`、`read0read.*`、`row0vers.*`
- 锁：`lock0lock.*`、`lock0priv.h`
- Redo/恢复：`mtr0mtr.*`、`log0log.*`、`recv0recv.*`
- 数据字典/DDL：`sql/dd/`、`row0mysql.*`、`handler0alter.*`

## 官方事实源

- MySQL 8.4 Reference Manual：`https://dev.mysql.com/doc/refman/8.4/en/`
- InnoDB locking/transaction model：`https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-transaction-model.html`
- InnoDB redo log：`https://dev.mysql.com/doc/refman/8.4/en/innodb-redo-log.html`
- Online DDL operations：`https://dev.mysql.com/doc/refman/8.4/en/innodb-online-ddl-operations.html`
- Replication：`https://dev.mysql.com/doc/refman/8.4/en/replication.html`
- MySQL Server source：`https://github.com/mysql/mysql-server`

## 版本纠错重点

- MySQL 8 已移除 Query Cache，Prepared Statement 与 Buffer Pool 都不是查询结果缓存。
- MySQL 8 使用事务数据字典，不再以 `.frm` 作为表定义事实源。
- Redo 在 8.0.30+ 使用动态 redo capacity 与 `#ib_redo*` 文件，不能继续只背 `ib_logfile0/1`。
- MySQL 8.4 doublewrite 使用独立 `#ib_*.dblwr` 文件，早期 system tablespace 固定区域模型不是当前实现。
- INSTANT、INPLACE、COPY 是 DDL 算法；INPLACE 不保证不重建，online 不保证完全无 MDL。
- 半同步 ACK 通常只表示副本已接收/记录，不代表副本已应用，更不等于共识提交。

## 构建

```powershell
cd D:\claudeProjects\anki\八股文\MySQL
python .\build_mysql_all.py
```

输出：`D:\claudeProjects\anki\牌组\八股文\MySQL\MySQL八股文.apkg`

同步 JSON：

```powershell
python .\export_mysql_notes_json.py
```

两个 Python 文件只解析 Markdown，不包含知识正文。
