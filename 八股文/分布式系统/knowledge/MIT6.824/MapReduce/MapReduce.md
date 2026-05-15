# MapReduce

## 概念卡
Q: MapReduce 的编程模型是什么？为什么它适合大规模离线计算？
A:
- MapReduce 把计算拆成 Map 和 Reduce 两类函数，用户只关心 key/value 转换逻辑
- Map 读取输入分片，输出中间 key/value；框架按 key 分区、排序、shuffle 后交给 Reduce
- Reduce 聚合相同 key 的所有 value，输出最终结果
- 框架负责并行调度、任务重试、数据分片、失败恢复和中间文件管理
- 面试表达：MapReduce 用受限编程模型换来了框架层面的自动并行化和容错

## 架构卡
Q: MIT 6.824 Lab1 中 Coordinator 和 Worker 分别负责什么？
A:
- Coordinator 维护 Map/Reduce 任务状态、分配任务、检测超时任务并重新调度
- Worker 通过 RPC 向 Coordinator 拉取任务，执行 Map 或 Reduce，然后汇报完成
- Map Worker 读取输入文件，调用用户 mapf，按 reduce 分区写出中间文件
- Reduce Worker 读取属于自己分区的所有中间文件，按 key 排序分组，调用 reducef 写最终结果
- 这种设计让 Worker 无状态化，Worker 崩溃后 Coordinator 可以把任务重新派发给其他 Worker

## Shuffle 卡
Q: MapReduce 中 shuffle 的作用是什么？中间文件为什么按 reduce 分区？
A:
- shuffle 负责把 Map 输出的中间 key/value 按 key 聚集到对应 Reduce
- 每个 Map 任务会生成 `nReduce` 个中间文件，通常用 `hash(key) % nReduce` 决定分区
- 这样同一个 key 一定落到同一个 Reduce 分区，Reduce 才能看到该 key 的全部 value
- Reduce 阶段需要读取所有 Map 产生的本分区文件，再排序和分组
- 面试重点：Map 并行的是输入分片，Reduce 并行的是 key 空间分区

## 容错卡
Q: MapReduce 如何处理 Worker 崩溃和任务重复执行？
A:
- Coordinator 给任务设置超时时间，Worker 领取任务后长时间不汇报完成，就认为该任务可能失败
- 失败或超时任务会被重新置为 idle，分配给其他 Worker 重新执行
- Map/Reduce 输出要么使用临时文件 + 原子 rename，要么保证最终命名确定，避免半成品被 Reduce 读取
- 因为任务可能重复执行，Map 和 Reduce 函数应尽量是确定性的、无外部副作用
- 面试亮点：容错不是让任务不失败，而是让失败任务可以安全重跑

## 调度卡
Q: MapReduce 为什么必须先完成所有 Map 再进入 Reduce？
A:
- Reduce 需要读取每个 Map 对应分区的中间输出
- 如果部分 Map 未完成，Reduce 无法保证某个 key 的 value 集合完整
- MIT Lab 简化实现通常按阶段推进：Map 全部完成后再分配 Reduce
- 真实系统可以更流水化地拉取已完成 Map 输出，但 Reduce 的最终聚合仍依赖所有相关 Map 输出完成
- 面试边界：MapReduce 更适合批处理，不适合低延迟在线请求链路

## 正确性审查卡
Q: MapReduce 有哪些常见误区？
A:
- “MapReduce 只是一堆线程并发”：不完整。核心是数据分区、shuffle、失败重试和确定性任务语义
- “Worker 崩溃任务就失败”：错误。Coordinator 会超时重派任务
- “Reduce 可以任意提前结束”：错误。它必须看到负责 key 空间里的完整中间数据
- “Map 输出直接给 Reduce 内存传输”：MIT Lab 中通常通过中间文件交接，真实系统也会有落盘/网络 shuffle
- “重试一定安全”：不一定。只有任务输出和用户函数没有不可控副作用时才安全
