# Buffer Pool 控制块、页帧与页哈希

## 结构定位
Q: InnoDB Buffer Pool 中“一页”在内存里由哪些对象表示？
A:
- 数据页内容位于固定大小的 page frame；旁边的 `buf_block_t/buf_page_t` 控制块保存 `(space_id,page_no)`、状态、锁、fix count、脏页 LSN 和链表节点。
- page hash 以 page id 快速查找已缓存页，避免扫描 LRU；命中后仍要 pin/fix 并获取合适 page latch。
- Buffer Pool 可分实例和 chunk，实例减少全局 mutex 竞争，chunk 支持在线调整内存。
- 源码锚点：`buf0buf.h/.cc`、`buf0lru.cc`、`buf0flu.cc`。

## 状态与并发
Q: page latch、buffer fix 和行锁分别保护什么？
A:
- page latch 是短期内存结构锁，保护页内容和 B-tree 结构操作，通常随 mini-transaction 很快释放。
- buffer fix/pin 防止正在访问的页被淘汰；它不是读写互斥语义。
- 行锁属于事务锁，保护逻辑记录/间隙，可跨语句持有到提交。
- 把 latch 等待、I/O 等待和 row lock wait 混成“数据库锁”会导致错误排障。

## 取页算法
Q: 访问一个不在 Buffer Pool 的页时发生什么？
A:
1. 查 page hash，未命中后从 free list 取 frame；没有空闲 frame 时从 LRU 尾选择可淘汰干净页，脏页需先安排刷盘。
2. 在 hash 中建立“正在读取”状态，合并其他线程对同页的并发请求。
3. 发起文件 I/O，完成后校验页并设置状态；访问线程获得 latch/fix 后读取。
4. 页根据访问模式进入 LRU old/young 区，修改时还会进入 flush list。

## 容量与代价
Q: Buffer Pool 越大越好吗，怎样评估合理大小？
A:
- 大池减少数据页 miss，但会挤压 OS、连接内存、Performance Schema、redo/binlog 和其他进程；发生 swap 通常灾难性更大。
- Dedicated server 常给 InnoDB 大部分内存只是起点，不是固定 80% 定律；容器限额和 per-session 峰值必须纳入。
- 大池会增加预热、全量扫描污染和故障切换恢复时间；可持久化 dump/load 热页信息改善重启预热。
- 应以工作集、命中质量、物理读延迟、淘汰率和系统剩余内存联合调节。

## 验证与误区
Q: `Buffer pool hit rate 99.9%` 为什么仍不能证明缓存健康？
A:
- 高 QPS 下 0.1% miss 仍可能是大量随机 I/O；累计比率还会掩盖短时抖动。
- 大扫描可能挤出热点但总体逻辑读数巨大，使比率看起来很好。
- 写延迟可能来自 flush/redo/doublewrite，而与读命中率无关。
- 需要看单位时间 logical/physical reads、LRU eviction、young/not young、free pages、dirty pages 和磁盘 p99。
