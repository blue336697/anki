# 深入理解Dubbo与实战（八）| Dubbo过滤器

type: Post
status: Published
date: 2022/08/20
summary: Dubbo过滤器
tags: Dubbo
category: 中间件

# Dubbo过滤器

- 概述

> 本章首先介绍Dubbo过滤器的总体概况，包括如何配置和使用一些框架自定义的规则约束,整个过滤器接口的总体结构，Dubbo框架中内置过滤器的不同用途；然后介绍众多的过滤器是如何初始化成一个过滤器链的
> 

## 1.Dubbo过滤器的概述

- 概述

> 做过Java Web开发的读者对过滤器应该都不会陌生，Dubbo中的过滤器和Web应用中的过滤器的概念是一样的，**提供了在服务调用前后插入自定义逻辑的途径**。过滤器是整个Dubbo框架中非常重要的组成部分，Dubbo中有很多功能都是基于过滤器扩展而来的。**过滤器提供了服务提供者和消费者调用过程的拦截，即每次执行RPC调用的时候，对应的过滤器都会生效。虽然过滤器的功能强大，但由于每次调用时都会执行，因此在使用的时候需要注意它对性能的影响**
> 

### 1.1 过滤器的作用

- 概述

> 我们知道Dubbo中巳经有很多内置的过滤器，并且大多数都是默认启用的，如ContextFilter。对于自行扩展的过滤器，要如何启用呢？
> 
> - 一种方式是使用@Activate注解默认启用；
> - 另一种方式是在配置文件中配置
- 配置示例

```xml
<!--消费方调用过程拦截-->
<dubbo:reference filter="xxx,yyy" />
<!--消费方调用过程默认拦截器，将拦截所有reference -->
<dubbo:consumer filter="xxx,yyy"/>
<!--服务提供方调用过程拦截-->
<dubbo:service filter="xxx,yyy" />
<!--服务提供方调用过程默认拦截器，将拦截所有service -->
<dubbo:provider filter="xxx,yyy"/>
```

- 需要注意的规则

> 
> 
> 1. 过滤器顺序：用户自定义的会在内置默认过滤器的后面，当然可以改变优先级；`filter="xxx,yyy"`这种写法，前者先执行
> 2. 剔除过滤器：对于不想用的默认过滤器使用`filter="-xxFilter"`会让xxFilter不生效
> 3. 过滤器的叠加：如果服务提供者、消费者端都配置了过滤器，则两边的过滤器不会互相覆盖，而是互相叠加，都会生效。如果需要覆盖，则可以在消费方使用`“-”`的方式剔除对应的过滤器

### 1.2 过滤器的总体结构

- 接口关系

> 
> 
> - **从图中可以看到所有的内置过滤器中除了 CompatibleFilter特别突出，只继承了 Filter接口，即不会被默认激活**，
> - 其他的内置过滤器都使用了@Activate注解，即默认被激活。Filter接口上有SPI注解，说明过滤器是一个扩展点，用户可以基于这个扩展点接口实现自己的过滤器。
> - 所有的过滤器会被分为消费者和服务提供者两种类型，消费者类型的过滤器只会在服务引用时被加入Invoker，服务提供者类型的过滤器只会在服务暴露的时候被加入对应的Invoker。**MonitorFilter比较特殊，它会同时在暴露和引用时被加入Invoker**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AB%EF%BC%89%20Dubbo%E8%BF%87%E6%BB%A4%E5%99%A8/image.png)
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AB%EF%BC%89%20Dubbo%E8%BF%87%E6%BB%A4%E5%99%A8/image%201.png)
> 
- 过滤器作用列表

> **每个过滤器的使用方不一样，有的是服务提供者使用，有的是消费者使用。Dubbo是如何保证服务提供者不会使用消费者的过滤器的呢？**
> 

> 答案就在@Activate注解上，该注解可以设置过滤器激活的条件和顺序，如`@Activate (group = Constants.PROVIDER, order = -110000)`表示在服务提供端扩展点实现才有效，并且过滤器的顺序是-110000
> 

==服务提供方==

| 过滤器名 | 作用 |
| --- | --- |
| AccessLogFilter | 打印每一次请求的访问日志。如果需要访问的日志只出现在指定的appender中，则可以在log的配置文件中配置additivity |
| ExecuteLimitFilter | 用于限制服务端的最大并行调用数 |
| ClassLoaderFilter | 用于切换不同线程的类加载器，服务调用完成后会还原回去 |
| ContextFilter | 为服务提供者把一些上下文信息设置到当前线程的 RpcContext 对象中，包括 invocation、localhost、remote host 等 |
| EchoFilter | 用于回声测试，在之前章节中已经有介绍 |
| ExceptionFilter | 用于统一的异常处理，防止出现序列化失败 |
| GenericFilter | 用于服务提供者端，实现泛化调用，实现序列化的检查和处理 |
| TimeoutFilter | 如果某些服务调用超时，则自动记录告警日志 |
| TokenFilter | 服务提供者下发令牌给消费者，通常用于防止消费者绕过注册中心直接调用服务提供者 |
| TpsLimitFilter | 用于服务端的限流，注意与ExecuteLimitFilter区分 |
| TraceFilter | Trace指令的使用 |

==消费者方==

| 过滤器名 | 作用 |
| --- | --- |
| ActiveLimitFilter | 用于限制消费者端对服务端的最大并行调用数 |
| ConsumerContextFilter | 为消费者把一些上下文信息设置到当前线程的 RpcContext 对象中，包括 invocation、localhost、 remote host 等 |
| DeprecatedFilter | 如果调用的方法被标记为已弃用，那么DeprecatedFilter将记录一个错误消息 |
| GenericImplFilter | 用于消费端，实现泛化调用，实现序列化的检查和处理 |
| FutureFilter | 在发起invoke或得到返回值、出现异常的时候触发回调事件 |

==特殊过滤器==

| 过滤器名 | 作用 | 属于 |
| --- | --- | --- |
| CompatibleFilter | 用于使返回值与调用程序的对象版本兼容，默认不启用。如果启用，则会把JSON或fastjson类型的返回值转换为Map类型；如果返回类型和本地接口中定义的不同，则会做POJO的转换 | 不属于任何 |
| MonitorFilter | 监控并统计所有的接口的调用情况，如成功、 失败、耗时。后续DubboMonitor会定时把该过滤器收集的数据发送到Dubbo-Monitor服务上 | 服务提供者+消费者 |

## 2.过滤器链初始化的实现原理

- 概述

> 这么多默认的过滤器实现类都会在扩展点初始化的时候进行加载、排序等。使用过Filter的读者都知道，所有的Filter会连接成一个过滤器链，每个请求都会经过整个链路中的每一个Filter。那么这个过滤器链在Dubbo框架中是如何组装起来的呢？
> 

> 服务的暴露与引用会使用Protocol层，而ProtocolFilterWrapper包装类则实现了过滤器链的组装。在服务的暴露与引用过程中，会使用ProtocolFilterWrapper#buildInvokerChain方法组装整个过滤器链
> 
- 源码分析之何时调用——`ProtocolFilterWrapper#buildInvokerChain`——`export&refer`

```java
//暴露服务的时候会调用buildlnvokerChain
public <T> Exporter<T> export(Invoker<T> invoker) throws RpcException {
	//此处会传入 constants.PROVIDER,标识自己是服务提供者类型的调用链
    return UrlUtils.isRegistry(invoker.getUrl()) ?
    	this.protocol.export(invoker) :
    	this.protocol.export(buildInvokerChain(invoker, "service.filter", "provider"));
}

//引用远程服务的时候也会调用 buildlnvokerChain
public <T> Invoker<T> refer(Class<T> type, URL url) throws RpcException {
	//此处会传入Constants.CONSUMER,标识自己是消费类型的调用链
    return UrlUtils.isRegistry(url) ?
    	this.protocol.refer(type, url) :
    	buildInvokerChain(this.protocol.refer(type, url), "reference.filter", "consumer");
}
```

==细节之——构造调用链——`buildlnvokerChain`==

> 构建节点链以后，节点类有一个invoke方法，会逐一的循环下一个节点；同时还会判断是异步还是同步等
> 

```java
private static <T> Invoker<T> buildInvokerChain(final Invoker<T> invoker, String key, String group) {
	//保存引用，后续用于把真正的调用者保存到过滤器链的最后
    Invoker<T> last = invoker;
    //获取所有的过滤器，包括有@Activate注解默认启动的和用户在XML中自定义配置的
    List<Filter> filters = ExtensionLoader.getExtensionLoader(Filter.class).getActivateExtension(invoker.getUrl(), key, group);
    if (!filters.isEmpty()) {
    	//对过滤器做倒排遍历，即从尾到头
        for(int i = filters.size() - 1; i >= 0; --i) {
            Filter filter = (Filter)filters.get(i);
            //注意这段逻辑，把last节点变成next节点，并放到 Filter 链的 next 中
            /*下面这一段逻辑就是FilterNode方法的逻辑
				this.invoker = invoker;
		        this.next = next;
		        this.filter = filter;
						*/
            last = new FilterNode(invoker, (Invoker)last, filter);
        }
    }

    return (Invoker)last;
}
```

- 为什么lash变成下一个节点的next

> 源码中为什么要倒排遍历呢？因为是通过从里到外构造匿名类的方式构造Invoker的，所以只有倒排，最外层的Invoker才能是第一个过滤器。
> 

> 我们来看一个例子： 假设有过滤器`A、B、C和Invoker`，会按照`C、B、A`倒序遍历，过滤器链构建顺序为： `C—Invoker，B—C—Invoker，A—B—C—Invoker`。**最终调用时的顺序就会变为A是第一个过滤器。**
> 

## 3.关于服务提供者&消费者的过滤器实现原理就不进行讲解，后续可自行了解