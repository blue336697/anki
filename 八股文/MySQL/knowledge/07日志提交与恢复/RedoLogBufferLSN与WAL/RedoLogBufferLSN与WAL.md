# Redo Log Buffer、LSN、文件与 WAL

## 结构定位
Q: Redo 从 mtr 生成到磁盘文件经历哪些层次？
A:
- mtr 生成 redo record 并预留全局日志序列空间；LSN 是单调递增的逻辑字节位置。
- redo 先进入内存 log buffer，后台 writer 写入 redo files，flusher 负责使目标 LSN 持久化。
- MySQL 8.0.30+ 以 `innodb_redo_log_capacity` 管理一组 `#ib_redo*` 文件，旧 `ib_logfile0/1` 固定模型已过时。
- checkpoint 推进后，早于安全边界的循环日志空间才能复用。

## 三种进度
Q: write_lsn、flushed_to_disk_lsn 与 checkpoint_lsn 的区别是什么？
A:
- write_lsn 表示 redo 已从内存写到 OS/文件层，但不一定跨掉电持久化。
- flushed LSN 表示已按 fsync 等语义持久化，可用于提交 durability 判断。
- checkpoint LSN 表示对应更早修改已反映在数据页安全状态，决定恢复起点和日志复用。
- 三者差距分别揭示 writer、fsync 和数据页刷脏瓶颈。

## WAL算法
Q: WAL 如何允许数据页延迟刷盘却保证提交持久性？
A:
1. 修改先在 Buffer Pool 完成，同时生成足够 redo。
2. 提交按 `innodb_flush_log_at_trx_commit` 要求把事务相关 redo 写/刷到持久介质。
3. 脏数据页可稍后批量刷盘，但刷某页前必须保证其 page LSN 对应 redo 已持久化。
4. 崩溃后从 checkpoint 重放 redo，把落后的数据页推进到一致状态。

## 容量与性能
Q: Redo capacity 太小或太大分别有什么后果？
A:
- 太小使 checkpoint age 很快逼近容量，迫使 aggressive flush，写吞吐和延迟抖动。
- 更大能吸收突发写并改善批量刷脏，但占磁盘并可能增加最坏 crash recovery 时间。
- 容量不能提高底层持续写带宽；长期 redo 生成率高于刷脏能力最终仍会受压。
- 以峰值 redo bytes/s、可接受突发窗口和恢复目标估算，再压测。

## 验证与误区
Q: 怎样判断事务慢在 redo write 还是 redo fsync？
A:
- 对比 current/write/flushed LSN、log waits、os log fsync、设备 fsync p99 和提交延迟。
- write 落后说明 writer/CPU/带宽问题，write 已前进但 flushed 落后更指向 fsync。
- `innodb_flush_log_at_trx_commit=2` 只改变 redo 持久化时点，不消除 binlog sync 与其他写。
- OS 报告写完成不一定等于断电持久，存储 cache 与 flush command 必须可信。
