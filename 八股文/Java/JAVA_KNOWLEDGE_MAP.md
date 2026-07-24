# Java 五年后端面试知识地图

> 单一知识源政策：`knowledge/<大类>/<知识点>/<知识点>.md` 是唯一可进入 Anki 的知识内容。  
> 根目录只保留本地图、构建脚本和构建报告；APKG 是派生产物，不反向编辑。  
> 版本基线：JDK 21/25、Spring Boot 3.5/4.1、Spring Framework 6.2/7.0。涉及旧版本时必须显式标注历史边界。

## 验收模型

每个 P0/P1 知识点应能回答：

1. 它解决什么问题，核心结论是什么？
2. 内部状态、数据结构或执行链怎样运作？
3. 为什么这样设计，成本是什么？
4. 在什么边界下失效，线上会表现成什么？
5. 如何验证和排障？
6. 哪些流行说法已经过时或不严谨？

## P0：必须掌握

| 大类 | 知识点 |
|---|---|
| Java 基础 | 对象语义、String、equals/hashCode、泛型擦除、反射、注解与 SPI、异常、IO/NIO、序列化、时间金额、值传递、record/sealed/pattern |
| 集合 | HashMap、ArrayList/LinkedList、Set、TreeMap/LinkedHashMap、Queue/Deque、不可变集合与选型 |
| 并发 | JMM/happens-before、volatile、CAS/原子类、synchronized/Monitor、AQS/Lock、线程生命周期与中断、ThreadLocal、线程池、BlockingQueue、ConcurrentHashMap、CompletableFuture、虚拟线程 |
| JVM | 类加载、运行时区域、对象布局、字节码、可达性与屏障、G1/ZGC、JIT/去优化、Safepoint、统一日志、OOM/泄漏与 native memory |
| Spring | IoC、Bean 生命周期、循环依赖、AOP 代理、事务执行链与失效、MVC、Boot 自动装配与启动、配置绑定、Jakarta/AOT、缓存/异步/事件 |
| Spring Security | FilterChain、认证上下文、授权、JWT/OAuth2、CSRF/CORS、密码存储 |
| 工程生态 | Maven、Jackson、HTTP Client/Feign、日志门面、测试边界 |
| JDK 演进 | 8、9–10、11–25 LTS 主线、虚拟线程与 preview 边界 |

## P1：深挖加分

| 大类 | 知识点 |
|---|---|
| 并发 | ForkJoin 工作窃取、StampedLock、并发背压、结构化并发/Scoped Values 状态 |
| JVM | JFR/NMT、类卸载、Code Cache、逃逸分析、引用处理、大对象与容器 CPU throttle |
| Spring | 条件装配报告、三级缓存真实边界、事务资源绑定、MVC 异步、可观测性、原生镜像限制 |
| 工程 | 序列化安全、依赖冲突治理、超时重试幂等、测试金字塔 |

## P2：专项扩展

- 编译器插件与字节码增强框架细节
- 特定厂商 JDK 的专属 GC/诊断能力
- 低频工具库 API 清单
- 旧 Springfox、CMS、PermGen 等仅用于遗留系统的历史知识

## 官方事实源

- OpenJDK JEP 与 Java SE 规范：语言、JVM、GC 和版本状态
- Spring 官方 reference/system requirements：Spring Boot/Framework/Security 行为
- JDK 源码：集合、JUC 与 HotSpot 版本实现
- Maven、Jackson 等项目官方文档：构建和库行为

任何实现常量都要带版本；任何 preview/incubator 特性都要写状态；任何旧实现都不得伪装成当前推荐。
