# TCP/IP网络编程 | 理解网络编程和套接字

type: Post
status: Published
date: 2023/10/21
summary: 理解网络编程和套接字
tags: 计算机网络
category: 技术分享

# 理解网络编程和套接字

网络编程四步走——用打电话类比：

1. 调用socket函数创建套接字——安装电话
2. 调用bind函数分配IP和端口号——给电话分配电话号码
3. 调用listen函数转为可接收请求状态——给电话安装电话线
4. 调用accept函数受理连接状态——有电话拿起话筒接听

## **1.1 基于Linux的文件操作**

### **什么是底层**

在大多数情况下底层都可以被理解为“与标准无关的，操作系统独立提供的”一些函数，而非ANSI提供的标准函数，例如在Linux下想要网络编程和Windows下的函数就不同

```java
//Linux
#include <arpa/inet.h>
#include <sys/socket.h>
//Windows
#include <Winsock2.h>
#include <winsock.h>
```

---

### **简单提一嘴文件描述符（File Descriptor）**

在Windows下会被称为句柄，但是两者还是有些许差别。在Linux中会将几乎一切视为文件（套接字也是文件），所以存在文件就要分配文件描述符，但不是所有文件的文件描述符每次都需要分配，肯定是有默认就分配好的，标准常用的。例如标准的输入输出：

| **文件描述符** | **对象** |
| --- | --- |
| 0 | 标准输入：Standard Input |
| 1 | 标准输出：Standard Output |
| 2 | 标准错误：Standard Error |

即文件描述符是为了方便**称呼**OS创建的套接字或文件而赋予的值，而这个值都是从3开始按顺序分配，因为012都被标准的操作所代表的值给占用

### **一些基本的知识点：**

- 在C或CPP中，一些基础数据类型的后缀可能会加_t结尾，称为元数据类型，在typedef包中，随着计算机的进步OS默认支持的数据类型大小也在变化，拿int举例加入_t代表从原来的16位转化为32位，这样就可以只改程序中类型的名字即可，而不用关心其他的
- 在linux和win平台上的close函数，都是关闭当前终端的输入流和输出流

### **编写服务端代码**

**服务端代码** 

```java
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
 
void error_handling(const char *message);
 
#define PORT 8081
 
int main(int argc, char *argv[]) {
    // 当刚进来时,argc=1,argv[0]为exe的路径
    // argc = 2;
    // argv[1] = const_cast<char*>("8080");
    int serv_sock;
    int clnt_sock;
 
    struct sockaddr_in serv_addr;
    struct sockaddr_in clnt_addr;
    socklen_t clnt_addr_size;
 
    char message[] = "Hello World!";
 
    // if(argc != 2) {
    //     printf("Usage : %s <port>\n", argv[0]);
    //     exit(1);
    // }
    //创建套接字
    serv_sock = socket(PF_INET, SOCK_STREAM, 0);
    if(serv_sock == -1) {
        error_handling(const_cast<char*>("socket() error"));
    }
    //初始化地址信息
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET; //使用IPv4地址
    // serv_addr.sin_addr.s_addr = htonl(INADDR_ANY); //自动获取IP地址
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); //手动指定IP地址
    serv_addr.sin_port = htons(PORT); //设置端口号
 
    //绑定套接字
    if(bind(serv_sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1) {
        error_handling(const_cast<char*>("bind() error"));
    }
    //监听套接字
    if(listen(serv_sock, 5) == -1) {
        error_handling(const_cast<char*>("listen() error"));
    }
    //接受客户端请求
    clnt_addr_size = sizeof(clnt_addr);
    clnt_sock = accept(serv_sock, (struct sockaddr*)&clnt_addr, &clnt_addr_size);
    if(clnt_sock == -1) {
        error_handling(const_cast<char*>("accept() error"));
    }
    //向客户端发送数据
    write(clnt_sock, message, sizeof(message));
    //关闭套接字
    close(clnt_sock);
    close(serv_sock);
    return 0;
}
 
void error_handling(const char *message) {
    fputs(message, stderr);
    fputc('\n', stderr);
    exit(1);
}
```

### **编写客户端代码**

**客户端代码** 

```java
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
 
void error_handling(const char *message);
 
#define PORT 8081
 
int main(int argc, char *argv[]) {
    // argc = 3;
    // argv[1] = const_cast<char*>("127.0.0.1");
    // argv[2] = const_cast<char*>("8080");
 
    int sock;
    struct sockaddr_in serv_addr;
    char message[30];
    int str_len;
 
    // if(argc != 3) {
    //     printf("Usage : %s <IP> <port>\n", argv[0]);
    //     exit(1);
    // }
    //创建套接字
    sock = socket(PF_INET, SOCK_STREAM, 0);
    if(sock == -1) {
        error_handling(const_cast<char*>("socket() error"));
    }
    //初始化地址信息
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET; //使用IPv4地址
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); //手动设置IP地址
    serv_addr.sin_port = htons(PORT); //设置端口号
 
    //连接服务器
    if(connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1) {
        error_handling(const_cast<char*>("connect() error"));
    }
    //读取服务器传输的数据
    str_len = read(sock, message, sizeof(message) - 1);
    if(str_len == -1) {
        error_handling(const_cast<char*>("read() error"));
    }
    printf("Message from server : %s \n", message);
    //关闭套接字
    close(sock);
    return 0;
}
 
void error_handling(const char *message) {
    fputs(message, stderr);
    fputc('\n', stderr);
    exit(1);
}
```

### **调试**

可以先基于debug先把调试文件launch.json生成然后在自定义，并且添加c_cpp_properties.json和tasks.json两个配置文件前者配置CPP文件的环境设置，后者配置运行CPP文件的可执行文件的输出位置，执行命令如下：

可以看到-g就是说明是调试的文件，-o就是可执行文件的输出路径和名称

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E7%90%86%E8%A7%A3%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%E5%92%8C%E5%A5%97%E6%8E%A5%E5%AD%97/image.png)

先运行服务端在运行客户端结果如下：

**可以看到客户端接收到了来自服务端的Hello World！**

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E7%90%86%E8%A7%A3%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%E5%92%8C%E5%A5%97%E6%8E%A5%E5%AD%97/image%201.png)

## **1.2 Windows和Linux下网络编程的区别**

- 前者使用的网络头文件是winsock2.h，库是ws2_32.lib，后者则是soket
- 在现实中一般是linux的物理机作为服务端，而windows的物理机作为客户端进行网络交互
- 前者在初始化和结束时需要额外进行两个操作，并且关闭socket连接时有专门的关闭函数

```java
//开始初始化WSAStartUp函数
int WSAStartUp(WORD wVersionRequested, LPWSADATA lpWSAData);
 
//关闭socket连接，成功返回0
int closesocket(SOCKET s);
 
//结束初始化WSACleanUp，成功返回0
int WSACleanUp(void)
```

- 前者返回的文件名称呼变为**文件句柄，并且不像后者socket句柄和普通文件句柄是不一样的**
- 前者在使用socket句柄的IO函数时大多参数都有多一个flags参数
- 前者的交互基于send和recv，后者的交互基于read和write，但并不代表两者的含义是一样的，在linux中也是存在send函数
- 前者的socket返回值是一个Socket结构体，当然也可以使用常量去与之对比

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E7%90%86%E8%A7%A3%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%E5%92%8C%E5%A5%97%E6%8E%A5%E5%AD%97/image%202.png)

## **1.3 详解创建socket函数的三个参数**

**socket函数**

```java
//成功时返回文件描述符，失败返回-1
int socket(int domain, int type, int protocol);
```

### **domain：套接字中使用协议族信息**

第一个参数表示协议分类的信息，全章的内容都是基于第一个协议族讨论的，其他的都是不常用，最终使用的协议会用第一个参数+第三个参数来决定

| **名称** | **协议族** |
| --- | --- |
| PF_INET | IPv4互联网协议族 |
| PF_INET6 | IPv6互联网协议族 |
| PF_LOCAL | 本地通信的UNIX协议族 |
| PF_PACKET | 底层套接字的协议族 |
| PF_IPX | IPX Novell协议族 |

### **type：套接字类型**

这一部分就对应传输层的两种主流协议，分别是面向连接的套接字和面向数据的套接字

- 面向连接的套接字（SOCK_STREAM）：可靠的、按序传递的、数据无边界的、基于字节的面向连接数据传输方式的套接字，这一部分去学习TCP协议的具体原理即可知道如何保证可靠、按序等

> 对于数据无边界的理解，就是写与读的次数并不对等，基于网卡中有发送和接收缓存区的存在，写入可以只写一次，接收可以分多次，同样相反写入可以写多次，而接收直接一次即可
> 
- 面向数据的套接字（SOCK_DGRAM）：不可靠的、不按序传递的、数据有边界的、以数据的告诉传输为目的的套接字

### **protocol：协议的最终选择**

其实到这里应该有一些疑惑，就是前两个参数应该就能决定一个协议了啊，但是会存在相同协议族中存在多个数据传输方式相同的协议，此时就需要第三个参数来决定，例如IPv4协议族下面向连接的套接字，满足前面两个参数的协议只有TCP，所以第三个参数为IPPROTO_TCP

### **C语言中表示IPv4的数据传输结构体：sockaddr_in**

在原始结构题中还存在sockaddr，后缀为in的是为了扩充原始字段的类型大小，同样也做了向前适配sockaddr的措施，下图中sin_zero[8]就是向前适配的标识符。

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E7%90%86%E8%A7%A3%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%E5%92%8C%E5%A5%97%E6%8E%A5%E5%AD%97/image%203.png)

注意：在使用bind函数时，就需要传递类型为sockaddr的参数，这时就需要把sockaddr_in转换为sockaddr

## **1.4 网络字节序和地址变换**

### **网络字节序：采用CPU存储顺序中的大端存储，即数据的高位字节存储在低位地址**

那么即使小端存储的CPU接收到网络数据时，都知道遵循网络字节序将数据转换为大端存储。在c语言中的网络字节序转化函数为：

![image.png](TCP%20IP%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%20%E7%90%86%E8%A7%A3%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B%E5%92%8C%E5%A5%97%E6%8E%A5%E5%AD%97/image%204.png)

- htons：h代表主机字节序，n代表网络字节序，即代表把short类型的数据从主机序转化为网络序
- 其中s代表short、l代表long（Linux中一个long占4个字节）
- 当s作为后缀时，代表端口号进行转换；当l作为后缀是，代表IP地址进行转换

相互转换大端小端示例代码，可以看到本人的电脑M1是小端存储

**示例** 

```java
#include <stdio.h>
#include <arpa/inet.h>
 
int main(int argc, char *argv[]) {
    unsigned short host_port = 0x1234;
    unsigned short net_port;
    unsigned long host_addr = 0x12345678;
    unsigned long net_addr;
 
    net_port = htons(host_port);
    net_addr = htonl(host_addr);
 
    //Host ordered port: 0x1234
    printf("Host ordered port: %#x \n", host_port);
    //Network ordered port: 0x3412
    printf("Network ordered port: %#x \n", net_port);
    //Host ordered address: 0x12345678
    printf("Host ordered address: %#lx \n", host_addr);
    //Network ordered address: 0x78563412
    printf("Network ordered address: %#lx \n", net_addr);
    return 0;
}
```

总结：在传输过程中其实无需考虑这些事情，OS和网络协议方面都会帮我们自动转换

## **1.5 网络地址的初始化与分配**

这里可以学习到几个点

- 在传入结构体sockaddr_in中的IP地址时，需要把点分10进制表示法（127.0.0.1）转换为32位整数型
- 服务端的准备是在bind函数中完成的，而客户端的准备则是在connect函数中完成的

## 入Q就代表传输终止，那种规则就是应用层协议