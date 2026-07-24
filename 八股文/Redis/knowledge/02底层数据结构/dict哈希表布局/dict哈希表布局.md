# dict哈希表布局

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-dict结构

Q: Redis 7.4 的 dict 为什么有两张哈希表？字段分别是什么？

A:
```c
struct dict {
    dictType *type;
    dictEntry **ht_table[2];
    unsigned long ht_used[2];
    long rehashidx;
    unsigned pauserehash:15;
    unsigned useStoredKeyApi:1;
    signed char ht_size_exp[2];
};
```
- `ht_table[0]` 是当前表，`ht_table[1]` 是渐进 rehash 的目标表。
- 容量用指数保存，实际 bucket 数是 `1 << ht_size_exp[i]`；`ht_used` 是真实 entry 数。
- `rehashidx=-1` 表示未迁移，否则指向下一待迁移 bucket。

## 02-dictEntry与冲突

Q: bucket 冲突怎样存储？dictEntry 里有哪些逻辑部分？

A:
- bucket 数组元素指向 entry 链，冲突通常通过链地址法连接；索引由 hash 与 `size-1` 掩码得到，因此容量取 2 的幂。
- entry 逻辑上保存 key、value 和 next；Redis 7.x 对 entry 表示做了多种紧凑优化，源码把 `dictEntry` 设为 opaque，不能机械背旧版固定结构。
- value 可按 dictType 配置为指针、整数或“无独立 value”；不同字典复用同一引擎但生命周期回调不同。
- `dictType` 提供 hash、比较、复制、析构、扩容许可等回调。

## 03-查找路径

Q: dictFind 在 rehash 期间怎样查找一个 key？

A:
1. 计算 key 的 64 位 hash。
2. 在 table 0 用 `hash & sizemask0` 定位 bucket，沿冲突链比较。
3. 若未命中且正在 rehash，再在 table 1 用新掩码定位并比较。
4. 两表都未命中才返回不存在；新增 entry 在 rehash 期间进入 table 1，避免继续扩大旧表。
- 平均 O(1)，最坏碰撞链 O(N)；Redis 使用随机 hash seed 降低可构造碰撞攻击。

## 04-扩缩容条件

Q: dict 什么时候扩容或缩容？为什么 fork 期间策略会不同？

A:
- 负载因子达到策略阈值时扩容到能容纳 used 的下一个 2 的幂；严重超载时即使暂时禁止普通 resize 也会强制扩。
- 低填充率时可缩容，7.4 源码 `HASHTABLE_MIN_FILL=8` 表示低于约 12.5% 才考虑，避免频繁伸缩。
- 有 RDB/AOF 子进程时，某些 resize 会受控制以减少触碰页和 COW；但过高负载因子会拖慢查询，因此不能无限禁止。
- 精确阈值是实现细节，回答时要区分“原理”与“该版本常量”。

## 05-验证与陷阱

Q: 为什么不能用 DBSIZE 直接估算 dict 内存？

A:
- DBSIZE 只给 key 数，不包含 bucket 空槽、冲突 entry、key SDS、redisObject、value 底层结构和过期字典。
- rehash 期间两张 bucket 数组同时存在，峰值内存高于稳定态；fork 时再叠加 COW。
- `MEMORY STATS`/`INFO memory` 看全局，`MEMORY USAGE key` 看单 key 近似，采样工具看分布。
- 旧面试资料常背 `dictht ht[2]` 和固定 `dictEntry`；Redis 7.4 字段已演进，应以当前源码为准。
