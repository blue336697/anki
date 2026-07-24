# ZSet双索引

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-zset结构

Q: 为什么大 ZSet 同时维护 dict 和 skiplist？

A:
```c
typedef struct zset {
    dict *dict;
    zskiplist *zsl;
} zset;
```
- dict 提供 member → score 的平均 O(1) 精确查找，支持 ZSCORE、判断成员是否存在和更新旧分数。
- skiplist 按 `(score, member)` 排序，支持范围、排名、删除区间。
- 只用 dict 无法高效有序遍历；只用跳表按 member 查找要 O(log N) 且需要 score 才能精确定位。
- 代价是双份索引元数据，写操作必须同时维护一致。

## 02-元素共享

Q: dict 和 skiplist 会不会复制两份 member 字符串？

A:
- Redis 7.4 的经典实现让两侧共享同一 SDS 成员内容，避免复制 payload。
- dict 的 value 保存 score 或关联节点信息；跳表节点拥有成员生命周期，删除顺序要避免悬空引用。
- 共享的是成员字节，不代表索引没有额外内存：dict entry、bucket、跳表节点和各层 forward/span 都存在。
- `MEMORY USAGE` 评估排行榜时要按成员数量和平均层高估算，不只算字符串。

## 03-ZADD更新

Q: ZADD 更新已有成员分数时内部怎样走？

A:
- 先在 dict 中按 member 找到旧 score；若新旧相同且无其他语义变化，可避免重排。
- 若新分数仍位于原前驱和后继之间，跳表可直接改 score；否则从跳表删除旧位置并按新 `(score,member)` 插入。
- dict 的 score 视图同步更新；任何一侧失败都不能留下双索引不一致。
- 单次平均 O(log N)，批量 ZADD 乘以元素数；大批量更新会长时间占主线程。

## 04-listpack转换

Q: 小 ZSet 何时从 listpack 转为 skiplist？

A:
- Redis 7.4 默认 `zset-max-listpack-entries=128`、`zset-max-listpack-value=64`。
- 元素数或任一 member 长度超阈值时转为 zset 双索引；listpack 中 member/score 成对连续保存。
- listpack 查询是线性但内存紧凑；小集合常数低。双索引查询更稳，但每元素元数据更重。
- 转换通常单向，不会因删除回到 128 以下自动转回；阈值可配，且属于版本/配置细节。

## 05-工程边界

Q: 用 ZSet 做百万级排行榜时最容易忽略哪些成本？

A:
- 单 key 的所有写和范围查询集中在一个主线程/分片，热点无法靠 Cluster 自动把一个 key 拆开。
- ZRANGE 大范围的 O(log N + M) 中，M 和返回字节常是主成本；LIMIT 大 offset 也会遍历跳过数据。
- 双索引和 SDS 使内存远高于 `member长度+8字节score`。
- 需要按业务维度分榜、限制 top-N、异步归档；跨分片总榜要在应用层合并并接受一致性取舍。
