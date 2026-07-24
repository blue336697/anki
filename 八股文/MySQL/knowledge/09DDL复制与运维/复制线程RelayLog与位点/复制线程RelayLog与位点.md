# 复制线程、Relay Log 与位点

## 结构定位
Q: MySQL 异步复制的数据流由哪些线程/组件组成？
A:
- Source dump thread 按位点/GTID 发送 binlog。
- Replica receiver（I/O）thread 接收事件写 relay log，并更新连接/接收元数据。
- Coordinator/SQL applier 读取 relay log，单线程或分发给 worker 应用事务。
- Relay log 是副本本地中继，隔离网络接收与 SQL 应用速度。

## 位点结构
Q: executed source position、relay log position 和 received transaction set 有何区别？
A:
- received 表示事件已到副本并写 relay log，不代表已执行。
- relay position 表示 applier 在本地 relay log 的进度。
- executed GTID set 表示已提交应用的事务集合，用于故障切换和追赶判断。
- `Seconds_Behind_Source` 是有限估计，网络断连、并行应用和无新事件时可能误导。

## 复制算法
Q: 一笔 ROW 事务从主库 commit 到副本可读经历什么？
A:
1. 主库事务完成 binlog group commit，事件进入可发送 binlog。
2. receiver 拉取并持久/写入 relay log，更新 received 状态。
3. coordinator 依据依赖分配 worker，worker 重放行事件并在副本 InnoDB 提交。
4. 只有 apply commit 后，普通副本查询才看到该事务；半同步 ACK 可能早于此时。

## 故障边界
Q: 复制 I/O 线程正常为什么副本仍可能延迟很大？
A:
- receiver 只证明网络接收，SQL/applier 可能被大事务、锁、缺主键、DDL、慢盘或 worker 冲突限制。
- ROW delete/update 无合适 key 时副本定位行昂贵。
- 副本同时承担查询/备份会争 Buffer Pool、CPU 与 I/O。
- 应分别测 receive lag、apply lag、relay log 增长和 worker 状态。

## 验证与治理
Q: 排查复制延迟的证据链是什么？
A:
- 查 replication_connection/applier_status_by_worker、relay/GTID 集合和具体 worker 错误。
- 解码阻塞位置附近 binlog，识别大事务、DDL、热点表和无主键操作。
- 对照副本 CPU、I/O、锁等待、redo fsync 与查询负载。
- 修复源端事务大小/主键/并行依赖，不能只增加 worker。
