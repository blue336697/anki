# redisObject对象系统

> 版本基线：Redis 7.4 OSS。答案中的结构体与函数名以官方源码为准；版本差异会显式标注。

## 01-对象与底层结构的分工

Q: Redis 为什么要在具体数据结构外再包一层 redisObject？

A:
- `redisObject` 是命令层看到的统一值对象，`ptr` 才指向 SDS、quicklist、dict、zset、stream 等具体实现。
- `type` 回答“逻辑上是什么”：string/list/set/zset/hash/stream；`encoding` 回答“物理上怎么存”。
- 同一逻辑类型可切换编码，命令实现只需先按 `type` 校验，再按 `encoding` 分派，不必把存储方式暴露给客户端。
- `refcount` 支持共享对象和生命周期管理；`lru` 复用为 24 位 LRU 时钟或 LFU 元数据。
- 源码锚点：`src/server.h::struct redisObject`、`src/object.c`。

## 02-位域与内存布局

Q: Redis 7.4 的 redisObject 每个字段具体存什么？

A:
```c
struct redisObject {
    unsigned type:4;
    unsigned encoding:4;
    unsigned lru:24;
    int refcount;
    void *ptr;
};
```
- 4 位 `type` 和 4 位 `encoding` 共占一个字节语义空间，24 位 `lru` 与它们合成前 32 位。
- LFU 模式下，`lru` 的高 16 位是分钟级最近衰减时间，低 8 位是对数频率计数器。
- 在典型 64 位 ABI 上还要考虑指针对齐，不能只把字段位数相加就断言对象固定为 16 字节；以目标编译器 `sizeof(robj)` 为准。

## 03-type与encoding

Q: type 和 encoding 为什么不能混为一谈？请给出完整例子。

A:
- `OBJ_STRING` 可用 `int`、`embstr`、`raw`；`OBJ_LIST` 在 7.4 用 `quicklist`；`OBJ_SET` 可用 `intset`、`listpack` 或 `hashtable`。
- `OBJ_ZSET` 可用 `listpack` 或 `skiplist`，其中 `skiplist` 编码实际由 dict 与跳表组成。
- `TYPE key` 只暴露逻辑类型；`OBJECT ENCODING key` 才能观察物理编码。
- 编码切换通常由元素数量、单元素长度或值域触发，切换后一般不会因数据变小自动降回紧凑编码，避免反复转换抖动。

## 04-引用计数与共享

Q: refcount 如何工作？为什么 embstr 对象不能原地扩容？

A:
- 新对象通常 `refcount=1`；被多个容器或客户端参数持有时递增，释放引用时递减，到 0 才释放对象及 `ptr` 指向的数据。
- Redis 还存在整数共享对象和特殊静态引用计数，不能把所有对象都按普通堆对象释放。
- `embstr` 把 robj 与 SDS 放在同一块连续内存里，一次分配、一次释放；但 SDS 头部之前紧邻 robj，无法单独 `realloc`。
- 因此需要修改且空间不足时，embstr 会转成 raw，再让 SDS 独立扩容。

## 05-面试验证链

Q: 线上如何证明某个 key 的对象编码、空闲时间和频率，而不是凭印象回答？

A:
- `TYPE key` 看逻辑类型，`OBJECT ENCODING key` 看物理编码。
- `OBJECT IDLETIME key` 观察近似空闲秒数，但启用 LFU 淘汰策略时该字段被复用，不能同时得到传统 LRU idle。
- `OBJECT FREQ key` 在 LFU 策略下读取 8 位频率估计；它不是精确访问次数。
- `MEMORY USAGE key [SAMPLES n]` 估算对象及其底层分配，不等于进程 RSS。
- 追问时应同时说出“命令看到的类型—当前编码—触发转换条件—是否可逆”。
