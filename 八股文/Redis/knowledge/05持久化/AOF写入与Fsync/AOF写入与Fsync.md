# AOF写入与Fsync

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-命令传播

Q: 写命令怎样变成 AOF 内容？AOF 是原始客户端请求的逐字节日志吗？

A:
- 命令执行并确定产生写效果后，传播层把规范化 argv 交给 `feedAppendOnlyFile`，编码为 RESP 命令追加到 `aof_buf`。
- 不是所有输入都原样记录：过期可改写为绝对时间形式，脚本效果/命令可能为确定性复制重写，SELECT 按 DB 需要插入。
- 没有产生数据变化或被禁止传播的命令不一定进入 AOF。
- AOF 是可重放命令流，不是网络抓包。

## 02-三层缓冲

Q: AOF 数据从命令到稳定介质要经过哪些层？

A:
1. Redis 用户态 `aof_buf`。
2. `write` 后进入内核 page cache；此时进程崩溃通常文件仍在，但机器掉电未必安全。
3. `fsync/fdatasync` 请求内核把数据刷到设备；设备缓存和存储栈还决定最终持久语义。
- 把“write 成功”等同于“绝不丢数据”是错误的。

## 03-fsync策略

Q: appendfsync always/everysec/no 的故障窗口和成本分别是什么？

A:
- always：每批/每事件循环写都同步，最小化窗口但延迟强依赖存储 fsync。
- everysec：主线程写 page cache，后台大约每秒 fsync；通常宣称故障可能丢约 1 秒，但极端调度/存储卡顿窗口可更复杂。
- no：Redis 不主动 fsync，交给 OS 刷脏页，吞吐高但窗口更不可控。
- Redis 7.4 默认 everysec；选择必须结合业务 RPO 和磁盘 p99。

## 04-fsync阻塞

Q: AOF everysec 为什么仍可能让主线程出现延迟？

A:
- 后台 fsync 进行时，主线程对同一文件的 write 可能因内核文件系统/设备锁和脏页回写而阻塞。
- `no-appendfsync-on-rewrite yes` 可在 rewrite 时跳过 fsync 降抖动，但扩大数据丢失窗口。
- AOF rewrite、RDB、宿主机其他 I/O 共享磁盘会抬高 fsync 尾延迟。
- 观察 `aof_delayed_fsync`、latency event、磁盘 await/util 和 slowlog 的差异。

## 05-AOF错误

Q: AOF write/fsync 失败后 Redis 会怎样，为什么必须监控？

A:
- 短写、ENOSPC、I/O error 会记录状态；根据配置和版本，后续写命令可能被拒绝以避免继续承诺不可持久化的数据。
- fsync 错误与 write 错误语义不同：数据可能已在 page cache，但稳定介质状态未知。
- 磁盘满不能靠 AOF rewrite 瞬间自救，rewrite 本身还需要额外临时空间。
- 监控 `aof_last_write_status`、`aof_last_bgrewrite_status`、磁盘空间/inode 和告警日志。
