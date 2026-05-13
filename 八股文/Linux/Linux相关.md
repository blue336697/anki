# Linux相关

## 前言：命令基于centos

- tailf -n 行数
- ssh(22)/ftp(21)
- ps -ef | grep 进程名
- netstat -lnp | grep 端口号
- rm -rf 文件名/文件夹名
- ps au 查看进程/ps -p后面跟实际想看的进程号
- curl ifconfig.me 查看自己的出口外网IP

### **0、su和sudo**

切换用户：

1. sudo su - 用户名
2. sudo su 用户名
3. sudo -i -u 用户名
4. su 用户名

### **1、find**

在CentOS中，你可以使用`find`命令来查找文件或文件夹。以下是一些基本的使用方法：

1. 在当前目录及其子目录中查找名为"filename"的文件或文件夹：
    
    find . -name filename
    
2. 在根目录及其子目录中查找名为"filename"的文件或文件夹：
    
    find / -name filename
    
3. 在当前目录及其子目录中查找名为"filename"的文件：
    
    find . -type f -name filename
    
4. 在当前目录及其子目录中查找名为"filename"的文件夹：
    
    find . -type d -name filename
    

在以上命令中，`.`代表当前目录，`/`代表根目录，`-name`后面跟的是你要查找的文件或文件夹的名字，`-type f`表示只查找文件，`-type d`表示只查找文件夹。你需要将`filename`替换为你要查找的文件或文件夹的名字。

### **2、which**

which命令

### **3、copy命令**

在Linux中，你可以使用`cp`命令来拷贝文件。以下是一些基本的使用方法：

1. 将文件`file1.txt`拷贝到当前目录下的`folder1`文件夹：
    
    cp file1.txt folder1/
    
2. 将文件`file1.txt`拷贝到其他位置，例如`/path/to/folder2`：
    
    cp file1.txt /path/to/folder2/
    

在以上命令中，你需要将`file1.txt`、`folder1`和`/path/to/folder2`替换为你的实际文件名和文件夹路径。

在Linux中，你可以使用`cp`命令并加上`-r`（或`--recursive`）选项来拷贝文件夹。以下是一些基本的使用方法：

1. 将文件夹`folder1`拷贝到当前目录下的`folder2`文件夹：
    
    cp -r folder1 folder2/
    
2. 将文件夹`folder1`拷贝到其他位置，例如`/path/to/folder3`：
    
    cp -r folder1 /path/to/folder3/
    

在以上命令中，你需要将`folder1`、`folder2`和`/path/to/folder3`替换为你的实际文件夹名和路径。`-r`选项表示递归复制，即复制文件夹及其所有子文件和子文件夹。

### **4、env命令**

可以一键看centos的全部环境变量

### **5、nslookup命令**

查看域名和IP的对应关系

```java

> baidu.com
Server:     2408:8409:2410:db66::6f
Address:    2408:8409:2410:db66::6f#53
 
Non-authoritative answer:
Name:   baidu.com
Address: 39.156.66.10
Name:   baidu.com
Address: 110.242.68.66
# 退出
> exit
```

---

### **6、tail命令**

```java
# 常规用法
tail xx文件名 -n 行数
 
# 查询关键字
tail -f 文件名 | grep -i "关键字"
grep -i "关键字" 文件名
 
#进入vi以后输入/后跟关键字也能查询
```

---

### **7、yum命令**

```java
yum install
yum update
yum remove
yum clean all && yum makecache
wget -O /etc/yum.repos.d/CentOS-Base-ali.repo http://mirrors.aliyun.com/repo/Centos-7.repo
wget -O /etc/yum.repos.d/CentOS-Base-hw.repo https://repo.huaweicloud.com/repository/conf/CentOS-7-reg.repo
```

---

### **8、netstat命令**

```java
# 查看端口占用
netstat -tlunp
```

---

## 配置Centos的毛坯房

[wget命令下载](https://blog.csdn.net/weixin_39025362/article/details/105836169)

[更换yum下载源](https://zhuanlan.zhihu.com/p/533479432)

下载cmake

```java
wget https://github.com/Kitware/CMake/releases/download/v3.31.0/cmake-3.31.0.tar.gz
 
sudo systemctl stop firewalld    # 停止防火墙服务
sudo systemctl disable firewalld # 禁止防火墙开机自启
 
# 关机
reboot
shutdown -h now:立即关机
poweroff:快速关机
```

---