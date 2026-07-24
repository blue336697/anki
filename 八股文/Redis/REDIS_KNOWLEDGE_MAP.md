# Redis 源码机制级知识地图

> 基线：Redis 7.4 OSS，官方源码 commit `93a16ee`。  
> `knowledge/` 是唯一知识源；旧版宽主题笔记归档在 `knowledge_legacy/`，不参与构建。

## 制卡标准

每个主题固定拆成 5 张连续追问卡：

1. **结构定位**：它解决什么问题，与上下层怎样连接。
2. **字段与布局**：结构体字段、指针关系、字节布局或状态数据。
3. **关键算法**：沿源码函数把执行过程分步骤说清。
4. **复杂度与阈值**：时间/空间复杂度、默认配置和编码转换条件。
5. **故障边界与验证**：哪些保证不成立，怎样用命令、指标或源码验证。

答案中的版本常量均标为 Redis 7.4 实现细节，不当作跨版本协议保证。

## 全量目录

| 模块 | 主题数 | 卡片数 | 源码级主题 |
|---|---:|---:|---|
| 01 内核与执行链路 | 4 | 20 | redisObject、ae 事件循环、客户端请求执行链、I/O 线程与后台任务 |
| 02 底层数据结构 | 10 | 50 | SDS 布局/扩容、dict、渐进 rehash/SCAN、listpack、quicklist、intset、跳表、ZSet 双索引、Stream rax+listpack |
| 03 对象编码与类型 | 3 | 15 | String 三编码、Hash/Set 转换、List/ZSet 转换 |
| 04 数据库与内存 | 5 | 25 | redisDb/TTL、主动过期、maxmemory 淘汰、近似 LRU/LFU、jemalloc/碎片/COW |
| 05 持久化 | 5 | 25 | RDB 格式、BGSAVE/fork、AOF 写入/fsync、多部件 AOF/rewrite、加载与混合持久化 |
| 06 复制与高可用 | 5 | 25 | replid/offset/backlog、全量/部分同步、异步复制/WAIT、Sentinel SDOWN/ODOWN、选举/failover |
| 07 集群 | 4 | 20 | 槽与节点结构、Cluster Bus/PFAIL/FAIL、MOVED/ASK/reshard、副本选举与一致性 |
| 08 事务脚本与锁 | 4 | 20 | MULTI/EXEC、WATCH 双向索引、Lua/Functions、Redis 锁/Redisson/watchdog/fencing |
| 09 客户端与缓存工程 | 5 | 25 | RESP/pipeline/MGET、Lettuce/Jedis、缓存一致性、穿透击穿雪崩、hot/big key |
| 10 消息安全排障 | 5 | 25 | Pub/Sub、Stream 消费组/PEL、Slowlog/Latency、ACL/TLS、Key/TTL/容量模型 |
| **合计** | **50** | **250** | 每主题 5 张追问链卡 |

## 版本差异重点

- Redis 6：引入可配置网络 I/O threads，但普通 keyspace 命令仍以主线程串行执行为主。
- Redis 7：listpack 替代旧 ziplist；AOF 使用 BASE + INCR + manifest 的多部件结构；Functions 成为持久化函数库方案。
- Redis 7.2+：小 Set 可使用 listpack，不能再只回答 intset/hashtable。
- Redis 7.4：包含 hash field expiration 等新机制；key 级过期与字段级过期不能混为一套实现。
- Redis 8.4+：官方锁文档提供 DELEX 条件删除；本牌组基线 7.4，解锁仍以 Lua 比较 token 后删除为主。

## 主要源码锚点

- 对象与命令：`src/server.h`、`src/object.c`、`src/networking.c`、`src/server.c`
- 数据结构：`src/sds.*`、`src/dict.*`、`src/listpack.c`、`src/quicklist.*`、`src/intset.*`、`src/t_zset.c`、`src/stream.*`
- 内存与过期：`src/expire.c`、`src/evict.c`、`src/lazyfree.c`、`src/defrag.c`
- 持久化：`src/rdb.c`、`src/aof.c`
- 复制与高可用：`src/replication.c`、`src/sentinel.c`
- 集群：`src/cluster.c`、`src/cluster.h`
- 事务脚本：`src/multi.c`、`src/script_lua.c`、`src/functions.c`

## 构建

```powershell
cd D:\claudeProjects\anki\八股文\Redis
python .\build_redis_all.py
```

输出：`D:\claudeProjects\anki\牌组\八股文\Redis\Redis八股文.apkg`

同步到 Anki 前需要 JSON 时，运行：

```powershell
python .\export_redis_notes_json.py
```

两个 Python 脚本都只解析 `knowledge/` 中的 Markdown，不包含卡片知识正文。
