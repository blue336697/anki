# 深入理解Dubbo与实战（七）| Dubbo高级特性

type: Post
status: Published
date: 2022/08/19
summary:  Dubbo高级特性
tags: Dubbo
category: 中间件

# Dubbo高级特性

> 本章首先对Dubbo支持的高级特性进行介绍，然后给出使用这些高级特性的示例，帮助读者更好地理解高级特性，最后对常用的高级特性的原理进行深入的分析，帮助读者更好地理解和掌握Dubbo框架。当发现Dubbo无法满足业务诉求时，也能进行深入的定制或扩展。
> 

## 1.Dubbo高级特性概述

- 概述

> Dubbo解决了分布式场景RPC通信调用的问题，但是要满足各种业务场景还是不够的。
> 

> • 举个例子，支付业务需要自身迭代版本，比如1.0版本和2.0版本，在2.0版本做了大量性能改进， 需要发布到性能测试环境与1.0版本做对比，这个时候需要框架提供服务隔离的能力。
• 再举另外一个场景的例子，客户端消费远程服务时不希望阻塞，这个时候业务方可以在线程池中发起RPC调用，但是这样不够优雅，需要框架支持异步调用和回调。
> 
- Dubbo支持高级特效一览

> 目前Dubbo框架在支持RPC通信的基础上，提供了大量的高级特性，比如`服务端Telnet调用、Telnet调用统计、服务版本和分组隔离、隐式参数、异步调用、泛化调用、上下文信息和结果缓存`等特性。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%83%EF%BC%89%20Dubbo%E9%AB%98%E7%BA%A7%E7%89%B9%E6%80%A7/image.png)

## 2.服务分组和版本

- 概述

> Dubbo中提供的服务分组和版本是强隔离的，如果服务指定了服务分组和版本，则消费方调用也必须传递相同的分组名称和版本名称。下面我们以某个订单查询接口 `com. alibaba. pay. order.QueryService`，这个接口包含不同的版本实现，比如版本分别为`1.0.0-stable和2.0.0`，在服务端对应的实现名称分别为`com.alibaba.pay.order.StableQueryService和com.alibaba.pay.order.PerfomanceQueryService`
> 
- 服务方暴露指定版本

> 当服务提供方进行服务暴露时，服务端会根据`serviceGroup/serviceName:serviceversion:port`组合成key,然后服务实现作为value保存在DubboProtocol类的exporterMap字段中。这个字段是一个HashMap对象，当服务消费调用时，根据消费方传递的服务分组、服务接口、版本号和服务暴露时的协议端口号重新构造这个key，然后从内存Map中查找对应实例进行调用。
> 

==在XML中的配置==

> 服务暴露直接配置version属性即可，如果要为服务指定分组，则继续添加group属性即可。因为这个特性是强隔离的，消费方必须在配置文件中指定消费的版本。
> 

```xml
<!--省略其他Dubbo配置-->
<dubbo:service interface="com.alibaba.pay.order.QueryService"
	class="com.alibaba.pay.order.StableQueryService" version="1.0.0-stable"/>

<dubbo:service interface="com.alibaba.pay.order.QueryService"
	class="com.alibaba.pay.order.PerfomanceQueryService" version="2.0.0"/>
<!--省略其他Dubbo配置-->
```

- 消费方进行配置与调用

> 在消费方`<dubbo:reference>`标签中指定要消费的版本号时，在服务拉取时会在客户端做一次过滤。如果要消费指定的分组，那么还需要指定group属性。当客户端指定了分组和版本时，在Dubbolnvoker构造函数中会将`URL中包含的接口、分组、Token和timeout`加入attachment，同时将接口上的版本号存储在version字段。当发起RPC请求时，通过DubboCodec把这些信息发送到服务器端，服务器端收到这些关键信息后重新组装成key，然后查找业务实现并调用。
> 

==在XML的配置==

```xml
<!--省略其他Dubbo配置-->
<dubbo:reference interface="com.alibaba pay.order.QueryService"
version="1.0.0-stable"/>

<dubbo:reference interface="com.alibaba.pay.order.QueryService"
version="2.0.0"/>
<!--省略其他Dubbo配置-->
```

- 消费方如何获取指定分组和版本对应的调用列表？——`ZookeeperRegistry#toUrlsWithoutEmpty`

> **当Dubbo客户端启动时，实际上会把调用接口所有的协议节点都拉取下来，然后根据本地URL配置的接口、category、分组和版本做过滤**，具体过滤是在注册中心层面实现的。以ZooKeeper注册中心为例， 当注册中心推送列表时，会调用`ZookeeperRegistry#toUrlsWithoutEmpty`方法，这个方法会把所有服务列表进行一次过滤
> 

```java
private List<URL> toUrlsWithoutEmpty(URL consumer, List<String> providers) {
	List<URL> urls = new ArrayList();
	if (CollectionUtils.isNotEmpty(providers)) {
	    Iterator var4 = providers.iterator();

	    while(var4.hasNext()) {
	    	//遍历所有的服务列表，并解码特殊字符
	        String provider = (String)var4.next();
	        if (provider.contains(CommonConstants.PROTOCOL_SEPARATOR_ENCODED)) {
	            URL url = URLStrParser.parseEncodedStr(provider);
	            //根据接口、category、版本和分组过滤
	            if (UrlUtils.isMatch(consumer, url)) {
	                urls.add(url);
	            }
	        }
	    }
	}

	return urls;
}
```

- 上面代码分析之接收服务列表——`RegistryDirectory`

> Dubbo中接收服务列表是在RegistryDirectory中完成的，它收到的列表是全量的列表。RegistryDirectory主要将URL转换成可以调用的Invokers。**在获取列表前会经过①把服务列表解码，用于解码被转译的字符。消费指定分组和版本关键逻辑在②中，它会将特定接口的全量列表和消费方URL进行匹配，匹配规则是校验接口名、类别、版本和分组是否一致。消费方默认的类别是providers**
> 

## 3.参数回调

- 概述

> Dubbo支持异步参数回调，当消费方调用服务端方法时，允许服务端在某个时间点回调回客户端的方法。在服务端回调到客户端时，服务端不会重新开启TCP连接，会复用已经建立的从客户端到服务端的TCP连接。
> 
- 官网实例

> [参数回调过程](https://www.notion.so/%E5%AE%98%E7%BD%91%EF%BC%9Ahttps://dubbo.apache.org/zh/docs/advanced/callback-parameter/)
> 
- 回调的原理

> 
> 
> - 客户端在启动时，会拉取服务服务端接口元数据， 因为服务端配置了异步回调信息，这些信息会透传给客户端。
> - 客户端在编码请求时，会发现第2个方法参数为回调对象。
> - 此时，客户端会暴露一个Dubbo协议的服务，服务暴露的端口号是本地TCP连接自动生成的端口。
> - 在客户端暴露服务时，会将客户端回调参数对象内存id存储在`attachment`中，对应的key为`sys_callback_arg-`回调参数索引。
> - 这个key在调用普通服务addListener时会传递给服务端，服务端回调客户端时，会把这个key对应的值再次放到`attachment`中传给客户端。
> - 从服务端回调到客户端的`attachment`会用`keycallback.service.instid`保存回调参数实例id，用于查找客户端暴露的服务。
> - 客户端调用服务端方法时，并不会把第2个异步参数实例序列化并传给服务端。
> - 当服务端解码时，会先检查参数是不是异步回调参数。如果发现是异步参数回调，那么在服务端解码参数值时，会自动创建到消费方的代理。
> - 服务端创建回调代理实例Invoker类型是`ChannelWrappedlnvoker`，比较特殊的是，构造函数的service值是客户端暴露对象id，当回调发生时，会把`keycallback.service.instid`保存的对象id传给客户端，这样就能正确地找到客户端暴露的服务了。

## 4.隐式参数

- 概述

> Dubbo服务提供者或消费者启动时，配置元数据会生成URL, 一般是不可变的。**在很多实际的使用场景中，在服务运行期需要动态改变属性值，在做动态路由和灰度发布场景中需要这个特性**。Dubbo框架支持消费方在`RpcContext#setAttachment`方法中设置隐式参数，在服务端`RpcContext#getAttachment`方法中获取隐式传递。
> 
- 隐式传递的原理图

> 当客户端发起调用前，设置隐藏参数，框架会在拦截器中把当前线程隐藏参数传递到`Rpclnvocation的attachment`中，服务端在拦截器中提取隐藏参数并设置到当前线程`RpcContext`中。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%83%EF%BC%89%20Dubbo%E9%AB%98%E7%BA%A7%E7%89%B9%E6%80%A7/image%201.png)

- 使用示例

> 在消费方调用服务方传递隐式参数时，会在`Abstractlnvoker#invoke`方法调用中合并
`RpcContext#getAttachments()`参数。用户的隐式参数会被合并到 `Rpclnvocation` 中的 `attachment`字段，这个字段发送给服务端。在服务提供方收到请求时，在`ContextFilter#invoke`中提取`Rpclnvocation`中的attachment信息，并设置到当前线程上下文中。因为后端业务方法调用和拦截器在同一个线程中执行，所以直接使用`RpcContext.getContext().getAttachment`获取值即可。在上面图中会发现客户端在拦截器中`(ConsumercontextFilter)执行setAttachements`方法，这个主要支持服务端透传隐式参数给客户端。
> 

```java
//在客户端设置隐式传参后面的远程调用都会隐式将这些参数发送到服务器端
RpcContext.getContext().setAttachment("index", "1");
//具体远程方法调用
xxxService.xxx();
//在服务端获取隐式参数
public class XxxServicelmpl implements XxxService {
	public void xxx() {
		//获取客户端隐式传入的参数
		String index = RpcContext.getContext().getAttachment("index");
	}
}
```

## 5.异步调用

- 概述

> 在客户端实现异步调用非常简单，在消费接口时配置异步标识，在调用时从上下文中获取Future对象，在期望结果返回时再调用阻塞方法`Future.get()`即可。
> 
- 代码实例

> 我们知道在客户端发起异步调用时，**应该在保存当前调用的Future后， 再发起其他远程调用，否则前一次异步调用的结果可能丢失(异步Future对象会被上下文覆盖)**。 因为框架要明确知道用户意图，所以需要再明确开启使用异步特性，在`<dubbo:reference ...>`标签中指定async标记
> 

```java
//触发异步调用
xxxService.findFoo(fooId);
//在发起其他RPC调用时，先获取Future引用，当结果返回后，会被通知和设置到此Future
Future<Foo> fooFuture = RpcContext.getContext().getFuture();
//如果foo已返回，则直接获取返回值，否则当前线程会被阻塞并等待
Foo foo = fooFuture.get();
// ...客户端非阻塞处理其他任务
```

```xml
<!--名略其他消费方配置-->
<dubbo:reference id="xxxService" interface="com.alibaba.foo.xxxService" async="true"/>
```

- 异步调用流程图

> 站在Dubb。客户端角度来说，直接发起RPC调用端属于用户线程。
> 
> - 用户线程①发起任意远程方法调用，最终会通过I/O线程发送网络报文。
> - 在真实发送报文前会在用户线程中设置当前异步请求Future (③)。
> - 因此在用户线程发起下一个远程方法调用前，需要先保存异步Future对象(④)
> - Dubbo框架会把异步请求对象保存在DefaultFuture类中，当服务端响应或超时时， 被挂起的用户线程将被唤醒(⑤)。
> - 用户线程设置异步Future对象的逻辑在`Dubbolnvoker#dolnvoke`方法中完成
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%83%EF%BC%89%20Dubbo%E9%AB%98%E7%BA%A7%E7%89%B9%E6%80%A7/image%202.png)
> 

## 6.泛化调用

- 概述

> **Dubbo泛化调用特性可以在不依赖服务接口 API包的场景中发起远程调用。这种特性特别适合框架集成和网关类应用开发。Dubbo在客户端发起泛化调用并不要求服务端是泛化暴露**
> 
- 调用示例

> 假设我们调用服务端com.xxx.XxxService#sayHello方法；目前泛化调用必需的参数主要包括`应用名称、注册中心(或者是直连调用地址)、真实接口名称和泛化标识`。在发起远程服务调用时，GenericService方法参数类型分别为真实方法名、 真实方法参数类型签名和真实参数值。这里有一个注意事项，每次动态创建的GenericService实例比较重，需要建立TCP连接，处理注册中心订阅和服务列表等计算，**因此需要缓存ReferenceConfig对象进行复用。但是往往很多业务开发时，忘记设置ReferenceConfig对象的Check方法为false，导致在没有服务提供者时，触发框架抛出No provider available的异常，从而导致缓存命中失败。**
> 

```java
ReferenceConfig<GenericService> ref = new ReferenceConfig<>();
ApplicationConfig appConfig = new ApplicationConfig("demo-consumer");

RegistryConfig registryConfig = new RegistryConfig();
registryConfig.setProtocol("zookeeper");
registryConfig.setAddress("localhost:2181");

ref.setProtocol("dubbo");
ref.setApplication(appConfig);
ref.setRegistry(registryConfig);
ref.setlnterface("com.xxx.XxxService");

ref.setGeneric(true); //1.标识泛化调用
GenericService genericService = ref.get(); //2.创建远程代理
//3.发起远程调用
Object result = genericService.$invoke("sayHello", new String[]{"java.lang.String"}, new Object[] {"world"});
```

- 大白话原理

> 服务端在处理服务调用时，在`GenericFilter`拦截器中先把`Rpclnvocation`中传递过来的参数类型和参数值提取出来，然后根据传递过来的接口名、 方法名和参数类型查找服务端被调用的方法。获取真实方法后，主要提取真实方法参数类型(可能包含泛化类型)，然后将参数值做Java类型转换。最后用解析后的参数值构造新的Rpclnvocation对象发起调用。
> 

## 7.上下文信息

- 概述

> Dubbo上下文信息的获取和存储同样是基于JDK的`ThreadLocal`实现的。上下文中存放的是当前调用过程中所需的环境信息。RpcContext是一个ThreadLocal的临时状态记录器，当收到或发送RPC时，当前线程关联的RpcContext状态都会变化。
> 

> **比如：A调用B，B再调用C，则在B机器上，在B调用C之前，RpcContext记录的是A调用B的信息，在B调用C之后， RpcContext记录的是B调用C的信息。**
> 
- 获取上下文信息示例

> 在客户端和服务端分别有一个拦截设置当前上下文信息，对应的分别为ConsumerContextFilter和ContextFiltero在客户端拦截器实现中，因为Invoker包含远程服务信息，因此直接设置远程IP等信息。在服务端拦截器中主要设置本地地址，这个时候无法获取远程调用地址。设置远程地址主要在`DubboProtocol#ExchangeHandlerAdapter.reply`方法中完成，可以直接通过`channel.getRemoteAddress` 方法获取。
> 

```java
public class DemoServicelmpl implements DemoService {
	public void hello() {
		// 本端是否为提供端，这里会返回true
		boolean isProviderSide = RpcContext.getContext().isProviderSide();
		//获取远程客户端IP地址
		String clientIP = RpcContext.getContext().getRemoteHost();
		//获取当前服务配置信息，所有配置信息都将转换为URL的参数
		String application = RpcContext.getContext().getUrl().getParameter("application");
		//注意：每发起RPC调用，上下文状态会变化这里假设调用yyyService服务done方法
		yyyService.done();
		//此时本端变成消费端，这里会返回false
		boolean isProviderSide = RpcContext.getContext().isProviderSide();
	}
}
```

## 8.Telnet操作（命令）

- 概述

> 目前Dubbo支持通过Telnet登录进行简单的运维，比如查看`特定机器暴露了哪些服务、显示服务端口连接列表、跟踪服务调用情况、调用本地服务和服务健康状况`等。在之前的章节我们详细讨论过如何实现，所以在这节我们主要聚焦于`Is、ps、trace和count`命令的实现和原理。
> 

==ls命令==

> 当服务发布时，如果注册中心没有对应的服务，那么我们可以初步使用Is命令检查Dubbo服务是否正确暴露了。**Is主要提供了查询已经暴露的服务列表、查询服务详细信息和查询指定服务接口信息等功能。**
> 
> - service代表要查询的服务接口名称，可以是短名称或全名称；
> - options代表支持的命令参数；
> - l显示服务详细信息列表或服务方法的详细信息。

```bash
Is options [service]
```

- 使用示例

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%83%EF%BC%89%20Dubbo%E9%AB%98%E7%BA%A7%E7%89%B9%E6%80%A7/image%203.png)

- 原理

> Is命令的实现主要基于`ListTelnetHandler，Dubbo`框架的Telnet调用只对Dubbo协议提供支持。它的原理非常简单，当服务端收到Is命令和参数时，会加载`ListTelnetHandler`并执行， 然后触发`DubboProtocol.getDubboProtocol().getExporters()`方法获取所有已经暴露的服务， 获取暴露的接口名和暴露服务别名(path属性)进行匹配，将匹配的结果进行输出。如果是查看服务暴露的方法，则框架会获取暴露接口名，然后反射获取所有方法并输出。
> 

==ps命令==

> ps命令用于查看提供服务本地端口的连接情况
> 
> - port代表要查询的服务暴露的端口 ；
> - options代表支持的命令参数；
> - l显示服务暴露的所有端口或服务端端口建立连接的信息。

```bash
ps options [port]
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%83%EF%BC%89%20Dubbo%E9%AB%98%E7%BA%A7%E7%89%B9%E6%80%A7/image%204.png)

- 原理

> ps命令实现类对应PortTelnetHandler类，当Dubbo服务暴露时，会把关联端口的服务端实例加入DubboProtocol类的serverMap字段。当执行ps命令时，PortTelnetHandler类会通过
DubboProtocol.getDubboProtocol().getServers()提取暴露的 server 实例。它持有了端口号和所有客户端连接信息等。当无法确认命令对应的后端实现时，可以查找和扩展点名称相同的文件，它包含扩展点所有的实现定义
> 

==trace命令==

> trace用于统计服务方法的调用信息，比如跟踪服务调用方法返回值、连接信息和耗时等。
> 
> - service代表要查询的服务接口名称，可以是短名称或全名称；
> - method代表要跟踪的方法；
> - count代表跟踪的最大次数

```bash
trace service [method] [count]
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%83%EF%BC%89%20Dubbo%E9%AB%98%E7%BA%A7%E7%89%B9%E6%80%A7/image%205.png)

- 注意

> 如果在使用trace命令跟踪方法调用时指定了最大次数，则不需要重复执行trace命令，当服务接口方法调用超过了最大次数后，不会把调用结果信息推送给Telnet客户端。
> 
- 原理

> trace命令对应的实现类是TraceTelnetHandler，它本身不会执行任何方法调用，首先根据传递的接口和方法查找对应的Invoker，然后把当前的Telnet连接（Channel 、接口、方法和最大执行次数信息记录在TraceFilter中，当接口方法被调用时，TraceFilter会取出对应的Telnet连接（Channel），并把调用结果信息发送的Telnet客户端
> 

==count命令==

> count命令也用于统计服务信息，但它主要统计方法调用成功数、失败数、正在并发执行数、 平均耗时和最大耗时。如果在服务方暴露服务时配置了 executes属性，那么使用count命令可以统计并发调用信息。
> 
> - service代表要查询的服务接口名称，可以是短名称或全名称；
> - method代表要跟踪的方法；
> - count代表跟踪的最大次数。

```bash
count service [method] [count]
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%83%EF%BC%89%20Dubbo%E9%AB%98%E7%BA%A7%E7%89%B9%E6%80%A7/image%206.png)

- 原理

> count命令对应的实现类是CountTelnetHandler，每次执行count命令时在服务端会启动一个线程去循环统计当前调用次数。比如统计10次，在线程中每间隔1秒执行一次统计，直到达到统计次数时退出线程。框架会使用RpcStatus类记录并发调用信息，CountTelnetHandler负责提取这些统计信息并输出给Telnet客户端。
> 

## 9.Mock调用

- 概述

> **Dubbo提供服务容错的能力，通常用于服务降级，比如验权服务，当服务提供方“挂掉” 后，客户端不抛出异常，而是通过Mock数据返回授权失败。**
> 
- 六种Mock方案

> 主要逻辑实现在`MockClusterlnvoker（MockClusterWrapper 类对 Cluster 实例进行包装）#invoke方法中`
> 

```xml
<!--第1种和第2种的使用方式是等价的，当直接指定mock=true时， 客户端启动时会查找并加装com.foo. BarServiceMock类。查找规则根据接口名加Mock后缀组
合成新的实现类，当然也可以使用自己的Mock实现类指定给Mock属性。-->
<dubbo:reference mock="true" .../>
<dubbo:reference mock="com.foo.BarServiceMock"・・・/>
<dubbo:reference mock="return null" .../>
<dubbo:reference mock="throw com.alibaba.XXXException" ・・・/>
<dubbo:reference mock="force:return fake" ・・・/>
<dubbo:reference mock="force:throw com.foo.MockException"・・/>
```

## 10.结果缓存

- 概述

> Dubbo框架提供了对服务调用结果进行缓存的特性，用于加速热门数据的访问速度，Dubbo提供声明式缓存，以减少用户加缓存的工作量。因为每次调用都会使用`JSON.toJSONString`方法将请求参数转换成字符串，然后拼装唯一的key,用于缓存唯一键。如果不能接受缓存造成的开销，则谨慎使用这个特性。 如果要使用缓存，则可以在消费方添加如下配置：
> 

```xml
<dubbo:reference cache="lru" .../>
```

- LRU策略的说明——`LinkedHashMap`的使用

> LRU缓存策略是框架默认使用的，因此我们会对它进行简单的说明。它的原理比较简单，缓存对应实现类是LRUCacheo缓存实现类LRUCache继承了 JDK的LinkedHashMap类，**LinkedHashMap是基于链表的实现，它提供了钩子方法removeEldestEntry，它的返回值用于判断每次向集合中添加元素时是否应该删除最少访问的元素。LRUCache重写了这个方法，当缓存值达到1000时，这个方法会返回true,链表会把头部节点移除。链表每次添加数据时都会在队列尾部添加，因此队列头部就是最少访问的数据 LinkedHashMap在更新数据时，会把更新数据更新到列表尾部）。**
>