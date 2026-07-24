# WATCH乐观锁

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-双向索引

Q: WATCH 为什么同时维护 client.watched_keys 和 db.watched_keys？

A:
- `client.watched_keys` 列出该客户端观察的 key，便于 UNWATCH、EXEC 或断开时一次清理。
- `db.watched_keys` 从 key 映射到观察它的客户端/`watchedKey` 列表，写 key 时可直接定位受影响客户端。
- Redis 7.4 的 watchedKey 同时链接两侧，避免移除时再做全表搜索。
- 这是典型双向索引：多付内存，换取修改 key 和释放客户端都能高效处理。

## 02-脏标记

Q: 被 WATCH 的 key 修改后，Redis 怎样让 EXEC 失败？

A:
- 修改路径调用 `touchWatchedKey`，查 `db.watched_keys[key]`，把相关客户端标记 `CLIENT_DIRTY_CAS`。
- 标脏后可解除其 watch 链接，避免同一客户端后续每次修改都重复扫描。
- EXEC 发现 DIRTY_CAS 返回 null array，表示乐观条件不成立；与 DIRTY_EXEC 的 EXECABORT 不同。
- 过期、删除、覆盖、FLUSHDB/SWAPDB 等也需触发相应失效语义。

## 03-过期语义

Q: WATCH 的 key 在等待期间过期，EXEC 会发生什么？

A:
- Redis 在 EXEC 前调用 `isWatchedKeyExpired` 检查观察后的过期变化，并设置 DIRTY_CAS。
- WATCH 时已经过期的状态会被记录，避免把“观察前就不存在”错误当成观察后修改。
- 从 Redis 6.0.9 起，过期可使 WATCH 事务中止；回答旧行为要标版本。
- TTL 竞争逻辑不能仅靠先 GET 再 MULTI，必须 WATCH 在读取之前建立观察。

## 04-CAS重试

Q: 用 WATCH 实现扣减库存时，正确重试循环是什么？

A:
1. WATCH key，再 GET 当前值并校验库存。
2. MULTI，排队 DECRBY/写关联状态，EXEC。
3. EXEC 返回 null 表示冲突：退避后从 WATCH 重新读取，不能复用旧值盲重试。
4. EXEC 成功仍要检查每个子命令结果。
- 高竞争下大量失败重试浪费 RTT 和 CPU，Lua 通常更适合单实例原子读改写。

## 05-WATCH边界

Q: WATCH 为什么不能解决数据库和 Redis 的双写一致性？

A:
- WATCH 只观察同一 Redis 实例/数据库中的 key 版本变化，不覆盖 MySQL 提交、消息发送或其他分片。
- 客户端在数据库提交后、Redis EXEC 前崩溃仍会产生不一致。
- Cluster 多 key WATCH/MULTI 还要求同槽，迁移与重定向需客户端正确处理。
- 跨系统用事务消息/outbox、CDC、幂等消费和最终一致性；WATCH 只能作为 Redis 内 CAS。
