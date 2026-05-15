# Cluster槽与重分片
## 槽卡
![image](csdn_9d5e6e721385fb923d2c473c2669f812.png)
![image](csdn_04ab264143033a6d172705564c14e8af.png)
![image](csdn_4d55f58a2217cafd30cb38c357062805.png)
![image](csdn_cc9f39ffec0413445b0bf53da7ed7e0c.png)
![image](csdn_47fa4688f5e13ea65b7f7b54c96d3b10.png)
Q: Redis Cluster 的槽机制是什么？
A:
- Redis Cluster 把 key 空间划分为 16384 个 hash slot
- 每个主节点负责一部分槽
- key 通过 CRC16 计算槽位
- 客户端根据槽位把命令发送到负责节点
- 槽机制让集群能水平分片和迁移数据

## 重分片卡
![image](csdn_71adb933bae3f800488b19e2673f2727.png)
![image](csdn_1587114b9a1db5f49702748d668f0480.png)
![image](csdn_8c966e31805cd5a3e7679f71dd7d5931.png)
![image](csdn_3b1dac3199bea8b6e975fa18cef7fe26.png)
![image](csdn_b946d1e8096c6fa44b0a5116508a6df2.png)
![image](csdn_8f07aa9e2b8d50dae702835a53299c9f.png)
![image](csdn_507ff09bdcaae593c765779e639fa3ee.png)
![image](csdn_ee8f32a83bf2eedff508bdf70f5012e3.png)
![image](csdn_8c966e31805cd5a3e7679f71dd7d5931.png)
![image](csdn_3b1dac3199bea8b6e975fa18cef7fe26.png)
![image](csdn_48048fe429f2deb38395ebefd8a7bdd5.png)
![image](csdn_41774cf81d55a0f2ad6bc9af6ecbb152.png)
![image](csdn_19c60351637c256353a5119c9c0ab020.png)
![image](csdn_fcebfc5d0e2eecdab9915a72128e85f9.png)
Q: Redis Cluster 重分片如何工作？
A:
- 重分片本质是把部分槽从源节点迁移到目标节点
- 迁移期间源节点处于 migrating 状态，目标节点处于 importing 状态
- 槽内 key 会逐步迁移，而不是一次性搬完整个集群
- 客户端可能收到 ASK 或 MOVED 重定向
- 重分片要关注迁移期间延迟、热点槽和客户端兼容性

## 故障转移卡
![image](csdn_901a84fddba781fb6d9e75bc2e78d783.png)
![image](csdn_001a43b067e1fc07a103487b4b0e74d3.png)
![image](csdn_9798d3047070ba1ceb81092ffe1f84eb.png)
Q: Redis Cluster 如何做故障检测和故障转移？
A:
- 节点之间通过 Gossip 交换状态信息
- 多个节点认为某主节点故障后，会标记 FAIL
- 故障主节点的从节点参与选举
- 获胜从节点晋升为主节点并接管槽
- 这提供分片场景下的高可用，但仍有异步复制丢数据窗口

## 正确性审查卡
![image](csdn_3991c8d474d14c6a7c42925209d7eca0.png)
![image](csdn_71adb933bae3f800488b19e2673f2727.png)
![image](csdn_1587114b9a1db5f49702748d668f0480.png)
![image](csdn_61822c3eb3bf61b74c1db1b21e928ee6.png)
![image](csdn_89501aac7b6fd7157cf4b464035f284e.png)
![image](csdn_60c8843cf4f83433a7d5bfb305f980f0.png)
Q: Redis Cluster 有哪些常见误区？
A:
- “Cluster 只要加机器就线性扩容”：不一定。热点 key 和热点槽会限制扩展
- “槽迁移对业务无感”：不完整。客户端要正确处理 ASK/MOVED
- “Cluster 保证强一致”：错误。主从复制通常仍是异步
- “所有多 key 命令都能跨节点执行”：错误。跨槽命令受限制
- “分片解决大 key 问题”：不一定。单个大 key 仍落在一个槽和一个节点上