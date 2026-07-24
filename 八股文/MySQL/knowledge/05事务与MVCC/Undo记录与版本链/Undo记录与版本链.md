# Undo 记录、Roll Pointer 与版本链

## 结构定位
Q: InnoDB undo log 的两类核心用途是什么？
A:
- 回滚：记录如何撤销当前事务的 INSERT/UPDATE/DELETE，使语句失败或 ROLLBACK 能恢复旧值。
- MVCC：update undo 保存旧版本信息，其他事务可沿 `DB_ROLL_PTR` 构造可见历史记录。
- insert undo 只对本事务回滚需要，提交后可更早回收；update undo 还可能被旧 Read View 需要。
- undo 自身也受 redo 保护，因为崩溃恢复必须可靠提交或回滚事务。

## 记录结构
Q: 聚簇记录如何通过 undo 形成版本链？
A:
- 当前聚簇记录保存最后修改事务的 `DB_TRX_ID` 和指向 undo 的 `DB_ROLL_PTR`。
- undo 记录保存前一版本的事务信息、被修改列旧值、操作类型以及继续回溯所需指针。
- 读取旧版本时在内存副本上反向应用 undo，逐级恢复；磁盘上并不存在一棵独立“版本链表表”。
- 二级索引版本核验最终依赖聚簇记录和 undo，可见性与物理索引条目清理由 purge 协调。

## 更新算法
Q: UPDATE 一行时 undo/redo/记录版本怎样协作？
A:
1. 取得必要记录锁，创建 update undo，保存旧值及回滚信息。
2. 修改聚簇记录的业务列、`DB_TRX_ID` 和 `DB_ROLL_PTR`；索引列变化还会 delete-mark 旧二级 key 并插新 key。
3. 所有页修改由 mtr 生成 redo；undo 页的修改也写 redo。
4. 回滚时读取 undo 逆操作；提交后 undo 进入 history，等待所有相关 Read View 结束再 purge。

## 空间与复杂度
Q: 读取一个很老的快照为什么可能突然变慢？
A:
- 当前版本不可见时要沿 undo 链逐版本判断，成本与该行在快照后被更新次数相关，不只是 B+ 树 O(logN)。
- undo 页若不在 Buffer Pool 会产生额外 I/O；长事务让许多记录都积累长链。
- purge 受最老 Read View 限制，单个遗忘事务可让全实例历史增长。
- 高频更新热点行既有锁竞争，也有长版本链和 redo/undo 放大。

## 验证与误区
Q: “undo log 就是 SQL 的反向语句”为什么不准确？
A:
- undo 是 InnoDB 内部物理/逻辑混合记录，包含记录定位、旧列和事务元数据，不是可直接执行的 SQL 文本。
- 回滚还需维护所有相关索引、锁和事务状态；并非简单执行一条反向 UPDATE。
- 观察 `History list length`、undo tablespace、长事务和 purge metrics 判断积压。
- 不要通过手工删除 undo 文件清空间；应结束阻塞 purge 的事务并按官方方式管理 undo tablespace。
