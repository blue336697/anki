# Flush List、脏页 LSN 与 Checkpoint

## 结构定位
Q: InnoDB 为什么需要 flush list，它按什么顺序组织脏页？
A:
- 页第一次从干净变脏时记录 oldest modification LSN，并加入 flush list；链表按 oldest LSN 近似排序。
- checkpoint 要推进到某 LSN，必须确保所有 oldest LSN 更早的脏页已经安全落盘。
- 同一页后续可多次修改并产生更高 page LSN，但决定最早恢复依赖的是第一次未落盘修改。
- LRU flush 为腾 frame，flush-list flush 为推进 checkpoint，目标不同。

## 三个LSN
Q: current LSN、flushed redo LSN 和 checkpoint LSN 分别约束什么？
A:
- current LSN 表示已经分配/生成到的 redo 位置。
- flushed redo LSN 表示 redo 已持久化到存储的位置，提交持久性受它影响。
- checkpoint LSN 表示该点之前对应的数据页修改已可由磁盘页承接，恢复可从此处开始扫描 redo。
- WAL 要求数据页落盘前，其 page LSN 对应 redo 必须先持久化。

## 自适应刷脏
Q: InnoDB 如何决定后台刷多少脏页？
A:
1. page cleaner 综合脏页比例、redo 生成速度、checkpoint age 和 I/O capacity 计算压力。
2. 当 redo 空间逼近容量边界时加速 flush，避免日志循环覆盖恢复仍需要的记录。
3. LRU 缺 free page 时前台线程也可能同步参与或等待刷页，形成延迟尖刺。
4. `innodb_io_capacity/max` 是设备能力提示，不是越大越好；过高会与前台查询争 I/O。

## 代价与故障
Q: “脏页多一点只是内存占用”为什么错误？
A:
- 脏页对应未 checkpoint 的 redo，过多会推高 checkpoint age 和崩溃恢复时间。
- 突发刷脏占用 doublewrite、数据盘队列和 CPU，前台可能等待 free page。
- redo 容量太小或设备写入慢会触发 aggressive flushing，吞吐呈锯齿。
- 脏页比例低也不保证健康，若热点页反复修改，redo 速率仍可能很高。

## 验证与治理
Q: 排查 checkpoint pressure 应看哪些指标？
A:
- 看 `Innodb_redo_log_current_lsn - checkpoint_lsn`、redo capacity、脏页数、pending flush、fsync 与数据盘 latency。
- 关联业务写入速率、批量任务、Buffer Pool free pages 和前台等待，确认是日志容量还是设备吞吐。
- 调大 redo capacity 可吸收波动并减少强制刷脏，但会增加最坏恢复窗口；不能替代足够磁盘带宽。
- 调整 I/O capacity 前用设备稳态随机写/顺序写能力校准，并观察读请求是否被刷脏挤压。
