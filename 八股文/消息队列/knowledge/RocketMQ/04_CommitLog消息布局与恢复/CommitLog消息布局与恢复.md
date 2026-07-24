# RocketMQ CommitLog 消息布局与恢复

> 基线：描述经典 DefaultMessageStore 的本地文件实现。云存储、分层存储或未来存储插件可能改变介质，但物理日志与逻辑队列分离的思想仍然重要。

## 01-物理组织
Q: CommitLog 在磁盘上怎样组织，文件名为什么能定位物理位置？
A:
- CommitLog 是 Broker 级共享顺序日志，不按 Topic 分文件；来自不同 Topic 和 Queue 的消息按到达顺序追加。
- 日志被切成固定大小的 MappedFile 段，文件名通常是该段第一字节的全局物理 Offset，并使用定长十进制表示。
- 给定 CommitLogOffset，可通过“Offset / 段大小”定位文件，再用“Offset % 段大小”定位文件内位置。
- 段式组织便于内存映射、顺序写、滚动创建、恢复扫描和按最旧文件批量删除。

## 02-记录布局
Q: 一条经典 CommitLog 记录内部包含哪些关键字段？
A:
- 头部包含总长度、MagicCode、BodyCRC、QueueId、Flag、QueueOffset、PhysicalOffset 和 SysFlag。
- 时间与来源相关字段包含 born timestamp/host、store timestamp/host；还有 reconsumeTimes 与事务相关物理偏移。
- 变长部分保存 body、Topic 和 properties，Tag、Keys、原 Topic、延迟级别等系统或业务属性会编码进 properties。
- 这些字段共同支持恢复校验、逻辑队列派发、查询、重试和事务，而不是只把 body 原样写进文件。

## 03-顺序追加
Q: 多个发送线程如何保证 CommitLog 中记录不会交叉写坏？
A:
- 存储层在追加关键区串行化对当前映射文件的写入，先计算完整记录长度和队列逻辑 Offset，再编码为连续字节。
- 记录必须整体落在当前段可用空间内；空间不足时写入文件结束标记并切换或创建下一个 MappedFile。
- 串行化会形成热点，但换来单日志顺序写和简单恢复；性能依靠短临界区、Page Cache 与批量磁盘写回。
- “磁盘顺序写快”不代表业务没有锁竞争，压测要同时看 PutMessageLock、刷盘和复制等待。

## 04-两种Offset
Q: QueueOffset 和 CommitLogOffset 为什么必须同时存在？
A:
- CommitLogOffset 是 Broker 共享物理日志的字节位置，用于定位完整消息记录。
- QueueOffset 是某个 `topic + queueId` 内从零递增的逻辑序号，用于消费进度和队列顺序。
- ConsumeQueue 把逻辑 QueueOffset 映射到 CommitLogOffset 与消息大小，使消费者无需扫描整个共享日志。
- 一条消息的业务顺序通常讨论 QueueOffset；磁盘恢复、复制和物理查找则围绕 CommitLogOffset。

## 05-序列化与长度
Q: 为什么 CommitLog 记录要保存总长度、MagicCode 和 BodyCRC？
A:
- 总长度允许恢复扫描器从一条记录跳到下一条，也能判断剩余文件空间是否足够。
- MagicCode 用于区分合法消息记录、文件结束空白标记和损坏数据，避免把随机字节当成消息解析。
- BodyCRC 可以发现消息体在存储或传输中的破坏，但不能替代副本、业务签名或端到端校验。
- 变长 Topic、properties 和 body 都要受长度限制，否则畸形数据可能造成越界、超大分配或无法恢复。

## 06-文件滚动
Q: 当前 CommitLog 段写满时发生什么？
A:
- 追加器判断剩余空间不足以容纳完整消息时，写入表示文件结束的特殊记录或填充，提交当前写位置。
- AllocateMappedFileService 可提前准备后续文件，减少真正切换时创建和映射大文件造成的延迟尖刺。
- 新消息从下一段起始 Offset 继续追加，物理 Offset 在整个 CommitLog 空间中单调增长。
- 文件滚动不是日志清理；旧段仍要等保留期、磁盘水位以及关联逻辑文件条件满足后才能删除。

## 07-正常恢复
Q: Broker 正常重启时怎样恢复 CommitLog 写位置？
A:
- Broker 从末尾少量 MappedFile 开始扫描，逐条校验记录长度、MagicCode 和 CRC，找到最后一条完整有效消息。
- 有效记录推进 mapped file 的 wrote/committed/flushed position，遇到非法或空白区域后截断后续逻辑位置。
- 然后校正 ConsumeQueue、IndexFile 等派生结构，使其不指向超过 CommitLog 有效末尾的数据。
- 逻辑索引可以从 CommitLog 重建，因此 CommitLog 是经典本地存储中的权威消息事实。

## 08-异常恢复
Q: 异常宕机后的恢复为什么比正常关闭更保守？
A:
- 进程被杀或机器掉电时，最后一段可能只有部分字节写入 Page Cache 或磁盘，且服务没有记录干净关闭状态。
- 恢复会从更靠前的安全文件开始扫描，验证每条记录并丢弃尾部不完整数据。
- 同步刷盘只能缩小已确认消息的丢失窗口，硬件缓存、文件系统和副本策略仍决定最终 RPO。
- 若物理日志和副本分歧，还必须结合 HA 选主规则，不能单凭某台机器文件更长就判定其正确。

## 09-删除与保留
Q: CommitLog 为什么按文件段删除，而不是消费一条删一条？
A:
- 多个 ConsumerGroup 拥有独立 Offset，一条消息被某个 Group 消费并不代表其他 Group 已完成。
- 顺序日志若逐条删除会产生随机写、碎片和复杂引用管理；按段滚动删除成本更低。
- 清理服务依据文件保留时间、磁盘空间水位和手工触发等条件删除最旧段，并同步清理失效逻辑索引。
- 因此消费 ACK 与物理删除解耦；落后 Group 可能因保留期结束而永久越过旧消息。

## 10-正确性审查
Q: 关于 CommitLog，哪些常见结论需要修正？
A:
- “每个 Topic 一个 CommitLog”错误；经典 Broker 的多个 Topic 共享物理 CommitLog。
- “消息写入 CommitLog 就一定已落盘”错误；内存映射写入与持久介质刷盘是两个阶段。
- “ConsumeQueue 丢失就消息丢失”通常不准确；只要 CommitLog 完整，逻辑索引可以重新派发重建。
- “顺序写没有随机 IO”过于绝对；索引、刷盘、读取冷数据和操作系统回写仍会产生其他 IO 行为。
