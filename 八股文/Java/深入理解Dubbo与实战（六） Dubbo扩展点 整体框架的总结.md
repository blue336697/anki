# 深入理解Dubbo与实战（六）| Dubbo扩展点 | 整体框架的总结

type: Post
status: Published
date: 2022/08/18
summary: Dubbo扩展点 | 整体框架的总结
tags: Dubbo
category: 中间件

# Dubbo扩展点

- 概述

> 前面我们已经了解过Dubbo的SPI扩展机制，本章主要介绍在整个框架中有哪些已有的接口是可以扩展的，主要涉及扩展接口的作用，原理性的内容相对较少。首先介绍整个框架中核心扩展点的总体大图，让读者对这些扩展点有一个总体的了解。其次从上到下介绍整个RPC层的扩展点。然后介绍Remote层的扩展点。最后会把其他一些零散的扩展点也简单介绍一下。
> 

## 1.Dubbo核心扩展点概述

- 开闭原则在Dubbo中的体现

> 业务开发的发展变化，作为一个框架既需要满足日常开发的需求，同样也要提供足够的扩展能力，使得用户可以再不改变内部代码的基础上按照接口约定做出自己的功能。**Dubbo使用扩展点来实现这个功能，在保持原有的逻辑结构不变每一层都提供了扩展接口**
> 

### 1.1 扩展点整体架构

- 按照使用者和开发者来分，Dubbo可以分为API层和SPI层。

> • API层让用户只关注业务的配置，直接使用框架的API即可
• SPI层则可以让用户自定义不同的实现类来扩展整个框架的功能
> 
- 按照逻辑来区分，那么又可以把Dubbo从上到下分为业务、RPC、Remote三个领域。

> 我们主要讲后面两个，可扩展的RPC和Remote层继续细分，又能分出7层，如下图
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image.png)

## 2.RPC扩展点

- 概述

> 按照完整的Dubbo结构分层，RPC层可以分为四层：Config、Proxy、Registry、Cluster。由于Config属于API的范畴，因此我们只基于`Proxy、Registry、Cluster`三层来介绍对应的扩展点。
> 

### 2.1 Proxy层扩展点

- 远程调用的代理执行者——代理对象

> Proxy层主要的扩展接口是ProxyFactoryo我们在使用Dubbo框架的时候，明明调用的是一个本地的接口，为什么框架会自动帮我们发起远程请求，并把调用结果返回呢？**整个远程调用的过程对开发者完全是透明的，就像本地调用一样。这正是由于ProxyFactory帮我们生成了代理类，当我们调用某个远程接口时，实际上使用的是代理类。**
> 
- 代理类远程调用过程

> 里面就是大概的一个过程图精简了很多细节，如如序列化等，主要是为了说明整个代理调用过程。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%201.png)

- ProxyFactory方法细节

> Dubbo中的ProxyFactory有两种默认实现:Javassist和JDK,用户可以自行扩展自己的实现，如CGLIB(CodeGeneration Library)。 Dubbo选用Javassist作为`默认`字节码生成工具，**主要是基于性能和使用的简易性考虑，Javassist的字节码生成效率相对于其他库更快，使用也更简单**。下面我们来看一下ProxyFactory接口有哪些具体的方法
> 

> 我们可以看到ProxyFactory接口有三个方法，每个方法上都有`@Adaptive`注解，**并且方法会根据URL中的proxy参数决定使用哪种字节码生成工具。第二个方法的generic参数是为了标识这个代理是否是泛化调用。**
> 

```java
@SPI("javassist")
public interface ProxyFactory {
    @Adaptive({"proxy"})
    <T> T getProxy(Invoker<T> invoker) throws RpcException;

    @Adaptive({"proxy"})
    <T> T getProxy(Invoker<T> invoker, boolean generic) throws RpcException;

    @Adaptive({"proxy"})
    <T> Invoker<T> getInvoker(T proxy, Class<T> type, URL url) throws RpcException;
}
```

- 默认已有扩展点的实现

> stub比较特殊，它的作用是创建一个代理类，**这个类可以在发起远程调用之前在消费者本地做一些事情**，比如先读缓存。它可以决定要不要调用Proxy
> 
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%202.png)
> 

### 2.2 Registry 层扩展点

- 概述

> Registry层可以理解为注册层，这一层中最重要的扩展点就是org. apache, dubbo. registry.RegistryFactory。整个框架的注册与服务发现客户端都是由这个扩展点负责创建的。该扩展点有`@Adaptive({"protocol"))`注解，可以根据URL中的protocol参数创建不同的注册中心客户端。例如：**protocol=redis,该工厂会创建基于Redis的注册中心客户端。因此，如果我们扩展了自定义的注册中心，那么只需要配置不同的Protocol即可**
> 
- 源码

> 使用这个扩展点，还有一些需要遵循的“潜规则”：
> 
> - 如果URL中设置了 check-false，则连接不会被检查。否则，需要在断开连接时抛出异常。
> - 需要支持通过usemame:password格式在URL中传递鉴权。
> - 需要支持设置backup参数来指定备选注册集群的地址。
> - 需要支持设置file参数来指定本地文件缓存。
> - 需要支持设置timeout参数来指定请求的超时时间。
> - 需要支持设置session参数来指定连接的超时或过期时间。

```java
@SPI(“dubbo”)
public interface RegistryFactory (
	@Adaptive(("protocol"})
	Registry getRegistry(URL url);
}
```

- 已有的扩展点实现

> 在Dubbo,有AbstractRegistryFactory已经抽象了一些通用的逻辑，用户可以直接继承该抽象类实现自定义的注册中心工厂。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%203.png)

### 2.2.1 以etcd作为注册中心

- 什么是etcd

> etcd是一种分布式键值存储系统，它提供了可靠的集群存储数据的途径。它是开源的，可以在GitHub上找到它的源码。**etcd使用了 Raft算法保证集群中数据的一致性，当leader节点下线时会自动触发新的leader选举，以此容忍机器的故障。应用可以在etcd中读写数据，例如： 把一些参数性的信息通过key-value （键值对）形式写入etcd,这些数据可以被监听，当数据发生变化的时候，可以通知监听者。**
> 
- etcd的应用及优点

> 虽然Dubbo默认支持ZooKeeper和Redis等注册中心实现，但是生产环境中使用较多的还是ZooKeeper。**后起之秀etcd广泛应用于Kubernates中（用于服务发现）**，经过了生产环境的考验。相比于ZooKeeper实现，基于etcd实现的注册中心有很多优点，例如：不需要每次子节点变更都重新全量拉取节点数据，大大降低了网络的压力。
> 

> 
> 
> 1. etcd使用增量快照，可以避免在创建快照时暂停。
> 2. etcd使用堆外存储，没有垃圾收集暂停功能。
> 3. etcd己经在微服务Kubernates领域中有大量生产实践，其稳定性经得起考验。
> 4. 基于etcd实现服务发现时，不需要每次感知服务进行全量拉取，降低了网络冲击。
> 5. etcd具备更简单的运维和使用特性，基于Go开发更轻量。
> 6. etcd的watch可以一直存在。
> 7. ZooKeeper会丢失一些旧的事件，etcd设计了一个滑动窗口来保存一段时间内的事件，客户端重新连接上就不会丢失事件了。
- etcd的数据结构设计

> 在理解ZooKeeper基础上，就很容易理解etcd的存储结构了。etcd注册中心所有元数据信息都是基于key-value （键值对）存储的，和ZooKeeper中节点和子节点不同，**etcd存储是通过前缀区分的**。
> 

> 在ZooKeeper中有`临时节点`的概念，它是通过TCP连接状态断开自动删除临时节点数据的。etcd注册中心也有临时节点的概念，但不是根据TCP连接状态，**而是根据租约到期自动删除对应的key实现的**。当provider和consumer上线时，会自动向注册中心写临时节点。**同时JVM关闭后也会及时删除临时key**
> 

> 其实etcd3没有树的概念，etcd3里面都是平铺展开的键值对，我们可以把展开的键值对抽象成树的概念，使其与ZooKeeper的模型保持一致
> 

`例子——接口子目录存储为key-value格式`

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%204.png)

`例子——临时节点存储为key-value格式`

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%205.png)

`以com.alibaba.service.HelloService为例的树形化结构`

> 这里有意地画出了树状结构，每个层级都代表etcd中的key,非临时节点默认存储的是Hash值，临时节点中存储的是key关联的租约id。服务注册和发现过程中，服务提供者和消费者都会将自己的IP和端口等相关信息写入对应的key-value中。存储到注册中心的任何特殊字符都会被编码，比如URL中包含的“/”字符，在etcd3注册中心内部已经调用URLEncode进行特殊字符处理了
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%206.png)

- 后续

> 我们可以通过来接etcd在dubbo中的客户端，这个客户端就是负责对这个结构进行观察、CRUD等操作的。例如类似在使用Zookeeper时的zkclient客户端。**目前虽然采用官方的jetcd作为默认客户端，但提供了 SPI扩展（也就是说后续可以更换客户端）**
> 

> 我们可以通过了解以下几个方面，读者可自行了解
> 
> - 支持其他客户端的底层交互接口：提供一个新的扩展点EtcdTransporter，在注册中心初始化时会通过这个transporter初始化真实的交互client
> - 创建etcd注册中心的注册工厂：EtcdRegistryFactory
> - 客户端的实体：JEtcdClient的实现，以及能进行的操作，我们可以了解里面创建临时节点的过程、失败重试机制（RetryPolicy）等
> - 底层调用的gRPC协议（HTTP2）：如何利用连接复用的特性细节等去优化watch事件、watch底层如何处理幂等性等
> - 注册中心宕机的容灾机制：etcd下FailbackRegistry的实现

### 2.3 Cluster层扩展点

- 概述

> Cluster层负责了整个Dubbo框架的集群容错，涉及的扩展点较多，**包括容错(Cluster)、 路由(Router)、负载均衡(LoadBalance)、 配置管理工厂(ConfiguratorFactory)和合并器(Merger)**
> 

==Cluster扩展点==

> Cluster需要与Cluster层区分开，Cluster主要负责一些容错的策略，也是整个集群容错的入口。当远程调用失败后，由Cluster负责重试、快速失败等，整个过程对上层透明。整个集群容错层之间的关系
> 
- Cluster扩展点接口

> Cluster接口只有一个join方法，并且有@Adaptive注解，说明会根据配置动态调用不同的容错机制。不同的实现如下表
> 

```java
@SPI(FailoverCluster.NAME)
public interface Cluster {
	@Adaptive
	<T> Invoker<T> join(Directory<T> directory) throws RpcException;
)
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%207.png)

==RouterFactory 扩展点==

> RouterFactory是一个工厂类，顾名思义，就是用于创建不同的Router。假设接口 A有多个服务提供者提供服务，如果配置了路由规则(某个消费者只能调用某个几个服务提供者)，则Router会过滤其他服务提供者，只留下符合路由规则的服务提供者列表。
> 
- 接口源码

> 现有的路由规则支持文件、脚本和自定义表达式等方式。接口上有`@Adaptive("protocol")`注解，会根据不同的protocol自动匹配路由规则，下图是已有的实现
> 

```java
@SPI
public interface RouterFactory {
	@Adaptive("protocol")
	Router getRouter(URL url);
}
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%208.png)

- 注意

> **在2.7版本之后，路由模块会做出较大的更新，每个服务中每种类型的路由只会存在一个， 它们会成为一个路由器链。**
> 

==LoadBalance扩展点==

> LoadBalance是Dubbo框架中的负载均衡策略扩展点，框架中已经内置`随机(Random)、 轮询(RoundRobin)、最小连接数(LeastActive)、一致性 Hash (ConsistentHash)这几种负载均衡的方式`，**默认使用随机负载均衡策略**。LoadBalance主要负责在多个节点中，根据不同的负载均衡策略选择一个合适的节点来调用。
> 
- 接口源码

> 同样有Adaptive注解，下图为已有的实现
> 

```java
@SPI(RandomLoadBalance.NAME)
public interface LoadBalance (
	@Adaptive("loadbalance")
	<T> Invoker<T> select(List<Invoker<T>> invokers,
							URL url,
							Invocation invocation)throws RpcException;
}
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%209.png)

==ConfiguratorFactory 扩展点==

> ConfiguratorFactory是创建配置实例的工厂类，现有override和absent两种工厂实现，分别会创建`OverrideConfigupatop和AbsentConfigurator`两种配置对象。默认的两种实现：
> 
> - OverrideConfigurator会直接把配置中心中的参数覆盖本地的参数；
> - AbsentConfigurator会先看本地是否存在该配置，没有则新增本地配置，如果己经存在则不会覆盖。
- 接口源码

> 该扩展点的方法上也有`@Adaptive("protocol")`注解，会根据URL中的protocol配置值使用不同的扩展点实现。下图为已有的实现
> 

```java
@SPI
public interface ConfiguratorFactory {
	@Adaptive("protocol")
	Configurator getConfigurator(URL url);
}
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%2010.png)

==Merger扩展点==

> Merger是合并器，可以对并行调用的结果集进行合并，**例如：并行调用A、B两个服务都会返回一个List结果集,Merger可以把两个List合并为一个并返回给应用**。默认已经支持`map、set、list、byte`等11种类型的返回值。用户可以基于该扩展点，添加自定义类型的合并器。
> 
- 接口源码

> 下图为已有的实现
> 

```java
@SPI
public interface Merger<T> {
	T merge(T... items);
}
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%2011.png)

## 3.Remote层扩展点

- 概述及作用

> Remote处于整个Dubbo框架的底层，**涉及协议、数据的交换、网络的传输、序列化、线程池等**，涵盖了一个远程调用的所有要素。
> 

> Remote层是对Dubbo传输协议的封装，内部再划为Transport传输层和Exchange信息交换层。其中Transport层只负责单向消息传输，是对Mina、 Netty等传输工具库的抽象。而Exchange层在传输层之上实现了 Request-Response语义，这样我们可以在不同传输方式之上都能做到统一的请求/响应处理。**Serialize层是RPC的一部分，决定了在消费者和服务提供者之间的二进制数据传输格式。不同的序列化库的选择会对RPC调用的性能产生重要影响，目前默认选择是Hessian2序列化。**
> 

### 3.1 Protocol层扩展点

- 概述

> Protocol层主要包含四大扩展点，分别是`Protocol、Filter、ExporterListener和 InvokerListener`。 其中Protocol、Filter这两个扩展点使用得最多。
> 

==Protocol扩展点==

> Protocol是Dubbo RPC的核心调用层，具体的RPC协议都可以由Protocol点扩展。如果想增加一种新的RPC协议，则只需要扩展一个新的Protocol扩展点实现即可。
> 
- 接口代码

```java
^SPlC'dubbo")
public interface Protocol (
	int getDefaultPort(); //当用户没有设置端口的时候，返回默认的端口

	@Adaptive //把一个服务暴露成远程invocation
	<T> Exporter<T> export(Invoker<T> invoker) throws RpcException;

	@Adaptive //引用一个远程服务
	<T> Invoker<T> refer(Class<T> type, URL url) throws RpcException;

	void destroy(); //销毁
}
```

- 每个方法都有自己的规则

export 方法：

1. 协议收到请求后应记录请求源IP地址。通过RpcContext.getContext(). setRemoteAddress()方法存入RPC上下文。
2. export方法必须实现幕等，即无论调用多少次，返回的URL都是相同的。
3. Invoker实例由框架传入，无须关心协议层。

refer方法：

1. 当我们调用refer。方法返回Invoker对象的invoke()方法时，协议也需要相应地执行invoke()方法。这一点在设计自定义协议的Invoker时需要注意。
2. 正常来说refer。方法返回的自定义Invoker需要继承Invoker接口。
3. 当URL的参数有check=false时，自定义的协议实现必须不能抛出异常，而是在出现连接失败异常时尝试恢复连接。

destroy 方法：

1. 调用destroy方法的时候，需要销毁所有本协议暴露和引用的方法。
2. 需要释放所有占用的资源，如连接、端口等。
3. 自定义的协议可以在被销毁后继续导出和引用新服务。
- `Protocol、Exporter、Invoker`

> 整个Protocol的逻辑由Protocol、Exporter、Invoker三个接口串起来：
> 
> - 其中Protocol接口是入口，其实现封装了用来处理Exporter和Invoker的方法：
> - Exporter代表要暴露的远程服务引用，Protocol#export方法是将服务暴露的处理过程
> - Invoker代表要调用的远程服务代理对象，Protocol#refer方法通过服务类型和URL获得要调用的服务代理。
- 装饰器模式的应用

> 由于Protocol可以实现Invoker和Exporter对象的创建，因此除了作为远程调用对象的构造， 还能用于其他用途，**例如：可以在创建Invoker的时候对原对象进行包装增强，添加其他Filter进去，ProtocolFilterWrapper实现就是把Filter链加入Invoker**
> 

==Filter扩展点==

> Filter是Dubbo的过滤器扩展点，可以自定义过滤器，在Invoker调用前后执行自定义的逻辑。在Filter的实现中，必须要调用传入的Invoker的invoke方法，否则整个链路就断了。
> 
- 接口源码

```java
@SPI 	//Filter 接口定义
public interface Filter (
	Result invoke(Invoker<?> invoke、 Invocation invocation) throws RpcException;
	//可以看到，Filter接口使用了 JDK8的新特性，
	//接口中有default方法onResponse,默认返回收到的结果。
	default Result onResponse(Result result, Invoker<?> invoke、Invocation invocation){
		return result;
	}
}

//invoke方法实现示例，加入在调用下一个Invoker前做的事情
doSomeThingBefore();
Result result = invoker.invoke(invocation);
//加入在调用下一个Invoker后做的事情
doSomeThingAfter();
return result;
```

==ExporterListener/lnvokerListener 扩展点==

> ExporterListener和InvokerListener这两个扩展点非常似，
> 
> - ExporterListener是在暴露和取消暴露服务时提供回调；
> - InvokerListener则是在服务的引用与销毁引用时提供回调。
- 两者的接口源码

```java
@SPI //ExporterListener 扩展接口
public interface ExporterListener {
	void exported(Exporter<?> exporter) throws RpcException;
	void unexported(Exporter<?> exporter);
}
@SPI //InvokerListener 扩展接口
public interface InvokerListener {
	void referred(Invoker<?> invoker) throws RpcException;
	void destroyed(Invoker<?> invoker);
}
```

### 3.2 Exchange扩展点

- 概述

> **Exchange层只有一个扩展点接口 Exchanger，这个接口主要是为了封装请求/响应模式，例如：把同步请求转化为异步请求**。默认的扩展点实现是`org.apache.dubbo.remoting.exchange.support.header.HeaderExchanger`。 每个方法上都有@Adaptive 注解，会根据 URL 中的Exchanger参数决定实现类。
> 
- 接口源码

```java
@SPI(HeaderExchanger.NAME)
public interface Exchanger (
	@Adaptive({Constants.EXCHANGER_KEY})
	Exchangeserver bind(URL url, ExchangeHandler handler) throws RemotingException;

	@Adaptive((Constants.EXCHANGER_KEY})
	Exchangeclient connect(URL url, ExchangeHandler handler) throws RemotingException;
}
```

- 为什么为了传输层还有有个所谓的交换层

> **因为上层业务关注的并不是诸如Netty这样的底层Channel。上层一个Request只关注对应的Response，对于是同步还是异步请求，或者使用什么传输根本不关心。Transport层是无法满足这项需求的， Exchange层因此实现了 Request-Response模型，我们可以理解为基于Transport层做了更高层次的封装**
> 

### 3.3 Transport 层扩展点

- 概述

> Transport层为了**屏蔽不同通信框架的异同，封装了统一的对外接口**。主要的扩展点接口有`Transporter、 Dispatcher、Codec2和ChannelHandler`
> 

==Transporter 扩展接口==

> Transporter屏蔽了通信框架接口、实现的不同，使用统一的通信接口。
> 
- 接口源码

> bind方法会生成一个服务，监听来自客户端的请求；connect方法则会连接到一个服务。 **两个方法上都有@Adaptive注解，首先会根据URL中server的参数值去匹配实现类，如果匹配不到则根据transporter参数去匹配实现类。默认的实现是`netty4`**
> 

```java
@SPI("netty")
public interface Transporter {
	@Adaptive((Constants.SERVER_KEY, Constants.TRANSPORTER_KEY})
	Server bind(URL url, ChannelHandler handler) throws RemotingException;

	@Adaptive({Constants CLIENT_KEY, Constants.TRANSPORTER_KEY})
	Client connect(URL url, ChannelHandler handler) throws RemotingException;
}
```

- 接口已有的实现

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%2012.png)

==Dispatcher扩展接口==

> 如果有些逻辑的处理比较慢，**例如：发起I/O请求查询数据库、请求远程数据等，则需要使用线程池。因为I/O速度相对CPU是很慢的，如果不使用线程池，则线程会因为I/O导致同步阻塞等待。Dispatcher扩展接口通过不同的派发策略，把工作派发到不同的线程池，以此来应对不同的业务场景。**
> 
- 接口源码

```java
@SPI(AllDispatcher.NAME)
public interface Dispatcher {
	@Adaptive({Constants.DISPATCHER_KEY, "dispather","channel.handler"})
	ChannelHandler dispatch(ChannelHandler handler, URL url);
}
```

- 已有的实现

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%2013.png)

==Codec2扩展接口==

> Codec2主要实现对数据的编码和解码，**但这个接口只是需要实现编码/解码过程中的通用逻辑流程，如解决半包、粘包等问题。**该接口属于在序列化上封装的一层。
> 
- 接口源码

```java
@SPI
public interface Codec2 {
	@Adaptive({Constants.CODEC_KEY))
	void encode(Channel channel, ChannelBuffer buffer, Object message) throws IOException;

	@Adaptive((Constants.C0DEC_KEY))
	Object decode(Channel channel, ChannelBuffer buffer) throws IOException;

	enum DecodeResult {
		NEED_MORE_INPUTJ SKIP_SOME_INPUT
	}
}
```

- 已有的实现

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%2014.png)

==ThreadPool扩展接口==

> 我们在Transport层由Dispatcher实现不同的派发策略，最终会派发到不同的ThreadPool中执行。ThreadPool扩展接口就是线程池的扩展。
> 
- 接口源码

```java
@SPI("fixed")
public interface ThreadPool {
	@Adaptive({Constants.THREADPOOL_KEY})
	Executor getExecutor(URL url);
}
```

- 线程池的四种默认实现

> • `fixed`：固定大小线程池，启动时建立线程，不关闭，一直持有。
• `cached`：缓存线程池，空闲一分钟自动删除，需要时重建。
• `limited`：可伸缩线程池，但池中的线程数只会增长不会收缩。只增长不收缩的目的是为了避免收缩时突然来了大流量引起的性能问题。
• `eager`：优先创建Worker线程池。在任务数量大于corePoolSize小于maximumPoolSize时，优先创建Worker来处理任务。当任务数量大于maximumPoolSize时，将任务放入阻塞队列。阻塞队列充满时抛出RejectedExecutionException (cached在任务数量超过maximumPoolSize时直接抛出异常而不是将任务放入阻塞队列)。
> 

### 3.4 Serialize 层扩展点

- 概述

> Serialize层主要实现具体的对象序列化，只有Serialization 一个扩展接口。**Serialization是具体的对象序列化扩展接口，即把对象序列化成可以通过网络进行传输的二进制流。**
> 

==Serialization 扩展接口==

> Serialization就是具体的对象序列化
> 
- 接口源码

> **Serialization默认使用Hessian2做序列化**
> 

```java
@SPI("hessian2")
public interface Serialization {
	byte getContentTypeId();

	String getContentType();

	@Adaptive
	Objectoutput serialize(URL url, Outputstream output) throws IOException;

	@Adaptive
	Objectinput deserialize(URL url. Inputstream input) throws IOException;
}
```

- 已有的接口实现

> 
> 
> - 其中compactedjava是在Java原生序列化的基础上做了压缩，实现了自定义的类描写叙述符的写入和读取。在序列化的时候仅写入类名，而不是完整的类信息，这样在对象数量很多的情况下，可以有效压缩体积。
> - NativeJavaSerialization是原生的Java序列化的实现方式。
> - JavaSerialization是原生Java序列化及压缩的封装。
> - 其他的序列化实现则封装了现在比较流行的各种序列化框架，如kryo、protostuff和fastjson等。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%2015.png)
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%85%AD%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%20%E6%95%B4%E4%BD%93%E6%A1%86%E6%9E%B6%E7%9A%84%E6%80%BB%E7%BB%93/image%2016.png)
> 

## 4.其他扩展点

- TelnetHandler 扩展点

> 我们知道，Dubbo框架支持Telnet命令连接，TelnetHandler接口就是用于扩展新的Telnet命令的接口。
> 
- StatusChecker 扩展点

> 通过这个扩展点，可以让Dubbo框架支持各种状态的检查，默认已经实现了内存和load的检查。用户可以自定义扩展，如硬盘、CPU等的状态检查。
> 
- Container 扩展点

> 服务容器就是为了不需要使用外部的Tomcat JBoss等Web容器来运行服务，因为有可能服务根本用不到它们的功能，只是需要简单地在Main方法中暴露一个服务即可。此时就可以使用服务容器。Dubbo中默认使用Spring作为服务容器。
> 
- CacheFactory 扩展点

> 我们可以通过dubbo:method配置每个方法的调用返回值是否进行缓存，用于加速数据访问速度。
> 

==默认四种实现==

> • Iru：基于最近最少使用原则删除多余缓存，保持最热的数据被缓存。
• threadlocal：当前线程缓存，比如一个页面渲染，用到很多portal，每个portal都要去查用户信息，通过线程缓存可以减少这种多余访问。
• jcache：与JSR107集成，可以桥接各种缓存实现。
• expiring：实现了会过期的缓存，有一个守护线程会一直检查缓存是否过期。
> 
- Validation 扩展点

> 该扩展点主要实现参数的校验，我们可以在配置中使用`＜dubbo: service validation="校验实现名"/＞`实现参数的校验。
> 
- LoggerAdapter 扩展点

> 日志适配器主要用于适配各种不同的日志框架，使其有统一的使用接口。
> 
- Compiler 扩展点

> ©Adaptive注解会生成Java代码，然后使用编译器动态编译出新的Classo Compiler接口就是可扩展的编译器
>