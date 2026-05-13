# Redis设计与实现（九）| RDB和AOF持久化

type: Post
status: Published
date: 2022/07/04
summary: 因为Redis是内存数据库，它将自己的数据库状态储存在内存里面，所以如果不想办法将储存在内存中的数据库状态保存到磁盘里面，那么一旦服务器进程退出，服务器中的数据库状态也会消失不见。为了解决这个问题，Redis提供了RDB持久化功能，这个功能可以将Redis在内存中的数据库状态保存到磁盘里面，避免数据意外丢失
tags: Redis
category: 缓存

# 一、RDB

因为Redis是内存数据库，它将自己的数据库状态储存在内存里面，所以如果不想办法将储存在内存中的数据库状态保存到磁盘里面，那么一旦服务器进程退出，服务器中的数据库状态也会消失不见。为了解决这个问题，Redis提供了RDB持久化功能，这个功能可以将Redis在内存中的数据库状态保存到磁盘里面，避免数据意外丢失

RDB配置相关命令

- dbfilename dump.rdb
    - 设置本地数据库文件名，默认值为 dump.rdb
    - 通常设置为dump-端口号.rdb
- dir
    - 设置存储.rdb文件的路径
    - 通常设置成存储空间较大的目录中，目录名称data
- rdbcompression yes
    - 设置存储至本地数据库时是否压缩数据，默认为 yes，采用 LZF 压缩
    - 通常默认为开启状态，如果设置为no，可以节省 CPU 运行时间，但会使存储的文件变大（巨大）
- rdbchecksum yes
    - 设置是否进行RDB文件格式校验，该校验过程在写文件和读文件过程均进行
    - 通常默认为开启状态，如果设置为no，可以节约读写性过程约10%时间消耗，但是存储一定的数据损坏风险

## 1.RDB文件的创建与载入

有两个Redis命令可以用于生成RDB文件，一个是save，另一个是bgsave

- save命令会阻塞Redis服务器进程，直到RDB文件创建完毕为止，在服务器进程阻塞期间，服务器不能处理任何命令请求
- bgsave命令会派生出一个子进程，然后由子进程负责创建RDB文件，服务器进程（父进程）继续处理命令请求
- RDB文件的载入工作启动时自动执行

**save命令执行时的服务器状态**

当save命令执行时，Redis服务器会被阻塞，所以当save命令正在执行时，客户端发送的所有命令请求都会被拒绝

只有在服务器执行完save命令、重新开始接受命令请求之后，客户端发送的命令才会被处理

**bgsave命令执行时的服务器状态**

因为bgsave命令的保存工作是由子进程执行的，所以在子进程创建RDB文件的过程中，Redis服务器仍然可以继续处理客户端的命令请求，但是，在bgsave命令执行期间，服务器处理save、bgsave、bgrewriteaof三个命令的方式会和平时有所不同

- 在bgsave命令执行期间，客户端发送的save命令会被服务器拒绝，服务器禁止save命令和bgsave命令同时执行是为了避免父进程（服务器进程）和子进程同时执行两个rdbSave调用，防止产生竞争条件
- 在bgsave命令执行期间，客户端发送的bgsave命令会被服务器拒绝，因为同时执行两个bgsave命令也会产生竞争条件
- bgwriteaof和bgsave两个命令不能同时执行
    - 如果bgsave命令正在执行，那么客户端发送的bgwriteaof命令会被延迟到bgsave命令执行完毕之后执行
    - 如果bgwriteaof命令正在执行，那么客户端发送的bgsave命令会被服务器拒绝

RDB文件载入时的服务器状态

服务器再载入RDB文件期间，会一直处于阻塞状态，直到载入工作完成

## 2.自动间隔性保存

因为BGSAVE命令可以在不阻塞服务器进程的情况下执行，所以Redis允许用户通过设置服务器配置的save选项，让服务器每隔一段时间自动执行一次BGSAVE命令

用户可以设置多个保存条件，只要其中任意一个满足，就会执行BGSAVE命令

例如：

```bash
save 900 1		# 900秒内修改1次数据，则保存
save 300 10		# 300秒内修改10次数据，则保存
save 60 10000	# 60秒内修改10000次数据，则保存
```

① 设置保存条件

服务器程序会根据save选项所设置的保存条件，设置服务器状态redisServer结构的saveparams属性

```bash
struct redisServer {
	// 保存save配置参数
	struct saveparam *saveparams;
	...
};
```

saveparams属性是一个数组，数组中的每个元素都是一个saveparam结构，每个saveparam结构都保存了一个save选项设置的保存条件。saveparam的结构如下

```bash
struct saveparam {
	// 设定的秒数
	time_t seconds;
	// 规定时间内的修改次数
	int changes;
};
```

如果设置参数如上所示，那么该数组的情况如下

![image.png](Redis%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%AE%9E%E7%8E%B0%EF%BC%88%E4%B9%9D%EF%BC%89%20RDB%E5%92%8CAOF%E6%8C%81%E4%B9%85%E5%8C%96/image.png)

② dirty计数器和lastsave属性

- dirty计数器记录距离上一次成功执行save命令或者bgsave命令之后，服务器对数据库状态（服务器中的所有数据库）进行了多少次修改（包括写入、删除、更新等操作）
- lastsave属性是一个UNIX时间戳，记录了服务器上一次成功执行save命令或者bgsave命令的时间

```
struct redisServer {
	...
	// 上次save到现在Redis中数据修改的次数
	long long dirty;                /* Changes to DB from the last save */
	// 上一次成功save到现在所经过的时间
	time_t lastsave;                /* Unix time of last successful save */
	...
};
```

③ 检查保存条件是否满足

Redis的服务器周期性操作函数serverCron默认每隔100毫秒就会执行一次，该函数用于对正在运行的服务器进行维护，它的其中一项工作就是检查save选项所设置的保存条件是否已经满足，如果满足的话，就执行bgsave命令

- 程序会遍历并检查saveparams数组中的所有保存条件，只要有任意一个条件满足就会执行BGSAVE命令

### 3. RDB优缺点

优点

- RDB是一个紧凑压缩的二进制文件，存储效率较高
- RDB内部存储的是redis在某个时间点的数据快照，非常适合用于数据备份，全量复制等场景
- RDB恢复数据的速度要比AOF快很多
- 应用：服务器中每X小时执行bgsave备份，并将RDB文件拷贝到远程机器中，用于灾难恢复

缺点

- RDB方式无论是执行指令还是利用配置，无法做到实时持久化，具有较大的可能性丢失数据
- bgsave指令每次运行要执行fork操作创建子进程，要牺牲掉一些性能
- Redis的众多版本中未进行RDB文件格式的版本统一，有可能出现各版本服务之间数据格式无法兼容现象

# 二、AOF

除了RDB持久化功能之外，Redis还提供了AOF（Append Only File）持久化功能。与RDB持久化通过保存数据库中的键值对来记录数据库状态不同，AOF持久化是通过保存Redis服务器所执行的写命令来记录数据库状态的

![image.png](Redis%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%AE%9E%E7%8E%B0%EF%BC%88%E4%B9%9D%EF%BC%89%20RDB%E5%92%8CAOF%E6%8C%81%E4%B9%85%E5%8C%96/image%201.png)

AOF功能开启

- 配置是否开启AOF持久化

```bash
appendonly yes|no  # 是否开启AOF持久化，默认不开启
```

配置AOF写数据策略

- always：每次写入操作均同步到AOF文件中
- everysec：每秒将缓冲区中的指令同步到AOF文件中
- no：由操作系统控制每次同步到AOF文件的周期

```bash
appendfsync always|everysec|no
```

## 1.AOF持久化实现

AOF持久化功能的实现可以分为命令追加（append）、文件写入、文件同步（sync）三个步骤

### 1.1 命令追加

当AOF持久化功能处于打开状态时，服务器在执行完一个写命令之后，会以协议格式将被执行的写命令追加到服务器状态的aof_buf缓冲区的末尾

```bash
struct redisServer {
...
// AOF缓冲区，本质上是一个动态字符串
sds aof_buf;      /* AOF buffer, written before entering the event loop */
...
};
```

例如：

```bash
127.0.0.1:6379> SET KEY VALUE
```

那么服务器就会将一下协议内容追加到aof_buf缓冲区末尾

```bash
3\r\n$ 3 \r\nSET\r\n$ 3 \r \nKEY\r\n$5 \r\nVALUE\r\n
```

### 1.2 AOF 文件的写入与同步

Redis的服务器进程就是一个事件循环（loop），这个循环中的文件事件负责接收客户端的命令请求，以及向客户端发送命令回复，而时间事件则负责执行像serverCron函数这样需要定时运行的函数

因为服务器在处理文件事件时可能会执行写命令，使得一些内容被追加到aof_buf缓冲区里面，所以在服务器每次结束一个事件循环之前，它都会调用flushAppendOnlyFile函数，考虑是否需要将aof_buf缓冲区中的内容写入和保存到AOF文件里面

伪代码：

```
def eventLoop():
while True:
	// 处理文件事件，接受命令请求以及发送命令回复
	// 处理命令请求时可能会有新内容被追加到aof_buf缓冲区中
	processFileEvents()

	// 处理事件事件
	processTimeEvents()

	// 考虑是否将aof_buf 中的内容写入和保存到AOF文件中
	// 由配置的appendfsync 属性决定
```

AOF持久化的效率和安全性

服务器配置 appendfsync 选项的值来直接决定AOF持久化功能的效率和安全性

- always：每个事件都要将aof_buf 缓冲区的内容写入到AOF内存缓存区中，并且同步AOF文件，所以效率是最慢的，但是安全性是最高的，就算服务器宕机，也只会丢失一个事件
- everysec：每个事件都要将aof_buf 缓冲区的内容写入到AOF内存缓存区中，每隔一秒子线程对AOF文件进行一次同步，效率来说，该模式也很快，并且就算出现故障，也只会丢失一秒钟的事件，所以是默认配置
- no：每个事件都要将aof_buf 缓冲区的内容写入到AOF内存缓存区中，但是何时将缓存区同步到AOF文件，则由操作系统决定，所以该AOF写入操作是最快的，但是，同步时间是最慢的，平摊来看，效率和everysec相似，出现故障会丢失上次同步之后的所有命令

## 2. AOF文件的载入和数据还原

因为AOF文件里面包含了重建数据库状态所需的所有写命令，所以服务器只要读入并重新执行一遍AOF文件里面保存的写命令，就可以还原服务器关闭之前的数据库状态

具体步骤：

1. 创建一个不带网络连接的伪客户端（fake client）
    - 因为Redis的命令只能在客户端上下文中执行，而载入AOF文件时所使用的命令直接来源于AOF文件而不是网络连接，所以服务器使用了一个没有网络连接的伪客户端来执行AOF文件保存的写命令，伪客户端执行命令的效果和带网络连接的客户端执行命令的效果完全一样
2. 从AOF文件中分析并读出一条写指令，伪客户端执行该写指令
3. 一直重复上部操作，直到AOF文件所有写命令被执行完

![image.png](Redis%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%AE%9E%E7%8E%B0%EF%BC%88%E4%B9%9D%EF%BC%89%20RDB%E5%92%8CAOF%E6%8C%81%E4%B9%85%E5%8C%96/image%202.png)

## 3.AOF重写

因为AOF持久化是通过保存被执行的写命令来记录数据库状态的，所以随着服务器运行时间的流逝，AOF文件中的内容会越来越多，文件的体积也会越来越大，如果不加以控制的话，体积过大的AOF文件很可能对Redis服务器、甚至整个宿主计算机造成影响，并且AOF文件的体积越大，使用AOF文件来进行数据还原所需的时间就越多

例如：

```bash
127.0.0.1:6379> RPUSH list1 A B
(integer) 2
127.0.0.1:6379> RPUSH list1 C
(integer) 3
127.0.0.1:6379> RPUSH list1 D E
(integer) 5
127.0.0.1:6379> LPOP list1
"A"
127.0.0.1:6379> LPOP list1
"B"
127.0.0.1:6379> RPUSH list1 F
(integer) 4
```

如果通过一条一条记录，则需要保存六条指令，而对于实际应用，肯定比上述案例要复杂的多，造成的问题也更严重，所以Redis提供重写功能，Redis服务器可以创建一个新的AOF文件代替现有的AOF文件，两个文件保存数据库住哪个台相同，新的AOF文件不会包含任何冗余命令，所以体积小得多

- 手动重写：输入命令

```bash
127.0.0.1:6379> bgrewriteaof
```

自动重写 ：配置相关参数

```bash
//触发重写的最小大小
auto-aof-rewrite-min-size size
//触发重写须达到的最小百分比
auto-aof-rewrite-percentage percent
```

### 3.1 AOF文件重写的实现

Redis将生成新AOF文件替换旧AOF文件的功能命名为“AOF文件重写”，但实际上，AOF文件重写并不需要对现有的AOF文件进行任何读取、分析或者写入操作，这个功能是通过读取服务器当前的数据库状态来实现的

例如上面的命令等同于

```bash
127.0.0.1:6379> RPUSH list1 C D E F
```

服务器想要尽量少的命令来记录list键记录的状态，最简单高效的方法不是读取现有AOF文件，而是从数据库直接读取键list的值，然后用以上命令代替

实现伪代码如下：

```bash
def aof_rewrite (new_aof_file_name) :
#创建新AoF文件
f = create_file (new_aof_file_name)#遍历数据库
for db in redisserver.db :
#忽略空数据库
if db.is_empty() : continue
#写入SELECT命令，指定数据库号码
f.write_command ("SELECT" +[db.id](http://db.id/))
#遍历数据库中的所有键
for key in db:
#忽略已过期的键
if [key.is](http://key.is/) expired() : continue
#根据键的类型对键进行重写
if key.type == string:
rewrite_string (key)
elif key.type == List :
rewrite_list (key)
elif key.type == Hash:
rewrite_hash (key)
elif key.type -= set:
rewrite_set (key)
elif key.type -= Sortedset:
rewrite_sorted_set (key)
#如果键带有过期时间，那么过期时间也要被重写
if key.have_expire_time ( ) :
rewrite_expire_time ( key)
#写入完毕，关闭文件
f.close ()
```

```bash
def rewrite_string ( key) :
#使用GET命令获取字符串键的值value = GET (key)
#使用SET命令重写字符串键
f.write_command (SET,key, value)

def rewrite_list (key) :
#使用LRANGE命令获取列表键包含的所有元素
iteml, item2, ..., itemN = LRANGE (key,0,-1)
#使用RPUSH命令重写列表键	
f.write_command(RPUSH,key, iteml, item2, ..., itemN)

def rewrite_hash (key) :
#使用HGETALL命令获取哈希键包含的所有键值对
fieldl, valuel, field2, value2, ..., fieldN, valueN=HGETALL(key)
#使用HMSET命令重写哈希键
f.write_command (HMSET,key, fieldl, valuel, field2, value2, ..., fieldN, valueN)

def rewrite_set (key) ;
#使用SMEMBERS命令获取集合键包含的所有元素
eleml, elem2, ..., elemN = SMEMBERS (key)
#使用sADD命令重写集合键
f.write_command (SADD,key, eleml, elem2, ..., elemN)

def rewrite_sorted_set (key) :
#使用ZRANGE命令获取有序集合键包含的所有元素
member1, scorel,member2,score2, ..., memberN,sc
oreN=ZRANGE(key, 0,-1,"WITHSCORES")
#使用zADD命令重写有序集合键
f.write_command (ZADD，key, scorel, member1,score2,member2, ..., scoreN, memberN)

def rewrite_expire_time (key):
#获取毫秒精度的键过期时间戳
timestamp = get_expire_time_in_unixstamp (key)
#使用PEXPIREAT命令重写键的过期时间
f.write_command (PEXPIREAT,key, timestamp)

```

因为aof_rewrite函数生成的新AOF文件只包含还原当前数据库状态所必须的命令，所以新AOF文件不会浪费任何硬盘空间

注意：为了避免在执行命令时造成客户端输入缓冲区溢出，如果元素数量超过了一定值，那么重写程序还是会使用多条命令来记录键的值

### 3.2 AOF后台重写

为了防止写入aof_buf 文件，长时间阻塞Redis服务器，所以Redis决定将AOF重写程序放到子进程里执行，这样做可以有以下两个目的

- 子进程进行AOF重写期间，服务器进程（父进程）可以继续处理命令请求
- 子进程带有服务器进程的数据副本，使用子进程而不是线程，可以在避免使用锁的情况下，保证数据的安全性

不过，使用子进程也有一个问题需要解决，因为子进程在进行AOF重写期间，服务器进程还需要继续处理命令请求，而新的命令可能会对现有的数据库状态进行修改，从而使得服务器当前的数据库状态和重写后的AOF文件所保存的数据库状态不一致

为了解决这种数据不一致问题，Redis服务器设置了一个AOF重写缓冲区（保存了子进程在重写过程中，主进程执行的操作），这个缓冲区在服务器创建子进程之后开始使用，当Redis服务器执行完一个写命令之后，它会同时将这个写命令发送给AOF缓冲区和AOF重写缓冲区，如下图所示

![image.png](Redis%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%AE%9E%E7%8E%B0%EF%BC%88%E4%B9%9D%EF%BC%89%20RDB%E5%92%8CAOF%E6%8C%81%E4%B9%85%E5%8C%96/image%203.png)

也就是说在子进程执行AOF重写期间，服务器进程需要执行以下三个工作

- 执行客户端发来的命令
- 将执行后的写命令追加到AOF缓冲区
- 将执行后的写命令追加到AOF重写缓冲区

这样可以保证

- AOF缓冲区的内容会定期被写入和同步到AOF文件，对现有AOF文件的处理工作会如常进行
- 从创建子进程开始，服务器执行的所有写命令都都会记录到AOF重写缓冲区里

当子进程完成AOF重写工作之后，它会向父进程发送一个信号，父进程在接到该信号之后，会调用一个信号处理函数，并执行以下工作

- 将AOF重写缓冲区中的所有内容写入到新AOF文件中，这时新AOF文件所保存的数据库状态将和服务器当前的数据库状态一致（同步操作）
- 对新的AOF文件进行改名，原子地（atomic）覆盖现有的AOF文件，完成新旧两个AOF文件的替换（原子操作）

在整个AOF后台重写过程中，只有信号处理函数执行时会对服务器进程（父进程）造成阻塞，在其他时候，AOF后台重写都不会阻塞父进程，这将AOF重写对服务器性能的影响降到了最低

![image.png](Redis%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%AE%9E%E7%8E%B0%EF%BC%88%E4%B9%9D%EF%BC%89%20RDB%E5%92%8CAOF%E6%8C%81%E4%B9%85%E5%8C%96/image%204.png)

以上就是AOF后台重写，也就是BGREWRITEAOF命令的实现原理

# 三、RDB 和 AOF

对数据非常敏感，建议使用默认的AOF持久化方案

- AOF持久化策略使用everysecond，每秒钟fsync一次。该策略redis仍可以保持很好的处理性能，当出现问题时，最多丢失0-1秒内的数据。
- 注意：由于AOF文件存储体积较大，且恢复速度较慢

数据呈现阶段有效性，建议使用RDB持久化方案

- 数据可以良好的做到阶段内无丢失（该阶段是开发者或运维人员手工维护的），且恢复速度较快，阶段 点数据恢复通常采用RDB方案
- 注意：利用RDB实现紧凑的数据持久化会使Redis降的很低

综合比对

- RDB与AOF的选择实际上是在做一种权衡，每种都有利有弊
- 如不能承受数分钟以内的数据丢失，对业务数据非常敏感，选用AOF
- 如能承受数分钟以内的数据丢失，且追求大数据集的恢复速度，选用RDB
- 灾难恢复选用RDB
- 双保险策略，同时开启 RDB 和 AOF，重启后，Redis优先使用 AOF 来恢复数据，降低丢失数据