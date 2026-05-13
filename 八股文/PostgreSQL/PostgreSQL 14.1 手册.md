# PostgreSQL 14.1 手册

## 安装

### **1、使用docker安装**

```java
# 下载镜像
docker pull postgres
# 创建容器
docker run --name some-postgres -e POSTGRES_PASSWORD='admin' -e POSTGRES_USER='admin' -e POSTGRES_DB=mydb -p 5432:5432 -d postgres
```

### **2、命令行创建数据库**

### [**常用命令**](https://blog.csdn.net/YJ000312/article/details/132231377)

出现的问题：当进入该容器后，使用一些pgsql的命令会报如下错误：

1. 第一种是因为没有使用-U来指定登陆用户，缺省采用系统目录，而上面我们创建的用户为admin，所以最后报错用户不存在
2. 第二种错误原因是因为没有指定登陆的数据库，当使用-U时默认就是当前docker帮你配置好的用户，所以会识别admin是一个数据库，而我们上面创建的是mydb数据库，所以报错

```java
psql mydb
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  role "postgres" does not exist
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  role "root" does not exist
# psql -U admin -W
Password:
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  database "admin" does not exist
```

正确用法：

![image.png](PostgreSQL 14 1 手册/image.png)

注意：

- mydb=#：代表超级用户

### **3、窗口函数**

### **用法：非窗口函数的聚合函数() over (partition by 分组列)：over括号中的东西可以省略；窗口函数在非窗口聚集函数之后执行。这意味着可以在窗口函数的参数中包括一个聚集函数，但反过来不行。**

这个相较于group by可以观察被分组的所有行信息，观察之前之后的变化

```java
select t.activity_name ,t.bill_id ,t.payment_amount,avg(t.payment_amount) over (partition by activity_name) avg  from t_acc_payment_bill t where t.is_deleted =0;

```

![image.png](PostgreSQL 14 1 手册/image 1.png)

```java
select t.activity_name, t.bill_id, t.payment_amount,row_number() over (partition by activity_name) rn
from t_acc_payment_bill t
where t.is_deleted = 0;
```

![image.png](PostgreSQL 14 1 手册/image 2.png)

空也算

![image.png](PostgreSQL 14 1 手册/image 3.png)

### **窗口帧：**

对于每一行，在它的分区中（通过over中的语句进行划分）的行集被称为它的窗口帧。第一个sql函数中没有指定任何，那么窗口帧就是整个结果集，而第二个语句则是以order by为基础，相同及以前为一个窗口帧

```java
SELECT payment_amount, sum(payment_amount) OVER () sum FROM t_acc_payment_bill limit 5;
 
SELECT payment_amount, sum(payment_amount) OVER (order by payment_amount desc) sum FROM t_acc_payment_bill limit 5;
```

![image.png](PostgreSQL 14 1 手册/image 4.png)

![image.png](PostgreSQL 14 1 手册/image 5.png)

### **窗口函数提取——》window**

```java
select sum(payment_amount) over w sum, avg(payment_amount) over w avg
from t_acc_payment_bill
window w as (partition by activity_name order by payment_amount desc);
```

### **4、继承**

```java
CREATE TABLE cities (
 name text,
 population real,
 elevation int -- (in ft)
);
 
CREATE TABLE capitals (
 state char(2) UNIQUE NOT NULL
) INHERITS (cities);
 
SELECT name, elevation
 FROM ONLY cities
 WHERE elevation > 500;
```