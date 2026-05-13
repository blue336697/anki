# Java虚拟机|JVM知识点汇总及简述-＞运行时数据区(堆、方法区)篇（总结自尚硅谷JVM课程）

type: Post
status: Published
date: 2021/09/04
summary: Java栈、堆与方法区的关系图
tags: JVM
category: 虚拟机

## 四、堆（Heap）

### 1.Java栈、堆与方法区的关系图

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image.png)

### 2.堆的核心概述

1. 一个JVM实例只存在一个堆内存，堆也是Java内存管理的核心区域。
2. Java堆区在JVM启动的时候即被创建，其空间大小也就确定了。是JVM管理的最大一块内存空间。
    
    > 堆内存的大小是可以调节的。
    > 
3. 推在**物理上**是可以不连续存储的，但在逻辑上被视为连续
4. 虽然对于堆来说所有线程是共享的，在堆中有一个区域叫做线程私有的缓冲区（ThreadLocal Allocation Buffer，TLAB)，这个区域中是每个线程独一份的
5. "几乎"所有的对象实例以及数组都应该存放在运行时分配的堆上
    
    > **记住无论等号左面有什么关键字，右边new出来的对象实体永远存放在堆中**
    > 
6. 在Java栈中对堆的引用消失后，堆中的对象会根据GC的判断进行垃圾回收
7. 堆是GC执行垃圾回收的重点区域

### 3.堆的内存细分

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%201.png)

JDK8以后堆内存中逻辑上分为：

**年轻代（新生区）+老年代（养老区）+元空间（Metaspace）**

> 注意：**在JDK7以前元空间称为永久代（Permanent generation永久区）**
> 

### 3.1 堆空间相关参数

- 开发中通常会将-Xms和-Xmx两个参数配置相同的值，**其目的是为了能够在java垃圾回收机制清理完堆区后不需要重新分隔计算堆区的大小，从而提高性能。**
- 默认情况下，初始内存大小:物理电脑内存大小/64、最大内存大小:物理电脑内存大小/ 4
- 起始单位为字节（byte）

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%202.png)

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%203.png)

> 注意：**JDK8以后这两个参数只能设置"年轻代和老年代"的内存大小，因为8之后将永久代改为了元空间划分了出去**
> 
- XX:+PrintFLagsInitial :查看所有的参数的默认初始值
- XX:+PrintFLagsFinal:查看所有的参数的最终值（可能会存在修改，不再是初始值）
- XX:NewRatio:配置新生代与老年代在堆结构的占比
- XX:SurvivorRatio:设置新生代中Eden和s0/s1空间的比例
- XX:HandlePromotionFailure:是否设置空间分配担保

> 注意对于HandlePromotionFailure这个参数而言，jdk7参数值（true或false）都不会影响规则，**规则变为只要老年代的连续空间大于新生代对象总大小或者历次晋升的平均大小就会进行Minor GC，否则将进行Full GC。**
> 

### 3.2 获取堆空间（年轻代和老年代）的大小

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%204.png)

```java
	//返回Java虚拟机中的堆内存总量
	long initialMemory = Runtime.getRuntime().totalMemory() / 1024 / 1024;
	//返回ava虚拟机试图使用的最大堆内存量
	long maxMemory = Runtime.getRuntime().maxMemory() / 1024 / 1024;
	system.out.println("-xms : " + initialMemory +"M");
	system.out.println("-xmx : " +maxMemory + "M");

	system.out.println("系统内存大小为:" + initialNemory * 64.0 / 1024 + "G");
	system.out.println("系统内存大小为:" + maxMemory * 4.0 / 1024 +"G");
```

结果如下：

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%205.png)

> 这里from区（S0区）与to区（S1）区单次只能用其一个，两个区是相互传递的，比如说第一次GC后，将存活的对象放入了S0区，第二次GC时就将Eden区的存活对象和S0中的存活对象全部移动到S1区中。其最大的目的就是为了使对象的地址是连续的，防止内存碎片化。
> 

### 4.年轻代与老年代

- 之所以分成年轻代与老年代，就是在堆中有不同生命周期的对象，来对症下药
- 几乎所有的Java对象都是在Eden区被new出来的
- 绝大部分的Java对象的销毁都在新生代进行了。

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%206.png)

### 4.1 年轻代与老年代的大小参数调整(当然一般不会调)

> 配置新生代与老年代在堆结构的占比
**默认**-XX:NewRatio=2，表示新生代占1，老年代占2，新生代占整个堆的1/3
> 

### 4.2 年轻代中（Eden、from、to）大小参数调整

> 同理也是占比
**默认**-XX:SurvivorRatio=8，在HotSpot中，Eden空间和另外两个survivor空间缺省所占的比例是8:1:1
但注意，JVM中有**自适应机制**，在设置最大堆空间为600M的前提下，这个比例为6:1:1，所以需要8:1:1的时候我们需要自己显式的加上-XX:SurvivorRatio=8这个参数
> 

### 5.对象分配内存过程详解

1. 首先对象创建进入新生代的伊甸园区，**当存满时用户线程停止**
2. YGC/Minor GC垃圾回收线程启动开始**判断哪些对象销毁，那些对象需要进入S0或S1区**
3. 当有对象进入S0或S1时，自身带有**年龄计数器从0变为1**

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%207.png)

1. 在不断的放置对象中，伊甸园区又满了，同理触发垃圾回收线程
2. **在伊甸园中还有要使用的对象，但同时S0中的对象也要使用**，此时垃圾回收线程将三者全部**移动到S1中**
3. 各自对象的年龄计数器分别进行**加一**

> 注意：S0和S1区的别名为from和to区，起名生动形象的说明对象的移动过程，**但from和to是相对概念即谁空往谁处移动，谁空谁是to**
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%208.png)

1. 当又又又伊甸园区又满时，垃圾回收线程开始工作
2. S0与S1开始移动，年龄计数器加一
3. 但此时注意S1区已经有两个对象的年龄计数器已经到15(**默认**)了，**当到达15时我们说此时为一个阈值，要转移到老年代中了，即"晋升"**

> 但注意此时JVM还有动态对象年龄的判断，当在幸存者区中对象的大小已经
> 
> 
> **大于**
> 
> **此时计算年龄的平均值，大于等于这个平均值的直接放到老年代中**
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%209.png)
> 

### 5.1 注意

> • YGC/Minor GC垃圾回收线程的触发条件：**只有当伊甸园区满时，其他任何区域满时都不会触发**
• 关于垃圾回收，频繁在新生区收集，很少在养老区收集，几乎不在永久区（元空间）收集。
• 关于对象寿命，80%符合在伊甸园区“朝生夕死”
> 

### 5.2 图示步骤（有特殊情况展示）

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2010.png)

> 特殊情况：对象大到一开始就在新生代中放不下，然后直接放到老年代
> 

### 6.MinorGC、MajorGC和FullGC的对比（对于HotSpot）

- JVM在进行GC时，并非每次都对上面三个内存(新生代、老年代;方法区)区域一起回收的，大部分时候回收的都是指新生代。针对HotSpot VM的实现，它里面的GC按照回收区域又分为两大种类型
1. 部分收集:不是完整收集整个Java堆的垃圾收集。其中又分为:

> 新生代收集（Minor GC / Young GC）:只是新生代（Eden\s0,s1）的垃圾收集
> 

> 老年代收集（Major GC / Old GC）:只是老年代的垃圾收集。
> 
> - 目前，只有CMSGC会有单独收集老年代的行为。
> - 注意，很多时候Major GC会和Full Gc混淆使用，需要具体分辨是老年代回收还是整堆回收。

> 混合收集（Mixed GC):收集整个新生代以及部分老年代的垃圾收集。目前，只有G1 GC会有这种行为
> 
1. 一种是整堆收集（Full GC）

> 整堆收集（Full GC)：**收集整个java堆和方法区的垃圾收集。**
> 

### 6.1 MinorGC / Young GC触发机制

- 当年轻代空间不足时，就会触发Minor GC，这里的年轻代满指的是**伊甸园代满**，Survivor（S0、S1）满不会引发GC。（每次Minor GC会清理年轻代的内存)
- 因为ava 对象大多都具备**朝生夕灭**的特性，所以Minor GC非常频繁，一般回收速度也比较快。这一定义既清晰又易于理解。
- Minor GC会引发STW，暂停其它用户的线程，等垃圾回收结束，用户线程才恢复运行。

### 6.2 Major GC / Old GC触发机制

- 在老年代空间不足时，**会先尝试触发一次Minor GC**。如果之后空间还不则触发Major GC
- Major GC的速度一般会比Minor GC慢10倍以上，STW的时间更长。
- 如果Major GC后，内存还不足，就报OOM了。
- Major Gc的速度一般会比Minor GC慢10倍以上。

### 6.3 Full GC触发机制

> 总的来说就是方法区或老年代空间不足。
注意：**full gc是开发或调优中尽量要避免的。这样暂时时间会短一些.**
> 

### 7.TLAB（Thread Local Allocation Buffer）及对象分配过程图解

> • 我们知道堆在多线程中是共享的，但在并发下面多个线程对对象的访问时线程不安全的，但如果加锁又会影响对象分配内存的速度
• 所以我们提出TLAB即**快速分配策略**，就是在**年轻代的伊甸园区**中给每个线程划分一个私有的**缓冲区域**来优化对象分配内存速度效率，**此区域仅占整个伊甸园的百分之1**
• **默认情况是开启的即Use前面是+**，参数为-XX:+UseTLAB
• 一旦对象在TLAB空间分配内存**失败(就是放不下)时，JVM就会尝试着通过使用加锁机制确保数据操作的原子性**，从而直接在Eden空间中分配内存。
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2011.png)

### 8.关于面试

### 8.1 举例常见异常

> 在面试中，面试官常常问异常的问题，在这里的异常常常指的是广义的异常，即不能让程序正常运行下去的异常，所以我们一般都将**Java中的错误和异常都说出来**
> 

### 8.2 堆空间分代的原因

> 就是为了优化GC的性能才分代，不然就是全部对象都在一起无法**因材施教**
> 

### 8.3 堆空间一定是共享的吗

> 很显然不是，因为有TLAB的存在
> 

### 8.4 堆是分配对象的唯一选择吗

> 随着Java的发展，越来越多的优化技术出现，典型的就是**逃逸分析（默认打开）**。但目前来说逃逸分析还不成熟，我们保守的回答这个问题：**对象实例还是全都分配在堆上**
> 

### 8.4.1 逃逸分析

> 通过让未发生逃逸的对象直接在栈上分配内存（因为栈天然具有出栈进栈的特性）以此来降低GC的频率
> 

> 如何快速的判断是否发生了逃逸分析，就看**new的对象实体**是否有可能在方法外被调用。
> 

```java
//以下两端代码就是典型的将逃逸对象转化为不逃逸对象

public static stringBuffer createstringBuffer(string s1，strings2){
	stringBuffer sb = new stringBuffer () ;
	sb.append(s1);
	sb.append(s2);
	return sb;
}

public static string createstringBuffer(string s1，String s2){
	stringBuffer sb = new stringBuffer();
	sb.append(s1);
	sb.append(s2);
	return sb.toString() ;
}
```

### 8.4.2 逃逸分析之代码优化

1. 对于未发生逃逸的对象进行**栈上分配**

> 在逃逸分析中，典型的逃逸分别是给**成员变量赋值、方法返回值、实例引用传递**。
> 
1. 对于在动态编译同步块的时候，JIT编译器可以借助逃逸分析来判断同步块所使用的锁对象是否只能够被一个线程访问而没有被发布到其他线程。如果没有那么jvm自动取消这个锁，称为**同步省略**也称“**锁消除**”

```java
//优化前
public void f(){
	Object hollis = new Object ( );
	synchronized (hollis){
		System.Out.Println (hollis) ;
	}
}
//优化后
public void f(){
	object hollis = new Object();
	System.Out.Println (hollis) ;
}
```

1. **标量替换**（默认JVM打开）

> 将聚合量（对象）分解成标量（属性）
> 

### 8.4.3 逃逸分析总结

> 经过逃逸分析优化过后**时间明显缩短**，但逃逸分析这项技术还不成熟
> 

## 五、方法区

### 1.栈、堆、方法区（元空间）之间的交互

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2012.png)

- Person这个类的结构体全部放到方法区中
- person这个**局部变量**引用放到虚拟机栈的局部变量表中
    
    > **如果是成员变量则随着对象实体存放到Java堆当中**
    > 
- new Person()这个对象实体放到堆中

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2013.png)

### 2.方法区（永久代）详述

1. 前面提到JDK8以后堆内存中逻辑上分为：**年轻代（新生区）+老年代（养老区）+方法区**，但实际上我们会将方法区看作是**一块独立于Java堆的内存空间**
2. 方法区（Method Area）与Java堆一样，是各个线程共享的内存区域。
3. 方法区在JVM启动的时候被创建，并且它的实际的物理内存空间中和Java堆区一样都可以是不连续的。
4. 方法区的大小，跟堆空间一样，可以选择固定大小或者可扩展。
5. 方法区的大小决定了系统可以保存多少个类，如果系统定义了太多的类，导致方法区溢出，虚拟机同样会抛出内存溢出错误: java.lang.outOfMemoryError:PermGen space（JDK7及以前）或者java.lang.outOfMemoryError: Metaspace（JDK8及以后）
    
    > 加载大量的第三方的jar包、Tomcat部署的工程过多（30-50个）、大量动态的生成反射类
    > 
6. 关闭JVM就会释放这个区域的内存。
7. 将永久代改为元空间以后**元空间不在虚拟机设置的内存中，而是使用本地内存。**

### 3.方法区大小参数设置

### 3.1 JDK7及以前

- XX:PermSize来设置永久代初始分配空间。默认值是20.75M
- XX:MaxPermSize来设定永久代最大可分配空间。32位机器默认是64M，64位机器模式是82M
- 当JVM加载的类信息容量超过了这个值，会报异常OutOfMemoryError:PermGen space

### 3.2 JDK8及以后

- XX:MetaspaceSize来设置永久代初始分配空间，window下默认值时**21M**
- XX:MaxMetaspaceSize来设定永久代最大可分配空间，**默认值为-1**，即没有限制

### 3.3 修改默认值

> -XX:Metaspacesize=100m 初始
-XX:MaxMetaspacesize=100m 最大
> 

### 3.4 修改建议

> 为了避免频繁的触发Full GC，我们可以将Metaspacesize值调的稍微高一点，MaxMetaspacesize的值就可以不用动了
> 

### 4.方法区的内部结构

### 4.1 方法区到底存放什么

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2014.png)

它用于存储已被虚拟机加载的**类型信息、常量、静态变量、即时编译器编译后的代码缓存**等

> 注意：当然会有例外！
> 

### 4.2 运行时常量池

- 方法区内部包含了**运行时常量池**

> 字节码文件中包含了**常量池**，当字节码文件被类加载器加载后，在运行时数据区中的方法区中，**常量池就变为了运行时常量池**
> 
- 常量池中的**符号引用**————>运行时常量池的**直接引用**
- 运行时常量池体现出一定的**动态性**，会将一些类的结构或引用**进行补充在添加**

### 4.2.1 字节码文件结构

- 都是一个有效的字节码文件中除了包含类的版本信息、字段、方法以及接口等描述信息外，还包含-项信息那就是常量池表(ConstantPoolTable)，包括各种字面量（String类型的值）和对类型、域和方法的符号引用。

### 4.2.2 为什么需要常量池

- 为了避免每次都要加载实际重复使用的类架构和节省内存，所以我们将这个常用的类结构（**类名、方法名、参数列表和字面量等**）在常量池中以符号引用的方式存储起来，等运行时通过符号引用转换为直接引用类的结构

> 图中的红框都是符号引用的代号，对应到常量池里的代号就是相关的类结构了
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2015.png)

### 4.3 方法区的演进细节（⭐）

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2016.png)

> JDK6.7.8演进对比
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2017.png)

### 4.3.1 永久代为什么会被元空间替代

> 我的理解就是为了优化GC触发的次数，永久代期间使用的时虚拟内存很容易造成空间溢出OOM的错误，而改为元空间后使用了本地内存，OOM的错误出现次数减少，优化GC线程占用用户线程的时间，试进程运行效率提高
> 

### 4.3.2 String Table为什么要调整

> 从永久代放到堆区，一是因为永久代的默认大小比较小，二是因为永久代的GC频率很低，因为触发Full GC才会回收永久代的东西，而Full GC实在永久代或老年代不足时才会触发，这就导致String Table回收效率太低，而String类型又是我们很常用的一个类型，很容易导致内存不足，所以我们放到了堆中及时回收
> 

### 5.方法区的垃圾回收

> • 一般来说这个区域的回收效果比较**难令人满意**，尤其是类型的卸载，条件相当苛刻。但是这部分区域的回收有时又确实是必要的。
• 方法区的垃圾收集主要回收两部分内容：**常量池中废弃的常量和不再使用的类型**。
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E8%BF%90%E8%A1%8C%E6%97%B6%E6%95%B0%E6%8D%AE%E5%8C%BA(%E5%A0%86%E3%80%81%E6%96%B9%E6%B3%95%E5%8C%BA)%E7%AF%87%EF%BC%88%E6%80%BB%E7%BB%93%E8%87%AA%E5%B0%9A%E7%A1%85%E8%B0%B7JVM%E8%AF%BE%E7%A8%8B%EF%BC%89/image%2018.png)