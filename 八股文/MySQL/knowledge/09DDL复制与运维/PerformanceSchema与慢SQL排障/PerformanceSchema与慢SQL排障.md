# Performance Schema、Slow Log 与线上排障

## 结构定位
Q: Slow Log、Performance Schema、sys schema 各自提供什么视角？
A:
- Slow Log 记录超过阈值/指定条件的单次语句样本，可落文件或表。
- Performance Schema 在内存中采集 statement、stage、wait、lock、thread 和 I/O 事件，并按 digest 聚合。
- sys schema 是 P_S/I_S 上的可读视图，快速定位全表扫描、锁等待、冗余索引等。
- 它们反映数据库内部，仍需和 OS CPU、内存、网络、磁盘及应用 trace 关联。

## Digest结构
Q: statement digest 为什么适合找“总消耗最大的 SQL”，又有什么盲区？
A:
- Digest 归一化字面量，把同形 SQL 聚合，提供 count、总/平均/最大延迟、rows examined/sent、临时表等。
- 高频中等慢 SQL 的总资源可能远超偶发最慢 SQL，digest 能揭示这一点。
- 参数分布被合并，热点值与冷值计划差异可能被平均；历史表容量有限会淘汰。
- 动态 SQL 形状过多会造成 digest explosion，应在应用侧归一化。

## 排障算法
Q: MySQL 延迟突然升高时标准排查链是什么？
A:
1. 先确认影响范围、开始时间和资源饱和：CPU、I/O、连接、Threads_running。
2. 查当前线程/事务/锁等待，区分排队、MDL、row lock、fsync 和慢执行。
3. 用 digest/slow log 找 workload 变化，再对关键 SQL 看 ANALYZE、统计与数据量。
4. 选择止血：限流、kill blocker、回滚变更、切流；随后做根因与容量修复。

## 观测代价
Q: Performance Schema 是否“零开销，可以全开”？
A:
- 不是。instrument/consumer 越细、事件历史越长，CPU 和内存开销越大。
- 默认配置做了取舍；临时开启高粒度采集应设时间窗并验证容量。
- `INFORMATION_SCHEMA.INNODB_BUFFER_PAGE` 等全量页视图本身可很重，不应生产频繁扫描。
- 观测必须能回答问题，避免因诊断把过载放大。

## 验证与闭环
Q: 慢 SQL 优化完成后应怎样验收？
A:
- 同数据分布比较执行计划、actual rows/loops、逻辑/物理读、锁时间、临时表和 p95/p99。
- 同时检查写入成本、索引空间、redo/binlog、Buffer Pool 与复制延迟。
- 灰度发布并保留回退；监控业务正确性而不只看耗时。
- 把根因、触发条件、证据和防复发告警写入运行手册，形成可重复排障链。
