# DRAM 单元、Bank、Row Buffer 与时序

> 基线：DRAM 访问不是均匀随机 O(1)；地址映射到 channel/rank/bank/row/column，行命中与刷新显著影响延迟。

## 01-存储单元
Q: DRAM bit 为什么需要刷新，读取为何具有破坏性？
A:
- 典型单元用一个电容表示电荷和一个晶体管选通，电荷会泄漏，所以内存控制器必须周期刷新。
- 读取把微小电荷差耦合到 bitline，由 sense amplifier 放大并恢复原值，过程本质上会扰动电容。
- DRAM 密度高、单位成本低，但需要激活、预充电和刷新；SRAM 用多晶体管锁存，快却面积大。
- Cache 常用 SRAM，主存常用 DRAM，是成本/容量/延迟权衡，不是“内存芯片速度都一样”。

## 02-层次组织
Q: channel、DIMM、rank、bank、row、column 分别是什么？
A:
- 内存控制器通过一个或多个 channel 并行传输；DIMM 上芯片组成 rank，共同提供总线宽度。
- 每个 rank 内有多个 bank，可独立保持打开行并交错服务；bank group 等结构进一步约束并行时序。
- bank 内二维阵列按 row 激活到 row buffer，再按 column 选择部分数据突发传输。
- 物理地址位如何映射这些层次由平台控制器决定，直接影响并行、行命中与安全分析。

## 03-ACTREADPRE
Q: 一次关闭行上的 DRAM 读取为何需要 ACTIVATE、READ、PRECHARGE？
A:
- ACTIVATE 选择 row，将整行感测到 row buffer；等待 tRCD 后才能发 READ/WRITE 选择 column。
- 数据经总线 burst 传出；切换同 bank 到另一 row 前需 PRECHARGE 恢复 bitline，再等待 tRP。
- 同一打开 row 的后续 column 访问是 row hit，可省 ACT/PRE；不同 row 是 conflict，延迟更高。
- 因此顺序/局部访问不仅对 Cache 有利，也提高 DRAM row-buffer 命中。

## 04-内存控制器
Q: 内存控制器如何调度请求，为什么会影响尾延迟和公平性？
A:
- 它维护各 bank 队列，遵守 tRCD、tRAS、tRP、总线方向切换等时序并尽量并行不同 bank。
- FR-FCFS 类策略优先 ready 的 row hit 提高吞吐，但连续热点可能让等待旧请求饥饿。
- 读写批处理减少总线 turnaround，却可能延迟另一方向；刷新期间相关 bank/rank 暂不可服务。
- 多核请求在控制器争用，单线程局部性优化可能影响系统级公平。

## 05-带宽与延迟
Q: DDR 标称速率、内存带宽和单次访问延迟是什么关系？
A:
- DDR 在时钟边沿传输，标称 MT/s 乘总线字节宽度给理论通道带宽，多个 channel 可叠加。
- 单次随机访问仍要付 cache/TLB、队列、ACT/PRE 等数十纳秒级链路，频率升高不等于延迟同比下降。
- 大量并行 outstanding 请求可把总线填满获得带宽，但指针依赖链无法并行，主要受延迟限制。
- STREAM 测带宽与随机延迟基准回答不同问题，不能用一个数字代表“内存速度”。

## 06-刷新与RowHammer
Q: DRAM refresh 和 RowHammer 各说明什么物理边界？
A:
- refresh 在数据丢失前重写行，容量/密度增加会带来更多刷新占用与功耗。
- RowHammer 反复激活某行可通过电气耦合扰动邻近行电荷，造成位翻转，突破纯软件隔离假设。
- 缓解包括提高刷新、目标行刷新、ECC 和访问监控，但不同代硬件有效性不同。
- 它说明页表权限保护依赖底层存储可靠性，硬件故障可影响系统安全。

## 07-ECC
Q: ECC 内存能检测/纠正什么，为什么不能替代所有可靠性措施？
A:
- 常见 SECDED 编码可纠正单 bit、检测双 bit 错误；更强 Chipkill 类方案跨芯片组织冗余。
- 内存控制器在读时校验 syndrome，纠正后可记录 corrected error，无法纠正时触发机器检查。
- ECC 增加容量、带宽/延迟和成本，不能修复地址/控制逻辑错误、软件越界或所有多 bit 模式。
- 线上应监控可纠正错误增长趋势，持续错误可能预示 DIMM 退化而非“已经自动修好无需管”。

## 08-工程优化
Q: 后端程序能从 DRAM 组织得到哪些可操作结论？
A:
- 顺序访问、分块和提高并行 outstanding miss 能更好利用 burst、bank 并行和行局部性。
- 大量随机指针链同时损害 cache、TLB 与 DRAM row buffer，往往是多层叠加延迟。
- NUMA 绑定决定请求走本地还是跨 socket 内存控制器；带宽饱和时增加线程可能只增加排队。
- 具体地址映射与时序依平台，优化应依 perf/uncore counters 和基准而非猜 bank 位。

