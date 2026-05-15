![Copy-On-Write流程](knowledge/内存管理/PageFault与CopyOnWrite/copy_on_write.svg)

# PageFault与CopyOnWrite

## PageFault卡
Q: page fault 一定表示程序错误吗？
A:
- 不一定。page fault 是 CPU 发现页表映射缺失或权限不满足时触发的异常
- 合法缺页可能用于按需分页、栈增长、mmap 文件加载
- 写时拷贝也依赖写保护触发 page fault
- 非法地址或权限错误才会变成段错误等异常
- 面试表达：page fault 是操作系统懒加载和保护机制的入口

## COW卡
Q: Copy-On-Write 写时拷贝解决什么问题？
A:
- fork 后父子进程先共享物理页，并把页标记为只读
- 任一方写入时触发 page fault
- 内核复制该页，再让写入方修改自己的副本
- 它避免 fork 后立刻复制大量内存
- 对 fork 后立刻 exec 的场景尤其有效

## 缺页成本卡
Q: page fault 的成本取决于什么？
A:
- minor fault 只需建立映射或复制内存，不访问磁盘
- major fault 需要从磁盘读取页面，成本高很多
- COW fault 需要复制物理页
- mmap 文件首次访问可能触发文件页加载
- 排查性能时要区分 minor/major fault 数量和业务访问模式

## 正确性审查卡
Q: Page fault 和 COW 有哪些常见误区？
A:
- “缺页就是内存不够”：错误。很多缺页是正常按需机制
- “COW 不会消耗内存”：不准确。写入后仍会复制页
- “fork 很便宜所以随便用”：fork 页表和 COW 后写入仍有成本
- “major fault 和 minor fault 一样”：错误。major fault 可能涉及磁盘 IO
- “mmap 后文件全部进内存”：不一定。通常按需加载
