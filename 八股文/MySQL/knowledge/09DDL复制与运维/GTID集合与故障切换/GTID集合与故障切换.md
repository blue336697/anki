# GTID 集合、自动定位与故障切换

## 结构定位
Q: GTID 的格式和核心价值是什么？
A:
- GTID 全局标识一个已提交事务，经典形式为 source UUID 加 transaction sequence number；8.4 还支持 tagged GTID。
- `gtid_executed` 表示实例已执行集合，`gtid_purged` 表示 binlog 已清理但历史需保留的集合。
- 自动定位按集合差异请求缺失事务，不再人工换算 file/position。
- GTID 提高拓扑切换可验证性，但不自动选主、防脑裂或保证数据最新。

## 集合语义
Q: 为什么故障切换要比较 GTID 集合包含关系，而不是只比数量？
A:
- 两实例 executed 数量相同也可能包含不同事务，已经分叉。
- 候选应包含其他可达副本的必要已提交集合，并确认无 errant transactions。
- `A ⊆ B` 表示 B 至少执行了 A 的全部事务；集合差异可精确定位缺口。
- purged 缺口若源端已无 binlog，需要从兼容备份/其他实例恢复，无法凭 GTID 生成数据。

## 自动定位
Q: Replica Auto Position 如何决定从哪里开始拉取？
A:
1. 副本向 source 发送自己的 executed GTID set。
2. source 从 binlog 找出自身拥有而副本未执行的事务。
3. 按 binlog 顺序发送缺失事务；副本遇到已执行 GTID 可跳过。
4. 若所需事务已 purge 且无其他来源，复制报错而不是静默跨过。

## 故障边界
Q: 什么是 errant transaction，它为什么危险？
A:
- 在副本本地执行、但不属于合法主库历史的 GTID 是 errant transaction。
- 提升该副本后，这些变更进入新主历史，其他节点可能冲突或数据语义分叉。
- 空事务注入 GTID 只能修集合，不能自动修复数据；必须先比较真实行差异。
- 严格只读、权限和编排 fencing 用于阻止副本意外写。

## 验证与实践
Q: GTID 切换前应检查什么？
A:
- 比较 executed/purged 集合、apply lag、复制错误和事务持久化配置。
- 选择最完整候选，停止旧主写入或实施 fencing，再等待必要事务追平。
- 提升后重指向其他副本并验证业务校验和；旧主未经重建/重新加入前不得恢复写。
- 定期演练缺 binlog、errant GTID 和网络分区，而非只测正常 switchover。
