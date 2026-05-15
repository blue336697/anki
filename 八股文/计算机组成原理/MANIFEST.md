# 计算机组成原理 产物清单

- 目录：/Users/haojie.liu/personalProjects/anki/八股文/计算机组成原理
- 目标牌组：八股文::计算机组成原理::<大类>::<知识点>
- APKG 输出位置：/Users/haojie.liu/personalProjects/anki/牌组/八股文/计算机组成原理/计算机组成原理八股文.apkg

## 知识点

- 体系结构总览/冯诺依曼架构（5 张卡）
- CPU与指令/ISA与RISC-CISC（5 张卡）
- CPU与指令/CPU执行与流水线（5 张卡）
- CPU与指令/中断异常与系统调用硬件视角（5 张卡）
- CPU与指令/微程序控制与硬布线控制（5 张卡）
- CPU与指令/流水线冒险与分支预测（5 张卡）
- 存储系统/存储层次与局部性（5 张卡）
- 存储系统/CPU缓存与CacheLine（5 张卡）
- 存储系统/虚拟地址到物理地址（5 张卡）
- 存储系统/缓存一致性与MESI（5 张卡）
- 存储系统/内存对齐与结构体布局（5 张卡）
- 存储系统/NUMA与内存屏障（5 张卡）
- IO系统/总线DMA与零拷贝硬件基础（5 张卡）
- 程序表示/编译链接与装载（5 张卡）
- 程序表示/大小端补码与浮点数（5 张卡）
- 并行计算/SIMD与GPU基础（5 张卡）
- 性能分析/性能指标与瓶颈定位（5 张卡）

## 总计

- 17 个知识点
- 85 张卡
- 17 张配图

## 配图

- von_neumann_architecture.drawio / `.svg`
- isa_risc_cisc.drawio / `.svg`
- cpu_pipeline.drawio / `.svg`
- interrupt_syscall.drawio / `.svg`
- control_unit_design.drawio / `.svg`
- pipeline_hazards.drawio / `.svg`
- memory_hierarchy.drawio / `.svg`
- cache_line.drawio / `.svg`
- virtual_memory_translation.drawio / `.svg`
- mesi_states.drawio / `.svg`
- memory_alignment_layout.drawio / `.svg`
- numa_memory_barrier.drawio / `.svg`
- dma_io_path.drawio / `.svg`
- compile_link_load.drawio / `.svg`
- number_representation.drawio / `.svg`
- simd_gpu_parallel.drawio / `.svg`
- performance_bottleneck.drawio / `.svg`

## 覆盖评估

- P0 已覆盖：冯诺依曼架构、CPU 执行与流水线、存储层次、Cache/Cache Line、虚拟内存翻译、MESI、DMA/零拷贝、编译链接装载、数值表示、性能瓶颈定位
- P1 已覆盖：ISA/RISC/CISC、微程序控制与硬布线控制、流水线冒险与分支预测、内存对齐与对象/结构体布局、NUMA 与内存屏障、SIMD/GPU 基础
- 与已有操作系统牌组有交叉但角度不同：这里偏硬件和计组因果链，操作系统牌组偏内核机制
- 后续 P2 可补：RAID 与磁盘阵列、PCIe/中断合并、GPU 显存层次、JIT 与硬件优化更细关联
