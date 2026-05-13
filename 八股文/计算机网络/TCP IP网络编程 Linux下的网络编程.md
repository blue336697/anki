# TCP/IP网络编程 | Linux下的网络编程

type: Post
status: Published
date: 2023/10/01
summary: Linux下的网络编程
tags: 计算机网络
category: 技术分享

## Linux中的进程

在linux中使用fork函数进行创建子进程，在linux中fork函数返回的pid对于父进程来说返回的子进程的pid，而子进程的pid则是0

```java
#include <stdio.h>
#include <unistd.h>
 
int gval = 10;
int main(int argc, char *argv[]) {
    pid_t pid;
    int lval = 20;
    gval++, lval += 5;
 
    pid = fork();
    if(pid == 0) {
        gval += 2;
        lval += 2;
    } else {
        gval -= 2;
        lval -= 2;
    }
 
    if(pid == 0) {
        //Child Proc: [13, 27]
        printf("Child Proc: [%d, %d]\n", gval, lval);
    } else {
        //Parent Proc: [9, 23]
        printf("Parent Proc: [%d, %d]\n", gval, lval);
    }
    return 0;
}
```

### **fork函数复制父进程的套接字文件描述符的过程**

如图，可以看到每个套接字有两个文件描述符

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image.png)

当销毁文件描述符时就需要把两个套接字中的来自同一个进程的一起销毁，那么就要避免出现下图的情况，即子进程需要销毁自己的客户端与服务端文件描述符

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%201.png)

### **1.1 僵尸进程**

对于进程的创建与销毁，当销毁不当时就会产生孤儿进程或者僵尸进程，对于子进程来说，退出的函数是exit函数，而主进程则是return，这两个函数都会返回信息给操作系统，这时直到父进程收到这些信息之前都不会销毁子进程，对于父进程来说，不会主动接收操作系统传来的值，而是在父进程主动发起函数调用时，才会主动去获取，如果父进程不执行该动作，则子进程一直处于僵尸状态

下面的子进程PID打出来以后就可以通过ps -p pid的方式可以看到对应进程的状态就是Z+，即僵尸进程

```java
#include <stdio.h>
#include <unistd.h>
 
int main(int argc, char *argv[]) {
    pid_t pid = fork();
    if(pid == 0) {
        //Hi, I am a child process
        puts("Hi, I am a child process");
    } else {
        //Child Process ID: 90556
        printf("Child Process ID: %d\n", pid);
        sleep(30);
    }
 
    if(pid == 0) {
        //End child process
        puts("End child process");
    } else {
        //End parent process
        puts("End parent process");
    }
    return 0;
}
```

### **1.2 如何销毁僵尸进程**

### **1、利用wait函数**

前面讨论了什么是僵尸进程，同时想要销毁子进程，父进程应主动去请求子进程的返回消息，那么就可以使用wait函数

注意：如果子进程一直不返回，那么父进程会一直等待

需要考虑一种情况：就是调用此函数时已经有子进程完成，此时的statloc所有信息会保存在当前函数的内存空间，其中一些信息可以辅助我们判断这个子进程的状态并以此回收，所以需要配合WIFEXITED和WEXITSTATUS函数辅助判断

> 这段代码演示了在Unix-like系统中使用fork()和wait()函数进行进程创建和管理的基本方法。下面是代码的逐行解释：
> 
> 1. **包含头文件**：包含了执行程序所需的头文件，`stdio.h`用于输入输出，`stdlib.h`用于常规实用程序，`unistd.h`提供对POSIX操作系统API的访问，`sys/wait.h`用于进程等待。
> 2. **`main`函数定义**：程序的入口点，接受命令行参数。
> 3. **变量定义**：定义了`status`变量用于存储子进程的退出状态，`pid`变量用于存储`fork()`函数的返回值。
> 4. **创建第一个子进程**：通过`fork()`创建一个子进程。`fork()`会返回两次，一次在父进程中（返回子进程的PID），一次在子进程中（返回0）。
> 5. **子进程逻辑**：如果`fork()`返回0，说明当前是子进程，子进程通过`return 3;`结束并返回状态码3。
> 6. **父进程逻辑**：如果`fork()`返回的是子进程的PID，说明当前是父进程。首先，打印出第一个子进程的PID。
> 7. **创建第二个子进程**：父进程再次调用`fork()`创建另一个子进程。
> 8. **第二个子进程逻辑**：如果`fork()`在第二次调用时返回0，说明当前是第二个子进程，通过`exit(7);`结束并返回状态码7。
> 9. **父进程等待子进程结束**：父进程继续执行，打印第二个子进程的PID，然后两次调用`wait(&status);`来等待任一子进程结束。`wait()`函数会阻塞父进程的执行，直到一个子进程结束。
> 10. **检查子进程的退出状态**：使用`WIFEXITED(status)`宏来检查子进程是否正常结束。如果是，使用`WEXITSTATUS(status)`宏获取子进程的返回值，并打印出来。
> 11. **父进程休眠**：最后，父进程调用`sleep(30);`休眠30秒。这是为了演示父进程在子进程结束后仍然可以执行操作。
> 12. **程序结束**：父进程通过`return 0;`正常结束。
> 
> 这段代码的目的是演示如何创建和管理子进程，以及如何获取子进程的退出状态。它创建了两个子进程，每个子进程都返回一个不同的退出状态，父进程等待每个子进程结束并打印它们的退出状态。
> 

**wait使用实例** 

```java
//成功返回子进程ID，失败返回-1
pid = wait(int *statloc)
 
 
int main(int argc, char *argv[]) {
    int status;
    pid_t pid = fork();
 
    if(pid == 0) {
        return 3;
    } else {
        printf("Child PID: %d\n", pid);
        pid = fork();
        if(pid == 0) {
            exit(7);
        } else {
            printf("Child PID: %d\n", pid);
            wait(&status);
            if(WIFEXITED(status)) {
                printf("Child send one: %d\n", WEXITSTATUS(status));
            }
 
            wait(&status);
            if(WIFEXITED(status)) {
                printf("Child send two: %d\n", WEXITSTATUS(status));
            }
            sleep(30);
        }
    }
    return 0;
}
```

### **2、利用waitpid函数**

由于wait方法会引起阻塞，所以可以使用waitpid方法

**waitpid例子** 

```java
//成功返回子进程ID或者当前子进程ID返回0，失败返回-1
pid_t   waitpid(pid_t, int *statloc, int options) __DARWIN_ALIAS_C(waitpid);
 
int main() {
    int status;
    pid_t pid = fork();
 
    if(pid == 0) {
        sleep(15);
        return 24;
    } else {
        //如果这里换乘waitpid则主进程会执行5次“sleep 3sec”
        //while(!waitpid(-1, &status, WNOHANG)) {
        while(!wait(&status)) {
            sleep(3);
            puts("sleep 3sec.");
        }
 
        if(WIFEXITED(status)) {
            printf("Child send %d\n", WEXITSTATUS(status));
        }
    }
    return 0;
}
```

### **1.3 信号**

### **signal函数、alarm函数以及sigaction函数**

对于signal函数来说就是通过传入某个操作系统信号，以及信号的对应handler

而对于alarm函数来说，传入正整数的秒数，含义为多少秒后调用信号【SIGALRM】

对于最后的sigaction函数来说，相较于signal更为常用，signal是为了适配旧版本留下的函数

函数结果是交替打印wait与time out三次，一次主函数的alarm，与两次handler中的alarm

对于处理信号的进程唤醒是调用sleep函数的进程，而唤醒的进程不会进入睡眠状态直到遇到下一次的sleep

```java
void timeout(int sig) {
    if(sig == SIGALRM) {
        puts("Time out!");
    }
    alarm(2);
}
 
void keycontrol(int sig) {
    if(sig == SIGINT) {
        puts("CTRL+C pressed");
    }
}
 
int main(int argc, char *argv[]) {
    int i;
    signal(SIGALRM, timeout);
    signal(SIGINT, keycontrol);
    alarm(2);
 
    for(i = 0; i < 3; i++) {
        puts("wait...");
        sleep(100);
    }
    return 0;
}
 
int main(int argc, char *argv[]) {
    int i;
    struct sigaction act;
    act.sa_handler = timeout;
    sigemptyset(&act.sa_mask);
    act.sa_flags = 0;
 
    sigaction(SIGALRM, &act, 0);
    alarm(2);
 
    for(i = 0; i < 3; i++) {
        puts("wait...");
        sleep(100);
    }
    return 0;
}
```

### **1.4 多进程服务端与IO分离客户端**

多进程服务器：即一个服务端服务多个客户端，来一个客户端创建一个进程的方式

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%202.png)

IO分离客户端：即主线程读取，子线程负责写

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%203.png)

### **1.5 进程通信**

### **单个管道双向通信**

这个管道存在一个问题，就是要人工去控制生产与消费，如果不控制会出现，生产方自己消费自己的问题

```java
int fds[2];
 
pipe(fds);
```

---

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%204.png)

### **两个管道双向通信**

```java
int fds01[2],fds02[2];
 
pipe(fds01);
pipe(fds02);
```

---

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%205.png)

## 并发服务器

前面讨论的多进程服务器并不是完美的，因为无论从编码层面还是操作系统层面创建进程的消耗都十分巨大，即引入池化思想

### **1.1 I/O多路复用服务器**

### **理解“复用”的概念**

在通信领域内可以这样解释：在一个通信频道内传递多个信号（数据）的技术，可以拿三个人通过纸杯传音的例子来形象说明，通过减少连线个数、纸杯个数；亦或者用老师与学生的概念来举例，当来一个学生就来一个老师时显然是不现实的，那么一个老师多个学生通过举手并确认的方式更加好

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%206.png)

### **多进程服务端与IO复用的客户端**

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%207.png)

### **1.2 select函数的功能和调用顺序**

由调用步骤和顺序来看函数使用的难度较高

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%208.png)

### **设置文件描述符**

由于是IO复用的机制，那么select就需要同时监听多个描述符，当描述符准备好了就开始处理对应的socket，同时监听时需要把文件描述符分为三类：接收、传输、异常，这些文件描述符会统一维护在fd_set这个数组中，这个数组是一个二进制数组，每一位代表一个文件描述符，当值为1时表示描述符正在被监听，通过一些列c语言给定的宏函数来操作这个数组，如下图

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%209.png)

操作每个函数的效果如下：

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%2010.png)

### **select函数**

```java
int select(int maxfd,
fd_set * __restrict readset,
fd_set * __restrict writeset,
fd_set * __restrict exceptset,
struct timeval * __restrict timeout)
```

---

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%2011.png)

## 多种IO函数的解释

### **1.1 send&recv函数**

- socket：表示数据传输对象的连接套接字文件描述符（Windows则为句柄）
- buf：保存待传输数据的缓冲地址值
- nbytes：待传输的字节数
- flags：传输数据时指定的可选择配置

```java
WINSOCK_API_LINKAGE int WSAAPI send(SOCKET s,const char *buf,int len,int flags);
WINSOCK_API_LINKAGE int WSAAPI recv(SOCKET s,char *buf,int len,int flags);
```

---

### **flags**

- MSG_OOB（out of band：适用于send+recv）：用于传输带外的紧急数据，可以理解为医院有很多病人在等待看病由此演变出来的急诊，但这个急诊更像是通知这里有一个很严重的病人，请加快当前的处理进度，而不是立马处理当前紧急病人，这是因为OOB实际含义是另开一个通信路径去传输，而TCP本身是没有实现，所以只能依赖于TCP的紧急模式；在代码层面配合SIGURG信号来处理，分配处理信号的进程则是在接收信号时去指定

> 紧急模式：含义是督促这里有一个紧急信息需要处理，如下面的代码实际上表达的信息是890的长度为3，那么紧急信息的结束指针就位于对于基准位向左偏移3位，即8对0，9对1，0对2后一位即是3；从代码结果上来看确实是只提供提醒而不是实际处理
> 
> 
> ```java
> # 这一行在接收端会接收为0，而不是890
> send(sock, "890", strlen("890"), MGB_OOB)
> ```
> 
> ---
> 
> 注意：对于windows平台来说由于不存在信号处理机制，对于windows平台来说当接收了这种信息时会认定为异常，那么就可以利用select函数的异常处理机制，
> 
- MSG_PEEK+MSG_DONTWAIT：检查缓存去是否存在接收的数据，设置了会在读取缓冲区信息后不删除，与后者配合即使不存在待读取数据也不会进入阻塞状态

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%2012.png)

### **1.2 readv&writev函数**

这两个函数能够增加传输的效率，作用简而言之：对数据整合传输以及发送的函数。可以将多个缓冲区的信息进行整合并且发送，返回成功发送的字节数

- 文件描述符
- 需要传输的缓冲区地址+大小
- 从这个缓冲区开始往后有几个缓冲区需要整合

```java
ssize_t writev(int filedes, const struct iovec * iov, int iovcnt)
struct iovec{
 void * iov_base; //缓冲地址
 size_t iov_len; //缓冲大小
}
```

---

### **何时可以用这两个函数**

其实在任何情况下都可以用这两个函数加快处理速度，尤其是在不再用Nagle算法的前提下，这两个函数就更有意义了；其实可以把writev的作用等价为，将存储在不同内存地址的数据统一存放在一个大数组中，然后直接使用write发送这个数据。

注意：与MSG_OOB一致，在windows平台是没有writev和readv的对应函数，但是可以通过“重叠I/O”的方式来实现相同的效果

## 多播与广播

### **1.1 多播**

多播技术是基于UDP协议实现的，与UDP的发送格式非常相似，同时多播实现的原理则是发送方发送一份数据，而不同的接收方（相同组）根据路由器的转发复制，常用于多媒体的直播，这样做可以在同一区域内节省网络带宽，对于同一个数据而言在到底目的地之间的路径只会走一次，若有几个主机发送几次则会造成大量的路径重复；而现状则是路由器大多不支持多播，就算支持也会因为网络拥堵等多种原因而禁用。

### **路由（Routing）和TTL以及加入组的方法**

为了避免使用多播时造成一些网络拥堵原因所以需要考虑加入一些制约，类似于TTL，一般称之为“跳”，例如TTL=3时，则表达还需要3跳即三个路由器才能到达目的地，当TTL为0时，即代表数据包无法被传递了。使用设置socket的函数设置IP_MULTICAST_TTL的具体跳数+IP_ADD_MEMBERSHIP协议层变更+ip_mreq结构体去指定组IP地址和加入该组的主机IP地址

### **1.2 广播**

与多播类似，同样是“一次性向多个主机发送数据”，区别主要集中在一点：传输数据的范围，多播规定只要在一个组内，管你是哪的网络都可以被多播影响；而相反广播只能在同一网络中传输；广播也是基于UDP来实现的；根据广播时使用的IP可分为两类：

1. 直接广播：例如想192.168.1下的所有主机发送广播，则可以向192.168.1.255发送信息即可达成目的
2. 本地广播：相反本地则是向255.255.255.255发送广播，则发送消息的主机所在的网络下所有主机都可以收到消息

## epoll

epoll是从Linux2.5.44内核引入的，epoll解决了select的五个缺点：

**1. 连接数限制**

- **select** 支持的最大文件描述符数量有限（通常是 1024，受 FD_SETSIZE 限制），不适合大规模并发连接。
- **epoll** 支持的文件描述符数量远大于 select，理论上只受限于操作系统最大句柄数。

---

**2. 轮询效率低**

- **select** 每次调用都要把所有 fd 集合从用户态拷贝到内核态，然后内核遍历所有 fd 检查状态，**时间复杂度 O(n)**，连接数越多效率越低。
- **epoll** 采用事件驱动机制，只有真正发生事件的 fd 才会被通知，**时间复杂度 O(1)**，高并发下效率极高。

---

**3. 内存拷贝开销大**

- **select** 每次调用都要把 fd 集合从用户空间拷贝到内核空间，数据量大时开销很大。
- **epoll** 只需在注册时拷贝一次，后续无需重复拷贝。

---

**4. 事件通知方式** 

- **select** 返回后需要遍历整个 fd 集合，判断哪些 fd 有事件发生，效率低。
- **epoll** 直接返回有事件的 fd 列表，无需遍历所有 fd。

---

**5. 支持的并发模型**

- **select** 只能采用水平触发（Level Triggered），不支持边缘触发（Edge Triggered）。
- **epoll** 支持水平触发和边缘触发，边缘触发更适合高性能网络编程。

### **1.1 epoll_create**

调用此方法会创建文件描述符，描述符指代的空间被称为“epoll例程”，注意这个size不是传入多少就生成多少，而是一个对操作系统的建议。在Linux2.6.8后续这个参数被完全取消；使用的模式类似于文件描述符，在结束使用后要调用close函数

```java
# include <sys/epoll.h>
 
#返回文件描述符
int epoll_create(int size);
```

---

### **1.2 epoll_ctl**

在产生文件描述符后，即epoll例程则要注册监视对象，那么此时就要调用epoll_ctl

- epfd：监视对象的epoll例程文件描述符
- op：指定对文件描述符的CRUD；ADD、DEL、MOD（更改关注事件的类型）
- fd：需要监视的文件描述符
- event：监视对象的事件类型

```java
# include <sys/epoll.h>
 
#返回文件描述符
int epoll_ctl(int epfd, int op, int fd, struct epoll_event * event);
 
# 意义时epoll例程A注册文件描述符B，主要目的是为了监视参数C中的事件
epoll_ctl(A, EPOLL_CTL_ADD, B, C);
 
# 意义是从epoll例程A中删除文件描述符B
epoll_ctl(A, EPOLL_CTL_DELETE, B, null);
```

---

### **event指针结构体**

其中事件类型分别有这么几种：

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20Linux%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B/image%2013.png)

```java

struct epoll_event event;
event.events = EPOllIN;
event.data.fd = sockfd;
xxx(,,,*event);
```

---

### **1.3 epoll_wait**

这个函数的大致用途就与select相等了。函数返回监视的文件描述符，并将返回的文件描述符加入到事件描述符结构体中

- epfd：epoll例程的文件描述符
- events：保存发生事件的文件描述符集合的结构体
- maxevents：前者events中最大事件数
- timeout：ms单位，传递-1则是无限等到发生事件

```java
# include <sys/epoll.h>
 
int epoll_wait(int epfd, struct epoll_event * event, int maxevents, int timeout);
```

---

### **1.4 条件触发和边缘触发**

本质区别：在于发生事件的时间点

- 条件触发：只要缓冲区里还有数据，就会无数次注册事件
- 边缘触发：只会在一开始缓冲区有数据时以事件的方式注册一次，以后都是这个事件去监听描述符了