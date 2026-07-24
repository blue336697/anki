# Spring Boot 启动、配置绑定与条件评估

> 基线：Spring Boot 3.5/4.1；自动配置候选以 `AutoConfiguration.imports` 机制为主。

## 01-启动阶段
Q: `SpringApplication.run` 从入口到应用可用经历哪些阶段？
A:
- 推断应用类型、加载 bootstrap 扩展并准备 Environment。
- 解析命令行、系统属性、环境变量和配置数据，完成属性源与 profile 组合。
- 创建对应 ApplicationContext，加载主配置类和 BeanDefinition。
- refresh 阶段执行工厂后处理器、注册后处理器、创建非懒加载 singleton，并启动内嵌服务器。
- 发布生命周期事件并执行 Runner；“端口已监听”“上下文刷新完成”“业务预热完成”是不同就绪点。

## 02-自动配置候选
Q: Boot 3/4 如何发现自动配置类？
A:
- 自动配置类通过 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 声明候选。
- `@EnableAutoConfiguration`/组合注解触发导入选择，读取候选并做 exclusions、排序与条件评估。
- `@ConditionalOnClass`、`OnBean`、`OnMissingBean`、`OnProperty` 等控制配置是否匹配。
- `spring.factories` 仍可承载其他工厂扩展，但不能继续说 Boot 3/4 只靠它发现自动配置。
- 候选列表只是入口，最终是否注册 Bean 取决于条件和用户配置。

## 03-属性源优先级
Q: 为什么同一个配置值在不同环境结果不同？
A:
- Environment 由多个 PropertySource 按优先级查询，命令行、系统属性、环境变量、配置文件和默认值可相互覆盖。
- profile 激活、配置导入和外部配置位置会改变参与合并的文档集合。
- 环境变量到属性名存在 relaxed binding 规则，但复杂 Map/List 覆盖语义不能靠直觉。
- Actuator env/configprops、启动调试和测试 ApplicationContextRunner 可帮助定位来源。
- 配置值属于敏感数据时不要直接在日志和诊断端点暴露。

## 04-ConfigurationProperties
Q: `@ConfigurationProperties` 为什么比大量 `@Value` 更适合结构化配置？
A:
- 它把同一前缀绑定为类型化对象，支持嵌套结构、转换、校验和 IDE metadata。
- 构造器/record 绑定便于表达不可变配置，启动时一次校验失败优于运行到请求才 NPE。
- `@Value` 适合少量表达式或单值，但分散后难以发现完整配置契约。
- 配置对象不应夹带复杂业务行为或远程调用。
- List/Map 的合并覆盖和默认值需用真实 profile 测试，不要只验证单一 application.yml。

## 05-排障
Q: 自动配置没有生效或意外生效，怎样排查？
A:
- 打开 condition evaluation report，确认候选配置、matched/not matched 原因。
- 检查 classpath 版本与包名，尤其 Jakarta 迁移和 optional dependency。
- 检查用户是否已声明同类型/同名称 Bean 导致 `@ConditionalOnMissingBean` 退让。
- 检查配置属性来源、profile 和 relaxed binding 后的实际值。
- 最小化上下文并用 ApplicationContextRunner 写条件测试，比反复改注解猜测更可靠。

## 06-正确性审查
Q: Boot 自动配置有哪些过时说法？
A:
- “Boot 3 仍只扫描 spring.factories 自动配置”：错误，主线是 AutoConfiguration.imports。
- “Starter 包含业务代码”：通常 starter 主要聚合依赖，自动配置实现可在独立 artifact。
- “只要依赖在 classpath 就必然创建 Bean”：还要满足全部条件且未被用户配置覆盖。
- “配置文件后写的一定覆盖前写的”：实际由 PropertySource/profile/import 优先级决定。
- “run 返回就代表所有外部依赖完成预热”：不一定，就绪语义需应用明确设计。
