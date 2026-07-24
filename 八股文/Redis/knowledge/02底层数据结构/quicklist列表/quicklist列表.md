# quicklist列表

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-两层结构

Q: quicklist 为什么是“链表 + listpack”，而不是纯链表或单个大数组？

A:
- quicklist 顶层是双向链表，每个 `quicklistNode` 的 `entry` 通常指向一个 listpack。
- 单个大 listpack 中部修改搬移成本太高；纯链表每元素指针和独立分配浪费大、缓存局部性差。
- 分块后，跨块定位沿链表，块内连续存储；在内存开销和修改成本之间折中。
- `quicklist` 保存 head、tail、总元素 count、节点数 len、fill 和 compress depth。

## 02-node字段

Q: quicklistNode 的关键字段和位域分别表示什么？

A:
- `prev/next` 连接节点；`entry` 指向 listpack 或压缩后的 quicklistLZF；`sz` 是未压缩 entry 字节数。
- `count:16` 是节点内元素数；`encoding` 区分 RAW/LZF；`container` 区分 PACKED/PLAIN。
- `recompress` 标记临时解压后需重新压缩；`dont_compress` 防止正在使用的节点被压缩。
- 大到不适合装进 listpack 的单元素可用 plain node，避免强塞导致昂贵搬移。

## 03-fill参数

Q: list-max-listpack-size=-2 到底表示什么？

A:
- quicklist 的 fill 可按正数限制每节点元素数，也可用负数表示近似字节上限。
- 默认 `-2` 表示每个 listpack 目标约 8 KiB；其他负值对应更小/更大的预设尺寸。
- 节点过满时插入会新建或拆分节点；删除后可能尝试合并相邻节点。
- 调大块可省链表节点但增加 memmove 和局部修改成本；调小块则相反。

## 04-压缩深度

Q: list-compress-depth 如何控制 quicklist 的 LZF 压缩？

A:
- 0 表示不压缩；正数 N 表示首尾各保留 N 个节点不压缩，中间节点可压缩。
- LPUSH/RPUSH/LPOP/RPOP 热路径集中在两端，所以端部保留 raw，避免每次操作都解压。
- 访问中间压缩节点时先解压，操作完成按 `recompress` 再压回；省内存但增加 CPU 和尾延迟。
- 已很小或压缩收益差的节点会跳过压缩，不能把压缩率当固定值。

## 05-命令复杂度

Q: 为什么 LINDEX/LINSERT 可能慢，而两端 push/pop 很快？

A:
- 两端操作直接定位 head/tail 节点，再在 listpack 端部修改，通常接近 O(1)。
- LINDEX 会从更近的一端跨 quicklistNode 计数，再在目标 listpack 内定位，最坏 O(N)。
- LINSERT 还要比较元素并可能在连续字节中 memmove/拆节点，value 越大成本越高。
- `LRANGE 0 -1` 的返回和网络成本至少 O(总字节数)，即使内部遍历很高效也会形成大响应。
