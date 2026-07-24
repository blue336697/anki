# Doublewrite、Page Flush 与部分写保护

## 结构定位
Q: InnoDB 已有 redo，为什么还需要 doublewrite？
A:
- redo 的重放通常假设目标页至少是可解析的旧完整页；若 16KiB 页写到一半断电，页结构本身可能损坏。
- doublewrite 先把待刷页批量顺序写到独立 doublewrite 文件并持久化，再写各自表空间位置。
- 恢复发现数据文件页损坏时，可取 doublewrite 中完整副本，再应用 redo。
- redo 防止丢失已提交修改，doublewrite 防 torn page，职责互补。

## 文件与队列
Q: MySQL 8.4 的 doublewrite 文件和 flush 来源怎样组织？
A:
- doublewrite 存储在 `#ib_<page_size>_<n>.dblwr` 等独立文件，而不是早期常讲的 system tablespace 固定区域。
- 每个 Buffer Pool instance 默认可有 flush-list 与 LRU-list doublewrite 文件；另有 single-page flush slot。
- 批量顺序写和一次 fsync 摊薄首次写成本，第二阶段再分散写数据文件。
- 加密或压缩表空间的页在 doublewrite 中也按相应规则处理。

## 刷盘算法
Q: 一批脏页从 Buffer Pool 到数据文件的完整顺序是什么？
A:
1. page cleaner 选取可刷页并确认相应 redo 已先持久化，满足 WAL。
2. 计算/写入页 checksum，把页拷入 doublewrite batch。
3. 顺序写 doublewrite 并 fsync，获得完整页副本。
4. 将各页写到真实表空间位置，完成后更新页状态；崩溃恢复按需要修复。

## 配置边界
Q: 什么情况下可以关闭 doublewrite？
A:
- 只有底层存储明确提供与 InnoDB 页写相匹配的原子写，并经过厂商/版本支持验证时才可能安全关闭。
- “SSD 很可靠”“文件系统有日志”“云盘有副本”都不自动等于 16KiB 原子写。
- `DETECT_ONLY` 只记录检测元数据，不提供完整页恢复，和 `DETECT_AND_RECOVER` 不等价。
- 基准测试关闭可测上限，但生产关闭是在用数据完整性换性能。

## 验证与排障
Q: doublewrite 成为写瓶颈时怎样处理？
A:
- 看 doublewrite pages/writes、fsync 延迟、数据文件写延迟、redo pressure 与 page cleaner 吞吐。
- 把 doublewrite 目录放到合适的低延迟介质、校准文件数与 I/O capacity，并排除设备饱和。
- 过多脏页、Buffer Pool 太小或 checkpoint 压力才是上游原因时，单改 doublewrite 无法解决。
- 任何关闭实验都必须包含断电/崩溃恢复与校验测试，而非只跑 TPS。
