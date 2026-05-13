# 深入理解Dubbo与实战（五·续）| Dubbo集群容错——负载均衡

type: Post
status: Published
date: 2022/08/17
summary: Dubbo集群容错——负载均衡
tags: Dubbo
category: 中间件

# Dubbo集群容错——负载均衡

## 1.负载均衡的实现

- 概述

> 在整个集群容错流程中，**①.首先经过Directory获取所有Invoker列表，②.然后经过Router根据路由规则过滤Invoker，③.最后幸存下来的Invoker还需要经过负载均衡这一关，选出最终要调用的 Invoker。**
> 

### 1.1 包装后的负载均衡

- 概述

> 前面一章我们介绍了七种容错策略，发现很多容错策略中都使用了负载均衡，都来自他们的抽象父类`Abstractclusterinvoker#select`方法中，**而并不是直接使用LoadBalance方法。因为抽象父类在LoadBalance的基础上又封装了一些新的特性**
> 
- 新特性

> 
> 
> 1. 粘滞连接：Dubbo中有一种特性叫粘滞连接，粘滞连接用于有状态服务，**尽可能让客户端总是向同一提供者发起调用**，除非该提供者“挂了”，再连接另一台。 粘滞连接将自动开启延迟连接，以减少长连接数。`<dubbo:protocol name=Hdubbo" sticky="true" />`
> 2. 可用检测：Dubbo调用的URL中，如果含有`cluster.availablecheck=false`，则不会检测远程服务是否可用，直接调用。如果不设置，则默认会开启检查，对所有的服务都做是否可用的检查，如果不可用，则再次做负载均衡。
> 3. 避免重复调用：对于已经调用过的远程服务，避免重复选择，每次都使用同一个节点。 这种特性主要是为了避免并发场景下，某个节点瞬间被大量请求。
- 负载均衡整个逻辑过程

> 从上述逻辑中，我们可以得知，框架会优先处理粘滞连接。否则会根据可用性检测或重复调用检测过滤一些节点，并在剩余的节点中做负载均衡。如果可用性检测或重复调用检测把节点都过滤了，**则兜底的策略是：在己经调用过的节点中通过负载均衡选择出一个可用的节点。**
> 
> 1. 检查URL中是否有配置粘滞连接，如果有则使用粘滞连接的Invoker。如果没有配置粘滞连接，或者重复调用检测不通过、可用检测不通过，则进入第2步。
> 2. 通过ExtensionLoader获取负载均衡的具体实现，并通过负载均衡做节点的选择。对选择出来的节点做重复调用、可用性检测，通过则直接返回，否则进入第3步。
> 3. 进行节点的重新选择。如果需要做可用性检测，则会遍历Directory中得到的所有节点，过滤不可用和已经调用过的节点，在剩余的节点中重新做负载均衡；如果不需要做可用性检测，那么也会遍历Directory中得到的所有节点，但只过滤已经调用过的，在剩余的节点中重新做负载均衡。这里存在一种情况，就是在过滤不可用或已经调用过的节点时，节点全部被过滤，没有剩下任何节点，此时进入第4步。
> 4. 遍历所有已经调用过的节点，选出所有可用的节点，再通过负载均衡选出一个节点并返回。如果还找不到可调用的节点，则返回null。

### 1.2 负载均衡的总体结构

- 概述

> Dubbo现在内置了 4种负载均衡算法，用户也可以自行扩展，因为LoadBalance接口上有@SPI注解。**从代码中我们可以知道默认的负载均衡实现就是RandomLoadBalance，即随机负载均衡。**
> 

```java
@SPI(RandomLoadBalance.NAME)
public interface LoadBalance {
     //我们在URL中可以通过loadbalance=xxx来动态指定select时的负载均衡算法
    @Adaptive("loadbalance")
    <T> Invoker<T> select(List<Invoker<T>> invokers, URL url, Invocation invocation) throws RpcException;
}
```

- 负载均衡算法

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image.png)

- 四种接口的类关系

> 4种负载均衡算法都继承自同一个抽象类，使用的也是模板模式，抽象父类中己经把通用的逻辑完成，留了一个抽象的doSelect方法给子类实现。抽象父类AbstractLoadBalance有两个权重相关的方法：`calculateWarmupWeight和getWeight`。
> 
> - getWeight方法就是获取当前Invoker的权重，getWeight方法中会调用calculateWarmupWeigt
> - calculateWarmupWeight是计算具体的权重。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image%201.png)
> 
- `getWeight`方法

```java
int getWeight(Invoker<?> invoker, Invocation invocation) {
    int weight;
    URL url = invoker.getUrl();
    //多注册中心场景，多注册中心之间的负载均衡。
    if (REGISTRY_SERVICE_REFERENCE_PATH.equals(url.getServiceInterface())) {
        weight = url.getParameter(REGISTRY_KEY + "." + WEIGHT_KEY, DEFAULT_WEIGHT);
    } else {
    	//通过URL获取当前Invoker设置的权重
        weight = url.getMethodParameter(invocation.getMethodName(), WEIGHT_KEY, DEFAULT_WEIGHT);
        if (weight > 0) {
        	//获取启动的时间点
            long timestamp = invoker.getUrl().getParameter(TIMESTAMP_KEY, 0L);
            if (timestamp > 0L) {
            	//求差值，得到已经预热了多久
                long uptime = System.currentTimeMillis() - timestamp;
                if (uptime < 0) {
                    return 1;
                }
                //获取设置的总预热时间
                int warmup = invoker.getUrl().getParameter(WARMUP_KEY, DEFAULT_WARMUP);
                if (uptime > 0 && uptime < warmup) {
                	//计算出最后的权重
                    weight = calculateWarmupWeight((int)uptime, warmup, weight);
                }
            }
        }
    }
    return Math.max(weight, 0);
}
```

- calculateWarmupWeight的代码逻辑

> 由于框架考虑了服务刚启动的时候需要有一个预热的过程，如果一启动就给予100%的流量，则可能会让服务崩溃，因此实现了calculateWarmupWeight方法用于计算预热时候的权重。
计算逻辑是：**`(启动至今时间/给予的预热总时间)的平方X权重，总结果的向下取整`**。例如：**假设我们设置A服务的权重是5，让它预热10分钟，则第一分钟的时候，它的权重变为(1/10)^2^ X5 = 0.05，0.05/5 = 0.01，也就是只承担1%的流量；10分钟后，权重就变为(10/10)^2^ X5 = 5，也就是权重变为设置的100%,承担了所有的流量。**
> 

```java
static int calculateWarmupWeight(int uptime, int warmup, int weight) {
	int ww = (int) (Math.round(Math.pow((uptime / (double) warmup), 2) * weight));
    return ww < 1 ? 1 : (Math.min(ww, weight));
}
```

### 1.3 Random 负载均衡

- 计算步骤

> Random负载均衡是按照权重设置随机概率做负载均衡的。这种负载均衡算法并不能精确地平均请求，但是随着请求数量的增加，最终结果是大致平均的：
> 
> 1. 计算总权重并判断每个Invoker的权重是否一样。遍历整个Invoker列表，求和总权重。在遍历过程中，会对比每个Invoker的权重，判断所有Invoker的权重是否相同。
> 2. 如果权重相同，则说明每个Invoker的概率都一样，因此直接用nextlnt随机选一个Invoker返回即可。
> 3. 如果权重不同，则首先得到偏移值，然后根据偏移值找到对应的Invoker
- 权重不同根据偏移值得到`Invoker`代码

> 注意，在原版的weights数组中存放的是每个invoker的权重，但是新版中存放的是权重的前缀和，所以可以看到没有累减的步骤，直接根据随机到的值得到对应符合条件的invoker
> 

```java
if (totalWeight > 0 && !sameWeight) {
	//根据总权重计算出一个随机的偏移量，此处使用了ThreadLocalRandom 性能会更好
    int offset = ThreadLocalRandom.current().nextInt(totalWeight);
    //遍历所有的Invoker,得到被选中的Invoker
    for (int i = 0; i < length; i++) {
        if (offset < weights[i]) {
            return invokers.get(i);
        }
    }
}
```

- 例子

> 看源码可能还没理解原理，下面做一个场景假设：**假设有4个Invoker，它们的权重分别是1、2、3、4,则总权重是 1 +2+3+4=10。说明每个 Invoker 分别有 1/10、2/10、3/10、4/10 的概率会被选中。然后nextlnt(10)会返回0〜10之间的一个整数，假设为5。weights中为`[1,3,5,9]`，然后根据规则为会在`weight[3]`时满足条件进行返回，但是获取的invoker的索引为3就是第三个权重为3的invoker**
> 

### 1.4 RoundRobin 负载均衡

- 几种轮询的概述

> • 权重轮询负载均衡会根据设置的权重来判断轮询的比例。权重轮询又分为**普通权重轮询和平滑权重轮询**。普通权重轮询会造成某个节点会突然被频繁选中，这样很容易突然让一个节点流量暴增。Nginx中有一种叫平滑轮询的算法`(smooth weighted round-robinbalancing)`，**这种算法在轮询时会穿插选择其他节点，让整个服务器选择的过程比较均匀，不会“逮住”一个节点一直调用。Dubbo框架中最新的RoundRobin代码已经改为平滑权重轮询算法。**
• 普通轮询负载均衡的好处是每个节点获得的请求会很均匀，如果某些节点的负载能力明显较弱，则这个节点会堆积比较多的请求。因此普通的轮询还不能满足需求，还需要能根据节点权重进行干预。
> 
- 负载均衡的工作步骤

> 
> 
> 1. 初始化权重缓存Map。以每个Invoker的URL为key，对象WeightedRoundRobin为value生成一个 ConcurrentMap，并把这个 Map 保存到全局的 methodWeightMap 中：`ConcurrentMap <String, ConcurrentMap<String, WeightedRoundRobin>> methodWeightMap`。methodWeightMap的key是每个接口+方法名。这一步只会生成这个缓存Map，但里面是空的，第2步才会生成每个Invoker对应的键值。

```java
protected static class WeightedRoundRobin {
	//Invoker 设定的权重
	private int weight;
	//考虑到并发场景下某个Invoker会被同时选中，表示该节点被所有线程选中的权重总和
	//例如：某节点权重是100，被4个线程同时选中，则变为400
	private AtomicLong current = new AtomicLong(0);
	//最后一次更新的时间，用于后续缓存超时的判断
	private long lastUpdate;
	...
}
```

> 
> 
> 1. 遍历所有Invoker。首先，在遍历的过程中把每个Invoker的数据填充到第1步生成的权重缓存Map中。其次，获取每个Invoker的预热权重，新版的框架RoundRobin也支持预热， 通过和Random负载均衡中相同的方式获得预热阶段的权重。如果预热权重和Invoker设置的权重不相等，则说明还在预热阶段，此时会以预热权重为准。然后，进行平滑轮询。每个Invoker会把权重加到自己的current属性上，并更新当前Invoker的lastUpdate。同时累加每个Invoker的权重到totalweighto最终，遍历完后，选出所有Invoker中current最大的作为最终要调用的节点。
> 2. 清除已经没有使用的缓存节点。由于所有的Invoker的权重都会被封装成一个weightedRoundRobin对象，因此如果可调用的Invoker列表数量和缓存weightedRoundRobin对象的Map大小不相等，则说明缓存Map中有无用数据（有些Invoker己经不在了，但Map中还有缓存）。
> 3. 返回Invoker。注意，返回之前会把当前Invoker的current减去总权重。这是平滑权重轮询中重要的一步。

==为什么大小不相等就有老数据==

> **如果Invoker列表比缓存Map大，则说明有没被缓存的Invoker,此时缓存Map会新增数据。因此缓存Map永远大于等于Invoker列表。**
> 

> **清除老旧数据时，各线程会先用CAS抢占锁（抢到锁的线程才做清除操作，抢不到的线程就直接跳过，保证只有一个线程在做清除操作），然后复制原有的Map到一个新的Map中，根 据lastupdate清除新Map中的过期数据（默认60秒算过期），最后把Map从旧的Map引用修改到新的Map上面。这是一种CopyOnWrite的修改方式。**
> 
- 算法的具体工作逻辑

> 
> 
> 1. 每次请求做负载均衡时，会遍历所有可调用的节点（Invoker列表）。对于每个Invoker，让它的current = current + weight。属性含义见weightedRoundRobin对象。同时累加每个Invoker 的 weight 到 totalWeight，即 totalweight = totalweight + weight
> 2. 遍历完所有Invoker后，current值最大的节点就是本次要选择的节点。最后，把该节点的 current 值减去 totalWeight，即 current = current - totalweight
- 算法例子

> 假设有3个Invoker： A、B、C,它们的权重分别为1、6、9，初始current都是0，则平滑权重轮询过程如下表所示。
> 
> 
> **从这16次的负载均衡来看，我们可以清楚地得知，A刚好被调用了 1次，B刚好被调用了6次，C刚好被调用了 9次。符合权重轮询的策略，因为它们的权重比是1 ： 6 ： 9。此外，C并没有被频繁地一直调用，其中会穿插B和A的调用**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image%202.png)
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image%203.png)
> 

### 1.5 LeastActive 负载均衡

- 概述

> LeastActive负载均衡称为最少活跃调用数负载均衡，**即框架会记下每个Invoker的活跃数， 每次只从活跃数最少的Invoker里选一个节点**。这个负载均衡算法需要配合ActiveLimitFilter过滤器来计算每个接口方法的活跃数。最少活跃负载均衡可以看作Random负载均衡的`“加强版”`，因为最后根据权重做负载均衡的时候，使用的算法和Random的一样。
> 
- 代码分析

> 遍历所有Invoker，不断寻找最小的活跃数(leastActive)，如果有多个Invoker的活跃数都等于leastActive，则把它们保存到同一个集合中， 最后在这个Invoker集合中再通过随机的方式选出一个Invoker
> 

```java
......	//初始化各种计数器，如最小活跃数计数器、总权重计数器等
for (int i = 0; i < length; i++) {
    .....	//获得Invoker的活跃数、预热权重
    //第一次,或者发现有更小的活跃数
    if (leastActive == -1 || active < leastActive) {
    	//不管是第一次还是有更小的活跃数，之前的计数都要重新开始这里置空之前的计数。
    	//因为只计数最小的活跃数
        	....
    } else if (active == leastActive) {
        //当前Invoker的活跃数与计数相同说明有N个Invoker都是最小计数，全部保存到集合中
        //后续就在它们里面根据权重选一个节点
        ....
    }
}
//如果只有一个Invoker则直接返回
if (leastCount == 1) {
    return invokers.get(leastIndexes[0]);
}
//如果权重不一样，则使用和Random负载均衡一样的权重算法找到一个Invoker并返回
if (!sameWeight && totalWeight > 0) {
    ......
}
//如果权重相同，则直接随机选一个返回
return invokers.get(leastIndexes[ThreadLocalRandom.current().nextInt(leastCount)]);
```

- 如何获取最小活跃数

> 在ActiveLimitFilter中，只要进来一个请求，该方法的调用的计数就会原子性+1。整个Invoker调用过程会包在try-catch-finally中，无论调用结束或出现异常，finally中都会把计数原子-1。该原子计数就是最少活跃数。
> 

### 1.6 一致性Hash负载均衡

- 概述

> **一致性Hash负载均衡可以让参数相同的请求每次都路由到相同的机器上。这种负载均衡的方式可以让请求相对平均，相比直接使用Hash而言，当某些节点下线时，请求会平摊到其他服务提供者，不会引起剧烈变动。**
> 
- 普通一致性Hash算法

> **普通一致性Hash会把每个服务节点散列到环形上，然后把请求的客户端散列到环上，`顺时针`往前找到的第一个节点就是要调用的节点。假设客户端落在区域2，则顺时针找到的服务C就是要调用的节点。当服务C宕机下线，则落在区域2部分的客户端会自动迁移到服务D上。 这样就避免了全部重新散列的问题。**
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image%204.png)

- `Ketama` 一致性Hash源码分析

> 普通的一致性Hash也有一定的局限性，它的散列不一定均匀，容易造成某些节点压力大。 因此Dubbo框架使用了优化过的Ketama 一致性Hash。**这种算法会为每个真实节点再创建多个虚拟节点，让节点在环形上的分布更加均匀，后续的调用也会随之更加均匀。**
> 

==ConsistentHashLoadBalance#doSelect==

```java
@Override
protected <T> Invoker<T> doSelect(List<Invoker<T>> invokers, URL url, Invocation invocation) {
	//获得方法名
    String methodName = RpcUtils.getMethodName(invocation);
    //以接口名+方法名拼接出key
    String key = invokers.get(0).getUrl().getServiceKey() + "." + methodName;
    // 把所有可以调用的Invoker列表进行“Hash”
    int invokersHashCode = getCorrespondingHashCode(invokers);
    //现在Invoker列表的Hash码和之前的不一样，说明Invoker列表已经发生了变化，则重新创建Selector
    ConsistentHashSelector<T> selector = (ConsistentHashSelector<T>) selectors.get(key);
    if (selector == null || selector.identityHashCode != invokersHashCode) {
        selectors.put(key, new ConsistentHashSelector<T>(invokers, methodName, invokersHashCode));
        selector = (ConsistentHashSelector<T>) selectors.get(key);
    }
    //通过 selector 选出一个 Invoker
    return selector.select(invocation);
}
```

==细节之——ConsistentHashLoadBalance#ConsistentHashSelector==

> TreeMap实现一致性Hash：**在客户端调用时候，只要对请求的参数也做“MD5”即可。虽然此时得到的MD5值不一定能对应到TreeMap中的一个key，因为每次的请求参数不同。但是由于TreeMap是有序的树形结构，所以我们可以调用TreeMap的ceilingEntry方法，用于返回一个至少大于或等于当前给定key的Entry，从而达到顺时针往前找的效果。如果找不到，则使用firstEntry返回第一个节点。**
> 

```java
....//前面就是获取参数，获取hash环的节点
for (Invoker<T> invoker : invokers) {	//遍历所有的节点
	//得到每个节点的IP
   String address = invoker.getUrl().getAddress();
   //replicaNumber是生成的虚拟节点数,默认为160个
   for (int i = 0; i < replicaNumber / 4; i++) {
   		//以IP+递增数字做MD5,以此作为节点标识
       byte[] digest = Bytes.getMD5(address + i);
       for (int h = 0; h < 4; h++) {
       		//对标识做“Hash” 得到 TreeMap 的 key,以Invoker 为 value
           long m = hash(digest, h);
           virtualInvokers.put(m, invoker);
       }
   }
}
```

## 2.Merger的实现

- 概述

> 当一个接口有多种实现，消费者又需要同时引用不同的实现时，可以用group来区分不同的实现
> 

```xml
<dubbo:service group="groupl" interface="com.xxx.testService" />
<dubbo:service group="group2" interface="com.xxx.testservice" />
```

- 如何调用不同group的服务

> 如果我们需要并行调用不同group的服务，并且要把结果集合并起来，贝懦要用到Merger特性。Merger实现了多个服务调用后结果合并的逻辑。虽然业务层可以自行实现这个能力，但Dubbo直接封装到框架中，作为一种扩展点能力，简化了业务开发的复杂度。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image%205.png)

- Merger的扩展点

> 框架中有一些默认的合并实现。Merger接口上有@SPI注解，没有默认值，属于SPI扩展点。用户可以基于Merger扩展点接口实现自己的自定义类型合并器。
> 

### 2.1 总体结构

- 概述

> MergerCluster也是Cluster接口的一种实现，因此也遵循Cluster的设计模式，在invoke方法中完成具体逻辑。整个过程会使用Merger接口的具体实现来合并结果集。在使用的时候，通过MergerFactory获得各种具体的Merger实现。
> 
- Merger的12种默认实现

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image%206.png)

- 合并逻辑——`MapMerger`

> 如果开启了 Merger特性，并且未指定合并器(Merger的具体实现)，则框架会根据接口的返回类型自动匹配合并器。我们可以扩展属于自己的合并器，MergerFactory在加载具体实现的时候，**会用ExtensionLoader把所有SPI的实现都加载到缓存中。后续使用时直接从缓存中读取，如果读不到则会重新全量加载一次SPI**。内置的合并我们可以分为四类：`Array、Set、List、 Map`
> 

> 整个实现的思路就是，在Merge中新建了一个Map，把返回的多个Map合并成一个。其他类型的合并器实现都是类似的
> 

```java
@Override
public Map<?, ?> merge(Map<?, ?>... items) {
	//如果结果集为空，则直接返回null
   if (ArrayUtils.isEmpty(items)) {
       return Collections.emptyMap();
   }
   //如果结果集不为空则新建一个Map,遍历返回的结果集并放入新的Map
   Map<Object, Object> result = new HashMap<Object, Object>();
   Stream.of(items).filter(Objects::nonNull).forEach(result::putAll);
   return result;
}
```

### 2.2 MergeableClusterlnvoker 机制

- 调用过程

> MergeableClusterlnvoker串起了整个合并器逻辑，我们先回顾一下整个调用的过程：**MergeableCluster#join方法中直接生成并返回了MergeableClusterlnvoker, MergeableClusterInvoker#invoke 方法又通过 MergerFactory 工厂获取不同的Merger接口实现，完成了合并的具体逻辑。**
> 
- 机制逻辑——`MergeableClusterInvoker#doInvoke`

> MergeableCluster并没有继承抽象的Cluster实现，而是独立完成了自己的逻辑。因此，它
的整个逻辑和之前的Failover等机制不同，其步骤如下：
> 
> 1. 前置准备。通过directory获取所有Invoker列表。
> 2. 合并器检查。判断某个方法是否有合并器，如果没有，则不会并行调用多个group，找到第一个可以调用的Invoker直接调用就返回了。如果有合并器，则进入第3步。
> 3. 获取接口的返回类型。通过反射获得返回类型，后续要根据这个返回值查找不同的合并器。
> 4. 并行调用。把Invoker的调用封装成一个个Callable对象，放到线程池中执行，保存线程池返回的future对象到HashMap中，用于等待后续结果返回。
> 5. 等待fixture对象的返回结果。获取配置的超时参数，遍历(4)中得到的fixture对象， 设置Future#get的超时时间，同步等待得到并行调用的结果。异常的结果会被忽略，正常的结果会被保存到list中。如果最终没有返回结果，则直接返回一个空的RpcResult；如果只有一个结果， 那么也直接返回，不需要再做合并；如果返回类型是void,则说明没有返回值，也直接返回。
> 6. 合并结果集。如果配置的是merger=".addAll"，则直接通过反射调用返回类型中的.addAll方法合并结果集。例如：返回类型是Set，则调用Set.addAll来合并结果

==细节之——第六步的合并逻辑——指定方法合并结果集==

```java
if (merger.startsWith(".")) {
	//字符串截取，得到要调用的方法名
    merger = merger.substring(1);
    Method method;
    try {
    	//获取真正的方法对象
        method = returnType.getMethod(merger, returnType);
    } catch (NoSuchMethodException e) {
        ...
    }
    //如果是private等不可访问的方法，则设置为可以访问
    ReflectUtils.makeAccessible(method);
    result = resultList.remove(0).getValue();
    try {
    	//如果返回类型不为void,并会返回相同的类型，则反射调用该方法合并结果，并修改result
        if (method.getReturnType() != void.class
                && method.getReturnType().isAssignableFrom(result.getClass())) {
            for (Result r : resultList) {
                result = method.invoke(result, r.getValue());
            }
        } else {
        	//如果不符合，则直接把结果合并进去即可
            for (Result r : resultList) {
                method.invoke(result, r.getValue());
            }
        }
    } catch (Exception e) {
        ....
    }
}
```

==细节之——第六步的合并逻辑——未指定方法，调用合并器来合并==

```java
else {
    Merger resultMerger;
    //如果是默认的Merger 参数为true或default ,则用MergerFactory获取默认的合并器，
    //否则通过ExtensionLoader获取对应名字的合并器
    if (ConfigUtils.isDefault(merger)) {
        resultMerger = MergerFactory.getMerger(returnType);
    } else {
        resultMerger = ExtensionLoader.getExtensionLoader(Merger.class).getExtension(merger);
    }
    //找到合并器则合并，否则抛出异常
    if (resultMerger != null) {
        List<Object> rets = new ArrayList<Object>(resultList.size());
        for (Result r : resultList) {
            rets.add(r.getValue());
        }
        result = resultMerger.merge(
                rets.toArray((Object[]) Array.newInstance(returnType, 0)));
    } else {
        throw new RpcException("There is no merger to merge result.");
    }
}
```

## 3.Mock

- 概述

> 在Cluster中，还有最后一个MockClusterWrapper,由它实现了 Dubbo的本地伪装。这个功能的使用场景较多，通常会应用在以下场景中：服务降级；部分非关键服务全部不可用，希望主流程继续进行；在下游某些节点调用异常时，可以以Mock的结果返回。
> 

### 3.1 Mock常见的使用方式

- 概述

> Mock只有在拦截到RpcException的时候会启用，属于异常容错方式的一种。业务层面其实也可以用try-catch来实现这种功能，如果使用下沉到框架中的Mock机制，则可以让业务的实现更优雅。常见配置如下：
> 
- 配置以及使用方式

```xml
<dubbo:reference interface="com.foo.BarService" mock="true" />
<!--配置方式2-->
<dubbo:reference interface="com.foo.BarService" mock="com.foo.BarServiceMock" />
<!--配置方式3-->
<dubbo:reference interface="com.foo.BarService" mock="return null" />
```

```java
//提供Mock实现，如果Mock配置了 true或default,则实现的类名必须是接口名+Mock,如配置方式1
//否则会直接取Mock参数值作为Mock实现类，如配置方式2
package com.foo;
public class BarServiceMock implements BarService {
	public String sayHello(String name) {
		return "容错数据";//可以伪造容错数据，此方法只在出现RpcException时被执行
	}
}
```

- 服务降级

> 服务的降级是在dubbo-admin中通过override协议更新Invoker的Mock参数实现的。如果Mock参数设置为mock=force: return+null，则表明是强制Mock，强制Mock会让消费者对该服务的调用直接返回null，不再发起远程调用。通常使用在非重要服务己经不可用的时候，可以屏蔽下游对上游系统造成的影响。此外，还能把参数设置为mock=fail:retupn+null,这样消费者还是会发起远程调用，不过失败后会返回null，但是不抛出异常。如果配置的参数是以throw开头的，即mock= throw,则直接抛出RpcException，不会发起远程调用。
> 

### 3.2 Mock的总体结构

- 概述

> Mock涉及的接口比较多,整个流程贯穿Cluster和Protocol层
> 
> - MockClusterWrapper是一个包装类，包装类会被自动注入合适的扩展点实现，它的逻辑很简单，只是把被包装扩展类作为初始化参数来创建并返回一个MockClusterlnvoker
> - MockClusterlnvoker和其他的Clusterinvoker 一样，在Invoker方法中完成了主要逻辑。
> - MocklnvokersSelector 是 Router 接口 的一种实现，用于过滤出 Mock 的 Invoker。
> - MockProtocol根据用户传入的URL和类型生成一个Mockinvoker
> - Mockinvoker实现最终的Invoker逻辑。
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%94%C2%B7%E7%BB%AD%EF%BC%89%20Dubbo%E9%9B%86%E7%BE%A4%E5%AE%B9%E9%94%99%E2%80%94%E2%80%94%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/image%207.png)
> 
- `Mockinvoker与MockClusterlnvoker`

> • 首先，强制Mock、失败后返回Mock结果等逻辑是在MockClusterlnvoker里处理的；其次， MockClusterlnvoker在某些逻辑下，会生成Mockinvoker并进行调用；
• 然后，在Mockinvoker里会处理 `mock="return null"、 mock="throw xxx"或 mock=com.xxService` 这些配置逻辑。
• 最后， Mockinvoker还会被 MockProtocol在引用远程服务的时候创建。
> 

> **我们可以认为， MockClusterlnvoker会处理一些Class级别的Mock逻辑，例如：选择调用哪些Mock类。Mockinvoker处理的是方法级别的Mock逻辑，如返回值。**
> 

### 3.3 Mock的实现原理

==MockClusterlnvoker 的实现原理==

- `MockClusterlnvoker#invoke`

> MockClusterWrapper是一个包装类，它在创建 MockClusterlnvoker的时候会把被包装的Invoker传入构造方法，因此MockClusterlnvoker内部天生就含有一个Invoker的引用。MockClusterlnvoker的invoke方法处理了主要逻辑，步骤如下：
> 
> 1. 获取Invoker的Mock参数。前面已经说过，该Invoker是在构造方法中传入的。如果该Invoker根本就没有配置Mock,则直接调用Invoker的invoke方法并把结果返回；如果配置了 Mock参数，则进入下一步。
> 2. 判断参数是否以force开头，即判断是否强制Mock。如果是强制Mock，则进入doMocklnvoke逻辑，这部分逻辑在后面统一讲解。如果不以force开头，则进入失败后Mock的逻辑。
> 3. 失败后调用doMocklnvoke逻辑返回结果。在try代码块中直接调用Invoker的invoke方法，如果抛出了异常，则在catch代码块中调用doMocklnvoke逻辑。
- 细节之——强制Mock和失败后Mock都会调用doMocklnvoke

> 
> 
> 1. 通过 selectMocklnvoker 获得所有 Mock 类型的 Invoker。selectMocklnvoker 在对象的attachment属性中偷偷放进一个invocation.need.mock=true的标识。directory在list方法中列出所有Invoker的时候，如果检测到这个标识，则使用MockinvokersSelector来过滤Invoker，而不是使用普通route实现，最后返回Mock类型的Invoker列表。如果一个Mock类型的Invoker都没有返回，则通过directory的URL新创建一个Mockinvoker；如果有Mock类型的Invoker，则使用第一个。
> 2. 调用Mockinvoker的invoke方法。在try-catch中调用invoke方法并返回结果。如果出现了异常，并且是业务异常，则包装成一个RpcResult返回，否则返回RpcException异常。
>     
>     MocklnvokersSelector 的实现原理
>     
- `MocklnvokersSelector #route`

> 在 doMocklnvoke 的第 1 步中，directory 会使用 MocklnvokersSelector 来过滤出 Mock 类型
的Invoker。MocklnvokersSelector是Router接口的其中一种实现。它路由时的具体逻辑如下：
> 
> 1. 判断是否需要做Mock过滤。如果attachment为空，或者没有invocation.need.mock=true的标识，则认为不需要做Mock过滤，进入步骤2；如果找到这个标识，则进入步骤3。
> 2. 获取非Mock类型的Invoker。遍历所有的Invoker,如果它们的protocol中都没有Mock参数，则整个列表直接返回。否则，把protocol中所有没有Mock标识的取出来并返回。
> 3. 获取Mock类型的Invoker。遍历所有的Invoker,如果它们的protocol中都没有Mock参数，则直接返回null。否则，把protocol中所有含有Mock标识的取出来并返回。
> ==MockProtocol 与 Mockinvoker 的实现原理==
- `MockProtocol#export&refer`

> MockProtocol也是协议的一种,主要是把注册中心的Mock URL转换为Mockinvoker对象。URL可以通过dubbo.admin或其他方式写入注册中心，它被定义为只能引用，不能暴露
> 

```java
@Override
public <T> Exporter<T> export(Invoker<T> invoker) throws RpcException (
	throw new UnsupportedOperationException(); //不能暴露，否则会抛异常
}
@Override
public <T> Invoker<T> refer(Class<T> type, URL url) throws RpcException (
	return new MockInvoker<T>(url); // 直接把引用的 Mock URL 转换为一个 Mockinvoker 对象
}
```

- 工作流程实例——`Mockinvoker#invoke`

> 例如，我们在注册中心`/dubbo/com.test.xxxService/providers`这个服务提供者的目录下， 写入一个 Mock 的 URL： `mock:// 192.168.0.123/com.test.xxxService`
> 
> 1. 获取Mock参数值。通过URL获取Mock配置的参数，如果为空则抛出异常。优先会获取方法级的Mock参数，例如：以methodName.mock为key去获取参数值；如果取不到， 则尝试以mock为key获取对应的参数值。
> 2. 处理参数值是return的配置。如果只配置了一个return,即mock=return,则返回一个空的RpcResult；如果return后面还跟了别的参数，则首先解析返回类型，然后结合Mock参数和返回类型，返回Mock值。现支持以下类型的参数：Mock参数值等于empty，根据返回类型返回new xxx()空对象；如果参数值是null、 true、 false,则直接返回这些值；如果是其他字符串，则返回字符串；如果是数字、List、Map类型，则返回对应的JSON串；如果都没匹配上， 则直接返回Mock的参数值。
> 3. 处理参数值是throw的配置。如果throw后面没有字符串，则包装成一个RpcException异常，直接抛出；如果throw后面有自定义的异常类，则使用自定义的异常类，并包装成一个RpcException 异常抛出。
> 4. 处理Mock实现类。先从缓存中取，如果有则直接返回。如果缓存中没有，则先获取接口的类型，如果Mock的参数配置的是true或default，则尝试通过“接口名+Mock”查找Mock实现类，例如：TestService会查找Mock实现TestServiceMock0如果是其他配置方式，则通过Mock的参数值进行查找，例如：配置了 mock=com.xxx.testservice ，则会查找com.xxx.testservice