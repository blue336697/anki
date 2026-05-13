# 关于数据库(MySql、TiDb、Calcite、Mybatis-plus)

## 预发关键字

### **EXISTS关键字**

`EXISTS` 是 SQL 中的一个关键字，用于检查一个子查询是否返回至少一行数据。

如果子查询返回至少一行数据，那么 `EXISTS` 子句就会返回 `true`，否则返回 `false`。

例如，以下查询会返回所有在 t_act_activity 表中有对应记录的 t_ecm_contract：

> 对于contract中每一个记录都会进行一次子查询，检查在activity中是否存在对应记录，如果存在则返回true，则这个contract就会被加入到结果集中
> 

```java
UPDATE t_ecm_contract
SET oa_status = '新的状态值'
WHERE execute_status IS NULL
AND oa_status IN (1, 11, 12, 13)
AND EXISTS (
    SELECT 1 FROM t_act_activity
    WHERE FIND_IN_SET(t_ecm_contract.id, relation_contract_id_list)
);
```

---

### **Varchar(xx)**

自mysql4.0版本以后xx代表的就是字符数了，无论是什么中文、英文、俄文等等

### **Text、MediumText、LongText**

这三者的区别是存储的大小限制：

- text：64KB
- MediumText：16MB
- LongText：4GB

### **Both关键字**

在MySQL中，`BOTH`关键字通常与`TRIM()`函数一起使用，用于从字符串的两端（即开始和结束）去除指定的字符。

`TRIM()`函数的语法如下：

```java
TRIM([BOTH | LEADING | TRAILING] [remstr] FROM str)
```

---

其中：

- `BOTH`：从字符串的两端去除字符。这是默认选项，如果不指定`BOTH`、`LEADING`或`TRAILING`，则默认为`BOTH`。
- `LEADING`：只从字符串的开始去除字符。
- `TRAILING`：只从字符串的结束去除字符。
- `remstr`：要去除的字符。如果不指定，那么默认为去除空格。
- `str`：原始字符串。

例如，以下查询将从字符串`' hello '`的两端去除空格：

```java
SELECT TRIM('  hello  ');
```

---

这将返回`'hello'`。

以下查询将从字符串`'!!!hello!!!'`的两端去除`'!'`：

```java
SELECT TRIM(BOTH '!' FROM '!!!hello!!!');
```

---

这将返回`'hello'`。

### **Replace函数**

MySQL的`REPLACE()`函数用于在字符串中替换所有出现的子串。它接受三个参数：

1. 原始字符串
2. 要被替换的子串
3. 替换子串

以下是一个使用`REPLACE()`函数的例子：

```java
SELECT REPLACE('Hello World', 'World', 'MySQL');
```

---

这个查询会返回字符串`'Hello MySQL'`，因为它将`'Hello World'`中的`'World'`替换为`'MySQL'`。

你也可以在`UPDATE`语句中使用`REPLACE()`函数来更新表中的数据。例如：

```java

UPDATE my_table
SET my_column = REPLACE(my_column, 'old_value', 'new_value')
WHERE some_condition;
```

---

这个查询会将`my_table`表中满足`some_condition`的所有行的`my_column`列中的`'old_value'`替换为`'new_value'`。

### **Concat函数**

如果你想将一个字段设置为其他几个字段的字符串连接，你可以使用`CONCAT`函数。例如：

```java

UPDATE your_table
SET column1 = CONCAT(column2, column3)
WHERE some_condition;
```

---

在这个例子中，`column1`被设置为`column2`和`column3`的字符串连接。

请注意，你需要将`your_table`、`column1`、`column2`、`column3`和`some_condition`替换为你的实际表名、列名和条件。并且如果列的某个值为null则组合后的值也为null

### **substring_index(string,sep,num)函数**

参数说明

- string：用于截取目标字符串的字符串。可为字段，表达式等。
- sep：分隔符，string存在且用于分割的字符，比如“，”、“.”等。
- num：序号，为非0整数。若为整数则表示从左到右数，若为负数则从右到左数。比如“[www.mysql.com](http://www.mysql.com/)”截取字符‘www’，分割符为“.”，从左到右序号为1，即substring_index("[www.mysql.com](http://www.mysql.com/)",'.',1)；若从右开始获取“com”则为序号为-1即substring_index("[www.mysql.com](http://www.mysql.com/)",'.',-1)

### **SET FOREIGN_KEY_CHECKS = 0/1**

这个字段的设置就是将表的外键约束关闭或者开启的设置，在开启时无法更新或删除数据。

```java
SET FOREIGN_KEY_CHECKS = 0;
  
DELETE FROM TABLE_NAME_;    //先关闭，然后DML，在开启
  
SET FOREIGN_KEY_CHECKS = 1;
```

---

### **TimeStamp日期类型**

timeStamp时间戳类型支持的最早时间经验证是1970-01-01 08:00:00

![image.png](关于数据库(MySql、TiDb、Calcite、Mybatis-plus)/image.png)

### **唯一索引**

在加入唯一索引时，一定要考虑列的组成，尤其是如果表存在逻辑删时，逻辑的字段不在唯一索引，这是一定要注意数据的插入

## 各种知识点

### **Online DDL**

Online DDL（在线数据定义语言）是一种数据库操作技术，允许在不锁定表或最小化锁定的情况下对数据库表进行结构性更改（如添加列、修改列类型、添加索引等）。这对于高可用性和高并发的数据库系统尤为重要，因为它可以在不影响数据库正常读写操作的情况下进行表结构的修改。

### **Online DDL 的主要特点和优势**

1. **最小化锁定**：
    - Online DDL 操作通常只会在短时间内锁定表，避免长时间的表锁定，从而减少对数据库正常操作的影响。
2. **高可用性**：
    - 由于表在大部分时间内是可读写的，在线 DDL 操作可以在不影响数据库服务可用性的情况下进行。
3. **并发支持**：
    - Online DDL 操作支持高并发环境下的表结构修改，适用于需要处理大量并发请求的系统。
4. **数据一致性**：
    - 在线 DDL 操作通常会确保数据的一致性，避免在表结构修改过程中出现数据不一致的情况。

### **Online DDL 解决的问题**

1. **避免长时间锁表**：
    - 传统的 DDL 操作可能会长时间锁定表，导致应用程序无法访问该表。在线 DDL 通过最小化锁定时间，避免了这个问题。
2. **减少停机时间**：
    - 在线 DDL 操作可以在数据库正常运行时进行，减少了因表结构修改而导致的停机时间。
3. **提高操作效率**：
    - 在线 DDL 操作通常更高效，可以在不影响数据库性能的情况下完成表结构修改。
4. **支持大规模数据表**：
    - 在线 DDL 操作可以处理大规模数据表的结构修改，适用于需要处理大量数据的系统。

### **示例**

以下是一个使用 MySQL Online DDL 的示例，展示了如何在不锁定表的情况下添加列：

```java
ALTER TABLE zlop_system.t_ecm_contract ADD COLUMN business_line_id INT DEFAULT 0 NULL COMMENT '所属业务线', ALGORITHM=INPLACE, LOCK=NONE;
```

在这个示例中，`ALGORITHM=INPLACE` 和 `LOCK=NONE` 指定了使用在线 DDL 操作，确保在不锁定表的情况下添加列。

### **总结**

Online DDL 是一种重要的数据库操作技术，允许在不影响数据库正常操作的情况下进行表结构修改。它通过最小化锁定时间、减少停机时间和提高操作效率，解决了传统 DDL 操作中的许多问题，特别适用于高可用性和高并发的数据库系统。

### **block_encryption_mode参数、TO_BASE64函数以及AES_ENCRYPT函数在SQL中的加密用法**

数据库参数

- block_encryption_mode：设置块加密模式。 SET block_encryption_mode = 'AES-192-ECB';作用：指定加密算法和模式，这里使用的是 AES-192 算法和 ECB 模式。
- @AES_KEY：设置AES加密的密钥。 SET @AES_KEY = 'xxx';作用：定义一个变量 @AES_KEY，存储用于AES加密的密钥。

函数

- AES_ENCRYPT：使用AES算法加密数据。 AES_ENCRYPT('data', @AES_KEY)。作用：使用指定的密钥 @AES_KEY 对数据进行AES加密。
- TO_BASE64：将数据编码为Base64格式。TO_BASE64(AES_ENCRYPT('data', @AES_KEY))。作用：将加密后的数据转换为Base64编码格式，便于存储和传输

### 关于数据库脚本版本的管理工具

1、byteBase

https://www.modb.pro/db/621194

2、flyway

### TP、AP

**TP（Transaction Processing，事务处理）**

- **全称**：Transaction Processing
- **中文**：事务处理
- **特点**：
- 主要处理**大量的短小、频繁的增删改查操作**（如插入、更新、删除、查询）。
- 关注**数据一致性、并发控制、响应速度**。
- 典型场景：银行转账、电商下单、用户注册、订单支付等。
- 事务性强，要求ACID（原子性、一致性、隔离性、持久性）保障。
- **常见数据库**：MySQL、Oracle、OceanBase（TP场景）、SQL Server等。

---

**AP（Analytical Processing，分析处理）**

- **全称**：Analytical Processing
- **中文**：分析处理
- **特点**：
- 主要处理**大批量数据的复杂分析、统计、报表、挖掘等操作**。
- 关注**查询性能、并发分析能力、数据吞吐量**。
- 典型场景：数据仓库、BI报表、离线分析、数据挖掘、风控模型训练等。
- 通常是读多写少，支持复杂的多表关联、聚合、分组等SQL操作。
- **常见数据库**：ClickHouse、Greenplum、Hive、OceanBase（AP场景）、Snowflake等。

---

**总结对比**

| 类型 | 全称 | 主要用途 | 典型场景 | 关注点 |
| --- | --- | --- | --- | --- |
| TP | Transaction Processing | 事务型业务 | 订单、支付、转账 | 一致性、响应速度 |
| AP | Analytical Processing | 分析型业务 | 报表、分析、挖掘 | 吞吐量、分析性能 |

### 字符集不一致导致关联出错

**会出现的问题（以 MySQL 为例）**

- **报错**：最典型是
    - ERROR 1267 (HY000): Illegal mix of collations ... for operation '='
    - Character set ... is not a compiled character set / ... incompatible with collation ...
- **性能下降**：为了“找公共字符集/排序规则”，数据库会对一侧做隐式转换，导致
    - 连接条件不可走索引 → 全表/大范围扫描、临时表、filesort。
- **匹配结果异常**：
    - 不同排序规则（如 _ci 忽略大小写、重音）导致“明明不同却被判相等/或相反”。
    - 字符集从宽到窄（如 utf8mb4 → latin1）可能丢失信息或变成 ?，出现误匹配或漏匹配。
- **排序/分组不一致**：ORDER BY/GROUP BY 在不同排序规则下结果顺序、去重口径不同。

**同理如果连接的两张表字符集的排序顺序不一样也会报错！！**

[**关于Mybatis-Plus的查缺补漏**](%E5%85%B3%E4%BA%8E%E6%95%B0%E6%8D%AE%E5%BA%93(MySql%E3%80%81TiDb%E3%80%81Calcite%E3%80%81Mybatis-plus)/%E5%85%B3%E4%BA%8EMybatis-Plus%E7%9A%84%E6%9F%A5%E7%BC%BA%E8%A1%A5%E6%BC%8F%2020e444514a318018ab82c5bf99541bbb.md)

[**Apache Calcite**](%E5%85%B3%E4%BA%8E%E6%95%B0%E6%8D%AE%E5%BA%93(MySql%E3%80%81TiDb%E3%80%81Calcite%E3%80%81Mybatis-plus)/Apache%20Calcite%2029a444514a3180d3bab8e955f1ddbe30.md)