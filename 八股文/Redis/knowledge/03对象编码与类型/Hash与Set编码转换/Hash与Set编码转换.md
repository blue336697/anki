# Hash与Set编码转换

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-Hash-listpack

Q: Hash 的 listpack 编码内部怎样排列？

A:
- field 和 value 交替连续保存：`field1,value1,field2,value2...`，没有额外哈希索引。
- HGET 需要顺序扫描 field，找到后取下一 entry；小对象靠紧凑布局和缓存局部性获得低常数。
- Redis 7.4 默认最多 512 个 field，且 field/value 都不超过 64 字节；任一条件突破就转 hashtable。
- 配置项：`hash-max-listpack-entries/value`。

## 02-Hash-hashtable

Q: Hash 转 hashtable 后内存和复杂度怎样变化？

A:
- 每个 field 变成 dict key，value 作为 entry 的值；平均 HGET/HSET O(1)，渐进 rehash 逻辑与主 keyspace dict 类似。
- 代价包括 bucket 数组、entry、field/value SDS、指针和 allocator 对齐，内存可能跳升。
- 转换需要遍历原 listpack 建表，是 O(N) 的一次性主线程工作；临界点大批量写可能出现延迟尖峰。
- 删除到阈值以下通常不自动转回，避免反复转换。

## 03-Set三编码

Q: Redis 7.4 的 Set 为什么可能是 intset、listpack 或 hashtable？

A:
- 全为整数且数量不超过 `set-max-intset-entries`（默认 512）时优先 intset。
- Redis 7.2+ 对短小非整数集合可用 listpack；7.4 默认不超过 128 项且成员不超过 64 字节。
- 超过数量/长度或操作要求通用表示时转 hashtable，成员作为 dict key，value 可省略。
- 旧资料只写 intset/hashtable 已不完整，回答必须标版本。

## 04-集合运算

Q: SINTER/SUNION/SDIFF 为什么容易成为慢命令？

A:
- 复杂度取决于参与集合总元素数，不是 key 数；编码不同还会走不同迭代/查找路径。
- 交集通常从最小集合枚举并到其他集合查 membership；hashtable 平均 O(1)，listpack/intset 有各自常数。
- STORE 版本还要构造目标集合，可能触发扩容/编码转换和大规模传播。
- 多个大 Set 集中在同一主线程执行，会阻塞其他客户端；应预计算、分批或换离线集合系统。

## 05-阈值调优

Q: 为什么不应该为了省内存无限调大 listpack 阈值？

A:
- listpack 越大，查找和中部插删越接近线性字节扫描/memmove；主线程 p99 会恶化。
- 阈值调小会更早转 dict，内存上涨但访问复杂度稳定；调优是内存与延迟的交换。
- 应按真实 field/member 长度和命令比例压测，不只看元素数。
- 调整配置不会保证现存对象立即重编码，需观察 `OBJECT ENCODING` 和新写入行为。
