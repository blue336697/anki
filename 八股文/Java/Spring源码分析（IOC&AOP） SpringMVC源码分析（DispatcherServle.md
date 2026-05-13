# Spring源码分析（IOC&AOP）| SpringMVC源码分析（DispatcherServlet）| Mybatis相关考点（缓存）

type: Post
status: Published
date: 2022/07/04
summary: 是一种设计思想，就是将原本在程序中手动创建对象的控制权，交由Spring框架来管理。IOC容器是Spring用来实现IOC的载体，IOC容器实际上就是个Map(key,value)，Map中存放的是各种对象。
tags: Spring
category: 技术栈

# Spring

## 1.IOC and AOP

==IOC（Inverse of Control:控制反转）==：是一种设计思想，就是将原本在程序中手动创建对象的控制权，交由Spring框架来管理。IOC容器是Spring用来实现IOC的载体，IOC容器实际上就是个Map(key,value)，Map中存放的是各种对象。

- 优点

> **将对象之间的相互依赖关系交给IoC容器来管理，并由IoC容器完成出来对象的注入。这样可以很大程度上简化应用的开发，把应用从复杂的依赖关系中解放出来。IoC容器就像是一个工厂一样，当我们需要创建一个对象的时候，只需要配置好配置文件/注解即可，完全不用考虑对象是如何被创建出来的。**
> 

> • 控制：控制体现在对于创建对象的控制权交给Spring框架来管理
• 反转：就是将我们程序员的创建对象和注入依赖的这个动作交由IOC容器来触发
> 

==AOP==：

> 所谓AOP就是面向切面变成编程,，够将那些与业务无关，却为业务模块所共同调用的逻辑或责任(例如事务管理、日志管理、权限控制)封装起来，便于减少系统的重复代码，降低模块间的耦合度，并有利于未来的可拓展性和可维护性。
> 

==Spring AOP==：

> 通过代理的方式，在调用想要的对象方法时候，进行拦截处理，执行切入的逻辑，然后再调用真正的方法实现。**如果要代理的对象，实现了某个接口，那么Spring AOP会使用JDK Proxy,去创建代理对象，而对于没有实现接口的对象(有些类单类，不去实现接口)，就无法使用JDK Proxy去进行代理，这时候Spring AOP会使用Cglib，生成一个被代理对象的子类来作为代理。**
> 

## 2.源码阅读

### 2.1 AbstractApplicationContext（其中包括Bean的生命周期）

- 概述

> 对于容器的具体实现和操作的基本功能就是这个类来定义，这个类间接实现了`BeanFactory和ApplicationContext`，对于BeanFactory来说其实就是容器的具体实现，帮助我们创建管理对象
> 

==容器初始化（刷新）之Refresh方法：==
`第一步：prepareRefresh()`

> 初始化一些属性。校验属性的合法性保存容器刷新的一些早期事件：设置logger啊。
> 

`第二步：beanFactory()`

> 创建beanFactory（通过CAS的过程去创建）
> 

`第三步：prepareBeanFactory(beanFactory);`

> 给 beanFactory 添加一些属性和组件，设置Bean的加载器、添加Bean的后置处理器啊（上下文感知器、监听器）、注册依赖项、忽略依赖项、然后会根据你的配置文件的相关配置注册对应的单例对象到beanFactory
> 

`第四步：postProcessBeanFactory(beanFactory);`

> 子类实现该方法进行自定义逻辑
> 

`第五步：invokeBeanFactoryPostProcessors(beanFactory);`

> 执行 beanFactory 的后置处理器。主要包括 BeanFactoryPostProcessor 和 BeanDefinitionRegistryPostProcessor
> 

`第六步：registerBeanPostProcessors(beanFactory);`

> 注册所有的 BeanPostProcessors 到 beanFactory
> 

`第七步：initMessageSource();`

> 初始化 MessageSource 组件，主要用于国际化，消息绑定解析等
> 

`第八步：initApplicationEventMulticaster();`

> 初始化 ApplicationEventMulticaster 事件多播器，用于事件的广播
> 

`第九步：onRefresh();`

> 空方法，子类可以实现该方法自定义逻辑例如 SpringMVC 在该方法初始化了八大组件，Tomcat 在该方法创建启动。
> 

`第十步：registerListeners();`

> 注册 Listeners 监听器，监听之间多播器的内容
> 

`第十一步：finishBeanFactoryInitialization(beanFactory)`（ 完成工厂的初始化，bean 的生命周期）

1. 通过 `getBean()` 获取类的 `BeanDefinition` 定义信息。
2. `BeanDefinition` 定义信息中存储了对象的各种属性。
3. 通过 `createBean()` 方法真正创建对象。
4. 先调用 `Instantiation` 前后的 `BeanPostProcessor` 后置处理器
5. 如果有实现各种 `xxxAware` 接口的则设置一些值。
6. 然后执行初始化方法，初始化前后又有`Initialization`的后置处理器

> （1） AOP 功能就在此处实现：
（2）通过 `AnnotationAwareAspectJAutoProxyCreator` 会调用 `postProcessAfterInitialization()` 方法
（3）该后置处理器会检查生成的对象是否是需要增强的对象
（4）如果是，则保存它的所有增强方法，并创建一个代理对象返回
（5）之后对该对象的获取，其实是获取了它的代理对象
（6）执行方法时会被拦截器，将该代理对象的所有增强方法包装成一个拦截器链，进行链式调用
> 
1. 最后给该对象注册销毁方法
2. 穿件完成之后，将单例对象加入到单例池中

`第十二步：finishRefresh();`

> 完成刷新，清理一些内容。
> 

### 2.2 AOP之动态代理

- 概述

> 两者的都明显的区别就是一个是基于接口动态代理的，一个是基于类动态代理的，其实所谓的动态代理就是代理类需要增强方法或者逻辑业务，又或者代理类需要被包装一个去调用远程的方法等
> 

### 1.JDK动态代理

- 概述

> 在springboot2.0版本以后默认的动态代理为CGLIB，JDK动态代理是基于接口实现的
> 
- 实现过程

> 通过实现InvocationHandler得到一个切面类然后利用 Proxy 糅合目标类的类加载器、接口和切面类得到一个代理类。代理类的逻辑就是执行切入逻辑，把所有接口方法的调用转发到 InvocationHandler 的 invoke() 方法上，然后根据反射调用目标类的方法。
> 
- 总结

> 大致就是生成的代理类通过反射得到所有的方法并存入静态变量中，并且将静态变量缓存了起来，然后调用代理类的方法其实就是调用了invoke方法，这个invoke就会最终执行到被代理类的方法
> 

==newProxyInstance方法详解==：

1. 得到被代理类接口的克隆副本
2. 执行getProxyClass0方法，传入的是被代理类的加载器和接口方法（方法太多会抛异常），在方法中会执行proxyClassCache的`get`方法
3. 然后在方法中会先从缓存（是一个map，key是被代理类的类加载器，value是一个引用队列）中获取是否以前执行过，缓存过；这里主要就是让其缓存起来，并将生成的代理类返回（如果为空则更新缓存）

> 这里就是说明为啥JDK必须用接口进行代理，get方法中会通过上面缓存作为key去获取二级缓存，去过为null则会根据实现类的接口来生成二级缓存的key，其中生成方法为`apply`，主要做了三件事**①.生成文件名，②.生成代理的字节码数组，③.生成对应class**
> 
1. 拿到代理类之后，得到代理类的构造器以及构造器需要传入的参数
2. 设置传入的执行器
3. 然后会检查方法的权限修饰符是不是public的，如果不是public则会设置成public的（给予一个特权）
4. 然后返回通过构造器的newInstance方法创建的代理类并返回代理类（通过反编译得到代理类的全限定类名为`com.sun.proxy.$Proxy0`）

==invoke方法详解==：

1. 通过返回的代理类调用代理类方法，实际上就是调用invoke方法，invoke方法会调用方法类的invoke方法并将被代理类传入
2. 进来先回检查你实现处理器接口有没有重写里面的invoke方法，其实就是为了确认访问的权限
3. 获取方法执行器，为空就创建一个
4. **然后调用执行器的invoke方法，最里层调用的是执行器的实现类（NativeMethodAccessorImpl）的invoke方法，其中会记录调用次数，并且会获取方法的类，方法的名字等，最后通过反射机制将这些静态变量、方法（toString等）都进行初始化**
5. **然后调用当前执行器的实现类的父类（DelegatingMethodAccessorImpl）的setDelegate将执行器传入，然后该代理类会实现我们的接口，并重写里面的方法，根据我们的被代理类重新**
6. 最后返回invoke0方法的执行结果，这个直接就跳到目标执行方法开始执行了

==JDK 动态代理为什么要有接口==：

> 通过我们的分析主要就是代理类将被代理类和执行器关联起来
> 
> - 我们先考虑如何将执行器和代理类关联起来，在源码中代理类会继承父类 Proxy，并把 InvocationHandler 存在父类的对象中，那么由于是单继承
> - 所以代理类会通过实现被代理类接口来重写方法，将代理类和被代理类关联起来已达到方法扩展增强

### 2.CGLIB动态代理

- 概述

> 不适用springboot时要通过引入依赖来使用CGLIB，CGLIB 是基于ASM 字节码生成工具，它是通过继承的方式来实现代理类，所以要注意 final 方法，这种方法无法被继承。**简单理解下，就是生成代理类的子类，通过字节码技术动态拼接成一个子类，在其中织入切面的逻辑。**
> 
- 代码实例

```java
public class CglibProxyTest {

    public static void main(String[] args) {
        Dog proxy = CglibProxy.createProxy(Dog.class);
        proxy.bark();
    }
}

class Dog {

    void bark() {
        System.out.println("汪汪汪...");
    }
}

class CglibProxy {

    /**
     * 可以为任意对象创建代理类， 不需要实现接口
     * 相当于为代理类在字节码中创建一个子类，直接操作字节码
     * @param clazz
     * @param <T>
     * @return
     */
    public static <T> T createProxy(Class<T> clazz) {
        // 1. 创建一个增强器
        Enhancer enhancer = new Enhancer();

        // 2. 设置父类
        enhancer.setSuperclass(clazz);

        // 3. 设置回调方法，执行方法目标方法前会被该拦截器拦截
        enhancer.setCallback(new MethodInterceptor() {
            @Override
            public Object intercept(Object o, Method method, Object[] objects, MethodProxy methodProxy) throws Throwable {

                System.out.println("cglib 代理...");
                // 真正执行目标方法，要调用invokeSuper，因为目标类是该类的父类
                Object res = methodProxy.invokeSuper(o, objects);
                return res;
            }
        });

        return (T) enhancer.create();
    }
}
```

### 3.两者的区别

JDK基于接口与CGLib基于继承

==①.JDK和CGLib的区别==

> • JDK动态代理只能对实现了接口的类生成代理，而不能针对类
• CGLib是针对类实现代理，主要是对指定的类生成一个子类，覆盖其中的方法（继承）
> 

==②.Spring在选择用JDK还是CGLib的依据==

> • 当Bean实现接口时，Spring就会用JDK的动态代理
• 当Bean没有实现接口时，Spring使用CGLib来实现
> 

> 可以强制使用CGLib（在Spring配置中加入`<aop:aspectj-autoproxy proxy-target-class=“true”/>`）
> 

==③.JDK和CGLib的性能对比==

> • 使用CGLib实现动态代理，CGLib底层采用ASM字节码生成框架，使用字节码技术生成代理类，在JDK1.6之前比使用Java反射效率要高。唯一需要注意的是，CGLib不能对声明为final的方法进行代理，因为CGLib原理是动态生成被代理类的子类。
• 在JDK1.6、JDK1.7、JDK1.8逐步对JDK动态代理优化之后，在调用次数较少的情况下，JDK代理效率高于CGLib代理效率，只有当进行大量调用的时候，JDK1.6和JDK1.7比CGLib代理效率低一点，但是到JDK1.8的时候，JDK代理效率高于CGLib代理
> 

### 2.3 拦截器（链）

- 概述

> 对于拦截器是非常能体现AOP思想的组件，spring为该组件设立了很多拦截点，比如使用`@Before、@After、@AfterReturning、@AfterThrowing` 等等。**方便我们在目标方法执行前、后、抛错等地方进行一些逻辑的切入。**默认切入的实现是cglib
> 
- 拦截链（chain）

> 上面说了这么多的拦截点，spring是如何让他们配合的，这就引入了拦截链，对应注解都有不同的拦截器实现，将不同的拦截器加入到一个集合，然后使用一个CglibMethodInvocation的类封装，调用其proceed方法将拦截链传入
> 

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image.png)

==proceed方法==：

> 在方法中主要看到对于索引的递增，来获取不同的拦截器；宏观上是一个调用invoke方法的递归，通过调用invoke来让索引递增（从-1开始，每次加1），那么一层一层的可以看到就是链的样子
> 

```java
public Object proceed() throws Throwable {
        if (this.currentInterceptorIndex == this.interceptorsAndDynamicMethodMatchers.size() - 1) {
            return this.invokeJoinpoint();
        } else {
            Object interceptorOrInterceptionAdvice = this.interceptorsAndDynamicMethodMatchers.get(++this.currentInterceptorIndex);
            if (interceptorOrInterceptionAdvice instanceof InterceptorAndDynamicMethodMatcher) {
                InterceptorAndDynamicMethodMatcher dm = (InterceptorAndDynamicMethodMatcher)interceptorOrInterceptionAdvice;
                //调用拦截器的执行方法，拦截器执行拦截逻辑后继续调用目标方法的proceed()方法，参考下面的两个拦截器invoke()实现
                return dm.methodMatcher.matches(this.method, this.targetClass, this.arguments) ? dm.interceptor.invoke(this) : this.proceed();
            } else {
                return ((MethodInterceptor)interceptorOrInterceptionAdvice).invoke(this);
            }
        }
    }
```

- 拦截器的内部实现

> 我们拿MethodBeforeAdviceInterceptor这个拦截器来举例子，根据名字就可以知道执行的是前置拦截，
> 
> 
> **里面的invoke方法执行前置逻辑，并且调用proceed方法进行递归调用**
> 
> ![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%201.png)
> 

```java
public class MethodBeforeAdviceInterceptor implements MethodInterceptor, Serializable {
    private MethodBeforeAdvice advice;

    public MethodBeforeAdviceInterceptor(MethodBeforeAdvice advice) {
        Assert.notNull(advice, "Advice must not be null");
        this.advice = advice;
    }

    public Object invoke(MethodInvocation mi) throws Throwable {
        this.advice.before(mi.getMethod(), mi.getArguments(), mi.getThis());
        return mi.proceed();
    }
}
```

**ExposeInvocationInterceptor拦截器:**

> 该拦截器可以看到是索引第一个调用的，作用其实就是创建拦截链的封装对象并存入threadLocal，后面调用这个对象就非常方便了
> 

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%202.png)

**Spring AOP 和 AspectJ 有什么区别**：

> **Spring AOP 是动态代理，AspectJ支持更多种代理这里我们用的其静态代理。**
从一个是运行时织入，一个在编译时织入，我们稍微一想到就能知道，编译时就准备完毕，那么在调用时候没有额外的织入开销，性能更好些。
> 

> 且 AspectJ 提供完整的 AOP 解决方案，像 Spring AOP 只支持方法级别的织入，而 AspectJ 支持字段、方法、构造函数等等，所以它更加强大，当然也更加复杂。
> 

### 1.过滤器 (Filter) 和 拦截器 (Interceptor)

- 概述

> 两者均体现了AOP织入的思想，他们的不同主要体现在以下的几个方面
> 

==实现原理：==

> • 过滤器 是基于函数回调的；
• 拦截器 则是基于Java的反射机制（动态代理）实现的。
> 

==使用范围：==

> • 过滤器Filter 的使用要依赖于Tomcat等容器，导致它只能在web程序中使用。
• 拦截器(Interceptor) 它是一个Spring组件，并由Spring容器管理，并不依赖Tomcat等容器，是可以单独使用的。
> 

==触发时机不同：==

> • 过滤器Filter是在请求进入容器后，但在进入servlet之前进行预处理，请求结束是在servlet处理完以后。
• 拦截器 Interceptor 是在请求进入servlet后，在进入Controller之前进行预处理的，Controller 中渲染了对应的视图之后请求结束。
> 

### 2.4 循环依赖

### 1.问题概述

- 依赖概述

> 如下图，例如两个Bean相互依赖，例如A要依赖B，发现B还没创建然后开始创建B，创建B的时候发现又要依赖A，而A此时等着B创建好，所以就隔着卡Bug
> 

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%203.png)

- 如何解决

> **依赖的 Bean 必须都是单例依赖注入的方式，必须不全是构造器注入，且 beanName 字母序在前的不能是构造器注入**
> 
- 为什么必须是单例

> 在Bean工厂的具体抽象类中有一个叫做doGetBean的方法去根据Bean的名称、要求返回的类型、参数等创建一个Bean对象，其中就有一个判断如下图是不允许多例也就是说只支持单例，**A需要B，B也需要未创建完成的A，**我们的解决的方案就是就是将还未初始化完全的A放入一个map中，然后A需要B，B创建时会拿到这个A先完成初始化然后回过头在初始化A
> 

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%204.png)

> 如果两个Bean是原型模式下的多例，会造成更严重的循环依赖，**A1需要B1，B1需要A2，A2需要B2会这样一直循环下去**
> 
- 为什么不能全是构造器注入

==Spring创建对象的三个步骤==：

> 我们可以先分析以下Spring创建对象的三个步骤
> 
> 1. 实例化，createBeanInstance，就是 new 了个对象
> 2. 属性注入，populateBean， 就是 set 一些属性值
> 3. 初始化，initializeBean，执行一些 aware 接口中的方法，initMethod，AOP代理等

`如果全是构造器注入`：

> 比如A(B b)，**那表明在 new 的时候，就需要得到 B**，此时需要 new B ，但是 B 也是要在构造的时候注入 A ，即B(A a)，这时候 B 需要在一个 map 中找到不完整的 A ，发现找不到。因为A此时还没new完呢
> 

`如果一个setter，一个构造器就一定能成功吗？`：

> 此时其实是成功的，避免了A未能new完的窘境；**实例化 A 之后，此时可以在 map 中存入 A，开始为 A 进行属性注入，发现需要 B，此时 new B，发现构造器需要 A，此时从 map 中得到 A ，B 构造完毕，B 进行属性注入，初始化，然后 A 注入 B 完成属性注入，然后初始化 A。**
> 

`如果先构造器，在setter呢？`：

> 如果先构造器，此时A还是没有实例化完的所以没有放入map中，因为A需要B，创建B时map中没有即拿不到；**但是如果根据上面的让B先setter就可以解决，但是spring规定一般加载是根据对象名的字典序来的**
> 

### 2.全过程解析（AbstractBeanFactory）及三级缓存源码

- 概述

> 上面我们说到，为了解决相互依赖，会创建一个map存放未初始化好的对象，在spring中这个map实际上有三个，称为三级缓存分别为如下：
> 
> - `第一级：singletonObjects`：用于存放完全初始化好的bean，从该缓存中取出的bean可以直接使用。
> - `第二级：earlySingletonObjects`：存放原始的bean对象(尚未填充属性)，用于解决循环依赖
> - `第三级：singletonFactories`：**存放bean工厂对象，存储能建立这个 Bean 的一个工厂，通过工厂能获取这个 Bean，延迟化 Bean 的生成，工厂生成的 Bean 会塞入二级缓存**
- **`getBean()的doGetBean()的getSingleton()方法`**
1. 首先，获**取单例 Bean 的时候会通过 BeanName 先去 singletonObjects（一级缓存） 查找完整的 Bean，如果找到则直接返回**，否则进行步骤 2。
2. **看对应的 Bean 是否在创建中，如果不在直接返回找不到，如果是，则会去 earlySingletonObjects （二级缓存）查找 Bean，如果找到则返回**，否则进行步骤 3
3. 去 **singletonFactories （三级缓存）通过 BeanName 查找到对应的工厂，如果存着工厂则通过工厂创建 Bean ，并且放置到 earlySingletonObjects 中。**如果三个缓存都没找到，则返回 null。

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%205.png)

==doCreateBean方法==：

> 可以看到有两个时间点会返回null，当返回null时说明此时是没有需要的bean的，那么就会调用该方法进行创建进行三步初始化步骤；该方法是一个抽象方法具体是它的抽象子类`AbstractAutowireCapableBeanFactory`来完成的，**一般有三个参数，一个是bean的名字，一个是bean的相关结构等，还有一个是参数**，具体过程如下
> 
1. 在方法中会先创建实例的包装器，然后是在同步代码块中进行实例化的
2. 实例化后会检查当前实例化的对象是否为单例、是否允许循环引用、是否正在被创建中
3. 全部为true则会往 `singletonFactories（三级缓存）` 塞入一个工厂，而调用这个工厂的 getObject 方法，就能得到这个 Bean。此时并不知道会不会发送依赖，反正注入就完事了即`提前暴露`

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%206.png)

1. **然后开始属性注入开始填充（populateBean方法），实例A发现有别的对象实例B需要注入，就会跳到需要对象的流程重复此过程，同样实例B到了填充阶段会去从第一到三级缓存去查，查到三级查到了。并且通过上面提前在三级缓存里暴露的工厂得到 A，然后将这个工厂从三级缓存里删除，并将 A 加入到二级缓存中。**

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%207.png)

1. 然后B开始初始化的最后阶段，完成后返回到A这里，此时B已经在一级缓存中了
2. **这时候就回到了 A 的属性注入，此时注入了 B，接着执行初始化，最后 A 也会被加到一级缓存里，且从二级缓存中删除 A。**

**为什么循环依赖需要三级缓存，二级不够吗？：**

> 可以发现在创建Bean的过程中其实对于三级缓存来说有点多余，**在实例化 Bean A 之后，我在二级 map 里面塞入这个 A，然后继续属性注入，发现 A 依赖 B 所以要创建 Bean B，这时候 B 就能从二级 map 得到 A ，完成 B 的建立之后， A 自然而然能完成。**
> 

> 我们需要回到上面的第三步，添加Bean工厂到三级缓存中的`getEarlyBeanReference`方法中，由下图可以看到如果后者不满足为false，返回的对象传进来是啥返回去就是啥，那么这个`InstantiationAwareBeanPostProcessors` ，可以很明显的看出来是与代理相关的。
> 

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%208.png)

> 那么我们想要直接拿到的是代理对象，也就是说如果 A 需要被代理，那么 B 依赖的 A 是已经被代理的 A，所以我们不能返回 A 给 B，而是返回代理的 A 给 B。这个工厂的作用其实就是判断对象是否需要代理；可是这个工作其实二级缓存也能做啊，但是细想就是就类似于延迟加载的需求，结合Bean的生命周期
> 

> **当执行后置处理器的时候，执行器会看对象是不是一个需要增强的对象，如果是则要触发动态代理生成代理对象，而如果你放在二级缓存就进行代理其实是破坏了 Bean 定义的生命周期。**
> 

==总结==：

> 所以 Spring 先在一个三级缓存放置一个工厂，如果产生循环依赖，那么就调用这个工厂提早得到代理对象，如果没产生依赖，这个工厂根本不会被调用，所以 Bean 的生命周期就是对的。
> 

## 3.其他相关考点

### 3.1 Bean的作用域

- ==singleton==：默认是单例，含义不用解释了吧，一个 IOC 容器内部仅此一个
- ==prototype==：原型，多实例
- ==request==：每个请求都会新建一个属于自己的 Bean 实例，这种作用域仅存在 Spring Web 应用中
- ==session==：一个 http session 中有一个 bean 的实例，这种作用域仅存在 Spring Web 应用中
- ==application==：整个 ServletContext 生命周期里，只有一个 bean，这种作用域仅存在 Spring Web 应用中
- ==websocket==：一个 WebSocket 生命周期内一个 bean 实例，这种作用域仅存在 Spring Web 应用中

### 3.2 Spring的注入方式

- 构造器注入，Spring 倡导构造函数注入，因为构造器注入返回给客户端使用的时候一定是完整的。
- setter 注入，可选的注入方式，好处是在有变更的情况下，可以重新注入。
- 字段注入，就是平日我们用 @Autowired 标记字段
- 方法注入，就是平日我们用 @Autowired 标记方法
- 接口回调注入，就是实现 Spring 定义的一些内建接口，例如 BeanFactoryAware，会进行 BeanFactory 的注入

==@Autowired和@Resource的区别==：

> **@Autowire默认按照类型装配**，默认情况下它要求依赖对象必须存在如果允许为null，可以设置它required属性为false，如果我们想使用按照名称装配，可以结合@Qualifier注解一起使用;
> 

> **@Resource默认按照名称装配**，当找不到与名称匹配的bean才会按照类型装配，可以通过name属性指定，如果没有指定name属性，当注解标注在字段上，即默认取字段的名称作为bean名称寻找依赖对象，当注解标注在属性的setter方法上，即默认取属性名作为bean名称寻找依赖对象.
> 

> 注意：如果没有指定name属性，并且按照默认的名称仍然找不到依赖的对象时候，会回退到按照类型装配，但一旦指定了name属性，就只能按照名称装配了.
> 

==@Autowire 标注在字段上和构造方法上的区别==

> 放在字段上是通过set方法注入；
放在构造器上是通过构造方法注入；
> 

### 3.3 Spring（boot）事务

### 1.spring事务传播级别

- 概述

> 对于spring的事务而言其实就是最好的AOP理念的体现，**会生成开启事务方法的代理对象，在获取该对象操作时，会执行代理对象的方法，先设置事务为非自动提交，然后开启事务，最后提交事务或者回滚事务。**
> 
- 事务的传播级别

> **所谓传播级别，就是当某个方法调用其他方法，其他方法的事务要不要跟调用方用同一个事务**
> 

> `REQUIRED`：如果当前存在事务，则加入该事务，不存在则创建一个新的事务，spring默认的事务传播级别
`SUPPORTS`：如果当前存在事务，加入该事务，不存在则以非事务的方式运行
`MANDATORY`：如果当前存在事务，加入该事务，不存在则抛出异常
`REQUIRES_NEW`：创建一个新的事务，如果当前存在事务则挂起
`NOT_SUPPORTED`：非事务方式运行，有事务则挂起
`NEVER`：非事务方式运行，存在事务则抛出异常
`NESTED`：如果当前存在事务，则创建⼀个事务，作为当前事务的嵌套事务来运⾏
> 

### 2.spring boot的事务实现

- 概述

> 首先通过 `@EnableTransactionManagement` 注解会为容器倒入一个 `TransactionManagementConfigurationSelector` 的选择器，也就是对事务的自动配置，会为需要事务处理的对象生成代理对象，通过拦截器 `TransactionInterceptor` 拦截进行调用，主要会进入拦截器的`invoke`方法。
> 

==事务注意事项==：

> **就是因为采用生成代理对象的形式，那么调用同一个服务的方法（同一对象中）时无论你被调用的方法采用什么设置都不会采纳，全部跟随调用方的事务走，因为你等于绕过了代理对象**，但如果识别的服务（同一对象）就按照被调用的来，因为每个方法的代理对象都不一样啊！
> 

`解决`：

> 将AOP默认采用的动态代理切换为AspectJ就可以了，AspectJ是比JDK原生动态代理和Cglib更加强大的AOP思想的动态代理框架，有兴趣的可以自行了解
> 

### 3.4 SpringBoot 自动装配原理详解

- 流程

> 入口处就是main函数启动的SpringBootApplication注解，其中EnableAutoConfiguration注解是完成自动注解的主力军EnableAutoConfiguration会加载对应的装配类对象AutoConfigurationImportSelector这个类实现的接口中的selectImports方法这个方法首先会检查是否看起自动装配的配置（默认开启）然后调用getAutoConfigurationEntry来获取每个jar包META-INF/spring.factories下的全限定类名找到要装配的类全部加载所有的依赖肯定是不现实的，所以后续会进行过滤，比如Jar破损、不符合注解的条件等等都会被过滤
> 

# SpringMVC

- 概述

> Spring MVC 是基于 Servlet API 构建的，可以说核心就是 `DispatcherServlet`，即一个前端控制器。强大的组件构成。由这几个组件让我们与 Servlet 解耦，不需要写一个个 Servlet ，基于 Spring 的管理就可以很好的实现 web 应用，简单，方便。
> 
- 重要组件

> 处理器映射、控制器、视图解析器等。
> 

## 1.Spring MVC 具体的工作原理

- 当一个请求过来的时候，由 `DispatcherServlet` 接待，它会根据处理器映射`（HandlerMapping）`找到对应的 `HandlerExecutionChain`（这里面包含了很多定义的 `HandlerInterceptor`，拦截器）。
- 然后通过`HandlerAdapter`适配器的适配（适配器模式了解一下）后，执行 `handler`，即通过 `controller` 的调用，返回 `ModelAndView`。
- 然后 `DispatcherServlet` 解析得到 `ViewName`，将其传给 `ViewResoler` 视图解析器，解析后获得 `View` 视图。
- 然后 `DispatcherServlet` 将 `model` 数据填充到`view` ，得到最终的 `Responose` 返回给用户。
- 我们常用的视图有 `jsp、freemaker、velocity` 等。

## 2.SpringMVC执行流程（DispatcherServlet）

- DispatcherServlet的架构

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%209.png)

### 1.doDispatch 的代码细节

```java
protected void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
		HttpServletRequest processedRequest = request;
		HandlerExecutionChain mappedHandler = null;
		boolean multipartRequestParsed = false;

		WebAsyncManager asyncManager = WebAsyncUtils.getAsyncManager(request);

		try {
			ModelAndView mv = null;
			Exception dispatchException = null;

			try {
				//检查当前请求是否为文件上传请求
				processedRequest = checkMultipart(request);
				multipartRequestParsed = (processedRequest != request);

				// Determine handler for the current request.
				//该方法就是找到是那个controller来处理请求
				//HandlerMapping：处理器映射。/xxx->>xxxx，处理器的信息都在这里面
				mappedHandler = getHandler(processedRequest);
				if (mappedHandler == null) {
					//如果没有找到那个处理器（控制器），能处理这个请求就404，抛出异常
					noHandlerFound(processedRequest, response);
					return;
				}

				// Determine handler adapter for the current request.
				//拿到能执行这个类的所有方法的适配器AnnotationMethodHandlerAdapter
				//适配器可以理解为反射工具
				HandlerAdapter ha = getHandlerAdapter(mappedHandler.getHandler());

				// Process last-modified header, if supported by the handler.
				String method = request.getMethod();
				boolean isGet = "GET".equals(method);
				if (isGet || "HEAD".equals(method)) {
					long lastModified = ha.getLastModified(request, mappedHandler.getHandler());
					if (new ServletWebRequest(request, response).checkNotModified(lastModified) && isGet) {
						return;
					}
				}

				if (!mappedHandler.applyPreHandle(processedRequest, response)) {
					return;
				}

				// Actually invoke the handler.
				//处理器（控制器）的方法被调用，所以目标方法执行了
				//控制器（Controller），处理器（Handler）
				//使用刚才得到的代理工具即适配器来执行这个方法
				//将目标方法执行完成后的返回值作为视图名，保存到ModelAndView中
				//目标方法无论怎么写，最终适适配器执行完后都是将执行后的信息封装成ModelAndView
				mv = ha.handle(processedRequest, response, mappedHandler.getHandler());

				if (asyncManager.isConcurrentHandlingStarted()) {
					return;
				}

				//如果没有视图名设置一个默认的视图名
				applyDefaultViewName(processedRequest, mv);
				mappedHandler.applyPostHandle(processedRequest, response, mv);
			}
			catch (Exception ex) {
				dispatchException = ex;
			}
			catch (Throwable err) {
				// As of 4.3, we're processing Errors thrown from handler methods as well,
				// making them available for @ExceptionHandler methods and other scenarios.
				dispatchException = new NestedServletException("Handler dispatch failed", err);
			}
			//这个方法是转发到目标页面
			//6.根据方法最终执行完成后封装的ModelAndView，转发到对应页面
			//而且ModelAndView中的数据可以从请求域中获取
			processDispatchResult(processedRequest, response, mappedHandler, mv, dispatchException);
		}
		catch (Exception ex) {
			triggerAfterCompletion(processedRequest, response, mappedHandler, ex);
		}
		catch (Throwable err) {
			triggerAfterCompletion(processedRequest, response, mappedHandler,
					new NestedServletException("Handler processing failed", err));
		}
		finally {
			if (asyncManager.isConcurrentHandlingStarted()) {
				// Instead of postHandle and afterCompletion
				if (mappedHandler != null) {
					mappedHandler.applyAfterConcurrentHandlingStarted(processedRequest, response);
				}
			}
			else {
				// Clean up any resources used by a multipart request.
				if (multipartRequestParsed) {
					cleanupMultipart(processedRequest);
				}
			}
		}
	}
```

### 2.doDispatch的执行文字流程

根据代码流程可知请求被拦截以后进入到doDispatch()后，在该方法中的大致流程是这样的：

1. getHandler()根据当前请求地址找到能处理这个请求的目标处理器类（即自己写的处理器）根据当前请求在HandlerMapping中找到这个请求的映射信息，获取到目标处理器类
2. getHandlerAdapter()根据当前处理器类获取到能执行这个处理器方法的适配器，根据当前处理器类，找到当前类的HandlerAdapter（适配器）
3. 使用刚才获取到的适配器（RequestMappingHandlerAdpter）执行目标方法
4. 目标方法执行后会返回一个ModelAndView对象（最难的步骤）
5. 根据ModelAndView的信息转发到具体页面，并可以在请求域取出中ModelAndView中的模型数据

### 3.更多细节

如果你是spring的新版本
**AnnotationMethodHandlerAdapter**会被改名为**RequestMappingHandlerAdpter**

### 1.getHandler()

怎么能够根据当前请求找到那个类能来处理？
getHandler()会返回目标处理器类的执行链；

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2010.png)

进入getHandler()代码如下

```java
@Nullable
	protected HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception {
		if (this.handlerMappings != null) {
			for (HandlerMapping mapping : this.handlerMappings) {
				HandlerExecutionChain handler = mapping.getHandler(request);
				if (handler != null) {
					return handler;
				}
			}
		}
		return null;
	}
```

==HandlerMapping（处理器映射）== :
它里面保存了每一个处理器能处理那些请求的映射信息
上面是注解的资源，下面那个是配置的资源，如果用controller注解就用上面那个

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2011.png)

==handler==：

> ioc容器启动创建Controller对象的时候扫描每个处理器都能处理什么请求，保存在HandlerMapping的handler属性中；
下一次请求过来，就来看哪个HandlerMapping中有这个请求映射信息就行了；
> 

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2012.png)

### 2.getHandlerAdapter()

如何找到目标处理器类的适配器，要拿适配器才能去执行目标方法

```java
protected HandlerAdapter getHandlerAdapter(Object handler) throws ServletException {
		if (this.handlerAdapters != null) {
		//遍历所有的handlerAdapter
			for (HandlerAdapter adapter : this.handlerAdapters) {
				//supports()方法就是判断三种adapter哪一种能够处理这个请求
				if (adapter.supports(handler)) {
					return adapter;
				}
			}
		}
		throw new ServletException("No adapter for handler [" + handler +
				"]: The DispatcherServlet configuration needs to include a HandlerAdapter that supports this handler");
	}
```

总共有三种handlerAdapter，而我们使用的是**RequestMappingHandlerAdpter**，能够解析注解方法的适配器，处理器类中只要有方法标了注解就能用

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2013.png)

### 4.SpringMVC中的九大组件

在DispatcherServlet中有几个引用类型的属性：

### 4.1 说明

SpringMVC在工作的时候，关键位置都是由这些组件完成的；
共同点：九大组件全部都是**接口**；接口就是规范；提供了非常强大的扩展性；
SpringMVC的九大组件工作原理

```java
	//文件上传解析器
	@Nullable
	private MultipartResolver multipartResolver;

	/** LocaleResolver used by this servlet. */
	//区域信息解析器，国际化
	@Nullable
	private LocaleResolver localeResolver;

	/** ThemeResolver used by this servlet. */
	//主题解析器，强大的主题效果更换，没什么人用
	@Nullable
	private ThemeResolver themeResolver;

	/** List of HandlerMappings used by this servlet. */
	//Handler映射信息，HandlerMapping
	@Nullable
	private List<HandlerMapping> handlerMappings;

	/** List of HandlerAdapters used by this servlet. */
	//Handler的适配器
	@Nullable
	private List<HandlerAdapter> handlerAdapters;

	/** List of HandlerExceptionResolvers used by this servlet. */
	//springMVC中提供了强大的异常处理机制，解析功能，即异常解析器
	@Nullable
	private List<HandlerExceptionResolver> handlerExceptionResolvers;

	/** RequestToViewNameTranslator used by this servlet. */
	//不用了解
	@Nullable
	private RequestToViewNameTranslator viewNameTranslator;

	/** FlashMapManager used by this servlet. */
	//FlashMapManager ：允许重定向携带数据的功能
	@Nullable
	private FlashMapManager flashMapManager;

	/** List of ViewResolvers used by this servlet. */
	//视图解析器：
	@Nullable
	private List<ViewResolver> viewResolvers;
```

### 4.2 九大组件的初始化

服务器启动九大组件就会初始化
DispatcherServlet中有一个onRefresh方法，其中调用了initStrategies来初始化九大组件

```java
protected void initStrategies(ApplicationContext context) {
		initMultipartResolver(context);
		initLocaleResolver(context);
		initThemeResolver(context);
		initHandlerMappings(context);//着重
		initHandlerAdapters(context);//着重
		initHandlerExceptionResolvers(context);
		initRequestToViewNameTranslator(context);
		initViewResolvers(context);
		initFlashMapManager(context);
	}
```

==修改九大组件中的各种属性==：

> 在web.xml中配置DispatcherServlet中可以进行修改
例如initHandlerMappings中的detectAllHandlerMappings默认是true
> 

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2014.png)

```xml
可以在web.xml中修改DispatcherServlet某些属性的默认配置；
	<init-param>
            <param-name>detectAllHandlerMappings</param-name>
            <param-value>false</param-value>
        </init-param>
```

### 4.2 总结

组件的初始化：去容器中找这个组件，如果有没找到就用默认的配置；默认配置的配置文件在

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2015.png)

有些组件在容器中是使用类型找的，有些组件是使用id找的；

### [5.mv](http://5.mv/) = ha.handle()

具体执行过程：
先进入handle的方法然后进入handleInternal方法进行具体执行

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2016.png)

```java
@Nullable
	protected ModelAndView invokeHandlerMethod(HttpServletRequest request,
			HttpServletResponse response, HandlerMethod handlerMethod) throws Exception {
		//包装原生的request, response，
		ServletWebRequest webRequest = new ServletWebRequest(request, response);
		try {

			//创建了一个，隐含模型
			ModelAndViewContainer mavContainer = new ModelAndViewContainer();
```

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2017.png)

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2018.png)

```java
			//真正来执行目标方法的
			invocableMethod.invokeAndHandle(webRequest, mavContainer);
			if (asyncManager.isConcurrentHandlingStarted()) {
				return null;
			}

			return getModelAndView(mavContainer, modelFactory, webRequest);
		}
		finally {
			webRequest.requestCompleted();
		}
	}
```

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2019.png)

### 5.1方法执行的细节invokeAndHandle

invokeAndHandle方法中传入的参数第三个就是我们方法中参数的传入入口

```java
public void invokeAndHandle(ServletWebRequest webRequest, ModelAndViewContainer mavContainer,
			Object... providedArgs)
```

==总结==：

> 确定方法运行时使用的每一个参数的值，流程如下
> 

==①.标注解==：保存注解的信息；最终得到这个注解应该对应解析的值；
==②.没标注解==：

> 看是否是原生API；看是否是Model或者是Map，xxxx都不是，看是否是简单类型；paramName；给attrName赋值；attrName（参数标了@ModelAttribute("")就是指定的，没标就是""）拿到之前创建好的对象，使用数据绑定器(WebDataBinder)将请求中的每个数据绑定到这个对象中；
> 

## 3.其他知识点

### 1. SpringMVC 父子容器

- 图示

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2020.png)

==为什么有父与子之分==：

> 其实在执行spring容器时，创建启动一个容器context，此时就是父容器，**然后此项目如果是web服务就会生成DispatcherServlet ，并初始化它，在其中就会生成一个新的context即为子容器，将之前的容器置为自己的父容器**
> 

> 这样就有了父子之分，这样指责就更加清晰，子容器就负责 web 部分，父容器则是通用的一些 bean。
> 

# Mybatis

## 1.运行过程

- 图示

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2021.png)

1. 读取MyBatis配置文件mybatis-config.xml。mybatis-config.xml作为MyBatis的全局配置文件，配置了MyBatis的运行环境等信息，其中主要内容是获取数据库连接。
2. 加载映射文件Mapper.xml。Mapper.xml文件即SQL映射文件，该文件中配置了操作数据库的SQL语句，需要在mybatis-config.xml中加载才能执行。mybatis-config.xml可以加载多个配置文件，每个配置文件对应数据库中的一张表。
3. 构建会话工厂。通过MyBatis的环境等配置信息构建会话工厂SqlSessionFactory。
4. 创建SqlSession对象。由会话工厂创建SqlSession对象，该对象中包含了执行SQL的所有方法。
5. MyBatis底层定义了一个Executor接口来操作数据库，它会根据SqlSession传递的参数动态的生成需要执行的SQL语句，同时负责查询缓存的维护。
6. 在Executor接口的执行方法中，包含一个MappedStatement类型的参数，该参数是对映射信息的封装，用来存储要映射的SQL语句的id、参数等。Mapper.xml文件中一个SQL对应一个MappedStatement对象，SQL的id即是MappedStatement的id。
7. 输入参数映射。在执行方法时，MappedStatement对象会对用户执行SQL语句的输入参数进行定义(可以定义为Map、List类型、基本类型和POJO类型)，Executor执行器会通过MappedStatement对象在执行SQL前，将输入的Java对象映射到SQL语句中。这里对输入参数的映射过程就类似于JDBC编程中对preparedStatement对象设置参数的过程。
8. 输出结果映射。在数据库中执行完SQL语句后，MappedStatement对象会对SQL执行输出的结果进行定义(可以定义为Map和List类型、基本类型、POJO类型)，Executor执行器会通过MappedStatement对象在执行SQL语句后，将输出结果映射至Java对象中。这种将输出结果映射到Java对象的过程就类似于JDBC编程中对结果的解析处理过程。

==Mybatis的动态代理==：

> 对于Mybatis来说代理对象就是每个mapper接口，在实际使用中我们发现根本没有使用对应的mapper实现类，而Mybatis底层是使用JDK来动态代理的，没有实现类怎么代理，其实你将每个mapper对应的xml文件理解为被代理对象，
> 
> 1. 根据 .xml 上关联的 namespace, 通过 Class#forName 反射的方式返回 Class 对象（不止 .xml namespace 一种方式）
> 2. 将得到的 Class 对象（实际就是接口对象）传递给 Mybatis 代理工厂生成代理对象，也就是刚才 mapperInterface 属性

## 2.Mybatis的缓存

==详细配置过程==：
[配置](https://www.cnblogs.com/wenxuehai/p/15357086.html)

### 2.1 一级缓存（本地缓存）

- 概述

> 一级缓存的作用域是sqlSesson级别，同一个sqlsession中执行相同的sql查询（相同的sql和参数），第一次会去查询数据库并写到缓存中，第二次从一级缓存中取。**一级缓存是基于 PerpetualCache 的 HashMap 本地缓存，`默认打开一级缓存`。**
> 
- 特性

> • 在同一个sqlSession中，会把执行的参数和sql进行算法压缩成key，查询结果作为value放入这个map中
• 不同的sqlSession之间的查询是相互隔离的，即缓存不共用
• 任何的**增删改**，都会清空一级缓存，当然你也可以配置查询的时候，返回结果时也删除一级缓存
• **有commit的语句会清空一级缓存和二级缓存**
• 无过期时间，**创建一个新的SqlSession对象，SqlSession对象中会有一个Executor对象，Executor对象中持有一个PerpetualCache对象，见下面代码。当会话结束时，SqlSession对象及其内部的Executor对象还有PerpetualCache对象也一并释放掉。**
> 

### 2.2 二级缓存（全局缓存）

- 概述

> 二级缓存简介 它指的是Mybatis中SqlSessionFactory对象的缓存。由同一个SqlSessionFactory对象创建的SqlSession共享其缓存。**二级缓存是 mapper 映射级别的缓存，多个 SqlSession 去操作同一个 Mapper 映射的 sql 语句，多个SqlSession 可以共用二级缓存，二级缓存是跨 SqlSession 的。** `默认不打开二级缓存`
> 
- 特性

> • 在查sql时，会先命中二级缓存，二级缓存中没有再看一级缓存，都没有才去查数据库。
• 缓存优先放到一级缓存，当前查询关闭后，才会把一级缓存添加到二级缓存中
• 开启二级缓存后，只要将pojo对象实现序列化接口
• 每个二级缓存的默认存活时间为1H，每次去查询都会检查缓存时间
> 

## 3.其他知识点

### 1. MyBatis #{} 和 ${}

==#{}==：

- 在方法上使用注解

![image.png](Spring%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88IOC&AOP%EF%BC%89%20SpringMVC%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%88DispatcherServle/image%2022.png)

- 当然也可以在xml中写

==#{} 和 ${}的区别一起为什么#{}可以防止注入==：

> 一个是变量占位（？），一个是静态占位（需要的值）
> 
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/89a6ea242e0833b1d1e7dcd65378d3e6.png)
> 
1. 当我向mybatis输入一条带有#{}的语句时：

> `select * from user where uid=#{id} and password=#{pwd};`这时数据库就会进行预编译，并进行一个缓存动作，缓存一条这样的语句：`select * from user where uid=? and password=?;`当我们调用这条语句，并实际向`#{id}`中的id传了一个值`“deftiii” or 1=1#`时，不需要在编译，数据库会直接找对应的表中有没有名字是 `“deftiii” or 1=1#` 的用户，而不再有编译sql语句的过程。
> 
1. 而如果把上述语句中的`#{id}`换成`${id}`，那么就没有了预编译和缓存的过程

> 向`${id}里面传值 deftiii or #1=1`时，会编译执行`select * from user where uid=“deftiii” or 1=1 #and password=某个密码`
，这样#后面的内容被注释掉了，这条语句就相当于`select * from user where uid= “deftiii” or 1=1`，即当我们语句中使用`${}`时，可以无视密码就能查出所有用户信息，这就是sql注入。
> 

==如何实现防SQL注入的 LIKE %A%==:
`like concat('%', #{A}, '%')`

### 2.MybatisPlus#saveOrUpdate

- 概述

> 这个方法如果是第一次使用再不知道MybatisPlus寻找主键的方式可能就会造成出错
> 
- saveOrUpdate的作用

> 官方说你传入一个entity，这个时候entity会有一个主键，这个时候它先通过主键去查询记录是否存在，如果记录存在则选择修改，如果记录不存在则选择增加，主要的流程如下
> 
> - 首先会直接更新
> - 如果更新失败返回0，尝试查询
> - 如果没有查询到，那么直接调用insert进行插入
- MybatisPlus找主键的方式

> 一般找主键的方式有两种，后者比前者优先级高，如果两种都找不到，那么直接报错
> 
> 1. 第一种情况，你的表存在一个`id`字段，默认把`id`字段当作主键
> 2. 第二种情况，你给表字段增加一个`@TableId`注解（别用成了`@TableField`注解），算是你主动给字段加记号让`mybatis-plus`知道
- 根据流程主键可能会发生的情况

> 插入的数据不带id：插入是成功的`mybatis-plus`自动帮你生成一个`id{1498495250845941762}`，19位)，策略为：mybatis-plus默认使用的主键生成的策略是`IdType.ID_WORKER`，根据类型随机产生一个全局唯一的ID插入的数据带id，且数据库存在：修改成功插入的数据带id，且数据库不存在：插入成功
>