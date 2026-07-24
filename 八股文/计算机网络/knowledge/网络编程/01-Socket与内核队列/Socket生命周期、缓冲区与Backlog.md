# Socket 生命周期、缓冲区与 Backlog
## 01-Socket对象
Q: 一个 TCP socket 在内核中保存哪些关键状态？
A:
- 保存四元组、TCP 状态、序号/窗口/拥塞控制、定时器以及发送和接收队列。
- 文件描述符只是进程引用内核 socket 的句柄，dup/fork 后多个 fd 可共享同一对象。
- close 只有最后引用释放才真正启动关闭，阻塞/非阻塞是 fd/open-file 状态而非协议可靠性。
- 应用对象、fd、socket 和网络连接是不同层次，不能混称“一个连接对象”。
## 02-BindListenAccept
Q: 服务端 bind、listen、accept 分别做什么？
A:
- bind 选择本地地址端口，listen 把 socket 变为监听状态并建立握手/完成队列。
- 内核完成三次握手后把 child socket 放 accept queue，accept 取出并返回新的 connected fd。
- 监听 fd 不承载业务字节，child fd 各自拥有 TCP 状态和缓冲区。
- accept 慢会让完成队列积压，即使网卡和线程 CPU 尚未满也可能拒绝新连接。
## 03-发送缓冲
Q: send/write 成功是否表示对端应用已经收到？
A:
- 通常只表示字节已复制/引用进本机发送缓冲，之后才受 Nagle、cwnd、rwnd 和重传调度。
- 对端 ACK 只表示进入对端 TCP 栈，不代表应用读取、处理或持久化。
- 非阻塞写可能短写/EAGAIN，应用必须保存未写尾部并在可写时继续。
- 业务确认需要应用层响应或事务语义，不能用 send 返回值替代。
## 04-接收语义
Q: TCP recv 为什么可能少于请求长度或合并多次 send？
A:
- TCP 是字节流，内核按当前连续可用字节返回，不保留发送调用边界。
- 一次 recv 可只得半条消息，也可含多条；EOF 为返回 0，错误与 EAGAIN 另行处理。
- 协议必须使用定长、分隔符或长度前缀 framing，并限制长度防内存攻击。
- 循环读取要处理短读、半包、粘包与取消，所谓粘包不是 TCP 故障。
## 05-端口复用
Q: SO_REUSEADDR 与 SO_REUSEPORT 解决的问题有何不同？
A:
- REUSEADDR 常允许重启服务绑定仍有旧连接状态的本地地址，具体冲突规则依 OS。
- REUSEPORT 允许多个监听 socket 绑定同一地址端口，由内核把新流分配给不同 socket。
- 它可减少 accept 锁竞争并配合多核，但 hash 不均、热连接和 BPF 策略仍需观察。
- 两者不是绕过任意端口占用的万能开关，也不消除 TIME_WAIT 语义。
## 06-排障
Q: 如何从 socket 队列判断慢在发送端、网络还是接收应用？
A:
- Send-Q 持续大表示应用写入快于网络/对端窗口；Recv-Q 大表示本机应用读取慢。
- `ss -ti` 结合 rtt、cwnd、retrans、rwnd 和状态判断 congestion/receiver/application limited。
- 监听队列看 ListenOverflows/Drops、SYN_RECV 和 accept 速率，不能只看 ESTABLISHED。
- 进程栈、抓包和 socket 指标要同时间对齐，单个队列快照可能误导。

