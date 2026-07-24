# Binlog Group Commit 与持久性矩阵

## 结构定位
Q: Binlog group commit 为什么能减少 fsync，又不让事务彼此混成一个事务？
A:
- 多个待提交事务进入同一 commit group，依次经过 flush、sync、commit stage。
- leader 执行或协调公共 binlog write/fsync，followers 共享该次昂贵持久化。
- 每个事务仍有独立事件边界、GTID/XID 和成功状态；共享的是批次 I/O。
- stage 队列与 InnoDB prepare/commit 顺序还用于维护复制可并行性/提交顺序元数据。

## 阶段结构
Q: flush、sync、commit 三阶段分别做什么？
A:
- flush stage 把各事务 binlog cache 依序写入 binlog 文件缓冲/文件。
- sync stage 按 `sync_binlog` 和组策略执行持久化。
- commit stage 调用存储引擎 commit，并按依赖顺序唤醒会话。
- 具体锁与优化随版本变化，面试重点是共享 I/O 和保持事务顺序约束。

## 组提交算法
Q: 高并发提交时一个 group 怎样形成？
A:
1. 首个线程成为 leader，后续在窗口内到达的事务加入队列。
2. leader 收集已 prepare 事务，批量写 binlog。
3. 整组一次或少数 sync，随后批量 engine commit。
4. 各会话获得自己的提交结果；`binlog_group_commit_sync_delay` 可人为扩大组但增加延迟。

## 持久性矩阵
Q: redo flush=1/2/0 与 sync_binlog=1/0 的风险怎样理解？
A:
- redo=1 每提交刷 redo；2 通常每提交写 OS cache、后台约每秒刷；0 连写也主要由后台周期完成。
- sync_binlog=1 每组提交刷 binlog；0 依赖 OS；N>1 每 N 组同步。
- 弱化任一侧都可能在 OS/掉电时丢最近事务或造成恢复边界变化，具体损失窗口不是精确“一秒”保证。
- 主库双日志一致还依赖协调协议，不能只单看一个参数。

## 验证与权衡
Q: 如何在性能和持久性之间做可解释选择？
A:
- 先由 RPO 定义 mysqld crash、OS crash、主机掉电各允许丢多少，再选择配置，不能先追 TPS。
- 使用断电语义真实的存储做故障注入，测吞吐、p99、丢失窗口和恢复一致性。
- 半同步/副本可降低单机丢失风险但不修复本地不可靠 fsync，也不等于副本已应用。
- 人为 delay 扩大 group 会直接增加提交延迟，应看整体吞吐与尾延迟。
