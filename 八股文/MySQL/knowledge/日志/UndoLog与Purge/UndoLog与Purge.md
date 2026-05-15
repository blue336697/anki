# UndoLog与Purge

## Undo卡
Q: InnoDB undo log 解决什么问题？
A:
- undo log 记录逻辑上的反向修改，用于事务回滚
- MVCC 需要通过 undo 版本链读取历史版本
- insert、delete、update 会产生不同类型 undo 记录
- undo 与隐藏列 `trx_id`、`roll_pointer` 一起支撑多版本可见性
- 面试表达：undo 同时服务原子性和 MVCC，不只是回滚日志

## 版本链卡
Q: undo log 如何支撑 MVCC 版本链？
A:
- 聚簇索引记录中保存最近修改事务 ID 和 roll pointer
- roll pointer 指向上一版本对应的 undo 记录
- 一条记录多次更新会形成版本链
- ReadView 判断当前版本不可见时，会沿版本链查找可见旧版本
- 长事务会阻止旧版本清理，导致 undo 膨胀

## Purge卡
Q: purge 线程在 InnoDB 中做什么？
A:
- purge 清理不再被任何 ReadView 需要的旧版本
- 删除操作通常先 delete mark，后续由 purge 真正清理记录
- 长事务会让 purge 无法推进，history list length 增长
- undo 表空间和回滚段也与 purge 进度相关
- 线上长事务可能导致空间膨胀和查询变慢

## 正确性审查卡
Q: undo 和 purge 有哪些常见误区？
A:
- “undo 只用于 rollback”：错误。MVCC 也依赖 undo
- “事务提交后 undo 立即删除”：不一定。仍可能被其他 ReadView 需要
- “delete 立刻物理删除记录”：通常不是，会先标记删除
- “长事务只占连接”：错误。还可能拖住 purge 和历史版本清理
- “purge 慢只影响磁盘空间”：不完整。版本链变长也会影响读性能
