# Netty | 分布式RPC

type: Post
status: Published
date: 2023/04/21
summary: 分布式RPC
tags: Netty
category: 中间件

# 分布式RPC

- 概述

> 这一节我们实现分布式RPC是在第一章的基础上进行扩充，在长连接通信的基础上想要完成完整的分布式RPC还需要完成接下来的两项工作
> 
> - 在编写业务代码时，只需像运用`SpringMVC或Dubbo`一样，引入对应的`jar`包即可，无须关注太多的`Netty`底层实现。
> - 服务端可动态扩展，不用指定具体的`IP`地址和端口进行连接通信。
- 上层协议

> 当服务端与客户端通信时，需要制定上层协议，运用`Java`反射机制，把协议内容与代码进行映射，让业务代码与`Netty的Handler`逻辑处理解耦。同时引入分布式协调器`Zookeeper`，实现服务的注册与发现，动态扩展服务。
> 

## 1.采用Netty实现一套RPC框架

- 概述

> 所谓PRC框架，就是将网络传输对用户透明，用户只需要关注自己调用什么服务即可，其他的任何网络操作都是框架自己来实现的，我们的目标就是将下面2~8步封装成一个RPC框架
> 
- 步骤流程图

> 
> 
> 1. 服务消费方（client）调用以本地调用方式调用服务；
> 2. client stub接收到调用后负责将方法、参数等组装成能够进行网络传输的消息体；
> 3. client stub找到服务地址，并将消息发送到服务端；
> 4. server stub收到消息后进行解码；
> 5. server stub根据解码结果调用本地的服务；
> 6. 本地服务执行并将结果返回给server stub；
> 7. server stub将返回结果打包成消息并发送至消费方；
> 8. client stub接收到消息，并进行解码；
> 9. 服务消费方得到最终结果。
> 
> ![image.png](Netty%20%E5%88%86%E5%B8%83%E5%BC%8FRPC/image.png)
> 
- PRC内部消息处理图

![image.png](Netty%20%E5%88%86%E5%B8%83%E5%BC%8FRPC/image%201.png)

- 复习一边SpringMVC的底层过程

> `SpringMVC`底层主要通过解析URL获取`Controller`对象和对应的接 口方法，然后运用`Java`的反射运行对应的接口方法。获取的方式依赖`@Controller和@RequestMapping`注解，由URL解析出接口方法上的注解`@RequestMapping`的值，再根据这个值映射对应的接口方法。这种映射方式需要把注解`@RequestMapping`的值放入`Map`容器中缓存起来，`Map中 的key`为注解`@RequestMapping`的值、`value`为对应的接口方法的`Method`对象。当读取`URL`时，就相当于有了`key`，此时就可以从容器中获取接口方法的`Method`对象了。
> 

### 1.1 解析请求URL的注解@Remote，并获取相应方法

- 概述

> 本书RPC框架的实现借用的也是上述这种方式，只是具体路径需要 客户端和服务端制定上层协议。客户端每次在发送请求时都需要把请 求路径传送给服务端，服务端获取路径后，在本地缓存`Map`中得到对应 的调用方法。本地缓存`Map`在构建之前需要先编写注解类`@Remote（与SpringMVC中的@RequestMapping注解类似）`，这个注解作用于接口方 法，通过扫描这个注解类，可以获取所有的接口方法。
> 

### 1.2 构建静态单例本地缓存map

- 概述

> 构建本地缓存`Map容器Mediator.methodBeans`，用于缓存所有接口 的对象和方法。把容器放在中介者`Mediator`类中，这个类把`Netty`代码 与业务代码解耦，后面还包含协议的解析，接口方法的调用。
> 

### 1.3 实现相同接口实现类的优先级访问问题

- 概述

> 当Spring容器启动并完成`Bean`的初始化后，可以运用上下文刷新 事件`ContextRefreshedEvent`，在事件中循环遍历容器中的Bean，获取 带有`Controller`的注解对象及其`@Remote`注解方法。并把它们放入缓存 容 器 `Mediator.methodBeans` 中 。 由 于 Netty 服务的启动也是在`ContextRefreshedEvent`事件中完成的，所以两个动作的执行有先后顺 序，为了保证在`Netty`服务启动前所有接口方法都已放入缓存容器中，`Spring`容器提供了`Ordered`接口，用来处理相同接口实现类的优先级问题。
> 

### 1.4 Mediator中介者的进一步完善

- 概述

> 缓存容器`Mediator.methodBeans`初始化后，中介者`Mediator`需要 根据`RequestFuture`请求从缓存容器中获取接口方法。`RequestFuture`类加上路径`String path`属性，服务端`Mediator`根据`path`的值从缓存中 获取调用对象和方法，运用`Java`反射运行业务逻辑处理方法并获取执 行结果。方法参数类型对List泛型集合需要用`JSONArray`反序列化。
> 

### 1.5 服务handler的完善

- 概述

> Mediator类作为中介者，衔接Netty服务的Handler类和业务逻辑 处 理 类 。 如 果 需 要 对 服 务 器 的 Handler 进 行 一 些 改 动 ， 就 引 入Mediator，并把请求RequestFuture交给它去处理。
> 

### 1.6 编写接口实例

- 概述

> 最后编写一个接口实例UserController类，这个类中有根据userId参数获取用户信息的方法。
> 

## 2.分布式RPC的构建

- 为什么需要分布式

> `RPC`框架整合了`Spring`，并实现了`Netty`核心通信代码与业务逻辑 代码的解耦，但这个框架需要客户端指定服务端具体的IP和端口才能 调用，服务无法动态扩展。当然，可以使用`Nginx或LVS`等反向代理服 务实现横向扩展，但修改反向代理服务器配置并重启无法动态扩展。 本节引入一个分布式应用程序协调服务——`Zookeeper`，以实现服务的注册与发现，完成一套分布式动态扩展`RPC`服务。
> 

### 2.1 服务器注册与发现

- 组件的选择

> 注册与发现是分布式RPC所必须具备的功能，市面上比较常用的服务注册与发现的工具有`Zookeeper、Consul、ETCD、Eureka。`
> 

> 我们选用`Zookeeper`这主要是由于很多大数据 组件基本上都会用Zookeeper，如`Hadoop、HBase、JStorm、Kafka`等。Zookeeper主要通过心跳来维护活动会话的临时节点，从而维护集群中 的服务器状态。分布式RPC也是使用Zookeeper的临时节点来维护`Netty`服务状态的，`RPC`客户端运用`Zookeeper`的`Watch`机制监听`Netty`服务在`Zookeeper`上注册的目录，从而及时感知服务列表的改变。
> 
- 架构图

> 在服务端增加 了服务注册功能，同时客户端新增了`Watch`机制，用来监听`Netty`服务 注册在`Zookeeper`上的目录。客户端与Netty服务连接的链路缓存在`ChannelManager`中，一旦发现有`Netty`服务宕机或新增的情况，缓存在`ChannelManager`中的链路就会发生相应的改变。客户端每次在发送请求之前都需要从`ChannelManager`中轮询获取一个连接。
> 

![image.png](Netty%20%E5%88%86%E5%B8%83%E5%BC%8FRPC/image%202.png)

- ChannelManager的服务发现的负载均衡

> **分布式服务发现的负载均衡算法采用的是`轮询加权重`，每个服务 的权重信息都放在配置文件中，当Netty服务启动并向Zookeeper注册 时，需要加上其权重信息。由于Netty服务与Zookeeper的会话也会出 现被断开的情况，所以也需要在服务端加入监听机制。**
> 

### 2.1.1 服务监听ServerWatcher+Netty服务中的修改

- 概述

> 修改Netty服务，加上服务注册与服务监听`ServerWatcher`类，只要发现其服务本身与`Zookeeper`的临时会话丢失，就需要重新注册
> 

> 分布式RPC服务端的修改基本上已完成，需要注意的是，一定要把 服务端与Zookeeper的监听加上，否则会出现服务端正常运行，但Zookeeper中没有此服务端注册的临时节点的情况。Zookeeper的地 址，以及Netty服务启动监听端口、权重、服务注册到Zookeeper的路 径都需要写入配置文件中，不能写死在代码里
> 
- Netty服务修改

> 就是让其创建Zookeeper的客户端进行路径绑定等
> 

### 2.1.2 链路管理ChannelManager

- 概述

> 客 户 端 新 增 与 服 务 器 列 表 连 接 的 链 路 管 理 类`ChannelManager`，拥有链路缓存链表，以及对此链表提供增、删、改、查的方法，且必须为原子性操作。就是管理服务实现负载均衡的。同时提供轮询获取连接链路的方法，以及其他修改缓存链表的辅助方法。
> 

### 2.1.3 客户端监听器ServerChangeWatcher

- 概述

> 客户端新增监听器`ServerChangeWatcher`，监听`Netty`服务注 册在`Zookeeper`上的目录，且主要监听其子目录的变化。同时调用`ChannelManager`修改其链路缓存链表。当获取不到连接时，还需提供初始化连接方法。
> 

### 2.1.4 将IP和端口改为动态获取对应的服务

- 概述

> 调整客户端，不再通过服务端IP和端口直连，改成从`ChannelManager`中获取连接。即将bootStrap进行构建并返回给ChannelManager，然后直接通过配置文件进行连接
> 

### 2.2 动态代理

- 透明化远程服务调用

> 分布式RPC框架在每次发送请求时都需要查看接口文档，根据接口 文档封装好请求参数，指定具体的调用方法并设置请求路径，只有这 样才能实现远程调用。显然，这种方式开发效率低、使用不够便捷。 想要把分布式RPC改造成类似Dubbo的框架，在只引入接口的jar包依 赖、调用对应的接口方法的情况下完成远程调用，就需要引入动态代理
> 
- 代理过程

> 用户在登录时使用动态代理获取用户信息的远程调用过 程，当调用登录接口时，运行UserService对象的getUserInfo()方法 获取用户信息。然而，UserService是个接口，需要在服务启动时采用Java的反射机制把UserService属性换成一个代理对象。
> 

![image.png](Netty%20%E5%88%86%E5%B8%83%E5%BC%8FRPC/image%203.png)

- 代理的分类

> • JDK 动 态 代 理 ： 通 过 java.lang.reflect.Proxy 类 的newProxyInstance()方法反射生成代理类。
• Cglib动态代理：采用Enhancer类的create()方法生成代理 类，底层利用ASM字节码生成框架，在内存中生成一个需要被代理类的子类。
> 

### 2.2.1 JDK动态代理

- 前言

> 在编码前先了解Spring的一个扩展接口——`BeanPostProcessor`。为了实现此接口及其两个方 法，可以在Bean初始化前后进行一些额外的处理，这两个方法分别是`postProcessBeforeInitialization() 和 postProcessAfterInitialization()`。当bean在初始化并检测到远程 调用的`Service`属性时，把对应的`Service`属性通过`Java`反射和动态代 理修改成代理类
> 

![image.png](Netty%20%E5%88%86%E5%B8%83%E5%BC%8FRPC/image%204.png)

- 实现功能

> **动态代 理远程调用RPC服务端；在Bean初始化前获取所有远程调用属性并生成 代理属性，以替换远程调用属性；使用注解`RemoteInvoke`标识远程调 用属性。同时，由于`RequestFuture`对象在动态3代理类中已构建了，所 以`NettyClient`类还需要重载一个`sendRequest()`方法。**
> 

### 1.2.2 Cglib动态代理

- 概述

> 若使 用Cglib动态代理代替JDK动态代理，就需要把JdkProxy的@Component注解注释掉，同时新增一个类CglibProxy。CglibProxy与JdkProxy的 区别在于动态代理属性的构建方式不同，Cglib动态代理使用Enhancer代替JDK动态代理的Proxy。至此，整个分布式RPC服务的编码全部结束 了 ， 可 以 对 部 分 代 码 进 行 优 化 调 整 。 例 如 ， 序 列 化 在 使 用 了SPI（Service Provider Interface）技术后，可以不用写死在代码中，这样可增强代理类的扩展性。
>