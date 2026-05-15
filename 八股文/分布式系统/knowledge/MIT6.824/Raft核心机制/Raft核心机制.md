# Raft 核心机制

## 概念卡
Q: Raft 要解决什么问题？它为什么比 Paxos 更适合工程实现和面试表达？
A:
- Raft 解决的是复制状态机的一致性问题：多节点在故障和网络异常下，对同一串日志达成一致
- 它把共识拆成 leader 选举、日志复制、安全性约束、成员变更和日志压缩等相对清晰的模块
- Leader 负责接收客户端请求、追加日志、复制到多数派、提交后通知状态机执行
- 相比 Paxos，Raft 更强调可理解性，工程实现路径和调试边界更清楚
- 面试一句话：Raft 的核心是“强 leader + 多数派复制 + 日志匹配 + 选举限制”，用这些规则保证已提交日志不会丢

## 角色卡
Q: Raft 中 follower、candidate、leader 三种角色如何转换？
A:
- follower 被动接收 leader 心跳和日志复制请求
- follower 在 election timeout 内没有收到有效 leader 消息，就增加 term，转为 candidate 并发起 RequestVote
- candidate 给自己投票，并向其他节点请求投票；获得多数派后成为 leader
- leader 周期性发送 AppendEntries 心跳，维持权威并阻止新选举
- 节点看到更大 term 的 RPC 或响应时，必须更新 term 并退回 follower

## 选举卡
Q: Raft 过半选举机制为什么能避免同一任期出现两个 leader？
A:
- 每个节点在同一 term 最多投一票，投票信息需要持久化
- 成为 leader 必须获得多数派投票
- 任意两个多数派集合必然有交集，如果同一 term 出现两个 leader，交集节点就必须投两票，违反规则
- 随机 election timeout 可以降低多个 candidate 同时发起选举导致平票的概率
- 面试重点：过半不是为了“人多”，而是利用多数派交集建立安全性

## 日志复制卡
Q: Raft 的 AppendEntries 如何保证 follower 日志最终与 leader 一致？
A:
- leader 为每个 follower 维护 nextIndex 和 matchIndex
- AppendEntries 带上 prevLogIndex 和 prevLogTerm，follower 只有在对应位置日志匹配时才接受新日志
- 如果不匹配，follower 拒绝请求，leader 回退 nextIndex 后重试
- 一旦找到共同前缀，follower 会删除冲突日志并追加 leader 的日志
- 这个机制保证：如果两个日志在同一 index 和 term 相同，那么它们之前的所有日志也相同

## 提交卡
Q: Raft 中日志什么时候算 committed？为什么 leader 不能随便提交旧任期日志？
A:
- leader 看到某条当前任期日志被复制到多数派后，可以把 commitIndex 推进到该日志位置
- follower 通过 AppendEntries 中的 leaderCommit 更新自己的 commitIndex
- Raft 限制 leader 只能通过“当前任期日志复制到多数派”来推进提交，再间接提交之前旧任期日志
- 这样可以避免某些旧任期日志虽然存在于多数派，但后续被更高任期 leader 覆盖的安全性问题
- 面试亮点：Raft 的提交规则不仅看多数派，还看日志所属 term

## 选举限制卡
Q: Raft 为什么要求候选人的日志必须“足够新”才能拿到投票？
A:
- RequestVote 携带 lastLogIndex 和 lastLogTerm
- 投票方只会投给日志至少和自己一样新的候选人
- 比较规则先看 lastLogTerm，term 更大说明日志更新；term 相同再看 lastLogIndex
- 这保证包含已提交日志的多数派节点不会把票投给缺少这些日志的候选人
- 面试表达：选举限制把“谁能当 leader”和“谁拥有足够完整的日志”绑定起来，防止已提交日志被新 leader 丢掉

## 快照卡
Q: Raft 为什么需要快照？InstallSnapshot 解决什么问题？
A:
- 日志会持续增长，如果只靠重放日志恢复，磁盘占用和重启时间都会越来越大
- 应用在某个 index 做状态机快照，Raft 可以丢弃该 index 之前的日志
- 如果 follower 落后太多，leader 已经没有它需要的旧日志，就通过 InstallSnapshot 发送快照
- follower 安装快照后更新 lastIncludedIndex/Term，并让状态机恢复到快照状态
- 面试边界：快照内容属于应用状态，Raft 只管理快照对应的日志边界和传输安装

## 线性一致卡
Q: 基于 Raft 的 KV 服务如何提供线性一致读写？
A:
- 写请求必须通过 leader 追加日志，复制到多数派并 apply 后再返回
- 对读请求，最保守做法是也走 Raft 日志，把读当作一条命令线性化
- 优化读可以使用 ReadIndex 或 leader lease，但必须确认当前 leader 仍然拥有多数派认可的领导权
- 客户端重试要带唯一请求 ID，服务端去重，避免超时后重复 Put/Append
- 面试注意：Raft 保证日志一致，不自动保证应用层去重和读路径线性化，这些要由 KV 层补齐

## 正确性审查卡
Q: Raft 面试中哪些说法容易不严谨？
A:
- “多数派复制就一定提交”：不完整。Raft leader 直接推进提交还要求当前任期日志复制到多数派
- “leader 心跳只是保活”：不完整。AppendEntries 同时承担日志一致性检查、提交推进和权威传播
- “选举只看 term”：错误。投票还要检查候选人日志是否足够新
- “快照是 Raft 自己理解业务状态”：错误。快照内容由应用生成和安装，Raft 只维护日志边界
- “读请求不需要经过 Raft”：不一定。要保证线性一致读，必须确认 leader 权威或走日志
