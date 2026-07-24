# redisDb与过期字典

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-数据库布局

Q: redisDb 怎样同时管理 keyspace 和 TTL？

A:
- Redis 7.4 的 `redisDb.keys` 是主 keyspace（当前源码通过 kvstore 封装字典），保存 key → redisObject。
- `expires` 是独立 kvstore，记录有 TTL 的 key 与绝对毫秒过期时间；没有 TTL 的 key 不进入该结构。
- 两边逻辑上共享 key 身份，删除 key 时必须同步移除过期元数据。
- `avg_ttl` 是统计估计，`expires_cursor` 保存主动过期扫描进度；WATCH、阻塞键也各有索引。

## 02-绝对时间

Q: 为什么 TTL 在内存和 RDB 中要保存绝对过期时间，而不是只保存剩余秒数？

A:
- 命令执行时把 EX/PX 等相对时长换算成绝对 Unix 毫秒时间，判断只需比较 `now > expiretime`。
- RDB 保存绝对时间，停机期间时间仍流逝；加载时已过期的 key 可以直接丢弃。
- 主从复制过期语义由主节点驱动删除并传播，避免各节点时钟独立产生不同删除顺序。
- 代价是系统时钟跳变会影响 TTL，因此宿主机时间同步很重要。

## 03-惰性过期

Q: 惰性过期在一次读写 key 时如何发生？

A:
- 访问路径先查 expires；若当前时间超过截止时间，主节点执行过期删除并把 key 当不存在。
- 删除还要触发 keyspace notification、dirty 统计、AOF/复制传播等副作用，不能只是从 dict 静默摘掉。
- replica 通常不自行决定对外传播删除，而跟随主节点的合成 DEL/UNLINK 语义；复制状态下有额外分支。
- 只靠惰性过期会让从不访问的过期 key 永久占内存，因此还需要主动过期。

## 04-TTL命令语义

Q: SET、EXPIRE、PERSIST 和覆盖写入怎样影响 TTL？

A:
- 普通 SET 覆盖 key 默认清除原 TTL；使用 KEEPTTL 才保留。
- EXPIRE 支持 NX/XX/GT/LT 条件，过期时间小于等于当前时间会转成删除语义。
- 对容器内部内容的修改通常不清除 key TTL，例如 HSET/LPUSH；替换整个 key 的命令要单独确认。
- RENAME 会把源 key 的 TTL 一起移动；TTL/PTTL 的 -1 表示存在但无过期，-2 表示 key 不存在。

## 05-内存幻觉

Q: 为什么大量 key 已经过期，used_memory 仍可能暂时不降？

A:
- 过期是逻辑截止时间，不是为每个 key 创建一个精确定时器；未访问 key 要等待主动采样。
- 主动过期受 CPU 时间预算限制，过期风暴时会分多轮清理。
- 删除对象后，jemalloc 可能保留 arena/page，used_memory 或 RSS 不会同步等比例下降。
- 应同时看 `expired_keys`、`expire_cycle_cpu_milliseconds`、key 数、allocator active/resident 和 RSS。
