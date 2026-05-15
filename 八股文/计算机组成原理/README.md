# 计算机组成原理

面向字节 5 年后端面试的计算机组成原理牌组，重点不放在教材式推导，而放在后端工程会被追问的底层因果链：

- CPU 指令执行、流水线、CPI/IPC
- 冯诺依曼架构、存储程序思想、哈佛架构对比
- ISA、RISC/CISC、微程序控制、硬布线控制
- 流水线冒险、分支预测、乱序执行的面试边界
- 中断、异常、系统调用的硬件视角
- 存储层次、CPU Cache、Cache Line、伪共享
- 内存对齐、对象/结构体布局、NUMA、内存屏障
- 虚拟地址到物理地址、TLB、缺页
- 多核缓存一致性、MESI 与 Java 内存模型的边界
- DMA、总线、零拷贝硬件基础
- 编译、链接、装载和程序内存布局
- 大小端、补码、浮点数
- 性能指标与瓶颈定位

## 构建

```bash
cd 八股文/计算机组成原理
python3 build_computer_arch_all.py
```

输出：

```text
牌组/八股文/计算机组成原理/计算机组成原理八股文.apkg
```

## 配图

`diagrams/` 下保留 `.drawio` 可编辑源文件和 `.svg` Anki 媒体文件。当前 macOS sandbox 中 draw.io CLI 导出 PNG 不稳定，因此 APKG 使用 SVG。

## 后续 P2 缺口

- RAID 与磁盘阵列
- PCIe、MSI-X、中断合并
- GPU 显存层次与 kernel 调度
- JIT 与硬件优化更细关联
