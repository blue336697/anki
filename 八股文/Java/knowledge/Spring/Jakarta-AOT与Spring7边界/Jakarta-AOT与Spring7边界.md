# Jakarta、AOT 与 Spring 7 版本边界

## 01-Jakarta迁移
Q: Spring 6/7 的 `javax`→`jakarta` 迁移影响哪些代码？
A:
- Servlet、Persistence、Validation、Annotation 等 Java EE API 包名迁移到 `jakarta.*`。
- 业务 import、过滤器、JPA 实体、校验注解、容器版本和第三方库必须成套兼容。
- 仅批量替换包名不够，Tomcat/Jetty、Hibernate、Validator 和测试 mock 也需升级到对应代际。
- `javax.sql`、`javax.crypto` 等 Java SE 包不属于此次 Jakarta EE 迁移，不能全局替换所有 javax。
- 混用旧新 API 常表现为 ClassNotFound、NoSuchMethod、类型不兼容或条件装配失败。

## 02-Spring代际
Q: Spring Framework 5.3、6.2、7.0 的主要边界是什么？
A:
- 5.3 面向 Java EE `javax` 生态，开源支持已结束，遗留系统仍可能使用。
- 6.x 以 JDK 17 和 Jakarta EE 9+ 为基线，是 Spring Boot 3 的核心框架代际。
- 7.x 是 Spring Boot 4 的框架代际，继续提高 Jakarta 与依赖基线，生产迁移需验证生态兼容。
- 面试不应把“最低 JDK 17”说成推荐永远停留在 17；实际生产可选择 21/25 LTS。
- 版本回答要同时给出 JDK、Servlet/Jakarta、Boot、Framework 四条兼容轴。

## 03-AOT处理
Q: Spring AOT 在构建期做什么？为什么它不等于普通 JIT？
A:
- AOT 引擎分析 ApplicationContext，生成 Bean 注册、反射、资源和代理等运行时 hints。
- 目的是减少运行时动态发现，并为 GraalVM native image 的 closed-world 分析提供元数据。
- JVM AOT 处理后的应用仍可运行在 HotSpot；native image 则编译成本地可执行文件，是进一步的部署形态。
- 动态类路径扫描、运行时生成代理、反射和资源访问需可静态推断或显式 hints。
- AOT 改变扩展约束和测试需求，不是打开一个开关就保证所有库可原生化。

## 04-NativeImage权衡
Q: Spring Native Image 的主要收益和代价是什么？
A:
- 收益通常是更快启动、更低稳态基础内存和适合弹性/函数场景。
- 代价包括构建更慢、静态分析约束、动态能力受限、调试与 profiling 工具链不同。
- 峰值吞吐未必胜过充分暖机的 HotSpot，取决于工作负载和优化空间。
- 必须覆盖反射、序列化、代理、资源、JNI、TLS 和 observability agent 的集成测试。
- 长时间运行高吞吐服务未必需要 native image；应按启动 SLO 和成本模型选型。

## 05-正确性审查
Q: Spring 现代化迁移有哪些错误做法？
A:
- 把所有 `javax` 无差别替换成 `jakarta`：会破坏 Java SE API。
- 只升级 Boot 版本不升级容器/ORM/验证库：代际不匹配会在运行时失败。
- 把 AOT 和 JVM JIT 当同一概念：前者是上下文/元数据预处理，后者是运行时热点编译。
- 认为 native image 必然更快：启动、内存、峰值吞吐和动态能力是不同指标。
- 把 Spring 6 的知识全删掉：Boot 3 系统仍大量存在，应保留并标注与 7/Boot 4 的边界。
