# Stream消费组与PEL

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-消费组结构

Q: streamCG、streamConsumer 和 streamNACK 如何组成消费组？

A:
- `streamCG` 保存 last_id、entries_read、组级 PEL（rax）和 consumers（rax）。
- `streamConsumer` 保存 name、seen/active time 和该消费者自己的 PEL；它与组 PEL 共享同一个 NACK 值。
- `streamNACK` 保存最近投递时间、投递次数和当前 consumer 指针。
- 一条未 ACK 消息在组 PEL 可全局查，在 consumer PEL 可按消费者查，不复制两份完整消息。

## 02-XREADGROUP

Q: XREADGROUP 使用 `>` 读取新消息时怎样写入 PEL？

A:
- 从 group.last_id 之后取尚未投递给该组的新消息，分配给请求 consumer。
- 为每条消息创建/更新 NACK，同时插入组 PEL 和 consumer PEL，记录 delivery_time/count。
- 推进 group.last_id/entries_read 后返回消息；消息正文仍在 Stream 主 rax/listpack 中。
- NOACK 可跳过 PEL，但失去故障恢复与确认能力，语义更接近至多一次。

## 03-ACK与删除

Q: XACK、XDEL 和 trim 的关系为什么容易误解？

A:
- XACK 只把消息 ID 从消费组/消费者 PEL 移除，不删除 Stream 正文。
- XDEL 删除正文，但某组 PEL 仍可能保留该 ID 的 pending 元数据；之后读 pending 可能得到正文已不存在的情况。
- XTRIM 按 MAXLEN/MINID 裁剪日志，也不等价于替所有组 ACK。
- 保留策略必须同时考虑正文长度、最大处理时长和 PEL 清理。

## 04-Claim恢复

Q: XPENDING、XCLAIM/XAUTOCLAIM 怎样恢复宕机消费者的消息？

A:
- XPENDING 查看 pending ID、owner、idle 和 delivery count；监控 idle 过长的任务。
- XCLAIM 在满足 min-idle-time 后把指定 ID owner 改给新 consumer，更新时间并增加投递次数。
- XAUTOCLAIM 从游标自动扫描并转移超时 PEL，适合后台恢复循环。
- claim 会造成重复处理：旧消费者可能只是慢并在恢复后继续，因此业务 handler 必须幂等。

## 05-可靠性边界

Q: Stream 为什么通常只能实现 at-least-once，而不能自动 exactly-once？

A:
- 消费者处理业务成功但 XACK 前崩溃，消息会被再次 claim；先 ACK 再处理则崩溃会丢业务效果。
- Redis 无法与外部数据库提交组成原子事务，重复/不确定状态不可避免。
- 使用 message ID/业务唯一键建立 inbox 表或幂等状态，事务内写业务结果与消费记录，再 ACK。
- AOF/复制策略还决定 Stream 自身故障后的 RPO，PEL 并不超越 Redis 持久化保证。
