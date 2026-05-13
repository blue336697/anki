# GC相关（GMS、G1、ZGC）

type: Post
status: Published
date: 2023/11/27
summary: GC相关（GMS、G1、ZGC）
tags: JVM, Java
category: 技术分享

https://tech.meituan.com/2017/12/29/jvm-optimize.html

https://tech.meituan.com/2020/08/06/new-zgc-practice-in-meituan.html

https://tech.meituan.com/2025/06/20/jdk17-zgc.html

## 优化与BUG修复

### **NIO 重写与优化**

1. **UDS（Unix-domain Sokcet）**

**Unix-Domain Socket**（简称UDS，中文常译为“Unix域套接字”或“Unix本地域套接字”）是一种在同一台主机（操作系统）内部进行**进程间通信（IPC, Inter-Process Communication）**的机制。

---

**主要特点**

- **本地通信**：只能用于同一台机器上的进程间通信，不能跨主机。
- **高效**：比基于TCP/IP的本地通信更快，因为数据不需要经过网络协议栈，只在内核空间传递。
- **文件系统路径**：Unix-Domain Socket 通常以文件的形式存在于文件系统（如 /tmp/my.sock），进程通过这个“文件”进行通信。
- **支持多种通信方式**：支持字节流（类似TCP）、数据报（类似UDP）等。

---

**应用场景**

- 本地服务之间的高效通信（如Nginx与PHP-FPM、MySQL、Redis等的本地连接）
- 替代本地TCP端口，提升安全性和性能
- 进程间消息传递、数据共享

---

**示例**

假设有两个本地进程A和B：

- A创建一个Unix-Domain Socket文件 /tmp/demo.sock
- B通过该文件连接A，双方即可像用网络Socket一样收发数据，但数据不会离开本机

---

**与TCP/IP Socket的区别**

| 特点 | Unix-Domain Socket | TCP/IP Socket |
| --- | --- | --- |
| 通信范围 | 仅本机 | 可跨主机 |
| 性能 | 更高（无协议栈开销） | 稍低（有协议栈开销） |
| 地址 | 文件路径 | IP+端口 |
| 安全性 | 更高（文件权限控制） | 依赖网络安全措施 |

---

**总结：**

Unix-Domain Socket 是一种高效的本地进程间通信方式，常用于需要高性能、本地安全通信的场景。

1. **文件通道的优化：可以把一些热点文件的信息提前映射到内存中，随拿随取**
2. **零拷贝支持：数据拷贝不用先拷贝到用户态，在拷贝到目标内核态，全程在内核态完成**

### **Java SDK 模块化设计**

JVM 的模块化是 Java 9 引入的一个重要特性，通过 Java Platform Module System (JPMS) 实现。这一特性旨在解决 Java 应用在可扩展性和维护上的问题，提供更高级别的封装和依赖管理机制。

- **减少环境资源开销**：在 JDK 9 之前，每次启动 JVM 都要耗费至少 30MB 到 60MB 的内存空间，因为 JVM 需要加载整个 rt.jar。模块化允许 JVM 选择性地加载必需的模块，从而减少内存占用。
- **提升开发效率和运行速度**：随着代码库的复杂性增加，开发效率和运行速度会受到影响。模块化通过规范化路径和依赖关系，使系统更安全、更高效。
- **规范化路径及依赖关系**：JDK 9 之前，系统没有对不同 JAR 之间的依赖或敏感路径进行限制，导致所有 JAR 都可以被访问，暴露了安全问题。模块化通过管理模块间的依赖关系，隐藏不必要的模块，提高了安全性和空间利用率。

### **Java Agent 机制的 Attach Bug 修复**

Java Attach Socket 文件被删除后会导致 Java Agent 注入失败，在 JDK 8 上只能通过重启解决，而 JDK 17 会重新创建一个新的文件。

### **弹性元空间**

更及时地将未使用的元空间内存回收，减少元空间占用的内存。

### 元空间相关

1、当元空间不足时，可能会导致类加载时类没有加载进去，在实际业务中就会报错找不到某个类