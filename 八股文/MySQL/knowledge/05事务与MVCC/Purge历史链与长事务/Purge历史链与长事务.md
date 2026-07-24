# Purge、History List 与长事务

## 结构定位
Q: Purge 线程清理什么，为什么提交后 undo 和 delete-mark 不能立即删除？
A:
- update undo 提交后进入 history list，旧 Read View 可能仍需它重建记录版本。
- DELETE 和索引 key 更新产生的 delete-mark 也必须等没有快照需要旧记录后才能物理移除。
- Purge 依据最老活跃 Read View 的边界消费 history，清理 undo、聚簇旧版本关联和二级索引条目。
- insert undo 通常只服务事务回滚，提交后可更快回收。

## 内部队列
Q: History list length 表示什么，为什么它不等于“undo 文件字节数”？
A:
- 它近似待 purge 的 undo log history 单元数量，反映积压趋势，不是行数或字节的直接映射。
- 单个事务大小差异很大，undo 页还存在已释放但表空间未截断的可重用空间。
- Purge worker 并行处理，但边界仍受最老视图限制；增加线程无法越过可见性安全线。
- undo tablespace truncate 是空间管理步骤，与逻辑 history 消费相关但不等价。

## 清理算法
Q: Purge 如何安全删除一个被标记的二级索引记录？
A:
1. 选择早于 purge view 的已提交 undo 记录。
2. 确认没有活跃 Read View 可能需要对应旧版本。
3. 定位聚簇/二级记录，取得必要 latch/锁，物理移除 delete-mark 条目或回收 undo。
4. 更新页与表空间结构并生成 redo；页空间先在 InnoDB 内复用，不必立刻归还 OS。

## 长事务故障链
Q: 一个只读长事务如何导致写库膨胀和查询变慢？
A:
- 它持有旧 Read View，使所有在其后提交的更新版本不能 purge。
- 写入持续产生 undo 与 delete-mark，history/undo 空间增长，二级索引扫描遇到更多旧条目。
- 读取旧行需要更长 undo 链，Buffer Pool 和 I/O 被历史页占用；备份/恢复也更重。
- 最终不是长事务本身写很多，而是它阻止全局垃圾回收前进。

## 验证与治理
Q: 发现 history list 持续增长时怎样处理？
A:
- 查 `INNODB_TRX` 最老事务及其线程、用户、来源；关注 Sleep in transaction 和长快照备份。
- 同时观察 DML 速率、purge worker、undo 空间与磁盘，确认是阻塞边界还是 purge 吞吐不足。
- 优先修复事务边界、分页批处理和连接池；必要时评估 kill 最老事务及其业务影响。
- kill 大写事务会触发漫长回滚，必须监控 rollback，而不是马上认为空间会下降。
