# Buffered I/O、Direct I/O 与文件 mmap

> 基线：buffered/direct 描述是否经文件 Page Cache；同步/异步描述调用完成方式；二者是不同维度。

## 01-buffered-read
Q: 普通 `read()` 文件的完整数据路径是什么？
A:
- VFS 根据 file offset 进入文件系统读取迭代器，查询 inode address_space 中的 page cache。
- 命中时把缓存数据复制到用户 buffer；未命中时分配缓存页、提交块 IO 并等待或使用预读。
- 返回后更新共享 open file description 的 offset，除非使用 pread 指定独立位置。
- 一次 read 可因 EOF、信号或当前可用数据返回短读，调用方必须循环处理。

## 02-buffered-write
Q: 普通 `write()` 为什么通常比设备落盘快？
A:
- 内核先从用户 buffer 复制到 page cache，标记页 dirty 并更新 inode 大小/时间。
- 只要缓存和脏页预算允许，write 可在磁盘真正完成前返回，后续由 writeback 合并顺序写出。
- 脏页过多时写线程会被 balance_dirty_pages 节流，延迟突然接近设备吞吐。
- 成功返回只证明数据进入内核文件语义，不证明断电持久，需要 fsync 类协议。

## 03-O_DIRECT
Q: O_DIRECT 试图绕过什么，为什么使用困难？
A:
- Direct I/O 尽量在用户页与块设备之间传输，不把数据作为普通文件 page cache 内容长期缓存。
- 用户 buffer 地址、长度和文件 offset 常需满足设备/文件系统对齐；不满足可能失败或回退，具体依实现。
- 它减少双份缓存和大顺序 IO 的 cache 污染，但每次小 IO、未对齐和缺少合并会降低性能。
- O_DIRECT 不等于同步持久化，IO 完成和设备易失缓存 flush 仍是独立问题。

## 04-coherency
Q: 同一文件同时使用 buffered I/O 和 Direct I/O 有什么风险？
A:
- Page Cache 中可能存在脏页或旧页，Direct I/O 又直接访问存储，内核必须协调失效、回写和并发范围。
- 混用会增加锁、等待和语义复杂度，应用若没有严格同步可能观察到意外顺序。
- 数据库通常统一管理对齐 buffer、IO 调度和 cache 策略，避免随机混用。
- “绕过 page cache”是意图而非所有文件系统、所有请求都完全零缓存。

## 05-file-mmap
Q: mmap 文件相对 read 有什么数据路径差异？
A:
- mmap 建立文件 VMA，首次访问由 page fault 把 page cache 页映射进用户页表，应用随后直接 load/store。
- read 则由系统调用把 page cache 数据复制到用户 buffer，边界和错误更显式。
- mmap 避免重复 copy 和 syscall 频率，适合随机访问；但 page fault、SIGBUS、地址空间和修改同步更复杂。
- mmap 不是把整个文件一次读入内存，实际驻留仍按需。

## 06-shared-mmap
Q: `MAP_SHARED` 写文件映射后，何时对其他进程和磁盘可见？
A:
- 写入修改共享 page cache 页，映射同一页的进程可通过缓存一致性观察，但仍需应用级同步保证数据结构一致。
- 脏页由后台回写；`msync(MS_SYNC)` 或 fsync 可请求把修改推进持久化路径。
- CPU 可见、内核 page cache 可见、设备完成和断电持久是不同阶段。
- 修改文件大小、truncate 与映射并发可能产生 SIGBUS 或数据竞争，不能把 mmap 当普通共享数组随意使用。

## 07-append
Q: `O_APPEND` 能保证哪些原子性，不能保证哪些？
A:
- 内核在每次 write 时原子地把位置设为当前文件末尾并执行该次写，避免多个写者先 seek 后覆盖。
- 它不保证多个 write 调用组成的一条逻辑记录连续，中间可插入其他写者数据。
- 文件系统、网络文件系统和超大写入的原子边界需按具体实现确认，不能把 O_APPEND 等同事务日志提交。
- 日志应尽量单次 write 完整记录并处理短写，再通过 fsync 策略定义持久边界。

## 08-pread-pwrite
Q: pread/pwrite 为什么适合多线程随机文件访问？
A:
- 它们显式传入 offset，不修改 `struct file` 的共享当前位置，避免多线程在 seek+read 间竞态。
- 每次调用位置独立，但对同一文件范围并发写仍需业务同步，数据可能覆盖。
- direct I/O、文件锁、fsync 和 append 等语义仍需单独考虑。
- Java FileChannel positional I/O、数据库页读写常利用这种模型管理自己的逻辑页号。

## 09-shortIO
Q: 为什么文件和 socket 都必须正确处理短读短写？
A:
- read 可在 EOF、信号、终端/管道当前数据、非阻塞状态等情况下少于请求长度。
- write 可因信号、空间、配额、socket buffer 或设备错误只接受部分数据。
- 返回正数表示这部分已经完成，重试应从剩余位置继续；直接重发完整 buffer 会造成重复。
- `readn/writen` 循环要处理 EINTR、EAGAIN、0 和不可恢复 errno，不能假设一次调用完成。

## 10-正确性审查
Q: 关于文件 I/O，哪些说法需要纠正？
A:
- “O_DIRECT 就是异步 IO”错误；它控制 cache 路径，调用仍可同步阻塞。
- “mmap 文件不经过 Page Cache”错误；普通文件映射正是把 page cache 页映射到用户空间。
- “write 成功等于数据落盘”错误；buffered write 多数只写到 cache。
- “O_APPEND 保证多次 write 的整段业务事务原子”错误；原子性通常以单次写位置选择为边界。
