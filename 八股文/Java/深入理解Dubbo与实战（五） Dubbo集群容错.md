# 深入理解Dubbo与实战（五）| Dubbo集群容错

type: Post
status: Published
date: 2022/08/16
summary: Dubbo集群容错
tags: Dubbo
category: 中间件

# Dubbo集群容错

- 概述

> 本章首先介绍整个集群容错层的总体结构与实现，让读者对集群容错层有一个整体的了解。 然后讲解该层中的每个重要组件，包括普通容错策略的实现原理，如`Failover、 Failfast`等策略； 整个集群容错过程都会使用的`Directory、Router、LoadBalance`及实现原理。此外，还会讲解特殊的集群容错策略Merger和Mock的实现原理。
> 

## 1.Cluster 层概述

- 我们为什么需要容错

> 在微服务环境中，为了保证服务的高可用，很少会有单点服务出现，服务通常都是以集群的形式出现的。然而，被调用的远程服务并不是每时每刻都保持良好状况，当某个服务调用出现异常时，如网络抖动、服务短暂不可用需要自动容错，或者只想本地测试、服务降级，需要Mock返回结果
> 
- `Cluster`层

> 我们可以把Cluster看作一个集群容错层，该层中包含Cluster、Directory、Router、LoadBalance几大核心接口。**注意这里要区分Cluster层和Cluster接口，Cluster层是抽象概念，表示的是对外的整个集群容错层；Cluster是容错接口，提供Failover、Failfast等容错策略**。
> 
- Cluster的总体工作流程——`以Abstractclusterinvoker为例`

> 前三步都Abstractclusterinvoker中去做一些通用的校验、参数准备等工作。真正调用方法则是子类的doInvoke方法
> 
> 1. 生成Invoker对象。不同的Cluster实现会生成不同类型的Clusterinvoker对象并返回。然后调用Clusterinvoker的Invoker方法，正式开始调用流程。
> 2. 获得可调用的服务列表。首先会做前置校验，检查远程服务是否已被销毁。然后通过`Directory#list`方法获取所有可用的服务列表。接着使用Router接口处理该服务列表，根据路由规则过滤一部分服务，最终返回剩余的服务列表。
> 3. 做负载均衡。在第2步中得到的服务列表还需要通过不同的负载均衡策略选出一个服务，用作最后的调用。首先框架会根据用户的配置，调用ExtensionLoader获取不同负载均衡策略的扩展点实现。然后做一些后置操作，如果是异步调用则设置调用编号。接着调用子类实现的dolnvoke方法（父类专门留了这个抽象方法让子类实现）， 子类会根据具体的负载均衡策略选出一个可以调用的服务。
> 4. 做RPC调用。首先保存每次调用的Invoker到RPC上下文，并做RPC调用。然后处理调用结果，对于调用出现异常、成功、失败等情况，每种容错策略会有不同的处理方式。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image.png)
> 

## 2.容错机制的实现

- 概述

> Cluster接口一共有9种不同的实现，每种实现分别对应不同的Clusterlnvokero本节会介绍继承了 Abstractclusterinvoker 的 7 种 Clusterinvoker 实现，Merge 和 Mock属于特殊机制后面会讲到
> 

### 2.1 容错机制概述

- 概述

> Dubbo容错机制能增强整个应用的健壮性，容错过程对上层用户是完全透明的，但用户也可以通过不同的配置项来选择不同的容错机制。每种容错机制又有自己个性化的配置项。Dubbo中现有 `Failover、Failfast、 Failsafe、 Fallback、 Forking、 Broadcast` 等容错机制
> 
- 容错机制的特性

> Cluseter的具体实现：用户可以在`<dubbo :service>、<dubbo:reference>、<dubbo:consumer>、 <dubbo:provider>`标签上通过cluster属性设置。
> 
> - 对于Failover容错模式，用户可以通过retries属性来设置最大重试次数。可以设置在`dubbo: reference`标签上，也可以设置在细粒度的方法标签`dubbo:method`上。
> - 对于Forking容错模式，用户可通过forks="最大并行数”属性来设置最大并行数。假设设置的forks数为们 可用的服务数为v，当`n<v`时，即可用的服务数大于配置的并行数，则并行请求n个服务；当`n>v`时，即可用的服务数小于配置的并行数，则请求所有可用的服务v。
> - 对于Mergeable容错模式，用可以在`dubbo:reference`标签中通过`merger="true"`开启，合并时可以通过`group="*"`属性指定需要合并哪些分组的结果。默认会根据方法的返回值自动匹配合并器，**如果同一个类型有两个不同的合并器实现，则需要在参数中指定合并器的名字merger-“合并器名“）**。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%201.png)
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%202.png)
> 

### 2.2 Cluster 接口关系

- 概述

> **在微服务环境中，可能多个节点同时都提供同一个服务**。当上层调用Invoker时，无论实际存在多少个Invoker，只需要通过Cluster层，即可完成整个调用的容错逻辑，包括`获取服务列表、路由、负载均衡`等，整个过程对上层都是透明的。
> 
- 容错接口的分类

> 第一类是Cluster类，第二类是Clusterinvoker类。Cluster和Clusterinvoker之间的关系也非常简单：**Cluster接口下面有多种不同的实现，每种实现中都需要实现接口的join方法，在方法中会`“new”`一个对应的Clusterinvoker实现。**
> 

==例子之——FailoverCluster==

> FailoverCluster是Cluster的其中一种实现，FailoverCluster中直接创建了一个新的FailoverClusterlnvoker 并返回。FailoverClusterlnvoker 继承的接口是 Invoker。
> 

```java
public class FailoverCluster extends AbstractCluster {

    public static final String NAME = "failover";

    @Override
    public <T> AbstractClusterInvoker<T> doJoin(Directory<T> directory) throws RpcException {
        return new FailoverClusterInvoker<>(directory);
    }
}
```

- Cluster接口的类图关系

> Cluster是最上层的接口，下面一共有9个实现类。Cluster接口上有SPI注解，也就是说支持扩展机制动态生成的。
> 
> 
> **每个实现类里都只有一个join方法，实现也很简单，直接`“new”` 一个对应的Clusterinvoker。其中AvailableCluster例外，直接使用匿名内部类实现了所有功能。**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%203.png)
> 
- `Clusterinvoker`的类结构

> Invoker 接口是最上层的接口，它下面分别有 AbstractClusterlnvoker> MockClusterlnvoker和 MergeableClusterlnvoker 三个类。其中，AbstractClusterlnvoker 是一个抽象类，其封装了通用的模板逻辑，如获取服务列表、负载均衡、调用服务提供者等，并预留了一个dolnvoke方法需要子类自行实现。AbstractClusterlnvoker T面有7个子类，分别实现了不同的集群容错机制。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%204.png)

- 注意

> MockClusterlnvoker和MergeableClusterlnvoker由于并不适用于正常的集群容错逻辑，因此没有挂在AbstractClusterlnvoker下面，**而是直接继承了 Invoker接口**。
> 

### 2.3 Failover 策略

- 概述

> Cluster 接口上有 SPI 注解`@SPI(FailoverCluster.NAME)`，即默认实现是 Failover。该策略的代码逻辑如下：前3步都是做一些校验、数据准备的工作。第4步开始真正的调用逻辑。
> 
> 1. 校验。校验从AbstractClusterlnvoker传入的Invoker列表是否为空。
> 2. 获取配置参数。从调用URL中获取对应的retries重试次数。
> 3. 初始化一些集合和对象。用于保存调用过程中出现的异常、记录调用了哪些节点(这个会在负载均衡中使用，在某些配置下，尽量不要一直调用同一个服务)。
> 4. 使用for循环实现重试，for循环的次数就是重试的次数。成功则返回，否则继续循环。 如果for循环完，还没有一个成功的返回，则抛出异常，把(3)中记录的信息抛出去。

==细节之——第四步——for循环中的逻辑==

> • 校验。如果for循环次数大于1，即有过一次失败，则会再次校验节点是否被销毁、传入的Invoker列表是否为空。
• 负载均衡。调用select方法做负载均衡，得到要调用的节点，并记录这个节点到步骤3的集合里，再把己经调用的节点信息放进RPC上下文中。
• 远程调用。调用`invoker#invoke`方法做远程调用，成功则返回，异常则记录异常信息， 再做下次循环
> 
- Failover流程

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%205.png)

### 2.4 Failfast 策略

- 步骤概述

> Failfast会在失败后直接抛出异常并返回，实现非常简单，步骤如下：
> 
> 1. 校验。校验从AbstractClusterlnvoker传入的Invoker列表是否为空。
> 2. 负载均衡。调用select方法做负载均衡，得到要调用的节点。
> 3. 进行远程调用。在try代码块中调用`invoker#invoke`方法做远程调用。如果捕获到异常，则直接封装成RpcException抛出。

### 2.5 Failsafe 策略

- 步骤概述

> Failsafe调用时如果出现异常，则会直接忽略。实现也非常简单，步骤如下：
> 
> 1. 校验传入的参数。校验从AbstractClusterlnvoker传入的Invoker列表是否为空。
> 2. 负载均衡。调用select方法做负载均衡，得到要调用的节点。
> 3. 远程调用。在try代码块中调用invoker#invoke方法做远程调用，“catch”到任何异常都直接“吞掉”，返回一个空的结果集。

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%206.png)

### 2.6 Failback 策略

- 步骤概述

> Failback如果调用失败，**则会定期重试**。FailbackClusterlnvoker里面定义了一个ConcurrentHashMap，专门用来保存失败的调用。另外定义了一个定时线程池，**默认每5秒把所有失败的调用拿出来**，重试一次。如果调用重试成功，则会从ConcurrentHashMap中移除。
> 
> 1. 校验传入的参数。校验从AbstractClusterlnvoker传入的Invoker列表是否为空。
> 2. 负载均衡。调用select方法做负载均衡，得到要调用的节点。
> 3. 远程调用。在try代码块中调用invoker#invoke方法做远程调用，`“catch”`到异常后直接把invocation保存到重试的ConcurrentHashMap中，并返回一个空的结果集。
> 4. 定时线程池会定时把ConcurrentHashMap中的失败请求拿出来重新请求，请求成功则从ConcurrentHashMap中移除。如果请求还是失败，则异常也会被“catch”住，不会影响ConcurrentHashMap中后面的重试。
- 重试步骤

> 在新版中是使用一个timer和内部类RetryTimerTask去实现重试任务。大致的步骤就是得到失败任务调用addFailed方法加入重试任务，然后task的run方法得到重试任务进行重试
> 

### 2.7 Available 策略

- 步骤概述

> Available是找到第一个可用的服务直接调用，并返回结果。步骤如下：
> 
> 1. 遍历从AbstractClusterlnvoker传入的Invoker列表，如果Invoker是可用的，则直接调用并返回。
> 2. 如果遍历整个列表还没找到可用的Invoker,则抛出异常。

### 2.8 Broadcast 策略

- 步骤概述

> Broadcast会广播给所有可用的节点，如果任何一个节点报错，则返回异常。步骤如下：
> 
> 1. 前置操作。校验从AbstractClusterlnvoker传入的Invoker列表是否为空；在RPC上下文中设置Invoker列表；初始化一些对象，用于保存调用过程中产生的异常和结果信息等。
> 2. 循环遍历所有Invoker，直接做RPC调用。任何一个节点调用出错，并不会中断整个广播过程，会先记录异常，在最后广播完成后再抛出。如果多个节点异常，则只有最后一个节点的异常会被抛出，前面的异常会被覆盖

### 2.9 Forking 策略

- 步骤概述

> Forking可以同时并行请求多个服务，有任何一个返回，则直接返回。相对于其他调用策略，Forking的实现是最复杂的。其步骤如下：
> 
> 1. 准备工作。校验传入的Invoker列表是否可用；初始化一个Invoker集合，用于保存真正要调用的Invoker列表；从URL中得到最大并行数、超时时间。
> 2. 获取最终要调用的Invoker列表。假设用户设置最大的并行数为n，实际可以调用的最大服务数为v。如果n<0或n<v，则说明可用的服务数小于用户的设置，因此最终要调用的Invoker只能有v个；如果n<v,则会循环调用负载均衡方法，不断得到可调用的Invoker，加入步骤1中的Invoker集合里。
> 
> > 这里有一点需要注意：在Invoker加入集合时，会做去重操作。因此，如果用户设置的负载均衡策略每次返回的都是同一个Invoker，那么集合中最后只会存在一个Invoker，也就是只会调用一个节点。
> > 
> 1. 调用前的准备工作。设置要调用的Invoker列表到RPC上下文；初始化一个异常计数器；初始化一个阻塞队列，用于记录并行调用的结果。
> 2. 执行调用。循环使用线程池并行调用，调用成功，则把结果加入阻塞队列；调用失败， 则失败计数+1。如果所有线程的调用都失败了，即失败计数>=所有可调用的Invoker时，则把异常信息加入阻塞队列。
> 
> > 这里有一点需要注意：并行调用是如何保证个别调用失败不返回异常信息，只有全部失败才返回异常信息的呢？因为有判断条件，当失败计数N所有可调用的Invoker时，才会把异常信息放入阻塞队列，所以只有当最后一个Invoker也调用失败时才会把异常信息保存到阻塞队列， 从而达到全部失败才返回异常的效果。
> > 
> 1. 同步等待结果。由于步骤4中的步骤是在线程池中执行的，因此主线程还会继续往下执行，主线程中会使用阻塞队列的poll(-超时时间“)方法，同步等待阻塞队列中的第一个结果， 如果是正常结果则返回，如果是异常则抛出。
- 总结

> 从上面步骤可以得知，Forking的超时是通过在阻塞队列的poll方法中传入超时时间实现的； 线程池中的并发调用会获取第一个正常返回结果。只有所有请求都失败了，Forking才会失败。
> 
- 调用流程图

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%207.png)

## 3.Directory的实现

- 概述

> 整个容错过程中首先会使用Directory#list来获取所有的Invoker列表。Directory也有多种实现子类，既可以提供静态的Invoker列表，也可以提供动态的Invoker列表。静态列表是用户自己设置的Invoker列表；动态列表根据注册中心的数据动态变化，动态更新Invoker列表的数据，整个过程对上层透明。
> 

### 3.1 总体实现

- 类结构

> 又是熟悉的“套路”，使用了模板模式。Directory是顶层的接口。AbstractDirectory封装了通用的实现逻辑。抽象类包含`RegistryDirectory和StaticDirectory`两个子类。
> 
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%208.png)
> 
- 不同子类的职责和工作

==AbstractDirectory==

> 封装了通用逻辑，主要实现了四个方法：检测Invoker是否可用， 销毁所有Invoker， list方法，还留了一个抽象的doList方法给子类自行实现。list方法是最主要的方法，用于返回所有可用的list，逻辑分为两步：
> 
> - 调用抽象方法doList获取所有Invoker列表，不同子类有不同的实现；
> - 遍历所有的router,进行Invoker的过滤，最后返回过滤好的Invoker列表。

> **doList抽象方法则是返回所有的Invoker列表，由于是抽象方法，子类继承后必须要有自己的实现。**
> 

==RegistryDirectory==

> 属于Directory的动态列表实现，会自动从注册中心更新Invoker列表、配置信息、路由列表。
> 

==StaticDirectory==

> Directory的静态列表实现，即将传入的Invoker列表封装成静态的Directory对象，里面的列表不会改变。因为`Cluster#join(Directopy<T> directory)`方法需要传入Directory对象，因此该实现主要使用在一些上层已经知道自己要调用哪些Invoker，只需要包装一个 Directory对象返回即可的场景。
> 

> 在`ReferenceConfig#createProxy`和`RegistryDirectory#toMergeMethodInvokerMap` 中使用了 `Cluster#join` 方法。StaticDirectory 的逻辑非常简单，在构造方法中需要传入Invoker列表，doList方法则直接返回初始化时传入的列表。因此，不再详细说明。
> 

### 3.2 RegistryDirectory 的实现

- 概述

> RegistryDirectory中有两条比较重要的逻辑线：
> 
> - 第一条，框架与注册中心的订阅，并动态更新本地Invoker列表、路由列表、配置信息的逻辑；
> - 第二条，子类实现父类的doList方法。

==订阅与动态更新==

> 我们先看一下订阅和动态更新逻辑。这个逻辑主要涉及`subscribe、notify、refreshinvoker`三个方法，其余是一些数据转换的辅助类方法，如`toConfigurators、 toRouters`
> 
> - subscribe是订阅某个URL的更新信息。Dubbo在引用每个需要RPC调用的Bean的时候， 会调用`directory.subscribe`来订阅这个Bean的各种URL的变化(Bean的配置在配置中心中都是以URL的形式存放的)。这个方法比较简单，只有两行代码，仅仅使用`registry.subscribe`订阅。
> - notify：就是监听到配置中心对应的URL（配置configurators、路由规则router、Invoker列表）的变化，然后更新本地的配置参数。
- 监听更新配置的工作流程：

> 
> 
> 1. 新建三个List，分别用于保存更新的`Invoker URL、路由配置URL、配置URL`。遍历监听返回的所有URL，分类后放入三个List中。
> 2. 解析并更新配置参数。对于每种URL的具体更新过程如下：
>     - 对于router类参数，首先遍历所有router类型的URL,然后通过Router工厂把每个URL包装成路由规则，最后更新本地的路由信息。这个过程会忽略以empty开头的URL
>     - 对于Configurator类的参数，管理员可以在dubbo-admin动态配置功能上修改生产者的参数，这些参数会保存在配置中心的configurators类目下。notify监听到URL配置参数的变化，会解析并更新本地的Configurator配置。
>     - 对于Invoker类型的参数，如果是empty协议的URL，则会禁用该服务，并销毁本地缓存的Invoker；如果监听到的Invoker类型URL都是空的，则说明没有更新，直接使用本地的老缓存；如果监听到的Invoker类型URL不为空，则把新的URL和本地老的URL合并，创建新的Invoker,找出差异的老Invoker并销毁。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%209.png)
> 
- override参数的URL举例

> dubbo-admin（服务治理平台）上更新路由规则或参数是通过`“override://”`协议实现的。override协议的URL会覆盖更新本地URL中对应的参数。如果是`“empty://"`协议的URL，则会清空本地的配置，这里会调用Configurator接口来实现该功能。
> 
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2010.png)
> 

==doList的实现==

> notify中更新的Invoker列表最终会转化为一个字典`Map<String, List<Invoker<T>>>methodlnvokerMap`。key是对应的方法名称，value是整个Invoker列表。doList的最终目标就是在字典里匹配出可以调用的Invoker列表，并返回给上层。
> 
> 1. 检查服务是否被禁用。如果配置中心禁用了某个服务，则该服务无法被调用。如果服务被禁用则会抛出异常。
> 2. 根据方法名和首参数匹配Invokero这是一个比较奇特的特性。根据方法名和首参数查找对应的Invoker列表，暂时没看到相关的应用场景。**如果在这一步没有匹配到Invoker列表，则进入第3步**。

```java
void test(String arg) //假设有 test 方法
test(“123”); //调用该方法
test .123 //用 test 123 在 methodlnvokerMap 中匹配对应的 Invoker 列表
```

> 
> 
> 1. 根据方法名匹配Invokero以方法名为key去methodlnvokerMap中匹配Invoker列表，如果还是没有匹配到，则进入第4步。
> 2. 根据`"*”`匹配Invokero用星号去匹配Invoker列表，如果还没有匹配到，则进入最后一步兜底操作。
> 3. 遍历methodlnvokerMap,找到第一个Invoker列表返回。如果还没有，则返回一个空列表。

## 4.路由的实现

- 概述

> 通过上节的Directory获取所有Invoker列表的时候，就会调用到本节的路由接口。路由接口会根据用户配置的不同路由策略对Invoker列表进行过滤，只返回符合规则的Invoker。
> 

> 例如：如果用户配置了接口 A的所有调用，都使用IP为192.168.1.22的节点，则路由会过滤其他的 Invoker，只返回 IP 为 192.168.1.22 的 Invoker
> 

### 4.1 路由的总体结构

- 路由的分类

> 路由分为条件路由、文件路由、脚本路由，对应dubbo-admin中三种不同的规则配置方式。
> 
> - 条件路由是用户使用Dubbo定义的语法规则去写路由规则;
> - 文件路由则需要用户提交一个文件，里面写着对应的路由规则，框架基于文件读取对应的规则；
> - 脚本路由则是使用JDK自身的脚本引擎解析路由规则脚本，所有JDK脚本引擎支持的脚本都能解析，默认是JavaScript
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2011.png)
> 
- 三种路由的SPI配置

```yaml
file=org.apache.dubbo.rpc.cluster.router.file.FileRouterFactory
script=org.apache.dubbo.rpc.cluster.router.script.ScriptRouterFactory
condition=org.apache.dubbo.rpc.cluster.router.condition.ConditionRouterFactory
```

- `RouterFactory`

> RouterFactory是一个SPI接口，没有设置默认值，但由于有`@Adaptive("protocol")`注解， 因此它会根据URL中的protocol参数确定要初始化哪一个具体的Router实现（实现类直接返回一个对应的Router实现）。**当然，FileRouterFactory除外，直接在工厂类中实现了所有逻辑**。
> 

```java
@SPI
public interface RouterFactory {
	@Adaptive("protocol")
	Router getRouter(URL url);
)
```

### 4.2 条件路由的参数规则

- 概述

> 条件路由使用的是 `condition://`协议，URL 形式是`”condition://0.0.0.0/com.fbo.BarService?category=routers&dynamic=false&rule="+ URL.encode(nhost = 10.20.153.10 => host = 10.20.153.11")。` 我们可以看到，最后的路由规则会用URL.encode进行编码。
> 
- 路由规则

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2012.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2013.png)

- 路由规则配置实例

> `method = find* =＞ host = 192.168.1.22`
> 
> - 这条配置说明所有调用find开头的方法都会被路由到IP为192.168.1.22的服务节点上。
> - =＞之前的部分为消费者匹配条件，将所有参数和消费者的URL进行对比，当消费者满足匹配条件时，对该消费者执行后面的过滤规则。
> - =＞之后的部分为提供者地址列表的过滤条件，将所有参数和提供者的URL进行对比，消费者最终只获取过滤后的地址列表。
> - 如果匹配条件为空，则表示应用于所有消费方，如=＞ host != 192.168.1.22。
> - 如果过滤条件为空，则表示禁止访问，如host = 192.168.1.22 =＞。
- 注意

> 整个规则的表达式支持 protocol等占位符方式，也支持`=、!=`等条件。值可以支持多个， 用逗号分隔，如`host = 192.168.1.22,192.168.1.23`；如果以`“*”`号结尾，则说明是通配符， 如`host = 192.168.1.*`表示匹配`192.168.1.`网段下所有的IP。
> 

### 4.3 条件路由的实现

- 概述

> 条件路由的具体实现类是ConditionRouter, Dubbo会根据自定义的规则语法来实现路由规则。我们主要需要关注其构造方法和实现父类接口的route方法。
> 

==ConditionRouter构造方法的逻辑==

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2014.png)

ConditionRouterFactory在初始化ConditionRouter的时候，其构造方法中含有规则解析的逻辑。还以`method = find* =＞ host = 192.168.1.22`为例，步骤如下：

1. 根据URL的键rule获取对应的规则字符串。以=>为界，把规则分成两段，前面部分为whenRule，即消费者匹配条件；后面部分为thenRule，即提供者地址列表的过滤条件。其会被解析为whenRule： method = find*和thenRule: host =192.168.1.22。
    
    ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2015.png)
    
2. 分别解析两个路由规则。调用parseRule方法，通过正则表达式不断循环匹配whenRule和thenRule字符串。解析的时候，会根据key-value之间的分隔符对key-value做分类(如果A=B,则分隔符为=)，支持的分隔符形式有：A=B、A&B、A!=B、A,B这4种形式。最终参数都会被封装成一个个MatchPair对象，放入Map中保存。Map的key是参数值，value是MatchPair对象。**会生成以method为key的when Map,以host为key的 then Mapo value 则分别是包装了 find*和 192.168.1.22 的 MatchPair 对象。**

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2016.png)

- MatchPair的作用

> 
> 
> 1. **第一个作用是通配符的匹配和占位符的赋值**。MatchPair对象是内部类，里面只有一个isMatch方法，用于判断值是否能匹配得上规则。规则里的`$、*`等通配符都会在MatchPair对象中进行匹配。其中`$`支持protocol、username、password、host、port、path这几个动态参数的占位符。例如：规则中写了`$protocol`，则会自动从URL中获取protocol的值，并赋值进去。
> 2. **第二个作用是缓存规则**。MatchPair对象中有两个Set集合，一个用于保存匹配的规则，如=find*；另一个则用于保存不匹配的规则， 如!=find*o这两个集合在后续路由规则匹配的时候会使用到。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99/image%2017.png)
> 

==route方法的实现原理==

> ConditionRouter继承了 Router接口，需要实现接口的route方法。该方法的主要功能是过滤出符合路由规则的Invoker列表，即做具体的条件匹配判断，其步骤如下：
> 
> 1. 校验。如果规则没有启用，则直接返回；如果传入的Invoker列表为空，则直接返回空；如果没有任何的whenRule匹配，即没有规则匹配，则直接返回传入的Invoker列表；如果whenRule有匹配的，但是thenRule为空，即没有匹配上规则的Invoker,则返回空。
> 2. 遍历Invoker列表，通过thenRule找出所有符合规则的Invoker加入集合。例如：匹配规则中的method名称和当前URL中的method是不是相等。
> 3. 返回结果。如果结果集不为空，则直接返回；如果结果集为空，但是规则配置了force=true,即强制过滤，那么就会返回空结果集；非强制则不过滤，即返回所有Invoker列表。

### 4.4 文件路由的实现

- 概述

> 文件路由是把规则写在文件中，文件中写的是自定义的脚本规则，可以是JavaScript、Groovy等，URL中对应的key值填写的是文件的路径。文件路由主要做的就是把文件中的路由脚本读出来，然后调用路由的工厂去匹配对应的脚本路由做解析。
> 
- 代码实例

```java
//把类型为file的protocol替换为script类型
Stringprotocol = url.getParameter(Constants.ROUTER_KEY，ScriptRouterFactory.NAME)；
//解析文件的后缀名，后续用于匹配的到底是什么脚本，如JS、Groovy等
String type = null;
String path = url.getPath();
if (path != null) {
	int i = path.lastlndexOf('.');
	if (i > 0) {
		type = path.substring(i + 1);
	}
}
//读取文件
String rule = lOUtils.read(new FileReader(new File(url.getAbsolutePath())));
//读取是否是运行时的参数
boolean runtime = url.getParameter(Constants. RUNTIME_KEY? false);
//生成路由工厂可以识别的URL,并把参数添加进去
URL script = url.setProtocol(protocol)
.addParameter(Constants.TYPE_KEY, type)
.addParameter(Constants.RUNTIME_KEY, runtime)
.addParameterAndEncoded(Constants.RULE_KEY, rule);
//再次调用路由的工厂，由于前面配置了 protocol为script类型，这里会使用脚本路由进行解析
return routerFactory.getRouter(script);
```

### 4.5 脚本路由的实现

- 概述

> 脚本路由使用JDK自带的脚本解析器解析脚本并运行，默认使用JavaScript解析器，其逻辑分为构造方法和route方法两大部分。构造方法主要负责一些初始化的工作，route方法则是具体的过滤逻辑执行的地方。
> 
- 脚本实例

```jsx
function route(invokers) {
	//创建了一个 List
	var result = new java.util.ArrayList(invokers.size());
	for (i = 0; i < invokers.size(); i ++) {
		if ("10.20.153.10".equals(invokers.get(i).getUrl().getHost())) {
			//遍历传入的所有Invoker)过滤所有IP不是10.20.153.10 的 Invoker
			result.add(invokers.get(i)); 丁
		}
	}
	return result;
} (invokers); //表示立即执行方法
```

- 脚本路由构造的逻辑

> 
> 
> 1. 初始化参数。获取规则的脚本类型、路由优先级。如果没有设置脚本类型，则默认设置为JavaScript类型，如果没有解析到任何规则，则抛出异常。
> 2. 初始化脚本执行引擎。根据脚本的类型，通过Java的ScriptEngineManager创建不同的脚本执行器，并缓存起来。
- 脚本路由的route逻辑

```java
List<Invoker<T>> invokersCopy = new ArrayList<Invoker<T>>(invokers);
Compilable compilable = (Compilable) engine;
//构造要传入脚本的参数
Bindings bindings = engine. createBindings();
bindings.put("invokers"> invokersCopy);
bindings.put("invocation", invocation);
bindings.put(''context", RpcContext.getContext());
CompiledScript function = compilable.compile(rule);
// 执行脚本
Object obj = function, eval(bindings);
```