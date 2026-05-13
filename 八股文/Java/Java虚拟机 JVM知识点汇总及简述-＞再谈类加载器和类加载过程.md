# Java虚拟机|JVM知识点汇总及简述-＞再谈类加载器和类加载过程

type: Post
status: Published
date: 2021/09/11
summary: 在Java中数据类型分为基本数据类型和引用数据类型。基本数据类型由虚拟机预先定义（所以这时你获取类加载器是null，并不引导类加载器的问题，而是已经被预先加载了），引用数据类型（接口、注解、对象、枚举等等）则需要进行类的加载
tags: JVM
category: 虚拟机

## 一、类的加载过程（类的生命周期）详解

### 1.概述

> 在Java中数据类型分为基本数据类型和引用数据类型。**基本数据类型由虚拟机预先定义（所以这时你获取类加载器是null，并不引导类加载器的问题，而是已经被预先加载了），引用数据类型（接口、注解、对象、枚举等等）则需要进行类的加载**
> 
- 类的生命周期（通过类加载器来加载）

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image.png)

- **链接阶段中三个步骤前后顺序一般有所不同：验证与加载一起发生，解析往往在初始化之后发生**

### 2.过程一：加载（Loading）阶段

### 2.1 加载完成的操作

- 加载

> 所谓加载，就是将Java类的字节码文件加载到机器内存中，并在内存中构建出Java类的原型—―类模板对象。类模板对象，其实就是Java类在JVM内存中的一个快照，JVM将从字节码文件中解析出的常量池、类字段、类方法等信息保存到类模板中
> 
- 加载阶段

> 对于JVM来说在加载的时候必须做三件事：（查找并加载类的二进制数据，生成Class的实例）
> 
> 1. 通过类的全名，获取类的二进制数据流。
> 2. 解析类的二进制数据流为方法区内的数据结构（Java类模型)
> 3. 创建java.lang.Class类的实例，表示该类型。作为方法区这个类的各种数据的访问入口

### 2.2 二进制流的获取方式

> 虚拟机可能通过文件系统读入一个class后缀的文件（最常见)读入jar、zip等归档数据包，提取类文件（最常见)事先存放在数据库中的类的二进制数据使用类似于HTTP之类的协议通过网络进行加载在运行时生成一段Class的二进制信息等
> 

总的来说：只要读取的文件符号JVM的文件格式规范即可，如果不是该规范会报ClassFormatError

### 2.3 类模型与Class实例的位置

- 类模型的位置

> 加载的类在JVM中创建相应的类结构，类结构会存储在方法区(JDK1.8之前：永久代；JDK1.8及之后：元空间)。
> 
- Class实例的位置

> 类将**.class**文件加载至**元空间**后，会在堆中创建一个Java.lang.Class对象，用来封装类位于方法区内的数据结构，该Class对象是在加载类的过程中创建的，每个类都对应有一个Class类型的对象。(instanceClass）
> 
- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%201.png)

- 说明

> **Class类的构造方法是私有的，只有JVM能够创建。**
java.lang.Class实例是访问类型元数据的接口，也是实现反射的关键数据、入口。通过Class类提供的接口，可以获得目标类所关联的.class文件中具体的数据结构:方法、字段等信息。
> 

### 2.4 数组类的加载

- 概述

> **创建数组类的情况稍微有些特殊，因为数组类本身并不是由类加载器负责创建，**而是由JVM在运行时根据需要而直接创建的，但数组的元素类型仍然需要依靠类加载器去创建。
> 
- 过程

> 如果数组的元素类型是引用类型，那么就遵循定义的加载过程递归加载和创建数组A的元素类型;JVM使用指定的元素类型和数组维度来创建新的数组类。
> 
- 注意

> 如果数组的元素类型是引用类型，数组类的可访问性就由元素类型的可访问性决定。否则数组类的可访问性将被缺省定义为public。
> 

### 3.过程二：链接（Linking）阶段

- 概述

> 这个阶段还会发送指令重排序，在类的初始化之前完成
> 

### 3.1 验证（Verification）

- 图示过程

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%202.png)

- 说明

> • 其中格式验证会和加载阶段一起执行。验证通过之后，类加载器才会成功将类的二进制数据信息加载到方法区中。
• 格式验证之外的验证操作将会在方法区中进行。
• 虽然检查很耗资源和时间，但避免了运行时会出现的问题。即一次检查，一劳永逸
• 在前面3次检查中，已经排除了文件格式错误、语义错误以及字节码的不正确性。但是依然不能确保类是没有问题的。
> 

### 3.2 准备（Preparation）!!!

- 作用

> 为类的**静态变量**分配内存，并初始化为默认值
> 
- 初始化值如下

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%203.png)

> 注意：
> 
> - 对Boolean值是将其转化为int值为0，而0就代表false
> - 这些默认初始化不包括static final 的情况，因为final关键字在编译时期就会确定下来（因为是常量啊），**而显式初始化会在准备阶段就完成**
>     
>     > 对应每个常量字段的字段表中的ConstantValue这个属性
>     > 
> - 此时还未到java实例对象的初始化，因为new出来才有对象实例啊；但凡有new的任何情况都是特殊情况
- 在链接阶段的准备环节赋值的情况

> • **对于基本数据类型的字段来说，如果使用static final修饰，则显式赋值通常是在链接阶段的准备环节进行**
• **对于String来说，如果使用字面量的方式赋值，使用static final修饰的话，则显式赋值通常是在链接阶段的准备环节进行**
> 

### 3.3 解析（Resolution）

- 作用：

> 将类、接口、字段和方法等的符号引用（在常量池中的那些属性）转化为直接引用
> 
- 总结

> • 所谓解析就是将符号引用转为直接引用，也就是得到类、字段、方法在内存中的指针或者偏移量。因此可以说，**如果直接引用存在，那么可以肯定系统中存在该类、方法或者字段。但只存在符号引用，不能确定系统中一定存在该结构**。
• 链接阶段的解析操作常常会在jvm的初始化阶段后来进行
> 

### 4.过程三：初始化（Initialization）!!!

- 概述

> • 此阶段是类装载的最后一个阶段，到此阶段才会真正的执行java程序代码
• 加载一个类之前都会去加载这个类的子类，因此父类的`<clinit>()`方法以及静态代码块都会优先于子类；总结为：**由父及子，静态先行**。
• 温馨提示：如果想看有哪些父类被加载了，可在junit测试单元中的编辑参数页面或本类的参数页面加入此参数：-XX:+TraceClassLoading
> 
- 作用

> 前面我们提到链接的准备阶段会给静态变量**赋默认初始化值即隐式赋值**，**而初始化阶段会给静态变量显式赋值**
> 
- `<clinit>()`方法

> • **有此方法被调用就代表类被初始化了**，且方法中的代码都执行了
• 该方法仅能由Java编译器生成并由JVM调用，程序开发者无法自定义一个同名的方法，更无法直接在Java程序中调用该方法，虽然该方法也是由字节码指令所组成。
• **它是由类静态成员的赋值语句以及static语句块合并产生的。**
• **未加final关键字的基本都在此赋值**
> 
- 不生成`<clinit>()`方法 的情况

> • 如果一个类中没有任何类变量（静态变量），无论实例变量（非静态变量）赋没赋值都不会有`<clinit>()`方法生成
• 类变量未进行显式赋值
• 加上static final关键字的基本数据类型变成了常量
> 

### 4.1 static final的搭配问题

- 使用static final修饰的字段的显式赋值情况：

> • 在链接阶段的准备环节赋值（字段表中ConstantValue里进行赋值）：
> 
> 1. **对于基本数据类型的字段来说，如果使用static final修饰，则显式赋值（`这里的赋值是指常量赋值，而不是调用方法创建对象等方式`）通常是在链接阶段的准备环节进行**
> 2. **对于String来说，如果使用字面量的方式赋值，使用static final修饰的话，则显式赋值通常是在链接阶段的准备环节进行**
> - 在初始化`<clinit>()`中赋值
- 代码举例例外情况
    
    ```java
    public class InitializationTest(){
        public static int a = 1;//在初始化阶段<clinit>()中赋值
        public static final int INT_CONSTANT = 10;//在链接阶段的准备环节赋值
    
        public static final Integer INTEGER_CONSTANT1 = Integer.valueOf(100);//在初始化阶段<clinit>()中赋值
        public static Integer INTEGER_CONSTANT2 = Integer.valueOf(100);//在初始化阶段<clinit>()中赋值
    
        public static final String so = "helloworld0";//在链接阶段的准备环节赋值
    	public static final String s1 = new String( original: "helloworld1");//在初始化阶段<clinit>()中赋值
    
        public static final int NUM1 = 1;//在链接阶段的准备环节赋值
        public static final int NUM2 = new Random().nextInt(10);//在初始化阶段<clinit>()中赋值
    }
    ```
    
    - 最终结论
    
    > **使用static + final修饰，且显示赋值中不涉及到方法或构造器调用的基本数据类型或String类型的显式赋值，是在链接阶段的准备环节进行（ConstantValue）。**
    > 

### 4.2 `<clinit>()`的线程安全问题

> **因为函数`<clinit>()`带锁线程安全的**，因此，如果在一个类的`<clinit>()`方法中有耗时很长的操作，就可能造成多个线程阻塞，引发死锁。并且这种死锁是很难发现的，因为看起来它们并没有可用的锁信息。
> 

### 4.3 类的初始化：主动使用和被动使用

- 主动使用：会去调用`<clinit>()`方法

> 主动使用的情况如下（对于相关情况的举例可看尚硅谷JVM 275~279）：
> 
> 1. 当创建一个类的实例时，比如使用new关键字，或者通过反射、克隆、反序列化。
> 2. 当调用类的静态方法时，即当使用了字节码invokestatic指令。
> 3. 当使用类、接口的静态字段时(final修饰特殊考虑)，比如，使用getstatic或者putstatic指令（对应访问变量、赋值变量操作）
> 4. 当使用java.lang.reflect包中的方法反射类的方法时。比如: Class.forName( " com.atguigujava.Test")
> 5. 当初始化子类时，如果发现其父类还没有进行过初始化，则需要先触发其父类的初始化。
> 6. 如果一个接口定义了default方法，那么直接实现或者间接实现该接口的类的初始化，该接口要在其之前被初始化。
> 7. 当虚拟机启动时，用户需要指定一个要执行的主类〈包含main()方法的那个类)，虚拟机会先初始化这个主类。
> 8. 当初次调用 MethodHandle实例时，初始化该MethodHandle 指向的方法所在的类。（涉及解析REF_getStatic、REF_putStatic、REF_invokeStatic方法句柄对应的类）
- 被动使用：不会去调用`<clinit>()`方法

> 被动使用的情况如下：
> 
> - 当访问一个静态字段时，只有真正声明这个字段的类才会被初始化。当通过子类引用父类的静态变量，不会导致子类初始化
> - 通过数组定义类引用，不会触发此类的初始化
> - 引用常量不会触发此类或接口的初始化。因为常量在链接阶段就已经被显式赋值了。
> - 调用ClassLoader类的LoadCLass()方法加载一个类，并不是对类的主动使用，不会导致类的初始化。

> **被动使用不会引起类的初始化，也就是说，并不是在代码中出现的类，就一定会被加载或者初始化。如果不符合主动使用的条件，类就不会初始化。**
> 
- 注意：

> 当Java虚拟机初始化一个类时，要求它的所有父类都已经被初始化，但是这条规则并不适用于接口。**因此，一个父接口并不会因为它的子接口或者实现类的初始化而初始化。只有当程序首次使用特定接口的静态字段时，才会导致该接口的初始化。**
> 
> - 在初始化一个类时，并不会先初始化它所实现的接口Ⅰ
> - 在初始化一个接口时，并不会先初始化它的父接口
> - 没有初始化的类，不意味着没有加载!

### 5.过程四：类的使用

> **任何一个类型在使用之前都必须经历过完整的加载、链接和初始化3个类加载步骤**。一旦一个类型成功经历过这3个步骤之后，便“万事俱备，只欠东风”，就等着开发者使用了。开发人员可以在程序中访问和调用它的静态类成员信息（比如:静态字段、静态方法)，或者使用new关键字为其创建对象实例。对于程序员来说，这一过程是我们接触最多的了
> 

### 6.过程五：类的卸载（Unloading）

### 6.1 类、类的加载器、类的实例之间的引用关系

- 概述

> • 在类加载器的内部实现中，用一个Java集合来存放所加载类的引用。另一方面，一个Class对象总是会引用它的类加载器，调用Class对象的[getClassLoader()方法，就能获得它的类加载器。由此可见，代表某个类的Class实例与其类的加载器之间为双向关联关系。
• 一个类的实例总是引用代表这个类的Class对象。在Object类中定义了getClass()方法，这个方法返回代表对象所属类的Class对象的引用。此外，所有的Java类都有一个静态属性class，它引用代表这个类的Class对象。
> 
- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%204.png)

### 6.2 类的生命周期

> • 当Sample类（对于这个Sample类就是最大的Class这个类）被加载、链接和初始化后，它的生命周期就开始了。当代表Sample类的Class对象不再被引用，即不可触及时，Class对象就会结束生命周期，Sample类在方法区内的数据也会被卸载，从而结束Sample类的生命周期。
• **一个类何时结束生命周期，取决于代表它的Class对象何时结束生命周期。**从图上可知一个大的Class对象被回收的条件需要断很多条指针才可以
> 

### 6.3 类的卸载

1. 启动类加载器加载的类型在整个运行期间是不可能被卸载的(jvm和jls规范)
2. 被系统类加载器和扩展类加载器加载的类型在运行期间不太可能被卸载，因为系统类加载器实例或者扩展类的实例基本上在整个运行期间总能直接或者间接的访问的到，其达到unreachable的可能性极小。
3. 被开发者自定义的类加载器实例加载的类型只有在很简单的上下文环境中才能被卸载，而且一般还要借助于强制调用虚拟机的垃圾收集功能才可以做到。可以预想，稍微复杂点的应用场景中(比如:很多时候用户在开发自定义类加载器实例的时候采用缓存的策略以提高系统性能)，被加载的类型在运行期间也是几乎不太可能被卸载的(至少卸载的时间是不确定的)。
    
    > 综合以上三点，一个已经加载的类型被卸载的几率很小至少被卸载的时间是不确定的。同时我们可以看的出来，开发者在开发代码时候，不应该对虚拟机的类型卸载做任何假设的前提下，来实现系统中的特定功能。
    > 

## 二、再谈类的加载器

### 1.概述

> 类加载器是JVM执行类加载机制的前提，是Java的核心组件
> 

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%205.png)

### 1.1 显式加载与隐式加载

- 代码举例

```java
public class UserTest {
	public static void main(String[ ] args) {
		User user = new User(); //隐式加载
		try {
			class clazz = Class.forName(" com.atguigu.java.User");//显式加载
			ClassLoader.getSystemCLassLoader( ).loadClass( name: "com.atguigu.java.User" );//显式加载
        }catch (classNotFoundException e) {
			e.printstackTrace();
		}
	}
}
```

### 1.2 命名空间

- 类的唯一性

> 对于任意一个类，**都需要由加载它的类加载器和这个类本身一同确认其在Java虚拟机中的唯一性**。每一个类加载器，都拥有一个独立的类名称空间：**比较两个类是否相等，只有在这两个类是由同一个类加载器加载的前提下才有意义**。否则，即使这两个类源自同一个Class文件，被同一个虚拟机加载，只要加载他们的类加载器不同，那这两个类就必定不相等。
> 
- 命名空间

> • 每个类加载器都有自己的命名空间，命名空间由该加载器及所有的父加载器所加载的类组成
• **在同一命名空间中，不会出现类的完整名字（包括类的包名）相同的两个类**
• 在不同的命名空间中，有可能会出现类的完整名字（包括类的包名）相同的两个类
> 

### 1.3 类加载机制的基本特征

- 双亲委派模型。但不是所有类加载都遵守这个模型，有的时候，启动类加载器所加载的类型，是可能要加载用户代码的，比如JDK内部的ServiceProvider/ServiceLoader机制，用户可以在标准API框架上，提供自己的实现，JDK也需要提供些默认的参考实现。
    
    > 例如，Java 中NDI、JDBC、文件系统、Cipher等很多方面，都是利用的这种机制，这种情况就不会用双亲委派模型去加载，而是利用所谓的上下文加载器。
    > 
- 可见性，子类加载器可以访问父类加载器加载的类型，但是反过来是不允许的。不然，因为缺少必要的隔离，我们就没有办法利用类加载器去实现容器的逻辑。
- 单一性，由于父加载器的类型对于子加载器是可见的，所以父加载器中加载过的类型，就不会在子加载器中重复加载。但是注意，类加载器“邻居”间，同一类型仍然可以被加载多次，因为互相并不可见。

### 2.ClassLoader源码分析

- ClassLoader与现有类加载器的关系

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%206.png)

> 如果想要更加了解内部原理等可以直接看ClassLoader的源码及运作过程
> 
- 启动类加载器、扩展类加载器和应用类加载器之间的层级关系

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%207.png)

> 注意：这里的层级关系并不是父类的意思，类似于谁由谁加载的关系
> 

### 2.1 ClassLoader的主要方法

1. loadClass()

> **该方法就是体现双亲委派机制的最佳例子，代码源码如下：**
> 
> 
> ```java
> //resolve为true要加载class的同时进行解析操作
> protected Class<?> loadClass(String name, boolean resolve)
>      throws ClassNotFoundException
>  {
>      synchronized (getClassLoadingLock(name)) {	//同步操作，保证只能被加载一次
>          // 首先判断在缓存中是否以及加载过同名的类
>          Class<?> c = findLoadedClass(name);
>          if (c == null) {
>              long t0 = System.nanoTime();
>              try {
>                  //获取当前类加载器的父类加载器
>                  if (parent != null) {
>                      //如果父类加载器存在，就调用父类加载器进行类的加载
>                      c = parent.loadClass(name, false);
>                  } else {
>                      //如果加载器的父类加载器为空，则调用此方法让引导类加载器进行加载
>                      c = findBootstrapClassOrNull(name);
>                  }
>              } catch (ClassNotFoundException e) {
>                  // ClassNotFoundException thrown if class not found
>                  // from the non-null parent class loader
>              }
> 
>              if (c == null) {	//当前类的加载器的父类加载器为加载过此类 或者 当前类的加载器未加载此类
>                  //	调用当前ClassLoader的findClass()
>                  long t1 = System.nanoTime();
>                  c = findClass(name);
> 
>                  // this is the defining class loader; record the stats
>                  sun.misc.PerfCounter.getParentDelegationTime().addTime(t1 - t0);
>                  sun.misc.PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
>                  sun.misc.PerfCounter.getFindClasses().increment();
>              }
>          }
>          if (resolve) {	//是否进行解析操作
>              resolveClass(c);
>          }
>          return c;
>      }
>  }
> ```
> 
1. findClass()

> • 作用：
		查找二进制名称为name的类，返回结果为java.lang.Class类的实例。这是一个受保护的方法，JVM鼓励我们重写此方法，需要自定义加载器遵循双亲委托机制，该方法会在检查完父类加载器之后被loadClass()方法调用。
• 注意：
	**一般情况下，在自定义类加载器时，会直接覆盖ClassLoader的findClass()方法并编写加载规则，取得要加载类的字节码后转换成流，然后调用defineClass()方法生成类的Class对象。**
> 
1. defineClass()

> • 作用：
根据给定的字节数组b转换为Class的实例，off和1en参数表示实际Class信息在byte数组中的位置和长度，其中byte数组b是ClassLoader从外部获取的。这是受保护的方法，只有在自定义ClassLoader子类中可以使用。
• 注意：
**defineClass()方法通常与findClass()方法一起使用，一般情况下，在自定义类加载器时，会直接覆盖ClassLoader的findClass()方法并编写加载规则，取得要加载类的字节码后转换成流，然后调用defineClass()方法生成类的Class对象**
> 

### 2.2 URLClassLoader

> ClassLoader是一个抽象类，很多方法是空的没有实现，比如 findClass()、findResource()等。**而URLClassLoader这个实现类为这些方法提供了具体的实现**。并新增了URLClassPath类协助取得Class字节码流等功能。**在编写自定义类加载器时，如果没有太过于复杂的需求，可以直接继承URLClassLoader类，这样就可以避免自己去编写findClass()方法及其获取字节码流的方式，使自定义类加载器编写更加简洁。**
> 

### 2.3 Class.forName()与ClassLoader.loadClass()的区别

- Class.forName()

> 此方法是一个静态方法，根据传入类的全限定类名返回一个Class对象，方法除了加载此对象，还会在clinit方法中初始化
> 
- ClassLoader.loadClass()

> 此方法是一个实例方法，需要new一个ClassLoader对象来调用，并且只会加载此Class，不会初始化直到第一次使用此Class
> 

### 3.再谈双亲委派机制

### 3.1 定义与本质

- 说明

> 类加载器用来把类加载到Java虚拟机中。**从JDK1.2版本开始**，类的加载过程采用双亲委派机制，这种机制能更好地保证Java平台的安全。
> 
- 定义

> 如果一个类加载器在接到加载类的请求时，它首先不会自己尝试去加载这个类，而是把这个请求任务委托给父类加载器去完成，依次递归，如果父类加载器可以完成类加载任务，就成功返回。只有父类加载器无法完成此加载任务时，才自己去加载。
> 
- 本质

> 规定了类加载的顺序是:引导类加载器先加载，若加载不到，由扩展类加载器加载，若还加载不到，才会由系统类加载器或自定义的类加载器进行加载。
> 
- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%208.png)

### 3.2 优势与劣势

- 优势

> 避免类的重复加载，保护程序安全，防止核心API被篡改。这些优势的体现就是每一次都会检查此类是否以及被加载过了，而且就算有同名API越往上找，肯定能够被检查到，核心的API肯定早就被加载过了，同名冒牌的也不会充当真的
> 
- 思考

> 如果将寻找父类的类加载器这一步骤抹除，自定义的类加载器重写的loadClass方法能够加载核心API吗：
> 
> 
> **还是不行的**，因为JDK还有一层保障，不管是自定义的类加载器，还是系统类加载器抑或扩展类加载器，最终都必须调用java.lang.ClassLoader.defineClass(String, byte[], int, int,ProtectionDomain)方法，**而该方法会执行preDefineClass()接口，该接口中提供了对JDK核心类库的保护。**
> 
- 劣势

> **检查类是否加载的委托过程是单向的，这个方式虽然从结构上说比较清晰**，使各个ClassLoader的职责非常明确，但是同时会带来一个问题，即顶层的ClassLoader无法访问底层的ClassLoader所加载的类。**应用类访问系统类是没有问题，但是系统类访问应用类就会出现问题。**
> 
- 结论

> 但是JDK规范中并没有明确加载机制必须使用双亲委派机制，只是建议使用
> 

### 3.3 破坏双亲委派机制

- 第一类

> 在交替更换JDK1.2时，新版本为老版本向下兼容代码，导致可以在老版本重写loadClass方法，从而避免双亲委派机制
> 
- 第二类

> 由于这个机制自身的结构问题导致，我们都知道越基本的Class类就由越高的类加载器加载，而用户的代码是由底层加载器加载的，如果此时基本Class类想要调用用户代码，按照双亲委派机制是行不通的，此时Java引入了线程上下文类加载器（服务发现机制），就可以自由调用所需的代码。这是一种父类加载器去请求子类加载器完成类加载的行为，**这种行为实际上是打通了双亲委派模型的层次结构来逆向使用类加载器，已经违背了双亲委派模型的一般性原则。**
> 
- 第三类

> 第三类是由于用户对于程序动态性的追求，例如鼠标的热拔插，用户想要将每次重启所需要的加载类时间降到最低甚至没有，此时就有一个新技术叫模块化热部署，让全部类结构分成一个一个的模块，使每个模块都有自己的一个类加载器，这样使原来的树状结构，变为了网状结构
> 
- 破坏的好处（弥补局限性）

> 但是使用双亲委派也存在一定的局限性，在正常情况下，用户代码是依赖核心类库的，所以按照正常的双亲委派加载流程是没问题的；
但是在加载核心类库时，如果需要使用用户代码，双亲委派流程就无法满足；
> 

例如：

> 比如在使用JDBC时， 利用DriverManager.getConnection获取连接时，就会存在这样的问题。
> 

> DriverManager是由根类加载器Bootstrap加载的，在加载DriverManager时，会执行其静态方法，加载初始驱动程序，也就是Driver接口的实现类；但是这些实现类基本都是第三方厂商提供的，根据双亲委派原则，第三方的类不可能被根类加载器加载。
> 

### 3.4 代码热替换

- 概述

> 热替换是指在程序的运行过程中，不停止服务，只通过替换程序文件来修改程序的行为。热替换的关键需求在于服务不能中断，修改必须立即表现正在运行的系统之中。基本上大部分脚本语言都是天生支持热替换的，比如: PHP，只要替换了PHP源文件，这种改动就会立即生效，而无需重启web服务器。
> 
- 图示

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%209.png)

### 4.再谈沙箱（sandbox）安全机制

- 概述

> 沙箱机制就是将**Java代码限定在虚拟机（JVM）特定的运行范围中，并且严格限制代码对本地系统资源（CPU、内存、文件系统和网络）访问**。通过这样的措施来保证对代码的有限隔离，防止对本地系统造成破坏。
> 
- 作用

> 就是一句话：保证程序安全，保护Java原生的JDK代码
> 

### 5.自定义类的加载器

### 5.1 为什么要自定义类加载器

- 隔离加载类

> 在某些框架内进行中间件与应用的模块隔离，把类加载到不同的环境。不同的容器空间中对应用进行隔离
> 
> - 比如:阿里内某容器框架通过自定义类加载器确保应用中依赖的jar包不会影响到中间件运行时使用的jar包。
> - 再比如:Tomcat这类web应用服务器，内部自定义了好几种类加载器，用于隔离同一个web应用服务器上的不同应用程序。（类的仲裁-->类冲突)
- 修改类加载的方式

> 类的加载模型并非强制，除引导类加载器外，其他的加载并非一定要引入，或者根据实际情况在某个时间点进行按需进行动态加载
> 
- 扩展加载源

> 从各种流媒体终端加载二进制流
> 
- 防止源码泄露

> Java代码容易被编译和篡改，可以进行编译加密。那么类加载也需要自定义，还原加密的字节码。
> 

### 5.2 实现方式

- 概述

> 自定义加载器的父类是系统类加载器
> 
- 步骤
1. Java提供了抽象类java.lang.ClassLoader，所有用户自定义的类加载器都应该继承ClassLoader类
2. 在自定义ClassLoader的子类时候，我们会有两种方式进行自定义：重写loadClass()或重写findClass()方法
- 建议：

> **这里建议采用重写findClass()方法，因为这样不会破坏双亲委派机制的稳定结构**
> 
> 
> 当然你也可以重写loadClass()方法，将双亲委派机制留下来，不过这样就有点“脱裤子放屁了”
> 
- 代码演示

> 加载器类
> 

```java
import java.io.*;

public class MyClassLoader extends ClassLoader{
    private String byteCodePath;

    public MyClassLoader(String byteCodePath) {
        this.byteCodePath = byteCodePath;
    }

    public MyClassLoader(ClassLoader parent, String byteCodePath) {
        super(parent);
        this.byteCodePath = byteCodePath;
    }

    @Override
    protected Class<?> findClass(String className) throws ClassNotFoundException {
        BufferedInputStream bis = null;
        ByteArrayOutputStream baos = null;
        try {
            //获取字节码文件的完整路径
            String fileName = byteCodePath + className+".class";
            //获取一个输入流
            bis = new BufferedInputStream(new FileInputStream(fileName));
            //获取一个输出流
            baos = new ByteArrayOutputStream();

            //具体读入并写出的过程
            int len;
            byte[] b1 = new byte[1024];
            while((len=bis.read(b1))!=-1){
                baos.write(b1,0,len);
            }
            //获取内存中完整的字节数据
            byte[] bytes = baos.toByteArray();
            //调用defineClass方法，将字节数组的数据转化为Class实例
            Class clazz = defineClass(null, bytes, 0, bytes.length);
            return clazz;
        } catch (IOException e) {
            e.printStackTrace();
        }finally {
            try {
                if(baos!=null && bis!=null){
                    baos.close();
                    bis.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }

        }
        return null;
    }
}
```

> 测试类
> 

```java
public class LoaderTest {
    public static void main(String[] args) {
        MyClassLoader myClassLoader = new MyClassLoader("D:/");

        try {
            Class clazz = myClassLoader.loadClass("RuntimeHeap");
            System.out.println("加载此类的加载器为："+clazz.getClassLoader());
            System.out.println("此类加载器的父类为："+clazz.getClassLoader().getParent());
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
```

结果

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%2010.png)

### 6.JDK9的新特性

1. 扩展机制被移除，扩展类加载器由于向后兼容性的原因被保留，不过被重命名为平台类加载器(platform classloader）。可以通过classLoader的新方法getPlatformClassLoader()来获取。

> JDK9时基于模块化进行构建（原来的 rt.jar和 tools.jar被拆分成数十个JMOD文件），其中的Java类库就已天然地满足了可扩展的需求，那自然无须再保留〈JAVA_HONE>\liblext目录，此前使用这个目录或者 java.ext.dirs系统变量来扩展JDK功能的机制已经没有继续存在的价值了。
> 
1. 平台类加载器和应用程序类加载器都不再继承自java.net.URLClassLoader。现在启动类加载器、平台类加载器、应用程序类加载器全都继承于jdk.internal.loader.**BuiltinClassLoader**。

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%2011.png)

1. 在Java 9中，类加载器有了名称。该名称在构造方法中指定，可以通过getName()方法来获取。平台类加载器的名称是platform，应用类加载器的名称是app。类加载器的名称在调试与类加载器相关的问题时会非常有用。
2. 启动类加载器现在是在jvm内部和java类库共同协作实现的类加载器（以前是C++实现)，但为了与之前代码兼容在获取启动类加载器的场景中仍然会返回null，而不会得到BootClassLoader实例。
3. 类加载的委派关系也发生了变动。当平台及应用程序类加载器收到类加载请求，在委派给父加载器加载前，要先判断该类是否能够归属到某一个系统模块中，如果可以找到这样的归属关系，就要优先委派给负责那个模块的加载器完成加载。

![image.png](Java%E8%99%9A%E6%8B%9F%E6%9C%BA%20JVM%E7%9F%A5%E8%AF%86%E7%82%B9%E6%B1%87%E6%80%BB%E5%8F%8A%E7%AE%80%E8%BF%B0-%EF%BC%9E%E5%86%8D%E8%B0%88%E7%B1%BB%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%92%8C%E7%B1%BB%E5%8A%A0%E8%BD%BD%E8%BF%87%E7%A8%8B/image%2012.png)