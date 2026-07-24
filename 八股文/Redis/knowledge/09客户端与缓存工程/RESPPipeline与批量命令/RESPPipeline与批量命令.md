# RESPPipeline与批量命令

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-RESP帧

Q: RESP2 请求 `SET k v` 在字节层是什么结构？

A:
```text
*3

$3
SET

$1
k

$1
v

```
- 数组声明参数数，每个 bulk string 声明字节长度；因此 value 可含空格、换行和零字节。
- Redis 解析的是字节长度，不依赖文本分隔猜测；RESP3 扩展了 map/set/push 等回复类型。
- Pipeline 只是连续发送多帧合法请求，不引入新的服务端事务协议。

## 02-Pipeline原理

Q: Pipeline 为什么能提高吞吐？

A:
- 非 pipeline 时每条命令经历发送→等待 RTT→下一条，客户端单连接吞吐受 RTT 限制。
- pipeline 把多条请求连续写入 socket，服务端仍按顺序解析执行，回复也按顺序返回。
- 节省的是网络往返和系统调用/调度开销，不会降低命令本身 CPU 复杂度，也不提供原子性。
- 批次过大使服务端 query/output buffer、客户端内存和队头阻塞增长。

## 03-MGET对比

Q: MGET 和 Pipeline 多个 GET 的区别是什么？

A:
- MGET 是一条多 key 命令，一次解析并生成一个数组回复；单实例通常比多个 GET pipeline 协议开销更低。
- Pipeline 是客户端传输技术，可混合命令；服务端仍逐条执行并逐条产生结果。
- Cluster 中 MGET 要求 key 同槽，否则 CROSSSLOT；cluster client 的 pipeline 可按节点分组并并行多个连接。
- 两者返回总字节都相同量级，大 value 时瓶颈仍是网络和输出缓冲。

## 04-错误与顺序

Q: Pipeline 中第 3 条命令报错，第 4 条还会执行吗？

A:
- 会。pipeline 没有事务语义，服务端按输入顺序独立执行，每条产生自己的成功/错误回复。
- 客户端必须按位置匹配每个 future/result；不能因为一次 write 成功就认为所有业务命令成功。
- 连接在中途断开时可能出现“不知道哪些已执行”的不确定结果，重试必须幂等。
- 要原子批量用 MULTI/EXEC 或 Lua，但仍应控制批量大小。

## 05-批次调优

Q: Pipeline batch size 应怎样确定？

A:
- 小批次 RTT 摊销不足；大批次增加内存、单连接独占时间和失败重试范围。
- 以“命令数 + 请求字节 + 预期响应字节”三维限制，而不是固定 1000 条适配所有 value。
- 压测 p50/p99、吞吐、client output buffer、网络带宽和 GC；在 Cluster 还要看每节点分组倾斜。
- 对在线流量设置上限和背压，避免生产突发把 pipeline 当无限队列。
