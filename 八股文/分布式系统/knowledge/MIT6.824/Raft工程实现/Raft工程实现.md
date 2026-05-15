# Raft 工程实现

## 结构卡
Q: MIT 6.824 Raft 实现中，Raft 结构体通常要维护哪些关键状态？
A:
- 持久化状态：currentTerm、votedFor、log，崩溃重启后必须恢复
- 易失状态：commitIndex、lastApplied，用于控制提交和应用到状态机
- leader 专属状态：nextIndex、matchIndex，用于跟踪每个 follower 的复制进度
- 角色状态：follower/candidate/leader，以及 election timer、heartbeat timer
- applyCh：Raft 层向应用层交付已提交日志或快照的通道

## 并发卡
Q: Raft 实现为什么容易出现死锁和数据竞争？如何控制？
A:
- Raft 同时有 ticker、RPC handler、RPC sender、apply goroutine 多个并发路径
- 共享状态如 term、log、commitIndex、role 必须在锁内读写
- 持锁期间不要阻塞发送 RPC、等待 channel 或执行耗时持久化，否则容易死锁或卡住心跳
- 常见做法是在锁内复制必要参数，释放锁后发 RPC，回来后再加锁校验 term/role 是否仍然有效
- 面试表达：Raft 工程难点不是只写论文规则，而是把锁粒度、RPC 并发和状态校验处理正确

## 投票实现卡
Q: RequestVote RPC handler 的关键判断顺序是什么？
A:
- 如果请求 term 小于当前 term，直接拒绝
- 如果请求 term 大于当前 term，更新 currentTerm，转 follower，并清空 votedFor
- 检查自己是否尚未投票或已投给该 candidate
- 检查 candidate 日志是否至少和自己一样新，比较 lastLogTerm 再比较 lastLogIndex
- 满足条件后记录 votedFor 并持久化，再返回投票成功

## 追加实现卡
Q: AppendEntries RPC handler 的关键逻辑是什么？
A:
- 如果 leader term 小于当前 term，拒绝
- 如果 term 合法，转 follower 并重置选举计时器
- 检查 prevLogIndex/prevLogTerm 是否匹配，不匹配则拒绝并返回冲突信息帮助 leader 快速回退
- 匹配后删除本地冲突日志，追加 leader 发来的新日志
- 根据 leaderCommit 推进本地 commitIndex，但不能超过本地最后一条日志

## 快速回退卡
Q: Lab 中的 XTerm、XIndex、XLen 快速回退优化解决什么问题？
A:
- 朴素回退每次只让 nextIndex 减 1，follower 落后很多时需要大量 RPC
- follower 拒绝 AppendEntries 时返回冲突 term、该 term 第一个 index 或自身日志长度
- leader 如果本地存在 XTerm，就把 nextIndex 跳到该 term 最后一个日志之后
- 如果 leader 不存在 XTerm，就跳到 XIndex；如果 follower 日志太短，就跳到 XLen
- 这样通常按 term 粒度回退，而不是按单条日志回退

## 持久化卡
Q: Raft 哪些状态必须持久化？什么时候持久化？
A:
- currentTerm、votedFor、log 必须持久化
- 快照相关的 lastIncludedIndex/lastIncludedTerm 也要与快照一起可靠保存
- 每次修改这些持久化状态后，在对外回复 RPC 成功或发送依赖该状态的 RPC 前完成持久化
- 否则节点崩溃重启后可能重复投票、丢日志或破坏安全性
- 面试边界：commitIndex 通常不需要持久化，重启后可由 leader 重新推进

## apply 卡
Q: 为什么 Raft 需要单独的 apply 循环？它要注意什么？
A:
- Raft 提交日志后，需要按 index 顺序把命令交给状态机执行
- apply 循环根据 commitIndex 和 lastApplied 推进，保证每条提交日志只应用一次
- 发送 ApplyMsg 时不要长时间持有 Raft 锁，否则应用层阻塞会反过来卡住 Raft RPC
- 安装快照时要处理 lastApplied、commitIndex 和快照边界，避免重复应用旧日志
- 面试表达：commit 是 Raft 层多数派结果，apply 是应用层状态真正变化，两者不能混为一谈

## 正确性审查卡
Q: Raft 工程实现有哪些高频坑？
A:
- 看到更大 term 没有立刻退回 follower，可能产生旧 leader 继续发号施令
- 投票没有持久化，崩溃后同一 term 可能投多票
- RPC 返回后不校验当前 term/role，旧响应可能污染新任期状态
- commitIndex 推进到未复制到多数派或非当前任期日志，可能破坏安全性
- 持锁发送 RPC 或持锁写 applyCh，容易死锁和心跳超时
