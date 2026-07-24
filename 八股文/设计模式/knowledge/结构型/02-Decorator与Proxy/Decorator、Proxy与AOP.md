# Decorator、Proxy 与 AOP
## 01-Decorator
Q: Decorator 如何在不继承的情况下叠加职责？
A:
- 装饰器实现同一接口并持有被装饰对象，在调用前后增加缓存、计时、压缩等行为。
- 多个装饰器可组合且顺序有语义，例如 retry 外包 timeout 与反向结果不同。
- 它适合单对象能力叠加，避免为所有组合创建子类。
- 装饰器必须保持接口契约，不能意外改变异常和幂等性。
## 02-Proxy
Q: Proxy 与 Decorator 的意图差异是什么？
A:
- Proxy 控制对真实对象的访问，如远程、延迟加载、权限或生命周期；Decorator 强调增强职责。
- 结构相似但讨论设计时应说明意图；远程代理还隐藏网络失败，不能假装本地调用零成本。
- 动态代理要求接口或可覆写方法，self-invocation 等可能绕过代理。
- 代理不等于业务对象本身。
## 03-代码
Q: 如何用装饰器给 Repository 增加缓存？
A:
```java
final class CachedOrders implements OrderRepository {
    private final OrderRepository target; private final Cache cache;
    public Optional<Order> find(OrderId id) {
        return cache.get(id).or(() -> target.find(id).map(o -> { cache.put(id,o); return o; }));
    }
}
```
- 写路径必须定义失效/事务时机，否则读到脏数据。
## 04-AOP
Q: AOP 与 Proxy/Decorator 是什么关系？
A:
- Spring AOP 常用 JDK/CGLIB proxy 在方法边界织入事务、日志等横切关注点。
- Decorator 是显式对象组合，类型与顺序可见；AOP 装配集中但调用链较隐蔽。
- private/final/self-call 和代理创建方式影响是否拦截。
- 业务不变量不应藏在切面，切面适合技术策略。
## 05-边界
Q: 多层代理装饰会产生哪些问题？
A:
- 调用栈和异常来源难追踪，顺序错误造成 retry 扩大事务或缓存未提交数据。
- equals/hashCode、序列化和类型判断可能看到代理类。
- 每层都应有单一技术职责并暴露指标。
- 简单一次增强可直接组合，不必引入全局 AOP。

