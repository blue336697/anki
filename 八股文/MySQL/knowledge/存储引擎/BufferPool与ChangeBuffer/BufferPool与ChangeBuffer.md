# BufferPool与ChangeBuffer

## BufferPool卡
Q: InnoDB Buffer Pool 的核心作用是什么？
A:
- Buffer Pool 缓存数据页、索引页等 InnoDB 页面，减少磁盘 IO
- 查询和更新都要先把页读入 Buffer Pool
- 被修改但未刷盘的页叫脏页，会进入 flush 链表
- Buffer Pool 内部有 free、LRU、flush 等链表协同管理页面
- 面试表达：Buffer Pool 是 InnoDB 性能和刷盘机制的核心

## LRU卡
Q: InnoDB 为什么不使用朴素 LRU？
A:
- 朴素 LRU 容易被全表扫描污染，热点页被大量冷数据挤出
- InnoDB 把 LRU 分为 young 区和 old 区
- 新读入页面先进入 old 区，真正热点再晋升到 young 区
- 还有访问时间窗口控制，避免短时间扫描导致频繁晋升
- 这体现了数据库缓存要专门处理顺序扫描和热点访问

## ChangeBuffer卡
Q: Change Buffer 是什么？适合什么场景？
A:
- Change Buffer 缓存对非唯一二级索引页的修改
- 当目标二级索引页不在 Buffer Pool 中时，可以先记录变更，后续 merge
- 它减少随机读，提高写入性能
- 唯一索引不能使用 Change Buffer，因为必须检查唯一性
- 适合写多读少、普通二级索引更新多的场景

## 正确性审查卡
Q: Buffer Pool 和 Change Buffer 有哪些常见误区？
A:
- “Buffer Pool 只缓存数据不缓存索引”：错误。索引页也会缓存
- “脏页越少越好”：不完整。太激进刷盘会牺牲吞吐
- “Change Buffer 适合所有索引”：错误。唯一索引不能用
- “全表扫描一定会打爆热点缓存”：InnoDB 有 old/young 区缓解，但仍要关注
- “Buffer Pool 越大越好”：不绝对。还要考虑 OS、连接内存和刷脏能力
