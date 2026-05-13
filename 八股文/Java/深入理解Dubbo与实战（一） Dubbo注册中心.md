# 深入理解Dubbo与实战（一）| Dubbo注册中心

type: Post
status: Published
date: 2022/08/12
summary: Dubbo注册中心
tags: Dubbo
category: 中间件

# Dubbo注册中心

- 概述

> 我们会从注册中心的工作流程、注册中心的数据结构、 订阅发布的实现、 缓存机制、 重试机制和设计模式这五个维度去解读Dubbo注册中心的构成与配合
> 

## 1.注册中心概述

- 注册中心的作用

> 在Dubbo微服务体系中，注册中心是其核心组件之一，实现了服务与服务之间的注册与发现；主要作用如下：
> 
> - 动态加入：一个服务提供者通过注册中心可以动态地把自己暴露给其他消费者，无须消费者逐个去更新配置文件。
> - 动态发现：一个消费者可以动态地感知新的配置、路由规则和新的服务提供者，无须重启服务使之生效。
> - 动态调整：注册中心支持参数的动态调整，新参数自动更新到所有相关服务节点。
> - 统一配置：避免了本地配置导致每个服务的配置不一致问题
- API模块

> 注册中心的源码在模块dubbo-register中，里面包含五个子模块，其名称和作用如下，可以看到注册中心有种类之分（zookeeper：官方推荐、Redis、Simple和Multicast），当然你可以制定自己的规则去使用nacos作为注册中心
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image.png)

==不同注册中心的区别==

> • 阿里内部并没有使用Redis作为注册中心，Redis注册中心并没有经过长时间运行的可靠性验证，其稳定性依赖于Redis 本身。
• Simple注册中心是一个简单的基于内存的注册中心实现，它本身就是一个标准的RPC 服务，不支持集群，也可能出现单点故障。
• Multicast模式则不需要启动任何注册中心，只要通过广播地址，就可以互相发现。服务提供者启动时，会广播自己的地址。消费者启动时，会广播订阅请求，服务提供者收到订阅请求，会根据配置广播或单播给订阅者。不建议在生产环境使用。
> 

### 1.1 工作流程

- 概述

> 
> 
> - 服务提供者启动时，会向注册中心写入自己的元数据信息，同时会订阅配置元数据信息。
> - 消费者启动时，也会向注册中心写入自己的元数据信息，并订阅服务提供者、路由和配置元数据信息。
> - 服务治理中心(dubbo-admin)启动时，会同时订阅所有消费者、服务提供者、路由和配置元数据信息。
> - 当有服务提供者离开或有新的服务提供者加入时，注册中心服务提供者目录会发生变化，变化信息会动态通知给消费者、服务治理中心。
> - 当消费方发起服务调用时,会异步将调用、统计信息等上报给监控中心 dubbo-monitor simple 。

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%201.png)

### 1.2 Zookeeper原理概述

- 概述

> ZooKeeper是树形结构的注册中心，每个节点的类型分为持久节点、持久顺序节点、临时节点和临时顺序节点。
> 
- 节点类型

> • 持久节点：服务注册后保证节点不会丢失，注册中心重启也会存在。
• 持久顺序节点：在持久节点特性的基础上增加了节点先后顺序的能力。
• 临时节点：服务注册后连接丢失或session超时，注册的节点会自动被移除。
• 临时顺序节点：在临时节点特性的基础上增加了节点先后顺序的能力。
> 
- 注意

> 上面有四种类型，但是如果zookeeper作为注册中心只会创建临时节点和持久节点两种（创建前后顺序无要求）
> 
- 路径例子

> 如下是提供者在zookeeper注册的路径，可以转换为树形结构分为四层：
> 
> 1. root：根节点，路径下的dubbo
> 2. service：接口名称，对应com.foo.BarService
> 3. 四种服务目录：对应providers，还有consumers、routers、configurators
> 4. 在服务分类下是具体的Dubbo服务URL

`/dubbo/com.foo.BarService/provider`

- 树形结构的关系

> 
> 
> - 树的根节点是注册中心分组，下面有多个服务接口，分组值来自用户配置`<dubbo:registry>`中的 group 属性，默认是/dubbo。
> - 服务接口下包含4类子目录，分别是providers、consumers、routers、configurators,这个路径是持久节点。
> - 不同目录下包含着多个不同的URL元数据信息
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%202.png)
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%203.png)
> 
- 目录包含信息实例

> 在Dubbo框架启动时，会根据用户配置的服务，在注册中心中创建4个目录，在providers和consumers目录中分别
> 
> 
> **存储服务提供方、消费方元数据信息，主要包括IP、端口、权重和应用名等数据**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%204.png)
> 
- xml的形式dubbo启动zookeeper

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%205.png)

### 1.3 Redis原理概述

- 概述

Redis注册中心也沿用了 Dubbo抽象的`Root、Service、Type、URL`四层结构。但是由于Redis属于NoSQL数据库，数据都是以键值对的形式保存的，并不能像ZooKeeper一样直接实现树形目录结构。**因此，Redis使用了 key/Map结构实现了这个需求，Root、Service、Type组合成Redis的key，Redis的value是一个Map结构，URL作为Map的key，超时时间作为Map的value**，如下图

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%206.png)

- 代码实例

```java
...
String key = tocategoryPath(url); 	//生成Redis key
String value = ur1.toFullString();	//生成URL...
...
jedis.hset(key, value,expire); //注册到 Redis注册中心,expire为超时时间
```

## 2.订阅/发布

- 传统修改配置的方法

> 在传统应用系统中，我们通常会把配置信息写入一个配置文件，当配置需要变更时会修改配置文件,**再通过手动触发内存中的配置重新加载， 如重启服务等**。在集群规模较小的场景下，这种方式也能方便地进行运维。
> 
- 有了注册中心的订阅和发布

> 如果我们使用了注册中心，那么上述的问题就会迎刃而解。当一个已有服务提供者节点下线，或者一个新的服务提供者节点加入微服务环境时，订阅对应接口的消费者和服务治理中心都能及时收到注册中心的通知，并更新本地的配置信息。然后对节点的状态实时进行调整
> 

### 2.1 ZooKeeper 的实现

- 题外话

> dubbo中抽象管理zookeeper的客户端有两种分别是：Apache Curator、zkCliento；用户可以在`＜dubbo: registry＞`的client属性中设置curator、zkclient来使用不同的客户端实现库，**如果不设置则默认使用Curator作为实现。**
> 

==发布的实现==

> 服务提供者和消费者都需要把自己注册到注册中心。**服务提供者的注册是为了让消费者感知服务的存在，从而发起远程调用；也让服务治理中心感知有新的服务提供者上线。消费者的发布是为了让服务治理中心可以发现自己**。ZooKeeper发布代码非常简单，只是调用了ZooKeeper的客户端库在注册中心上创建一个目录
> 

```java
//创建目录
zkClient.create(toUrlPath(url)
url.getParameter(Constants.DYNAMIJKEY, true));

//删除路径
zkClient.delete(toUrlPath(url));
```

==订阅的实现==

> 订阅通常有pull和push两种方式，一种是客户端定时轮询注册中心拉取配置，另一种是注册中心主动推送数据给客户端。这两种方式各有利弊，**目前Dubbo采用的是第一次启动拉取方式，后续接收事件重新拉取数据。**
> 

> 在服务暴露时，服务端会订阅`configurators`用于监听动态配置，在消费端启动时，消费端会订阅`providers、routers和configuratops`这三个目录，分别对应服务提供者、路由和动态配置变更通知。
> 
- zookeeper采取的方式

> ZooKeeper注册中心采用的是`“事件通知” + “客户端拉取”`的方式，**客户端在第一次连接上注册中心时，会获取对应目录下`全量`的数据。并在订阅的节点（节点的子节点也被会订阅）上注册一个watcher（中心就会处理订阅）**，客户端与注册中心之间保持TCP长连接，后续每个节点有任何数据变化的时候，注册中心会根据watcher的回调主动通知客户端（事件通知），客户端接到通知后，会把对应节点下的全量数据都拉取过来（客户端拉取），这一点在`NotifyListener#notify List<URL> urls` 接口上就有约束的注释说明。全量拉取有一个局限，当微服务节点较多时会对网络造成很大的压力。
> 

`全量订阅服务`

> **注意有全量就有类别订阅，在类别订阅中传入方法的URL中的category属性值获取具体的类别：providers、routers、consumers、configurators,然后拉取直接子节点的数据进行通知(notify)。**
> 

```java
if (ANY_VALUE.equals(url.getServiceInterface())) {	//订阅所有数据
	String root = toRootPath();
	//如果listeners是空的，则会把listeners放入缓存
	ConcurrentMap<NotifyListener, ChildListener> listeners = zkListeners.computeIfAbsent(url, k -> new ConcurrentHashMap<>());
	//zkListener 为空，说明是第一次，新建一个listener
	ChildListener zkListener = listeners.computeIfAbsent(listener, k -> (parentPath, currentChilds) -> {
	    for (String child : currentChilds) {		//如果子节点有变化则会接到通知，遍历所有子节点
	        child = URL.decode(child);
	        if (!anyServices.contains(child)) {	//如果存在子节点未被订阅，说明为新节点进行订阅
	            anyServices.add(child);
	            //递归至下一个子节点
	            subscribe(url.setPath(child).addParameters(INTERFACE_KEY, child,
	                    Constants.CHECK_KEY, String.valueOf(false)), k);
	        }
	    }
	});
	zkClient.create(root, false);		//创建持久节点，接下来订阅持久节点的直接子节点
	List<String> services = zkClient.addChildListener(root, zkListener);
	if (CollectionUtils.isNotEmpty(services)) {		//遍历所有子节点进行订阅
	    for (String service : services) {
	        service = URL.decode(service);
	        anyServices.add(service);
	        //增加当前节点的订阅，并且会返回该节点下所有子节点列表
	        subscribe(url.setPath(service).addParameters(INTERFACE_KEY, service,
	                Constants.CHECK_KEY, String.valueOf(false)), listener);
	    }
	}
}
```

> 每个节点都有一个对应的版本号，只要数据发生变化（即发生事务操作：无论前后值一不一样）都会使版本号变化（这个版本号强调变更次数）
> 
- 事务操作

> 客户端任何新增、删除、修改、会话创建和失效操作，都会被认为是事物操作，会由ZooKeeper集群中的leader 执行。即使客户端连接的是非leader节点，请求也会被转发给leader执行，以此来保证所有事物操作的全局时序性。由于每个节点都有一个版本号，因此可以通过CAS操作比较版本号来保证该节点数据操作的原子性。
> 

### 2.2 Redis的实现

==总体流程==

> 使用Redis作为注册中心，其订阅发布实现方式与ZooKeeper不同。我们在Redis注册中心的数据结构中已经了解到，**Redis订阅发布使用的是过期机制和publish/subscribe通道**。
> 

> **服务提供者发布服务，首先会在Redis中创建一个key，然后在通道中发布一条register事件消息。 但服务的key写入Redis后，发布者需要周期性地刷新key过期时间，在RedisRegistry构造方法中会启动一个expireExecutor定时调度线程池，不断调用deferExpired()方法去延续key的超时时间。如果服务提供者服务宕机，没有续期，则key会因为超时而被Redis删除，服务也就会被认定为下线**
> 
- 续期代码

```java
Iterator var1 = (new HashSet(this.getRegistered())).iterator();

while(var1.hasNext()) {
    URL url = (URL)var1.next();
    if (url.getParameter("dynamic", true)) {	//获取本地缓存的所有已注册的key，并遍历
        String key = this.toCategoryPath(url);
        //续期
        if (this.redisClient.hset(key, url.toFullString(), String.valueOf(System.currentTimeMillis() + (long)this.expirePeriod)) == 1L) {
            //如果续期返回1，则说明key已经被删除，这次等于重新发布服务并进行广播
            this.redisClient.publish(key, "register");
        }
    }
}
```

- 订阅首次连接注册中心

> 会获取全量数据并缓存在本地内存中。后续的服务列表变化则通过publish/subscribe通道广播，当有**服务提供者主动下线**的时候，会在通道中广播一条unregister事件消息，订阅方收到后则从注册中心拉取数据，更新本地缓存的服务列表。**新服务提供者上线也是通过通道事件触发更新的**
> 
- 两个情况下如何知道服务发布方已经下线

> 服务宕机而不是主动下线时，这个情况是不会进行广播unregister消息的继续附加条件，因为redis各个节点之间的消息传递并不是可靠的，采用失效转移的容错策略并且订阅的是从节点，如果主节点在向从节点同步的时候就宕机
> 

> **如果使用Redis作为服务注册中心，会依赖于服务治理中心（dubbo-admin），遍历key并删除超时key，并把以超时key发送unregister事件消息。其他消费者监听到取消注册事件后会删除本地对应服务的数据，从而保证数据的最终一致**
> 
- 过期key清理代码

> 在上面续期代码中，后续还有判断是否是服务治理中心，则还要清理过期的key
> 

```java
if (this.admin) {
    this.clean();
}
```

- 总体流程总结

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%207.png)

- Redis初始化时的集群模式配置`<dubbo:registry cluster="xxxx"/>`

> 
> 
> - 如果设置为failover或不设置，**则只会读取和写入任意一个Redis节点，失败的话再尝试下一个Redis节点。这种模式需要Redis自行配置数据同步。我们上面说的总体流程就是设置为此的基础下**
> - 设置为replicate，**则服务提供者在发布服务的时候,需要同时向Redis集群中所有的节点都写入，是多写的方式。但读取还是从一个节点中读取。 在这种模式下，Redis集群可以不配置数据同步，一致性由客户端的多写来保证。**

==发布的实现==

> 服务提供者和消费者都会使用注册功能，我们先来看看注册的代码
> 

```java
@Override
public void doRegister(URL url) {
    String key = toCategoryPath(url);
    String value = url.toFullString();
    //计算过期时间
    String expire = String.valueOf(System.currentTimeMillis() + expirePeriod);
    //遍历连接池中所有的节点
    for (Map.Entry<Stringj JedisPool> entry : jedisPools.entrySet()) {
		try {//向redis中注册，并在通道内发布注册事件
	        redisClient.hset(key, value, expire);
	        redisClient.publish(key, REGISTER);
	        success = true;
	        //如果Redis使用非replicate模式，只需要写一个节点，因此可以直接“break”；
	        //否则遍历所有节点,依次写入注册信息
			if (!replicate) (
				break;
			}
	    }
	}
}
```

==订阅的实现==

- Notifier内部类

> 服务消费者、服务提供者和服务治理中心都会使用注册中心的订阅功能。**在订阅时，如果是首次订阅，则会先创建一个Notifier内部类，这是一个线程类，在启动时会异步进行通道的订阅。在启动Notifier线程的同时，主线程会继续往下执行，全量拉一次注册中心上所有的服务信息。后续注册中心上的信息变更则通过Notifier线程订阅的通道推送事件来实现**
> 
- run方法中首次订阅的代码细节

```java
//以*结尾的进这里，如服务治理中心,订阅所有服务
if (service.endsWith(ANY_VALUE)) {
    if (!first) {	//如果不是第一次，则获取所有的服务key,并更新本地缓存
        first = false;
        Set<String> keys = redisClient.scan(service);
        if (CollectionUtils.isNotEmpty(keys)) {
            for (String s : keys) {
                doNotify(s);
            }
        }
        //由于连接过程允许一定量的失败，会做重置,此处则重置了计数器
        resetSkip();
    }
    redisClient.psubscribe(new NotifySub(), service);// blocking
} else {	//如果不是以*结尾，个别角色进入并且不是第一次，则表示订阅过
    if (!first) {
        first = false;
        //触发通知，更新本地缓存，并重置失败计数器
        doNotify(service);
        resetSkip();
    }
  	//订阅一个或多个符合给定模式的频道
    redisClient.psubscribe(new NotifySub(), service + PATH_SEPARATOR + ANY_VALUE);
}
```

## 3.缓存机制

- 概述

> 缓存的存在就是用空间换取时间，**如果每次远程调用都要先从注册中心获取一次可调用的服务列表，则会让注册中心承受巨大的流量压力**。另外，每次额外的网络请求也会让整个系统的性能下降。因此Dubbo的注册中心实现了通用的缓存机制
> 
- AbstractRegistry的类结构图

> 消费者或服务治理中心获取注册信息后会做本地缓存。内存中会有一份，保存在Properties对象里，磁盘上也会持久化一份文件，通过file对象引用。
> 

```java
private final Properties properties = new Properties();
private File file; //磁盘文件服务缓存对象
//内存中的服务缓存对象
private final ConcurrentMap<URL> Map<Stringj List<URL>>> notified =
new ConcurrentHashMap<URLMap<String> List<URL>>>();
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%208.png)

- 注意

> 内存中的缓存notified是ConcurrentHashMap里面又嵌套了一个Map,外层Map的key是消费者的 URL,内层 Map 的 key 是分类，包含 providers、consumers、routes和configurators四种。value则是对应的服务列表，对于没有服务提供者提供服务的URL，它会以特殊的empty://前缀开头。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%209.png)

### 3.1 缓存的加载

- 过程

> 在服务初始化的时候，`AbstractRegistry`构造函数里会从本地磁盘文件中把持久化的注册数据读到`Properties`对象里，并加载到内存缓存中
> 
- Properties的内存

> **Properties保存了所有服务提供者的URL,使用`URL#serviceKey()`作为key，提供者列表、 路由规则列表、配置规则列表等作为value。由于value是列表，当存在多个的时候使用空格隔开。还有一个特殊的key.registies，保存所有的注册中心的地址**。如果应用在启动过程中，注册中心无法连接或宕机，则Dubbo框架会自动通过本地缓存加载Invokers
> 

### 3.2 缓存的保存与更新

- 概述

> 缓存的保存有同步和异步两种方式。异步会使用线程池异步保存，如果线程在执行过程中出现异常，则会再次调用线程池不断重试。这些更新内存或者文件缓存的操作全在缓存类（AbstractRegistry）的notify方法中
> 

```java
if (syncSaveFile) {
	//同步保存
    doSaveProperties(version);
} else {
	//异步保存，放入一个线程池，传入一个原子类的版本号保证数据是最新的
    registryCacheExecutor.execute(new SaveProperties(version));
}
```

## 4.重试机制

- 概述

> 重试机制的实现大多是基于FailbackRegistry，它继承了AbstractRegistry，并在此基础上增加了失败重试机制作为抽象能力。不同注册中心使用集成然后实现自己的特点方法就好：ZookeeperRegistry和RedisRegistry继承该抽象方法后，直接使用即可。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%2010.png)

- 重试步骤

> 
> 
> - 在该类中设置了一个定时器retryTimer，该定时器会在默认时间去调用retry方法
> - 该类中还有四个重要的集合
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%2011.png)
> 
> - 在定时器中调用retry方法的时候会把这四个集合全部遍历和重试，重试成功则从集合中移除；所谓重试就是调用首次注册或者订阅时的模板方法，方法具体实现由子类定义；如果捕获到异常同样会加入到对应集合中

## 5.Dubbo中的设计模式

==模板方法模式==

> 整个注册的逻辑代码使用的就是模板方法模式：
> 
> - AbstractRegistry实现了 Registry接口中的注册、订阅、查询、通知等方法，还实现了磁盘文件持久化注册信息这一通用方法。但是注册、订阅、查询、通知等方法只是简单地把URL加入对应的集合，没有具体的注册或订阅逻辑。
> - FailbackRegistry又继承了 AbstractRegistry,重写了父类的注册、订阅、查询和通知等方法，并且添加了重试机制。此外，还添加了四个未实现的抽象模板方法；以订阅为例，FailbackRegistry重写了 subscribe方法，但只实现了订阅的大体逻辑及异常处理等通用性的东西。具体如何订阅，交给继承的子类实现

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%2012.png)

==工厂模式==

> 所有的注册中心实现，都是通过对应的工厂创建的。
> 
> 
> AbstractRegistryFactory 实现了 RegistryFactory 接口的 getRegistry(URL url)方法，是一个通用实现，主要完成了加锁，以及调用抽象模板方法createRegistry(URL url)创建具体实现等操作，并缓存在内存中。抽象模板方法会由具体子类继承并实现
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%80%EF%BC%89%20Dubbo%E6%B3%A8%E5%86%8C%E4%B8%AD%E5%BF%83/image%2013.png)

- 如何正确的建立注册中心和对应工厂的联系呢

> 答案是`@Adaptive({"protocol"})`注解，该注解就会自动生成代码实现一些逻辑，它的value参数会从URL中获取protocol键的值，并根据获取的值来调用不同的工厂类。例如，当`url.protocol = redis`时，获得`RedisRegistryFactory`实现类
> 

```java
@SPI("dubbo")
public interface RegistryFactory (
	@Adaptive({"protocol"})
	Registry getRegistry(URL url);
)
```