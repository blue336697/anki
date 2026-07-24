# B+ 树层级搜索与持久游标

## 结构定位
Q: InnoDB B+ 树点查从根到叶的内部路径是什么？
A:
- `dict_index_t` 定位 root page；每个非叶子页记录保存分隔 key 与 child page no，叶子页保存聚簇行或二级记录。
- `btr_cur_search_to_nth_level()` 逐层 latch 页面并在页目录中查找，最终把 `btr_pcur_t`/page cursor 定位到目标前后。
- Buffer Pool page hash 先尝试命中页；未命中才发起 I/O，算法复杂度与实际 I/O 次数不能混为一谈。
- 源码锚点：`btr0cur.*`、`btr0pcur.*`、`page0cur.*`。

## 游标结构
Q: 为什么 InnoDB 需要 persistent cursor，而不只保存“当前记录指针”？
A:
- 页分裂、合并、purge 或 latch 释放后，原内存地址可能失效；持久游标保存 index、page/record 位置及相对定位信息。
- 恢复游标时可依据保存的 key 和相对位置重新搜索，保证长扫描或跨函数调用继续。
- 游标有 before/after/on 等状态，范围边界判断依赖精确比较模式。
- 游标稳定性不等于事务可见性；定位后仍需 MVCC 或锁检查。

## 查找算法
Q: 唯一等值查找和范围查找在 B+ 树游标模式上有什么差别？
A:
1. 唯一等值以完整唯一 key 搜索，找到后校验删除标记、NULL 语义和可见性。
2. 范围下界通常定位首个 `>=` 或 `>` 目标的记录，上界在扫描过程中逐条判断。
3. 扫完本叶子后沿 FIL_PAGE_NEXT 到下一叶子，避免每行回根。
4. 复合 key 比较按索引列顺序、排序方向、NULL 和 collation 执行，不是简单字节 memcmp。

## 复杂度与扇出
Q: 为什么数据库 B+ 树常只有 3～4 层，但不能把这个数字当保证？
A:
- 内部页只存 key/child，16KiB 页具有高扇出；高度约为 `log_fanout(N)`。
- key 越长、页填充越低，扇出越小；行数、页大小、压缩和删除碎片都会影响高度。
- 根及上层页通常很热，易驻留 Buffer Pool，所以一次点查的物理 I/O 往往少于树高。
- 精确高度可从索引页 level 或诊断工具观察，不能按固定“千万行三层”回答所有表。

## 边界与验证
Q: B+ 树索引存在但点查仍慢，应沿哪条链验证？
A:
- 先看计划是否使用预期 key 和完整 key_len，再看估算/实际 rows 是否接近。
- 区分根到叶 I/O、二级回表、锁等待、MVCC 回溯、结果网络发送和 CPU collation 比较。
- 热点不存在于“树高”时，加索引无效；例如锁等待应看 `data_lock_waits`。
- 可用 `EXPLAIN ANALYZE`、Performance Schema file/io waits 和 Buffer Pool 指标建立证据链。
