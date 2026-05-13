# 深入理解Dubbo与实战（二）| Dubbo扩展点加载机制

type: Post
status: Published
date: 2022/08/13
summary: Dubbo扩展点加载机制
tags: Dubbo
category: 中间件

# Dubbo扩展点加载机制

- 概述

> 这章主要就是讲解Dubbo的加载机制以及相关注解的含义；以及最核心的类加载器的ExtensionLoader的工作流程及实现原理。最后介绍扩展中使用的类动态编译的实现原理。
> 

## 1.加载机制概述

- Dubbo拓展性的基石

> • 针对不同使用场景使用了不同的设计模式
• 独特的加载机制，让整个框架的接口和具体实现完全解耦
> 

> Dubbo的SPI（服务接口）是基于Java SPI所做的改进，同时有兼容Java，在服务启动时，Dubbo会查找这些支持扩展的所有实现
> 

### 1.1 Java SPI

- 例子

> 我们可以通过策略模式，来实现一个接口多种实现。我们只声明接口，具体的实现并不在程序中直接确定，而是由程序之外的配置掌控，用于具体实现的装配，代码步骤如下
> 

> 定义一个接口及对应的方法。编写该接口的一个实现类。在META-INF/services/目录下，创建一个以接口全路径命名的文件，如com.test.spi.PrintService文件内容为具体实现类的全路径名，如果有多个，则用分行符分隔。在代码中通过java.util.ServiceLoader来加载具体的实现类。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image.png)

> main方法里通过java. util.ServiceLoader可以获取所有的接口实现，**具体调用哪个实现，可以通过用户定制的规则来决定**
> 

```java
//①.SPI 接口定义
public interface PrintService {
    void printInfo();
}

//②SPI接口实现类
public class PrintServiceImpl implements PrintService{
    @Override
    public void printInfo() {
        System.out.println("Hello, World");
    }

    //③调用SPI具体的实现
    public static void main(String[] args) {
        //上下文类加载器（服务发现机制），破坏双亲委派机制，自由调用我们的代码
        ServiceLoader<PrintService> load = ServiceLoader.load(PrintService.class);
        //获取所有的SPI实现，循环调用
        //printService.printInfo(); printInfo()方法，此处只有一个实现：PrintServiceImpl
        for (PrintService printService : load) {
            printService.printInfo();
        }
    }
}
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%201.png)

### 1.2 扩展点加载机制的改进

- Java SPI加载的缺点

> **JDK的SPI会一次性实例化全部扩展点的所有实现，初始化很耗时，没用上之后也是一种浪费资源**如果扩展加载失败，则连扩展的名称都获取不到了。导致的结果就是根本的错误原因无法显著体现
> 
- Dubbo的改进

> Dubbo SPI只是加载配置文件中的类， 并分成不同的种类缓存在内存中，而不会立即全部初始化，在性能上有更好的表现Dubbo SPI在扩展加载失败的时候会先抛出真实异常并打印日志。扩展点在被动加载的时候，即使有部分扩展加载失败也不会影响其他扩展点和整个框架的使用。增加了对扩展IoC和AOP的支持，一个扩展可以直接setter注入其他扩展
> 
- 例子

> 我们可以把上面的Java SPI的例子该进程Dubbo的
> 
> 1. 在目录META-INF/dubbo/internal下建立配置文件 `com.lhj.dubbo.samples.echo.testDSPI.PrintService`,文件内容如下
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%202.png)
> 
> 1. 使用SPI注解和扩展类加载器进行加载

```java
@SPI("impl")    //为接口类添加SPI注解，设置默认实现为impl
public interface PrintService {
    void printInfo();
}
public class PrintServiceImpl implements PrintService {

    @Override
    public void printInfo() {
        System.out.println("Hello, World with Dubbo");
    }

    public static void main(String[] args) {
        //使用Dubbo自己的扩展类加载器加载
        PrintService printService = ExtensionLoader.getExtensionLoader(PrintService.class).getDefaultExtension();
        printService.printInfo();
    }
}
```

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%203.png)

==关于Dubbo改进的第三点——IOC和AOP==

> Dubbo支持包装扩展类，推荐把通用的抽象逻辑放到包装类中，用于实现扩展点的AOP特性。**举个例子，我们可以看到ProtocolFilterWrapper包装扩展了 DubboProtocol类，一些通用的判断逻辑全部放在了 ProtocolFilterWrapper类的 export方法中，但最终会调用 DubboProtocol#export方法。**
> 

> **这和Spring的动态代理思想一样，在被代理类的前后插入自己的逻辑进行增强，最终调用被代理类。**
> 

### 1.3 扩展点的配置规范

- 概述

> 所谓规范就像我们上面需要在resources中建立与类相同路径的目录和文件。例如：需要在META-INF/dubbo/下放置对应的SPI配置文件，文件名称需要命名为接口的全路径名。配置文件的内容为key=扩展点实现类全路径名（key是SPI注解的传入参数），如果有多个实现类则使用换行符分隔。
> 
- Dubbo SPI配置规范

> 在Dubbo启动的时候，会默认扫这三个目录下的配置文件：`META-INF/services/、META-INF/dubbo/、META-INF/dubbo/internal/`
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%204.png)

### 1.4 扩展点的分类与缓存

- 概述

> Dubbo SPI可以分为Class缓存、实例缓存。
> 
> - Class缓存：Dubbo SPI获取扩展类时，会先从缓存中读取。如果缓存中不存在，则加载配置文件，根据配置把Class缓存到内存中，并不会直接全部初始化。
> - 实例缓存：基于性能考虑，Dubbo框架中不仅缓存Class，也会缓存Class实例化后的对象。每次获取的时候，会先从缓存中读取，如果缓存中读不到，则重新加载并缓存起来。这也是为什么Dubbo SPI相对Java SPI性能上有优势的原因，因为Dubbo SPI缓存的Class并不会全部实例化，而是按需实例化并缓存，因此性能更好。
- 缓存根据不同的特性的在分类

> 普通扩展类、包装扩展类（Wrapper类）、自适应扩展类（Adaptive类）等。
> 
> 1. 普通扩展类。最基础的，配置在SPI配置文件中的扩展类实现。
> 2. 包装扩展类。这种Wrapper类没有具体的实现，只是做了通用逻辑的抽象，并且需要在构造方法中传入一个具体的扩展接口的实现。属于Dubbo的自动包装特性，
> 3. 自适应扩展类。一个扩展接口会有多种实现类，具体使用哪个实现类可以不写死在配置或代码中，在运行时，通过传入URL中的某些参数动态来确定。这属于扩展点的自适应特性，
> 4. 其他缓存，如扩展类加载器缓存、扩展名缓存等。

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%205.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%206.png)

### 1.5 扩展点的特性

- 概述

> 上面缓存的细分类，后对应四个不同的特性：自动包装、自动加载、自适应和自动激活
> 

==自动包装==

> ExtensionLoader在加载扩展时，如果发现这个扩展类包含其他扩展点作为构造函数的参数，则这个扩展类就会被认为是Wrapper类，可以看到ProtocolFilterWrapper本身就继承了Protocol，但构造函数又会注入Protocol
> 

```java
public class ProtocolFilterWrapper implements Protocol {

	private final Protocol protocol;
	public ProtocolFilterWrapper(Protocol protocol) {//实现了 Protocol,但构造函数中又传入了一个 Protocol 类型的参数，框架会自动注入
		if (protocol == null) {
			throw new IllegalArgumentException("protocol == null");
		}
		this.protocol = protocol;
	}
	...
}
```

==自动加载==

> 除了在构造函数中传入其他扩展实例，我们还经常使用setter方法设置属性值。如果某个扩展类是另外一个扩展点类的成员属性，并且拥有setter方法，那么框架也会自动注入对应的扩展点实例。如果扩展类的属性是一个接口，我们应该注入这个接口的那些实现类呢？——自适应
> 

==自适应==

> **在Dubbo SPI中，我们使用@Adaptive注解，可以动态地通过URL中的参数来确定要使用哪个具体的实现类。从而解决自动加载中的实例注入问题。**
> 

> 可以看到下面，当传入URL时，就是自动按照顺序去匹配server的value值，如果匹配上则直接使用对应的实现类，没有则继续匹配transporter的value值。直到匹配上或抛出异常
> 

```java
@SPI(nnetty")
public interface Transporter (
	@Adaptive({Constants.SERVER_KEY, Constants.TRANSPORTER_KEY})
	Server bind(URL url, ChannelHandler handler) throws RemotingException;
}
```

> 可以看见这种方法只能匹配并激活到一个实现类，如果需要多个实现类同时被激活，如Filter可以同时有多个过滤器;或者根据不同的条件，同时激活多个实现类， 如何实现？这就涉及最后一个特性一一自动激活。
> 

==自动激活==

> 使用@Activate注解，可以标记对应的扩展点默认被激活启用。该注解还可以通过传入不同的参数，设置扩展点在不同的条件下被自动激活。主要的使用场景是某个扩展点的多个实现类需要同时启用(比如Filter扩展点)。
> 

## 2.扩展点注解

### 2.1 扩展点注解：@SPI

- 概述

> @SPI注解可以使用在类、接口和枚举类上，Dubbo框架中都是使用在接口上。**它的主要作用就是标记这个接口是一个Dubbo SPI接口，即是一个扩展点，可以有多个不同的内置或用户定义的实现。运行时需要通过配置找到具体的实现类。**
> 
- 源码

> 通过value这个属性，我们可以传入不同的参数来设置这个接口的默认实现类。内部是通过调用`getExtension (Class<T> type. String name)`来获取扩展点接口的具体实现，此时会对传入的Class做校验，判断是否是接口，以及是否有@SPI注解
> 

```java
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE})
public @interface SPI {
	//默认实现的key名称
    String value() default "";
}
```

### 2.2 扩展点自适应注解：@Adaptive

- 概述

> @Adaptive注解可以标记在类、接口、枚举类和方法上，但是在整个Dubbo框架中，只有几个地方使用在类级别上；其余的都是方法级别，可以通过传入URL以及设置的不同key来动态获取真正的实现类（自适应）。**方法级别注解在第一次getExtension时，会自动生成和编译一个动态的Adaptive类（这个类会实现接口有Adaptive注解的方法，就是些抽象的通用逻辑），从而达到动态实现类的效果。**
> 
- Adaptive类

> 这个类主要就是去寻找真正的扩展点实现类，如果获取失败则使用默认的Netty实现，最终调用接口实现的方法
> 
- 标记在实现类上

> 该注解只能标注在某一个实现类上面（多个则会抛异常），并且不再自动生成通用逻辑；这样做的目的其实就是直接指定了实现类，而不用去动态生成代码实现
> 
- 方法级别和类级别在代码上的实现

> 在代码中的实现方式是： ExtensionLoader中会缓存两个与@Adaptive有关的对象，一个缓存在cachedAdaptiveClass中， **即Adaptive具体实现类的Class类型**；另外一个缓存在cachedAdaptivelnstance中，**即Class的具体实例化对象**。在扩展点初始化时，如果发现实现类有@Adaptive注解，则直接赋值给cachedAdaptiveClass ，后续实例化类的时候，就不会再动态生成代码，直接实例化cachedAdaptiveClass，并把实例缓存到cachedAdaptivelnstance中。
> 

> 如果注解在接口方法上， 则会根据参数，动态获得扩展点的实现，会生成Adaptive类，再缓存到cachedAdaptivelnstance 中。
> 
- 源码

> **上面说到自适应的特性时就看到此注解可以设置多个key，以此来匹配；第一遍没有匹配到则会使用驼峰命名在匹配一次，如果还没匹配到则抛异常；如果没有指定key，dubbo则会以方法的名称自动转化为驼峰命名，以此来作为默认实现类的名称**
> 

```java
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.METHOD})
public @interface Adaptive {
	//数组，可以设置多个key,会按顺序依次匹配
    String[] value() default {};
}
```

### 2.3 扩展点自动激活注解：@Activate

- 概述

> @Activate可以标记在类、接口、枚举类和方法上。主要使用在有多个扩展点实现、需要根据不同条件被激活的场景中，如Filter需要多个同时激活，因为每个Filter实现的是不同的功能。@Activate可传入的参数很多
> 
- 注解的默认参数

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%207.png)

## 3.ExtensionLoader 的工作原理

- 概述

> ExtensionLoader是整个扩展机制的主要逻辑类，在这个类里面卖现了**配置的加载、扩展类缓存、自适应对象生成**等所有工作。
> 

### 3.1 工作流程

- 概述

> ExtensionLoader 的逻辑入口可以分为 `getExtension、getAdaptiveExtension、getActivateExtension`三个，分别是获取**普通扩展类、获取自适应扩展类、获取自动激活的扩展类**。总体逻辑都是从调用这三个方法开始的，每个方法可能会有不同的重载的方法，根据不同的传入参数进行调整
> 
- 三者的工作流程图

> 三个入口中,**getActivateExtension对getExtension 的依赖比较重（因为前者只是激活多个符合条件的扩展类，所以只会做一些通用的逻辑判断，例如接口有没有Activate注解，条件是否匹配等，最后还是会调用getExtension方法获得具体扩展点实现类），而getAdaptiveExtension则相对独立**
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%208.png)

- `getExtension (String name）`

> 该方法就是Dubbo扩展强大的核心方法，**实现了一个完整的普通扩展类加载过程。加载过程中的每一步，都会先检查缓存中是否己经存在所需的数据，如果存在则直接从缓存中读取，没有则重新加载（初始化）。这个方法每次只会根据名称返回一个扩展点实现类。**
> 

==createExtension方法流程==

> 
> 
> 1. 框架读取SPI对应路径下的配置文件，并根据配置加载所有扩展类并缓存(不初始化)。
> 2. 根据传入的名称初始化对应的扩展类。
> 3. 尝试查找符合条件的包装类：包含扩展点的setter方法，例如`setProtocol(Protocol protocol)`方法会自动注入protocol扩展点实现；**包含与扩展点类型相同的构造函数，为其注入扩展类实例，例如本次初始化了一个Class A，初始化完成后，会寻找构造参数中需要Class A的包装类(Wrapper)，然后注入Class A实例，并初始化这个包装类。**
> 4. 返回对应的扩展类实例。
- `getAdaptiveExtension（）`

> 与上面的同理，再开始会检查是否有缓存，如果没有则调用createAdaptiveExtension重新初始化
> 

==createAdaptiveExtension方法流程==

> 
> 
> 1. 和getExtension 一样先加载配置文件。
> 2. 生成自适应类的代码字符串。（生成通用逻辑去寻找真正的实现类啊）
> 3. 获取类加载器和编译器，并用编译器编译刚才生成的代码字符串。Dubbo 一共有三种类型的编译器实现
> 4. 返回对应的自适应类实例。

### 3.2 getExtension()的实现原理

- 过程复习

> 
> 
> - getExtension的主要流程就是先检查缓存（双重检查，第一遍不加锁检查，第二遍加锁再检查一边），没有则会调用createExtension开始创建，这里有个特殊点，如果getExtension传入的name是true，则加载并返回默认扩展类
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%209.png)
> 
> - 然后开始会先检查缓存中是否有配置信息，如果不存在扩展类，则会从 `META-INF/services/、META-INF/dubbo/、META-INF/dubbo/internal/`这几个路径中读取所有的配置文件，通过I/O读取字符流，然后通过解析字符串，得到配置文件中对应的扩展点实现类的全称，整个过程的调用顺序为`getExtensionClasses（检查缓存）到loadExtensionClasses（没有缓存，从路径读取并加载class），最后返回Class<?> clazz = getExtensionClasses().get(name);`
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2010.png)
> 
> - 加载完配置信息，再通过反射获得所有扩展实现类并缓存起来。注意，此处仅仅是把Class加载到JVM中，但并没有做Class初始化。在加载Class文件时，会根据Class上的注解来判断扩展点类型，再根据类型分类做缓存。上面这些实在loadExtensionClasses中的loadDirectory中的loadResource中的loadClass方法所做的，
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2011.png)
> 
> - 最后回到createExtension方法，根据传入的name找到对应的类并通过`Class.forName`方法进行初始化，并为其注入依赖的其他扩展类(自动加载特性)。当扩展类初始化后，会检查一次包装扩展类`Set<Class<?>> wrapperclasses`,查找包含与扩展点类型相同的构造函数，为其注入刚初始化的扩展类
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2012.png)
> 
> - 然后我们看看injectExtension这个方法的内部细节，在injectExtension方法中可以为类注入依赖属性,它使用了 `ExtensionFactory#getExtension(Class<T> type, String name)`来获取对应的bean实例；**injectExtension方法总体实现了类似Spring的IoC机制，其实现原理比较简单：首先通过反射获取类的所有方法，然后遍历以字符串set开头的方法，得到set方法的参数类型，再通过ExtensionFactory寻找参数类型相同的扩展类实例，如果找到，就设值进去**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2013.png)
> 

### 3.3 getAdaptiveExtension()的实现原理

- 方法所做的大致工作

> 在getAdaptiveExtension()方法中，会为扩展点接口自动生成实现类字符串，实现类主要包含以下逻辑：为接口中每个有@Adaptive注解的方法生成默认实现(没有注解的方法则生成空实现)，每个默认实现都会从URL中提取Adaptive参数值，并以此为依据动态加载扩展点。然后，框架会使用不同的编译器，把实现类字符串编译为自适应类并返回。
> 
- 生成代码的逻辑步骤

> 
> 
> 1. 生成package、import、类名称等头部信息。此处只会引入一个类ExtensionLoader。 为了不写其他类的import方法，其他方法调用时全部使用全路径。类名称会变为`“接口名称+$Adaptive ”` 的格式。例如：`Transporter 接口 会生成 Transporter$Adpative`。
> 2. 遍历接口所有方法，获取方法的返回类型、参数类型、异常类型等。为第(3)步判断是否为空值做准备。
> 3. 生成参数为空校验代码，如参数是否为空的校验。如果有远程调用，还会添加Invocation参数为空的校验。
> 4. 生成默认实现类名称。如果@Adaptive注解中**没有**设定默认值，则根据类名称生成， 如`YyylnvokerWrapper会被转换为yyy.invoker.wrapper`。生成的规则是不断找大写字母，并把它们用连接起来。得到默认实现类名称后，还需要知道这个实现是哪个扩展点的。
> 5. 生成获取扩展点名称的代码。根据@Adaptive注解中配置的key值生成不同的获取代码，`例如：如果是@Adaptive("protocol"),则会生成 url.getProtocol()`
> 6. 生成获取具体扩展实现类代码。最终还是通过getExtension(extName)方法获取自适应扩展类的真正实现。如果根据URL中配置的key没有找到对应的实现类，则会使用第(4)步中生成的默认实现类名称去找。
> 7. 生成调用结果代码。
> 8. 对代码进行编译，Dubbo中的编译器也是一个自适应接口，但@Adaptive注解是加在实现类AdaptiveCompiler上的。这样一来AdaptiveCompiler就会作为该自适应类的默认实现，不需要再做代码生成和编译就可以使用了（前面我们说到过如果@Adaptive标注在类上，会直接赋值给class缓存，后续都无序生成或者编译，因为有Adaptive的类默认成为了自适应类的实现）。
- 自适应类生成的代码实例

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2014.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2015.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2016.png)

- 注意

> 如果SPI和Adaptive注解上都指定了key，那么以谁为标准呢；`例如：如果一个接口上既@SPI(”impl”)注解，方法上又有@Adaptive(”impl2”)注解`，根据上面代码可知最后是以Adaptive注解传入的key去查找扩展实现类，如果没找到再去SPI，如果SPI也没有则将类名转化为驼峰再去查找
> 

### 3.4 getActivateExtension()的实现原理

- 概述

> 先从它的入口方法说起。`getActivateExtension(URL url, String key, String group)`方法可以获取所有自动激活扩展点。参数分别是URL.URL中指定的key(多个则用逗号隔开)和URL中指定的组信息(group)
> 
- 方法流程

> 
> 
> 1. 检查缓存，如果缓存中没有，则初始化所有扩展类实现的集合。
> 2. 遍历整个@Activate注解集合，根据传入URL匹配条件(匹配group> name等)，得到所有符合激活条件的扩展类实现。然后根据@Activate中配置的before、after、order等参数进行排序
> 3. 遍历所有用户自定义扩展类名称，根据用户URL配置的顺序，调整扩展点激活顺序`(遵循用户在 URL 中配置的顺序，例如 URL 为 test://localhost/test?ext=orderl,default，则扩展点ext的激活顺序会遵循先orderl再default，其中default代表所有有@Activate注解的扩展点)。`
> 4. 返回所有自动激活类集合。
- 注意

> URL的参数如果传入带有`-`开头的，那么对应的扩展点就不会被自动激活。例如：-xxxx,表示名字为xxxx的扩展点不会被激活。
> 
- 总结

> 获取Activate扩展类实现，也是通过getExtension得到的。因此，可以认为getExtension是其他两种Extension的基石。
> 

### 3.5 ExtensionFactory的实现原理

- 概述

> 经过前面的介绍，我们可以知道ExtensionLoader类是整个SPI的核心。但是， ExtensionLoader类本身又是如何被创建的呢？
> 

> 
> 
> 
> 我们知道RegistryFactory工厂类通`@Adaptive({"protocol"})`注解动态查找注册中心实现，根据URL中的protocol参数动态选择对应的注册中心工厂，并初始化具体的注册中心客户端。**而实现这个特性的ExtensionLoader类，本身又是通过工厂方法ExtensionFactory创建的，并且这个工厂接口上也有SPI注解，还有多个实现。**
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2017.png)
> 
- 如何确定使用那个工厂实现ExtensionLoader

> 我们可以看到AdaptiveExtensionFactory上有Adaptive注解，那么这个类就作为默认的实现类
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2018.png)

- 工厂之间的关系图

> 由图可以看到我们除了能从Dubbo管理的容器中获取扩展，还能从Spring中获取
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2019.png)

==Dubbo和Spring容器之间的打通细节==

- `SpringExtensionFactory`的源码分析

> 该工厂提供了保存Spring上下文的静态方法，可以把Spring上下文保存到Set集合中。 当调用getExtension获取扩展类时，会遍历Set集合中所有的Spring上下文，先根据名字依次从每个Spring容器中进行匹配，如果根据名字没匹配到，则根据类型去匹配，如果还没匹配到则返回null
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2020.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2021.png)

- 何时保存Spring上下文

> 那么Spring的上下文又是在什么时候被保存起来的呢？我们可以通过代码搜索得知，在ReferenceBean和ServiceBean中会调用静态方法保存Spring上下文，即一个服务被发布或被引用的时候，对应的Spring上下文会被保存下来。
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2022.png)

==SpiExtensionFactory==

- 作用以及步骤

> 这个工厂主要就是获取扩展点接口对应的Adaptive实现类。`例如：某个扩展点实现类 ClassA 上有@Adaptive注解，则调用 SpiExtensionFactory#getExtension会直接返回ClassA实例`
> 

> 经过一番流转，最终还是回到了默认实现AdaptiveExtensionFactory上，因为该工厂上有@Adaptive注解。这个默认工厂在构造方法中就获取了所有扩展类工厂并缓存起来
> 

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2023.png)

![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2024.png)

> 被AdaptiveExtensionFactory缓存的工厂会通过TreeSet进行排序，**SPI排在前面，Spring排在后面。当调用getExtension方法时，会遍历所有的工厂，先从SPI容器中获取扩展类；如果没找到，则再从Spring容器中查找**。`我们可以理解为，AdaptiveExtensionFactory持有了所有的具体工厂实现，它的getExtension方法中只是遍历了它持有的所有工厂，最终还是调用SPI或Spring工厂实现的getExtension方法`。
> 
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2025.png)
> 

## 4.扩展点动态编译的实现

- 概述

> Dubbo SPI的自适应特性让整个框架非常灵活，而动态编译又是自适应特性的**基础**，因为动态生成的自适应类只是字符串，需要通过编译才能得到真正的Class。**虽然我们可以使用反射来动态代理一个类，但是在性能上和直接编译好的Class会有一定的差距**。
> 

### 4.1 总体结构

- Duboo的三种编译器以及关系

> Dubbo中有三种代码编译器，分别是`JDK编译器、Javassist编译器和AdaptiveCompiler编译器`。这几种编译器都实现了 Compiler接口
> 
> 
> ![image.png](%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3Dubbo%E4%B8%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%BA%8C%EF%BC%89%20Dubbo%E6%89%A9%E5%B1%95%E7%82%B9%E5%8A%A0%E8%BD%BD%E6%9C%BA%E5%88%B6/image%2026.png)
> 
- 修改默认编译器

> Compiler接口上含有一个SPI注解，注解的默认值是@SPI(”javassist”),很明显，**Javassist编译器将作为默认编译器**。如果用户想改变默认编译器，则可以通过`<dubbo:application compiler="jdk" />`标签进行配置。
> 
- 编译器的默认实现

> AdaptiveCompiler上面有^Adaptive注解，**说明AdaptiveCompiler会固定为默认实现**，这个Compiler的主要作用和AdaptiveExtensionFactory相似，**就是为了管理其他Compiler**：通过ExtensionLoader获取对应的编译器扩展类的实现，调用真正的compile做编译
> 

==AbstpactCompiler==

> 它是一个抽象类，无法实例化，但在里面封装了通用的模板逻辑。还定义了一个抽象方法decompile ,留给子类来实现具体的编译逻辑。JavassistCompiler和JdkCompiler都实现了这个抽象方法。
> 
- 抽象模板逻辑

> 通过正则匹配出包路径、类名，再根据包路径、类名拼接出全路径类名。尝试通过Class.forName加载该类并返回，防止重复编译。如果类加载器中没有这个类，则进入第3步。调用doCompile方法进行编译。这个抽象方法由子类实现。
> 

### 4.2 Javassist动态代码编译

- 概述

> Java中动态生成Class的方式有很多，可以直接基于字节码的方式生成，常见的工具库有CGLIB、ASM、Javassist等。而自适应扩展点使用了生成字符串代码再编译为Class的方式。
> 
- 例子

```java
public class test {
    public static void main(String[] args) throws Exception {
	    //初始化Javassist的类池
	    ClassPool aDefault = ClassPool.getDefault();
	    //创建一个Hello World 类
	    CtClass hello_world = aDefault.makeClass("Hello World");
	    //添加一个test方法,会打印Hello World,直接传入方法的字符串
	    CtMethod make = CtNewMethod.make("public static void test(){System.out.println(\\"Hello World\\");}", hello_world);
	    hello_world.addMethod(make);
	    //生成类
	    Class aClass = hello_world.toClass();
	    //通过反射调用这个类实例
	    Object o = aClass.newInstance();
	    Method test = aClass.getDeclaredMethod("test", null);
	    test.invoke(o,null);
    }
}
```

- 步骤总结

> **前面我们说到，如果缓存没有对应的实例，那么就会调用创建方法，其中就会有生成代码字符串的步骤（可回顾3.3.1）**：在JavassistCompiler中，就是不断通过正则表达式匹配不同部位的代码，然后调用Javassist库中的API生成不同部位的代码，最后得到一个完整的Class对象
> 
- JavassistCompiler重写的doCompile方法

> 初始化Javassist,设置默认参数，如设置当前的classpath通过正则匹配出所有import的包，并使用Javassist添加import通过正则匹配出所有extends的包，创建Class对象，并使用Javassist添加extends通过正则匹配出所有implements包，并使用Javassist添加implements通过正则匹配出类里面所有内容，即得到｛｝中的内容，再通过正则匹配出所有方法,并使用Javassist添加类方法。生成Class对象。
> 

### 4.3 JDK动态代码编译

- 概述

> DdkCompiler是Dubbo编译器的另一种实现，使用了 JDK自带的编译器，原生JDK编译器包位于 javax. tools下。主要使用了三个东西：`JavaFileObject 接口、ForwardingJavaFileManager 接口、DavaCompiler.CompilationTask 方法`。
> 
- 过程

> 整个动态编译过程可以简单地总结为：首先初始化一个JavaFileObject对象，并把代码字符串作为参数传入构造方法，然后调用JavaCompiler.CompilationTask方法编译出具体的类。JavaFileManager负责管理类文件的输入/输出位置。
>