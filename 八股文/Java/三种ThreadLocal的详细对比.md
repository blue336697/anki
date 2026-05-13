# 三种 ThreadLocal 的详细对比以及原理

### **InheritableThreadLocal、TransmittableThreadLocal和普通的threadLocal三者的区别**

### **1. ThreadLocal**

- 用途：为每个线程提供独立的变量副本，线程之间的数据是隔离的。
- 行为：每个线程对 ThreadLocal 的访问都是独立的，无法在子线程中继承父线程的值。

### **2. InheritableThreadLocal**

- 用途：允许子线程继承父线程的 ThreadLocal 值。
- 行为：子线程在创建时会复制父线程的 ThreadLocal 值，但之后的修改不会相互影响。

### **3. TransmittableThreadLocal (from Ali's open-source library)**

- 用途：在使用线程池等场景下，传递父线程的 ThreadLocal 值给子线程。
- 行为：解决 InheritableThreadLocal 在线程池中无法传递值的问题，支持线程池中线程复用时的值传递。
- 缺点：使用spring自带的线程池如果自己用完没有自己clear，就会出现乱窜

线程池与ThreadLocal如何共享父子线程

- 把threadLocal作为对象传到线程池中，子线程不负责存和删除，只负责用就行
- 把traceId作为串联的方式，这样父子线程都能拿到
- 使用阿里的线程池+阿里的threadLocal
    - 如果用了ThreadLocal但是没用阿里的线程池，照样会出现问题，字节码写入一个切面去识别线程执行方式：thread、runnable、callable等，然后识别到最后clear
- **TransmittableThreadLocal+ASM扫描线程创建方式然后clear**
    - 指定目录，尽量不扫tomcat和spring自己的线程池