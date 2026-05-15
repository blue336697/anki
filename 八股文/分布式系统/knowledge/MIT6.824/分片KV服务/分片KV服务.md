# 分片 KV 服务

## 架构卡
Q: MIT 6.824 Lab4 ShardKV 在 Lab3 基础上多了什么？
A:
- Lab3 是一个 Raft 组复制整份 KV 数据
- Lab4 把 key 空间切成多个 shard，不同 shard 可由不同 replica group 负责
- shardctrler 维护配置：每个 shard 属于哪个 group，以及 group 的 server 列表
- 每个 group 内部仍用 Raft 保证本组状态一致
- 难点从“单组复制”升级为“配置变更 + shard 迁移 + 跨组一致性”

## ShardCtrler 卡
Q: shardctrler 的 Join、Leave、Move、Query 分别做什么？
A:
- Join：新增 replica group，并重新平衡 shard 分布
- Leave：移除 replica group，把它负责的 shard 迁移给其他 group
- Move：手动把某个 shard 指定到某个 group
- Query：查询某个编号配置，-1 通常表示最新配置
- shardctrler 自身也需要用 Raft 复制配置变更，避免配置服务单点不一致

## 负载均衡卡
Q: shardctrler 重新分配 shard 时要兼顾哪些目标？
A:
- 均衡性：尽量让各 group 负责的 shard 数量接近
- 最小迁移：配置变化时尽量少移动 shard，降低数据迁移成本
- 确定性：所有 shardctrler 副本执行同一配置变更后必须得到完全相同的新配置
- 边界处理：group 数为 0、Join 多个 group、Leave 多个 group、Move 覆盖手动指定等
- 面试亮点：负载均衡不是只看平均，还要控制迁移量和确定性

## 配置变更卡
Q: ShardKV 为什么不能简单看到新配置就立刻服务所有 shard？
A:
- 新配置把某 shard 分配给新 group，但该 group 可能还没拿到旧 group 的数据
- 如果新旧 group 同时服务同一个 shard，会出现双写和不一致
- 如果旧 group 过早停止服务而新 group 未完成迁移，会出现不可用
- 需要为 shard 维护状态，例如 Serving、Pulling、BePulling、GCing 等，控制迁移过程
- 面试表达：配置变更的难点是“所有权变化”和“数据迁移完成”不是同一个瞬间

## 迁移卡
Q: shard 迁移的基本流程是什么？
A:
- group 通过定时任务发现 shardctrler 有新配置
- 对于新配置中自己新增负责的 shard，从旧 owner 拉取该 shard 数据和去重表
- 拉取到数据后，通过本组 Raft 提交迁移结果，确保组内所有副本一致安装
- 新 owner 安装完成后通知旧 owner 可以 GC 该 shard 旧数据
- 整个迁移相关状态变化也要进入 Raft，不能只在单个 server 本地修改

## 客户端路由卡
Q: ShardKV 客户端遇到 ErrWrongGroup 应该怎么处理？
A:
- 客户端根据 key 计算 shard，再根据当前配置找到负责 group
- 如果目标 group 返回 ErrWrongGroup，说明配置可能过期或 shard 正在迁移
- 客户端应向 shardctrler 查询最新配置，然后重试
- 仍然要保持同一 clientId/requestSeq，避免重试造成重复执行
- 面试边界：ErrWrongLeader 是组内 leader 错误，ErrWrongGroup 是跨组配置/路由错误，处理方式不同

## 正确性审查卡
Q: ShardKV 有哪些高频坑？
A:
- 只迁移 KV 数据，不迁移去重表，会导致迁移后重复请求再次执行
- 配置更新不走 Raft，只在某个 server 本地更新，会导致组内副本状态分裂
- 新旧 group 同时服务同一 shard，可能产生双写
- 拉取 shard 时没有指定配置编号，可能把旧配置数据装到新配置流程里
- GC 旧 shard 太早，迁移失败后可能丢数据
