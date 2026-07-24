# sendfile、splice、mmap 与零拷贝边界

> 基线：“零拷贝”通常指减少 CPU 在内核/用户缓冲之间的数据复制，不代表 DMA、协议处理和物理数据移动全部消失。

## 01-传统发送
Q: 传统 `read(file) -> write(socket)` 有哪些数据移动？
A:
- 设备 DMA 把文件块读入内核 page cache；read 再把数据从内核页复制到用户 buffer。
- write 把用户 buffer 数据复制/引用到 socket 发送路径，协议栈构建 skb 后由网卡 DMA 读取。
- 用户态需要两次系统调用和一次往返用户处理，CPU copy 与缓存污染在大文件传输中明显。
- 文件已在 page cache 时省掉磁盘 DMA，但内核到用户、用户到 socket 的复制仍可能存在。

## 02-mmap-write
Q: `mmap + write` 能减少哪一次复制？
A:
- mmap 把文件 page cache 页映射到用户地址，应用访问不需要 read 把文件内容复制进另一个用户 buffer。
- 随后的 write(socket) 仍可能从用户映射页复制到 socket buffer 或建立引用，取决于协议实现。
- mmap 引入 page fault、VMA、TLB 和映射生命周期成本，小文件或一次性传输未必更快。
- 应用可直接解析数据是其优势；只转发文件时 sendfile 通常更简单。

## 03-sendfile
Q: sendfile 如何减少文件到 socket 的用户态复制？
A:
- 应用传入输入文件 fd 和输出 socket fd，内核在 VFS/page cache 与网络发送路径之间传递数据。
- 用户态不需要分配 buffer，也不读取/重新写回字节，减少系统调用和 CPU copy。
- 网络栈可通过 page fragment/reference 让 skb 引用缓存页，网卡再 DMA 发送，具体取决于硬件与 offload。
- 若应用需要压缩、加密或修改内容，数据仍可能进入其他处理路径，sendfile 不适合任意变换。

## 04-splice
Q: splice 的 pipe 中间层有什么作用？
A:
- splice 在两个 fd 之间移动/引用页数据，其中至少一端通常是 pipe；pipe buffer 可持有页引用而非复制内容。
- 文件可 splice 到 pipe，再从 pipe splice 到 socket，构建内核内的数据管道。
- tee 可复制 pipe buffer 引用到另一 pipe，vmsplice 可把用户页接入 pipe，但生命周期和 pin 语义更复杂。
- 支持程度取决于 fd 类型和文件系统，不是任意两个设备都能真正无复制。

## 05-copy_file_range
Q: `copy_file_range` 与 sendfile 有什么不同？
A:
- 它表达文件到文件的范围复制，允许文件系统或存储使用 reflink、服务端复制等更高效实现。
- sendfile 常用于文件到 socket 发送，历史接口语义和支持目标不同。
- copy_file_range 可能回退到数据复制，跨文件系统、配额和稀疏文件语义要检查返回值。
- 它只复制内容范围，不自动替应用完成 fsync、元数据事务和崩溃协议。

## 06-MSG_ZEROCOPY
Q: socket `MSG_ZEROCOPY` 为什么需要异步完成通知？
A:
- 发送路径可能直接引用用户页供网卡 DMA，系统调用返回时硬件尚未完成，应用不能立即复用/释放 buffer。
- 内核通过 error queue 等机制通知一批 zerocopy 发送已完成，应用据此回收内存。
- pin 页、通知处理和小包管理成本可能高于普通 copy，通常只对大流量/大 buffer 有收益。
- 忽略 completion 会造成内存长期不可复用；零拷贝 API 改变了 buffer 所有权时序。

## 07-DMA
Q: DMA 为什么不等于整个链路“没有 CPU 参与”？
A:
- DMA engine 在设备和内存之间搬运数据，减少 CPU 逐字节复制，但 CPU 仍配置描述符、处理中断/完成和协议。
- 网卡收发还要进行 skb 元数据、TCP 状态、校验、拥塞控制和队列管理。
- IOMMU 地址映射、cache coherence 和页面 pin 都有成本；小请求时设置开销可能占主导。
- “零拷贝”应具体说明省掉哪一段 CPU copy，而不是营销式绝对描述。

## 08-TLS与压缩
Q: 加密或压缩为什么会破坏简单 sendfile 路径？
A:
- 用户态 TLS 需要读取明文、生成密文和记录头，普通 sendfile 无法让应用直接变换字节。
- kTLS 可把部分 TLS record 处理下沉内核，使 sendfile 与内核加密/网卡 offload 组合，但协议和 cipher 支持有限。
- 压缩、图片转换、动态模板等必须处理内容，复制往往不是主要瓶颈。
- 优化前应测 CPU profile、内存带宽和网络，不应为了零拷贝重构不适合的业务。

## 09-页生命周期
Q: 引用 page cache 页发送时，文件被 truncate 或回收会怎样？
A:
- 发送路径取得页引用并在完成前维持生命周期，普通回收不能释放仍被引用的页。
- truncate、写入和网络发送并发需要文件系统与 page cache 锁定规则保证不会读到已释放内存。
- 长时间网络阻塞会让大量页被 socket/skb 引用，增加不可回收内存和缓存压力。
- 零拷贝减少复制但可能延长原始页所有权，必须配合发送队列背压。

## 10-正确性审查
Q: 关于零拷贝，哪些说法需要纠正？
A:
- “sendfile 一次数据都不复制”错误；设备 DMA 和协议/硬件路径仍搬运数据，具体内核也可能回退。
- “mmap 就是零拷贝且一定更快”错误；page fault、TLB、映射和后续 socket copy 仍存在。
- “零拷贝适合小消息”不一定；引用、pin 和 completion 管理可能比 memcpy 更贵。
- 正确回答应画出传统和优化路径，明确减少了内核到用户、用户到内核中的哪一次 CPU copy。
