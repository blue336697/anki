# 热点Key与BigKey

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-定义差异

Q: hot key 和 big key 为什么是两个维度？

A:
- hot key 是单位时间访问/带宽高度集中，value 可以很小；风险是单分片 CPU、网卡和连接队头阻塞。
- big key 是单 key 的元素数或字节数很大，访问不一定频繁；风险是 O(N) 操作、大响应、删除、复制和迁移。
- 一个 key 可同时又热又大，问题会相乘；也可能只满足一个维度。
- 阈值应按实例带宽、p99 和业务对象分布定义，没有通用“超过 10KB 就一定大”。

## 02-发现热点

Q: 如何从 Redis 内部和客户端两侧发现 hot key？

A:
- `redis-cli --hotkeys` 依赖 LFU 策略/频率信息并进行扫描，生产使用要评估开销。
- `MONITOR` 全量输出代价高，不适合长期生产；可用代理/客户端采样 key hash、命令和字节量。
- Cluster 看每节点 CPU/ops/network 不平衡，再下钻槽和 key；slowlog 不擅长发现“单次很快但次数极多”的热点。
- 发现后要区分读热、写热和大响应热，治理方式不同。

## 03-发现BigKey

Q: 怎样安全找 big key，为什么 DBSIZE 和 key 名长度没有用？

A:
- SCAN 遍历 key，按 TYPE 使用 STRLEN/HLEN/LLEN/SCARD/ZCARD/XLEN 取逻辑规模，配合 MEMORY USAGE 抽样实际字节。
- `redis-cli --bigkeys` 看各类型最大逻辑项，`--memkeys`/MEMORY USAGE 更接近内存；都要在副本/低峰并限制扫描。
- DBSIZE 只给 key 数，key 名短不代表 value 小；容器一个 key 可有百万成员。
- listpack/压缩采样使 MEMORY USAGE 也可能是估算，关键对象应多指标交叉验证。

## 04-治理方法

Q: hot key 和 big key 分别怎样治理？

A:
- 读 hot key：本地缓存、只读副本（接受陈旧）、复制多个带后缀 key 并路由；写 hot key 通常要业务分片/聚合。
- big collection：按时间/用户/桶拆 key，分页有界读取，避免全量聚合；String 按块或改对象存储。
- 删除用 UNLINK/分批 HSCAN+HDEL 等控制单次工作量，但分批期间要定义可见性。
- Cluster 迁槽不能拆单 key，hash tag 还可能阻止拆分，必须从 key 模型解决。

## 05-操作风险

Q: 为什么删除、过期和迁移 big key 都可能造成延迟？

A:
- DEL 需要同步递归释放底层元素；UNLINK 把释放后移，但摘除、估算和后台队列仍有成本。
- big key 到期会在访问/主动过期时触发同样释放与传播，TTL 不会让释放成本消失。
- Cluster MIGRATE 要序列化、传输、RESTORE 并删除整 key，阻塞/带宽与 value 字节相关。
- 监控 lazyfree_pending_objects、网络、复制 lag 和 p99，操作前先在副本测实际耗时。
