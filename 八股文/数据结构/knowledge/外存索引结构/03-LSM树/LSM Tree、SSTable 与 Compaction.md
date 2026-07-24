# LSM Tree、SSTable 与 Compaction

> 基线：LSM 是由内存有序表、不可变有序文件和后台归并组成的写优化索引，不是一棵普通指针树。

## 01-组件全景
Q: LSM Tree 的写入路径由哪些核心数据结构组成？
A:
- 写入先追加 WAL 保证崩溃恢复，再写入内存中的 MemTable；MemTable 常由跳表、平衡树或并发有序结构实现。
- MemTable 达阈值后冻结为 immutable，后台顺序刷成不可变 SSTable；文件内 key 有序。
- 磁盘上存在多个 level/run，后台 compaction 归并重叠文件、丢弃可安全清理的旧版本和墓碑。
- manifest/version set 记录当前文件集合与 key 范围，缓存和 Bloom Filter 用于减少不必要读。

## 02-SSTable布局
Q: 一个 SSTable 内部通常怎样组织数据？
A:
- 数据按 key 排序分成 data block，每块可做前缀压缩、校验和与压缩，并保存 restart point 支持块内定位。
- index block 保存每个数据块的边界 key 和文件偏移；filter block 保存分块 Bloom，footer 指向这些元数据。
- 查询先用文件 key range/元数据排除，再查 Bloom 和 index，最后读取目标 data block。
- 文件不可变使顺序构建、校验、缓存和无锁读简单，但更新必须写新版本而不能原地覆盖。

## 03-写入与刷盘
Q: 一次写入从 WAL 到 SSTable 的完整过程是什么？
A:
- 请求先形成 sequence/version，追加 WAL；是否等待 fsync 决定持久性与吞吐延迟权衡。
- 再更新 active MemTable，读请求可立即看见满足快照规则的新值。
- 内存满后切换新 WAL/MemTable，旧表冻结；后台按序遍历它并生成 L0 SSTable，完成后更新 manifest。
- 只有新文件和版本元数据持久可见后，旧 WAL 才能安全删除；顺序错误会在崩溃后丢数据。

## 04-读路径
Q: LSM 的点查询为什么可能读多个结构，怎样降低读放大？
A:
- 先查 active/immutable MemTable，再按从新到旧的版本语义检查可能包含 key 的 SSTable。
- L0 文件 key 范围可能重叠，需查多个；leveled compaction 的较高层通常保证同层范围不重叠，可二分选一个文件。
- 每文件/分区 Bloom 排除确定不存在的文件，block cache 避免重复 IO，index 常驻内存加速定位。
- 找到值也要判断 sequence、快照和 tombstone；旧文件中存在更旧值不能覆盖新删除。

## 05-Compaction
Q: Compaction 具体做什么，它为什么不是简单“压缩文件”？
A:
- 选择若干 key 范围重叠的输入 SSTable，执行多路有序归并，按版本规则输出新的有序文件。
- 在没有旧快照需要时，可丢弃被覆盖的旧 value、过期记录和已传播到底层的 tombstone。
- 安装新 version 后旧文件才变成不可达，并等待无读者引用后删除；过程必须崩溃安全。
- 它重写大量仍有效数据以恢复读效率和空间，所以产生写放大并消耗 IO/CPU。

## 06-Leveled与Tiered
Q: Leveled Compaction 和 Size-Tiered/Universal Compaction 如何权衡？
A:
- Leveled 把数据分层，层容量按倍率增长，同层高层通常不重叠；点读文件少、空间放大低，但数据会被多次重写。
- Tiered 把大小相近的多个 run 合并，写入重写较少，但同时存在更多重叠 run，读放大和临时空间更高。
- workload 若写密集、可容忍读放大偏向 tiered；读密集和空间敏感常偏向 leveled。
- 实际系统有混合策略、子 compaction 和动态 level，不能把产品行为仅归为两个教科书标签。

## 07-三种放大
Q: LSM 的写放大、读放大和空间放大分别是什么？
A:
- 写放大是物理写入字节/用户写入字节，来源于 WAL、flush 和多轮 compaction 重写。
- 读放大是一次逻辑读检查的 run/file/block 数与额外字节，受重叠、Bloom 命中和缓存影响。
- 空间放大是实际占用相对最新有效数据的比例，来自旧版本、墓碑、冗余文件和 compaction 临时输出。
- 三者互相制约：减少 compaction 可降写放大，却通常提高读与空间放大，调优必须围绕 workload。

## 08-墓碑与快照
Q: LSM 为什么不能看到 tombstone 就立即物理删除？
A:
- tombstone 表示某 sequence 上的逻辑删除，必须遮蔽更老 SSTable 中仍存在的 value。
- 只有 compaction 已覆盖所有可能含旧值的更低层，且没有快照需要读取删除前版本时，才能丢弃墓碑。
- 过早清理会让旧值“复活”；长期快照或未覆盖范围会让墓碑和旧版本持续占空间。
- 范围墓碑比点墓碑更复杂，归并与查询必须正确处理覆盖区间和版本边界。

## 09-背压与故障
Q: Compaction 跟不上写入时会发生什么，系统为什么必须背压？
A:
- L0 文件数量与重叠增加，读请求检查更多文件，缓存失效和尾延迟上升；磁盘空间也可能被旧文件占满。
- 若继续无限接收写入，后台债务只会扩大并最终造成空间耗尽或延迟雪崩。
- 系统通常按 immutable 数、L0 文件数或 compaction debt 限速/暂停写入，让后台恢复。
- 排障要看各层大小、pending bytes、写停顿、IO 带宽和长快照，不应只提升 compaction 线程数抢占前台 IO。
