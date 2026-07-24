# Mini-Transaction、Latch 与生理 Redo

## 结构定位
Q: InnoDB mini-transaction（mtr）是什么，为什么它不是用户事务？
A:
- mtr 是一次短小的页/结构原子修改单元，负责持有 page latch、记录修改和提交 redo。
- 用户事务可包含成千上万个 mtr；mtr commit 释放 latch 并把 redo 放入日志系统，不代表 SQL 事务提交。
- mtr 保护 B-tree 页分裂、记录插入、页头更新等内部不变量；事务锁负责长时间逻辑隔离。
- 源码锚点：`mtr0mtr.h/.cc`、`mtr0log.*`、`log0log.*`。

## Memo与日志
Q: mtr memo stack 与 redo buffer 各保存什么？
A:
- memo 记录本次 mtr 获取的页 fix、S/X latch 和资源，提交时按规则释放。
- redo 部分编码页修改类型、space/page 和必要 payload；多个小记录组合描述本次物理结构变化。
- mtr 维护 start/end LSN，页的 `FIL_PAGE_LSN` 更新为相关修改日志位置。
- 某些可由其他方式恢复或临时对象修改可使用不同 log mode，不能把所有内存写都假设会产 redo。

## 修改算法
Q: 在叶子页插入一条记录时 mtr 怎样保证崩溃可恢复？
A:
1. 搜索阶段固定并 latch 目标页，必要时锁父/兄弟页。
2. 在 mtr 下修改记录链、page directory、页头；若分裂还修改多页关系。
3. 为每个必要变化追加 redo，提交 mtr 时获得连续 LSN 并发布日志。
4. 恢复重放这些记录，使页从旧一致状态前滚到新一致状态。

## 生理日志
Q: 为什么 InnoDB redo 常被称为 physiological，而非纯物理整页或逻辑 SQL？
A:
- 它通常定位具体 page，再记录“在页内插记录/改字段”等操作；比整页镜像小，比 SQL 重放确定。
- 恢复不需重新运行优化器或业务条件，避免数据状态变化导致不同执行路径。
- 某些首次修改/特定情况会记录更完整页信息，具体 redo 类型随版本演进。
- undo 负责事务级反向语义，redo 负责把已记录页变化可靠前滚，两者不可互换。

## 边界与验证
Q: “每改一行就写一条 redo”为什么错误？
A:
- 一次行修改会触及聚簇、多个二级索引、undo 页和内部元数据，产生多个 mtr/redo record。
- 一个 mtr 也可能修改多页；日志按页操作而非按 SQL 行一一对应。
- 通过 `Innodb_redo_log_current_lsn` 差值测 workload 日志率，比按行数猜更可靠。
- 源码分析要对应 8.4 redo 类型，旧版本博客中的 log block/file 结构可能已变化。
