# Java虚拟机|JVM知识点汇总及简述-＞JVM运行时参数及如何分析GC日志

type: Post
status: Published
date: 2021/09/12
summary: JVM参数选项类型
tags: JVM
category: 虚拟机

# JVM运行时参数

## 一、JVM参数选项类型

### 1.类型一：标准参数选项

- 特点

> 比较稳定，后续版本基本不会出现变化**以-开头**
> 

### 1.1 各种选项（通过运行java -help是可以看到这些参数的）

- disableassertions[ `:<packagename> ... | :<classname>`]：禁用具有指定粒度的断言
- esa / -enablesystemassertions：启用系统断言
- dsa | -disablesystemassertions：禁用系统断言
- agentlib:`<libname>`[=<选项>]：加载本机代理库`<libname>`，例如-agentlib:hprof；另请参阅-agentlib:jdwp=help和-agentlib:hprof=help
- agentpath: `<pathname>`[=<选项>]：按完整路径名加载本机代理库
- javaagent:`<jarpath>`[=<选项>]：加载Java 编程语言代理,请参阅java.lang.instrument
- splash: `<imagepath>`：使用指定的图像显示启动屏幕

### 1.2 补充内容

Hotspot JVM有两种模式，分别是server和client，分别通过-server和-client模式设置

> 在32位Windows系统上，默认使用client类型的JVM。要想使用Server模式，则机器配置至少有2个以上的CPU和2G以上的物理内存。client模式适用于对内存要求较小的桌面应用程序，默认使用Serial串行垃圾收集器64位机器上只支持server模式的JVM，适于需要大内存的应用程序，默认使用并行垃圾收集器
> 

### 2.类型二：-X参数选项

- 特点

> 非标准化参数功能还是比较稳定的。但官方说后续版本可能会变更**以-X开头**
> 

### 2.1 各种选项（通过Java -X命令可以看到所有的X选项）

### 2.2 JVM的JIT编译模式相关的选项

- Xint：禁用JIT，所有字节码都被解释执行，这个模式的速度最慢的
- Xcomp：所有字节码第一次使用就都被编译成本地代码，然后再执行
- Xmixed：混合模式，默认模式，让JIT根据程序运行的情况，有选择地将某些热点代码进行预留提高速度

### 2.3 特别注意

- **Xmx -Xms -Xss属于XX参数！！**

> • -Xms`<size>`：设置初始Java堆大小，等价于-XX:InitialHeapSize
• -Xmx`<size>`：设置最大Java堆大小，等价于-XX:MaxHeapSize
• -Xss`<size>`：设置Java线程堆栈大小，-XX:ThreadStackSize
> 

### 3.类型三：-XX参数选项

- 特点：

> 非标准化参数使用的最多的参数类型这类选项属于实验性，不稳定**以-XX开头**
> 
- 作用：用于开发和调试JVM

### 3.1 分类

1. Boolean类型格式（说明:因为有的指令默认是开启的，所以可以使用-关闭）

> • -XX:+`<option>`表示启用option属性
• -XX:-`<option>`表示禁用option属性
> 
> 
> 举例：
> 
> > • -XX：+UseParalle1GC选择垃圾收集器为并行收集器
> • -XX：+UseG1GC表示启用G1收集器
> • -XX：+UseAdaptiveSizePolicy自动选择年轻代区大小和相应的Survivor区比例
> > 
1. 非Boolean类型格式（key-value类型）

> • 子类型1：数值型格式-XX:`<option>=<number>`
• 子类型2：非数值型格式-XX:`<name>=<string>`
> 

### 3.2 特别参数

- XX:+PrintFlagsFinal
- 输出所有参数的名称和默认值
- 默认不包括Diagnostic和Experimental的参数
- 可以配合-XX:+UnlockDiagnosticVMOptions和-XX:UnlockExperimentalVMOptions使用

## 二、添加JVM参数选项

- Eclipse
- IDEA
- 运行jar包

> java -Xms50m -Xmx50m -XX:+PrintGCDetails -XX:+PrintGCTimeStamps -jar xxxxx.jar
> 
- 通过Tomcat运行war包

> • Linux系统下可以在tomcat/bin/catalina.sh中添加类似如下配置：JAVA_OPTS=" -Xms512M -Xm×1024M"
• windows系统下在catalina.bat中添加类似如下配置：set "JAVA_OPTS=-Xms512M -Xmx1024M”
> 
- 程序运行过程中

> • 使用jinfo -flag `<name> = <value> <pid>`设置非Boolean类型参数
• 使用jinfo -flag[+|-]`<name> <pid>`设置Boolean类型参数
> 

## 三、常用的JVM参数选项

### 1.打印设置的XX选项及值

- XX:+PrintCommandLineFlags：可以让在程序运行前打印出用户手动设置或者JVM自动设置的XX选项
- XX:+PrintFlagsInitial：表示打印出所有XX选项的默认值
- XX:+PrintFlagsFinal：表示打印出XX选项在运行程序时生效的值（在参数值等于号前面如果有冒号就等于这个参数被我们修改过）
- XX:+PrintVMOptions：打印JVM的参数

### 2.堆、栈、方法区等内存大小设置

### 2.1 堆

- Xms3550m：等价于-XX:InitialHeapSize，设置JVM初始堆内存为3550M
- Xmx3550m：等价于-XX:MaxHeapSize，设置JVM最大堆内存为3550M
- Xmn2g：设置年轻代大小为2G，官方推荐配置为整个堆大小的3/8
- XX:NewSize=1024m：设置年轻代初始值为1024M
- XX:MaxNewSize=1024m：设置年轻代最大值为1024M
- XX:SurvivorRatio=8：设置年轻代中Eden区与一个Survivor区的比值，默认为8即Eden区占8/10
- XX:+UseAdaptiveSizePolicy：**自动选择各区大小比例，比如说-XX:SurvivorRatio这个参数是8，但此参数的开启还会根据你的实际分配内存大小做出相对应的调整，但如果你就是想要设置自定义，你必须显式的对-XX:SurvivorRatio进行赋值修改或关闭此自动分配参数**
- XX:NewRatio=4：设置老年代与年轻代（包括1个Eden和2个Survivor区)的比值即四份是老年代，一份是新生代。默认值是2
- XX:PretenuresizeThreadshold=1024：设置让大于此阈值的对象直接分配在老年代，单位为字节，只对Serial、ParNew收集器有效
- XX:MaxTenuringThreshold=15：默认值为15，新生代每次MinorGC后，还存活的对象年龄+1，当对象的年龄大于设置的这个值时就进入老年代
- XX:+PrintTenuringDistribution：让JVM在每次MinorGC后打印出当前使用的Survivor中对象的年龄分布
- XX:TargetSurvivorRatio：表示MinorGc结束后Survivor区域中占用空间的期望比例

### 2.2 栈

- Xss128k：设置每个线程的栈大小为128k，等价于 -XX:ThreadStackSize=128k

### 2.3 方法区

永久代（JDK7及以前）：

> • -XX:PermSize=256m：设置永久代初始值为256M
• -XX:MaxPermsize=256m：设置永久代最大值为256M
> 

元空间（JDK8及以后）：

> • -XX:MetaspaceSize：初始空间大小
• -XX:MaxMetaspaceSize：最大空间，默认没有限制
• -XX:+UseCompressedOops：压缩对象指针
• -XX:+UseCompressedClassPointers：压缩类指针
• -XX:CompressedClassSpaceSize：设置Klass Metaspace的大小，默认1G
> 

### 2.4 直接内存

- XX:MaxDirectMemorySize：指定DirectMemory容量，若未指定，则默认与Java堆最大值一样

### 3.OutofMemory相关的选项

- XX:+HeapDumpOnOutOfMemoryError表示在内存出现OOM的时候，把Heap转存(Dump)到文件以便后续分析
- XX:+HeapDumpBeforeFullGC：表示在出现FullGC之前，生成Heap转储文件
- XX:HeapDumpPath= `<path>`：指定heap转存文件的存储路径
- XX:OnOutOfMemoryError：指定一个可行性程序或者脚本的路径，当发生OOM的时候，去执行这个脚本。运维常用

### 4.垃圾收集器相关选项

### 4.1 查看默认垃圾收集器

- XX:+PrintCommandLineFlags:查看命令行相关参数（包含使用的垃圾收集器)
- 使用命令行指令:jinfo - flag相关垃圾回收器参数进程ID

### 4.2 Serial回收器

- Serial收集器作为HotSpot中client模式下的默认新生代垃圾收集器。Serial old是运行在Client模式下默认的老年代的垃圾回收器。
- XX:+UseSerialGC：指定年轻代和老年代都使用串行收集器。等价于新生代用Serial Gc，且老年代用Serial old GC。可以获得最高的单线程收集效率。

### 4.3 ParNew回收器

- XX:+UseParNewGC：手动指定使用ParNew收集器执行内存回收任务。它表示年轻代使用并行收集器，不影响老年代。
- XX:ParallelGCThreads=N：限制线程数量，默认开启和CPU数据相同的线程数。

### 4.4 Parallel回收器

- XX:+UseParallelGC：手动指定年轻代使用Parallel并行收集器执行内存回收任务。
- XX:+UseParallelOldGC：手动指定老年代都是使用并行回收收集器。
    
    > 分别适用于新生代和老年代。默认jdk8是开启的。上面两个参数，默认开启一个，另一个也会被开启。（互相激活）
    > 
- XX:ParallelGCThreads 设置年轻代并行收集器的线程数。一般地，最好与CPU数量相等，以避免过多的线程数影响垃圾收集性能。
    
    > ◦ 在默认情况下，当CPU 数量小于8个，ParallelGCThreads的值等于CPU 数量。
        ◦ 当CPU数量大于8个，ParallelGCThreads的值等于3+[5*CPU_Count]/8]。
    > 
- XX:MaxGCPauseMillis 设置垃圾收集器最大停顿时间(即STw的时间)。单位是毫秒。
    
    > ◦ 为了尽可能地把停顿时间控制在MaxGCPauseMills以内，收集器在工作时会调整Java堆大小或者其他一些参数。
        ◦ 对于用户来讲，停顿时间越短体验越好。但是在服务器端，我们注重高并发，整体的吞吐量。所以服务器端适合Paralle1，进行控制。
        ◦ **该参数使用需谨慎。**
    > 
- XX:GCTimeRatio 垃圾收集时间占总时间的比例(= 1 / (N + 1))。用于衡量吞吐量的大小。
    
    > ◦ 取值范围（0,100）。默认值99，也就是垃圾回收时间不超过1%。
        ◦ 与前一个-XX:MaxGCPauseMillis参数有一定矛盾性。暂停时间越长，Radio参数就容易超过设定的比例。
    > 
- XX:+UseAdaptiveSizePolicy设置Parallel Scavenge收集器具有自适应调节策略
    
    > ◦ 在这种模式下，年轻代的大小、Eden和Survivor的比例、晋升老年代的对象年龄等参数会被自动调整，已达到在堆大小、吞吐量和停顿时间之间的平衡点。
        ◦ 在手动调优比较困难的场合，可以直接使用这种自适应的方式，仅指定虚拟机的最大堆、月标的吞吐量(GCTimeRatio）和停顿时间（MaxGCPauseMills），让虚拟机自己完成调优工作
    > 

### 4.5 CMS回收器

- XX:+UseConcMarkSweepGC：手动指定使用CMS 收集器执行内存回收任务。
    
    > 开启该参数后会自动将-XX:+UseParNewGC打开。即:ParNew(Young区用)+CMS(Old区用)+Serial Old的组合。
    > 
- XX:CMS1nitiating0ccupanyFraction：设置堆内存使用率的阙值，一旦达到该阈值，便开始进行回收。
    
    > ◦ JDK5及以前版本的默认值为68,即当老年代的空间使用率达到68%时，会执行一次CNS回收。JDK6及以上版本默认值为92%
        ◦ 如果内存增长缓慢，则可以设置一个稍大的值，大的阙值可以有效降低CMS的触发频率，减少老年代回收的次数可以较为明显地改善应用程序性能。反之，如果应用程序内存使用率增长很快，则应该降低这个阙值，以避免频繁触发老年代串行收集器。因此通过该选项便可以有效降低Full GC的执行次数。
    > 
- XX:+UseCMSCompactAtFullCollection：用于指定在执行完Full GC后对内存空间进行压缩整理，以此避免内存碎片的产生。不过由于内存压缩整理过程无法并发执行，所带来的问题就是停顿时间变得更长了。
- XX:CMSFullGCsBeforeCompaction：设置在执行多少次Full GC后对内存空间进行压缩整理。
- XX: Paralle1cMSThreads：设置CMS的线程数量。
    
    > CNS 默认启动的线程数是（ParallelGCThreads+3)/4，ParallelGCThreads是年轮代并行收集器的线程数。当CPU 资源比较紧张时，受到CNS收集器线程的影响，应用程序的性能在
    > 

### 4.5.1 补充参数

> • -XX:ConcGCThreads：设置并发垃圾收集的线程数，默认该值是基于ParallelGCThreads计算出来的;
• -XX:+UseCMSInitiating0ccupancyOnly：是否动态可调，用这个参数可以使CNS一直按CMSInitiatingoccupancyFraction设定的值启动
• -XX:+CMSScavengeBeforeRemark：强制hotspot虚拟机在cms remark阶段之前做一次minor gc，用于提高remark阶段的速度;
• -XX:+CISClassUnloadingEnable：如果有的话，启用回收Perm 区(JDK8之前)
• -XX:+CNSParallelInitialEnabled：用于开启CNS initial-mark阶段采用多线程的方式进行标记，用于提高标记速度，在Java8开始已经默认开启;
• -XX:+CNSParallelRemarkEnabled：用户开启CNS remark阶段采用多线程的方式进行重新标记，默认开启;
• -XX:+ExplicitGCInvokesConcurrent 、-XX:+ExplicitGCInvokesConcurrentAndUnloadsClasses：这两个参数用户指定hotspot虚拟在执行System.gc()时使用CMS周期;
• -XX;+CMSPrecleaningEnabled：指定CMS是否需要进行Pre cleaning这个阶段
> 

### 4.5.2 特别说明

> • JDK9新特性:CMS被标记为Deprecate了(JEP291)：如果对JDK9及以上版本的HotSpot虚拟机使用参数-XX:
+UseConcMarkSweepGC来开启CMS收集器的话，用户会收到一个警告信息，提示CMS未来将会被废弃。
• JDK14新特性:删除CMS垃圾回收器(EP363)：移除了CMS垃圾收集器，如果在JDK14中使用-xX:+UseConcMarkSweepGC的话，JVM不会报错，只是给出一个warning信息，但是不会exit。JVM会自动回退以默认GC方式启动TVM
> 

### 4.6 G1回收器

- XX:+UseG1GC：手动指定使用G1收集器执行内存回收任务。
- XX:G1HeapRegionSize：设置每个Region的大小。值是2的幂，范围是1MB到32NB之间，目标是根据最小的Java堆大小划分出约2048个区域。默认是堆内存的1/200日。
- XX:MaxGCPauseMillis：设置期望达到的最大Gc停顿时间指标(JVM会尽力实现，但不保证达到)。默认值是200ms
- XX:Paralle1GCThread：设置STW时Gc线程数的值。最多设置为8
- XX:ConcGCThreads：设置并发标记的线程数。将n设置为并行垃圾回收线程数(ParallelGCThreads)的1/4左右。
- XX:InitiatingHeapOccupancyPercent：设置触发并发GC周期的Java堆占用率阈值。超过此值，就触发Gc。默认值是45。
- XX:G1NewSizePercent、-XX:G1MaxNewSizePercent：新生代占用整个堆内存的最小百分比（默认5%)、最大百分比（默认60%)
- XX:G1ReservePercent=10：保留内存区域，防止 to space ( Survivor中的to区）溢出

### 4.6.1 Mixed GC调优参数

注意:G1收集器主要涉及到Mixed GC，Mixed GC会回收young区和部分old区。

- XX:InitiatingHeap0ccupancyPercent：设置堆占用率的百分比（0到100）达到这个数值的时候触发global concurrent marking（全局并发标记），默认为45%。值为0表示间断进行全局并发标记。
- XX:G1MixedGCLiveThresholdPercent：设置old区的region被回收时候的对象占比，默认占用率为85%。只有o1d区的region中存活的对象占用达到了这个百分比，才会在Mixed GC中被回收。
- XX:G1HeapwastePercent：在global concurrent marking（全局并发标记)结束之后，可以知道所有的区有多少空间要被回收，在每次young GC之后和再次发生Mixed Gc之前，会检查垃圾占比是否达到此参数，只有达到了，下次才会发生Mixed GC。
- XX:G1MixedGCCountTarget：一次global concurrent marking（全局并发标记）之后，最多执行Mixed GC的次数，默认是8。
- XX:G10ldCSetRegionThresholdPercent：设置Mixed GC收集周期中要收集的old region数的上限。默认值是Java堆的10%

### 4.7 怎么选择垃圾回收器

- 优先调整堆的大小让JVM自适应完成。
- 如果内存小于100M，使用串行收集器
- 如果是单核、单机程序，并且没有停顿时间的要求，串行收集器
- 如果是多CPU、需要高吞吐量、允许停顿时间超过1秒，选择并行或者JVM自己选择
- 如果是多CPU、追求低停顿时间，需快速响应（比如延迟不能超过1秒，如互联网应用），使用并发收集器。官方推荐G1，性能高。现在互联网的项目，基本都是使用G1。
- 没有最好的收集器，更没有万能的收集；调优永远是针对特定场景、特定需求，不存在一劳永逸的收集器

### 5.GC日志相关选项

### 5.1 常用参数

- verbose:gc：可以独立使用，输出gc日志信息，默认输出到标准输出
- XX:+PrintGC：等同于-verbose:gc，表示打开简化的GC日志
- XX:+PrintGCDetails：可以独立使用，在发生垃圾回收时打印内存回收详细的日志，并在进程退出时输出当前内存各区域分配情况可以独立使用
- XX:+PrintGCTimeStamps：输出GC发生时的时间戳
- XX:+PrintGCDateStamps：输出GC发生时的时间戳(以日期的形式，如2013-05-04T21:53:59.234+0800)
- XX:+PrintHeapAtGC：每一次GC前和GC后，都打印堆信息
- Xloggc:`<file>`：把GC日志写入到一个文件中去,而不是打印到标准输出中

### 5.2 其他参数

- XX:+TraceClassLoading：监控类的加载
- XX:+PrintGCApplicationStoppedTime：打印GC时线程的停顿时间
- XX:+PrintGCApplicationConcurrentTime：垃圾收集之前打印出应用未中断的执行时间
- XX:+PrintReferenceGC：记录回收了多少种不同引用类型的引用
- XX:+PrintTenuringDistribution：让JVM在每次MinorGC后打印出当前使用的Survivor中对象的年龄分布
- XX:+UseGCLogFileRotation：启用GC日志文件的自动转储
- XX:NumberOfGClogFiles=1：GC日志文件的循环数目
- XX:GCLogFileSize=1M：控制GC日志文件的大小

### 6.其他参数

- XX:+DisableExplicitGC：禁止hotspot执行Systerm.gc()，默认禁用
- XX:ReservedCodeCacheSize=`<n>`[g|m|k]、-XX:InitialCodeCacheSize=`<n>`[g|m|k]：指定代码缓存的大小
- XX:+UseCodeCacheFlushing：使用该参数让jvm放弃一些被编译的代码，避免代码缓存被占满时VM切换到interpreted-only的情况
- XX:+DoEscapeAnalysis：开启逃逸分析
- XX:一UseBiasedLocking：开启偏向锁
- XX:+UseLargePages：开启使用大页面
- XX:+UseTLAB：使用TLAB，默认打开
- XX:+PrintTLAB：打印TLAB的使用情况
- XX:TLABSize：设置TLAB大小

# 分析GC日志

## 一、GC日志格式

### 1.复习：GC分类

1. 部分收集:不是完整收集整个Java堆的垃圾收集。其中又分为:
    
    > ◦ 新生代收集（Minor GC / Young GC）:只是新生代(Eden\S0,s1）的垃圾收集
        ◦ 老年代收集（Major Gc / old Gc）:只是老年代的垃圾收集。
    `目前，只有CMS GC会有单独收集老年代的行为。注意，很多时候Major GC会和Full GC混淆使用，需要具体分辨是老年代回收还是整堆回收。`
        ◦ 混合收集（Mixed GC):收集整个新生代以及部分老年代的垃圾收集。
    `目前,只有G1 GC会有这种行为`
    > 
2. 整堆收集（Full GC):收集整个java堆和方法区的垃圾收集。

### 2.GC日志分类

### 2.1 MinorGC

### 2.2 FullGC

### 3.GC日志结构分析

### 3.1 垃圾收集器

- 使用Serial收集器在新生代的名字是Default New Generation，因此显示的是"[DefNew"
- 使用ParNew收集器在新生代的名字会变成"[ParNew" ,意思是"Parallel New Generation"
- 使用Parallel Scavenge收集器在新生代的名字是"[PSYoungGen" ,这里的.DK1.7使用的就是PSYoungGen
- 使用Parallel old Generation收集器在老年代的名字是"[Par0ldGen"
- 使用G1收集器的话，会显示为"garbage-first heap"
- Allocation Failure：表明本次引起GC的原因是因为在年轻代中没有足够的空间能够存储新的数据了。

### 3.2 GC前后情况

`[ PSYoungGen: 5986K->696K(8704K)]5986K->704K(9216K)`

通过上面代码显示，我们可以发现GC日志格式的规律一般都是：GC前内存占用一>GC后内存占用（该区域内存总大小)

> • 中括号内：GC回收前年轻代堆大小，回收后大小，（年轻代堆总大小）
• 括号外：GC回收前年轻代和老年代大小，回收后大小，（年轻代和老年代总大小)
> 

### 3.3 GC时间

GC日志中有三个时间:user，sys和real

- user - 进程执行用户态代码（核心之外）所使用的时间。这是执行此进程所使用的实际CPU时间，其他进程和此进程阻塞的时间并不包括在内。在垃圾收集的情况下，表示GC线程执行所使用的CPU 总时间。
- sys - 进程在内核态消耗的 CPU 时间，即在内核执行系统调用或等待系统事件所使用的CPU 时间
- real - 程序从开始到结束所用的时钟时间。这个时间包括其他进程使用的时间片和进程阻塞的时间（比如等待I/0完成)。对于并行gc，这个数字应该接近（用户时间+系统时间）除以垃圾收集器使用的线程数。
    
    > 由于多核的原因，一般的Gc事件中，real time是小于sys + user time的，因为一般是多个线程并发的去做GC，所以real time是要小于sys+user time的。如果real>sys+user的话，则你的应用可能存在下列问题:IO负载非常重或者是CPU不够用。
    > 

### 4.Minor GC日志解析

`2020-11-20T17:19:43.265-0800: 0.822:[GC(ALLOCATION FAILURE)[PSYOUNGGEN:76800K->8433K(89600K)] 76800K->8449K(294400K),0.0088371 SECs] [TIMES:USER=0.02 sYS=0.01,REAL=0.01 SECS]`

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EJVM%E8%BF%90%E8%A1%8C%E6%97%B6%E5%8F%82%E6%95%B0%E5%8F%8A%E5%A6%82%E4%BD%95%E5%88%86%E6%9E%90GC%E6%97%A5%E5%BF%97/image.png)

### 5.Full GC日志分析

`2020-11-20T17:19:43.794-0800: 1.351:[FULL GC(METADATA GC THRESHOLD)[PSYOUNGGEN:10082K->OK(89600K)][ PAROLDGEN: 32K->9638K(204800K)]10114K->9638K (294400K),[METASPACE: 20158K->20156K(1067008K)]，0.0285388 SECS][TIMES: USER=0.11sYS=0.00，REAL=0.03 SECS]`

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EJVM%E8%BF%90%E8%A1%8C%E6%97%B6%E5%8F%82%E6%95%B0%E5%8F%8A%E5%A6%82%E4%BD%95%E5%88%86%E6%9E%90GC%E6%97%A5%E5%BF%97/image%201.png)

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EJVM%E8%BF%90%E8%A1%8C%E6%97%B6%E5%8F%82%E6%95%B0%E5%8F%8A%E5%A6%82%E4%BD%95%E5%88%86%E6%9E%90GC%E6%97%A5%E5%BF%97/image%202.png)

## 二、GC日志分析工具

### 1.GCEasy

- 是一款免费在线日志分析工具（某些功能收费）

### 2.GCViewer

- 开源免费的客户端，可查看分析很多类型的虚拟器生成的GC日志