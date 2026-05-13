# MySQL是怎样运行的：从根儿上理解MySQL | 一条记录的多幅面孔-事务的隔离级别与 MVCC

type: Post
status: Published
date: 2022/03/28
slug: example-7
summary: 我们知道mysql是客户端+服务器端的结构软件，也就是说一个服务器端可能有多个客户端在连着就可以称之为一个会话（Session），同一个服务器可能处理这多个事务，事务是具有隔离性的，就是该事务对于某个数据的访问，其他事务应该排队，对这样效率太低；但我们有需要隔离性来保证数据的正确性，那么就可以牺牲一点点隔离性
tags: Mysql
category: 数据库

# 前言：本博文是对MySQL是怎样运行的：从根儿上理解MySQL这本书的归纳和总结

# 第24章 一条记录的多幅面孔-事务的隔离级别与 MVCC

## 1.事前准备

- 概述

> 为了讲述流畅我们先准备一张表，注意主键是number
> 

```sql
CREATE TABLE hero (
 number INT,
 name VARCHAR(100),
 country varchar(100),
 PRIMARY KEY (number)
) Engine=InnoDB CHARSET=utf8;

# 插入数据
INSERT INTO hero VALUES(1, '刘备', '蜀');

```

## 2.事务隔离级别

- 概述

> 我们知道mysql是客户端+服务器端的结构软件，也就是说一个服务器端可能有多个客户端在连着就可以称之为一个会话（Session），同一个服务器可能处理这多个事务，事务是具有隔离性的，就是该事务对于某个数据的访问，其他事务应该排队，对这样效率太低；但我们有需要隔离性来保证数据的正确性，那么就可以牺牲一点点隔离性
> 

### 2.1 事务并发执行遇到的问题

- 概述

> 对于怎么牺牲我们先要看看如果不保证事务对数据访问的串行执行，在这种情况下会出现什么情况呢？
> 
- 脏写（ Dirty Write ）：**`如果一个事务修改了另一个未提交事务修改过的数据，那就发生了脏写`**

> 我们可以观察两个会话对服务器的修改流程图：
> 
> 
> **Session A 和 Session B 各开启了一个事务， Session B 中的事务先将 number 列为 1 的记录的 name 列更新为 '关羽' ，然后 Session A 中的事务接着又把这条 number 列为 1 的记录的 name 列更新为张飞 。如果之后 Session B 中的事务进行了回滚，那么 Session A 中的更新也将不复存在，这种现象就称之为 `脏写`**
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/8da5bb83dcffd380e819fe03694bc2e6.png)
> 
- 脏读（ Dirty Read）：**`如果一个事务读到了另一个未提交事务修改过的数据，那就意味着发生了 脏读`**

> 同样观察两个会话发生的互动
> 
> 
> **Session A 和 Session B 各开启了一个事务， Session B 中的事务先将 number 列为 1 的记录的
> name 列更新为 '关羽' ，然后 Session A 中的事务再去查询这条 number 为 1 的记录，如果du到列 name 的值为 '关羽' ，而 Session B 中的事务稍后进行了回滚，那么 Session A 中的事务相当于读到了一个不存在的数据，这种现象就称之为`脏读`。**
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/25ae3ca246eef50ce6b3cfa6bed2ef43.png)
> 
- 不可重复读（Non-Repeatable Read）: **如果一个事务只能读到另一个已经提交的事务修改过的数据，并且其他事务每对该数据进行一次修改并提交后，该事务都能查询得到最新值，那就意味着发生了 `不可重复读`**

> 继续查看两个会话
> 
> 
> **我们在 Session B 中提交了几个隐式事务（`注意是隐式事务，意味着语句结束事务就提交了`），这些事务都修改了 number 列为 1 的记录的列 name 的值，每次事务提交之后，如果 Session A 中的事务都可以查看到最新的值，这种现象也被称之为 `不可重复读`**
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/a291cc826df6e0b8d04b6b0bdc361726.png)
> 
- 幻读（Phantom）：**如果一个事务先根据某些条件查询出一些记录，之后另一个事务又向表中插入了符合这些条件的记录，原先的事务再次按照该条件查询时，能把另一个事务插入的记录也读出来，那就意味着发生了 `幻读`**

> 请看下面两个会话
> 
> 
> **Session A 中的事务先根据条件 number > 0 这个条件查询表 hero ，得到了 name 列值为 '刘备' 的记录；之后 Session B 中提交了一个`隐式事务`，该事务向表 hero 中插入了一条新记录；之后Session A 中的事务再根据相同的条件 number > 0 查询表 hero ，得到的结果集中包含 Session B 中的事务新插入的那条记录，这种现象也被称之为 `幻读` 。**
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/51bc8029523dd6a54f64c669793274b8.png)
> 
- 幻读注意事项

> 那如果 Session B 中是删除了一些符合 number > 0 的记录而不是插入新记录，那Session A 中之后再根据 number > 0 的条件读取的记录变少了，这种现象算不算 幻读 呢？明确说一下，这种现象不属于 幻读 ， 幻读 强调的是一个事务按照某个相同条件多次读取记录时，后读取时读到了之前没有读到的记录。
> 
- 小贴士

> 那对于先前已经读到的记录，之后又读取不到这种情况，算啥呢？其实这相当于对每一条记录都发生了不可重复读的现象。幻读只是重点强调了读取到了之前读取没有获取到的记录。即幻读仅专指“新插入的行”
> 

### 2.2 SQL标准中的四种隔离级别

- 前言

> 我们对于前面所说的并发执行可能造成的问题，我们说凡事都有个轻重缓急，那么对于上面这四个情况可以依照严重性排个序：脏写 > 脏读 > 不可重复读 > 幻读
> 
- 概述

> 那么我们曾说道要牺牲事务的隔离性来换取性能，那么有这么一帮人就定义了通用SQL标准，在这个标准中规定了4个隔离级别：
> 
> - `READ UNCOMMITTED` ：未提交读。
> - `READ COMMITTED` ：已提交读。
> - `REPEATABLE READ` ：可重复读。
> - `SERIALIZABLE` ：可串行化。
- 隔离级别允许发生的严重程度

> READ UNCOMMITTED 隔离级别下，可能发生 脏读 、 不可重复读 和 幻读 问题。READ COMMITTED 隔离级别下，可能发生 不可重复读 和 幻读 问题，但是不可以发生 脏读 问题。REPEATABLE READ 隔离级别下，可能发生 幻读 问题，但是不可以发生 脏读 和 不可重复读 的问题。SERIALIZABLE 隔离级别下，各种问题都不可以发生。
> 
- 注意事项

> 你们也许有注意到没有脏写，因为在任何事务隔离级别中他都不被允许发生
> 

### 2.3 MySQL中支持的四种事务隔离级别

- 概述

> 不同的数据库厂商对 SQL标准 中规定的四种隔离级别支持不一样，比方说Oracle就只支持READ COMMITTED和SERIALIZABLE 隔离级别。本书中所讨论的MySQL虽然支持4种隔离级别，但与 SQL标准 中所规定的各级隔离级别允许发生的问题却有些出入，MySQL在REPEATABLE READ隔离级别下，是可以禁止幻读问题的发生的（关于如何禁止我们之后会详细说明的）。
> 
- MySQL的默认隔离级别

> MySQL 的默认隔离级别为 REPEATABLE READ ，我们可以手动修改一下事务的隔离级别。
> 

### 2.3.1 如何设置事务的隔离级别

- 可以通过下面的语句修改

```sql
SET [GLOBAL|SESSION] TRANSACTION ISOLATION LEVEL level;

# level可选的值
level: {
 REPEATABLE READ
 | READ COMMITTED
 | READ UNCOMMITTED
 | SERIALIZABLE
}

```

- 不同作用域的对事务产生的影响

> 使用GLOBAL关键字（在全局范围影响）：只对执行完该语句之后产生的会话起作用。当前已经存在的会话无效。
> 

```sql
 SET GLOBAL TRANSACTION ISOLATION LEVEL SERIALIZABLE;

```

> 使用 SESSION 关键字（在会话范围影响）：对当前会话的所有后续的事务有效。该语句可以在已经开启的事务中间执行，但不会影响当前正在执行的事务。如果在事务之间执行，则对后续的事务有效。
> 

```sql
SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;

```

> 上述两个关键字都不用（只对执行语句后的下一个事务产生影响）：只对当前会话中下一个即将开启的事务有效。下一个事务执行完后，后续事务将恢复到之前的隔离级别。该语句不能在已经开启的事务中间执行，会报错的。
> 

```sql
 SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

```

- 在服务器运行时修改

> 如果我们在服务器启动时想改变事务的默认隔离级别，可以修改启动参数 transaction-isolation 的值，比方说我们在启动服务器时指定了--transaction-isolation=SERIALIZABLE，那么事务的默认隔离级别就从原来的REPEATABLE READ 变成了 SERIALIZABLE 。
> 
- 查看当前会话默认的隔离级别

> 想要查看当前会话默认的隔离级别可以通过查看系统变量 transaction_isolation 的值来确定：
> 

```sql
mysql> SHOW VARIABLES LIKE 'transaction_isolation';
# 下面这个更简便
mysql> SELECT @@transaction_isolation;

```

## 3. MVCC原理

### 3.1 版本链

### 3.1.1 回顾两个必要隐藏列（trx_id、roll_pointer）

- 概述

> 我们前面说过对于InnoDB的存储引擎来说它的聚簇索引记录中都包含两个必要的隐藏列（ row_id 并不是必要的，我们创建的表中有主键或者非NULL的UNIQUE键时都不会包含 row_id 列）：
> 
> - `trx_id` ：每次一个事务对某条聚簇索引记录进行改动时，都会把该事务的 事务id 赋值给 trx_id 隐藏列。
> - `roll_pointer` ：每次对某条聚簇索引记录进行改动时，都会把旧的版本写入到 undo日志 中，然后这个隐藏列就相当于一个指针，可以通过它来找到该记录修改前的信息。

> 比如说我们的表中含有一条记录，并且该记录的对应事务ID为80，如下图展示两个隐藏列的引用关系
> 
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/6a7799b5cf655f2b35f758cb36dbd875.png)
> 
- 注意

> 实际上insert undo只在事务回滚时起作用，当事务提交后，该类型的undo日志就没用了，它占用的Undo Log Segment也会被系统回收（也就是该undo日志占用的Undo页面链表要么被重用，要么被释放）。虽然真正的insert undo日志占用的存储空间被释放了，但是roll_pointer的值并不会被清除，roll_pointer属性占用7个字节，第一个比特位就标记着它指向的undo日志的类型，如果该比特位的值为1时，就代表着它指向的undo日志类型为insert undo。所以我们之后在画图时都会把insert undo给去掉，大家留意一下就好了。
> 

### 3.1.2 通过更新操作引入版本链

- 概述

> 假如在之后有两个事务id分别为100、200的事务对这条记录进行update操作时流程如下：
也许你会想能不能在两个事务交叉更新一个数据呢，答案是不行因为这样就沦为脏写了啊，
> 
> 
> **InnoDB使用锁来保证不会有脏写情况的发生，也就是在第一个事务更新了某条记录后，就会给这条记录加锁，另一个事务再次更新时就需要等待第一个事务提交了，把锁释放之后才可以继续更新。`这个真的很重要，当更新操作去执行时，肯定是先读后写，这个读一定是当前读，也就是说必须拿到最新的数据，如果别的事务提前也在更新这条记录并且还未提交事务。那么当前事务会进入锁等待`**
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/a9e348107db80694b58a82c96c2a6b80.png)
> 
- 流程图解读

> 对于每次对记录的改动都会记录相对应的undo日志，
> 
> 
> **每条日志也都会有一个 roll_pointer属性**
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/1d660fb18e9735de80ad3b2d3c1be7de.png)
> 
> **都会将旧值放到一条 undo日志 中，就算是该记录的一个旧版本，随着更新次数的增多，所有的版本都会被 roll_pointer 属性连接成一个链表，我们把这个链表称之为 版本链**
> 
> ```
> 版本链的头节点就是当前记录最新的值
> ```
> 

### 3.2 ReadView

- 概述

> 我们前面说到了事务四种不同的隔离级别
> 
> - 对于未提交读（read uncommitted）的事务来说，由于可以读到未提交事务修改过的记录，所以读取直接用最新的版本就好
> - 对于串行化的事务，读取数据是要经过锁的过滤的稍后一章详解
> - 对于提交读（read commit）和重复读（repeatable read）来说，都必须保证读取到已提交了的事务修改过的记录，**也就是说一个未提交的事务修改过的记录是不能读取到的**

> 那么现在有一个核心的问题，怎么区别这些记录的版本呢，即需要判断版本链的不同版本对不同事务的可见性，为此则提出了ReadView的概念
> 
- ReadView的四个重要属性

> m_ids ：表示在生成 ReadView 时当前系统中活跃的读写事务的 事务id 列表。min_trx_id ：表示在生成 ReadView 时当前系统中活跃的读写事务中最小的 事务id ，也就是m_ids 中的最小值。max_trx_id ：表示生成 ReadView 时系统中应该分配给下一个事务的 id 值。creator_trx_id ：表示生成该 ReadView 的事务的 事务id 。
> 
- 注意事项

> 注意max_trx_id并不是m_ids中的最大值，事务id是递增分配的。比方说现在有id为1，2，3这三个事务，之后id为3的事务提交了。那么一个新的读事务在生成ReadView时，m_ids就包括1和2，min_trx_id的值就是1，max_trx_id的值就是4。我们前边说过，只有在对表中的记录做改动时（执行INSERT、DELETE、UPDATE这些语句时）才会为事务分配事务id，否则在一个只读事务中的事务id值都默认为0。
> 

### 3.2.1 判断记录某个版本是否可见的步骤

1. 如果被访问版本的 `trx_id` 属性值与 ReadView 中的`creator_trx_id`值**相同**，意味着当前事务在访问它自己修改过的记录，所以该版本可以被当前事务访问。
2. 如果被访问版本的`trx_id`属性值**小于** ReadView 中的 `min_trx_id` 值，表明生成该版本的事务在当前事务生成 ReadView 前已经提交，所以该版本可以被当前事务访问。
3. 如果被访问版本的 `trx_id` 属性值**大于** ReadView 中的 `max_trx_id` 值，表明生成该版本的事务在当前事务生成 ReadView 后才开启，所以该版本不可以被当前事务访问。
4. 如果被访问版本的`trx_id`属性值在 ReadView 的 `min_trx_id` 和`max_trx_id`**之间**，那就需要判断一下`trx_id` 属性值是不是在`m_ids`列表中，**如果在，说明创建 ReadView 时生成该版本的事务还是活跃的，该版本不可以被访问；如果不在，说明创建 ReadView 时生成该版本的事务已经被提交，该版本可以被访问。**

> 如果某个版本的数据对当前事务不可见的话，那就顺着版本链找到下一个版本的数据，继续按照上边的步骤判断可见性，依此类推，直到版本链中的最后一个版本。如果最后一个版本也不可见的话，那么就意味着该条记录对该事务完全不可见，查询结果就不包含该记录。
> 

### 3.2.2 READ COMMITTED —— 每次读取数据前都生成一个ReadView

- 前言

> 在 MySQL 中， READ COMMITTED 和 REPEATABLE READ 隔离级别的的一个非常大的区别就是它们生成ReadView的时机不同
> 
- 事前准备

> 我们向hero表中添加一条由事务id为80的事务插入的一条记录
> 
> 
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/cbb601595d3387822609cb1bec27e554.png)
> 
- 过程分析

> 比如说现在系统内有两个事务id分别为100、200的事务在执行；注意只有事务在做修改（插入、删除、更新）时才会被分配一个单独的事务id，这个事务id是递增的
> 

```sql
# Transaction 100
BEGIN;
UPDATE hero SET name = '关羽' WHERE number = 1;
UPDATE hero SET name = '张飞' WHERE number = 1;
# Transaction 200
BEGIN;
# 更新了一些别的表的记录
...

```

- 更新后版本链展示

> 
> 
- 假设现在有一个使用 READ COMMITTED 隔离级别的事务开始执行（**再次强调生成只读事务的id为0**）

> 执行过程如下：
> 
> - 在执行 `SELECT` 语句时会先生成一个`ReadView ， ReadView 的 m_ids`列表的内容就是`[100, 200] ，min_trx_id 为 100 ， max_trx_id 为 201 ， creator_trx_id 为 0`。
> - 然后从版本链中挑选可见的记录，从图中可以看出，最新版本的列 `name` 的内容是 '张飞' ，该版本的`trx_id` 值为 100 ，在`m_ids`列表内，所以不符合可见性要求，根据`roll_pointer`跳到下一个版本。
> - 下一个版本的列`name`的内容是 '关羽' ，该版本的`trx_id`值也为`100`，也在 `m_ids` 列表内，所以也不符合要求，继续跳到下一个版本。
> - 下一个版本的列 name 的内容是 '刘备' ，该版本的 `trx_id` 值为 80 ，小于 `ReadView` 中的 `min_trx_id` 值100 ，所以这个版本是符合要求的，最后返回给用户的版本就是这条列 name 为 '刘备' 的记录。

```sql
# 使用READ COMMITTED隔离级别的事务
BEGIN;
# SELECT1：Transaction 100、200未提交
SELECT * FROM hero WHERE number = 1; # 得到的列name的值为'刘备'

```

- 现在将事务id为100的提交一下

```sql
# Transaction 100
BEGIN;
UPDATE hero SET name = '关羽' WHERE number = 1;
UPDATE hero SET name = '张飞' WHERE number = 1;
COMMIT;

```

- 然后再到事务id为200的事务中更新一下表中hero中number为1的记录

```sql
# Transaction 200
BEGIN;
# 更新了一些别的表的记录
...
UPDATE hero SET name = '赵云' WHERE number = 1;
UPDATE hero SET name = '诸葛亮' WHERE number = 1;

```

- 更新完后的版本链

> 
> 
- 对此版本上再次进行查询操作（SELECT2）生成ReadView（**再次强调生成只读事务的id为0**）

> 在执行SELECT语句时会又会单独生成一个 ReadView ，该ReadView 的 m_ids列表的内容就是[200] （ 事务id 为100的那个事务已经提交了，所以再次生成快照时就没有它了）， min_trx_id 为 200 ，max_trx_id 为 201 ， creator_trx_id 为 0 。然后从版本链中挑选可见的记录，从图中可以看出，最新版本的列 name 的内容是 '诸葛亮' ，该版本的trx_id 值为 200 ，在 m_ids 列表内，所以不符合可见性要求，根据roll_pointer跳到下一个版本。下一个版本的列 name 的内容是 '赵云' ，该版本的 trx_id 值为 200 ，也在 m_ids 列表内，所以也不符合要求，继续跳到下一个版本。下一个版本的列 name 的内容是 '张飞' ，该版本的 trx_id 值为 100 ，小于 ReadView 中的 min_trx_id 值200 ，所以这个版本是符合要求的，最后返回给用户的版本就是这条列 name 为 '张飞' 的记录。
> 

```sql
# 使用READ COMMITTED隔离级别的事务
BEGIN;
# SELECT1：Transaction 100、200均未提交
SELECT * FROM hero WHERE number = 1; # 得到的列name的值为'刘备'
# SELECT2：Transaction 100提交，Transaction 200未提交
SELECT * FROM hero WHERE number = 1; # 得到的列name的值为'张飞'

```

- 最终结果

> 以此类推，如果之后 事务id 为 200 的记录也提交了，再此在使用 READ COMMITTED 隔离级别的事务中查询表hero 中 number 值为 1 的记录时，得到的结果就是 '诸葛亮' 了，具体流程我们就不分析了。总结一下就是：使 用READ COMMITTED隔离级别的事务在每次查询开始时都会生成一个独立的ReadView。
> 

### 3.2.3 REPEATABLE READ —— 在第一次读取数据时生成一个ReadView

- 概述

> 对于使用 REPEATABLE READ 隔离级别的事务来说，只会在第一次执行查询语句时生成一个 ReadView ，之后的查询就不会重复生成了。
> 
- 例子

```sql
# Transaction 100
BEGIN;
UPDATE hero SET name = '关羽' WHERE number = 1;
UPDATE hero SET name = '张飞' WHERE number = 1;
# Transaction 200
BEGIN;
# 更新了一些别的表的记录
...

```

- 版本链情况

> 
> 
- 使用 REPEATABLE READ 隔离级别的事务开始

> 这个 SELECT1 的执行过程如下：
> 
> - 在执行 `SELECT` 语句时会先生成一个`ReadView`， `ReadView 的 m_ids` 列表的内容就是 `[100, 200] ，min_trx_id 为 100 ， max_trx_id 为 201 ， creator_trx_id 为 0` 。
> - 然后从版本链中挑选可见的记录，从图中可以看出，最新版本的列`name`的内容是 '张飞' ，该版本的`trx_id 值为 100 ，在 m_ids` 列表内，所以不符合可见性要求，根据 `roll_pointer` 跳到下一个版本。
> - 下一个版本的列 `name` 的内容是 '关羽' ，该版本的`trx_id`值也为 100 ，也在 `m_ids` 列表内，所以也不符合要求，继续跳到下一个版本。
> - 下一个版本的列`name`的内容是 '刘备' ，该版本的`trx_id`值为 80 ，小于 `ReadView` 中的 `min_trx_id` 值100 ，所以这个版本是符合要求的，最后返回给用户的版本就是这条列 `name` 为 '刘备' 的记录。

```sql
# 使用REPEATABLE READ隔离级别的事务
BEGIN;
# SELECT1：Transaction 100、200未提交
SELECT * FROM hero WHERE number = 1; # 得到的列name的值为'刘备'

```

- 随后提交事务一（id为100）并通过事务二（id为200）更新数据

```sql
# Transaction 100
BEGIN;
UPDATE hero SET name = '关羽' WHERE number = 1;
UPDATE hero SET name = '张飞' WHERE number = 1;
COMMIT;

# Transaction 200
BEGIN;
# 更新了一些别的表的记录
...
UPDATE hero SET name = '赵云' WHERE number = 1;
UPDATE hero SET name = '诸葛亮' WHERE number = 1;

```

- 版本链情况

> 
> 
- 使用REPEATABLE READ 隔离级别的事务中继续查找number 为 1 的记录

> 这个 SELECT2 的执行过程如下：
> 
> - 因为当前事务的隔离级别为 `REPEATABLE READ` ，而之前在执行 `SELECT1` 时已经生成过 `ReadView` 了，**所以此时直接复用之前的 `ReadView`** ，之前的 `ReadView 的 m_ids 列表的内容就是 [100, 200] ， min_trx_id 为100 ， max_trx_id 为 201 ， creator_trx_id 为 0` 。
> - 然后从版本链中挑选可见的记录，从图中可以看出，最新版本的列 name 的内容是 '诸葛亮' ，该版本的`trx_id 值为 200` ，在`m_ids`列表内，所以不符合可见性要求，根据 `roll_pointer` 跳到下一个版本。
> - 下一个版本的列 `name` 的内容是 '赵云' ，该版本的 `trx_id` 值为 200 ，也在 `m_ids` 列表内，所以也不符合要求，继续跳到下一个版本。
> - 下一个版本的列 `name` 的内容是 '张飞' ，该版本的`trx_id`值为 100 ，而 `m_ids` 列表中是包含值为 100 的事务id 的，所以该版本也不符合要求，同理下一个列 name 的内容是 '关羽' 的版本也不符合要求。继续跳到下一个版本。
> - 下一个版本的列`name`的内容是 '刘备' ，该版本的 `trx_id` 值为 80 ，小于 `ReadView` 中的 `min_trx_id` 值100 ，所以这个版本是符合要求的，最后返回给用户的版本就是这条列 c 为 '刘备' 的记录。

```sql
# 使用REPEATABLE READ隔离级别的事务
BEGIN;
# SELECT1：Transaction 100、200均未提交
SELECT * FROM hero WHERE number = 1; # 得到的列name的值为'刘备'
# SELECT2：Transaction 100提交，Transaction 200未提交
SELECT * FROM hero WHERE number = 1; # 得到的列name的值仍为'刘备'

```

- 总结

> 也就是说两次 SELECT 查询得到的结果是重复的，记录的列 c 值都是 '刘备' ，这就是 可重复读 的含义。如果我们之后再把 事务id 为200的记录提交了，然后再到刚才使用REPEATABLE READ隔离级别的事务中继续查找这个 number 为 1 的记录，得到的结果还是 '刘备' ，具体执行过程大家可以自己分析一下。
> 

### 3.3 MVCC小结

- 总结

> 从上边的描述中我们可以看出来，所谓的 MVCC （Multi-Version Concurrency Control ，多版本并发控制）指的就是在使用 READ COMMITTD 、 REPEATABLE READ 这两种隔离级别的事务在执行普通的 SEELCT 操作时访问记录的版本链的过程，这样子可以使不同事务的读-写 、 写-读操作并发执行，从而提升系统性能。 READ COMMITTD 、REPEATABLE READ 这两个隔离级别的一个很大不同就是：生成ReadView的时机不同，READ COMMITTD在每一次进行普通SELECT操作前都会生成一个ReadView，而REPEATABLE READ只在第一次进行普通SELECT操作前生成一个ReadView，之后的查询操作都重复使用这个ReadView就好了。
> 
- 小贴士

> 我们之前说执行DELETE语句或者更新主键的UPDATE语句并不会立即把对应的记录完全从页面中删除，而是执行一个所谓的delete mark操作，相当于只是对记录打上了一个删除标志位，这主要就是为MVCC服务的，大家可以对比上边举的例子自己试想一下怎么使用。
另外，所谓的MVCC只是在我们进行普通的SEELCT查询时才生效，截止到目前我们所见的所有SELECT语句都算是普通的查询，至于啥是个不普通的查询，我们稍后再说哈
> 

## 4.关于purge

- 大家有没有发现两件事儿：

> 我们说 insert undo 在事务提交之后就可以被释放掉了，而 update undo 由于还需要支持 MVCC ，不能立即删除掉。为了支持 MVCC ，对于 delete mark 操作来说，仅仅是在记录上打一个删除标记，并没有真正将它删除掉。
随着系统的运行，在确定系统中包含最早产生的那个 ReadView 的事务不会再访问某些 update undo日志 以及被打了删除标记的记录后，有一个后台运行的 purge线程 会把它们真正的删除掉
>