# 深入理解Dubbo与实战（四）| Dubbo远程调用

type: Post
status: Published
date: 2022/08/15
summary: Dubbo远程调用
tags: Dubbo
category: 中间件

# Dubbo远程调用

- 概述

> 本章首先介绍Dubbo的核心调用流程，接下来讲解Dubbo内部协议的设计和实现，通过对具体协议细节的理解，我们可以更好地掌握RPC通信的核心原理。在理解现有RPC协议的基础上，我们会对编解码器实现展开深入解析，同时对本地Telnet调用展开分析，最后对Dubbo线程模型进行深入探讨。
> 

## 1.Dubbo调用介绍

- 简单回顾远程调用的步骤

> 如果我们动手写简单的RPC调用，**则需要把服务调用信息传递到服务端，每次服务调用的一些公用的信息包括服务调用接口、方法名、方法参数类型和方法参数值等，在传递方法参数值时需要先序列化对象并经过网络传输到服务端，在服务端需要按照客户端序列化顺序再做一次反序列化来读取信息，然后拼装成请求对象进行服务反射调用，最终将调用结果再传给客户端。**
> 
- Dubbo下完整的RPC调用

> 
> 
> - 首先在客户端启动时会从注册中心拉取和订阅对应的服务列表，Cluster会把拉取的服务列表聚合成一个Invoker，每次RPC调用前会通过Directory#list获取providers地址（已经生成好的Invoker列表），获取这些服务列表给后续路由和负载均衡使用。
> - 在①中主要是将多个服务提供者做聚合。在框架内部另外一个实现Directory接口是RegistryDirectory类，它和接口名是一对一的关系（每一个接口都有一个RegistryDirectory实例），主要负责拉取和订阅服务提供者、动态配置和路由项。
> - 在Dubbo发起服务调用时，所有路由和负载均衡都是在客户端实现的。客户端服务调用首先会触发路由操作，然后将路由结果得到的服务列表作为负载均衡参数，经过负载均衡后会选出一台机器进行RPC调用，这3个步骤依次对应于②、③和④。
> - 客户端经过路由和负载均衡后， 会将请求交给底层I/O线程池（比如Netty 处理，I/O线程池主要处理读写、序列化和反序列化等逻辑，因此这里一定不能阻塞操作，Dubbo也提供参数控制 decode.in.io 参数，在处理反序列化对象时会在业务线程池中处理。在⑤中包含两种类似的线程池，一种是I/O线程池Netty ，另一种是Dubbo业务线程池（承载业务方法调用）。
> - 目前Dubbo将服务调用和Telnet调用做了端口复用，在编解码层面也做了适配。在Telnet调用时，会新建立一个TCP连接，传递接口、方法和JSON格式的参数进行服务调用，在编解码层面简单读取流中的字符串（因为不是Dubbo标准头报文），最终交给Telnet对应的Handler去解析方法调用。如果是非Telnet调用，则服务提供方会根据传递过来的接口、分组和版本信息查找Invoker对应的实例进行反射调用。在⑦中进行了端口复用，如果是Telnet调用，则先找到对应的Invoker进行方法调用。Telnet和正常RPC调用不一样的地方是序列化和反序列化使用的不是Hessian方式，而是直接使用fastjson进行处理。

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image.png)

- 注意

> 我们就下来讲述的调用细节是针对于图中5、6和7这三个步骤
> 

## 2.Dubbo协议详解

- 概述

> Dubbo协议借鉴了TCP/IP的设计，一次调用包括协议头和协议体
> 
- 报文结构

> 16字节长的报文头部主要携带了魔法数(Oxdabb)，以及当前请求报文是否是Request、Response 心跳和事件的信息，请求时也会携带当前报文体内序列化协议编号。除此之外，报文头部还携带了请求状态，以及请求唯一标识和报文体长度
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%201.png)

- Dubbo报文字段解析

> 在传输方和接收方都会严格遵守相同的顺序读取消息，客户端发起请求的消息体依次保存下列内容：`Dubbo版本号、服务接口名、服务接口版本、方法名、参数类型、方法参数值和请求额外参数(attachment)。`
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%202.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%203.png)

- 状态响应码及作用一览

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%204.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%205.png)

- 响应标记

> 在返回消息体中，会先把返回值状态标记写入输出流，根据标记状态判断RPC是否正常，
> 
> 
> **比如一次正常RPC调用成功，则先往消息体中写一个标记1，紧接着再写方法返回值。**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%206.png)
> 
- Dubbo中解决粘包解包问题

> 一般TCP中通过特殊字符、换行符、回车或固定长度去解决，而Dubbo中显而易见是通过魔术数来分割处理粘包问题
> 
- Dubbo如何正确响应调用线程：全局请求ID

> 当客户端多个线程并发请求时，框架内部会调用DefaultFuture对象的get方法进行等待。 在请求发起时，框架内部会创建Request对象，这个时候会被分配一个唯一 id， DefaultFuture可以从Request对象中获取id，并将关联关系存储到静态HashMap中，下面是Futures集合。当客户端收到响应时，会根据Response对象中的id，从Futures集合中查找对应DefaultFuture对象，最终会唤醒对应的线程并通知结果。
> 
> 
> **客户端也会启动一个定时扫描线程去探测超时没有返回的请求。**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%207.png)
> 

## 3.编解码器原理

- 编解码设计关系

> 
> 
> - AbstractCodec主要提供基础能力，比如校验报文长度和查找具体编解码器等。
> - TransportCodec主要抽象编解码实现，自动帮我们去调用序列化、反序列实现和自动cleanup流。
> - 我们通过Dubbo编解码继承结构可以清晰看到，DubboCodec继承自ExchangeCodec，它又再次继承了 TelnetCodec实现。我们前面说过Telnet实现复用了 Dubbo协议端口，其实就是在这层编解码做了通用处理。
> - 因为流中可能包含多个RPC请求，Dubbo框架尝试一次性读取更多完整报文编解码生成对象，也就是图中的DubboCountCodec，它的实现思想比较简单，依次调用DubboCodec去解码，如果能解码成完整报文，则加入消息列表，然后触发下一个Handler方法调用。

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%208.png)

### 3.1 Dubbo协议编码器

- 概述

> Dubbo中的编码器主要将Java对象编码成**字节流**返回给客户端，主要做两部分事情，构造报文头部，然后对消息体进行序列化处理。所有编解码层实现都应该继承自Exchangecodec，Dubbo协议编码器也不例外。当Dubbo协议编码请求对象时，会调用ExchangeCodec#encode方法。
> 
- 请求对象编码——`ExchangeCodec#encode——encodeRequest`

> 
> 
> 1. 获取URL指定或默认的序列化协议(Hessian2)
> 2. 构造 16 字节头
> 3. 占用 2 个字节存储魔法数
> 4. 在第3个字节(16位和19~23位)分别存储请求标志和序列化协议序号
> 5. 设置请求/响应标记，标记这个请求需要服务端返回
> 6. 设置请求唯一标识，这个标识用于匹配响应的数据
> 7. 跳过buffer头部16个字节，用于序列化消息体
> 8. 序列化请求调用（比如接口、方法、 方法参数类型、方法参数），data —般是调用encodeRequestData方法对Rpclnvocation
> 9. 查是否超过默认8MB大小
> 10. 向消息长度写入头部第12个字节的偏移量（96~127位)
> 11. 定位指针到报文头部开始位置
> 12. 写入完整报文头部到 buffer
> 13. 设置writerindex到消息体结束位置

==细节之——第八步——encodeRequestData==

> 
> 
> 1. 写入框架版本，这里主要用于支持服务端版本隔离和服务端隐式参数透传给客户端的特性
> 2. 写入调用接口
> 3. 写入接口指定的版本，默认为0.0.0。Dubbo允许同一个接口有多个实现，可以指定版本或分组来区分。
> 4. 写入方法名称，指定远程调用的接口方法
> 5. 写入方法参数类型以Java类型方式传递给服务端
> 6. 依次写入方法参数值进行序列化
> 7. 写入隐式参数，这里可能包含timeout和group等动态参数。
- 响应对象的编码——`ExchangeCodec#encode——encodeResponse`

> 
> 
> 1. 获取指定或默认的序列化协议(Hessian2)
> 2. 构造 16 字节头
> 3. 占用2个字节存储魔法数
> 4. 在第3个字节（19~23位）存储响应标志，会将服务端配置的序列化协议写入头部
> 5. 在第4个字节存储响应状态，status会保存服务端调用状态码
> 6. 设置请求唯一标识
> 7. 空出16字节头部用于存储响应体报文
> 8. 序列化响应调用，data一般是Result对象。对服务端调用结果进行编码
> 9. 检查是否超过默认的8MB大小
> 10. 向消息长度写入头部第12个字节偏移量（96~127位)
> 11. 将buffer定位指针到报文头部开始位置
> 12. 写入完整报文头部到 buffer
> 13. 设置writerindex到消息体结束位置
> 14. 如果编码失败，则复位 buffer；处理编码报错复位buffer，否则导致缓冲区中数据错乱
> 15. 将编码响应异常发送给consumer，否则只能等待到超时。所以防止客户端只有等到超时才能感知服务调用返回。
> 16. 告知客户端数据包长度超过限制
> 17. 告知客户端编码失败的具体原因（为了防止报错对象无法在客户端反序列化，在服务端会将异常信息转成字符串处理）

==细节之——第八步——DubboCodec#encodeResponseData==

> 
> 
> 1. 判断客户端请求的版本是否支持隐式参数服务端参数返回到客户端
> 2. 提取正常返回结果
> 3. 在编码结果前，先写一个字节标志
> 4. 分别写一个字节标记和并序列化调用结果
> 5. 标记写一个字节调用抛异常，并序列化异常对象
> 6. 记录服务端Dubbo版本，并返回服务端隐式参数

### 3.2 Dubbo协议解码器

- 概述

> 相比于编码，解码会更加复杂一点。解码工作分为2部分，第1部分解码报文的头部(16字节)，第2部分解码报文体内容，以及如何把报文体转换成Rpclnvocation。
> 
- 读取流解码——ExchangeCodec#decode

> Dubbo协议解码继承了这个类实现，但是在解析消息体时，Dubbo协议重写了decodeBody方法。**整体实现解码过程中要解决粘包和半包问题。**
> 
> 1. 最多读取16个字节，并分配存储空间。如果流中不足16字节，则会把流中数据读取完毕。
> 2. 处理流起始处不是 Dubbo 魔法数0xdabb场景（**在流中判断报文分割点**）——`2~8步`
> 3. 流中还有数据可以读取（判断流可读字节数）
> 4. 为header重新分配空间，用来存储流中所有可读字节
> 5. 将流中剩余字节读取到header中，当流被读取完后，会查找流中第一个Dubbo报文开始处的索引
> 6. 将buffer读索引指向回Dubbo报文开头处(0xdabb)
> 7. 将流起始处至下一个Dubbo报文之间的数据放到header中
> 8. 主要用于解析header数据，比如用于Telnet
> 9. 如果读取数据长度小于16个字节，则期待更多数据
> 10. 取头部存储的报文长度，并校验长度是否超过限制（默认为8MB ）
> 11. 校验是否可以读取完整Dubbo报文，否则期待更多数据
> 12. 解码消息体，is流是完整的RPC调用报文
> 13. 如果解码过程有问题，则跳过这次RPC调用报文

==细节之解码请求报文——解码消息体第十二步——DubboCodec#decodeBody==

> 站在解码器的角度，解码请求一定是通过标志判断类别的，否则不知道是请求还是响应， Dubbo报文16字节头部长度包含了 FLAG_REQUEST标志位。
> 
> 1. 请求标志位被设置，根据标志（是心跳请求还是消费请求还是事件请求等）创建Request对象
> 2. 如果URL参数中有要求的相关属性，在I/O线程中直接解码(比如在Netty的I/O线程中)，然后简单调用decode解码
> 3. 否则交给Dubbo业务线程池解码（延迟）
> 4. 将 Rpclnvocation 作为 Request 的数据域
> 5. 如果解码失败，先做标记并把异常原因记录下来。

> 这里没有提到的是心跳和事件的解码，这两种解码非常简单，心跳报文是没有消息体的， 事件有消息体，在使用Hessian2协议的情况下默认会传递字符R,当优雅停机时会通过发送readonly事件来通知客户端服务端不可用。
> 

==细节之解码请求消息体——消息体转换为Rpclnvocation对象——DecodeableRpcInvocation#decode==

> 在解码请求时，是严格按照客户端写数据顺序来处理的。
> 
> 1. 读取框架版本
> 2. 读取调用接口
> 3. 读取接口指定的版本，默认为0.0.0。用来实现分组和版本隔离。
> 4. 读取方法名称
> 5. 读取方法参数类型，通过类型能够解析出实际参数个数。
> 6. 依次读取方法参数值，这里具体解析参数值是和序列化协议相关的。
> 7. 读取隐式参数，比如同机房优先调用会读取其中的tag值。
> 8. 处理异步参数回调，如果有则在服务端创建reference代理实例（因为参数是回调客户端方法，所以需要在服务端创建客户端连接代理。）

==细节之解析响应报文——DubboCodec#decodeBody——DecodeableRpcResult#decode==

> 就是上面的解码请求报文的另一种情况，在读取服务端响应报文时，先读取状态标志，然后根据状态标志判断后续的数据内容
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%209.png)

1. 响应结果首先会写一个字节标记位，处理返回结果标记位为 Null 值
2. 正常返回，读取方法调用返回值类型。返回值类型方便底层反序列化正确读取，将读取的值存在result字段中。
3. 如果返回值包含泛型，则调用反序列化解析接口
4. 保存（将结果保存在exception字段中）读取的返回值异常结果
5. 读取返回值为Null，并且有隐式参数。在客户端会继续读取保存在HashMap中的隐式参数值。
6. 其他类似隐式参数的读取（当然，还有其他场景，比 如RPC调用有返回值，RPC调用抛出异常时需要隐式参数给客户端的场景等等）

## 4.Telnet调用原理

- 概述

> 编解码器处理有三种场景：`请求、响应和Telent调用`。理解Telnet调用并不难，**编解码器主要把Telnet当作明文字符串处理， 按照Dubbo的调用规范，解析成调用命令格式，然后查找对应的Invoker,发起方法调用即可。**
> 

### 4.1 Telnet指令解析原理

- 概述

> 为了支持未来更多的Telnet命令和扩展性,Telnet指令解析被设置成了扩展点TelnetHandler，每个Telnet指令都会实现这个扩展点。
> 

```java
@SPI
public interface TelnetHandler {
    /**
     * @param channel
     * @param message：message包含处理命令之外的所有字符串参数
     */
    String telnet(Channel channel, String message) throws RemotingException;
}
```

- Telnet指令转发——`TelnetHandlerAdapter#telnet`

> 首先将用户输入的指令识别成command(比如invoke、Is和status)，然后将剩余的内容解析成message，message会交给命令实现者去处理
> 
> 1. 提取执行命令，提取Telnet一行消息的首个字符串作为命令，如果命令行有空格，则将后面的内容作为字符串
> 2. 提取命令后的所有字符串，存到message中
> 3. 检查系统是否有命令对应的扩展点
> 4. 如果存在对应的Telnet扩展点，交给具体扩展点执行
> 5. 在Telnet消息结尾追加回车和换行然后返回给调用方
- Telnet常用指令Invoke——`InvokeTelnetHandler#telnet`

> **当本地没有客户端，想测试服务端提供的方法时，可以使用Telnet登录到远程服务器(Telnet IP port)，根据invoke指令执行方法调用来获得结果。**
> 
> 1. 提取调用方法（由接口名.方法名组成)，去除参数信息
> 2. 提取调用方法参数值
> 3. 提取方法前面的接口
> 4. 提取方法名称
> 5. 将参数JSON串转换成JSON对象
> 6. 接口名、方法、参数值和类型作为检索方法和Invoker对象的条件
> 7. 在真正方法调用前，将JSON参数值转换成Java对象值
> 8. 根据查找到的Invoker、构造Rpclnvocation进行方法调用

### 4.2 Telnet实现健康监测

- 概述

> Telnet提供了健康检查的命令，可以在Telnet连接成功后执行status -1查看线程池、内存和注册中心等状态信息。为了完成线程池监控、内存和注册中心监控等诉求，Telnet提供了新的扩展点Statuscheck
> 

```java
@SPI
public interface StatusChecker {
    /**
     * check status
     * @return status
     */
    Status check();
}
```

- 健康监测对应的实现和作用

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%2010.png)

## 5.ChannelHandler

- 概述

> 我们都知道Dubbo底层通信框架使用了Netty，如果你熟悉Netty框架，那么很容易理解Dubbo内部使用的ChannlHandler组件的原理，Dubbo框架内部使用大量Handler组成类似链表，依次处理具体逻辑，比如编解码、心跳时间戳和方法调用Handler等。**因为Netty每次创建Handler都会经过ChannelPipeline，大量的事件经过很多Pipeline会有较多的开销，因此Dubbo会将多个Handler聚合为一个Handler**
> 

### 5.1 核心Handler和线程模型

- Dubbo中Handler的生命周期（五种状态）

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%2011.png)

- 已经支持的Handler

> Dubbo中提供了大量的Handler去承载特性和扩展，这些Handler最终会和底层通信框架做关联，比如Netty等。一次完整的RPC调用贯穿了一系列的Handler，
> 
> 
> **如果直接挂载到底层通信框架（Netty ,因为整个链路比较长，则需要触发大量链式查找和事件，不仅低效，而且浪费资源。**
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%2012.png)

- handler流转机制——同时具有入站和出站的ChannelHandler布局

> 
> 
> - 如果有一个入站事件被触发， 比如连接或数据读取，那么它会从ChannelPipeline头部开始一直传播到Channelpipeline的尾端。出站的I/O事件将从ChannelPipeline最右边开始，然后向左传播。
> - 在ChannelPipeline传播事件时，它会测试入站是否实现了 ChannellnboundHandler接口，如果没有实现则会自动跳过，出站时会监测是否实现ChannelOutboundHandler,如果没有实现，那么也会自动跳过
> - 在Dubbo框架中实现的这两个接口类主要是NettyServerHandler和NettyClientHandler。Dubbo通过装饰者模式层包装Handler，从而不需要将每个Handler都追加到Pipeline中。**在NettyServer 和 NettyClient 中最多有 3 个 Handler，分别是编码、解码和 NettyServerHandler或 NettyClientHandler**

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%2013.png)

- RPC调用服务方处理Handler的逻辑——`DubboProtocol内部类继承#ExchangeHandlerAdapter`

> 完成服务提供方Invoker实例的查找并进行服务的真实调用
> 
> 1. 找 invocation关联的 Invoker（查找当前已经暴露的服务）
> 2. 调用业务方具体方法，主要包含实例的Filter和真实业务对象，当触发invoker#invoke方法时，就会执行具体的业务逻辑。

> **Handler实现是触发业务方法调用的关键，在前面讲服务暴露时服务端已经按照特定规则(端口、接口名、接口版本和接口分组)把实例Invoker存储到HashMap中， 客户端调用过来时必须携带相同信息构造的key,找到对应Exporter然后调用。**
> 

```java
private ExchangeHandler requestHandler = new ExchangeHandlerAdapter() {
......
}
```

==细节之——ExchangeHandlerAdapter——getInvoker==

> 在服务端唯一标识的服务是由4部分组成的：`端口、接口名、 接口版本和接口分组`，异步回调现在请忽略
> 
> 1. 获取服务暴露协议的端口，比如Dubbo协议默认的端口为20880。
> 2. 获取调用传递的接口(大部分场景都是接口名)
> 3. 根据端口、接口名、接口分组和接口版本构造唯一的key
> 4. 从 HashMap 中获取 Exporter并调用Invoker属性值。
- 业务线程池和I/O线程池（Netty线程池）

> 因为I/O线程用于接收请求，如果I/O线程饱和，则不会接收新的请求。
> 
> - IO线程池：我们描述的I/O线程是指底层直接负责读写报文，比如Netty线程池。**如果一些事件逻辑可以很快执行完成，比如做个标记而已，则可以直接在I/O线程中处理。**
> - 业务线程池：Dubbo中提供的线程池负责业务**方法调用**，我们称为业务线程。**如果事件处理耗时或阻塞，比如读写数据库操作等，则应该将耗时或阻塞的任务转到业务线程池执行**
- Dubbo线程派发

> Dispatcher就是线程池派发器。这里需要注意的是，Dispatcher真实的职责是创建具有线程派发能力的 ChannelHandler，比如 AllChannelHandler 、 MessageOnlyChannelHandler和ExecutionChannelHandler等，其本身并不具备线程派发能力。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%2014.png)

==细节之——Dispatcher——线程分发策略==

> Dispatcher属于Dubbo中的扩展点，这个扩展点用来动态产生Handler，以满足不同的场景。目前Dubbo支持以下6种策略调用，有下面的建议：
> 
> - 具体业务方需要根据使用场景启用不同的策略。建议使用默认策略即可
> - 如果在TCP连接中需要做安全加密或校验，则可以使用ConnectionOrderedDispatcher策略。
> - 如果引入新的线程池，则不可避免地导致额外的线程切换，用户可在Dubbo配置中指定dispatcher属性让具体策略生效。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E5%9B%9B%EF%BC%89%20Dubbo%E8%BF%9C%E7%A8%8B%E8%B0%83%E7%94%A8/image%2015.png)
> 

### 5.2 Dubbo 请求响应 Handler

- `HeaderExchangeHandler`处理的四种场景

> 在Dubbo框架内部，所有方法调用会被抽象成Request/Response,每次调用（一次会话）都会创建一个请求Request，如果是方法调用则会返回一个Response对象。
> 
> 1. 更新发送和读取请求时间戳。
> 2. 判断请求格式或编解码是否有错，并响应客户端失则的具体原因。
> 3. 处理Request请求和Response正常响应。
> 4. 支持Telnet调用。
- 请求响应——`HeaderExchangeHandler#received`

> 该方法就是接收message，去判断是请求、响应或字符串（Telnet）然后做相应的判断
> 
> 1. 更新事件时间戳：负责响应读取时间并更新时间戳，在Dubbo心跳处理中会使用当前值并判断是否超过空闲时间。
> 2. 如果是请求并且是一个事件，处理 readonly 事件，在 channel 中打标，用于Dubbo优雅停机。（因为网络原因，客户端不能及时感知注册中心事件，服务端会发送 readonly报文告知下线。）
> 3. 不是事件，处理方法调用并返回给客户端
> 4. 如果是响应，接收响应，告知业务调用方
> 5. 如果message是字符串，但是客户端不支持 Telnet 调用：检验不支持Telnet调用，因为只有服务提供方暴露服务才有意义。
> 6. 如果支持，触发 Telnet 调用，并将字符串返回给客户端

> 针对于第五、第六步的题外话：这里有个小改进，因为客户端支持异步参数回调，但为什么这里不能支持Telnet调用呢？**异步参数回调客户端实际上也会暴露一个服务，因此针对这种场景Telnet应该是允许调用的。**
> 

==细节之处理请求报文——HeaderExchangeHandler#handleRequest==

> **在处理请求时，因为在编解码层报错会透传到Handler，所以在①中首先会判断是否是因为请求报文不正确，如果发生错误，则服务端会将具体异常包装成字符串返回，如果直接使用异常对象，则可能造成无法序列化的错误**。
> 
> 1. 处理请求格式不正确(编解码)，并把异常传换成字符串返回
> 2. 调用`DubboProtocol#reply`，触发方法调用
> 3. 如果方法调用失败，做容错并返回。
> 4. 当发送请求时，会在DefaultFuture中保存请求对象并阻塞请求线程，会唤醒阻塞线程并将Response中的结果通知调用方。

### 5.3 Dubbo 心跳 Handler

- 概述

> Dubbo默认客户端和服务端都会发送心跳报文，用来保持TCP长连接状态。在客户端和服务端，Dubbo内部开启一个线程循环扫描并检测连接是否超时，在服务端如果发现超时则会主动关闭客户端连接，在客户端发现超时则会主动重新创建连接。默认心跳检测时间是60秒，具体应用可以通过heartbeat进行配置。
> 
- 心跳实现——`HeartBeatTask#run`

> 
> 
> 1. 遍历所有 Channel，在服务端对应的是所有客户端连接，在客户端对应的是服务端连接。
> 2. 忽略关闭的 Channel（Socket连接）
> 3. TCP连接空闲超过心跳时间，发送事件报文：（**判断当前TCP连接是否空闲，如果空闲就发送心跳报文。目前判断是否是空闲的，根据Channel是否有读或写来决定，比如1分钟内没有读或写就发送心跳报文**）
> 4. 客户端空闲超时触发重连：**处理客户端超时重新建立TCP连接，目前的策略是检查是否在3分钟内(用户可以设置)都没有成功接收或发送报文。如果在服务端监测则会通过**
> 5. 主动关闭远程客户端连接