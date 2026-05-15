# MOVED-ASK与HashTag
## MOVED卡
![image](csdn_61822c3eb3bf61b74c1db1b21e928ee6.png)
![image](csdn_89501aac7b6fd7157cf4b464035f284e.png)
![image](csdn_901a84fddba781fb6d9e75bc2e78d783.png)
![image](csdn_3991c8d474d14c6a7c42925209d7eca0.png)
![image](csdn_61822c3eb3bf61b74c1db1b21e928ee6.png)
![image](csdn_89501aac7b6fd7157cf4b464035f284e.png)
![image](csdn_4d55f58a2217cafd30cb38c357062805.png)
![image](csdn_cc9f39ffec0413445b0bf53da7ed7e0c.png)
![image](csdn_47fa4688f5e13ea65b7f7b54c96d3b10.png)
![image](csdn_9d5e6e721385fb923d2c473c2669f812.png)
![image](csdn_19c60351637c256353a5119c9c0ab020.png)
![image](csdn_fcebfc5d0e2eecdab9915a72128e85f9.png)
![image](csdn_71adb933bae3f800488b19e2673f2727.png)
![image](csdn_1587114b9a1db5f49702748d668f0480.png)
![image](csdn_9798d3047070ba1ceb81092ffe1f84eb.png)
Q: Redis Cluster 中 MOVED 重定向表示什么？
A:
- MOVED 表示客户端访问了错误节点
- 返回信息会告诉客户端该槽当前由哪个节点负责
- 客户端应更新本地槽位缓存
- 后续同槽请求应直接发往正确节点
- MOVED 通常表示槽位归属已经稳定变化

## ASK卡
![image](csdn_ee8f32a83bf2eedff508bdf70f5012e3.png)
![image](csdn_48048fe429f2deb38395ebefd8a7bdd5.png)
![image](csdn_41774cf81d55a0f2ad6bc9af6ecbb152.png)
![image](csdn_8f07aa9e2b8d50dae702835a53299c9f.png)
![image](csdn_507ff09bdcaae593c765779e639fa3ee.png)
![image](csdn_ee8f32a83bf2eedff508bdf70f5012e3.png)
![image](csdn_8c966e31805cd5a3e7679f71dd7d5931.png)
![image](csdn_b946d1e8096c6fa44b0a5116508a6df2.png)
Q: ASK 重定向和 MOVED 有什么区别？
A:
- ASK 通常出现在槽迁移过程中
- 它表示当前 key 临时应去目标节点查询
- 客户端发送到目标节点前要先发 `ASKING`
- ASK 不应让客户端永久更新槽缓存
- 面试表达：MOVED 是稳定归属变化，ASK 是迁移过程中的临时重定向

## HashTag卡
![image](csdn_001a43b067e1fc07a103487b4b0e74d3.png)
![image](csdn_60c8843cf4f83433a7d5bfb305f980f0.png)
![image](csdn_3b1dac3199bea8b6e975fa18cef7fe26.png)
Q: Redis Cluster hash tag 解决什么问题？
A:
- hash tag 使用 `{}` 中的内容参与槽计算
- 它能让相关 key 落到同一个 slot
- 这样可以执行部分多 key 命令或 pipeline 聚合操作
- 典型用法是 `user:{1001}:profile` 和 `user:{1001}:cart`
- 滥用 hash tag 会造成热点槽，破坏分片均衡

## 正确性审查卡
![image](csdn_04ab264143033a6d172705564c14e8af.png)
Q: MOVED、ASK 和 hash tag 有哪些常见误区？
A:
- “ASK 后要更新槽缓存”：错误。ASK 是临时迁移提示
- “MOVED 只是重试一次”：不完整。客户端还应刷新槽映射
- “hash tag 可以随便用”：危险。可能导致大量 key 集中到一个槽
- “跨槽 mget 一定不能优化”：可通过 hash tag 或客户端拆分并发处理
- “客户端不用理解重定向”：错误。Cluster 客户端能力直接影响稳定性