# Spring Bean 生命周期与扩展点

> 基线：Spring Framework 6.2/7.0。

## 01-创建主链
Q: 一个普通 singleton Bean 从定义到可用经历哪些关键阶段？
A:
1. `BeanDefinition` 提供类、作用域、依赖、工厂方法等元数据，BeanFactory 决定创建。
2. 实例化阶段调用构造器或工厂方法，得到尚未完成属性填充的原始对象。
3. 属性填充和依赖注入完成后，执行 Aware 回调。
4. `BeanPostProcessor#postProcessBeforeInitialization`、初始化方法、`postProcessAfterInitialization` 依次参与。
5. AOP 等后处理器可能在 after 阶段返回代理，因此容器最终暴露对象不一定是原始实例。

## 02-初始化顺序
Q: `@PostConstruct`、InitializingBean 和自定义 init-method 的顺序与选择是什么？
A:
- `@PostConstruct` 由相应 BeanPostProcessor 识别，通常先于 `InitializingBean#afterPropertiesSet`。
- 随后执行 BeanDefinition 配置的 init-method；同一个初始化意图不要重复散落到三个入口。
- Spring 6/7 使用 `jakarta.annotation.PostConstruct`；`javax.annotation` 属于旧生态边界。
- 初始化应完成本地不变量，不应执行不可控的长时间远程调用，否则会阻塞上下文刷新。
- 需要所有 singleton 就绪后再启动任务，可使用生命周期组件或应用就绪事件，而不是猜 Bean 创建顺序。

## 03-后处理器
Q: BeanFactoryPostProcessor 与 BeanPostProcessor 有什么根本区别？
A:
- BeanFactoryPostProcessor 处理 BeanDefinition/容器元数据，发生在普通 Bean 大规模实例化之前。
- BeanPostProcessor 处理具体 Bean 实例，可在初始化前后包装、校验或替换对象。
- `BeanDefinitionRegistryPostProcessor` 还能注册新的定义，配置类解析就依赖类似扩展链。
- AOP 自动代理创建器是重要 BeanPostProcessor；它根据 Advisor 判断是否返回代理。
- 扩展器本身应尽早创建，过早实例化普通 Bean 可能让其绕过完整后处理链。

## 04-销毁
Q: Spring Bean 销毁时会发生什么？为什么原型 Bean 不一样？
A:
- 容器关闭时对受管理 singleton 执行销毁前后处理、`@PreDestroy`、DisposableBean 和自定义 destroy-method。
- 容器负责调用回调，不代表底层线程池/客户端一定自动优雅耗尽，Bean 自己需实现关闭语义。
- prototype Bean 创建后交给调用者，容器通常不跟踪其完整销毁生命周期。
- Web request/session scope 由相应 scope 管理销毁时机。
- 强制杀进程、崩溃或 OOM 不保证回调执行，关键资源不能只依赖 shutdown hook 保证一致性。

## 05-正确性审查
Q: Bean 生命周期有哪些常见误区？
A:
- “构造器执行完 Bean 就可用”：错误，注入、初始化和代理可能尚未完成。
- “Spring 注入的永远是原始对象”：错误，AOP 后常是代理。
- “@PostConstruct 来自 javax”：现代 Spring 6/7 主线是 jakarta。
- “prototype 也由容器自动销毁”：通常错误。
- “所有初始化都放构造器最好”：构造器适合建立基本不变量，但此时部分容器能力和代理尚不可用。
