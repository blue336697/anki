# RabbitMQ | 环境部署|交换机类型|消费幂等性

type: Post
status: Published
date: 2022/07/05
summary: 发布确认就是在持久化过程中将信息存放在本地磁盘中以后才进行的操作，队列成功存放到磁盘以后将这个确认消息回传给生产者，生产者收到确认消息这个过程称为发布确认
tags: MQ
category: 中间件

## 发布确认

### 1.概述

- 将传输过程中丢失消息以后的风险降到最低的步骤拢共分三步
    
    > 将消息队列持久化将队列中的消息持久化发布确认
    > 
- 发布确认

> 发布确认就是在持久化过程中将信息存放在本地磁盘中以后才进行的操作，**队列成功存放到磁盘以后将这个确认消息回传给生产者，生产者收到确认消息这个过程称为发布确认**
> 

### 2.springboot集成发布确认机制

### 2.0 配置文件中的各项参数

```yaml
rabbitmq:
    host: 47.101.139.122
    port: 5672
    #用户名和密码 默认都是guest
    username: guest
    password: guest
    #虚拟主机
    virtual-host: /
    listener:
      simple:
        #消费者的最小数量
        concurrency: 10
        #消费者的最大数量
        max-concurrency: 10
        #限制消费者每次只能处理一条消息，处理完在处理下一条
        prefetch: 1
        #启动时是否默认启动容器，默认为true
        auto-startup: true
        #被拒绝时重新进入队列
        default-requeue-rejected: true
    template:
      retry:
        #发布重试，默认为false
        enabled: true
        #重试时间，默认为1000ms
        initial-interval: 1000ms
        #重试最大次数，默认为三次
        max-attempts: 3
        #重试最大间隔时间，默认为10000ms
        max-interval: 10000ms
        #重试间隔时间，例如 2.0 第一次为10s、第二次为20s、第三次为40s
        multiplier: 1
```

- 前提配置springboot的配置文件信息

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image.png)

- 图示

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%201.png)

### 2.1 代码

- 前言

> 这里的代码有些是后面备份交换机内容所新加的代码
> 
- 架构图

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%202.png)

- 生产者代码

```java
/**
 * 发布确认的生产者
 */
@Slf4j
@RestController
@RequestMapping("/confirm")
public class ConfirmProducer {

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @GetMapping("/sendMessage/{message}")
    public void sendMessage(@PathVariable String message){
        //接收回调信息
        CorrelationData correlationData01 = new CorrelationData("1");
        rabbitTemplate.convertAndSend(ConfirmConfig.EXCHANGE_NAME,
                ConfirmConfig.routingKey,message+ConfirmConfig.routingKey,correlationData01);

        log.info("发送消息内容为：{}"+message+ConfirmConfig.routingKey);

        CorrelationData correlationData02 = new CorrelationData("2");
        rabbitTemplate.convertAndSend(ConfirmConfig.EXCHANGE_NAME,
                ConfirmConfig.routingKey+2,message+ConfirmConfig.routingKey,correlationData02);
		//这里我们故意将发送的第二条消息的routingkey写错，让他被处理
        log.info("发送消息内容为：{}"+message+ConfirmConfig.routingKey+2);
    }
}
```

- 消费者代码

```java
/**
 * 消费者
 */
@Slf4j
@Component
public class ConfirmConsumer {
    @RabbitListener(queues = ConfirmConfig.QUEUE_NAME)
    public void receiveConfirmMsg(Message message){
        String msg = new String(message.getBody());
        log.info("接收到的队列confirm.queue消息：{}",msg);
    }
}
```

- 交换机、队列绑定配置类

```java
/**
 * springboot继承发布确认机制的配置类
 */
@Configuration
public class ConfirmConfig {
    public static final String EXCHANGE_NAME = "confirm.exchange";

    public static final String QUEUE_NAME = "confirm.queue";

    public static final String routingKey = "key1";

    //备份交换机（当交换机宕机了还可以启动备份交换机）
    public static final String BACKUP_EXCHANGE_NAME ="backup.exchange";
    //备份队列
    public static final String BACKUP_QUEUE_NAME = "backup.queue";
    //报警队列，将错误的信息保存下来
    public static final String WARNING_QUEUE_NAME = "warning.queue";

    @Bean
    public DirectExchange confirmExchange(){
        //得让主交换机转发一份消息到备份交换机
        Map<String, Object> arguments = new HashMap<>();
        arguments.put("alternate-exchange","备份交换机");
        return new DirectExchange(EXCHANGE_NAME,true,false,arguments);
        //当然这里也能用Builder工具类来创建队列
    }

    @Bean
    public FanoutExchange backupExchange(){
        return new FanoutExchange(BACKUP_EXCHANGE_NAME,true,false);
    }

    @Bean
    public Queue confirmQueue(){
        return new Queue(QUEUE_NAME,true);
    }

    @Bean
    public Queue backupQueue(){
        return new Queue(BACKUP_QUEUE_NAME,true);
    }

    @Bean
    public Queue warningQueue(){
        return new Queue(WARNING_QUEUE_NAME,true);
    }

    @Bean
    public Binding backupExchangeToBackupQueue(@Qualifier("backupExchange") FanoutExchange backupExchange,
                                         @Qualifier("backupQueue") Queue backupQueue
                                         ){
        return BindingBuilder.bind(backupQueue).to(backupExchange);
    }

    @Bean
    public Binding backupExchangeToWarningQueue(@Qualifier("backupExchange") FanoutExchange backupExchange,
                                               @Qualifier("warningQueue") Queue warningQueue
                                               ){
        return BindingBuilder.bind(warningQueue).to(backupExchange);
    }

    @Bean
    public Binding confirmExchangeToQueue(@Qualifier("confirmExchange") DirectExchange confirmExchange,
                                          @Qualifier("confirmQueue") Queue confirmQueue){
        return BindingBuilder.bind(confirmQueue).to(confirmExchange).with(routingKey);
    }
}
```

### 2.2 Mandatory参数

> **这个参数是为了解决消息在通过routingkey路由过程中时**，队列突然挂了，但又无法回传给生产者任何回馈消息，将无法到达的消息回馈给生产者，让交换机将消息重新发送至给队列
> 
- 设置

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%203.png)

### 2.3 备份交换机

有些类复用了2.1的代码，可回去查看与图中对比，这里提供不能复用只能重新写的类

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%204.png)

- 无论是队列挂掉还是交换机挂掉，对应的配置类

```java
/**
 * 此配置类就是发布确认的关键，能够给我们回传发送成功还是失败的结果
 */
@Component
@Slf4j
public class MyCallBackConfig implements RabbitTemplate.ConfirmCallback,RabbitTemplate.ReturnsCallback {

    //由于是自己重写的RabbitTemplate的内部类，注意是内部类，当springboot注入容器时，是找不到我们自己实现的这个类，所以需要我们将此类注入到RabbitTemplate中
    @Autowired
    private RabbitTemplate rabbitTemplate;

    @PostConstruct  //将此方法注入到容器中
    public void init(){
        rabbitTemplate.setConfirmCallback(this);
        rabbitTemplate.setReturnsCallback(this);
    }

    /*
    * 交换机确认回调方法情况：
    * 1.发消息 交换机接收到了 回调
    *       - correlationData   保存了回调消息的ID即相关消息
    *       - ack   交换机收到消息返回true
    *       - cause 失败的原因，如果成功返回null
    *
    * 2.发消息 交换机接收失败
    *       - correlationData   保存了回调消息的ID即相关消息
    *       - ack   返回false
    *       - cause 返回失败的原因
    * */
    //这个是解决交换机挂掉的
    @Override
    public void confirm(CorrelationData correlationData, boolean ack, String cause) {
        String id = correlationData!=null?correlationData.getId():"";
        if(ack){
            log.info("交换机已经收到id为{}的消息",id);
        }else {
            log.info("消息发送失败，原因是：{}"+cause);
        }
    }

    //这个是解决队列挂了，路由失败后的退回消息，成功是不会触发的
    //新版本的rabbitmq对给该方法进行了又一层的封装
    @Override
    public void returnedMessage(ReturnedMessage returned) {
        log.error("消息{}，被交换机{}退回，退回原因：{}，路由key：{}",
                new String(returned.getMessage().getBody()),
                returned.getExchange(),
                returned.getReplyText(),
                returned.getRoutingKey());
    }
}
```

- 报警消费者

```java
/**
 * 报警消费者
 */
@Slf4j
@Component
public class WarningConsumer {
    //接收消息
    @RabbitListener(queues = ConfirmConfig.WARNING_QUEUE_NAME)
    public void receiveWarningMsg(Message message){
        String msg = new String(message.getBody());
        log.error("发现不可路由消息：{}",msg);
    }
}
```

### 2.4 总结

> 当Mandatory参数和备份交换机同时开启，那么这条路由失败的消息是**退回给生产者**还是**经过备份交换机发送给警告队列最后由警告消费者接受呢**
> 

`答案是：备份交换机的优先级更加高一点`

## 四种交换机类型

### MQ的结构

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%205.png)

### 交换机类型

- ==Fanout==：广播，将消息交给所有绑定到交换机的队列
- ==Direct==：定向，把消息交给符合指定routingKey（就是传输信道的一个标志）的队列
- ==Topic==：通配符，把消息交给符合routing pattern（路由模式） 的队列
- ==Header==：header模式与routing不同的地方在于，header模式取消routingkey，使用header中的 key/value（键值对）匹配队列。

### 1.发布订阅（Fanout）模式

### 1.1 概述

> 就是微信公众号会向所有关注的人推送新的消息，这种关系就是交换机与队列的绑定关系，但是这种模式不受路由键`（routingkey）`的约束
> 

### 2.Direct模式

### 1.1 概述

> 交换机通过消息携带的路由键识别与之绑定的某个队列并发送，这也是我们未指定交换机时，rabbitmq使用的默认交换机类型，一个路由键都匹配不到默认会丢弃这条消息
> 

### 3.Topic模式

### 3.1 Topic交换机

只要它的routingKey符合以下规则（通配符），就会去相应队列，单

**条消息只能在不同信道指向同一队列中出现一次**

，一个路由键都匹配不到默认会丢弃这条消息

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%206.png)

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%207.png)

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%208.png)

### 3.2 死信/死信队列/死信交换机

- 概述

> 先从概念解释上搞清楚这个定义，死信，顾名思义就是无法被消费的消息，字面意思可以这样理解，一般来说，producer将消息投递到broker或者直接到queue里了，consumer 从 queue取出消息进行消费，但某些时候由于特定的原因导致queue中的某些消息无法被消费，这样的消息如果没有后续的处理，就变成了死信，有死信自然就有了死信队列。这些死信会进入死信交换机（路由）
> 
- 产生原因

> 消息TTL（存活时间 time to live）过期队列达到最大长度(队列满了，无法再添加数据到mq.中)消息被拒绝(basic.reject或basic.nack)并且requeue=false.
> 

> **注意；成为死信肯定要先经过普通队列然后再去死信队列**，所以要实现队列之间的转发
> 
- 应用

> 为了保证订单业务的消息数据不丢失，需要使用到RabbitMQ的死信队列机制，当消息消费发生异常时，将消息投入死信队列中.还有比如说:用户在商城下单成功并点击去支付后在指定时间未支付时自动失效
> 

### 3.3 延迟队列（死信队列的一种）

- 概述

> 造成死信的三种原因里面有**消息TTL（存活时间 time to live）过期**，通过这种原因成为死信进入死信队列的队列称为**延迟队列**
> 
- 引用场景

> 订单在十分钟之内未支付则自动取消新创建的店铺，如果在十天内都没有上传过商品，则自动发送消息提醒。用户注册成功后，如果三天内没有登陆则进行短信提醒。用户发起退款，如果三天内没有得到处理则通知相关运营人员。预定会议后，需要在预定的时间点前十分钟通知各个与会人员参加会议
> 

### 3.3.1 SpringBoot整合代码案例一

- 不足

> 此队列有一个缺点就是拓展性太差，如果我们还需要别的延迟时间需求就只能在写一个队列来满足，那如果我们需要100个呢，所以案例二将引入一个动态代理队列，来满足我们的任何需求
> 

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%209.png)

- 队列、交换机创建和绑定类

```java
/**
 * 整合springboot的延迟队列实现
 *      配置文件类，相关交换机队列之间的联系都在这完成
 */
@Configuration
public class TTLQueueConfig {
    //普通交换机
    public static final String NORMAL_EXCHANGE = "X";
    //死信交换机
    public static final String DEAD_EXCHANGE = "Y";
    //普通队列
    public static final String NORMAL_QUEUE01 = "QA";
    public static final String NORMAL_QUEUE02 = "QB";
    //死信队列
    public static final String DEAD_QUEUE = "QD";

    //创建普通交换机
    @Bean("normalExchange")
    public DirectExchange normalExchange(){
        return new DirectExchange(NORMAL_EXCHANGE);
    }

    //创建死信交换机
    @Bean("deadExchange")
    public DirectExchange deadExchange(){
        return new DirectExchange(DEAD_EXCHANGE);
    }

    //创建普通队列
    @Bean("normalQueue01")
    public Queue normalQueue01(){
        //指定map的长度以此来节约时间
        Map<String, Object> map = new HashMap<>(3);
        //设置死信交换机
        map.put("x-dead-letter-exchange",DEAD_EXCHANGE);
        //设置死信routingKey
        map.put("x-dead-letter-routing-key", "YD");
        //设置等待时间,这个队列为等待10s的，单位为ms
        map.put("x-message-ttl",10000);

        return QueueBuilder.durable(NORMAL_QUEUE01).withArguments(map).build();

    }

    @Bean("normalQueue02")
    public Queue normalQueue02(){
        //指定map的长度以此来节约时间
        Map<String, Object> map = new HashMap<>(3);
        //设置死信交换机
        map.put("x-dead-letter-exchange",DEAD_EXCHANGE);
        //设置死信routingKey
        map.put("x-dead-letter-routing-key", "YD");
        //设置等待时间,这个队列为等待10s的，单位为ms
        map.put("x-message-ttl",40000);

        return QueueBuilder.durable(NORMAL_QUEUE02).withArguments(map).build();
    }

    //创建死信队列
    @Bean("deadQueue")
    public Queue deadQueue(){
        return QueueBuilder.durable(DEAD_QUEUE).build();
    }

    //绑定关系

    @Bean
    public Binding NE_NQ1(@Qualifier("normalQueue01") Queue normalQueue01,
                          @Qualifier("normalExchange") DirectExchange normalExchange){
        //普通交换机绑定普通队列一
        return BindingBuilder.bind(normalQueue01).to(normalExchange).with("XA");
    }

    @Bean
    public Binding NE_NQ2(@Qualifier("normalQueue02") Queue normalQueue02,
                          @Qualifier("normalExchange") DirectExchange normalExchange){
        //普通交换机绑定普通队列二
        return BindingBuilder.bind(normalQueue02).to(normalExchange).with("XB");
    }

    @Bean
    public Binding DE_DQ(@Qualifier("deadQueue") Queue deadQueue,
                          @Qualifier("deadExchange") DirectExchange deadExchange){
        //死信交换机绑定死信队列
        return BindingBuilder.bind(deadQueue).to(deadExchange).with("YD");
    }
}
```

- 生产者类

```java
/**
 * 生产者发送消息
 */
@Slf4j
@RestController
@RequestMapping("/ttl")
public class ProducerController {

    //使用spring提供的发送类来发送
    @Autowired
    private RabbitTemplate rabbitTemplate;

    @GetMapping("/sendMsg/{message}")
    public void sendMsg(@PathVariable String message){
        //大括号在这里是占位符
        log.info("当前时间：{}，发送一条消息给两个TTL队列：{}", new Date().toString(),
                message);

        rabbitTemplate.convertAndSend("X","XA","消息来自TTL为10s"+message);

        rabbitTemplate.convertAndSend("X","XB","消息来自TTL为40s"+message);

    }
}
```

- 消费者（监听器）

```java
/**
 * 消费者本质上就是一个监听器
 */
@Slf4j
@Component
public class ConsumerListener {
    //接收来自QD队列的消息
    @RabbitListener(queues = "QD")
    public void receiveMsg(Message message, Channel channel) throws Exception{
        String msg = new String(message.getBody());
        log.info("当前时间：{}，收到死信队列的消息：{}",new Date().toString(),msg);

    }
}
```

- springboot所需的依赖jar包

```xml
<dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

        <!--rabbitmq依赖-->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-amqp</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>fastjson</artifactId>
            <version>1.2.47</version>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
        </dependency>

        <!--图形化界面测试-->
        <dependency>
            <groupId>io.springfox</groupId>
            <artifactId>springfox-swagger2</artifactId>
            <version>2.9.2</version>
        </dependency>

        <dependency>
            <groupId>io.springfox</groupId>
            <artifactId>springfox-swagger-ui</artifactId>
            <version>2.9.2</version>
        </dependency>

        <!--rabbitmq依赖组件-->
        <dependency>
            <groupId>org.springframework.amqp</groupId>
            <artifactId>spring-rabbit-test</artifactId>
            <scope>test</scope>
        </dependency>

    </dependencies>
```

### 3.3.2 SpringBoot整合代码案例二

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2010.png)

- 代码

> 提示我们只需要在原来的队列交换机绑定类改变一些代码然后再生产者那边重新写一个对应控制器方法
> 

```java
//创建普通队列
    public static final String NORMAL_QUEUE03 = "QC";
//创建一个新的普通队列，具有动态代理性
    @Bean("normalQueue03")
    public Queue normalQueue03(){
        //指定map的长度以此来节约时间
        Map<String, Object> map = new HashMap<>(3);
        //设置死信交换机
        map.put("x-dead-letter-exchange",DEAD_EXCHANGE);
        //设置死信routingKey
        map.put("x-dead-letter-routing-key", "YD");

        return QueueBuilder.durable(NORMAL_QUEUE03).withArguments(map).build();

    }
	@Bean
    public Binding NE_NQ3(@Qualifier("normalQueue03") Queue normalQueue03,
                          @Qualifier("normalExchange") DirectExchange normalExchange){
        //普通交换机绑定普通队列二
        return BindingBuilder.bind(normalQueue03).to(normalExchange).with("XC");
    }

//设置一个能发送自定义TTL时间的生产者
    @GetMapping("/sendTTL/{message}/{ttlTime}")
    public void sendMsg(@PathVariable String message,
                        @PathVariable String ttlTime){
        //大括号在这里是占位符
        log.info("当前时间：{}，发送一条时长{}毫秒TTL信息给队列QC：{}", new Date().toString(),
                ttlTime,
                message);

        rabbitTemplate.convertAndSend("X","XC","消息来自TTL为10s"+message, msg->{
            //设置发送消息时候的 延迟时长
            msg.getMessageProperties().setExpiration(ttlTime);
            return msg;
        });
    }
```

- 结果

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2011.png)

- 总结

> 可以看到结果是不如意的，我们理想的状态就是2s的队列会在发出时间的两秒后收到，但由于我们先发的20s的队列信息，这样就会造成长时间的堵塞短时间的，队列并不会检测第二条消息，解决办法就是直接用官方的延时队列实现的插件
> 

### 3.4.3 SpringBoot整合代码案例三

- 延迟队列插件在docker安装的教程
[安装教程](https://www.cnblogs.com/geekdc/p/13549613.html)

> 在这里求助一下个位大佬，就是我怎么看docker里面各种容器的版本号，这个rabbitmq的版本号我找了半天最后去图形化后台界面找到了，烦得要死
> 
- 安装完成后

> 你在控制台创建一个新的交换机时就会有新的选项，但注意在创建交换机时需要选择自定义交换机类型
> 

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2012.png)

- 图示

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2013.png)

- 代码

> 配置类
> 

```java
/**
 * 关于rabbitmq官方依赖的延迟队列插件的配置类
 */
@Configuration
public class DelayedQueueConfig {
    //交换机
    public static final String EXCHANGE_NAME = "delayed_exchange";
    //队列
    public static final String QUEUE_NAME = "delayed_queue";
    //routingKey
    public static final String ROUTING_KEY = "delayed_routingKey";

    //声明交换机
    /*
    * CustomExchange(
    * String name：交换机的名字
    * String type：交换机的类型
    * boolean durable：是否要持久化
    * boolean autoDelete：是否要自动删除
    * Map<String, Object> arguments：其他参数
    * )
    * */
    @Bean
    public CustomExchange delayedExchange(){
        Map<String, Object> arguments = new HashMap<>();
        //设置交换机的延迟类型：direct，因为ROUTING_KEY是一个固定的值，我们不需路由给别的队列
        arguments.put("x-delayed-type", "direct");
        return new CustomExchange(EXCHANGE_NAME,"x-delayed-message",
                true, false, arguments);
    }

    //声明队列
    @Bean
    public Queue delayedQueue(){
        return new Queue(QUEUE_NAME,true);
    }

    //绑定交换机和队列
    //noargs()构建方法
    @Bean
    public Binding delayedExchangeToQueue(@Qualifier("delayedExchange")CustomExchange delayedExchange,
                                          @Qualifier("delayedQueue") Queue delayedQueue){
        return BindingBuilder.bind(delayedQueue).to(delayedExchange).with(ROUTING_KEY).noargs();

    }
}
```

> 生产者控制器
> 

```java
//基于rabbitmq的延迟队列插件进行构建的生产者
    @GetMapping("/sendDelayMsg/{message}/{delayTime}")
    public void sendMsg(@PathVariable String message,
                        @PathVariable Integer delayTime){
        log.info("当前时间：{}，发送一条时长{}毫秒信息给延迟队列delayed.queue：{}",
                new Date().toString(),
                delayTime,
                message);

        rabbitTemplate.convertAndSend("delayed_exchange","delayed_routingKey","消息来自延迟队列"+message, msg->{
            //设置发送消息时候的 延迟时长 单位为ms
            msg.getMessageProperties().setDelay(delayTime);
            return msg;
        });
    }
```

> 消费者监听器类
> 

```java
/**
 * 基于延迟队列插件实现的消费者，还是用监听的方式实现
 */
@Slf4j
@Component
public class DelayQueueConsumer {
    @RabbitListener(queues = DelayedQueueConfig.QUEUE_NAME)
    public void receiveDelayQueue(Message message){
        String msg = new String(message.getBody());
        log.info("当前时间：{}，收到的消息为：{}",new Date().toString(),msg);
    }

}
```

- 结果

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2014.png)

### 3.4 总结

> 延时队列在需要延时处理的场景下非常有用，使用RabbitMQ来实现延时队列可以很好的利用RabbitMQ的特性，如：**消息可靠发送、消息可靠投递、死信队列来保障消息至少被消费一次以及未被正确处理的消息不会被丢弃**。另外，**通过RabbitMQ集群的特性，可以很好的解决单点故障问题，不会因为单个节点挂掉导致延时队列不可用或者消息丢失。**
> 

> 当然，延时队列还有很多其它选择，比如利用Java的DelayQueue，利用Redis.的zset，利用Quartz或者利用kafka的时间轮，这些方式各有特点,看需要适用的场景
> 

### 4.Headers模式

### 4.1 概述

> 属于半抛弃状态，官网连入门案例都没有；书回正文，所谓headers模式就是不依赖路由键，发送消息会有一个对象，对象中有一个header属性（键值对）来匹配队列
> 

### 4.2 例子

```java
//绑定队列
@Bean
    public Binding binding01(){
        Map<String, Object> map = new HashMap<>();
        map.put("cqiLor" , "red");
        map.put("speed","low");
        return BindingBuilder.bind(queue01()).to(headersExchange()).whereAny(map).match();
    }

//发送
public void send05(Object msg) {
        log.info("发送消息(被两个queue接收):" + msg);
        MessageProperties properties = new MessageProperties();
        properties.setHeader("color" , "red");
        properties.setHeader( "speed" , "fast");
        rabbitTemplate.convertAndSend("headersExchange","",msg);
    }
//接收就要配合@RabbitListener注解指定队列名称即可
```

> 这些方法就是匹配参数，any就是两个参数中一个匹配上就算，all则是必须两个参数都匹配上
> 

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2015.png)

## 三、RabbitMq的其他知识点

### 1.幂等性（避免重复消费和少消费）以及可靠投递

### 1.1 概述

> 个人认为可以简单的理解为**事务管理**，即用户多次点击确认后（消息的重复提交）对于最后的结果是无影响的，或提交时网络异常等
> 
- 消息重复消费的三种场景

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2016.png)

### 1.2 解决思路

> • MQ消费者的幂等性的解决一般使用全局ID或者写个唯一标识比如时间戳或者UUID或者订单消费者消费MQ中的消息也可利用MQ的该id来判断，或者可按自己的规则生成一个全局唯一id，每次消费消息时用该id先判断该消息是否已消费过。
• 如果被消费过，但是消费业务本身失败了，这个情况是允许二次消费的；但是是因为其他情况有消费过的直接丢弃
> 

### 1.3 消费端的幂等性保障

> 在海量订单生成的业务高峰期，生产端有可能就会重复发生了消息，这时候消费端就要实现幂等性，这就意味着我们的消息永远不会被消费多次,即使我们收到了一样的消息。
> 

业界主流的幂等性有两种操作：

1. 唯一ID+指纹码机制
    
    > 指纹码：我们的一些规则或者时间戳加别的服务给到的唯一信息码，它并不一定是我们系统生成的，基本都是由我们的业务规则拼接而来，但是一定要保证唯一性，然后就利用查询语句进行判断这个id是否存在数据库中。
    **优势就是实现简单就一个拼接，然后查询判断是否重复;劣势就是在高并发时**，如果是单个数据库就会有写入性能瓶颈当然也可以采用分库分表提升性能，**但也不是我们最推荐的方式**。
    > 
2. Redis原子性
    
    > 利用redis.执行setnx.命令，天然具有幂等性。从而实现不重复消费
    > 

### 2.优先级队列

### 2.1 概述及应用场景

- 概述

> 在订单量大的情况下，当多个用户下单但未支付时，催付订单的短信就可以发送给用户，但注意此时应该要做到区分**大用户与小用户**，即多个订单应该有不用的优先级，利润高的先发送，低的则后发送
> 
- 解决方式

> 以前后端系统是使用redis，来存放的定时轮询，而redis只能用List做一个简简单单的消息队列，并不能实现一个优先级的场景，**所以订单量大了后采用RabbitMQ进行改造和优化,如果发现是大客户的订单给一个相对比较高的优先级，否则就是默认优先级。**
> 
- 实现方式

> 每个用户的订单消息，**进入队列后会在队列设置的最大优先级范围内（0~255，最高能设置到255）被赋值一个优先级**，然后根据优先级出队
> 

### 2.2 优先级队列的代码实现

- 生产者

```java
/**
 * 优先级队列生产者
 */
public class Producer {
    public static final String QUEUE_NAME = "hello";

    //发消息
    public static void main(String[] args) throws Exception {
        Channel channel = RabbitMqUtils.getChannel();

        //生成一个队列
        Map<String, Object> arguments = new HashMap<>();
        //设置队列最大优先级范围。官方的允许的范围是0~255
        arguments.put("x-max-priority",10);
        channel.queueDeclare(QUEUE_NAME, true, false,false, arguments);

        //发消息，需要发大量消息，你一条一条发有时间差，他就遵循先进先出原则，所以体现不出来优先级
        for (int i = 0; i < 10; i++) {
            String message = "hello world"+i;
            if (i==5){
                AMQP.BasicProperties properties = new AMQP.BasicProperties().builder().
                        priority(5).build();
                channel.basicPublish("", QUEUE_NAME, properties, message.getBytes(StandardCharsets.UTF_8));
            }else {
                channel.basicPublish("", QUEUE_NAME, null, message.getBytes(StandardCharsets.UTF_8));
            }
        }

        //通过信道进行发消息

        System.out.println("消息发送完成");
    }
}
```

- 结果

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2017.png)

### 3.惰性队列

### 3.1 概述即应用场景

- 概述

> 队列有两种模式：`default`和`lazy`模式，**正常情况下消息是存放在mq的内容中，如果队列是惰性队列消息是保存在磁盘上的，这样每次消息的传输都要到本地去读取效率自然就慢**
> 
- 应用场景

> 就是在订单量十分大的情况下且消费者异常或宕机的时候，这样队列就能派上用处，**可以节约mq中的内存使用**，在发送1百万条消息，每条消息大概占1KB的情况下，普通队列占用内存是1.2GB，而惰性队列仅仅占用1.5MB
> 

### 3.2 设置

在队列声明的时候可以通过"×-queue-mode"参数来设置队列的模式，取值为"default"和"lazy"

```java
Map<String, Object> args = new HashMap<String,Object>();
args.put("x-queue-mode" , "lazy");
channel.queueDeclare("myqueue" , false, false, false, args);
```

### 4.rabbitmq的集群搭建

### 5.镜像队列

### 5.1 概述

- 说明

> 书接上文集群搭建好后，**有一个问题就是三个结点都是复用一条队列的，当父结点挂了以后，后面两个结点随之失去功能**
> 
- 概述

> 引入镜像队列(Mirror Queue)的机制，可以将队列镜像到集群中的其他Broker 节点之上，如果集群中的一个节点失效了，队列能自动地切换到镜像中的另一个节点上以保证服务的可用性。
> 

### 6.实现负载均衡

### 6.1 概述

- 说明

> 前面我将连接rabbitmq的ip及各种参数写死，那么在多结点的前提下，如果父结点挂了，而生产者还在连接父结点，他并不知晓有其他两个结点导致服务终止
> 
- 解决方式

> **这时我们就可以引入Nginx、Haproxy、LVS等代理服务器来解决此问题，实现高可用的负载均衡**
> 

### 7.Federation Exchange（联邦交换机）

### 7.1 概述

- 使用原因

> **当两个距离很远的地方为了解决延迟问题肯定都有自己的地方rabbitmq，那么这两个rabbitmq怎么保持数据的同步呢**，这时就能用到联邦交换机
> 

### 8.Shovel

### 8.1 概述

> 与Federation（联邦交换机）具备的数据转发功能类似，Shovel够可靠、持续地从一个 Broker中的队列(作为源端即source)拉取数据并转发至另一个Broker中的交换器(作为目的端，即destination)。作为源端的队列和作为目的端的交换器可以同时位于同一个Broker，也可以位于不同的Broker上。Shovel 可以翻译为"铲子"，是一种比较形象的比喻，这个"铲子"可以将消息从一方"铲子"另一方。Shovel行为就像优秀的客户端应用程序能够负责连接源和目的地、负责消息的读写及负责连接失败问题的处理。
> 

### 9.MQ的三大用处

- MQ主要有三大用法

==异步传输==

> 对于异步控制来说，就是你发送请求后不比关注如何处理，直接返回；就拿下面的例子来说明**我们可以当下单成功后，只需要将订单消息发给MQ，然后立即将结果返回通知客户。这才是正确的打开姿势。这样一来，我订单系统只需要告诉你MQ，我下单成功了，其他模块收到消息后，该发短信的发短信，发邮件的发邮件。因为本来MQ的性能就很好，所以这个效率一下就提升了。**
> 

==应用解耦==

> 对于应用解耦来说，就是将服务之间的调用进行解耦，例如12306买票。需要做以下几件事：调用库存系统扣减车票库存，调用短信系统给用户发送短信，调用邮件系统给用户发邮件，调用第三方客户端通知买票成功。
> 
- 问题
1. 如果此时添加新的服务例如添加通知微信小程序的通知这怎么办，必须修改代码
2. 如果某天短信系统挂了，后面的系统会全部失效，因为订单消息就停在短信这里了

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2018.png)

- 解决

> 那么我们发现其实短信系统、邮件系统等都只依赖订单系统产生的一条数据那就是订单，因此我们在订单系统产生数据后，将订单这条数据发送给MQ，就返回成功，然后让短信、邮件等系统都订阅MQ，一旦发现MQ有消息，他们主动拉取消息，然后解析，进行业务处理。这样一来，就算你短信系统挂了，丝毫不会影响其他系统，而且如果后来想加一个新的系统，你也不用改订单系统的代码了，你只要订阅我们的MQ提供的消息就行了。
> 

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2019.png)

==流量控制==

> 这个就很简单了，将请求全部加入队列，消费者处理一个，在处理下一个，不存在一下子的流量涌入
> 

### 10.如何保证消息可靠性

==消息队列-消息可靠投递==：

- 生产者可靠传输两步走

> 生产者发送消息到对应交换机（broker服务器）成功到达，会调用回调方confirmCallback确认模式交换机发送消息到相应队列，成功则回调returnCallback 未投递到queue退回模式
> 
- 消费者可靠传输一步走

> 消费者会发送给队列ACK，这个ACK有自动（默认）或者手动，自动会将所有信息自动进行应答，并别删除队列消息，这样的话如果我们消费者对于消息的处理过程中突然宕机，没有处理的消息全部都没有了，所以我们手动处理一条确认一条
> 

### 1.消息队列把消息弄丢了怎么解决

### 1.1 生产者弄丢消息

- 图示

> 对于此会有一下解决方式
> 
> 1. 事务消息：发送消息之前先开启事务，在发送；如果消息代理没有收到消息会发送异常消息并回滚事务，**可靠但效率低**
> 2. confirm确认模式：即上面介绍的可靠投递，因为是异步的所以用的很多
> 3. 做好容错方法：重试机制、日志记录、定期重发（建立消息表，扫描未成功的消息）

![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2020.png)

### 1.2 MQ 在存储期间弄丢消息

- 概述

> 消息代理在成功收到消息后会把消息存储起来等待消费者来消费，在此期间造成的丢失一般都是MQ故障导致的，所以我们需要开启持久化（必须分别开启队列与消息的持久化）并开启publisher的确认回调（这样我们就知道消息的具体状态了）；或者建立MQ集群
> 

### 1.3 消费者弄丢消息

- 概述

> 如下图，如果在消费123的过程中突然宕机的话，对于消费端这条消息是丢失的，这也是我们前面讲到的，
> 
> 
> **对于MQ来说默认是自动应答，就是送到了就是回传ACK了，那么改为手动应答即消费完消息，处理完消息再回传ACK**
> 
> ![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2021.png)
> 
> ![image.png](RabbitMQ%20%E7%8E%AF%E5%A2%83%E9%83%A8%E7%BD%B2%20%E4%BA%A4%E6%8D%A2%E6%9C%BA%E7%B1%BB%E5%9E%8B%20%E6%B6%88%E8%B4%B9%E5%B9%82%E7%AD%89%E6%80%A7/image%2022.png)
> 

### 2.消息重复消费——看前面的幂等性

### 3.消费积压

- 出现原因

> • 消费者宕机积压
• 消费者消费能力不足积压
• 发送者发送流量太大
> 
- 解决

> 上线更多的消费者，进行正常消费
上线专门的队列消费服务，将消息先批量取出来，记录数据库，离线慢慢处理
> 

### x.关于使用docker搭建多结点高可用的负载均衡环境的教程

使用HAProxy：[HAProxy](https://www.cnblogs.com/sgh1023/p/11296013.html)
使用Nginx：[Nginx](https://blog.csdn.net/belonghuang157405/article/details/83540148)