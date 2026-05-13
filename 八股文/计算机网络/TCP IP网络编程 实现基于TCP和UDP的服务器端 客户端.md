# TCP/IP网络编程 | 实现基于TCP和UDP的服务器端/客户端

type: Post
status: Published
date: 2023/10/19
summary: 实现基于TCP和UDP的服务器端/客户端
tags: 计算机网络
category: 技术分享

## **实现基于TCP的服务器端/客户端**

### **1.1 TCP服务器的默认函数调用顺序**

![](https://www.notion.so/image/attachment%3A0b5e0101-7915-4caf-8bfe-cd2f8b3cbc99%3Aimage.png?table=block&id=33444451-4a31-801d-864d-fa0aaef4d7cb&spaceId=da3c3337-76d8-4b65-a581-d5573d6be963&width=850&userId=c04682dd-0470-47b9-a535-478c15bfc869&cache=v2)

### **1.2 进入等待连接状态**

因为已经讨论过了socket以及bind了，所以这里直接开始说明listen函数，在使用bind函数给socket分配地址信息后，就可调用listen函数进入等待连接的状态，若此时客户端提前调用connect则会出错，即调用listen后客户端才能connect

等待队列：等待链接状态是服务端的socket的行为，那么socket能处理几个，顺序是什么，这就用到了等待队列，这里可以类比为服务端socket是看守员，他来看新来的请求能不能处理，如果不能处理则去等待室即等待队列

listen(服务器套接字, 等待队列的大小)

### **1.3 受理客户端的请求**

受理请求即处理当前的请求，那么是谁来处理，或者说是谁来将这个请求转化为受理中，答案是显而易见的，即socket，但是如果直接用服务端的socket来处理那就没有处理等待队列的能力了，所以这时就需要根据accept的参数信息在服务端新建一个socket，来处理受理的请求

accept(服务器套接字, 客户端地址, 客户端地址长度)

### **2.1 TCP客户端调用过程**

这里其实就需要说明一点，可以看到客户端没有socket与地址的绑定过程，其实这个过程在connect函数中就完成了，IP就是客户端的IP，而端口号则是随机分配

![](https://www.notion.so/image/attachment%3Ae984fd95-e54a-4797-aa64-37504a134828%3Aimage.png?table=block&id=33444451-4a31-807e-ac57-cd6eb9a5e118&spaceId=da3c3337-76d8-4b65-a581-d5573d6be963&width=680&userId=c04682dd-0470-47b9-a535-478c15bfc869&cache=v2)

### **3.1 TCP服务端/客户端函数调用关系**

![](https://www.notion.so/image/attachment%3A846b8e5d-dc36-4cdf-b7b9-8ea0bf54d437%3Aimage.png?table=block&id=33444451-4a31-8048-b59e-ddaf7209c581&spaceId=da3c3337-76d8-4b65-a581-d5573d6be963&width=1170&userId=c04682dd-0470-47b9-a535-478c15bfc869&cache=v2)

### **以书中的例子来看回声客户端存在的问题，前提是以一个字符串作为单位**

客户端写完发送一次的信息，立马去读一次，并且期待立马接收

在TCP无数据边界的情况下，可能会发生发送了很多字符串，通过read一次性接收了，这是我们不希望看到的

同样还有可能发生，客户端发送字符串太大，服务端会分两次回传，同时如果客户端接收到第一次就调用read方法，这同样存在问题——能否进行等待，但是等多久？

![](https://www.notion.so/image/attachment%3Aa5c34ebd-f4dc-42c8-93cc-1885ffe7366d%3Aimage.png?table=block&id=33444451-4a31-80bf-8772-c185ec2f1b91&spaceId=da3c3337-76d8-4b65-a581-d5573d6be963&width=1170&userId=c04682dd-0470-47b9-a535-478c15bfc869&cache=v2)

解决方案：其实两者事先约定好发多少收多少即可，我发送20字节的数据，那么我就知道等20字节的数据

### **如果回声客户端无法知道传输数据的大小呢**

这时就需要两方同时制定一个规则，例如回声客户端中输

## 实现基于UDP的服务器端/客户端

这里简单提一嘴UDP中的socket数量与TCP有一些不同，假设有10个客户端socket或者一个客户端的10个socket通过TCP连接服务端，那么服务端创建的socket数量就有11个（10+门卫），而在UDP则只有1个，无论客户端还是服务端始终只有一个，这里指的个数都是指的是socket的数量

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E5%AE%9E%E7%8E%B0%E5%9F%BA%E4%BA%8ETCP%E5%92%8CUDP%E7%9A%84%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%20%E5%AE%A2%E6%88%B7%E7%AB%AF/image.png)

同时这里给UDP客户端分配IP和端口号的函数不同于TCP客户端调用connect，在UDP中实际上是sendto函数

### **1.1 UDP存在数据边界**

不存在数据边界即表示“数据传输过程中调用I/O函数的次数不具有任何意义”，UDP是基于数据包的传输形式，每个数据包都有它自己的边界，而同时TCP由于是基于字节流的传输方式，那么就不关注边界，发送多次可以先在缓冲区中统一发送，而客户端也不用只读取一次，可以分多次读取，那么I/O的次数就不存在意义；相反UDP由于分数据包，那么有很多个数据包需要接收，次数就有实际意义了，因为发送方发几次，接收方接收几次，当两者相等那么就证明数据是完整的，通常将类比到TCP，发送方发送三次，实际上接收方一次读取即可；

数据报：发送一次的数据包即为一个完整的数据，称为数据报

### **UDP套接字的反复使用？**

在学习TCP中常听到一句话：TCP面向连接的协议，我们可以通过解析UDP套接字的创建与销毁过程来理解这句话

从下图中可以看到当不传输数据时，伴随着删除UDP套接字信息的过程，那么每次如果接收方的地址不通，就可以用同一套接字来注册不同的内容来完成反复使用，这种套接字就称之为无连接套接字，那么显而易见面对长时间通信需求时，如果每次发送都需要注册信息，效率肯定没有面向连接的套接字高，因为第一第三步骤占了整个通信成本的三分之一

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E5%AE%9E%E7%8E%B0%E5%9F%BA%E4%BA%8ETCP%E5%92%8CUDP%E7%9A%84%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%20%E5%AE%A2%E6%88%B7%E7%AB%AF/image%201.png)

### **具体如何复用？**

直接调用connect方法，去使用已经创建好连接的套接字来节省效率，connect以后的函数使用就可以只能使用sendto、revfrom函数，还可以使用read、write函数

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E5%AE%9E%E7%8E%B0%E5%9F%BA%E4%BA%8ETCP%E5%92%8CUDP%E7%9A%84%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%20%E5%AE%A2%E6%88%B7%E7%AB%AF/image%202.png)

## 如何优雅的断开套接字连接

### **1.1 半关闭**

在前文中说到无论是linux还是win下的close函数都是直接将当前终端的输入/输出流全部关闭，这其实并不能称为优雅，同时也会导致一个问题，当A终端发送关闭函数后立马关闭输入/输出，那么会接收不到必须接收被关闭B终端发来的信息，**所以半关闭的意思就是能够发送但不能接收亦或者是能够接收不能发送**

**注意：**

**这里的关闭指的是应用层面的，而数据传输层还是会完成四次挥手的动作，而四次挥手中本身就存在两次半关闭，即我们指的实际上是编码应用层面上的半关闭！**

### **1.2 流与套接字**

实际上如果流只有单一方向，那么为了实现双向通信，就肯定要有两个流

### **1.3 shotdown函数**

整个函数的定义如下

```java
shutdown(int sock, int shotType);
 
#define SHUT_RD         0               /* shut down the reading side */
#define SHUT_WR         1               /* shut down the writing side */
#define SHUT_RDWR       2               /* shut down both sides */
```

---

### **1.4 为什么需要shotdown/半关闭**

其实只要不急于立马结束流，其实也可以不用半关闭？

拿传输文件这个例子来举例：

- 假设客户端接收服务器的一个文件流，在接收完成后发送一个“接收完成”，这里只是假设当接收完文件后客户端还需要发送信息给服务端，客户端怎么知道何时传递完成，在这个期间可能会一直调用输入函数，会导致阻塞
- 服务端发送结束后在文件流结尾放一个EOF标志位？但如果是close的关闭，那么服务端发送完后同样接收不到客户端给的响应，所以这时就需要半关闭了

### **1.5 Time-wait状态**

这个状态位于四次挥手之后的一段时间，谁发起的终止连接（首次发送FIN的一方）谁就会有这种状态，当服务端如果终止以后，立马在相同的端口启动该服务，则会报错：bind error

这个状态存在的意义是为了解决在发送最后一次挥手的消息之后立马发起终止，同时，这个消息还丢失了，那么接收方就会认为自己的FIN消息并没有被收到就会重发，但是永远收不到发送方的ACK了

### **Time-wait存在的问题**

发送ACKTime-wait计时器启动，如果ACK丢失的期间，接收到FIN后，再次发送ACK后计时器会被重制，如果此时服务重启后会重启失败报错，因为还处于这个状态（通常为120秒），所以在可以在socket中设置参数，来保证重启后使用新的socket

### **1.6 分离I/O流的两种方式和好处**

1、文件描述符的fork来区分IO流：即通过fork方法来复制出来一个文件描述符，一个输入一个输出，有点显而易见，降低编写难度，与输入无关的操作输出则可以提高速度

2、通过调用两次fdopen，获取两个FLIE指针，分为读模式和写模式，同样是为了降低编写难度，加入IO缓冲流时也很简单的分出了输入输出缓冲流的区别

> 对于第二种来说，通常搭配的系列函数都是f开头的（标准IO接口），这种分流如果要实现半关闭，则不能直接调用fclose，因为这个函数直接就把流给关闭了而不是半关闭，本质上是因为fdopen是基于一个文件miao'shu
> 

## DNS

如何查看否个域名的DNS，在类unix系统中控制台输入：nslookup

```java
> nslookup
>
>
>
> server
Default server: 2408:8409:2410:db66::6f
Address: 2408:8409:2410:db66::6f#53
Default server: 192.168.198.112
Address: 192.168.198.112#53
> quit
Server:     2408:8409:2410:db66::6f
Address:    2408:8409:2410:db66::6f#53
 
** server can't find quit: NXDOMAIN
> baidu
Server:     2408:8409:2410:db66::6f
Address:    2408:8409:2410:db66::6f#53
 
Non-authoritative answer:
*** Can't find baidu: No answer
> baidu.com
Server:     2408:8409:2410:db66::6f
Address:    2408:8409:2410:db66::6f#53
 
Non-authoritative answer:
Name:   baidu.com
Address: 39.156.66.10
Name:   baidu.com
Address: 110.242.68.66
# 退出
> exit
```

## Nagle算法

在TCP中由于发送的信息本身就带有数据流的顺序，那么实际上没有接收到ACK就能发送当前网络缓冲区的其他内容，那么在网络带宽小的情况下很容易产生阻塞，因为很快就把连接时发送方拿到的接收方的缓冲区大小打满了，慢慢就拥堵了，所以有了Nagle算法，一份一份处理。

### **Nagle的缺点：**

缺点显而易见，就是在传输大文件时效率不是很高，所以需要准确判断数据特性时在确定打不打开Nagle算法

### **Java中的禁用方式：**

在Java中，当使用TCP进行数据传输时，可以通过`Socket`类的`setTcpNoDelay(boolean on)`方法来禁用Nagle算法。如果将这个方法的参数设置为`true`，那么就会禁用Nagle算法，允许小包的即时发送，而不是等待更多的数据累积以减少网络中的小包数量。

以下是一个示例代码片段，展示了如何在创建`Socket`之后禁用Nagle算法：

```java
try {
    Socket socket = new Socket("example.com", 80);
    // 禁用Nagle算法
    socket.setTcpNoDelay(true);
 
    // 以下是使用socket进行数据传输的代码
} catch (IOException e) {
    e.printStackTrace();
}
```

---

在这个示例中，通过调用`socket.setTcpNoDelay(true);`，我们告诉TCP不要等待足够多的数据累积，而是立即发送每个包。这在某些实时应用中非常有用，比如游戏、VoIP（语音通信）或其他需要低延迟的场景。

请注意，虽然禁用Nagle算法可以减少延迟，但在某些情况下可能会增加网络拥塞，因为网络上会有更多的小包。因此，在决定是否禁用Nagle算法时，需要根据应用的具体需求和网络环境来权衡利弊。