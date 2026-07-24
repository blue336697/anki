# MySQL 源码机制级重写报告

## 结果

- 基线：MySQL 8.4 LTS / InnoDB
- 唯一知识源：`knowledge/`
- 旧版归档：`knowledge_legacy/`
- 主题：60
- 卡片：300
- 每主题：5 张连续追问卡
- APKG：`D:\claudeProjects\anki\牌组\八股文\MySQL\MySQL八股文.apkg`

## 深度变化

- 索引不再只讲“B+ 树与最左前缀”，而是覆盖 FIL/INDEX 页布局、record header、page directory、persistent cursor、分裂/合并、聚簇与二级记录、二级 MVCC、ICP/MRR/BKA。
- 事务不再只背 ACID，而是覆盖 `trx_t` 状态、undo record、roll pointer、Read View 四边界、版本回溯、current read、purge 与长事务故障链。
- 锁不再只列类型，而是覆盖 `lock_sys`、page/heap_no 位图、模式组合、SQL 扫描锁范围、等待图、victim 和 MDL 队列。
- 日志不再只背 redo/undo/binlog 区别，而是覆盖 mtr、LSN 进度、WAL、checkpoint、crash recovery、内部 XA、group commit、PITR 与 CDC。
- SQL 优化不再停留在 EXPLAIN 字段，而是覆盖 rewrite/semijoin、持久统计、histogram、成本模型、join iterator、filesort、TempTable 与 ANALYZE。
- 高可用覆盖 receiver/relay/applier、GTID 集合、半同步 ACK 边界、writeset 并行复制、备份恢复和故障切换 fencing。

## 工作流

1. 直接编辑 `knowledge/<模块>/<主题>/<主题>.md`。
2. `build_mysql_all.py` 从 Markdown 构建 APKG。
3. `export_mysql_notes_json.py` 从同一批 Markdown生成 Anki 同步 JSON。
4. Python 不保存知识正文，避免双重事实源。

## 自动质量检查

- Markdown：60 份
- 二级卡片分区：300，全部每文件 5 张
- 问题：300 个，唯一问题 300 个
- 答案有效字符：最短 120，中位数 166
- Q/A 缺失、代码围栏未闭合：0
- APKG notes/cards：300/300
- 重复 GUID：0
- MySQL/源码机制级/MySQL-8.4 标签缺失：0

## Anki 同步

- 已先新增并核对 300 张带 `源码机制级`、`MySQL-8.4` 标签的新卡。
- 旧构建卡删除预演与正式删除均精确命中 76 notes / 76 cards，未找到项为 0。
- 两张用户手工笔记“MYSQL中的所有日志类型”“成本计算”完整保留。
- 最终 `八股文::MySQL` 共 302 张：深度版 300 张，手工卡 2 张。
- MCP 同步卡放在 `八股文::MySQL` 根牌组，以模块/主题标签区分；APKG 保留 60 个叶子牌组层级。
- 旧卡与新卡结构不同，本次未迁移旧卡复习进度。
