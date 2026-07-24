# 慢SQL与Explain

## Explain卡
Q: 看 MySQL Explain 时重点看哪些字段？
A:
- `type` 看访问方法，从 const/ref/range 到 ALL 逐渐变重
- `key` 看实际使用的索引
- `rows` 看优化器估算扫描行数
- `Extra` 看是否 filesort、temporary、Using index、Using where
- `filtered` 看条件过滤比例估计

## 慢SQL卡
Q: 线上排查慢 SQL 的基本路径是什么？
A:
- 先确认慢是锁等待、IO 慢、CPU 高还是返回数据量大
- 查看慢日志、执行计划、扫描行数、返回行数和执行耗时
- 检查索引是否匹配 where、join、order by、group by
- 判断是否存在隐式类型转换、字符集转换、函数包列、深分页
- 最后再考虑加索引、改 SQL、拆查询、缓存或业务限流

## 一行慢卡
Q: 为什么查一行也可能很慢？
A:
- 可能在等 MDL 锁、行锁或 flush
- 可能优化器选错索引，扫描大量数据后只返回一行
- 可能发生隐式类型转换导致索引失效
- 可能表统计信息过旧，执行计划不稳定
- 可能磁盘 IO 抖动或 Buffer Pool 命中率低

## 正确性审查卡
Q: 慢 SQL 优化有哪些常见误区？
A:
- “慢 SQL 一定加索引”：错误。可能是锁等待、返回太多或 SQL 写法问题
- “Explain 只看 key”：不够。还要看 type、rows、Extra、filtered
- “rows 小就一定快”：不一定。锁等待和排序临时表仍可能慢
- “线上直接 force index”：风险高。要评估数据分布变化
- “优化 SQL 不用看业务”：错误。分页方式、查询频率和一致性要求都影响方案
