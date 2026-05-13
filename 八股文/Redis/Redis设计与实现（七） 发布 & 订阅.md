# Redis设计与实现（七）| 发布 & 订阅

type: Post
status: Published
date: 2022/07/02
summary: Redis的发布与订阅功能由PUBLISH、SUBSCRIBE、PSUBSCRIBE等命令组成。
tags: Redis
category: 缓存

# 发布与订阅

- 概述

> Redis的发布与订阅功能由PUBLISH、SUBSCRIBE、PSUBSCRIBE等命令组成。
通过执行SUBSCRIBE命令，客户端可以订阅一个或多个频道，从而成为这些频道的订阅者( subscriber ):每当有其他客户端向被订阅的频道发送消息 （message)时，频道的所有订阅者都会收到这条消息。
> 
- 命令使用

```sql
# 如果三个客户端都执行了这个，那么三个客户端都是这个频道的订阅者
SUBSCRIBE "news.it"
# 某个客户端发送这个，那么三个订阅者都会收到
PUBLISH "news.it" "hello"

```

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/24e94fce0890f352c340a13ed0917006.png)

- PSUBSCRIBE

> 这个命令可以让客户端订阅一个模式或多个模式，假设如下图A订阅it，B订阅et，C、D订阅一个ie模式，那么向it频道发送消息，C、D也会收到，
通配符中?表示一个占位符，*表示任意个占位符（包括0个），?*表示一个以上占位符
> 

```sql
# PSUBSCRIBE可以订阅一个或多个模式，类似于通配符
PSUBSCRIBE "news.?t"

```

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/4c6125dfc15574620611ed7296b6d581.png)

## 1.频道的订阅和退订

- 概述

> 订阅同一频道的客户端会在
> 
> 
> ```
> redisServer
> ```
> 
> ```
> pubsub_channels
> ```
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/dc75d1a2682d2f1cfdef4d4c9943d9c2.png)
> 

### 1.1 订阅频道

- 加入字典，会遍历输入的所有频道

> 加入频道的对应键，如果不存在该频道，那么必然不存在键，所以会先在字典中添加键如果存在频道，那么直接加入队尾
> 

### 1.2 退订

- 概述

> 这个动作就是刚才订阅动作的逆序
> 

```sql
UNSUBSCRIBE "频道1" "频道2"

```

## 2.模式的订阅和退订

- 概述

> 模式订阅和退订会在redisServer的pubsub_patterns属性中，同样也是一个链表，每个节点的结构为pubsubPattern
> 
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/989280e313423bbd1917eaaa98defe49.png)
> 
- 实例

> 
> 

### 2.1 订阅模式

- 步骤

> 新建一个pubsubPattern结构，将结构的pattern属性设置为被订阅的模式,client属性设置为订阅模式的客户端。将pubsubPattern结构添加到pubsub_patterns链表的表尾。
> 

### 2.2 退订

- 概述

> 模式的退订命令PUNSUBSCRIBE是 PSUBSCRIBE命令的反操作:当一个客户端退订某个或某些模式的时候，服务器将在pubsub_patterns链表中查找并删除那些pattern属性为被退订模式，并且client属性为执行退订命令的客户端的pubsubPattern结构。
> 

## 3.发送消息

- 概述

> 当一个Redis客户端执行PUBLISH <channel> <message>命令将消息message发送给频道channel的时候,服务器需要执行以下两个动作:
> 
> 1. 将消息message发送给channel频道的所有订阅者。
> 2. 如果有一个或多个模式pattern与频道channel相匹配，那么将消息message发送给pattern模式的订阅者。

## 4.查看订阅消息

- 概述

> PUBSUB命令是Redis 2.8新增加的命令之一，客户端可以通过这个命令来查看频道或者模式的相关信息，比如某个频道目前有多少订阅者，又或者某个模式目前有多少订阅者，诸如此类。
> 

### 4.1 PUBSUB CHANNELS

- 概述

> PUBSUB CHANNELS <pattern>，子命令用于返回服务器当前被订阅的频道，其中pattern是可选的
> 
> - 不给定模式，那么返回所有被订阅的频道
> - 给定模式，那么就符合模式的所有频道

### 4.2 PUBSUB NUMSUB

- 概述

> PUBSUB NUMSUB [channel-1 -2 ...-n]子命令，返回对应频道的订阅者数，底层就是通过遍历字典对应的频道名，对应的链表长度
> 

### 4.3 PUBSUB NUMPAT

- 概述

> PUBSUB NUMPAT子命令用于返回服务器当前被订阅模式的数量。这个子命令是通过返回pubsub patterns链表的长度来实现的，因为这个链表的长度就是服务器被订阅模式的数量，
>