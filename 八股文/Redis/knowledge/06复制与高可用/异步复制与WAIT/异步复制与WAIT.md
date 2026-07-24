# 异步复制与WAIT

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-异步语义

Q: 主节点什么时候向客户端确认写成功，replica 此时一定写完了吗？

A:
- 普通写命令在主节点内存执行并排入复制/AOF传播后即可回复，不等待所有 replica 执行。
- replica 通过异步 TCP 流接收并顺序重放，因此存在 replication lag。
- 主节点回复后、命令到达 replica 前主故障，提升旧 replica 可能丢该写。
- Redis 复制默认是异步高可用机制，不是多数派提交协议。

## 02-ACK与offset

Q: replica ACK 的 offset 表示什么，不表示什么？

A:
- replica 周期发送 `REPLCONF ACK <offset>`，表示已处理到复制流的字节位置。
- 主节点据此统计 lag、支持 WAIT 和选择复制状态；offset 是字节流进度，不是业务事务号。
- ACK 通常不表示 replica 已把该数据 fsync 到稳定介质，也不保证它一定会成为故障后的新主。
- 网络缓冲、event loop 和 replica 负载都会让 ACK 落后。

## 03-WAIT语义

Q: WAIT numreplicas timeout 到底保证什么？

A:
- 当前连接先记住自己最后一次写对应的全局复制 offset；WAIT 请求至少 N 个 replica ACK 到该 offset。
- 已满足则立即返回，否则客户端阻塞到 ACK 数达标或超时，返回实际确认副本数。
- 它提高已确认写存在于多个内存副本的概率，但故障窗口、选主和持久化语义仍不能提供强一致。
- WAIT 本身不回滚已在主节点执行的写；超时后业务必须决定重试/对账，且重试要幂等。

## 04-min-replicas

Q: min-replicas-to-write 与 WAIT 有什么区别？

A:
- min-replicas 配置是主节点的全局写入闸门：健康且 lag 小于阈值的 replica 不足时拒绝写。
- WAIT 是客户端按操作主动等待已有写传播，粒度更细且返回实际确认数。
- min-replicas 只能减少孤主持续写的窗口，网络分区和检测延迟内仍可能有写入。
- 两者都不是 quorum 日志复制；可用性与数据安全需要明确取舍。

## 05-一致性结论

Q: 面试追问“Redis 主从能保证不丢数据吗”应怎样分层回答？

A:
- 先给结论：默认异步复制不能。
- 再列减损：足够 backlog 减少全量、WAIT/WAITAOF（版本支持）、min-replicas、AOF、选较新 replica。
- 再说仍有边界：ACK 非共识提交、选主与分区、持久化窗口、客户端超时重试造成重复。
- 最后给业务措施：幂等键、唯一约束、操作日志、补偿/对账；不能把关键账务真相只放缓存。
