# List与ZSet编码转换

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-List编码

Q: Redis 7.4 的 List 为什么固定显示 quicklist，但内部仍有多种形态？

A:
- `OBJECT ENCODING` 通常返回 quicklist；quicklistNode 内部可装 listpack，也可为超大单元素使用 plain 节点。
- 中间节点还可能是 LZF 压缩表示，访问时临时解压；所以“quicklist”不是所有元素都未压缩地连续存放。
- `list-max-listpack-size` 控制节点填充，`list-compress-depth` 控制两端保留的未压缩层数。
- 旧 linkedlist/ziplist 编码在当前版本已标为不再使用。

## 02-ZSet紧凑编码

Q: ZSet 的 listpack 中 member 和 score 怎样保存？

A:
- member、score 成对连续存储，score 可按字符串/整数编码保存；排序顺序按 score 再 member。
- 插入需找到有序位置并 memmove 后续字节，查 member 也要扫描，因此小集合才合适。
- 默认 128 项、单 member 64 字节阈值突破后转 zset 双索引。
- 转换时构建 dict 与 skiplist，是一次 O(N log N) 或相近量级的集中工作，应防临界大批量写。

## 03-编码转换单向性

Q: 为什么多数容器从紧凑编码转通用编码后不自动降级？

A:
- 降级要扫描、验证所有元素长度/类型并重新编码，主线程成本高。
- 数据在阈值附近波动会产生来回转换、延迟抖动和 allocator 碎片。
- 通用结构虽然更耗内存，但保证未来增长和操作复杂度稳定。
- 若必须回收，可在业务低峰重建新 key 后原子切换，而不是依赖内部自动降级。

## 04-转换尖峰

Q: 如何解释“平时很快，某次 HSET/ZADD 突然变慢”的编码原因？

A:
- 该次写可能正好越过 entries/value 阈值，需要把完整 listpack 转成 dict/skiplist。
- 转换在命令执行主线程内进行，耗时与现有元素数和字节量相关；同时可能触发 allocator 和 rehash。
- Slowlog 可捕获实际执行耗时，前后用 `OBJECT ENCODING` 验证编码变化，结合 MEMORY USAGE 看内存阶跃。
- 预防方式是控制对象规模、避免一次塞满临界值，并在容量测试中覆盖“越阈值”场景。

## 05-版本表述

Q: 回答 Redis 数据类型底层结构时，怎样避免背旧版本答案？

A:
- 先说逻辑类型，再说“以 Redis 7.4 为例”的当前编码：String int/embstr/raw，List quicklist，Hash listpack/HT。
- Set intset/listpack/HT，ZSet listpack/skiplist，Stream rax+listpack。
- 再补历史差异：ziplist、linkedlist、zipmap 等常量仍可能为兼容保留，但当前新对象不再使用。
- 最后给 `OBJECT ENCODING` 与 redis.conf 阈值作为可验证证据。
