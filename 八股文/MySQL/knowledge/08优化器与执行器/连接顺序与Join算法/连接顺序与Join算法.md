# Join 顺序、Nested Loop 与 Hash Join

## 结构定位
Q: 多表 Join 为什么首先是“连接顺序”问题？
A:
- 中间结果大小会乘法传播；先用高过滤表可显著减少后续 inner lookup。
- 优化器枚举/剪枝候选顺序，并为每条边选择 nested loop、hash join 等路径。
- 外连接、semijoin、依赖子查询和 straight join 会限制可交换顺序。
- 统计误差在早期节点会导致错误顺序，后面再有好索引也难补救。

## 算法结构
Q: Nested Loop、BKA 和 Hash Join 的内部差异是什么？
A:
- Nested Loop 对外表每行驱动内表访问，内表有高效索引时很强。
- BKA 把外表 key 批量缓冲，通过 MRR 改善内表随机访问。
- Hash Join 先为一侧构建 hash table，再扫描另一侧 probe，适合无有效索引的等值连接。
- 非等值条件、内存限制、输出顺序和外连接语义影响可用算法。

## HashJoin流程
Q: Hash Join 如何执行，内存不足会怎样？
A:
1. 选择 build side，读取行并按 join key 建 hash table。
2. 扫描 probe side，按 key 查 bucket，再校验完整 join condition。
3. 匹配行传给上层；外连接还输出未匹配行。
4. 内存不足可分区/落盘，增加 I/O；EXPLAIN ANALYZE 可显示真实构建和 probe 代价。

## 复杂度与边界
Q: Hash Join O(N+M) 为什么不一定比索引 Nested Loop 快？
A:
- 小外表配合内表唯一索引只做少量点查，无需扫描/构建整侧。
- Hash 构建消耗内存和 CPU，冷数据扫描可能昂贵，LIMIT 早停也不利。
- 数据倾斜会造成大 bucket，落盘使常数急升。
- 复杂度忽略缓存、行宽、输出量和过滤位置，必须以真实计划判断。
- Hash Join 只改善访问算法，不会减少真实多对多输出；结果集本身巨大时任何 join 都必须承担输出成本。

## 验证
Q: Join 慢怎样定位是顺序、算法还是数据爆炸？
A:
- TREE/ANALYZE 逐节点看 estimated vs actual rows、loops 和首个放大节点。
- 检查 join key 类型/collation、索引、NULL 和一对多基数。
- 单独统计各过滤条件分布，避免用总表行数猜。
- 优先减少中间行与修正统计，再讨论 join buffer 或强制算法。
