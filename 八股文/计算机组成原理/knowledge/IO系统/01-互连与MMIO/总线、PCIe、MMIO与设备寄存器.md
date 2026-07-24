# 总线、PCIe、MMIO 与设备寄存器

> 基线：现代系统多为分层点对点互连而非一根共享总线；CPU 通过地址化寄存器配置设备，再由 DMA 搬运批量数据。

## 01-互连职责
Q: 地址总线、数据总线、控制信号的经典抽象解决什么？
A:
- 发起方给出目标地址、读写类型和属性，经互连路由到内存或设备；数据通道传 payload，响应返回状态。
- 控制还涉及仲裁、顺序、缓存属性、错误和事务完成，不只是三根物理线。
- 现代片上 NoC、内存总线和 PCIe 是不同层互连，桥/Root Complex 转换地址与协议。
- 教材“系统总线”适合说明职责，不能据此认为所有设备共享同一带宽和时钟。

## 02-PCIe拓扑
Q: PCIe 的 Root Complex、Switch、Endpoint、Lane 分别是什么？
A:
- Root Complex 连接 CPU/内存体系与 PCIe fabric；Endpoint 是网卡、NVMe、GPU 等设备；Switch 扩展端口。
- 链路由若干 lane 组成，每 lane 全双工串行；代际速率、编码开销和 lane 数共同决定有效带宽。
- PCIe 是点对点分包交换，事务以 TLP 传输，读通常需要请求/完成往返，写可 posted。
- 带宽标称值不等于应用吞吐，还受协议、IOMMU、DMA、设备内部和 NUMA 路径影响。

## 03-枚举与BAR
Q: 系统怎样发现 PCIe 设备并给它分配可访问地址？
A:
- 固件/OS 枚举 bus-device-function，读取标准 configuration space 获取 vendor/device、class 和能力。
- 设备 BAR 声明所需 MMIO/IO 空间大小和属性，系统分配地址窗口并编程 BAR。
- 驱动根据匹配 ID 绑定，映射 BAR 后访问设备控制/状态寄存器。
- BAR 指向设备资源窗口，不是普通 RAM；错误缓存属性、宽度或访问顺序会产生不可预期行为。

## 04-MMIO
Q: Memory-Mapped IO 与普通内存 Load/Store 有什么不同？
A:
- MMIO 把设备寄存器映射进物理地址空间，CPU 使用 load/store 指令访问，由互连路由到设备。
- 寄存器可能读清零、写一清零、触发命令等副作用，不能像普通内存任意重复、合并或预取。
- 页表和映射属性通常标记为 device/uncacheable 或受控 write-combining，阻止不合适缓存。
- 驱动要用专用 accessor 和 barrier，普通指针解引用不保证编译器/CPU/总线顺序正确。

## 05-PIO与DMA
Q: Programmed IO 和 DMA 的数据路径有何差异？
A:
- PIO 由 CPU 反复读写设备数据寄存器，简单但占用指令和互连事务，适合少量控制数据。
- DMA 由 CPU 写描述符/doorbell 配置，设备成为总线主设备，直接在设备与内存间搬运批量数据。
- 控制面仍常用 MMIO，数据面用 DMA ring；DMA 完成通过内存状态与中断/轮询通知。
- DMA 不等于设备完全自治，缓冲生命周期、地址映射和错误恢复仍由驱动管理。

## 06-PostedWrite
Q: PCIe posted write 为什么需要读回或屏障来确认顺序/到达？
A:
- posted write 可在没有立即完成响应时进入桥和设备队列，CPU 指令退休不代表设备已经执行该写。
- 某些驱动写控制寄存器后读取同设备寄存器，利用 non-posted read completion 冲刷先前写。
- memory barrier 约束 CPU/编译器和架构可见顺序，但是否保证穿过具体桥需遵循平台 IO accessor 语义。
- 把 MMIO 当 volatile 普通内存通常不足，必须使用 OS 提供的 readl/writel 等抽象。

## 07-带宽与延迟
Q: 为什么 PCIe 设备访问适合批量而非细粒度往返？
A:
- 每个事务有 packet header、链路编码、路由和完成往返固定成本，小 payload 有效利用率低。
- DMA descriptor batching、doorbell 合并和大块传输能摊薄成本并提高 outstanding 并行度。
- 但批量过大会增加排队和尾延迟，实时服务需要在吞吐与 latency 间选 batch size。
- GPU/加速器频繁 CPU-device 小交互可能被 PCIe latency 主导，即使峰值带宽很高。

## 08-边界与排障
Q: 排查 PCIe/设备吞吐不足应检查哪些层次？
A:
- 检查协商代际与 lane 宽度、错误/重传、设备 NUMA 位置、IOMMU 和 DMA 映射。
- 再看队列深度、descriptor 大小、中断/轮询、CPU affinity、内存带宽与设备内部上限。
- “插在 x16 槽就是 x16 满速”错误，电气连接、CPU lane 分配和协商可能不同。
- “PCIe 带宽足够就无瓶颈”也错误，单次读延迟和软件提交路径可能先限制性能。

