# Java集合相关总结（List | Set | Map）

type: Post
status: Published
date: 2022/07/06
summary: 集合体系图
tags: Java
category: 技术栈

# 集合体系图

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image.png)

# List

## 1.ArrayList和Vector的比较

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%201.png)

### 1.ArrayList扩容机制

- ArrayList的字段

> 无参的初始容量（10）、空的共享数组（用于指定容量时给元素数组初始化）、空的默认共享数组（未指定容量时给元素数组初始化）、存放元素的Object数组、size、最大size（int的最大值减8）
> 
- 构造器

> • 指定容量的构造器：如果指定的是0，则会把空的共享数组赋值给他；大于0则直接给元素数组new出来
• 未指定容量的构造器：直接用空的默认共享数组给元素数组赋值
• 传入集合类的构造器：则使用迭代器进行添加
> 
- 核心扩容机制，总共其实就分这么两步：

> • ①.确定现在的容量是否达到扩容阈值；
• ②.然后达到与否选择策略（扩容或不扩容）
> 
- 确定现在的容量是否达到扩容阈值的三个方法

> • ensureCapacity：这个方法会检查传入的新增容量，然后检查是否当前的list是自己传入容量的还是未指定容量的，如果是传入容量的，临时的容量值会设置为0，否则设置为默认的16；然后根据我们传入的新增容量跟这个比较，如果新增的比这个临时容量值要大则进入下一个；**注意这个方法是留给用户调用的，数组内部自己检查长度是用的带有Internal的方法，当我们进行大量操作后且有具体次数，可以在插入前调用此方法来提前进行扩容，而不是大的数据量每到一个扩容阈值都进行扩容**
• ensureCapacityInternal的calculateCapacity：其实这个方法就是对上面的补充，如果是未指定的容量的构造器，则会返回新增的容量和默认容量两个中的最大值；如果不是未指定的则会返回新增容量
• ensureExplicitCapacity：会使新增容量减去当前的元素数组长度，如果新增容量大则触发扩容grow方法
> 
- 添加元素add

> 在add方法中，首先会调用ensureCapacityInternal方法，来进行最小扩容量，即+1；我们需要知道传入grow的参数是多少，这个新增容量的大小，会在当前数组的长度+1和默认大小10之间选择最大的，也就是说我们无参还是有参，在刚开始传入数据时，元素数未达到10，这个新增容量的大小在传入grow方法中的值一直会是10，这个值是由calculateCapacity方法计算出来，然后传入ensureExplicitCapacity方法来进行判断是否进行扩容
> 
- 扩容核心方法grow，传入新增容量的大小

> • 首先获取当前数组的容量
• 新容量 = 当前容量 + 当前容量/2（有符号右移一位），宏观上面就是来说扩容1.5
• 然后回去检查新容量是否已经满足新增的容量，如果满足，则不会进行扩容，新容量会被重新赋值会新增容量的大小（因为10以内的元素数量，在进行右移1位就成0了，就会满足第一个if）
• 如果不满足第一个if：首先去检查新容量是否大于最大容量（第二个if），若超出则会比较新增容量和最大容量的关系（调用hugeCapacity方法），如果新增容量大于最大容量，容量设置为int的最大值；否则设置为最大容量
• 调用copy方法，将新容量传入
> 
- 数组迁移

> 由于底层是数组支持的，那么对于数组的复制迁移来说，源码中大量使用了复制的方法：Arrays.copyOf（传入操作数组，返回内部创建并操作后的一个数组）和system.arraycopy（传入原数组和目标数组已经索引起始等等）
copyOf其实内部调用了system.arraycopy
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%202.png)

- Vector扩容机制

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%203.png)

## 2.LinkedList

### 1.概述

1. LinkedList底层实现了双向链表和双端队列特点
2. 可以添加任意元素（元素可以重复），包括null
3. 线程不安全，没有实现同步

### 2.类的结构

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%204.png)

### 3.ArrayList与LinkedList的比较

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%205.png)

## 3.CopyOnWriteArrayList

- 概述

> `CopyOnWriteArrayList`主要通过**写时复制**使得迭代器遍历该list的情况下，遭到其他线程的修改不会抛出ConcurrentModificationException 异常。但是修改实时性并不是那么强。
> 
- 主要字段

> 有一个ReentrantLock的锁、存放元素的数组
> 
- add方法，不含索引参数的

> 可以很清晰的看到，是加锁进行写操作的
> 

```java
public boolean add(E e) {
       final ReentrantLock lock = this.lock;
       lock.lock();
       try {
           Object[] elements = getArray();
           int len = elements.length;
           Object[] newElements = Arrays.copyOf(elements, len + 1);
           newElements[len] = e;
           setArray(newElements);
           return true;
       } finally {
           lock.unlock();
       }
   }
```

- get方法

> get方法是不加锁直接获取的
> 

# Set

- 概述

> 无序（添加和取出的顺序不一致)，没有索引（即不能用普通for循环遍历）不允许重复元素，所以最多包含一个null虽然取出来的数据与添加的数据顺序不用，但第一次取出以后的顺序在之后是不会变得
> 

## 一、HashSet

### 1.概述

1. HashSet实现了Set接口
2. HashSet实际上是**HashMap**，看下源码（图）

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%206.png)

1. 可以存放null值，**但是只能有一个null**
2. HashSet不保证元素是有序的,取决于经过哈希函数计算过得结果后，再确定索引的结果.
3. 不能有重复元素或对象

### 2.添加过程

- 提示

> 这里十分值得一说底层在对比添加来的对象的索引值的位置上如果已经有元素了，那么底层会分为三种情况进行判断
> 
- 说明

> **这里的equals判断不是传统意义上的比值或比地址，而是可以根据我们程序员自定义的方法规则来比较，例如创建一个person类，其中有三个字段分别是身份证号、姓名、年龄；我们其实可以指定任意两个字段进行比较来使equals返回true或false，也就是说比较的意义在这里是十分宽泛的。相对单调的值判断已经在或运算符前面这个`(k = p.key) == key`进行了判断**
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%207.png)

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%208.png)

### 3.扩容机制

- 注意

> **对于元素添加完成后，底层的元素size()就会+1，无论你是添加到数组索引值的内容为null还是添加到链表后面都算+1。所以就算16个位置只有二个位置有元素（1个比较特殊，1个元素后跟着7各元素就已经开始扩容了），我们严重16个只占了2个，但这个两个元素分别带着8和4个结点，形成两个链表，此时如果再加一个元素，就要超过阈值开始扩容了**
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%209.png)

### 3.1 剪枝

> **就是当形成红黑树的时候，里面的结点越来越少，当小于一定值的时候就会又将红黑树转化为链表**
> 

### 4.LinkedHashSet

### 4.1 概述

1. LinkedHashSet是 HashSet的子类
2. LinkedHashSet 底层是一个 **LinkedHashMap**（而LinkedHashMap又是HashMap的子类），底层维护了一个数组+双向链表
3. LinkedHashSet根据元素的hashCode值来决定元素的存储位置,同时使用链表维护元素的次序，这使得元素看起来是以插入顺序保存的。
4. LinkedHashSet 不允许添重复元素

### 4.2 说明

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2010.png)

### 4.3 注意

由图可以看到，在LinkedHashSet中存放数据的表的类型是HashMap`$`Node，但元素的类型确实LinkedHashMap`$`Entry，**可以根据过往经验表示这两个类型的类绝对是继承关系**

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2011.png)

- 源码

> 可以看到LinkedHashSet的双链表结构也是Entry这个LinkedHashMap的内部类赋予的，然后可以清晰的看到Entry是继承于HashMap`$`Node，**所以当向我们展示这个是什么类型时，会显示为Node（多态！！！！）**
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2012.png)

## 二、TreeSet

### 1.概述

1. TreeSet的底层还是会到TreeMap的各种方法来实现
2. 如果创建treeSet时使用无参构造器创建，那么取数据还是无序的，但注意还是会比较是否重复添加相同的数据

> • **在下图中，系统默认给的这个Comparable的由来就是将你的字符串转成comparable，因为String类型实现了这个接口，然后这时我们就有比较器comparaTo（系统给的Comparable中的方法）方法来比较了**
• **所以这里请注意，如果你传入的这个元素是自定义的对象或什么，并且没有指定比较规则，这时会报错，因为你自定义的对象是没有实现Comparable这个接口的，无论你是第一次添加还是第二次添加，对于的代码区域都有相对应的检查你有无比较器，无论你是系统给的（实现了Comparable接口）还是自定义的**
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2013.png)

1. TreeSet可以实现自定义的排序（扩展较少），因为可以在创建对象时，向构造器中添加一个compare比较器，而且对于你指定的规则，符合此规则能够添加进去的元素只能有一个，第二个相同符合规则的是不能添加进去的
    
    > 比如你制定了按照字符的长度排序，如果有两个长度一致的字符，那么第二个字符就添加不进去
    > 

# Map

## 1.HashMap

- 节点继承关系

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2014.png)

### 1.概述

1. Map与Collection并列存在。用于保存具有映射关系的数据:Key-Value
2. Map中的key 和 value可以是任何引用类型的数据，会封装到HashMap$Node·对象中
3. Map中的key 不允许重复，原因和HashSet一样，前面分析过源码.
4. Map中的value可以重复
5. Map 的key可以为null, value也可以为null，注意key为null,只能有一个，value 为null ,可以多个.
6. key 和 value之间存在单向一对一关系，即通过指定的key 总能找到对应的value
7. 存在相同key添加时，会将原先的value值替换

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2015.png)

1. HashSet一样，不保证映射的顺序，因为底层是以hash表的方式来存储的.
2. HashMap没有实现同步，因此是线程不安全的

### 2.HashMap的存储结构

### Node 节点 & TreeNode节点

- Node节点

> 该节点是HashMap的内部类，实现了Map的内部接口Entry<K,V>，对应有hash值，key，value和next指针
> 

```java
 static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;

        Node(int hash, K key, V value, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }

        public final K getKey()        { return key; }
        public final V getValue()      { return value; }
        public final String toString() { return key + "=" + value; }

        public final int hashCode() {
            return Objects.hashCode(key) ^ Objects.hashCode(value);
        }

        public final V setValue(V newValue) {
            V oldValue = value;
            value = newValue;
            return oldValue;
        }

        public final boolean equals(Object o) {
            if (o == this)
                return true;
            if (o instanceof Map.Entry) {
                Map.Entry<?,?> e = (Map.Entry<?,?>)o;
                if (Objects.equals(key, e.getKey()) &&
                    Objects.equals(value, e.getValue()))
                    return true;
            }
            return false;
        }
    }
```

==为什么重写equals方法时必须重写hashcode方法==：

- TreeNode节点

> 有根节点、左右孩子、前序节点、布尔的值是否为红色节点（初始值为都为黑色？）
> 
- 树形化的条件

> 对于转换成红黑树是需要两个条件，一个是某个桶的链表容量大于等于8，并且整个哈希表的节点（桶的数量）大于64才会进行树形化
> 

> 如果只是链表节点数量大于8了，此时会尝试树形化，其中方法会检查哈希桶的数量，如果不符合条件，只会进行扩容而不会进行树形化，依次来减少哈希冲突
> 

### HashMap的重要字段

- HashMap的字段

> 初始容量（16）、最大容量（限制带参数创建的容量大小，必须是 2 <= 1<<30 的幂。）、负载因子、拉链法链表变红黑树的阈值（8）、红黑树变链表的阈值（6）、最小树形容量（这个容量是对于整个哈希表的为64）、以node为存储单位的哈希桶数组（7以前是entry）、元素的个数、更改或扩容的计数器、临界值（容量*负载因子）超阔会进行扩容
> 

==表变红黑树的阈值为啥是8==：

> 之所要转换成树，就是在查找时间复杂度上从n优化成logn；根据泊松分布的规律来看，随机哈希值对应到哈希桶的期望概率在8的时候就已经很小的，翻译成人话就是在hash算法正常的情况下，链表长度到8的概率已经很小的了所以通常情况下，并没有必要转为红黑树，所以就选择了概率非常小，小于千万分之一概率，也就是长度为8 的概率，把长度 8 作为转化的默认阈值。
> 

==二项分布和泊松分布==：

> 二项式分布就是只有两种结果的概率事件 在执行n次之后 某种结果的分布情况，就是n次伯努利实验，比如抛了n次硬币，k次正面的概率。其没有后效性
> 

> 泊松分布是离散随机分布的一种，通常被使用在估算在 一段特定时间/空间内发生成功事件的数量的概率。我们知道变为树的阈值是8，负载因子是0.75，出现树形的概率是0.00000006，树虽然比链表遍历快，但是树节点的大小却是链表节点的两倍，所以节点较小就树化不太值得，即8是一个空间和时间上的平衡
> 
- 加载因子：默认值为0.75。如果键值对的数量（size）与数组的长度的比值大于阈值，则需要进行扩容操作。

> • 当无线接近于1，节点密度高，链表长，查找效率低
• 当无限接近于0，密度低，链表短，查找效率高
> 
- 构造函数

> • 无参构造，不指定初始值和加载因子
• 有参构造：分为只指定初始值、指定了初始值和加载因子或是传入一个map类的集合
> 

> **当进行传入一个map集合时，构造函数首先会检查是否进行了初始化，如果已经进行初始化里面可能会有节点的，新加入的map可能加不下那么会进行扩容，然后开始一个一个的加节点**
> 

==HashMap的容量为啥是2的次幂==：

> 因为实际存放的地方是桶的索引，hash的值可以不限制，但集体到存储不可能全部存下，所以实际上要通过`“ (n - 1) & hash”`算出哈希桶的索引，也就是对hash值取模，得到的余数即是索引`hash%length`，但是理论上位操作是比取余操作是要快的，我们发现`(n - 1) & hash == hash % n`
> 

> hashmap通过在构造函数中的这个方法 ，来保证表的大小总是2的幂
> 

```java
    /**
     * Returns a power of two size for the given target capacity.
     */
    static final int tableSizeFor(int cap) {
        int n = cap - 1;
        n |= n >>> 1;
        n |= n >>> 2;
        n |= n >>> 4;
        n |= n >>> 8;
        n |= n >>> 16;
        return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
    }
```

- HashMap允许存在null

> hm中能够添加一个key的null和无数个value的null，也就是说可以存储null，你可以把null单独想成一个不特殊的值
> 

### hashmap并发的时候引起死循环（在jdk7及以前）

[参考链接](https://link.csdn.net/?target=https://coolshell.cn/articles/9606.html)

> 由于多线程在操作扩容时，引起的死循环；两个线程在执行扩容操作时，一个线程在执行时突然被终止，另一个线程完成扩容后，终止的线程恢复运行会指向新的引用，然后继续进行扩容操作，这时你就会发现由于当前节点位置和next节点位置因为在新的引用下面被逆置了，那么此时进行扩容操作的指向就会形成死循环
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2016.png)

> 可以看到成环的原因就是索引会发生变化，jdk8以后，使用了尾插法，可以使之不用逆置，当前节点指针和next指针不会发生变化，并且使用两组指针，一组指向高位一组指向低位，高位指向那些reHash后位置会发生变化的，低位指向不会发生变化的，依次进行，不发生逆置
> 

> 上面说的是链表中的节点会怎么操作，如果此节点是树呢，那么会引入双端链表解决死循环的问题
> 

### 3.HashMap主要方法实现

### 确定Hash值 & 定位桶索引

==确定Hash==：

- 为什么 hash 要将高十六位和低十六位异或

> 桶数量很少的时候虽然只有低位在进行运算，但是让高位参与进来可以更好的进行散列，降低冲突，并且高低位的信息也保留了下来
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2017.png)

- 为什么采用异或

> 而在这里采用异或运算而不采用& ，| 运算的原因是 异或运算能更好的保留各部分的特征，如果采用&运算计算出来的值的二进制会向1靠拢，采用|运算计算出来的值的二进制会向0靠拢
> 

==定位桶索引==：
**拿到对应键值对的hash值，会经过这个公式得到桶的索引`(n - 1) & hash`**

```java
int index = (n - 1) & hash
```

### put方法

- 概述

> 进行键值对添加，主要通过`put`方法来调用内部`putVal`方法，通过计算的桶索引如果该位置没有元素那么直接添加，如果有节点就要经过一系列的流程了
> 

> 如果对于桶索引有元素，会首先检查`key`，如果`key`存在那么直接覆盖，如果不存在，会检查当前桶后面跟着的是链表还是红黑树，链表则遍历插入，期间满足树形化的要求会进行树形化；如果是树则进行插入（可能会左旋右旋之类的）；这些操作完后会对表的容量进行检查，满足则进行扩容
> 
- 流程概述

> 先开桶数组是否进行初始化，没有进去resize
检查对应桶数组的索引位置，空就直接插入；
如果是红黑树则进行红黑树的插入过程
如果是链表则要进行遍历，插入到最后，检查总体容量和链表长度看是否满足树形化
> 
> - 找到相同的key则覆盖
> - 添加完最后检查包含键值对的个数是否到达容量阈值，到达则进行 resize()；（这里比JUC的ConcurrentHashMap就是先检查扩容在插入，这里是先插入再扩容容易浪费空间）

```java
    // 调用的put 方法
    public V put(K key, V value) {
        return putVal(hash(key), key, value, false, true);
    }
    // 真正做事的 putVal 方法
    final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                   boolean evict) {
        // 定义一些局部变量
        HashMap.Node<K,V>[] tab; HashMap.Node<K,V> p; int n, i;
        // 判断是否是第一次 put，是否分配过桶数组，没有则进行resize
        if ((tab = table) == null || (n = tab.length) == 0)
            n = (tab = resize()).length;
        // i = (n - 1) & hash 通过该方法计算加入节点的桶下标
        // 如果该下标没有数据，则直接插入
        if ((p = tab[i = (n - 1) & hash]) == null)
            tab[i] = newNode(hash, key, value, null);
        else {
            HashMap.Node<K,V> e; K k;
            // 如果存在相同的 key 则直接覆盖节点
            if (p.hash == hash &&
                    ((k = p.key) == key || (key != null && key.equals(k))))
                e = p;
            // 如果没有相同的并且，该部分已经变成红黑树，则进入红黑树的插入操作
            else if (p instanceof HashMap.TreeNode)
                e = ((HashMap.TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
            // 没有变成红黑树的情况
            else {
                // binCount 代表节点个数，表示遍历节点
                for (int binCount = 0; ; ++binCount) {
                    // 如果下一个是 null 直接插入，代表是尾插
                    if ((e = p.next) == null) {
                        p.next = newNode(hash, key, value, null);
                        // 如果插入后达到树化阈值，则进行树化
                        if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                            treeifyBin(tab, hash);
                        break;
                    }
                    // 如果找到相同的key 则覆盖
                    if (e.hash == hash &&
                            ((k = e.key) == key || (key != null && key.equals(k))))
                        break;
                    p = e;
                }
            }
            // 这主要是帮助 LinkedHashMap 维护一些顺序
            if (e != null) { // existing mapping for key
                V oldValue = e.value;
                if (!onlyIfAbsent || oldValue == null)
                    e.value = value;
                afterNodeAccess(e);
                return oldValue;
            }
        }
        // 内部改动次数 + 1
        // 该值保证出现并发问题的时候出发 fast-fail抛出异常
        ++modCount;
        // 如果尺寸大于容量，则扩容
        if (++size > threshold)
            resize();
        // 该方法同样留给子类做一些操作
        afterNodeInsertion(evict);
        return null;
    }
```

==Hash冲突了怎么办==

1. 开放地址法：向后寻找最近的位置放下
2. 拉链法：正是该HashMap的使用方法
3. 再哈希法：发现冲突，则继续使用下一个哈希函数进行计算，直到放入空闲的位置。
4. 建立公共溢出区：也就是分为一个基础的哈希表和一个溢出区，如果发生哈希冲突则将对应的节点加入到溢出区。

### get方法

> 观察源码，先得到键的哈希值，找对对于桶的索引，如果就这一个节点则直接返回，如果不止一个，则会在树或者链表中找
> 

### resize扩容方法

> 会根据初始容量和负载因子的乘积进行扩容 ，例如初始容量16*0.75=12，也就是说当实际容量来到12就要开始扩容了（resize），扩容会包括rehash，迁移数据等
> 

> 首先会检查当前桶的数量，大于最大值则不进行扩容了并将阈值改为int的最大值，没超过最大值对原来的容量*2；然后对扩容的阈值进行重新计算，然后开始移动桶
> 

> 拿到对应键值对的hash值，会经过这个公式得到桶的索引`(n - 1) & hash`
> 

> 遍历桶，如果桶中有节点，那么判断是否是链表节点还是树的节点，并开始移动，对于移动后新的桶索引会经过`（e.hash & oldCap）`这个公式来计算，如两个节点在hash值上不同，经过计算桶的索引是在一个位置
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2018.png)

> 然后我们进行扩容以后在进行计算桶的索引，可以看到，对于新的位置的差别就是在高位是否是1或0
> 
> - 如果是0可以看到前后的桶索引没变
> - 如果是1就是加上原来容量的16后的值

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2019.png)

> 那么可以通过`（e.hash & oldCap）`看这个公式是否为0，为0就保持不变，不为0就加上原来的容量就是新的桶位置了
> 

```java
    final HashMap.Node<K,V>[] resize() {
        // 先初始化一些数据
        HashMap.Node<K,V>[] oldTab = table;
        int oldCap = (oldTab == null) ? 0 : oldTab.length;
        int oldThr = threshold;
        int newCap, newThr = 0;
        if (oldCap > 0) {
            // 如果旧容量已经超过了最大容量，则设置容纳键值对个数也为最大。
            if (oldCap >= MAXIMUM_CAPACITY) {
                threshold = Integer.MAX_VALUE;
                return oldTab;
            }
            // 如果扩容为原来的两倍小于最大容量，并且原容量大于了初识容量，
            // 则左移一位，扩容为原来的两倍。
            else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                    oldCap >= DEFAULT_INITIAL_CAPACITY)
                newThr = oldThr << 1; // double threshold
        }
        // 如果原容量比0小，但是容纳的键值对不是，则容量改为原来的容纳键值对个数
        else if (oldThr > 0) // initial capacity was placed in threshold
            newCap = oldThr;
        // 否则，初始化为默认容量。
        else {               // zero initial threshold signifies using defaults
            newCap = DEFAULT_INITIAL_CAPACITY;
            newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
        }
        // 初始化新的容纳键值对个数
        if (newThr == 0) {
            float ft = (float)newCap * loadFactor;
            newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                    (int)ft : Integer.MAX_VALUE);
        }
        // 修改容纳键值对的阈值
        threshold = newThr;
        @SuppressWarnings({"rawtypes","unchecked"})
        // 分配新的桶数组
        HashMap.Node<K,V>[] newTab = (HashMap.Node<K,V>[])new HashMap.Node[newCap];
        table = newTab;
        // 如果原先的桶数组不是空的，则需要将旧数据拷贝到新的桶数组中
        if (oldTab != null) {
            // 遍历键值对
            for (int j = 0; j < oldCap; ++j) {
                HashMap.Node<K,V> e;
                if ((e = oldTab[j]) != null) {
                    oldTab[j] = null;
                    // 如果只是单个节点，则直接重新计算索引，放进新的桶数组
                    if (e.next == null)
                        newTab[e.hash & (newCap - 1)] = e;
                    // 如果是树结点，则将红黑树进行拆分，如果确实要树化，在进行树化
                    else if (e instanceof HashMap.TreeNode)
                        ((HashMap.TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                    // 否则将链表插入新的桶数组，并保证顺序
                    else { // preserve order
                        // lo 和 hi 分别为两个链表，用来保存原来一个桶中元素被拆分后的两个链表
                        HashMap.Node<K,V> loHead = null, loTail = null;
                        HashMap.Node<K,V> hiHead = null, hiTail = null;
                        HashMap.Node<K,V> next;
                        /**
                         * 检测节点的高位是否是 1
                         *      是 1 的放入 hi 链表中
                         *      是 0 的放入 lo 链表中
                         */
                        do {
                            next = e.next;
                            // 将哈希值和旧容量取与运算，
                            // 等于 0 代表原先的散列值是数组长度的偶数倍
                            // 所以扩容（2 倍）之后，只需要呆在原地
                            if ((e.hash & oldCap) == 0) {
                                if (loTail == null)
                                    loHead = e;
                                else
                                    loTail.next = e;
                                loTail = e;
                            }
                            // 如果值为1，则说明原先的散列值是数组长度的奇数倍
                            // 所以扩容之后，可以放在一个原先长度之后的位置
                            else {
                                if (hiTail == null)
                                    hiHead = e;
                                else
                                    hiTail.next = e;
                                hiTail = e;
                            }
                        } while ((e = next) != null);
                        // 划分完两个链表之后
                        // lo 链表呆在原来的位置
                        if (loTail != null) {
                            loTail.next = null;
                            newTab[j] = loHead;
                        }
                        // hi 链表加到【当前下标 + 旧容量】的位置
                        if (hiTail != null) {
                            hiTail.next = null;
                            newTab[j + oldCap] = hiHead;
                        }
                    }
                }
            }
        }
        return newTab;
    }
```

### 4.HashMap的遍历方式

> 集合在使用增强for循环遍历的时候，不要在使用add/remove，会导致异常
> 

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2020.png)

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2021.png)

> 大的方向上一共分为四类：
> 
> 1. 迭代器遍历：entrySet或keySet
> 2. for each遍历：entrySet或keySet
> 3. lambda遍历
> 4. 流式遍历：单线程或多线程；当以流的方式创建map的时候要注意key和value都不能为空，会报异常

```java
//使用for循环遍历，当然也可以使用原生迭代器
        for (String s : map.keySet()) {
            System.out.println(s);
            System.out.println(map.get(s));
        }
        for (Map.Entry<String, String> entry : map.entrySet()){
            System.out.println(entry.getKey());
            System.out.println(entry.getValue());
        }

        //Lambda式的遍历
        Collection values = map.values();
        for (Object value : values) {
            System.out.println(value);
        }
        map.forEach((key, value) -> {
            System.out.println(key);
            System.out.println(value);
        });

        //流式遍历
        map.entrySet().stream().forEach((entry) -> {    //单线程
            System.out.println(entry.getValue());
            System.out.println(entry.getKey());
        });

        map.entrySet().parallelStream().forEach((entry) -> {    //多线程
            System.out.println(entry.getKey());
            System.out.println(entry.getValue());
        });
```

- RandomAccess 接口

> 这个接口如果被某个集合实现就等于标识这个实现类是具有随机访问特性的
> 
- comparable 和 Comparator 的区别

> • comparable 接口为lang包下的，需要重写compareTo(Object obj)来完成排序需求，一般用于对象上
• Comparator 接口是util包下的，需要重写compare(Object obj1, Object obj2)来完成排序需求，一般用于集合
> 
- Queue和Deque

> • Queue是单端队列，只能从一端插，另一端删即为FIFO
• Deque就是双端队列，两端都能插和删，Deque扩展了Queue
> 
- 让集合变同步的方法（你要是SB就用这个，不是就直接用JUC）

> 如果你使用的集合不是线程安全的，你可以使用集合工具类来转换，`Collections 提供了多个synchronizedXxx()方法`·，该方法可以将指定集合包装成线程同步的集合，从而解决多线程并发访问集合时的线程安全问题。
> 

## 2.HashTable

### 1.概述

1. 存放的元素是键值对:即 K-V，结构也是数组+链表
2. **hashTable的键和值都不能为null，否则会抛出NullPointerException**

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2022.png)

1. hashTable使用方法基本上和HashMap—样
2. hashTable是线程安全的(synchronized), hashMap是线程不安全的
3. 遇到相同的Key也是会替换Value值
4. 起始大小是11，每次扩容机制如下图，然后临界值（阈值）的也是当前大小容量*0.75，即第一次扩容的阈值为8（超过8）

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2023.png)

### 2.Properties

1. Properties类继承自Hashtable类并且实现了Map接口，也是使用一种键值对的形式来保存数据。
2. 他的使用特点和Hashtable类似
3. Properties还可以用于从 xxx.properties文件中，加载数据到Properties类对象,并进行读取和修改
4. 说明:工作后 XX.properties文件通常作为配置文件

## 3.LinkedHashMap

- 概述

> 继承自hashmap，大致结构是相似的，只不过在某些的功能实现上有自己的特点
> 
- 主要字段

> • LinkedHashMap 的节点类型：在 HashMap 的基础上增加来前后指针，让所有节点形成一条双向链表
• 双向链表的头节点，也就是存在最久的节点
• 双向链表的尾节点，也就是新插入的节点
• 存取顺序，链表的排序规则：**True表示维护访问顺序（所以可以基于此实现一个LRU链表）；False表示维护插入的顺序**
> 
- 初始化方法

> 很简单就是调用了父类的构造器进行初始化，默认维护插入顺序
> 

### 1. 主要方法

### 插入方法

- 概述

> 在该方法中LinkedHashMap实现了自己的构造节点方法：
创建一个自己的包含前后指针的节点，并维护链表的头尾节点的关系。也就是把新加入的节点加入到链表尾部。
> 

```java
// 该下表没有节点的情况
tab[i] = newNode(hash, key, value, null);
// 对应下表是链表的情况
p.next = newNode(hash, key, value, null);
```

- 构建节点方法

```java
    HashMap.Node<K,V> newNode(int hash, K key, V value, HashMap.Node<K,V> e) {
        // 创建一个包含指针的节点
        LinkedHashMap.Entry<K,V> p =
                new LinkedHashMap.Entry<K,V>(hash, key, value, e);
        构造链表的关系
        linkNodeLast(p);
        return p;
    }

    private void linkNodeLast(LinkedHashMap.Entry<K,V> p) {
        LinkedHashMap.Entry<K,V> last = tail;
        tail = p;
        if (last == null)
            head = p;
        else {
            // 将新加入的节点加入到尾部
            p.before = last;
            last.after = p;
        }
    }
```

### 维护链表方法

- 概述

> 继承hashmap的节点，实现了维护链表的方法
> 

```java
    /**
     * 读取节点操作后的维护动作
     *      也就是当 accessOrder 设置为 true 的时候，
     *      会将被访问的节点更新到链表尾部。
     * @param p
     */
    void afterNodeAccess(HashMap.Node<K,V> p) { }

    /**
     * 插入节点后的维护动作
     *      插入一个节点之后，将该节点加到链表的尾部
     * @param evict
     */
    void afterNodeInsertion(boolean evict) { }

    /**
     * 删除节点的维护动作
     *      当一个节点被删除之后，就会在链表中也将该节点删除
     * @param p
     */
    void afterNodeRemoval(HashMap.Node<K,V> p) { }
```

## 4.TreeMap

### 1.概述

1. 与treeSet同理，**当使用无参构造器时取数据还是无序的**
2. 底层存放元素的实际上是entry

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2024.png)

### 2.判断是否添加的底层机制源码

![image.png](Java%E9%9B%86%E5%90%88%E7%9B%B8%E5%85%B3%E6%80%BB%E7%BB%93%EF%BC%88List%20Set%20Map%EF%BC%89/image%2025.png)

1. xxxx$yyyyy

> **表示yyyyy是xxxx的一个内部类**
> 

## 5.ConcurrentHashMap

想要了解可跳转到此[1.7和1.8的区别详解](https://blog.csdn.net/weixin_49258262/article/details/125463257?spm=1001.2014.3001.5502)