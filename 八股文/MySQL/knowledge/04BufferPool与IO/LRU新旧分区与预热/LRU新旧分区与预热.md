# Buffer Pool LRU 新旧分区与预热

## 结构定位
Q: InnoDB 为什么不是简单使用“访问一次就移到 LRU 头部”的 LRU？
A:
- 全表扫描或备份会一次性读入大量冷页，传统 LRU 会把真正热点全部淘汰。
- InnoDB 把 LRU 分为 young/new 与 old 子列表，新读页插在 old 区头部附近，而非全局头部。
- 页在 old 区停留超过 `innodb_old_blocks_time` 并再次访问后才有资格提升到 young。
- `innodb_old_blocks_pct` 控制 old 区比例，默认策略用于抵抗 scan pollution。

## 链表状态
Q: LRU list、free list 和 unzip LRU 的职责分别是什么？
A:
- LRU 按冷热管理可淘汰缓存页；free list 保存无有效页内容、可立即复用的 frame。
- 压缩表可能同时保留压缩页与解压 frame，unzip LRU 协调解压页内存回收。
- 被 fix、I/O 中或不可淘汰状态的页即使在尾部也不能直接复用。
- 脏页位于 LRU 的同时还在 flush list，链表成员身份不是互斥状态。

## 提升淘汰算法
Q: 一页从首次读取到成为热点再被淘汰的路径是什么？
A:
1. 物理读完成后插入 old 区起点，记录首次访问时间。
2. 短时间顺序扫描的再次触碰不立即提升；超过阈值后再次访问才移向 young 头。
3. 后续访问维持热点位置，长时间未访问逐渐向尾部移动。
4. 淘汰从尾部寻找可复用干净页；脏页先进入刷脏流程，frame 清空后回 free list。

## 预读与边界
Q: 为什么调大 old_blocks_time 既可能保护热点，也可能伤害新热点？
A:
- 阈值大可阻止一次性扫描晋升，但真正突然变热的新页要等待更久才能进入 young。
- 阈值小提高适应速度，却让重复扫描更易污染 young 区。
- 查询模式、存储延迟和 Buffer Pool/工作集比例决定最佳值，不存在统一参数。
- 先修复无界扫描、缺索引和备份流量，再考虑微调 LRU。

## 验证与工程实践
Q: 怎样证明一次大查询造成 Buffer Pool 污染？
A:
- 在查询窗口观察 buffer pool reads、pages made young/not young、LRU eviction、热点查询 p99 和磁盘读取同步变化。
- 对比查询前后关键索引页命中与工作集恢复时间；不要只看全局命中率。
- 在副本执行报表、分批按主键扫描、限速或建立合适覆盖索引通常比参数调优更稳。
- 重启预热可用 Buffer Pool dump/load，但保存的是页标识，不替代磁盘数据与一致性恢复。
