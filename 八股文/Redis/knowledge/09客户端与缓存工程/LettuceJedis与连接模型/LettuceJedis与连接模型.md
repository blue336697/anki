# LettuceJedis与连接模型

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-Lettuce复用

Q: Lettuce 为什么常说连接线程安全，它内部如何复用连接？

A:
- Lettuce 基于 Netty channel 和 event loop，把命令编码后排入同一连接；每条命令有对应 promise，按 RESP 顺序完成。
- 无事务/阻塞状态的常规异步命令可由多个调用方共享连接，因为写入和回复匹配在客户端框架内串行化。
- “线程安全”不等于无限并发：单连接仍有 socket 带宽、服务端顺序回复和 pending command 内存上限。
- 阻塞命令、事务、Pub/Sub 等有连接状态，通常应独占连接。

## 02-Jedis模型

Q: Jedis 连接为什么通常不能被多个线程直接共享？

A:
- 传统 Jedis connection 是同步阻塞 I/O，调用线程写请求后立即读对应回复；多线程交错会破坏请求/回复配对。
- 通常通过 JedisPool 借出独占连接，用完归还；池大小决定最大并发与等待。
- 连接池太小产生 borrow wait，太大则 Redis 连接数、线程和上下文开销上升。
- 新版本 API 可能演进，必须区分 JedisPooled/cluster 等封装，不能只背品牌结论。

## 03-队头阻塞

Q: 单个 Lettuce 连接多路复用时为什么仍会出现 head-of-line blocking？

A:
- Redis 在一个连接上按请求顺序执行并按顺序回复；前面的大命令/大响应未完成，后面小命令 future 也不能越过字节流。
- 客户端 event loop 若被业务回调阻塞，解码和 promise 完成同样积压。
- 将慢命令、阻塞命令、Pub/Sub 与普通低延迟流量分连接，能隔离队头阻塞。
- 连接多不是越多越好，应按流量类别和并发压测分池。

## 04-超时不确定性

Q: 客户端命令超时是否表示 Redis 没执行？

A:
- 不表示。请求可能尚未发出、已在网络、已执行但回复丢失，或回复在客户端队列中尚未完成。
- 对写命令盲重试可能重复扣减/发券；必须使用业务幂等 id、SET NX 状态机或数据库唯一约束。
- 客户端取消 future 通常只取消等待，不会从 Redis 事件循环撤回已发送命令。
- 监控应区分 connect timeout、command timeout、pool wait 和 server error。

## 05-Cluster拓扑刷新

Q: Cluster 客户端如何维护 slot map，为什么只依赖定时刷新不够？

A:
- 启动从 seed 节点获取槽拓扑；命令按 key slot 选连接。
- 收到 MOVED 立即更新目标/触发拓扑刷新；ASK 只做一次性 ASKING 跳转。
- 定时/自适应刷新补充节点新增、故障切换和长期未访问槽变化；seed 不必是永久中心。
- DNS、NAT、TLS advertised endpoint 错误会让 Redis 返回客户端不可达地址，需部署层配置正确 announce 信息。
