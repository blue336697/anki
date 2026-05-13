# Java虚拟机|JVM知识点汇总及简述-＞字节码指令集与解析举例

type: Post
status: Published
date: 2021/09/10
summary: Java字节码对于虚拟机，就好像汇编语言对于计算机，属于基本执行指令。
tags: JVM
category: 虚拟机

# 字节码指令集与解析举例

## 一、概述

- Java字节码对于虚拟机，就好像汇编语言对于计算机，属于基本执行指令。
- Java虚拟机的指令由一个字节长度的、代表着某种特定操作含义的数字（称为操作码，Opcode)以及跟随其后的零至多个代表此操作所需参数（称为操作数，Operands）而构成。由于Java虚拟机采用面向操作数栈而不是寄存器的结构，所以大多数的指令都不包含操作数，只有一个操作码。
- 由于限制了Java虚拟机操作码的长度为一个字节(即0~255），这意味着指令集的操作码总数不可能超过
256 条。
- 熟悉虚拟机的指令对于动态字节码生成、反编译Class文件、Class文件修补都有着非常重要的价值。因此，阅读字节码作为了解Java虚拟机的基础技能，需要熟练掌握常见指令。

### 1.执行模型

- 如果不考虑异常处理的话，那么Java虚拟机的解释器可以使用下面这个伪代码当做最基本的执行模型来理解

```
do{
	自动计算PC寄存器的值加1;
	根据PC寄存器的指示位置，从字节码流中取出操作码;
	if(字节码存在操作数）从字节码流中取出操作数;
	执行操作码所定义的操作;
}while(字节码长度>0);
```

### 2.字节码与数据类型

### 2.1数据类型助记符

> • i代表对int类型的数据操作
• l代表long
• s代表short
• b代表byte
• c代表char
• f代表float
• d代表double
• a代表引用类型
> 

> 注意：**也有一些指令的助记符中没有明确地指明操作类型的字母**，如arraylength指令，它没有代表数据类型的特殊字符，但操作数永远只能是一个数组类型的对象。还有另外一些指令，如无条件跳转指令goto则是与数据类型无关的。
> 

### 3.指令分类

JVM中的字节码指令集按用途大致分成9类，总计200多个

> • 加载与存储指令
• 算术指令
• 类型转换指令
• 对象的创建与访问指令
• 方法调用与返回指令
• 操作数栈管理指令
• 比较控制指令
• 异常处理指令
• 同步控制指令
> 

### 3.1 值相关操作指令注意事项

- 一个指令，可以从局部变量表、常量池、堆中对象、方法调用、系统调用中等取得数据，这些数据（可能是值，可能是对象的引用）被压入操作数栈。
- 一个指令，也可以从操作数栈中取出一到多个值（pop多次），完成赋值、加减乘除、方法传参、系统调用等等操作。

## 二、指令（这一章就不做过多详细的介绍）

### 1.加载与存储指令（最频繁）

- 作用

> 加载和存储指令用于将数据从栈帧的局部变量表和操作数栈之间来回传递。
> 
- 常用指令

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image.png)

- 注意

> 对于这若干组特殊指令来说，它们表面上没有操作数，不需要进行取操作数的动作，但操作数都隐含在指令中。（这样比较省空间）
> 

### 1.1 局部变量压栈指令（load）

- 代码

```java
public void load(int num,Object obj,long count,boolean flag,short[] arr){
        System.out.println(num);
        System.out.println(obj);
        System.out.println(count);
        System.out.println(flag);
        System.out.println(arr);
    }
```

- 字节码指令

> 指令操作码末尾数组超出范围时，改用操作码+操作数的指令
> 

```
 0 getstatic #2 <java/lang/System.out : Ljava/io/PrintStream;>
 3 iload_1
 4 invokevirtual #3 <java/io/PrintStream.println : (I)V>
 7 getstatic #2 <java/lang/System.out : Ljava/io/PrintStream;>
10 aload_2
11 invokevirtual #4 <java/io/PrintStream.println : (Ljava/lang/Object;)V>
14 getstatic #2 <java/lang/System.out : Ljava/io/PrintStream;>
17 lload_3
18 invokevirtual #5 <java/io/PrintStream.println : (J)V>
21 getstatic #2 <java/lang/System.out : Ljava/io/PrintStream;>
24 iload 5
26 invokevirtual #6 <java/io/PrintStream.println : (Z)V>
29 getstatic #2 <java/lang/System.out : Ljava/io/PrintStream;>
32 aload 6
34 invokevirtual #4 <java/io/PrintStream.println : (Ljava/lang/Object;)V>
37 return
```

- 图示过程

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%201.png)

> 注意：图片中忽略了出栈的操作
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%202.png)

### 1.2 常量入栈指令

- 概述

> 常量入栈指令的功能是将常数压入操作数栈，根据数据类型和入栈内容的不同，又可以分为const系列、push系列和ldc指令。不同系列所要表示的数值范围依次增大
> 
- 注意

> 常量入栈指令后面跟的是入栈的值而不是索引位置
> 

### 1.2.1 指令const系列

- 概述

> 指令const系列:用于对特定的常量入栈，入栈的常量隐含在指令本身里。指令有: `iconst_<i>(i从-1到5)`、`lconst_<l>(1从0到1)`、`fconst_<f>(f从e到2)`、`dconst_<d>(d从0到1)`、aconst_null。
> 
- 举例说明

> iconst_m1将-1压入操作数栈;
iconst_x(x为0到5）将x压入栈:
lconst_o、lconst_1分别将长整数0和1压入栈;
fconst_0、fconst_1、 fconst_2分别将浮点数0、1、2压入栈;
dconst_o和dconst_1分别将double型0和1压入栈。
aconst_null将null压入操作数栈;
> 
- 代码举例

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%203.png)

- 指令范围图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%204.png)

### 1.2.2 指令push

- 概述

> 主要包括bipush和sipush。它们的区别在于接收数据类型的不同，bipush接收8位整数作为参数，sipush接收16位整数，它们都将参数压入栈。
> 

### 1.2.1 指令ldc

- 概述

> 指令ldc系列:如果以上指令都不能满足需求，那么可以使用万能的ldc指令，它可以接收一个8位的参数，该参数指向常量池中的int、float或者String的索引，将指定的内容压入堆栈。**类似的还有ldc_w，它接收两个8位参数，能支持的索引范围大于ldc。如果要压入的元素是long或者double类型的,则使用ldc2_w指令**，使用方式都是类似的。
> 

### 1.3 出栈装入局部变量表指令

- 概述

> **出栈装入局部变量表指令用于将操作数栈中栈顶元素弹出后，装入局部变量表的指定位置，用于给局部变量赋值。**
这类指令主要以store的形式存在，比如xstore（x为i、1、f、d、a)、 xstore_n(x为i、1、f、d、a,n为至3）。
> 
> - 其中，指令istore_n将从操作数栈中弹出一个整数，并把它赋值给局部变量索引n位置。
> - 指令xstore由于没有隐含参数信息，故需要提供一个byte类型的参数类指定目标局部变量表的位置。
- 说明

> • 一般说来，类似像store这样的命令需要带一个参数，用来指明将弹出的元素放在局部变量表的第几个位置。但是，为了尽可能压缩指令大小，使用专门的istore_1指令表示将弹出的元素放置在局部变量表第1个位置。类似的还有istore_0、istore_2、istore_3,它们分别表示从操作数栈顶弹出一个元素，存放在局部变量表第0、2、3个位置。
• 由于局部变量表前几个位置总是非常常用，因此这种做法虽然增加了指令数量，但是可以大大压缩生成的字节码的体积。如果局部变量表很大，需要存储的槽位大于3,那么可以使用istore指令，外加一个参数，用来表示需要存放的槽位位
> 

### 2.算术指令

- 作用：

> 算术指令用于对两个操作数栈上的值进行某种特定运算，并把结果重新压入操作数栈。
> 
- 分类：

> 大体上算术指令可以分为两种:对整型数据进行运算的指令与对浮点类型数据进行运算的指令。
> 
- byte、short、 char和boolean类型说明

> 对于这些类型来说Java存在自动转型在计算
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%205.png)

- 运算时溢出

> 例如：分母取0，取余0。都会出现ArithmeticException
> 

```java
//注意这下面两个就不会报ArithmeticException
@Test
public void test01(){
	int i = 10;
	double j = i / 0.0;
	System.out.println(j);//无穷大

    double d1 = 0.0;
	double d2 = d1 / o.0;
	System.out.println(d2); //NaN: not a number
}
```

- 运算模式

> • 向最接近数舍入模式:JVM要求在进行浮点数计算时，所有的运算结果都必须舍入到适当的精度，非精确结果必须舍入为可被表示的最接近的精确值，如果有两种可表示的形式与该值一样接近，将优先选择最低有效位为零的;
• 向零舍入模式:将浮点数转换为整数时，采用该模式，该模式将在目标数值类型中选择一个最接近但是不大于原值的数字作为最精确的舍入结果;
> 
- NaN值的使用

> 当一个操作产生溢出时，将会使用有符号的无穷大表示，如果某个操作结果没有明确的数学定义的话，将会使用NaN值来表示。而且所有使用NaN值作为操作数的算术操作，结果都会返回NaN;
> 

### 2.1 所有算术指令

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%206.png)

- 举例

> **这里假如穿进去的参数为5**
> 

```java
public static int test02(int i){
    return ((i+1)-2)*3/4;
}
```

- 图解过程

> 绿色为局部变量表；蓝色为操作数栈
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%207.png)

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%208.png)

### 2.2 前++与后++

> 首先明确如果标量++完未进行任何的操作或赋值，两者在字节码层面上没有任何区别。例如下面的例子字节码都是完全相同的
> 

```java
public void test03(){
    i++;
    ++i;
    for(int j;j<10;j++){}
    for(int j;j<10;++j){}
}
```

> 但如果是下面的代码就会出现+1的时间不同
> 

```java
public void test04(){
    int i= 10;
    //此时对变量表1的位置加一，而变量表在2的位置上是10
    int a= i++;

    int j = 20;
    //将20放在变量表3的位置然后加一，然后压入栈中，
    //由将栈中的数据放在4的位置，而4就是变量b的位置
    int b = ++j;
}
```

1. 将i=10压入操作数栈
2. 将10弹出移动到局部变量表中索引为1的地方（0的地方为this）
3. 再将10加载到操作数栈
4. 将索引1的地方的值进行+1，为11（i的值为11）
5. 将操作数栈的10弹出放在索引为2的地方（a的值为10）
6. 剩下的同理

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%209.png)

> 同理在思考一道，**从字节码中可以看出在第5行发生了关键的一步，它将局部变量表位置1中的11改为10**
> 

```java
public void test05(){
        int i = 10;
        i = i++;
        System.out.println(i);		//结果还是10
}
```

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2010.png)

### 2.3 比较指令

- 概述

> • 比较指令的作用是比较栈顶两个元素的大小，并将比较结果入栈。
• **比较指令有: dcmpg, dcmpl、 fcmpg、fcmpl、 lcmp。**与前面讲解的指令类似，首字符d表示double类型，f表示float,l表示long。
• 对于double和float类型的数字，由于NaN的存在，各有两个版本的比较指令。以float为例，有fcmpg和fcmpl两个指令，它们的区别在于在数字比较时，若遇到NaN值，处理结果不同。
• 指令dcmpl和dcmpg也是类似的，根据其命名可以推测其含义，在此不再赘述。
• 指令lcmp针对long型整数，由于long型整数没有NaN值，故无需准备两套指令。
> 
- 举例

> **指令fcmpg和fcmpl都从栈中弹出两个操作数，并将它们做比较，设栈顶的元素为v2,栈顶顺位第2位的元素为v1,若v1=v2,则压入0;若v1>v2则压入1;若v1<v2则压入-1。两个指令的不同之处在于，如果遇到NaN值，fcmpg会压入1,而fcmpl会压入-1。**
> 

### 3.类型转换指令

- 类型转换指令可以将两种不同的**数值类型**进行相互转换。
- 这些转换操作一般用于实现用户代码中的**显式类型转换操作**，或者用来处理字节码指令集中数据类型相关指令无法与数据类型一一对应的问题。

### 3.1 宽化类型转换（Widening Numeric Conversions）

1. 转化规则

> 所谓宽化转换即为安全的由小范围到大范围的类型转化；int-->long-->float-->double
> 
> - 从int类型到long、float或者double类型。对应的指令为: i21、i2f、i2d
> - 从long类型到float、double类型。对应的指令为:12f、12d
> - 从float类型到double类型。对应的指令为:f2d
1. 精度损失问题

> • 宽化类型转换是不会因为超过目标类型最大值而丢失信息的，例如，从int转换到 long，或者从int转换到double，都不会丢失任何信息，转换前后的值是精确相等的。
• **从int、long类型数值转换到float，或者long类型数值转换到double时，将可能发生精度丢失—―可能丢失掉几个最低有效位上的值，转换后的浮点数值是根据IEEE754最接近舍入模式所得到的正确整数值。**
• **尽管宽化类型转换实际上是可能发生精度丢失的，但是这种转换永远不会导致Java虚拟机抛出运行时异常。**
> 
1. 补充

> 根据java基础我们知道byte、char和short都占四个字节，在做运算时jvm会自动转型为int。从底层来看就是因为根本没有这三个基本类型的相关转型指令，原因有以下两个：
> 
> - jvm中200多个指令，刚好为一个字节能表示的，如果把这三个类型的指令也加上去，恐怕范围会超出而且不易为后来指令做扩充
> - 因为这三个基本数据类型都占32个位，而int也占32个位，即局部变量表中四个槽位。所以不需要额外的指令不言自明

### 3.2 窄化类型转换（Narrowing Numeric Conversions）

> 就是我们常说的强制类型转换
> 
1. 转化规则

> 注意：如果没有直接类型的转换，会以int为桥梁进行两次转换
> 
> - 从int类型至byte、short或者char类型。对应的指令有: i2b、i2s、i2c
> - 从long类型到int类型。对应的指令有:l2i
> - 从float类型到int或者long类型。对应的指令有: f2i、f21
> - 从double类型到int、long或者float类型。对应的指令有: d2i、d21、d2f
1. 精度损失问题

> • 窄化类型转换可能会导致转换结果具备不同的正负号、不同的数量级，因此，转换过程很可能会导致数值丢失精度。
• **尽管数据类型窄化转换可能会发生上限溢出、下限溢出和精度丢失等情况，但是Java虚拟机规范中明确规定数值类型的窄化转换指令永远不可能导致虚拟机抛出运行时异常**
> 
1. 补充

> • 注意如果byte、short和char类型相互转换，一步就行，等号左边的已经自动转型为int
• 将一个无穷大或小的值转换为某一个基本类型，就会取改基本类型的最大或最小值来表示
• 当将一个浮点值窄化转换为整数类型T (T限于int或long类型之一）的时候，将遵循以下转换规则:如果浮点值是NaN，那转换结果就是int或long类型的0。
• 对于double 类型的 NaN值将按规定转换为float类型的 NaN值。
> 

### 4.对象的创建与访问指令

Java是面向对象的程序设计语言，虚拟机平台从字节码层面就对面向对象做了深层次的支持。有一系列指令专门用于对象操作，可进一步细分为创建指令、字段访问指令、数组操作指令、类型检查指令。

### 4.1 创建指令

虽然类实例和数组都是对象，但Java虚拟机对类实例和数组的创建与操作使用了不同的字节码指令:

- 创建类实例的指令

> 创建类实例的指令: new；它接收一个操作数，为指向常量池的索引，表示要创建的类型，执行完成后，将对象的引用地址压入栈。
> 
- 创建数组的指令

> 创建数组的指令: newarray（创建基本类型数组）、anewarray（创建引用类型数组）、multianewarray（创建多维数组）。
> 
- 代码演示及指令分析

```java
public void test01(){
        Object o = new Object();

        File file = new File("");
}
```

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2011.png)

### 4.2 字段访问指令

- 分类：

> • 访问类字段(static字段，或者称为类变量）的指令: getstatic、putstatic
• 访问类实例字段（非static字段，或者称为实例变量）的指令:getfield、putfield
> 
- 代码举例及字节码指令分析

```java
public void test02(){
        Order order = new Order();
        order.id = 1001;
        System.out.println(order.id);

        order.name = "ORDER" ;
        System.out.println(order.name) ;
}
```

### 4.3 数组操作指令

- 分类：

> 指令大致分为两类：xaload、xastore
> 
> - 把一个数组元素加载到操作数栈的指令: baload、caload、saload、iaload、laload、faload.daload、aaload
> - 将一个操作数栈的值存储到数组元素中的指令: bastore、castore、sastore、iastore、 lastore、fastore、dastore、aastore
> - 取数组长度指令：arraylength，将栈顶的数组引用弹出栈，获取数组的长度并压回栈中
- 步骤说明：

> • 指令xaload表示将数组的元素压栈，**比如saload、caload分别表示压入short数组和char数组。指令xaload在执行时，要求操作数中栈顶元素为数组索引i,栈顶顺位第2个元素为数组引用a,该指令会弹出栈顶这两个元素，并将a[i]重新压入栈。**
• xastore则专门针对数组操作，以iastore为例，它用于给一个int数组的给定索引赋值。**在iastore执行前，操作数栈顶需要以此准备3个元素:值、索引、数组引用，iastore会弹出这3个值，并将值赋给数组中指定索引的位置。**
> 
- 注意：

> 创建数组长度的那个值，压入栈中，随后创建数组的newarray指令压入时，此时长度的值已经出栈即被用过了
> 

### 4.4 类型检查指令

- 指令checkcast用于检查类型强制转换是否可以进行。如果可以进行，那么checkcast指令不会改变操作数栈，否则它会抛出ClasscastException异常。
- 指令instanceof用来判断给定对象是否是某一个类的实例，它会将判断结果压入操作数栈。

> java层面的判别关键字也是instanceof
> 

### 5.方法调用与返回指令

### 5.1 方法调用指令

1. ==invokevirtual指令==：用于调用对象的实例方法，根据对象的实际类型进行分派（虚方法分派），支持多态。这也是Java语言中最常见的方法分派方式。
2. ==invokeinterface指令==：用于调用接口方法，它会在运行时搜索由特定对象所实现的这个接口方法，并找出适合的方法进行调用。
3. ==invokespecial指令==：用于调用一些需要特殊处理的实例方法，包括实例初始化方法（构造器）、私有方法和父类方法。这些方法都是静态类型绑定的，不会在调用时进行动态派发。
4. ==invokestatic指令==：用于调用命名类中的类方法(static方法）。这是静态绑定的。
5. ==invokedynamic指令==：调用动态绑定的方法，这个是JDK1.7后新加入的指令。用于在运行时动态解析出调用点限定符所引用的方法，并执行该方法。前面4条调用指令的分派逻辑都固化在java 虚拟机内部，而invokedynamic指令的分派逻辑是由刖户所设定的引导方法决定的。

> 注意：第1条指令所代表的就是还能够被重写的方法；而3、4条指令则代表的就是不能够被重写的方法
> 
- 代码举例

```java
public class invokeMethod {

    public void test01(){
        //invokeSpecial:
        Date date = new Date();     //情况1：类实例构造器方法: <init>()
        super.toString();       //情况2：调用父类的方法
        test02();           //情况3：私有方法

        //invokeStatic  注意如果private和static一起出现，优先static
        test03();

        //invokeInterface
        Interface01 interface01 = new InterfaceImpl();
        interface01.test05();
        Interface01.test04();   //这里还是invokeStatic，符合优先static原则

        //invokeVirtual
        System.out.println("hello");
        Thread t1 = new Thread();
        t1.run();
    }

    private void test02(){}

    public static void test03(){}
}

interface Interface01{
    public static void test04(){}

    public default void test05(){}
}

class InterfaceImpl implements Interface01{

}
```

### 5.2 方法返回指令

- 分类

> 可根据返回值类型大致分为两类：
> 
> - 包括ireturn（当返回值是boolean、byte、char、short和int类型时使用)、lreturn、freturn、dreturn和areturn
> - 另外还有一条return 指令供声明为void的方法、实例初始化方法以及类和接口的类初始化方法使用

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2012.png)

- 步骤

> • 通过ireturn指令,将当前函数操作数栈的顶层元素弹出，并将这个元素压入调用者函数的操作数栈中（因为调用者非常关心函数的返回值），所有在当前函数操作数栈中的其他元素都会被丢弃。
• 最后，会丢弃当前方法的整个帧，恢复调用者的帧，并将控制权转交给调用者。
> 
- 注意事项

> • 如果当前返回的是synchronized方法，那么还会执行一个隐含的monitorexit指令，退出临界区。
• 这个返回类型不是变量的类型，而是方法的定义时确定的返回类型
> 

### 6.操作数栈管理指令

- 分类

> • 将一个或两个元素从栈顶弹出，并且直接废弃:pop，pop2;
• 复制栈顶一个或两个数值并将复制值或双份的复制值重新压入栈顶:dup，dup2，dup_x1,dup2_x1,dup_x2, dup2_x2;
• 将栈最顶端的两个Slot数值位置交换:swap。Java虚拟机没有提供交换两个64位数据类型（long、double）数值的指令。
• 指令nop,是一个非常特殊的指令，它的字节码为0x00。和汇编语言中的nop一样，它表示什么都不做。这条指令一般可用于调试、占位等。
> 
- 对于复制dup指令的注意事项

> **不带_x的指令是复制栈顶数据并压入栈顶**。包括两个指令，dup和dup2.dup的系数代表要复制的slot个数。
    ◦ dup开头的指令用于复制1个Slot的数据。例如1个int或1个reference类型数据.
    ◦ dup2开头的指令用于复制2个Slot的数据。例如1个long，或2个int，或1个int+1个float类型数据**带_x的指令是复制栈顶数据并插入栈顶以下的某个位置**。共有4个指令, dup_x1, dup2_x1,dup_x2，dup2_x2。对于带_x的复制插入指令，**只要将指令的dup和x的系数相加，结果即为需要插入的位置。**
    ◦ dup_x1插入位置:1+1=2，即栈顶2个slot下面.
    ◦ dup_x2插入位置:1+2=3，即栈顶3个Slot下面.
    ◦ dup2_x1插入位置:2+1=3，即栈顶3个Slot下面.
    ◦ dup2_x2插入位置:2+2=4，即栈顶4个Slot下面
> 
- 说明

> • 对于上述将一个或两个元素弹出栈顶，**准确的来说应该是将一个或两个槽位Slot（一个Slot占4个字节）中的元素弹出**
• 这些指令属于通用型，对栈的压入或者弹出无需指明数据类型。
> 

### 7.控制转移指令

> 控制转移指令一共有五类：条件跳转指令、比较条件跳转指令、比较指令、多条件分支跳转和无条件跳转
> 
> 
> **对于比较指令的介绍请转移至算术指令中的比较指令了解**
> 
- 注意：

> **对于这些指令来说一般都可以将byte、short和char型看成int来处理**
> 

### 7.1 条件跳转指令

- 指令概述

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2013.png)

> 它们的统一含义为：**弹出栈顶元素**，测试它是否满足某一条件，如果满足条件，则跳转到给定位置。跳转的位置给定的是偏移量
> 
- 注意：

> • 对于boolean、byte、char、short类型的条件分支比较操作，都是使用int类型的比较指令完成
• 对于long、float。 double类型的条件分支比较操作，则会先执行相应类型的比较运算指令，运算指令会返回一个整型值到操作数栈中，随后再执行int类型的条件分支比较操作来完成整个分支跳转
> 

### 7.2 比较条件跳转指令

- 概述

> 比较条件跳转指令类似于比较指令和条件跳转指令的结合体，将需要两个步骤的指令合二为一
> 
- 分类

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2014.png)

- 注意

> 这些指令都接收两个字节的操作数作为参数，用于计算跳转的位置。同时在执行指令时，栈顶需要准备两个元素进行比较。指令执行完成后，栈顶的这两个元素被清空，且没有任何数据入栈。如果预设条件成立，则执行跳转，否则，继续执行下一条语句。
> 

### 7.3 多条件分支跳转

- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2015.png)

- 两者区别

> • 指令tableswitch：**要求多个条件分支值是连续的**，它内部只存放起始值和终止值，以及若干个跳转偏移量,
通过给定的操作数index,可以立即定位到跳转偏移量位置，**因此效率比较高**。
• 指令lookupswitch：**内部存放着各个离散的case-offset对**，每次执行都要搜索全部的case-offset对，找到匹配的case值，并根据对应的offset计算跳转地址，**因此效率较低**。
> 
- 说明

> • lookupswitch会对离散的case-offset进行从小到大的严格排序，对于String类型也是根据hash值从小到大排序
• 由于JDK7以后Switch语句引入String类型，由于是String类型所以进行比较时肯定重写了hashcode()方法和equals()方法，先比较hash值如果不一样两者肯定不一样；如果一样则继续比较equals()方法
> 

### 7.4 无条件跳转

- 概述及图示

> 目前主要的无条件跳转指令为goto。指令goto接收两个字节的操作数，共同组成一个带符号的整数，**用于指定指令的偏移量，指令执行的目的就是跳转到偏移量给定的位置处。**
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2016.png)

- 注意
    
    > ◦ 如果指令偏移量太大，超过双字节的带符号整数的范围，则可以使用指令goto_w,它和goto有相同的作用，但是它接收4个字节的操作数，可以表示更大的地址范围。
        ◦ 指令jsr、jsr_w、 ret虽然也是无条件跳转的，但主要用于try-finally语句，**且已经被虚拟机逐渐废弃**，故不在这里介绍这两个指令。
    > 

### 8.异常处理指令

### 8.1 抛出异常指令

- athrow指令

> • 在Java程序中显示抛出异常的操作（throw语句）都是由athrow指令来实现。
• 除了使用throw语句显示抛出异常情况之外，JVM规范还规定了许多运行时异常会在其他Java虚拟机指令检测到异常状况时自动抛出。例如，在之前介绍的整数运算时，当除数为零时，虚拟机会在 idiv或ldiv指令中抛出ArithmeticException异常。**这是看字节码指令表中是没有athrow指令的**
> 
- 注意

> • 正常情况下，操作数栈的压入弹出都是一条条指令完成的。唯一的例外情况是在抛异常时，Java 虚拟机会清除操作数栈上的所有内容，而后将异常实例压入调用者操作数栈上。
• 当在方法上使用throws抛出异常，方法体字节码列表会出现异常表
> 
> 
> ```java
> public void test01(int i) throws RuntimeException{
>         if(i == 1){
>             throw new RuntimeException("拉拉");
>         }
>     }
> ```
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2017.png)

### 8.2 异常处理和异常表

1. 异常处理

> 在Java虚拟机中，处理异常(catch语句）不是由字节码指令来实现的（早期使用jsr、ret指令)，**而是采用异常表来完成的**。
> 
1. 异常表

> • 概述
> 
> 
> 如果一个方法定义了一个try-catch或者try-finally的异常处理，就会创建一个异常表。它包含了每个异常处理或者finally块的信息。异常表保存了每个异常处理信息。比如：**起始位置**、**结束位置**、**程序计数器记录的代码处理的偏移地址**和**被捕获的异常类在常量池中的索引**
> 
> - 代码演示及图示

```java
public void test02(){
        try {
            File file = new File("D:/test.txt");
            FileInputStream fis = new FileInputStream(file);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }catch (RuntimeException e){
            e.printStackTrace();
        }
    }
```

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2018.png)

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2019.png)

> **对于异常表来说每个异常信息都有自己负责的代码区域（会重叠），当发生异常时会立刻被catch到**
> 
1. 相关例题及分析

```java
@Test
    public static String test03( ) {
        String str = "hello";
        try{
            return str;
        } finally{
            str =  "llll";
        }
    }

    public static void main(String[] args) {
        System.out.println(test03());
    }
```

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2020.png)

> 注意：llll的字符串引用也经过处理了，并且最后还抛出了一个异常
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2021.png)

1. 注意

> • **当一个异常被抛出时，JVN会在当前的方法里寻找一个匹配的处理，如果没有找到，这个方法会强制结束并弹出当前枝帧**，并且异常会重新抛给上层调用的方法(在调用方法栈帧)。如果在所有栈帧弹出前仍然没有找到合适的异常处理，这个线程将终止。**如果这个异常在最后一个非守护线程里抛出，将会导致JVM自己终止，比如这个线程是个main线程**。
• **不管什么时候抛出异常，如果异常处理最终匹配了所有异常类型，代码就会继续执行。**在这种情况下。如果方法结束后没有
抛出异常，仍然执行finally块，在return前，它直接跳到finally块来完成目标
> 

### 9.同步控制指令

java虚拟机支持两种同步结构：**方法级的同步**和**方法内部一段指令序列的同步**，这两种同步都是使用monitor（**同步监视器即锁**）来支持的。

### 9.1 方法级的同步

- 概述

> 方法级的同步：**是隐式的**，即无须通过字节码指令来控制，它实现在方法调用和返回操作之中。虚拟机可以从方法常量池的方法表结构中的 ACC_SYNCHRONIZED 访问标志得知一个方法是否声明为同步方法;
> 
- 代码及同步标识

> 注意：有无同步关键字，在字节码层面都是一模一样的，不过只会有同步标识的显示
> 

```java
private int i = 0;
    public synchronized void add(){
        i++;
    }
```

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2022.png)

- 说明

> 当调用方法时，调用指令将会检查方法的ACC_SYNCHRONIZED访问标志是否设置。
> 
> - **如果设置了，执行线程将先持有同步锁，然后执行方法**。最后在方法完成（无论是正常完成还是非正常完成）时释放同步锁。
> - 在方法执行期间，**执行线程持有了同步锁，其他任何线程都无法再获得同一个锁**。
> - **如果一个同步方法执行期间抛出了异常，并且在方法内部无法处理此异常，那这个同步方法所持有的锁将在异常抛到同步方法之外时自动释放。**

### 9.2 方法内指定指令序列的同步

- 代码及案例分析

```java
private int i = 0;
    private Object object = new Object();
    public void test04(){
        synchronized (object){
            i--;
        }
    }
```

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2023.png)

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%AD%97%E8%8A%82%E7%A0%81%E6%8C%87%E4%BB%A4%E9%9B%86%E4%B8%8E%E8%A7%A3%E6%9E%90%E4%B8%BE%E4%BE%8B/image%2024.png)

> 注意：如果处理异常时未到释放锁位置又出现了异常，又会继续跳到处理异常的起点；**即反正一定要将锁的值改为初始值**
>