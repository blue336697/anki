# Java虚拟机|JVM知识点汇总及简述-＞Class文件结构

type: Post
status: Published
date: 2021/09/09
summary: write once ，run anywhere。当Java源代码成功编译成字节码后，如果想在不同的平台上面运行，则无须再次编译
tags: JVM
category: 虚拟机

# Class文件结构

## 一、概述

### 1.字节码文件的跨平台性

### 1.1 Java跨平台的语言

- Java圣经

> write once ，run anywhere。当Java源代码成功编译成字节码后，如果想在不同的平台上面运行，则无须再次编译
> 

### 1.2 Java虚拟机，跨语言的平台

> Java虚拟机不和包括Java 在内的任何语言绑定，它只与“Class文件”这种特定的二进制文件格式所关联。所有的JVM全部遵守Java虚拟机规范，也就是说所有的JVM环境都是一样的，这样一来字节码文件可以在各种JVM上运行。
> 
- 图示（平台的无关性）

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image.png)

- 官方文档

> 需要查阅每次Java语言和JVM的更新细节，请[点击传送](https://docs.oracle.com/javase/specs/index.html)
> 

### 1.3 字节码的规范

> 想要让一个Java程序正确地运行在JVM中，Java源码就必须要被编译为符合JVM规范的字节码。
> 
- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%201.png)

- 图解
1. 前端编译器的主要任务就是负责将符合Java语法规范的Java代码转换为符合JVM规范的字节码文件。
2. Javac是一种能够将Java源码编译为字节码的前端编译器。
    
    > Javac编译器在将Java源码编译为一个有效的字节码文件过程中经历了4个步骤，**分别是词法解析、语法解析、语义解析以及生成字节码。**
    > 

### 2.Java前端编译器

> 前端编译器负责把Java文件编译成字节码文件
> 

### 2.1 Javac

> Javac是Java语言自带的前端编译器，而HotSpot虚拟机不强制前端编译器必须使用Javac。Javac所使用的编译方案是全量式编译，即每次都将代码全部编译一遍，这也是比较慢的一种编译方式。
> 

### 2.2 ECJ（Eclipse Compiler for Java）

> 是Eclipse这个IDE自带的编译器，因为使用的编译策略是增量式编译，即只编译每次不同的，不变的不做改变。所以在与idea在编译速度方面会更胜一筹（因为idea使用的是Javac）。ECJ不仅是Eclipse的默认内置前端编译器，在Tomcat中同样也是使用ECJ编译器来编译jsp文件。
> 

## 二、Class文件结构

> **注意：反编译后的字节码都是以十六进制来显示**
> 

### 1.虚拟机的基石：Class文件

### 1.1 字节码文件里面是什么

> 源代码经过编译器编译之后便会生成一个字节码文件，字节码是一种二进制的类文件，它的内容是JVW的指令，而不像C、C++经由编译器直接生成机器码。
> 

### 1.2 什么是字节码指令

> Java虚拟机的指令由一个字节长度的、代表着某种特定操作含义的
> 
> 
> **操作码**
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%202.png)
> 

### 1.3 Class类的本质

> 任何一个Class文件都对应着唯一一个类或接口的定义信息，但反过来说，Class文件实际上它并不一定以磁盘文件的形式存在。class文件是一组以8位字节为基础单位的**二进制流**。
> 

### 1.4 Class文件格式

- Class 的结构不像XML等描述语言，由于它没有任何分隔符号。所以在其中的数据项，无论是字节顺序还是数量，都是被严格限定的，哪个字节代表什么含义，长度是多少，先后顺序如何，都不允许改变。
- Class文件格式采用一种类似于C语言结构体的方式进行数据存储，这种结构中只有两种数据类型：**无符号数和表。**
    
    > ◦ 无符号数属于基本的数据类型，以u1、u2、u4、u8 来分别代表1个字节、2个字节、4个字节和8个字节的无符号数，无符号数可以用来描述数字、索引引用、数量值或者按照UTF-8编码构成字符串值。
        ◦ 表是由多个无符号数或者其他表作为数据项构成的复合数据类型，所有表都习惯性地以“_info”结尾。表用于描述有层次关系的复合结构的数据，整个Class文件本质上就是一张表。由于表没有固定长度，所以通常会在其前面加上个数说明
    > 

### 1.5 Class文件结构

- 图示以及注释

> 前面u开头加数字代表：几个字节；其他则默认为：n个字节
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%203.png)

- 详细图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%204.png)

### 1.6 可视化查看字节码文件的几种方式

- 一个一个二进制的看。这里用到的是Notepad++,需要安装一个HEX-Editor插件，或者使用Binary Viewer
- 使用javap指令：jdk自带的反解析工具（要在class文件的目录下）
    
    > javap -v xxxx.class
    > 
- 使用IDEA插件：jclasslib或jclasslib bytecode viewer客户端工具。（可视化更好）

### 2.魔数：Class文件的标志

- 作用

> 它的唯一作用是确定这个文件是否为一个能被虚拟机接受的有效合法的Class文件。即:魔数是Class文件的标识符。使用魔数而不是扩展名来进行识别主要是基于安全方面的考虑，因为文件扩展名可以随意地改动。
> 
- 反编译图示

> 可以看到正好占四个字节；魔数值固定为OxCAFEBABE
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%205.png)

### 3.Class文件版本号

- 版本参照图

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%206.png)

- 图示

> 十六进制的34就是十进制的52，即JDK8
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%207.png)

- 注意

> **Java是支持向下兼容的，即高版本的JVM可以识别低版本编译的字节码文件。但反过来就不行了**
> 

### 4.常量池：存放所有常量

- 概述

> • 常量池是Class文件中内容最为丰富的区域之一。常量池对于Class文件中的**字段和方法解析**也有着至关重要的作用。
• 在版本号之后，紧跟着的是常量池的数量，以及若干个常量池表项。
• 常量池中常量的数量是不固定的，所以在常量池的入口需要放置一项u2类型的无符号数，代表常量池容量计数值(constant_pool_count）。与Java中语言习惯不一样的是，**这个容量计数是从1而不是0开始的。**
• 常量池表项中，用于存放编译时期生成的各种**字面量和符号引用**，这部分内容将在类加载后进入**方法区的运行时常量池中存放**
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%208.png)

### 4.1 常量池计数器

> 主要目的：由于常量池的数量不固定，所以就是为了记录常量池表中到底有多少个项
> 
> 
> **可以看到十六进制为0X0013，十进制为19，注意总共有18项（需要减一），索引范围为1~18**
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%209.png)
> 

### 4.2 常量池表

> 表中存放的大多是字面量（Literal）和符号引用（Symbolic References)
> 

### 4.2.1 字面量与符号引用

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2010.png)

- 全限定名

> src目录下开始计算到类名为止：test03Class/Demo。
为了使连续的多个全限定名之间不产生混淆，在使用时最后一般会加入一个“;”表示全限定名结束。
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2011.png)

- 简单名称

> 简单名称是指没有类型和参数修饰的方法或者字段名称，上面例子中的类的add()方法和num字段的简单名称分别是add和num。
> 
- 描述符

> 描述符的作用是用来描述字段的数据类型、方法的参数列表（包括数量、类型以及顺序）和返回值。根据描述符规则，基本数据类型(byte、char、double、float、int、long、short、boolean)以及代表无返回值的void类型都用一个大写字符来表示，而对象类型则用字符L加对象的全限定名来表示，详见下表:
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2012.png)

```java
public static void main(String[] args) {
		Object[] objects = new Object[10];
		System.out.println(objects);
		//	[Ljava.lang.Object;@14ae5a5
	}
```

### 4.2.2 符号引用和直接引用

> 虚拟机在加载Class文件时才会进行动态链接，也就是说，Class文件中不会保存各个方法和字段的最终内存布局信息因此，这些字段和方法的符号引用不经过转换是无法直接被虚拟机使用的。**当嘘虚拟机运行时，需要从常量池中获得对应的符号引用，再在加载过程中的解析阶段将其替换为直接引用，并翻译到具体的内存地址中。**
> 
- 符号引用

> **符号引用以一组符号来描述所引用的目标**，符号可以是任何形式的字面量，只要使用时能无歧义地定位到目标即可。**符号引用与虚拟机实现的内存布局无关，引用的目标并不一定已经加载到了内存中。**
> 
- 直接引用

> **直接引用可以是直接指向目标的指针、相对偏移量或是一个能问接定位到目标的句柄。直接引用是与虚拟机实现的内存布局相关的**，同一个符号引用在不司虚拟机实例上翻i译出来的直接引用一般不会相同。如果有了直接引用，那说明引用的目标必定己经存在于内存之中了。
> 

### 4.3 解析常量池中的各种常量

> 在常量池计数器后开始起，第一个标识慢慢一个一个对应下去（要把十六进制换成十进制）
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2013.png)

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2014.png)

### 5.访问标识（access_flag）

- 概述

> 在常量池后，紧跟着访问标记。该标记使用两个字节表示，用于识别一些类或者接口层次的访问信息，包括:这个Class是类还是接口，是否定义为public类型，是否定义为abstract类型;如果是类的话，是否被声明为final等。
> 

### 5.1 各种访问标记

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2015.png)

### 5.2 对于个别标识说明

1. ACC_INTERFACE

> • 如果一个class文件被设置了ACC_INTERFACE标志，那么同时也得设置ACC_ABSTRACT标志。同时它不能再设置 ACC_FINAL、ACC_SUPER或ACC_ENUM 标志。
• 如果没有设置ACC_INTERFACE标志，那么这个class文件可以具有上表中除 ACC_ANOTATION外的其他所有标志。当然，ACC_FINAL和ACC_ABSTRACT这类互斥的标志除外。这两个标志不得同时设置。
> 
1. ACC_SUPER

> ACC_SUPER标志是为了向后兼容由旧Java编译器所编译的代码而设计的。目前的 ACC_SUPER标志在由JDK 1.0.2之前的编译器所生成的access_flags中是没有确定含义的，如果设置了该标志，那么Oracle的Java虚拟机实现会将其忽略。
> 

### 6.类索引、父类索引和接口索引集合

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2016.png)

- 概述

> 这三项数据来确定这个类的继承关系
> 

### 6.1 类索引

- 概述

> 类索引用于确定这个类的全限定名
> 

### 6.2 父类索引

- 概述

> 父类索引用于确定这个类的父类的全限定名。由于Java语言不允许多重继承，所以父类索引只有一个，除了java.lang.0bject之外，所有的ava类都有父类，因此除了java.lang.0bject外，所有Java类的父类索引都不为0。
> 

### 6.3 接口索引集合

- 概述

> 接口索引集合就用来描述这个类实现了哪些接口，这些被实现的接口将按 implements语句(如果这个类本身是一个接口，则应当是 extends 语句）后的接口顺序从左到右排列在接口索引集合中。
> 
- 组成

> 由于是表结构，所以必须有一个计数器来记录当前表中的项目数即**接口计数器和接口索引集合**
> 

### 7.字段（Field）表集合

- 概述

> 描述接口或类当中声明的变量，即我们每个类中的静态与非静态属性（成员变量）。**不包括什么代码块或方法内部声明的局部变量**
> 
- 注意

> 字段表当中不会出现父类或实现的接口继承而来的字段
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2017.png)

### 7.1 字段表计数器

- 概述

> 用来记录字段表中的字段项数
> 

### 7.2 字段表

- 概述

> 字段表中分为很多个字段项，而每个字段项又分为如下图所示的结构信息
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2018.png)

### 7.2.1 字段表访问标志

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2019.png)

### 7.2.2 字段名的索引

> 根据字段名索引的值，查询常量池中的指定索引项即可。
> 

### 7.2.3 描述符索引

- 概述

> 前面我们涉及了方法的数据类型描述符，**而这个主要针对属性的数据类型描述符**
> 
- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2020.png)

### 7.2.4 属性（attribute）集合

- 概述

> 一个字段还可能拥有一些属性，用于存储更多的额外信息。比如初始化值、一些注释信息等。属性个数存放在attribute_count中，属性具体内容存放在attributes数组中。
其中信息包括：
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2021.png)

- 说明

> 对于常量属性而言，attribute_length值恒为2。
> 

### 8.方法（Method）表集合

- 概述

> • 在字节码文件中，每一个method_info项都对应着一个类或者接口中的方法信息。比如方法的访问修饰符(public、private或protected),方法的返回值类型以及方法的参数信息等。
• 如果这个方法不是抽象的或者不是native的，那么字节码中会体现出来。
• 一方面，methods表只描述当前类或接口中声明的方法，不包括从父类或父接口继承的方法。另一方面，methods表有可能会出现由编译器自动添加的方法，最典型的便是编译器产生的方法信息（比如:类(接口)初始化方法`<clinit>()`和实例初始化方法即构造器`<init>()`）。
> 

### 8.1 方法表

- 概述

> 一个方法表中有很多不同的方法项，方法项的结构如下：
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2022.png)

- 各个结构的内容与字段表中的内容十分相似，**只不过就是描述的对象换成了方法**

### 8.2 方法计数器

> 作用同上
> 

### 9.属性表集合

- 说明

> 这个属性不是我们所说的成员变量之类的东西。而且字段表和方法表都有自带的属性表来存储一些零七零八的东西，**但通过看字节码文件可以看出这部分内容非常多且杂不易阅读**
> 
- 概述

> 方法表集合之后的属性表集合，**指的是class文件所携带的辅助信息**，比如该class文件的源文件的名称。以及任何带有
RetentionPolicy.CLASS或者RetentionPolicy .RUNT工IME的注解。这类信息通常被用于Java虚拟机的验证和运行，以及Java程序的调试，**一般无须深入了解。**
> 

### 9.1 属性表通用格式

- 说明

> 从官方文档查阅，
> 
> 
> **属性表中属性项的类型大概有23种**
> 
> ![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2023.png)
> 

### 9.2 LineNumberTable和LocalVariableTable属性

- LineNumberTable

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2024.png)

- LocalVariableTable

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2025.png)

### 9.3 Code属性

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2026.png)

## 三、Javap指令解析Class文件

### 1.解析字节码文件的作用

> javap是jdk自带的反解析工具。它的作用就是根据class字节码文件，反解析出当前类对应的code区（字节码指令)局部变量表、异常表和代码行偏移量映射表、常量池等信息。通过局部变量表，我们可以查看局部变量的作用域范围、所在槽位等信息，甚至可以看到槽位复用等信息。
> 

### 2.Javac -g操作

> • 解析字节码文件得到的信息中，有些信息（如局部变量表、指令和代码行偏移量映射表、常量池中方法的参数名称等等）需要在使用javac编译成class文件时，指定参数才能输出。
• 比如，你直接javac xx.java，**就不会在生成对应的局部变量表等信息，如果你使用javac -g xx.java就可以生成所有相关信息了**。**如果你使用的eclipse或IDEA，则默认情况下，eclipse、IDEA在编译时会帮你生成局部变量表、指令和代码行偏移量映射表等信息的。**
> 

### 3.Javap的用法

- 格式：

> javap `<options> <classes>`。其中，classes就是你要反编译的class文件。
> 

### 3.1 Javap参数列表

- 参数说明：

> • -version：当前Javap所在的jdk版本信息，不是class文件的版本
• -v：输出较全的信息，不包括私有信息。（想要显示私有的信息在-v后面再加上-p）
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9EClass%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84/image%2027.png)