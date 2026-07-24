# ae事件循环

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-事件循环结构

Q: aeEventLoop 内部有哪些数组和链表？

A:
- `events[fd]` 是按文件描述符直接索引的已注册事件表，元素为 `aeFileEvent`，保存 readable/writable 回调和 clientData。
- `fired[]` 保存本轮多路复用器返回的就绪 fd 与掩码，避免边遍历内核结果边修改注册表。
- 时间事件由 `timeEventHead` 链接；`beforesleep`、`aftersleep` 是每轮阻塞前后的钩子。
- `apidata` 指向 epoll/kqueue/select 后端自己的状态；ae 层用统一 API 隔离平台差异。
- 源码锚点：`src/ae.h::aeEventLoop`、`aeFileEvent`、`aeTimeEvent`。

## 02-一轮循环

Q: aeProcessEvents 的一轮执行顺序是什么？

A:
1. 根据最近时间事件和调用标志计算 poll 超时。
2. 调用 `aeApiPoll`，Linux 下最终进入 epoll_wait，结果写入 `fired[]`。
3. 遍历就绪事件；通常先调用读回调，再按掩码调用写回调，`AE_BARRIER` 可改变同轮读写顺序。
4. 处理到期时间事件并执行其回调，回调返回下次调度间隔或 `AE_NOMORE`。
5. Redis 在外层 `aeMain` 中重复该过程，并借助 before/after sleep 做批量写、快速过期等工作。

## 03-单线程含义

Q: Redis 所谓“单线程”到底单在哪里？

A:
- 核心命令的解析后执行、数据结构修改和全局状态变更主要由主线程串行完成，因此普通命令之间天然没有共享内存锁竞争。
- 后台线程/进程一直存在：BIO 可做 lazy free、AOF fsync 等；RDB/AOF rewrite 常由 fork 子进程完成。
- Redis 6 起可配置 I/O threads 分担 socket 读写，但不会把普通命令逻辑任意并行执行。
- 所以“Redis 完全只有一个线程”是错的；准确说法是“核心命令执行模型以主线程串行为主”。

## 04-为什么仍会阻塞

Q: 事件循环是非阻塞的，为什么一个慢命令仍会拖住所有客户端？

A:
- 非阻塞 I/O 只保证等待 socket 时不占住线程；回调被调用后，命令本身仍在主线程运行。
- `KEYS`、超大集合聚合、巨型 Lua、删除大对象、fork/COW 压力都可能让一次回调长时间不返回。
- 在这段时间内，其他 fd 即使已就绪，也只能留在内核或 `fired[]` 等下一轮。
- 因此吞吐高不代表尾延迟安全；必须限制单条命令的工作量，使用 SCAN、UNLINK、分批处理和脚本时间预算。

## 05-源码与观测

Q: 如何把 ae 事件循环和线上延迟观测对应起来？

A:
- 源码从 `src/ae.c::aeMain/aeProcessEvents` 追到 `src/server.c::beforeSleep/afterSleep`。
- `LATENCY DOCTOR`、`LATENCY LATEST` 需要先配置 latency monitor；`SLOWLOG` 只记录命令执行阶段，不含网络排队和回包。
- 若 SLOWLOG 很干净但端到端延迟高，应继续查事件循环延迟、fork、AOF fsync、CPU steal、网络与客户端连接池。
- `redis-cli --intrinsic-latency` 测的是宿主机调度基线，不是 Redis 命令延迟。
