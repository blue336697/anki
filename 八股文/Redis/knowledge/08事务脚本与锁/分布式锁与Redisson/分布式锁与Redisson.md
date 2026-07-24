# 分布式锁与Redisson

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-最小正确锁

Q: 单 Redis 实例的最小正确加锁和解锁为什么是 SET NX PX + 比较删除？

A:
- 加锁：`SET lock-key random-token NX PX ttl`，NX 防覆盖，PX 给持有者崩溃后的自动释放。
- token 必须每次持有唯一，不能只存线程名/固定业务值；它证明“删除者仍是当前锁持有者”。
- 解锁需原子比较 value 与 token 后 DEL；Redis 8.4+ 有 DELEX 条件删除，旧版本用 Lua。
- 直接 GET 后 DEL 有竞态：检查后锁过期并被别人获得，旧持有者再 DEL 会删新锁。

## 02-租约失效

Q: 即使 token 解锁正确，锁过期后旧持有者继续执行会发生什么？

A:
- 客户端 A 获锁后长 GC/网络停顿超过 TTL；锁过期，B 获得新锁并执行。
- A 恢复后虽然不会误删 B 的锁，但仍可能继续写下游资源，两个持有者业务操作重叠。
- 所以 Redis 锁只约束租约窗口，不能保证暂停进程恢复后自动失去外部写权限。
- 对不可覆盖资源要使用单调 fencing token，让下游拒绝小于已见最大 token 的旧请求。

## 03-Redisson结构

Q: Redisson 可重入锁为何常用 Hash，而不是简单 String？

A:
- 锁 key 的 Hash field 编码“客户端实例 ID + 线程 ID”，value 记录重入次数。
- Lua 原子判断：key 不存在则创建并设 TTL；同一 owner 再锁则 HINCRBY 并续 TTL；其他 owner 返回剩余 TTL。
- unlock 只有 owner field 匹配才减计数，降到 0 才删除并发布解锁通知。
- 具体 field 格式和脚本会随 Redisson 版本变化，应以所用版本源码验证，原理是 owner→reentry count。

## 04-Watchdog

Q: Redisson watchdog 怎样续期，在哪些情况下仍会失效？

A:
- 未显式指定 leaseTime 时，客户端登记定时续期任务，周期检查仍持有后延长 key TTL。
- 续期依赖客户端进程、调度线程、网络和 Redis 可用；长时间 STW、event loop 饥饿或分区会错过续期。
- 显式 leaseTime 通常不启用无限 watchdog 语义，到期就是到期。
- watchdog 降低正常长任务误过期概率，不消除租约与 fencing 问题。

## 05-高可用争议

Q: 主从/Sentinel/Cluster 下用 Redis 锁为什么仍可能出现双持有者？

A:
- 锁写入旧主后尚未复制，旧主故障，落后 replica 提升；新主没有该锁，第二客户端再次获得。
- WAIT 可降低风险但不是共识提交；Redlock 的假设和安全性需结合独立故障域、时钟和业务模型审慎评估。
- 若业务不能容忍任何双持有，应选带线性一致性租约/会话的协调系统，并配 fencing。
- Redis 锁更适合“允许极低概率重叠且业务操作幂等”的互斥优化，不应替代数据库唯一约束。
