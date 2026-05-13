# Java多并发（五）| JUC包下的并发容器（ConcurrentHashMap）& 并发工具类 & 原子变量类

type: Post
status: Published
date: 2022/07/10
summary: Java并发容器及框架及并发工具类
tags: Java
category: 技术栈

# Java并发容器及框架及并发工具类

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image.png)

## 1.ConcurrentHashMap

[jdk7和jdk8的区别](https://www.cnblogs.com/awkflf11/p/12826164.html)

### 1.1 ConcurrentHashMap & HashMap & HashTable

- 为什么要使用ConcurrentHashMap

> `ConcurrentHashMap`是线程安全且高效的`HashMap`。在并发编程中使用`HashMap`可能导致程序死循环。而使用线程安全的`HashTable`效率又非 常低下，基于以上两个原因，便有了`ConcurrentHashMap`的登场机会。
> 
1. 线程不安全的HashMap

> 在多线程环境下，使用HashMap进行put操作会引起死循环，导致CPU利用率接近100%，所 以在并发情况下不能使用HashMap。例如，执行以下代码会引起死循环。**HashMap在并发执行put操作时会引起死循环，是因为多线程会导致HashMap的Entry链表 形成环形数据结构，一旦形成环形数据结构，Entry的next节点永远不为空，就会产生死循环获 取Entry。**
> 

> JDK7到JDK8的线程不安全得到了改善
[点击传送](https://blog.csdn.net/zzu_seu/article/details/106669757)
> 

```java
final HashMap<String, String> map = new HashMap<>();
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 0; i < 10000; i++) {
                    new Thread(new Runnable() {
                        @Override
                        public void run() {
                            map.put(UUID.randomUUID().toString(),"");
                        }
                    },"ftf"+i).start();
                }
            }
        }, "ftf");
        t.start();
        t.join();
```

1. 效率底下的HashTable

> **HashTable容器使用synchronized来保证线程安全，但在线程竞争激烈的情况下HashTable 的效率非常低下。因为当一个线程访问HashTable的同步方法，其他线程也访问HashTable的同 步方法时，会进入阻塞或轮询状态。如线程1使用put进行元素添加，线程2不但不能使用put方法添加元素，也不能使用get方法来获取元素，所以竞争越激烈效率越低。**
> 
1. ConcurrentHashMap的锁分段技术可以有效提高并发访问率

> **HashTable容器在竞争激烈的并发环境下表现出效率低下的原因是所有访问HashTable的 线程都必须竞争同一把锁，假如容器里有多把锁，每一把锁用于锁容器其中一部分数据，那么 当多线程访问容器里不同数据段的数据时，线程间就不会存在锁竞争，从而可以有效提高并 发访问效率，这就是ConcurrentHashMap所使用的锁分段技术。首先将数据分成一段一段地存 储，然后给每一段数据配一把锁，当一个线程占用锁访问其中一个段数据的时候，其他段的数 据也能被其他线程访问。**
> 

### 1.2 JDK1.7与1.8的区别

[主要概括](https://www.cnblogs.com/awkflf11/p/12826164.html)

### 1. ConcurrentHashMap（1.7）

- 概述

> 在1.7中，ConcurrentHashMap采用segment数组+hashEntry数组节点组成，默认默认 Segment 的个数是 16 个，你也可以认为 ConcurrentHashMap 默认支持最多 16 个线程并发。并且segment数组是不支持扩容的，但HashEntry数组时支持扩容的
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%201.png)

- 初始化

> 构造器是根据三个值来初始化的`默认容量、加载因子、并发等级`（**最大值时65535，即segments数组的最大长度是65536，注意2的次幂条件哦**）的，如果没指定全部采用默认；初始化其实就是初始化Segment数组，除了该数组还需要初始化段偏移量：segmentShift、段掩码：segmentMask和每个segment里的 HashEntry数组
> 
- 初始化Segments数组

> **该数组的长度并不是直接拿默认容量来设置的，而是通过并发等级计算出来的容量，为了加强性能使用位运算，所以长度肯定是2的次幂，所以必须计算出一个大于等于并发等级的最小2的N次方值，即并发等于14、15或16，ssize都会等于16，默认长度都是16，即锁的个数也是16**
> 

```java
if (concurrencyLevel > MAX_SEGMENTS)
	concurrencyLevel = MAX_SEGMENTS;
	int sshift = 0;
	int ssize = 1;
	while (ssize < concurrencyLevel) {
		++sshift;
		ssize <<= 1;
	}
	segmentShift = 32 - sshift;
	segmentMask = ssize - 1;
	this.segments = Segment.newArray(ssize);
```

- 初始化segmentShift和segmentMask（注意：segmentShift != sshift）

> 这两变量在定位segment时会用到，sshift等于数组大小向左移位的次数；默认并发等级为16，那么大小也为16，从1变为16需要移动四次，所以sshift为4；**因为ssize的最大长度是65536，所以segmentShift最大值是16，segmentMask最大值是 65535，对应的二进制是16位，每个位都是1。**
> 
> - segmentShift用于定位参与哈希运算的位数，等于32-sshift，上述默认的情况下等于28；之所以是32是因为hash方法最大数是32位的；
> - segmentMask是哈希运算的掩码，等于ssize-1，上述默认为15，掩码的二进制各个位的值都是1
- 初始化每个segment

> 通过initialCapacity和loadfactor来初始化每个segment。初始化代码中先计算HashEntry数组的长度c（通过initialCapacity除以ssize），如果长度大于1，就会取大于等于c的2的N次方，所以cap要么是1要么就是2的N次方；segment的容量为`threshold＝（int）cap*loadFactor`
> 

> 默认情况下`initialCapacity`等于16，`loadfactor`等于 0.75，通过运算`cap`等于1，`threshold`等于零。
> 

```java
if (initialCapacity > MAXIMUM_CAPACITY)
	initialCapacity = MAXIMUM_CAPACITY;
	int c = initialCapacity / ssize;
	if (c * ssize < initialCapacity)
		++c;
	int cap = 1;
	while (cap < c)
		cap <<= 1;
	for (int i = 0; i < this.segments.length; ++i)
		this.segments[i] = new Segment<K,V>(cap, loadFactor);
```

- 定位Segment

> 我们知道并发的hashmap使用的是分段锁，那么在插入和获取元素时都需要通过哈希函数定位到桶的位置，通常会对hashcode后的散列值在散列的方式，在散列无非就是降低散列冲突；原版hashmap也是相同套路不过在散列没这个复杂
> 

```java
private static int hash(int h) {
	h += (h << 15) ^ 0xffffcd7d;
	h ^= (h >>> 10);
	h += (h << 3);
	h ^= (h >>> 6);
	h += (h << 2) + (h << 14);
	return h ^ (h >>> 16);
}
```

> `HASH_BITS`：该值就是与上图的那个十六进制相同的作用`0x7fffffff`，**后面与HASH_BITS按位与操作，是为了让最高位为0，保证是正数。HASH_BITS是最大的正数，首位为0，这时JDK8的用法，上面看到7中会先对低位进行运算**
> 

> 拿到这个散列值后，会通过一个散列函数定位到最后的桶中。**默认情况下segmentShift为28，segmentMask为15，再散列后的数最大是32位二进制数据， 向右无符号移动28位，意思是让高4位参与到散列运算中**
> 

```java
final Segment<K,V> segmentFor(int hash) {
	return segments[(hash >>> segmentShift) & segmentMask];
}
```

- get()方法

> 对于并发容器来说读是不用加锁的，除非读到的值为空才会加锁重读；在7中通过给每个共享变量都加上了Volatile关键字来保证读不用加锁；**即保证线程之间的可见性并且不会读到过期值（别忘了happen-before哦）对volatile字段的写入操作先于读操作，即使两个线程同时修改和获取 volatile变量，get操作也能拿到最新的值，这是用volatile替换锁的经典应用场景。**
> 

```java
public V get(Object key) {
	int hash = hash(key.hashCode());
	return segmentFor(hash).get(key, hash);
}
```

> 对于定位Segment的方法我们上面讲过，我们现在讲一下如何定位HashEntry数组，对于定位Segment来说拿到hash值时会对这个hash值进行加工，获取高位使用高位，使之散列性能很好；而对于定位HashEntry拿到hash值之后虽然也进行了再加工但是没有进行位之间的移动的
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%202.png)

- put()方法

> put操作则会经历两个步骤
> 
> - 是否需要对segment中的HashEntry数组进行扩容：
> - 定位添加元素的位置

==是否需要扩容==：

> 在插入元素前会先判断Segment里的HashEntry数组是否超过容量（threshold），**对于是否进行扩容这个是先于添加元素之间判断的，这个跟hashmap稍有不同，hashmap是将元素添加到里面后在进行判断，如果达到了就扩容，但是过添加完之后没有元素添加了那就很浪费了，所以hashmap在这点做的不好**
> 

==如何扩容==：

> 在扩容的时候，会创建一个容量是原来两倍的数组，然后将原数组进行散列在添加到这个数组，注意不会对整个Segment扩容，而是对定位到的那个Segment扩容
> 
- size()方法

> 对于获取容器的大小的方法，这个变量肯定是共享的，那么上面提到共享变量就是volatile修饰的，而我说过conut这个值是表示Segment大小的，那么我们把每个Segment的count都加起来不就好了，首先思考在累加的过程中前面count发生变化了怎么办？我们是否应该采取加锁的形式获取，
> 

> 在ConcurrentHashMap中采用两次不加锁累加获取size，然后通过对比modCount的大小，如果不一致则触发第三次加锁获取
> 

> modCount变量：该变量会在put、remove、clean方法操作元素后进行+1，那么通过比较这个就很轻易的知道容器是否发生变化了
> 

### 2. ConcurrentHashMap（1.8）

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%203.png)

- ConcurrentHashMap的字段

> 最大的桶容量（1<<30）、默认桶容量（16）、最大的数组大小（int最大值-8）、默认并发等级：决定桶的数量、负载因子（0.75）、变树链表长度的阈值（8）、变链表的阈值（6）、变树的数组长度阈值（64）、同步状态量（sizeCtl默认为16）、默认偏移值（16）、由于状态量有不同的值会表达出不同的意义，所以存在记录大小的标记位移（32-同步状态量）、可以帮助调整的最大线程数
> 
- 初始化

> 由于到8之后，该容器从原来的Segment改为了Synchronized+CAS的结果来实现线程安全，那么在初始化的改变就是会通过CAS操作来完成，初始化状态由`sizeCtl`来标注
> 

> sizeCtl的不同值的不同意味：
> 
> - 1 说明正在初始化
> - N 说明有N-1个线程正在进行扩容
> - 表示 table 初始化大小，如果 table 没有初始化
> - 表示 table 容量，如果 table　已经初始化。
- hash方法的改变

> 原先在7中，我们发送hash方法是得到hashcode后在进行散列得到的，到了8，方法名变为了spread，但内核没变代码简化，上面解释过Hash_BITS哦
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%204.png)

- 如何定位桶

> 在7中我们看到定位Segment时，会将通过hash方法算出的hash在散列后才是桶的位置，而在8中是直接拿spread方法算出的hash值用的，因为8中已经没有Segment数组中嵌套着HashEntry数组了（所以需要定位两次啊），只有Node数组，即没有上级了你就这么想
> 
- 对于put、get、size、resize

> 其实实现大多与7没有区别，核心思路是一样的，你只需要关心对于并发该容器做了那些细节改变，看上面那个网址就好
> 

## 2.ConcurrentLinkedQueue

- 概述

> **在并发编程中，有时候需要使用线程安全的队列。如果要实现一个线程安全的队列有两 种方式：一种是使用阻塞算法，另一种是使用非阻塞算法。使用阻塞算法的队列可以用一个锁 （入队和出队用同一把锁）或两个锁（入队和出队用不同的锁）等方式来实现。非阻塞的实现方 式则可以使用循环CAS的方式来实现。**
> 

### 2.1 ConcurrentLinkedQueue的结构

> `ConcurrentLinkedQueue由head节点和tail节点组成`，每个节点`（Node）`由节点元素`（item）`和 指向下一个节点`（next）`的引用组成，节点与节点之间就是通过这个`next`关联起来，从而组成一 张链表结构的队列。默认情况下`head`节点存储的元素为空，`tail`节点等于`head`节点。
> 

```java
private transient volatile Node<E> tail = head;
```

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%205.png)

### 2.2 入队（写出的源码都是jdk8的）

- 概述

> 我们直接观察一个入队例子就能很好的理解了
> 
> 
> **通过调试入队过程并观察`head节点和tail节点`的变化，发现入队主要做两件事情：第一是 将入队节点设置成当前队列尾节点的下一个节点；第二是更新tail节点，如果`tail节点的next节` 点不为空，则将入队节点设置成`tail节点`，如果`tail节点的next节点`为空，则将入队节点设置成 `tail的next节点`，所以`tail节点不总是尾节点`** 
> 
> ![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%206.png)
> 
- 多线程的情况下入队

> 在多线程的情况下会发生插队情况，下面看看如何使用CAS算法来入队的，**整个入队过程主要做两件事情：第一是定位出尾节点；第二是使用 CAS算法将入队节点设置成尾节点的next节点，如不成功则重试。**
> 

```java
	public boolean offer(E e) {
		//
        checkNotNull(e);
        //入队前创建一个入队节点
        final Node<E> newNode = new Node<E>(e);
		//死循环，入队不成功反复入队，创建一个指向tail节点的引用，
		//p用来表示队列的尾节点，默认情况下等于tail节点
        for (Node<E> t = tail, p = t;;) {
        	 //获得p节点的下一个结点
            Node<E> q = p.next;
            //如果为空，说明p是尾节点
            if (q == null) {
                //则设置p节点的next节点为入队节点
                if (p.casNext(null, newNode)) {
                    /*如果tail节点有大于等于1个next节点，
                    则将入队节点设置成tail节点， 更新失败了也没关系，
                    因为失败了表示有其他线程成功更新了tail节点*/
                        casTail(t, newNode);  //更新tail节点，允许失败
                    return true;
                }
                //
            }
            //此时说明p不是尾节点，需要设置指向新入队的节点
            else if (p == q)

                p = (t != (t = tail)) ? t : head;
            else
                // p有next节点，表示p的next节点是尾节点，则重新设置p节点
                p = (p != t && t != (t = tail)) ? t : q;
        }
    }
```

### 2.3 定位尾节点

- 概述

> **tail节点并不总是尾节点，所以每次入队都必须先通过tail节点来找到尾节点。尾节点可能 是tail节点，也可能是tail节点的next节点。**
> 

```java
final Node<E> succ(Node<E> p) {
        Node<E> next = p.next;
        return (p == next) ? head : next;
    }
```

### 2.4 设置入队节点为尾节点

- 概述

> **p.casNext（null，n）方法用于将入队节点设置为当前队列尾节点的next节点，如果p是null， 表示p是当前队列的尾节点，如果不为null，表示有其他线程更新了尾节点，则需要重新获取当 前队列的尾节点。**
> 

### 2.5 jdk7中的hops变量

- 概述

> 这个变量就是为了减少cas次数，提高入队效率存在的，但是jdk8中删除，而是使用单纯的if判断
> 

### 2.6 注意

> 入队列永远返回true，所以不要通过返回值来判断入队是否成功
> 

### 2.7 出队列

- 概述

> 从图中可知，并不是每次出队时都更新head节点，当head节点里有元素时，直接弹出head 节点里的元素，而不会更新head节点。只有当head节点里没有元素时，出队操作才会更新head 节点。
> 
> 
> **这种做法也是通过hops变量来减少使用CAS更新head节点的消耗，从而提高出队效率。**
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%207.png)

> **首先获取头节点的元素，然后判断头节点元素是否为空，如果为空，表示另外一个线程已 经进行了一次出队操作将该节点的元素取走，如果不为空，则使用CAS的方式将头节点的引 用设置成null，如果CAS成功，则直接返回头节点的元素，如果不成功，表示另外一个线程已经 进行了一次出队操作更新了head节点，导致元素发生了变化，需要重新获取头节点。**
> 

```java
public E poll() {
        restartFromHead:
        for (;;) {
        	//p表示头节点，需要出队的节点
            for (Node<E> h = head, p = h, q;;) {
				//获取p节点的元素
                E item = p.item;
				//如果p节点的元素不为空，使用cas设置p节点引用的元素为null
				//如果成功则返回p节点的元素
                if (item != null && p.casItem(item, null)) {
                    //将p节点的下一个节点设置成head节点
                    if (p != h)
                        updateHead(h, ((q = p.next) != null) ? q : p);
                    return item;
                }
                //如果p的下一个节点也为空，说明这个队列已经为空了，更新头节点返回null
                else if ((q = p.next) == null) {
                    updateHead(h, p);
                    return null;
                }
                // 如果头节点的元素为空或头节点发生了变化，这说明头节点已经被另外
                // 一个线程修改了。那么获取p节点的下一个节点
                else if (p == q)
                    continue restartFromHead;
                else
                    p = q;
            }
        }
    }
```

## 3.Java中的阻塞队列

[这里有里面几种队列的详解](https://blog.csdn.net/weixin_49258262/article/details/125463819?csdn_share_tail=%7B%22type%22:%22blog%22,%22rType%22:%22article%22,%22rId%22:%22125463819%22,%22source%22:%22weixin_49258262%22%7D&ctrtid=yqFcP)

### 3.1 什么是阻塞队列

- 概述

> 阻塞队列就是支持两个附加操作的队列，这两个附加的操作支持阻塞的插入和移除方法。**可以看到阻塞队列可以用到消费者和生产者的场景，阻塞队列就是生产者，消费者就是用来获取元素的容器**
> 
> - 插入：当队列满时，队列会阻塞要插入元素的线程，直到不满
> - 移除：队列空时，获取元素的线程会等到队列变为非空，
- 在阻塞队列不可用时，这两个附加操作提供了四种处理方式

> • **抛出异常**：当队列满时，如果再往队列里插入元素，会抛出`IllegalStateException（"Queue full"）`异常。当队列空时，从队列里获取元素会抛出`NoSuchElementException`异常。
• **返回特殊值**：当往队列插入元素时，会返回元素是否插入成功，成功返回`true`。如果是移 除方法，则是从队列里取出一个元素，如果没有则返回`null`。
• **一直阻塞**：当阻塞队列满时，如果生产者线程往队列里`put`元素，队列会一直阻塞生产者 线程，直到队列可用或者响应中断退出。当队列空时，如果消费者线程从队列里`take`元素，队 列会阻塞住消费者线程，直到队列不为空。
• **超时退出**：当阻塞队列满时，如果生产者线程往队列里插入元素，队列会阻塞生产者线程 一段时间，如果超过了指定的时间，生产者线程就会退出。
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%208.png)

- 注意

> **如果是无界阻塞队列，队列不可能会出现满的情况，所以使用put或offer方法永 远不会被阻塞，而且使用offer方法时，该方法永远返回true。**
> 

### 3.2 Java中的阻塞队列

> 这些queue的超类都十分类似，自上而下就是Iterable接口，Collection接口继承上面的，然后是queue接口和抽象Collection类继承或实现上面的，然后全部集合都实现了BlockingQueue，这个接口实现了Queue。还有抽象Queue类也几乎都被继承
> 

JDK 7提供了7个阻塞队列，如下。

- `ArrayBlockingQueue`：**一个由数组结构组成的有界阻塞队列。 默认情况下不保证公平性，可以使用可重入锁实现公平访问**
- `LinkedBlockingQueue`：**一个由链表结构组成的有界阻塞队列**。
- `PriorityBlockingQueue`：**一个支持优先级排序的无界阻塞队列**。
- `DelayQueue`：**一个使用优先级队列实现的无界阻塞队列**。
- `SynchronousQueue`：**一个不存储元素的阻塞队列**。
- `LinkedTransferQueue`：**一个由链表结构组成的无界阻塞队列**。
- `LinkedBlockingDeque`：**一个由链表结构组成的双向阻塞队列**。

### 3.3 阻塞队列的实现原理

- 需要解决的问题

> • 如果队列是空的，消费者会一直等待，当生产者添加元素时，消费者是如何知道当前队列有元素的呢？
• 如果让你来设计阻塞队列你会如何设计，如何让生产者和消费者进行高效率的通信呢？
> 

==通知模式==：

> 使用通知模式实现。所谓通知模式，就是当生产者往满的队列里添加元素时会阻塞住生 产者，当消费者消费了一个队列中的元素后，会通知生产者当前队列可用。通过查看JDK源码 发现ArrayBlockingQueue使用了Condition来实现
> 
- 总结

> 就是结合Condition和lockSupport组合实现的
> 

## 4.Fork/Join框架

- 概述

> `Fork/Join`框架是`Java 7`提供的一个用于并行执行任务的框架，是一个把大任务分割成若干 个小任务，最终汇总每个小任务结果后得到大任务结果的框架。 我们再通过`Fork和Join`这两个单词来理解一下`Fork/Join`框架。`Fork`就是把一个大任务切分 为若干子任务并行的执行，Join就是合并这些子任务的执行结果，最后得到这个大任务的结 果。比如计算`1+2+…+10000`，可以分割成`10`个子任务，每个子任务分别对`1000`个数进行求和， 最终汇总这`10`个子任务的结果。`Fork/Join`的运行流程如图6-6所示。
> 

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%209.png)

### 4.1 工作窃取算法（work-stealing）

- 概述

> 工作窃取（work-stealing）算法是指某个线程从其他队列里窃取任务来执行。可以减少线程间的竞争
> 
- 使用场景

> 一个大的任务，我们可以把任务分割成很多个互相不依赖的子任务，分别放到不同的队列中去，每个队列单独创建一个线程来执行，那么肯定有的线程执行的快，把自己的活干完了，闲着不如干活，就可以窃取别的队列的任务来完成。**而在这时它们会访问同一个队列，所以为了减少窃取任务线程和被 窃取任务线程之间的竞争，通常会使用双端队列，被窃取任务线程永远从双端队列的头部拿 任务执行，而窃取任务的线程永远从双端队列的尾部拿任务执行。**
> 
- 缺点

> 在某些情况下还是存在竞争，比如双端队列里只有一个任务时。并 且该算法会消耗了更多的系统资源，比如创建多个线程和多个双端队列。
> 

### 4.2 Fork/Join架构的设计

- 步骤：

> **步骤一：分割任务、步骤二：执行任务并合并结果**
> 
- 涉及到的类来完成上面的事情

> `①ForkJoinTask`：我们要使用ForkJoin框架，必须首先创建一个ForkJoin任务。它提供在任务 中执行fork()和join()操作的机制。通常情况下，我们不需要直接继承ForkJoinTask类，只需要继 承它的子类，Fork/Join框架提供了以下两个子类。
> 
> - RecursiveAction：用于没有返回结果的任务。
> - RecursiveTask：用于有返回结果的任务。

> `②ForkJoinPool`：ForkJoinTask需要通过ForkJoinPool来执行。
> 
- 例子

```java
/**
 * @author lhj
 * @create 2022/4/1 20:23
 * 让我们通过一个简单的需求来使用Fork/Join框架，需求是：计算1+2+3+4的结果
 *
 * 使用Fork/Join框架首先要考虑到的是如何分割任务，如果希望每个子任务最多执行两个 数的相加，
 * 那么我们设置分割的阈值是2，由于是4个数字相加，所以Fork/Join框架会把这个任 务fork成两个子任务，
 * 子任务一负责计算1+2，子任务二负责计算3+4，然后再join两个子任务 的结果。因为是有结果的任务，
 * 所以必须继承RecursiveTask
 */
public class CountTask extends RecursiveTask<Integer> {
    //阈值
    private static final int THRESHOLD = 2;

    private int start;
    private int end;

    public CountTask(int start, int end) {
        this.start = start;
        this.end = end;
    }

    @Override
    protected Integer compute() {
        int sum = 0;

        //如果任务足够小就计算任务
        boolean canCompute = (end - start) <= THRESHOLD;
        if(canCompute) {
            for (int i = start; i < end; i++) {
                sum += i;
            }
        } else{
            //如果超过阈值，那就分裂成两个子任务
            int mid = (start + end) / 2;
            CountTask leftTask = new CountTask(start, mid);
            CountTask rightTask = new CountTask(mid + 1, end);

            //执行子任务
            leftTask.fork();
            rightTask.fork();

            //等待子任务执行完，并得到其结果
            Integer leftRes = leftTask.join();
            Integer rightRes = rightTask.join();

            sum = leftRes + rightRes;
        }
        return sum;
    }

    public static void main(String[] args) {
        ForkJoinPool pool = new ForkJoinPool();
        //生成一个计算任务，负责计算1+2+3+4
        CountTask countTask = new CountTask(1, 4);
        //执行一个任务
        ForkJoinTask<Integer> result = pool.submit(countTask);
        try {
            System.out.println(result.get());
        } catch (InterruptedException e) {
        } catch (ExecutionException e) {
        }
    }
}
```

### 4.3 框架的异常处理

- 概述

> ForkJoinTask在执行的时候可能会抛出异常，但是我们没办法在主线程里直接捕获异常， 所以ForkJoinTask提供了`isCompletedAbnormally()`方法来检查任务是否已经抛出异常或已经被 取消了，并且可以通过`ForkJoinTask的getException`方法获取异常。**getException方法返回Throwable对象，如果任务被取消了则返回CancellationException。如 果任务没有完成或者没有抛出异常则返回null。**
> 

### 4.4 实现原理

- 概述

> ForkJoinPool由ForkJoinTask数组和ForkJoinWorkerThread数组组成，ForkJoinTask数组负责 将存放程序提交给ForkJoinPool的任务，而ForkJoinWorkerThread数组负责执行这些任务。
> 
- ForkJoinTask的fork方法

> • 当我们调用ForkJoinTask的fork方法时，程序会调用ForkJoinWorkerThread的pushTask方法 异步地执行这个任务，然后立即返回结果
• pushTask方法把当前任务存放在ForkJoinTask数组队列里。然后再调用ForkJoinPool的 signalWork()方法唤醒或创建一个工作线程来执行任务
> 
- ForkJoinTask的join方法

> Join方法的主要作用是阻塞当前线程并等待获取结果，首先，它调用了doJoin()方法，通过doJoin()方法得到当前任务的状态来判断返回什么结 果，**在这个方法中首先会看任务的状态，看任务是否已经执行完成，如果执行完成则直接返回任务状态，如果没有执行完则从数组中取出任务继续执行。顺利执行则返回normal，出现异常则标记异常，并将任务状态设置为exceptional**
> 

> 任务状态有4种：`已完成（NORMAL）、被取消（CANCELLED）、信号（SIGNAL）和出现异常 （EXCEPTIONAL）`。
> 
> - 如果任务状态是已完成，则直接返回任务结果。
> - 如果任务状态是被取消，则直接抛出CancellationException。
> - 如果任务状态是抛出异常，则直接抛出对应的异常。

## 5.原子变量类

- 概述

> 原子变量类时基于CAS实现的，对共享数据进行`read-modify-write`更新操作时，通过此类可以保证操作的原子性和可见性，由于volatile关键字只能保证可见性，无法保证原子性，原子变量类内部就是借助一个volatile变量，并且保障了该变量的原子性，**既可以把原子变量类看成一个加强版的volatile**
> 
- 大致过程

> 通过Unsafe拿到内存中的值，然后进行CAS就完事了
> 
- 分类

![image.png](Java%E5%A4%9A%E5%B9%B6%E5%8F%91%EF%BC%88%E4%BA%94%EF%BC%89%20JUC%E5%8C%85%E4%B8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E5%AE%B9%E5%99%A8%EF%BC%88ConcurrentHashMap%EF%BC%89&%20%E5%B9%B6%E5%8F%91%E5%B7%A5%E5%85%B7%E7%B1%BB%20&%20/image%2010.png)

## 6.Java中的并发工具类（CountDownLatch、CyclicBarrier、Semaphore、Exchanger）

- 等待多线程完成的CountDownLatch

> 你就理解为加强版的join，将count个线程阻塞爱一个地方，直至所有线程完成任务
> 

> 大致流程如下：
> 
> - 初始化为线程数量，即为状态量
> - 当线程使用countDown方法开始执行回去尝试将状态量减1，直至为0
> - 调用await方法，等待所有任务执行完（就看状态量为不为0，不为0就一直等）
> - 当状态量为0则执行完毕，await后面代码继续执行

> 除了上面的常规用法，还可以实现并行的任务执行，所有线程首先调用await方法等待，将计数器初始化为1，然后主线程调用countDown，全部线程统一被唤醒
> 
- 同步屏障CyclicBarrier

> 也是个加强版的join，等待全部线程完成任务统一返回
> 

> CyclicBarrier有两个构造方法，即代表两种不同的用法
> 
> - 传入线程数量的，那执行的线程数达到这个传入的线程数量才会触发await方法
> - 传入线程数量和一个barrierAction（可以以函数编程直接写），后者你就简单理解为是一个屏障方法，当线程达到数量后会优先执行该方法再去执行await方法
- CyclicBarrier和CountDownLatch的区别

> • CountDownLatch的计数器只能使用一次，而CyclicBarrier的计数器可以使用reset()方法重 置。所以CyclicBarrier能处理更为复杂的业务场景。例如，如果计算发生错误，可以重置计数 器，并让线程重新执行一次。
• CyclicBarrier还提供其他有用的方法，比如getNumberWaiting方法可以获得Cyclic-Barrier 阻塞的线程数量。isBroken()方法用来了解阻塞的线程是否被中断。代码清单8-5执行完之后会 返回true
> 
- 控制并发线程数的Semaphore

> 限制并发流量，比如一条马路要限制流量，只允许同时一百辆车行驶，其他的必须在路口等待，前一百辆会看到绿灯，直接开进去，后面的等待，直到里面出来多少，再进去多少。**所以Semaphore可以用于做流量控制，特别是公用资源有限的应用场景，比如数据库连接。**
> 

> 底层及时AQS那一套，超过限制的线程进去同步队列并自旋检查状态量是否大于0，大于0就结束阻塞继续执行任务，这个状态量会被前面拿到锁执行任务的线程执行特定的通知方法，这里就为release方法使之状态量+1
> 
- 线程间交换数据的Exchanger

> Exchanger（交换者）是一个用于线程间协作的工具类。Exchanger用于进行线程间的数据交 换。它提供一个同步点，在这个同步点，两个线程可以交换彼此的数据。这两个线程通过 exchange方法交换数据，如果第一个线程先执行exchange()方法，它会一直等待第二个线程也 执行exchange方法，当两个线程都到达同步点时，这两个线程就可以交换数据，将本线程生产 出来的数据传递给对方。
> 

> **下面来看一下Exchanger的应用场景**。 Exchanger可以用于遗传算法，遗传算法里需要选出两个人作为交配对象，这时候会交换 两人的数据，并使用交叉规则得出2个交配结果。**Exchanger也可以用于校对工作**，比如我们需 要将纸制银行流水通过人工的方式录入成电子银行流水，为了避免错误，采用AB岗两人进行 录入，录入到Excel之后，系统需要加载这两个Excel，并对两个Excel数据进行校对，看看是否 录入一致
> 

## 7.简单聊一下 CopyOnWriteArrayList

- 概述

> 该类是除了JUC包下除了ConcurrentHashMap外另一个非常重要的并发容器，**他对于并发的读写操作是分离，也就是说，读写操作在同一时间内不会相互堵塞，至于写写会堵塞**，对于读操作是在原容器上全程不加锁，而对于写操作则会拷贝一份原容器，然后在拷贝的上面进行操作，最后**替换**；所以对于`读多写少`的情况性能很好
> 

## 8.ConcurrentSkipListMap

- 概述

> 以跳表来实现的ConcurrentSkipListMap，来保证其有序性
>