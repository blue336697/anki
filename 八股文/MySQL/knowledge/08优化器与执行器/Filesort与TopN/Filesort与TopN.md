# Filesort、Sort Buffer 与 Top-N

## 结构定位
Q: MySQL `Using filesort` 是否一定写磁盘？
A:
- 不是。filesort 表示不能直接按索引序输出，需要额外排序；数据可完全在 sort buffer 内完成。
- 内存不足或中间数据大时生成 runs 并多路归并，才使用临时文件。
- 排序记录可保存 rowid+key 后回表，或保存额外字段一次返回；优化器按行宽和成本选择。
- `sort_buffer_size` 通常按执行 sort 的会话分配，盲目全局调大会放大并发内存。

## 内部记录
Q: two-pass 与 single-pass filesort 的取舍是什么？
A:
- two-pass 排序只携带排序 key 与 rowid，记录窄、排序省内存，但排序后需要回表取列。
- single-pass 携带查询需要的更多字段，避免二次回表但记录宽、可能更早落盘。
- BLOB/TEXT、max_length_for_sort_data 和投影宽度影响策略，具体变量随版本演进。
- Top-N 优化可用优先队列只保留 LIMIT 所需候选，减少完整排序。

## 排序算法
Q: 大结果 filesort 的执行链是什么？
A:
1. 子算子产出行，计算 sort key 并填入 sort buffer。
2. buffer 满时排序成 run 写临时文件。
3. 输入结束后多路归并 runs，按 OFFSET/LIMIT 输出。
4. 若记录只含 rowid，再按定位取完整行；深 OFFSET 仍需处理并丢弃前面大量结果。

## 代价边界
Q: 为什么加大 sort_buffer 可能让系统更慢？
A:
- 高并发下每线程大 buffer 造成内存峰值、allocator 开销和 swap 风险。
- 大于 CPU cache 后排序访问更慢；无法减少输入行时只是让浪费留在内存。
- 多表/窗口查询一条语句可有多个 sort。
- 首选索引顺序、减少投影和输入，再针对会话调节。
- 参数应按“单次算子内存 × 同时排序算子数 × 活跃会话数”估峰值，而不是按一条测试 SQL 的内存判断。

## 验证
Q: 如何诊断排序瓶颈？
A:
- ANALYZE 看 sort 输入/输出、耗时和 loops；状态指标看 sort_merge_passes、临时文件和磁盘。
- 检查 ORDER BY 与联合索引是否兼容、是否可加唯一 tie-breaker+LIMIT。
- 对比 keyset pagination，避免深 OFFSET。
- 排序不是唯一慢点：上游 join 产出爆炸时必须先减少行数。
