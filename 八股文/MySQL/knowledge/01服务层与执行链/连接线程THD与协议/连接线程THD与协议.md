# 连接、线程、THD 与客户端协议

## 结构定位
Q: 一个 MySQL 客户端连接在服务端对应哪些核心对象，THD 的职责是什么？
A:
- 经典 one-thread-per-connection 模型中，连接由监听线程接收，随后交给工作线程；企业线程池插件可以把连接与执行线程解耦。
- `THD` 是一次会话的核心上下文，持有连接协议对象、当前数据库、用户与权限、安全上下文、会话变量、诊断区、事务状态和正在执行的 `LEX/Query_block`。
- `THD` 不是 InnoDB 事务本身；进入 InnoDB 后通过 `thd_to_trx()` 关联 `trx_t`，一个 SQL 层会话可先后创建或复用存储引擎事务。
- 源码锚点：`sql/sql_class.h` 的 `THD`、`sql/conn_handler/connection_handler_manager.cc`、`sql/sql_connect.cc`。

## 协议与内存布局
Q: MySQL 经典协议的数据包和会话内存大致怎样组织？
A:
- TCP 建连后先完成初始握手：服务端发送 capability、随机 challenge 和认证插件信息，客户端回传能力位、用户名、认证响应及可选数据库。
- 包头为 3 字节 payload 长度加 1 字节 sequence id；超过单包上限的消息拆包，sequence id 用于本轮命令内排序，不提供跨命令可靠性。
- `NET` 维护读写缓冲，`Protocol_classic` 编解码结果集；字段元数据、行数据、OK/ERR 包均走同一经典协议状态机。
- 排序缓冲、join buffer、read buffer 等多为按会话或按执行算子分配；不能把 `max_connections × 所有 buffer 参数` 简化成精确内存公式，但必须按峰值并发评估。

## 请求执行算法
Q: 一条 COM_QUERY 从网络到开始执行经历什么关键路径？
A:
1. 工作线程从 socket 读取完整命令包，`do_command()` 解出命令字和 payload。
2. `dispatch_command()` 设置 THD 状态、审计信息和超时，COM_QUERY 进入 `mysql_parse()`。
3. 解析、预处理、权限检查和优化完成后，执行器通过 handler 接口访问存储引擎。
4. 行与元数据由 `Protocol` 编码进网络缓冲；语句结束时清理 statement arena、诊断区和临时对象，事务是否结束取决于 autocommit 和显式事务。

## 并发与代价
Q: “MySQL 一个连接一个线程”应怎样准确表述，它的主要代价是什么？
A:
- 社区版传统模型通常让活动连接绑定一个工作线程，但线程缓存可复用已退出连接的线程；并不意味着每次建连都创建全新 OS 线程。
- 连接空闲时仍占 THD、socket、栈和会话状态；执行时还会按需申请排序、连接和临时表内存。
- 高连接数会放大线程调度、内存峰值和 mutex 竞争；连接池的目的主要是限制并发和摊薄握手认证，而不是让数据库无限并行。
- 判断瓶颈要联合看 `Threads_connected`、`Threads_running`、连接创建速率、CPU run queue 和 Performance Schema waits。

## 边界与验证
Q: 排查 MySQL 连接暴涨或握手慢时应验证什么，而不是只调大 max_connections？
A:
- 用 `SHOW PROCESSLIST` 或 `performance_schema.threads` 区分 Sleep、执行中、锁等待和网络等待；连接多但 `Threads_running` 低通常不是 CPU 执行并发。
- 检查应用连接池上限、泄漏、超时与重试风暴，再看 `Aborted_connects`、`Connection_errors_%`、DNS 解析和 TLS/认证耗时。
- `max_connections` 只提高准入上限，不能增加 CPU、文件描述符或内存；盲目调大可能把过载从“拒绝连接”变成“全局雪崩”。
- 复现实验可对比短连接与连接池的 QPS、握手次数和 p99，并观察每连接内存及线程上下文切换。
