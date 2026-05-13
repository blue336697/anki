# Java虚拟机|JVM知识点汇总及简述-＞性能监控与调优

type: Post
status: Published
date: 2021/09/13
summary: 性能监控与调优
tags: JVM
category: 虚拟机

# 性能监控与调优

- 前言

> 这里学完整章后选择一到两个工具使用熟练，个人推荐Visual VM和Arthas搭配熟练使用
> 

## 一、概述

### 1.性能评价/测试指标

### 1.1 停顿时间（响应时间）

- 提交请求和返回该请求的响应之间使用的时间，一般比较关注平均响应时间常用操作的响应时间列表：

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image.png)

- 在垃圾回收环节中，暂停时间：执行垃圾收集时，程序的工作线程被暂停的时间。

### 1.2 吞吐量

- 对单位时间内完成的工作量（请求）的量度
- 在GC中:运行用户代码的时间占总运行时间的比例（总运行时间:程序的运行时间+内存回收的时间)吞吐量为1-1/(1+n)。
    
    > -XX:GCTimeRatio=n
    > 

### 1.3 并发数

同—时刻，对服务器有实际交互的请求数

### 1.4 内存占用

Java堆区所占的内存大小

### 1.5 相互间的关系

这里主要讨论停顿时间、吞吐量、并发数之间的关系，当吞吐量越高，并发数也就也高，而停顿时间就越短

## 二、JVM监控及诊断工具-命令行

### 1.概述

使用数据说明问题，使用知识分析问题，使用工具处理问题。无监控、不调优!

### 2.jps：查看正在运行的Java进程

- 说明

> Java process status，显示指定系统内所有的HotSpot虚拟机进程(查看虚拟机进程信息)，可用于查询正在运行的虚拟机进程。
说明:对于本地虚拟机进程来说，进程的本地虚拟机ID与操作系统的进程ID是一致的，是唯一的。
> 
- options参数：

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%201.png)

> 参数说明：
> 
> - q：仅仅显示LVMID (local virtual machine id)，即本地虚拟机唯一id。不显示主类的名称等
> -l：输出应用程序主类的全类名或如果进程执行的是jar包，则输出jar完整路径
> -m：输出虚拟机进程启动时传递给主类main()的参数
> -v：列出虚拟机进程启动时的JVM参数。比如:-Xms20m -Xmx50m是启动程序指定的jvm参数。
- 注意：

> 如果某Java进程关闭了默认开启的UsePerfData参数（即使用参数-XX:-UsePerfData），那么jps命令（以及下面介绍的jstat）将无法探知该Java进程。
> 

### 3.jstat：查看JVM的统计信息

- 说明

> • JVM Statistics Monitoring Tool：用于监视虚拟机各种运行状态信息的命令行工具。它可以显示本地或者远程虚拟机进程中的类装载、内存、垃圾收集、IT编译等运行数据。
• 在没有GUI图形界面，只提供了纯文本控制台环境的服务器上，**它将是运行期定位虚拟机性能问题的首选工具。常用于检测垃圾回收问题以及内存泄漏问题。**
> 

### 3.1 option参数

- 类装载相关的

> -class：显示ClassLoader的相关信息:类的装载、卸载数量、总空间、类装载所消耗的时间等
> 
- 垃圾相关的

> -gc：显示与GC相关的堆信息。包括Eden区、两个Survivor区、老年代、永久代等的容量、己用空间、GC时间合计等信息。-gccapacity：显示内容与-gc基本相同，但输出主要关注Java堆各个区域使用到的最大、最小空间。-gcutil：显示内容与-gc基本相同，但输出主要关注已使用空间占总空间的百分比。-gccause：与-gcutil功能一样，但是会额外输出导致最后一次或当前正在发生的GC产生的原因。-gcnew：显示新生代GC状况-gcnewcapacity：显示内容与-gcnew基本相同，输出主要关注使用到的最大、最小空间-geold：显示老年代GC状况-gcoldcapacity：显示内容与-gcold基本相同，输出主要关注使用到的最大、最小空间-gcpermcapacity：显示永久代使用到的最大、最小空间。
> 
- JIT相关的

> -compiler：显示JIT编译器编译过的方法、耗时等信息-printcompilation：输出已经被JIT编译的方法
> 

### 3.2 其他参数

- interval参数

> 用于指定输出统计数据的周期，单位为毫秒。**即：查询间隔**
> 
- count参数
    
    > 用于指定查询的总次数，跟在interval参数后面配合使用
    > 
- t参数

> 可以在输出信息加上一个TimeStamp列，来显示程序自打开运行的时间，单位：秒
> 
> 
> > 可以根据-t参数来判断是否要出现OOM：比较Java进程的启动时间以及总GC时间（GCT列），或者两次测量的间隔时间以及总GC时间的增量,来得出 GC时间占运行时间的比例。**如果该比例超过20%，则说明目前堆的压力较大;如果该比例超过90%，则悦明堆里几乎没有可用空间，随时都可能抛出 OOM异常。**
> > 
- h参数

> 可以在周期性数据输出时，输出多少行数据后输出一个表头信息
> 

### 3.3 如何通过jstat判断内存泄露

分别为两步：

1. 在长时间运行的 Java程序中，我们可以运行jstat命令连续获取多行性能数据，并取这几行数据中OU列（**即已占用的老年代内存**）的最小值。
2. 每隔一段较长的时间重复一次上述操作，**来获得多组OU最小值**。如果这些值呈上涨趋势，则说明该Java程序的老年代内存己使用量在不断上涨，这意味着无法回收的对象在不断增加，因此很有可能存在内存泄漏。

### 4.jinfo：实时查看和修改JVM配置参数

- 说明

> Configuration Info for Java，在很多情况下，Java应用程序不会指定所有的Java虚拟机参数。而此时，开发人员可能不知道某一个具体的Java虚拟机参数的默认值。在这种情况下，可能需要通过查找文档获取某个参数的默认值。这个查找过程可能是非常艰难的。但有了jinfo工具，开发人员可以很方便地找到Java虚拟机参数的当前值。
> 

### 4.1 option参数

基本使用语法：jinfo [ options ] pid

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%202.png)

> 注意：标记为manageable的参数非常有限
> 

### 4.2 拓展参数

- java -XX:+PrintFlagsInitial
    
    > 查看所有JVM参数启动的初始值
    > 
- java -xx:+PrintFlagsFinal
    
    > 查看所有JVM参数的最终值
    > 
- java -XX:+ PrintCommandLineFlags
    
    > 查看那些已经被用户或者JVM设置过的详细的XX参数的名称和值
    > 

### 5.jmap：导出内存映像文件&内存使用情况

- 说明：

> JVM Memory Map：作用一方面是获取dump文件（堆转储快照文件，二进制文件），它还可以获取目标Java进程的内存相关信息，包括Java堆各区域的使用情况、堆中对象的统计信息、类加载信息等。
> 

### 5.1 option参数

基本语法：

- jmap [option] `<pid>`
- jmap [option] `<executable> <core>`
- jmap [option] [server_id@] `<remote server IP or hostname>`

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%203.png)

### 5.2 两种用法详解

1. 导出内存映像文件（dump）

> • 手动方式：
`jmap -dump:live, format=b,file=d:\\4.hprof pid`
**说明：live参数表示只打印内存的存活对象（往往出现OOM的时候就是太多存货对象回收不了导致的，没有该参数就表示打印全部对象），format参数标识打印的文件格式可以被监控工具识别，file就是指定文件生成位置，文件名后缀为 .hprof ，pid为进程号**
• 自动方式：
`-XX:+HeapDumpOnoutOfMemoryError`：在程序发生OOM时，导出应用程序的当前堆快照。
`-XX:HeapDumpPath`：可以指定堆快照的保存位置。
**说明：当程序发生OOM退出系统时，一些瞬时信息都随着程序的终止而消失，而重现OOM问题往往比较困难或者耗时。此时若能在OOM时，自动导出dump文件就显得非常迫切。**
> 
1. 显示内存使用情况

> 说明：这两个参数都是对于内存某一个时刻进行的时间点信息，无法做到持续监控
> 

> • -jmap -heap pid
• -jmap -histo pid
> 

### 5.3 小结

> 由于jmap将访问堆中的所有对象，为了保证在此过程中不被应用线程干扰，jmap需要借助安全点机制，让所有线程停留在不改变堆中数据的状态。与前面讲的jstat则不同，垃圾回收器会主动将jstat所需要的摘要数据保存至固定位置之中，而jstat只需直接读取即可。
> 
- 缺点：

> • 由jmap导出的堆快照必定是安全点位置的。这可能导致基于该堆快照的分析结果存在偏差。
• 加入生命周期只在两个安全点之间有效，jmap记录的时候是检测不到的
• 如果某个线程长时间无法跑到安全点，jmap将一直等下去。
> 

### 6.jhat：JDK自带堆分析工具

- 概述

> JVM Heap Analysis Tool，jhat内置了一个微型的HTTP/HTML服务器，生成dump文件的分析结果后，用户可以在浏览器中查看分析结果(分析虚拟机转储快照信息)。使用了jhat命令，就启动了一个http服务，端口是7000，即http://localhost:7000/，就可以在浏览器里分析。
> 
- 注意

> jhat命令在JDK9、JDK10中已经被删除，官方建议用VisualVM代替。所以这里就不做过多介绍
> 

### 7.jstack：打印JVM中的线程快照

- 概述

> JVM Stack Trance打印当前进程的所有线程
> 
- 作用

> 生成线程快照的作用：可用于定位线程出现长时间停顿的原因，如线**程间死锁、死循环、请求外部资源导致的长时间等待等问题**。这些都是导致线程长时间停顿的常见原因。当线程出现停顿时，就可以用jstack显示各个线程调用的堆栈情况。
> 
- 快照中需要注意的地方

> • 死锁，Deadlock（重点关注）
• 等待资源，waiting on condition（重点关注)
• 等待获取监视器，waiting on monitor entry（重点关注)阻塞，Blocked（重点关注)
• 执行中，Runnable
• 暂停，Suspended
> 

### 7.1 option参数

- F：当正常输出的请求不被响应时，强制输出线程堆栈
- l：除堆栈外，显示关于锁的附加信息
- m：如果调用到本地方法的话，可以显示C/C++的堆栈
- h：帮助操作

### 8.jcmd：多功能命令行

- 概述

> 它是一个多功能的工具，可以用来实现前面除了jstat之外所有命令的功能。比如:用它来导出堆、内存使用、查看Java进程、导出线程信息、执行GC、JVM运行时间等。官方推荐使用jcmd代替jmap
> 

### 8.1 基本语法

- jcmd -l：列出所有的JVM进程
- jcmd pid help：针对指定的进程，列出支持的所有命令
- jcmd pid具体命令团：显示指定进程的指令命令的数据

## 三、JVM监控及诊断工具-GUI

### 1.工具概述

- 使用命令行工具的弊端

> 无法获取方法级别的分析数据，如方法间的调用关系、各方法的调用次数和调用时间等（这对定位应用性能瓶颈至关重要）。要求用户登录到目标Java应用所在的宿主机上，使用起来不是很方便。分析数据通过终端输出，结果展示不够直观。
> 
- 工具分类

> • JDK自带的工具：jConsole、Visual VM、JMC（Java mission control）
• 第三方工具：MAT（Eclipse）、JProfiler、Arthas、Btrace
> 

### 2.jConsole

### 2.1 概述

> • 从JDK5开始，在JDK中自带的java监控和管理控制台。
• 用于对VM中内存、线程和类等的监控，是一个基于JMX(java management extensions)的GUI性能监控工具
> 
- 位置：

> 在JDK目录下的bin目录可找到
> 

### 3.Visual VM

### 3.1 概述

> • Visual VM是一个功能强大的多合一故障诊断和性能监控的可视化工具。
• 它集成了多个JDK命令行工具，使用Visual M可用于显示虚拟机进程及进程的配置和环境信息(jps,jinfo)，监视应用程序的CPU、GC、堆、方法区及线程的信息(jstat、jstack)等，代替JConsole。
• 在JDK 6 Update 7以后，Visual VM便作为DK的一部分发布(VisualVM在JDK/bin目录下)，是完全免费的
• Visual VM也可以作为独立的软件安装
> 
- 安装方式

> • 在JDK的bin目录下，如果没有则自行下载
• 可在idea中下载启动Visual 的插件，记得要配置.exe文件和JDK的home目录
• 插件安装可在官网或客户端中下载（强烈推荐Visual GC这个插件）
> 

### 3.2 主要功能

1. 生成/读取堆内存快照
2. 查看JVM参数和系统属性
3. 查看运行中的虚拟机进程
4. 生成/读取线程快照
5. 程序资源的实时监控
6. 其他功能
    
    > JMX代理连接、远程环境监控、CPU分析和内存分析
    > 

### 4.MAT

### 4.1 概述

> MAT(Memory Analyzer Tool)工具是一款功能强大的Java堆内存分析器。**主要用于dump文件的分析可以用于查找内存泄漏以及查看内存消耗情况。**MAT是基于Eclipse开发的，不仅可以单独使用，还可以作为插件的形式嵌入在Eclipse中使用。是免费软件
> 

### 4.2 dump文件信息

- 内容

> MAT可以分析heap dump文件。在进行内存分析时，只要获得了反映当前设备内存映像的hprof文件，通过MAT打开就可以直观地看到当前的内存信息。一般说来，这些内存信息包含：
> 
> - 所有的对象信息，包括对象实例、成员变量、存储于栈中的基本类型值和存储于堆中的其他对象的
> 引用值。
> - 所有的类信息，包括classloader、类名称、父类、静态变量等. GCRoot到所有的这些对象的引用路径
> - 线程信息，包括线程的调用栈及此线程的线程局部变量（TLS)
- 优点

> 能够快速为开发人员生成**内存泄漏报表**，方便定位问题和分析问题
> 
- 导出dump文件方式

> • 可以在visual vm里面生成
• 在第5节imap参数中，直接用imap参数导出
• 有两个参数可以导出dump文件`-XX:+HeapDumpOnoutOfMemoryError`：在程序发生OOM时，导出应用程序的当前堆快照。`-XX:HeapDumpPath`：可以指定堆快照的保存位置。
• 当然也可以直接用MAT生成dump文件，前提要知道进程号
> 

### 4.3 分析MAT中的dump文件过程

- histogram

> 展示了各个类的实例数目以及这些实例的Shallowheap 或Retainedheap的总和
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%204.png)

- thread overview

> 查看系统中的Java线程、查看局部变量的信息
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%205.png)

- 获得对象相互引用的关系
    
    > with outgoing references：查看这个对象引用了谁
    > 
    > 
    > with incoming references：查看谁引用了这个对象
    > 

### 4.4 深堆和浅堆

- 浅堆（Shallow Heap）

> 浅堆是指一个对象所消耗的内存。在32位系统中，一个对象引用会占据4个字节，一个int类型会占据4个字节，long型变量会占据8个字节，每个对象头需要占用8个字节。根据堆快照格式不同，对象的大小可能会向8字节进行对齐。以String为例: 2个int值共占8字节，对象引用占用4字节，对象头8字节，合计20字节，向8字节对齐，故占24字节。（jdk7中)。
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%206.png)

> 注意：与value值的多少是无关的
> 
- 保留集（Retained Set）

> 对象A的保留集指当对象A被垃圾回收后，可以被释放的所有的对象集合(包括对象A本身)，**即对象A的保留集可以被认为是只能通过对象A被直接或间接访问到的所有对象的集合**。通俗地说，**就是指仅被对象A所持有的对象的集合**。
> 
- 深堆（Retained Heap）

> 就是自己的浅堆大小加上**保留集**的大小就是深堆的大小
> 
- 对象实际大小

> 对象的实际大小就是指：浅堆大小+自己能够引用的全部对象大小
> 
- 案例分析

> 代码：
> 
> 
> ```java
> public class StudentTrace {
>  static List<WebPage> webpages = new ArrayList<>();
> 
>  public static void createWebPages() {
>      for (int i = 0; i < 100; i++) {
>          WebPage wp = new WebPage();
>          wp.setUrl( "<http://www>." + Integer.toString(i) + ".com" );
>          wp.setContent( Integer.toString(i));
>          webpages.add(wp);
>      }
>  }
> 
>  public static void main(String[] args) {
>      createWebPages();
>      Student s3 = new Student(3,"LLL");
>      Student s5 = new Student(5,"HHH");
>      Student s7 = new Student(7,"JJJ");
> 
>      for (int i = 0; i < webpages.size(); i++) {
>          if (i % s3.getId() == 0)
>              s3.visit(webpages.get(i));
>          if (i %s5.getId( ) == 0)
>              s5.visit(webpages.get(i));
>          if (i %s7.getId( ) == 0)
>              s7.visit(webpages.get(i));
>      }
>      webpages.clear();
>      System.gc();
> 
>  }
> }
> 
> class Student{
>  private int id;
>  private String name;
>  private List<WebPage> history = new ArrayList<>();
> 
>  public Student(int id, String name) {
>      this.id = id;
>      this.name = name;
>  }
> 
>  public int getId() {
>      return id;
>  }
> 
>  public void setId(int id) {
>      this.id = id;
>  }
> 
>  public String getName() {
>      return name;
>  }
> 
>  public void setName(String name) {
>      this.name = name;
>  }
> 
>  public List<WebPage> getHistory() {
>      return history;
>  }
> 
>  public void setHistory(List<WebPage> history) {
>      this.history = history;
>  }
> 
>  public void visit(WebPage wp){
>      if(wp != null){
>          history.add(wp);
>      }
>  }
> }
> 
> class WebPage{
>  private String url;
>  private String content;
> 
>  public String getUrl() {
>      return url;
>  }
> 
>  public void setUrl(String url) {
>      this.url = url;
>  }
> 
>  public String getContent() {
>      return content;
>  }
> 
>  public void setContent(String content) {
>      this.content = content;
>  }
> }
> ```
> 

> 分析7号JJJ对象的内存占用
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%207.png)

> • 考虑JJJ同学：15个 webpage，每个对应152个字节 15* 152= 2280字节，即为elementData的实际大小
• 能被7整除，且能被3整除，以及能被7整除，且能被5整除的数值有:0，21,42,63,84,35,70 共7个数。7*152 = 1064字节，2280 -1064 +72 = 1288字节
• 72个字节组成为：15个elementData的元素*4字节 =60字节，60＋8个对象头的字节数＋4字节=72字节
> 

### 4.5 支配树

- 概述

> MAT提供了一个称为支配树（Dominator Tree）的对象图。支配树体现了对象实例间的支配关系。**在对象引用图中，所有指向对象B的路径都经过对象A，则认为对象A支配对象B。如果对象A是离对象B最近的一个支配对象，则认为对象A为对象B的直接支配者。**支配树是基于社象间的引用图所建立的，它有以下基本性质：
> 
> - 对象A的子树（所有被对象A支配的对象集合）表示对象A的保留集（retained set），即深堆。
> - 如果对象A支配对象B，那么对象A的直接支配者也支配对象B。
> - 支配树的边与对象引用图的边不直接对应。
- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%208.png)

## 四、再谈内存泄露

### 1.内存泄露的理解与分类

- 概述

> 可达性分析算法来判断对象是否是不再使用的对象，本质都是判断一个对象是否还被引用。那么对于这种情况下，由于代码的实现不同就会出现很多种内存泄漏问题（让JVM误以为此对象还在引用中，无法回收，造成内存泄漏）。
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%209.png)

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%2010.png)

### 1.1 内存泄漏与内存溢出的关系

> 内存泄漏（Memory Leak）：
申请了内存用完了不释放，比如一共有1024M 的内存，分配了512M的内存一直不回收，那么可以用的内存只有521M 了，仿佛泄露掉了一部分。内存溢出（Out Of Memory）：
申请内存时,没有足够的内存可以使用。
> 

> 可见，内存泄漏和内存溢出的关系:内存泄漏的增多，最终会导致内存溢出。
> 

### 1.2 内存泄漏的分类

- 经常发生：发生内存泄露的代码会被多次执行，每次执行，泄露一块内存;
- 偶然发生：在某些特定情况下才会发生;
- 一次性：发生内存泄露的方法只会执行一次;
- 隐式泄漏：一直占着内存不释放，直到执行结束;严格的说这个不算内存泄漏，因为最终释放掉了,但是如果执行时间特别长，也可能会导致内存耗尽。

### 2.Java中内存泄漏的8种情况

### 2.1 静态集合类

> 静态集合类，如HashMap、LinkedList等等。如果这些容器为静态的，那么它们的生命周期与JVM程序一致，则容器中的对象在程序结束之前将不能被释放，从而造成内存泄漏。简单而言，长生命周期的对象持有短生命周期对象的引用，尽管短生命周期的对象不再使用，但是因为长生命周期对象持有它的引用而导致不能被回收。
> 
> 
> ```java
> public class test01(){
>  static List list = new ArrayList();
> 
>  public void oomTest(){
>      Object o = new Object();//局部变量
>      list.add(o);
>  }
> }
> ```
> 

### 2.2 单例模式

> 单例模式，和静态集合导致内存泄露的原因类似，因为单例的静态特性，它的生命周期和JVM 的生命周期一样长，所以如果单例对象如果持有外部对象的引用，那么这个外部对象也不会被回收，那么就会造成内存泄漏。
> 

### 2.3 内部类持有外部类

> 内部类持有外部类，如果一个外部类的实例对象的方法返回了一个内部类的实例对象。
这个内部类对象被长期引用了，即使那个外部类实例对象不再被使用，但由于内部类持有外部类的实例对象，这个外部类对象将不会被垃圾回收，这也会造成内存泄漏。
> 

### 2.4 各种连接，数据库连接、网络连接和IO连接等

> 在对数据库进行操作的过程中，首先需要建立与数据库的连接，当不再使用时，需要调用close方法来释放与数据库的连接。只有连接被关闭后，垃圾回收器才会回收对应的对象。
否则，如果在访问数据库的过程中，对Connection、Statement或ResultSet不显性地关闭，将会造成大量的对象无法被回收，从而引起内存泄漏。
> 
> 
> ```java
> public static void main( String[] args) {
> 	try {
> 		Connection conn = null;
> 		Class.forName( "com.mysql.jdbc.Driver" );
> 		conn = DriverManager.getConnection( "ur1", "","");
>      Statement stmt = conn.createStatement();
> 		Resultset rs = stmt.executeQuery("....");
>  }catch (Exception e) {//异常日志
> 
>  }finally {
> 		//1.关闭结果集Statement
> 		//2.关闭声明的对象ResultSet
>      //3.关闭连接Connection
> }
> }
> ```
> 

### 2.5 变量不合理作用域

> 变量不合理的作用域。一般而言，一个变量的定义的作用范围大于其使用范围，很有可能会造成内存泄漏。另一方面，如果没有及时地把对象设置为null，很有可能导致内存泄漏的发生。
> 

```java
public class UsingRandom {
	private String msg;
	public void receiveMsg(){
		readFromNet();//从网络中接受数据保存到msg中
     saveDB();//把msg保存到数据库中
	}
}
//如上面这个伪代码，通过readFromNet方法把接受的消息保存在变量
//msg中，然后调用saveDB方法把msg的内容保存到数据库中，
//此时msg已经就没用了，由于msg的生命周期与对象的生命周期相同，
//此时msg还不能回收，因此造成了内存泄漏。
//实际上这个msg变量可以放在receiveMsg方法内部，当方法使用完，
//那么msg的生命周期也就结束，此时就可以回收了。还有一种方法，
//在使用完msg后，把msg设置为null，
//这样垃圾回收器也会回收msg的内存空间。
```

### 2.6 改变哈希值

> 改变哈希值，当一个对象被存储进HashSet集合中以后，就不能修改这个对象中的那些参与计算哈希值的字段了。
否则，对象修改后的哈希值与最初存储进HashSet集合中时的哈希值就不同了，在这种情况下，即使在contains方法使用该对象的当前引用作为的参数去HashSet集合中检索对象，也将返回找不到对象的结果，这也会导致无法从HashSet集合中单独删除当前对象，造成内存泄漏。
这也是String为什么被设置成了不可变类型，我们可以放心地把String存入 HashSet，或者把String 当做HashMap的key 值;
> 
> 
> ```java
> public class test02 {
> 	public static void main(String[ ] args) {
> 		HashSet set = new HashSet( );
> 		Person p1 = new Person( id: 1001，name: "AA" );
>      Person p2 = new Person( id: 1002,name: "BB");
> 		set.add(p1);
> 		set.add(p2);
>      p1.name = "CC";//此操作就是导致对象删除不掉的原因
>      set.remove(p1);
> 		System.out.println(set);
> 
> 		set.add(new Person(1001,"CC" ));
> 		System.out.println(set);//输出三个对象
> 		set.add(new Person(1001,"AA"));
>      System.out.printLn(set);//输出四个对象，解析如下图
> 	}
> }
> 
> class Person{
>  private int id;
>  private String name;
> 
>  public Person(int id, String name) {
>      this.id = id;
>      this.name = name;
>  }
> 
>  @Override
>  public boolean equals(Object o) {
>      if (this == o) return true;
>      if (!(o instanceof Person)) return false;
>      Person person = (Person) o;
>      return getId() == person.getId() && Objects.equals(getName(), person.getName());
>  }
> 
>  @Override
>  public int hashCode() {
>      return Objects.hash(id, name);
>  }
> 
>  @Override
>  public String toString() {
>      return "Person{" +
>              "id=" + id +
>              ", name='" + name + '\\'' +
>              '}';
>  }
> 
>  public int getId() {
>      return id;
>  }
> 
>  public void setId(int id) {
>      this.id = id;
>  }
> 
>  public String getName() {
>      return name;
>  }
> 
>  public void setName(String name) {
>      this.name = name;
>  }
> }
> ```
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%2011.png)

### 2.7 缓存泄漏

> 内存泄漏的另一个常见来源是缓存，一旦你把对象引用放入到缓存中，他就很容易遗忘。比如:之前项目在一次上线的时候，应用启动奇慢直到夯死，就是因为代码中会加载一个表中的数据到缓存（内存)中，测试环境只有几百条数据，但是生产环境有几百万的数据。
**对于这个问题，可以使用WeakHashMap（软引用）代表缓存，此种Map的特点是，当除了自身有对key的引用外，此key没有其他引用那么此map会自动丢弃此值。**
> 
> 
> ```java
> public class MapTest {
> 	static Map wMap = new WeakHashMap();
>  static Map map = new HashMap();
> 
> 	public static void main(String[] args) {
> 		init();
> 		testweakHashMap( );
>  	testHashMap();
> 	}
>  public static void init() {
> 		String s1 = new String( original: "obejct1");
>      String s2 = new String( original: "obejct2");
>      String s3 = new String( original: "obejct3");
>      String s4 = new strEing( original: "obejct4");
>      wMap.put(s1, "cacheObject1");
> 		wMap.put(s2,"cacheObject2");
>      map.put(ref3，"cacheObject3" );
>      map.put(ref4,"cacheObject4" );
> 		System.out.println("string引用s1,s2,s3,s4消失");
> 	}
>  public static void testweakHashMap() {
> 		System.out.print1n( "weakHashMap GC之前");
>      for (Object o : wMap.entrySet()){
> 			System.out.println(o);
> 		} try {
> 			System.gc();
> 			TimeUnit.SECONDS.sleep( timeout: 5);
>      }catch (InterruptedException e) {
> 			e.printStackTrace();
> 		}
> 		System.out.println( "weakHashMap GC之后");
>      for (object o : wMap. entrySet()) {
> 			System.out.println(o);
> 		}
> 	}
>  public static void testHashMap() {
> 		System.out.print1n( "HashMap GC之前");
>      for (Object o : Map.entrySet()){
> 			System.out.println(o);
> 		} try {
> 			System.gc();
> 			TimeUnit.SECONDS.sleep( timeout: 5);
>      }catch (InterruptedException e) {
> 			e.printStackTrace();
> 		}
> 		System.out.println( "HashMap GC之后");
>      for (object o : Map. entrySet()) {
> 			System.out.println(o);
> 		}
> 	}
> }
> ```
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%2012.png)

### 2.8 监听器和回调

> 内存泄漏另一个常见来源是监听器和其他回调，如果客户端在你实现的API中注册回调，却没有显示的取消,那么就会积聚。
需要确保回调立即被当作垃圾回收的最佳方法是只保存它的弱引用，例如将他们保存成为weakHashMap中的键。
> 

### 3.内存泄漏案例分析

### 3.1 案例一

```java
public class MyStack {

    private Object[] elements;
    private int size = 0;
    private static final int DEFAULT_INITIAL_CAPACITY = 16;

    public MyStack() {
        elements = new Object[DEFAULT_INITIAL_CAPACITY];
    }
    //压栈操作
    public void push(Object e) {
        ensureCapacity();
        elements[size++] = e;
    }

    //这个出栈操作是错误的，我们只是把想要删除的指针引用向下面移了，被删除的对象还占着空间
    /*public Object pop(){
        if (size == 0)
            throw new EmptyStackException();
        return elements[ --size];
    }*/

    //这样就可以了，让被删除的对象的值置为null
    public Object pop(){
        if(size == 0){
            throw new EmptyStackException();
        }
        Object o = elements[--size];
        elements[size] = null;  //size已经减过了
        return o;
    }

    private void ensureCapacity() {
        if (elements.length == size)
            elements = Arrays.copyOf(elements,2 * size + 1);
    }

}
```

### 3.2 案例二

```java
public class TestActivity extends Activity{

        private static final Object key = new Object();
        @Override
        protected void onCreate( Bundle savedInstanceState) {
            super.onCreate( savedInstanceState) ;
            setContentview(R.layout.activity_main);
            new Thread(){//匿名线程
                public void run() {
                    synchronized (key) {
                        try {

                        key.wait();
                    }catch (InterruptedException e) {
                        e. printstackTrace();
                    }
                }
            }
        }.start();
    }
}
```

- 出现的问题

> 匿名线程始终不能被GC
> 
- 解决办法

> 使用线程时，一定要确保线程在周期性对象（如Activity)销毁时能正常结束，如能正常结束，但是Activity销毁后还需执行一段时间，也可能造成泄露，此时可采用weakReference方法来解决，另外在使用Handler的时候，如存在Delay操作，也可以采用weakReference;使用Handler + HandlerThread时，记住在周期性对象销毁时调用looper.quit()方法;
> 

## 五、OQL语言查询对象信息

- 概述

> MAT支持一种类似于SQL的查询语言OQL (Object Query Language）。OQL使用类SQL语法，可以在堆中进行对象的查找和筛选。
> 

### 1.SELECT子句

> 在MAT中，Select子句的格式与SQL基本一致，用于指定要显示的列。Select子句中可以使用“*”，查看结果对象的引用实例（相当于outgoing references）。
> 
> - 使用“OB3ECTS”关键字，可以将返回结果集中的项以对象的形式显示。
>     
>     SELECT objects v.elementData FROM java.util.Vector v
>     
>     SELECT OBECTS s.value FROM java.lang.string s
>     
> - 在Select子句中，使用“AS RETAINED SET”关键字可以得到所得对象的保留集。
>     
>     SELECT AS RETAINED SET * FROM com.atguigu.mat. Student
>     
> - “DISTINCT”关键字用于在结果集中去除重复对象。
> SELECT DISTINCT OBECTS classof(s)FROM java.lang.String s

### 2.FROM子句

> • From子句用于指定查询范围，它可以指定类名、正则表达式或者对象地址。
SELECT * FROM java.lang.String s
• 下例使用正则表达式，限定搜索范围，输出所有com.atguigu包下所有类的实例
SELECT *FROM "com\.atguigul..*”
• 也可以直接使用类的地址进行搜索。使用类的地址的好处是可以区分被不同ClassLoader加载的同一种类型。
select * from 0x37a0b4d
> 

### 3.WHERE子句

> where子句用于指定oQL的查询条件。oQL查询将只返回满足where子句指定条件的对象。Where子句的格式与传统SQL极为相似。
> 
> - 下例返回长度大于10的char数组。
> SELECT * FROM char[] s WHERE s.@length>10
> - 下例返回包含“java”子字符串的所有字符串，使用“LIKE”操作符，“LIKE”操作符的操作参数为正则表达式。
> SELECT * FROM java.lang.String s WHERE toString(s）LIKE ".*java.*"
> - 下例返回所有value域不为null的字符串，使用“=”操作符。
> SELECT * FROM java.lang.String s where s.value !=null
> - where子句支持多个条件的AND、OR运算。下例返回数组长度大于15，并且深堆大于1000字节的所有Vector对象。
> SELECT * FROM java.util.Vector v WHERE v.elementData.@length>15 AN Dv.@retainedHeapsize>1000

### 4.内置对象与方法

> 0QL中可以访问堆内对象的属性，也可以访问堆内代理对象的属性。访问堆内对象的属性时,格式如下：
`[ <alias>. ] <field> . <field>. <field>`其中alias为对象名称。
> 
> - 访问java.io.File对象的path属性，并进一步访问path的value属性:
>     
>     SELECT toString(f.path.value）FROM java.io.File f
>     
> - 下例显示了String对象的内容、objectid和objectAddress。
> SELECT s.toString(), s.@objectId, s.@objectAddress FROMjava.lang.String s
> - 下例显示java.util.Vector内部数组的长度。
> SELECT v.elementData.@length FROM java.util.Vector v
> - 下例显示了所有的java.util.Vector对象及其子类型
> select * from INSTANCEOF java.util.Vector

## 六、JProfiler

### 1.基本概述

> 想要用一款集成在idea的分析工具，或想要比mat工具更加全面，JProfiler由此诞生，是一款Java应用性能诊断工具，功能强大，**但注意是收费的**
> 

### 1.1 特点

> • 使用方便、界面操作友好―(简单且强大)
• 对被分析的应用影响小(提供模板)
• CPU, Thread ,Memory分析功能尤其强大
• 支持对jdbc ,nosql，jsp, servlet, socket等进行分析
• 支持多种模式(离线，在线)的分析
• 支持监控本地、远程的JVM
• 跨平台,拥有多种操作系统的安装版本
> 

### 1.2 主要功能

> 方法调用：对方法调用的分析可以帮助您了解应用程序正在做什么，并找到提高其性能的方法内存分配：通过分析堆上对象、引用链和垃圾收集能帮您修复内存泄漏问题，优化内存使用线程和锁：JProfiler提供多种针对线程和锁的分析视图助您发现多线程问题高级子系统：许多性能问题都发生在更高的语义级别上。例如，对于JDBC调用，您可能希望找出；执行最慢的SQL语句。JProfiler支持对这些子系统进行集成分析
> 

### 2.具体使用

### 2.1 数据采集方式

- Instrumentation（重构模式）：这是JProfiler全功能模式。在class加载之前，JProfier把相关功能代码写入到需要分析的class的bytecode中，对正在运行的jvm有一定影响。

> • 优点：功能强大。在此设置中,调用堆栈信息是准确的。
• 缺点：若要分析的class较多,则对应用的性能影响较大,CPU开销可能很高(取决于Filter的控制)。因此使用此模式一般配合Filter使用,只对特定的类或包进行分析。
> 
- Full sampling（抽样模式）：类似于样本统计，每隔一定时间(5ms )将每个线程栈中方法栈中的信息统计出来。
    
    > ◦ 优点：对[PU的开销非常低，对应用影响小(即使你不配置任何Filter)
        ◦ 缺点：一些数据/特性不能提供(例如:方法的调用次数、执行时间)
    > 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E6%80%A7%E8%83%BD%E7%9B%91%E6%8E%A7%E4%B8%8E%E8%B0%83%E4%BC%98/image%2013.png)

### 2.2 各种重要功能

> 这里这些功能演示及案例分析就不扣字写了，大家想要了解请去尚硅谷看JVM视频（343~349）
> 
- 遥感监测（Telemetries）
- 内存视图（Live Memory）
- 堆遍历（heap walker）
- cpu视图（cpu views）
- 线程视图（threads）
- 监视器&锁（Monitors&locks）

## 七、Arthas

### 1.前奏

### 1.1 JProfiler与JvisualVM的缺点

> 这两款工具有个缺点，都必须在服务端项目进程中配置相关的监控参数。然后工具通过远程连接到项目进程，获取相关的数据。这样就会带来一些不便，比如线上环境的网络是隔离的，本地的监控工具根本连不上线上环境。并且类似于Jprofiler这样的商业工具，是需要付费的。
> 

### 1.2 概述

> Arthas(阿尔萨斯）是Alibaba开源的Java诊断工具，在线排查问题，无需重启;动态跟踪Java代码;实时监控JVM状态。Arthas支持JDK 6+，支持Linux/Mac/Windows，采用命令行交互模式，同时提供丰富的Tab自动补全功能，进一步方便进行问题的定位和诊断。借鉴并基于很多优秀的软件组合而成的一个工具
> 
- 注意：

> 由于是开源的项目且是国人开发，这里就不做过多介绍，大家可移步至官网查看中文文档https://arthas.aliyun.com/doc/，里面有十分详细的说明
> 

## 八、JMC（Java Mission Control）

### 1.概述

> 是oracle公司自己的工具，在JDK的bin目录下找到jmc.exe可执行文件
> 

## 九、其他调优工具

- Tprofiler：是由阿里开源的一款寻找错误热点代码的工具
- Btrace：简洁明了，大意是一个Java平台的安全的动态追踪工具。可以用来动态地追踪一个运行的Java程序。BTrace动态调整目标应用程序的类以注入跟踪代码（“字节码跟踪”)。
- YourKit
- JProbe
- Spring Insight