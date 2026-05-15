# 深分页与MyBatisPlus

## 深分页卡
Q: MySQL 深分页为什么慢？
A:
- `limit offset, size` 需要先扫描并丢弃 offset 行
- offset 越大，扫描和回表成本越高
- 如果排序字段没有合适索引，还会叠加 filesort 和临时表成本
- 业务上无限翻页通常没有必要，应限制最大页数或改用游标分页
- 面试表达：深分页慢是因为数据库必须找到并跳过大量前置记录

## Seek卡
Q: Seek Method 如何优化深分页？
A:
- 使用上一页最后一条记录的排序 key 作为下一页起点
- 查询形如 `where id > last_id order by id limit size`
- 它避免大 offset 扫描，适合稳定排序字段
- 复合排序需要用多列游标保持顺序一致
- 缺点是不适合任意跳页，但非常适合滚动加载和列表翻页

## MyBatisPlus卡
Q: 使用 MyBatis-Plus 写复杂 SQL 时要注意什么？
A:
- Wrapper 适合简单条件拼装，复杂查询仍建议写 XML 或注解 SQL
- `${}` 是字符串拼接，有 SQL 注入风险，只能用于受控字段如排序白名单
- `#{}` 是参数绑定，适合普通值传参
- LambdaUpdate 要注意条件是否完整，避免误更新全表
- 聚合、分组、复杂 join 要关注生成 SQL 和执行计划，而不是只看 Java 代码简洁

## 正确性审查卡
Q: 深分页和 ORM 使用有哪些常见误区？
A:
- “加索引就能解决所有深分页”：不完整。大 offset 仍要跳过大量记录
- “Seek 分页支持任意跳页”：不支持，它更适合连续翻页
- “MyBatis-Plus 生成的 SQL 一定最优”：错误。仍要 explain 检查
- “排序字段可以直接接收前端传入”：危险。要白名单校验
- “Wrapper 能替代所有 SQL”：不现实。复杂查询应回到清晰 SQL 和执行计划
