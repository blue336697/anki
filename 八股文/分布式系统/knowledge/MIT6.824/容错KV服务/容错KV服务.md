# 容错 KV 服务

## 架构卡
Q: MIT 6.824 Lab3 的 fault-tolerant KV 服务整体架构是什么？
A:
- 每个 KV server 内部包含应用层 KV 状态机和 Raft 实例
- Client/Clerk 把 Get/Put/Append 请求发给它认为的 leader
- leader 把请求封装成 Op 交给 Raft Start，日志提交后应用到 KV map
- 所有副本按 Raft 提交顺序执行同一串 Op，因此状态保持一致
- 如果 leader 失败，客户端重试到新 leader，系统继续提供服务

## 请求去重卡
Q: KV 服务为什么需要 clientId + requestSeq 去重？
A:
- 客户端 RPC 超时可能是 leader 已执行但响应丢失
- 客户端会重试同一个请求，如果服务端不去重，Append 或 Put 可能重复执行
- Clerk 给每个请求带唯一递增序号，服务端保存每个 client 最新已执行 seq 和结果
- 如果收到旧 seq 或重复 seq，直接返回缓存结果，不再次修改状态机
- 面试重点：Raft 保证日志一致，不保证客户端重试语义幂等，去重要在应用层做

## 等待通知卡
Q: KV server 如何知道某个 Start 提交的日志就是自己的请求？
A:
- server 调用 Raft Start 后拿到 log index、term 和 isLeader
- 如果是 leader，就为该 index 建立等待 channel
- apply loop 收到 ApplyMsg 后执行 Op，并通知对应 index 的等待者
- 等待者被唤醒后还要校验返回的 clientId/requestSeq 或 term，防止该 index 被新 leader 覆盖成别的请求
- 超时未等到提交时返回 ErrWrongLeader 或超时，让客户端换 server 重试

## 读路径卡
Q: Lab3 中 Get 请求为什么也通常要走 Raft？
A:
- 如果 follower 直接读本地 map，可能读到旧状态
- 即使 leader 自己读，也要确认自己仍然是当前合法 leader，否则网络分区后的旧 leader 可能返回过期值
- 把 Get 也作为日志命令提交，可以让读请求在线性一致顺序中占据一个位置
- 代价是读性能较低，但实现简单且正确性强
- 面试表达：强一致 KV 中读不是天然便宜，读路径也必须处理 leader 权威和线性化点

## 快照卡
Q: KV 服务为什么要做 snapshot？快照里应该保存什么？
A:
- Raft 日志无限增长会导致内存和持久化成本上升
- 当 Raft state size 超过阈值，KV 层把当前状态序列化成 snapshot，并通知 Raft 截断旧日志
- snapshot 至少包含 KV map 和客户端去重表
- 如果只保存 KV map，不保存去重表，重启或安装快照后可能重复执行旧请求
- 面试亮点：快照保存的是“应用状态 + 幂等语义状态”，不是只保存数据本身

## 正确性审查卡
Q: 容错 KV 服务有哪些常见错误说法？
A:
- “用了 Raft 就天然不会重复执行请求”：错误。客户端重试导致的重复语义要靠应用去重
- “Get 不修改状态，所以不用进 Raft”：不一定。线性一致读必须确认 leader 权威或进入日志
- “apply 了就可以直接唤醒所有请求”：不严谨。要按 log index 和请求身份匹配
- “snapshot 只保存 KV map”：不完整。还要保存去重表等影响语义的元数据
- “超时就是请求没提交”：错误。超时是未知状态，客户端只能带同一 requestId 重试
