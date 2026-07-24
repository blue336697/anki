# HDD、SSD、FTL 与 RAID

> 基线：HDD 成本受机械寻道，SSD 受擦除块、FTL 和写放大；RAID 改变性能与容错但不等于备份。

## 01-HDD结构
Q: HDD 随机 IO 为什么远慢于顺序 IO？
A:
- 数据位于旋转盘片磁道/扇区，随机读需磁头 seek 到目标磁道并等待扇区旋转到头下。
- 机械寻道和旋转等待以毫秒计，远大于连续扇区传输；顺序请求可摊薄定位成本。
- OS/设备调度可合并和排序请求，队列深度提高吞吐却增加排队延迟。
- LBA 是逻辑块地址，现代盘内部映射和缓存使软件不直接操纵物理柱面。

## 02-NAND限制
Q: NAND Flash 的 page 和 erase block 为什么导致“不能原地覆盖”？
A:
- 读写以 page 为较小粒度，擦除以包含许多 page 的 block 为大粒度；写通常只能把擦除态位单向编程。
- 更新已有逻辑块需把新数据写到另一个空 page，再把旧 page 标记 invalid，不能直接覆盖。
- 空闲 page 不足时垃圾回收搬走 block 内有效页并擦除整块，产生额外读写和延迟尖峰。
- P/E 次数有限，控制器需 wear leveling 把磨损分散。

## 03-FTL
Q: Flash Translation Layer 保存什么，怎样处理一次逻辑覆盖写？
A:
- FTL 维护 LBA→物理 page 映射、有效位、空闲块和磨损状态，并借助 DRAM/cache 加速元数据。
- 新写采用 out-of-place：分配新 page、写数据、原子更新映射，再让旧 page 失效。
- 映射粒度越细随机写越灵活，但元数据大；掉电保护需保证数据与映射恢复一致。
- SSD 性能不是 NAND 芯片裸性能，控制器、并行 channel/die、固件和 over-provisioning 同样关键。

## 04-写放大
Q: SSD write amplification 从哪里来，TRIM 有什么作用？
A:
- 主机写少量数据，GC 可能搬迁同一 erase block 中大量仍有效页，NAND 实际写入大于 host writes。
- 随机小写、盘接近满和空闲块少会提高放大；顺序/对齐写与 over-provisioning 通常改善。
- 文件系统删除后发 TRIM/Discard 告知哪些 LBA 不再有效，FTL 可少搬这些 page。
- TRIM 不保证数据立即物理擦除，也不等同安全擦除或同步持久化。

## 05-队列并行
Q: NVMe 为什么使用多队列，queue depth 对性能有何影响？
A:
- NVMe 通过 PCIe，支持多个 submission/completion queue，可让多核独立提交并减少共享锁。
- SSD 内部有多 channel/die，需要多个 outstanding 请求才能填满并行资源和峰值带宽。
- queue depth 增大通常提吞吐，但排队时间和 P99 会升高；低延迟服务不应盲目追满设备。
- 队列、MSI-X vector、CPU 与 NUMA 内存应尽量亲和，避免完成路径跨核。

## 06-RAID级别
Q: RAID 0/1/5/6/10 的数据与校验怎样分布？
A:
- RAID0 条带化无冗余，容量/吞吐高但任一盘失败即阵列失败；RAID1 镜像保存多份。
- RAID5 分布式单校验可容忍一盘故障，RAID6 双校验可容忍两盘；可用容量分别扣一/两盘。
- RAID10 先镜像再条带，随机 IO 和重建通常友好但容量利用率约一半。
- 容错结论还依具体故障组合、控制器和布局，不能只背“能坏几块”而忽略同镜像组。

## 07-小写惩罚
Q: RAID5/6 的小随机写为什么有 read-modify-write penalty？
A:
- 未覆盖完整 stripe 时，控制器需读旧数据和旧 parity，计算差异后写新数据与新 parity。
- RAID5 典型一次逻辑小写涉及两读两写，RAID6 校验更多；完整 stripe write 可直接计算新 parity。
- 写缓存可合并为满条带，但必须有可靠掉电保护，否则确认后断电会丢失或形成 write hole。
- SSD 阵列内部 FTL 写放大与 RAID 写放大可能叠加。

## 08-可靠性边界
Q: 为什么 RAID 不是备份，fsync 也不等于所有硬件都已安全落盘？
A:
- RAID 主要应对部分设备故障，无法防误删除、软件 bug、勒索、静默损坏和整个机房故障；副本也可能同步错误。
- 备份需要独立故障域、历史版本和恢复演练；端到端 checksum 发现静默错误。
- fsync 建立 OS/文件系统承诺，但最终耐久还依设备 flush/FUA、缓存电源保护和固件正确实现。
- 可靠链路要明确每层何时确认、断电模型和恢复测试，不能只看接口名称。
