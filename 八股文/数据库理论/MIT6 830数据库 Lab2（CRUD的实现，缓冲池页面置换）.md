# MIT6.830数据库 | Lab2（CRUD的实现，缓冲池页面置换）

type: Post
status: Published
date: 2022/09/01
summary: CRUD的实现，缓冲池页面置换
tags: 实践
category: 数据库

# Lab2

## 结构总概

- SimpleDB所包括的结构

> • 表示字段、元组和元组模式的类；
• 将谓词和条件应用于元组的类；
• 一种或多种访问方法（例如，堆文件），将关系存储在磁盘上，并提供一种遍历这些关系的元组的方法；
• 处理元组的运算符类（例如，选择、连接、插入、删除等）的集合；
• 一个缓冲池，在内存中缓存活动的元组和页面，并处理并发控制和事务；
• 并且，存储有关可用表及其模式的信息的目录。
> 
- 图示

> • Tuple和TupleDesc是数据库表的最基本元素了。Tuple就是一个若干个Field的数组，TupleDesc则是一个表的meta-data，包括每列的field name和type。
• HeapPage和HeapFile都分别是Page和DbFile interface的实现，毕竟HeapPage和HeapFile组织还是太简单了，后面lab会用B+树来替代之。
• BufferPool是用来做缓存的，getPage会优先从这里拿，如果没有，才会调用File的readPage去从文件中读取对应page，disk中读入的page会缓存在其中。
• SeqScan用来遍历一个table的所有tuple，包装了HeapFile的iterator。
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab2%EF%BC%88CRUD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%8C%E7%BC%93%E5%86%B2%E6%B1%A0%E9%A1%B5%E9%9D%A2%E7%BD%AE%E6%8D%A2%EF%BC%89/image.png)

## 1.Lab2的任务总概

- 概述

> 总体目标是实现对Lab剩下的操作函数以及置换页面算法的实现；大致有以下五个任务：
> 
> 1. 实现过滤和连接，即Filter和Join操作符。
> 2. 实现聚合操作，即Aggregate操作符。对Integer类型进行聚合时需要能够实现`MAX 、MIN 、COUNT、 SUM 、 AVG` ，对String类型进行聚合操作时，只需实现`COUNT` 。
> 3. 实现修改表的方法，从单个页面和文件的级别完成添加元组和删除元组的操作。
> 4. 实现Insert和Delete操作符。基于上面实现的方法，实现Insert 和 Delete操作符。
> 5. 实现BufferPool中的页面置换算法。

## 2.实现过滤和连接

- 过滤与连接

> • Filter：该操作符只返回满足谓词的元组，该元组被指定为其构造函数的一部分。因此，它过滤掉与谓词不匹配的任何元组。
• Join：该操作符根据作为其构造函数的一部分传入的`JoinPredicate`来连接它的两个子元组。我们只需要一个简单的嵌套循环连接
> 
- 谓词与谓词下推

> [这里有很详细的解释](https://zhuanlan.zhihu.com/p/554174896)
> 

### 2.1 实现基础Predicate（谓词）

- 概述

> 该类是Filter类的辅助类，用于筛选满足条件的tuple。将tuple中的字段与指定的字段进行比较，实现对单个tuple的过滤操作，比较逻辑有`==、 >=、 <=、 >、 <、 !=、 LIKE`(主要针对字符串)
> 
- 代码

```java
/**
 * 谓词将元组与指定的字段值进行比较。
 */
public class Predicate implements Serializable {

    private static final long serialVersionUID = 1L;

    /** Field.compare 中用于返回码的常量 */
    public enum Op implements Serializable {
        EQUALS, GREATER_THAN, LESS_THAN, LESS_THAN_OR_EQ, GREATER_THAN_OR_EQ, LIKE, NOT_EQUALS;

        /**
         * 通过整数值访问操作的接口，以方便命令行。
         *
         * @param i 一个有效的整数运算索引
         */
        public static Op getOp(int i) {
            return values()[i];
        }

        public String toString() {
            if (this == EQUALS)
                return "=";
            if (this == GREATER_THAN)
                return ">";
            if (this == LESS_THAN)
                return "<";
            if (this == LESS_THAN_OR_EQ)
                return "<=";
            if (this == GREATER_THAN_OR_EQ)
                return ">=";
            if (this == LIKE)
                return "LIKE";
            if (this == NOT_EQUALS)
                return "<>";
            throw new IllegalStateException("无法到达这里");
        }

    }

    private int fieldNo;
    private Op op;
    private Field opField;
    /**
     * 构造器
     *
     * @param field 要比较的传入元组的字段序号
     * @param op    用于比较的操作
     * @param operand   在元组中传递的要比较的字段
     */
    public Predicate(int field, Op op, Field operand) {
        this.fieldNo = field;
        this.op = op;
        this.opField = operand;
    }

    /**
     * @return 字段序号
     */
    public int getField() {
        return fieldNo;
    }

    /**
     * @return 返回比较逻辑
     */
    public Op getOp() {
        return op;
    }

    /**
     * @return 操作数
     */
    public Field getOperand() {
        return opField;
    }

    /**
     * 使用构造函数中特定的运算符将构造函数中指定的 t 的字段编号与构造函数中指定的操作数字段进行比较。
     * 可以通过Field的比较方法进行比较。
     *
     * @param t 要比较的元组
     * @return 如果比较为真，则为真，否则为假
     */
    public boolean filter(Tuple t) {
        if(t == null)
            return false;
        //得到元组的字段值
        Field field = t.getField(fieldNo);
        return field.compare(op, opField);
    }

    /**
     * 返回一些有用的东西，比如“f = field_id op = op_string operand =operand_string”
     */
    public String toString() {
        return "需要比较的字段序号为："+fieldNo+",比较逻辑是："+op+",比较字段为："+opField;
    }
}
```

### 2.2 实现JoinPredicate

- 概述

> 实现连接的条件，和Predicate类似 ，是JoinPredicate的辅助类，对两个tuple中的 某一字段进行比较。
> 
- 代码

```java
/**
 * 连接谓词使用谓词比较两个元组的字段。 Join 运算符最有可能使用 Join Predicate
 */
public class JoinPredicate implements Serializable {

    private static final long serialVersionUID = 1L;

    private Predicate.Op op;
    private int fieldNo1;
    private int fieldNo2;
    /**
     * 构造函数——在两个元组的两个字段上创建一个新谓词。
     *
     * @param field1    谓词中第一个元组的字段索引
     * @param field2    谓词中第二个元组的字段索引
     * @param op    要应用的操作（在 Predicate.Op 中定义）；
     *              Predicate.Op.GREATER_THAN、
     *              Predicate.Op.LESS_THAN、
     *              Predicate.Op.EQUAL、
     *              Predicate.Op.GREATER_THAN_OR_EQ 或
     *              Predicate.Op.LESS_THAN_OR_EQ
     * @see Predicate
     */
    public JoinPredicate(int field1, Predicate.Op op, int field2) {
        fieldNo1 = field1;
        this.op = op;
        fieldNo2 = field2;
    }

    /**
     * 将谓词应用于两个指定的元组。可以通过Field的比较方法进行比较。
     *
     * @return 如果元组满足谓词，则为 true。
     */
    public boolean filter(Tuple t1, Tuple t2) {
        if(t1 == null || t2 == null)
            return false;
        Field field01 = t1.getField(fieldNo1);
        Field field02 = t2.getField(fieldNo2);
        return field01.compare(op, field02);
    }

    public int getField1() {
        return fieldNo1;
    }

    public int getField2() {
        return fieldNo2;
    }

    public Predicate.Op getOperator(){
        return op;
    }
}
```

### 2.3 实现Filter

- 概述

> Filter实现了Operator接口。根据Predicate的判读结果，得到满足条件的tuples。实现了`where age> 23`这样的操作。即你可理解为Predicate判断后的实际过滤类
> 
> 
> ![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab2%EF%BC%88CRUD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%8C%E7%BC%93%E5%86%B2%E6%B1%A0%E9%A1%B5%E9%9D%A2%E7%BD%AE%E6%8D%A2%EF%BC%89/image%201.png)
> 
- 代码

```java
/**
 * Filter 是一个实现关系选择的运算符。与join和seqscan同级
 */
public class Filter extends Operator {

    private static final long serialVersionUID = 1L;

    private Predicate p;
    //待过滤的tuples的迭代器
    private OpIterator child;
    /**
     * 构造函数接受要应用的谓词和要读取要从中过滤的元组的子运算符。
     *
     * @param p 过滤元组的谓词
     * @param child 还未过滤元组的迭代器
     */
    public Filter(Predicate p, OpIterator child) {
        this.p = p;
        this.child = child;
    }

    public Predicate getPredicate() {
        return p;
    }

    public TupleDesc getTupleDesc() {
        return child.getTupleDesc();
    }

    //Filter是项目中的Operator类的子类， 需要执行super.open()
    public void open() throws DbException, NoSuchElementException,
            TransactionAbortedException {
        child.open();
        super.open();
    }

    public void close() {
        super.close();
        child.close();
    }

    public void rewind() throws DbException, TransactionAbortedException {
        child.rewind();
    }

    /**
     * AbstractDbIterator.readNext 实现。迭代来自子运算符的元组，
     * 将谓词应用于它们并返回那些通过谓词的元组（即 Predicate.filter() 返回 true。）
     * 返回过滤后的元组
     *
     * @return 通过过滤器的下一个元组，如果没有更多元组，则为 null
     * @see Predicate#filter
     */
    protected Tuple fetchNext() throws NoSuchElementException,
            TransactionAbortedException, DbException {
        while (child.hasNext()){
            Tuple next = child.next();
            if (p.filter(next)) {   //过滤一下，看看是不是我们需要比较的元组
                return next;
            }
        }
        return null;
    }

    @Override
    public OpIterator[] getChildren() {
        return new OpIterator[]{child};
    }

    @Override
    public void setChildren(OpIterator[] children) {
        child = children[0];
    }

}
```

### 2.4 实现Join

- 前言——驱动表与被驱动表

> 我们知道无论是内连接还是外连接都是有驱动表和被驱动表之说，整个的查询过程就是先去驱动表筛选区符合条件的记录然后再去让被驱动表根据这些记录进行回表，对比自己表中的记录；即我们只需要访问一次驱动表，但是要访问好几次被驱动表，可以总结我下面的步骤
> 
> 1. 步骤1：选取驱动表，使用与驱动表相关的过滤条件，选取代价最低的单表访问方法来执行对驱动表的单表查询。
> 2. 步骤2：对上一步骤中查询驱动表得到的结果集中每一条记录，都分别到被驱动表中查找匹配的记录。
- 概述

> 这里不是实现什么内外连接，而是实现连接的具体算法，在MySQL中大致有三种算法（当然还有很多算法，读者可自行了解）：
> 
> 1. 嵌套循环连接（Nested-Loop Join）：就是我们上述的查询过程，**这种驱动表只访问一次，但被驱动表却可能被多次访问，访问次数取决于对驱动表执行单表查询后的结果集中的记录条数的连接执行方式称之为 嵌套循环连接**
> 2. 基于块的嵌套循环连接（Block Nested-Loop Join）：大致的思路就是减少被驱动表的访问次数，在前者的连接中每次被驱动表对比数据都是一条一条在内存中对比完就清除的周而复始；所以我们可不可以在把被驱动表的记录加载到内存的时候，一次性和多条驱动表中的记录做匹配，这样就可以大大减少重复从磁盘上加载被驱动表的代价了。**即Join buffer诞生解决了：执行连接查询前申请的一块固定大小的内存，先把若干条驱动表结果集中的记录装在这个 join buffer 中，然后开始扫描被驱动表，每一条被驱动表的记录一次性和 join buffer 中的多条驱动表记录做匹配，因为匹配的过程都是在内存中完成的，所以这样可以显著减少被驱动表的 I/O 代价**
> 3. 第三种就是在第一种的基础上加入了索引以提高检索效率
- 本次实验中我们只实现嵌套循环连接

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab2%EF%BC%88CRUD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%8C%E7%BC%93%E5%86%B2%E6%B1%A0%E9%A1%B5%E9%9D%A2%E7%BD%AE%E6%8D%A2%EF%BC%89/image%202.png)

- 代码

```java
/**
 * Join 操作符实现了关系连接操作。
 */
public class Join extends Operator {

    private static final long serialVersionUID = 1L;

    private JoinPredicate jP;
    //下面这两个你就可以累计理解为连接语句中join左边的部分和右边的部分
    //右边的部分会指定过滤条件
    //例如：下面的可以很清晰的看到左右两遍的界限
    // SELECT s1.number, s1.name, s2.subject, s2.score FROM student AS s1
    // LEFT JOIN score AS s2 ON s1.number = s2.number;
    private OpIterator leftBody;
    private OpIterator rightBody;
    private Tuple leftTuple;
    /**
     * 构造函数。接受两个孩子加入和加入他们的谓词
     *
     * @param p 用于连接孩子的谓词
     * @param child1 要加入的左（外）关系的迭代器
     * @param child2 要加入的右（内部）关系的迭代器
     */
    public Join(JoinPredicate p, OpIterator child1, OpIterator child2) {
        this.jP = p;
        this.leftBody = child1;
        this.rightBody = child2;
        leftTuple = null;
    }

    public JoinPredicate getJoinPredicate() {
        return jP;
    }

    /**
     * @return  join field1 的字段名。应该用别名或表名来量化。即左边的表
     * */
    public String getJoinField1Name() {
        //得到字段的序号
        return leftBody.getTupleDesc().getFieldName(jP.getField1());
    }

    /**
     * @return join field2 的字段名。应该用别名或表名来量化。
     * */
    public String getJoinField2Name() {
        return rightBody.getTupleDesc().getFieldName(jP.getField2());
    }

    /**
     * @see TupleDesc#merge(TupleDesc, TupleDesc) 用于可能的实现逻辑。
     * 得到结果表的元组元信息
     */
    public TupleDesc getTupleDesc() {
        TupleDesc tupleDesc = leftBody.getTupleDesc();
        TupleDesc tupleDesc1 = rightBody.getTupleDesc();
        return TupleDesc.merge(tupleDesc, tupleDesc1);
    }

    public void open() throws DbException, NoSuchElementException,
            TransactionAbortedException {
        leftBody.open();
        rightBody.open();
        super.open();
    }

    public void close() {
        super.close();
        rightBody.close();
        leftBody.close();
    }

    public void rewind() throws DbException, TransactionAbortedException {
        leftBody.rewind();
        rightBody.rewind();
    }

    /**
     * 返回连接生成的下一个元组，如果没有更多元组，则返回 null。
     * 从逻辑上讲，这是 r1 cross r2 中满足连接谓词的下一个元组。
     * 有很多可能的实现；最简单的是嵌套循环连接。
     * <p>
     * 请注意，从这个特定的 Join 实现返回的元组只是连接来自左右关系的元组的串联。
     * 因此，如果使用相等谓词，则结果中将有两个连接属性副本。
     * （如果需要，可以使用额外的投影运算符删除此类重复列。）
     * <p>
     * 例如，如果一个元组是 {1,2,3} 而另一个元组是 {1,5,6}，在第一列相等时连接，
     * 则返回 {1,2,3,1,5,6 }。
     *
     * @return 下一个匹配的元组。
     * @see JoinPredicate#filter
     */
    protected Tuple fetchNext() throws TransactionAbortedException, DbException {
        while (leftBody.hasNext() || leftTuple != null){
            if(leftBody.hasNext() && leftTuple == null)
                leftTuple = leftBody.next();
            Tuple rightTuple;
            while (rightBody.hasNext()){
                rightTuple = rightBody.next();
                //如果对比运算符之后的结果
                if(jP.filter(leftTuple, rightTuple)){
                    //获取元组字段的数量
                    int len1 = leftTuple.getTupleDesc().numFields();
                    int len2 = rightTuple.getTupleDesc().numFields();
                    //构造新的元组
                    Tuple newTuple = new Tuple(getTupleDesc());
                    //得到两个元组一共的字段数
                    for (int i = 0; i < len1; i++) {
                        //一个一个字段设置
                        newTuple.setField(i, leftTuple.getField(i));
                    }
                    for (int i = 0; i < len2; i++) {
                        //一个一个字段设置
                        newTuple.setField(i + len1, rightTuple.getField(i));
                    }
                    return newTuple;
                }
            }
            leftTuple = null;
            //被驱动表获取完
            rightBody.rewind();
        }
        return null;
    }

    @Override
    public OpIterator[] getChildren() {
        return new OpIterator[]{leftBody, rightBody};
    }

    @Override
    public void setChildren(OpIterator[] children) {
        leftBody = children[0];
        rightBody = children[1];
    }

}
```

## 3.实现聚合操作

- 概述

> 集合操作，即Aggregate操作符。对Integer类型进行聚合时需要能够实现`MAX 、MIN 、COUNT、 SUM 、 AVG` ，对String类型进行聚合操作时，只需实现`COUNT` 。
> 
- 步骤

> **大概的思路就是将每个元组的某一列合并起来，得到这个合并结果的迭代器，结果中的每个元组有分组字段、聚合字段，当 group by字段的值是`Aggregator.NO_GROUPING`时，结果中的元组是聚合字段没有分组字段**
> 

> 先读取一个元组进行聚合，得到一个只聚合了一个元组的结果，然后循环读取每一个元组得到新的聚合结果，循环往复
> 
- agg工具类

> 由于我们要实现int和string两种数据类型的聚合函数，那么就要分辨使用的是那种聚合函数，可以将其抽象封装出来一个类
> 

```java
/**
 * @author lhj
 * @create 2022/8/28 20:27
 * 聚合运算符的工具类，将每个运算符进行实现并封装
 */
public abstract class AggUtil {
    //存放聚合结果的
    HashMap<Field, Integer> aggResult;
    //Filed是用于分组的gbField，gbFieIndex ==  NO_GROUPING时为null  Integer是聚合结果
    /**
     *
     * @param gbField   传入的分组字段，可能为null，为null就代表没有分组要求，
     *                  所以结果中的元组也只有一个聚合字段
     * @param intField  传入的该字段的当前行的整数字段值
     * @param stringField  传入的该字段的当前行的字符字段值
     */
    public abstract void handle(Field gbField, IntField intField, StringField stringField);

    public AggUtil(){
        aggResult = new HashMap<>();
    }

    public HashMap<Field,Integer> getAggResult(){
        return aggResult;
    }
}

/**
 * @author lhj
 * @create 2022/8/28 22:11
 */
public class AvgHandler extends AggUtil{
    HashMap<Field, Integer> sum;
    HashMap<Field, Integer> count;

    public AvgHandler(){
        sum = new HashMap<>();
        count = new HashMap<>();
    }

    @Override
    public void handle(Field gbField, IntField intField, StringField stringField) {
        int value = intField.getValue();
        if(sum.containsKey(gbField) && count.containsKey(gbField)){
            sum.put(gbField, sum.get(gbField)+value);
            count.put(gbField, count.get(gbField)+1);
        } else {
            sum.put(gbField, value);
            count.put(gbField, +1);
        }
        int avg = sum.get(gbField) / count.get(gbField);
        aggResult.put(gbField, avg);
    }
}

/**
 * @author lhj
 * @create 2022/8/28 22:01
 */
public class CountHandler extends AggUtil{
    @Override
    public void handle(Field gbField, IntField intField, StringField stringField) {
        if(aggResult.containsKey(gbField)){
            aggResult.put(gbField, aggResult.get(gbField) + 1);
        }else
            aggResult.put(gbField, 1);
    }
}

/**
 * @author lhj
 * @create 2022/8/28 22:02
 */
public class MaxHandler extends AggUtil{
    @Override
    public void handle(Field gbField, IntField intField, StringField stringField) {
        Type type = gbField.getType();
        if(type.equals(INT_TYPE)){
            int value = intField.getValue();
            //记录当前字段的最大值
            if(aggResult.containsKey(gbField)){
                aggResult.put(gbField, Math.max(aggResult.get(gbField) , value));
            } else {
                aggResult.put(gbField, value);
            }
        }else{
            //后续就可以在这继续添加String类型的相关了
        }

    }
}

/**
 * @author lhj
 * @create 2022/8/28 22:09
 */
public class MinHandler extends AggUtil{
    @Override
    public void handle(Field gbField, IntField intField, StringField stringField) {
        int value = intField.getValue();
        //记录当前字段的最大值
        if(aggResult.containsKey(gbField)){
            aggResult.put(gbField, Math.min(aggResult.get(gbField) , value));
        } else {
            aggResult.put(gbField, value);
        }
    }
}

/**
 * @author lhj
 * @create 2022/8/28 22:10
 */
public class SumHandler extends AggUtil{

    @Override
    public void handle(Field gbField, IntField intField, StringField stringField) {
        int value = intField.getValue();
        if(aggResult.containsKey(gbField)){
            aggResult.put(gbField, aggResult.get(gbField)+value);
        } else {
            aggResult.put(gbField, value);
        }
    }
}
```

### 3.1 实现IntegerAggregator

- 概述

> 该类就是主要负责聚合字段时Int型的情况处理
> 
- 代码

```java
/**
 * 知道如何在一组 IntFields 上计算一些聚合。
 */
public class IntegerAggregator implements Aggregator {

    private static final long serialVersionUID = 1L;

    //分组字段的索引，即依据什么字段进行分组
    private int gbFieldIndex;
    //分组字段的类型
    private Type gbFieldType;
    //聚合函数中的字段索引
    private int aggFiledIndex;
    //运算符执行器，帮助我们得到结果
    private AggUtil aggHandler;
    //用来存储需要分组的字段
    private Field gbField;

    /**
     * 聚合构造函数
     *
     * @param gbfield 元组中 group-by 字段索引，如果没有分组，则为 NO_GROUPING
     * @param gbfieldtype 分组依据字段的类型（例如，Type.INT_TYPE），如果没有分组，则返回 null
     * @param afield 元组中聚合字段索引
     * @param what 聚合运算符
     */

    public IntegerAggregator(int gbfield, Type gbfieldtype, int afield, Op what) {
        this.gbFieldIndex = gbfield;
        this.gbFieldType = gbfieldtype;
        this.aggFiledIndex = afield;
        switch (what){
            case AVG :
                aggHandler = new AvgHandler();
                break;
            case MAX :
                aggHandler = new MaxHandler();
                break;
            case MIN :
                aggHandler = new MinHandler();
                break;
            case SUM :
                aggHandler = new SumHandler();
                break;
            case COUNT :
                aggHandler = new CountHandler();
                break;
            default :
                throw new UnsupportedOperationException("该聚合函数不支持");
        }
    }

    /**
     * 将新元组合并到聚合中，按照构造函数中的指示进行分组
     * 聚合操作的执行过程是：先读取一个tuple进行聚合操作，得到一个只聚合了一个tuple的聚合结果，
     * 之后每读取一个tuple就将其加入到聚合结果中重新进行聚合
     *
     * 就是如果有分组要求就要将分组的字段传入，如果没有则传入的是null，只获取聚合的字段值就好
     *
     * @param tup 包含聚合字段和分组依据字段的元组
     */
    public void mergeTupleIntoGroup(Tuple tup) {
        //需要加入的新元组，依据这个分组

        //得到已经聚合的字段结果
        IntField aggField = (IntField) tup.getField(aggFiledIndex);
        if(gbFieldIndex == NO_GROUPING){
            gbField = null;
        }else
            gbField = tup.getField(gbFieldIndex);
        //依据这个分组并进行聚合操作
        aggHandler.handle(gbField, aggField, null);
    }

    /**
     * 在组聚合结果上创建 OpIterator。
     *
     * @return 一个 OpIterator，如果使用组，其元组是对 (groupVal, aggregateVal)，
     * 如果没有分组，则为单个 (aggregateVal)。 aggregateVal 由构造函数中指定的聚合类型确定。
     */
    public OpIterator iterator() {
        HashMap<Field, Integer> aggResult = aggHandler.getAggResult();

        Type[] fieldTypes;  //字段类型
        String[] fieldNames; //字段名称
        TupleDesc tupleDesc;    //当前元组的各种信息
        List<Tuple> tuples = new ArrayList<>();
        //如果没有分组要求，构造新的元组、元信息
        if(gbFieldIndex == NO_GROUPING){
            //获取类型和名称
            fieldTypes = new Type[]{Type.INT_TYPE};
            fieldNames = new String[]{"aggValue"};
            tupleDesc = new TupleDesc(fieldTypes, fieldNames);
            Tuple tuple = new Tuple(tupleDesc);
            //获取聚合元组
            IntField resultField = new IntField(aggResult.get(gbField));
            tuple.setField(0, resultField);
            //加入到迭代的元组集中
            tuples.add(tuple);
        }else{
            //如果有分组要求就会除了聚合字段还有元组字段
            fieldTypes = new Type[]{gbFieldType, Type.INT_TYPE};
            fieldNames = new String[]{"groupValue", "aggValue"};
            tupleDesc = new TupleDesc(fieldTypes, fieldNames);
            for(Field f : aggResult.keySet()){
                Tuple tuple = new Tuple(tupleDesc);
                if(gbFieldType == Type.INT_TYPE){
                    IntField intField = (IntField) f;
                    tuple.setField(0, intField);
                }else{
                    StringField stringField = (StringField) f;
                    tuple.setField(0,stringField);
                }
                IntField resField = new IntField(aggResult.get(f));
                tuple.setField(1, resField);
                tuples.add(tuple);
            }

        }
        return new TupleIterator(tupleDesc,tuples);
    }
}
```

### 3.2 实现StringAggregator

- 概述

> 该类就是负责聚合类是String字符串的时候
> 
- 代码

```java
/**
 * 知道如何在一组 StringFields 上计算一些聚合。
 */
public class StringAggregator implements Aggregator {

    private static final long serialVersionUID = 1L;

    //分组字段的索引，即依据什么字段进行分组
    private int gbFieldIndex;
    //分组字段的类型
    private Type gbFieldType;
    //聚合函数中的字段索引
    private int aggFiledIndex;
    //运算符执行器，帮助我们得到结果
    private AggUtil aggHandler;

    //分组字段
    private Field gbField;

    /**
     * 聚合构造函数
     *
     * @param gbfield 元组中 group-by 字段索引，如果没有分组，则为 NO_GROUPING
     * @param gbfieldtype 分组依据字段的类型（例如，Type.INT_TYPE），如果没有分组，则返回 null
     * @param afield 元组中聚合字段索引
     * @param what 聚合运算符
     */

    public StringAggregator(int gbfield, Type gbfieldtype, int afield, Op what) {
        this.gbFieldIndex = gbfield;
        this.gbFieldType = gbfieldtype;
        this.aggFiledIndex = afield;
        switch (what){
            case COUNT:
                aggHandler = new CountHandler();
                break;
            default:
                throw new UnsupportedOperationException("暂时只支持计数的聚合哦！");
        }
    }

    /**
     * 将新元组合并到聚合中，按照构造函数中的指示进行分组
     * @param tup 包含聚合字段和分组依据字段的元组
     */
    public void mergeTupleIntoGroup(Tuple tup) {
        StringField aggField = (StringField) tup.getField(aggFiledIndex);
        if(gbFieldIndex == NO_GROUPING){
            gbField = null;
        }else
            gbField = tup.getField(gbFieldIndex);
        aggHandler.handle(gbField,null, aggField);
    }

    /**
     * 在组聚合结果上创建 OpIterator。
     *
     * @return 一个 OpIterator，如果使用组，其元组是对 (groupVal, aggregateVal)，
     * 如果没有分组，则为单个 (aggregateVal)。 aggregateVal 由构造函数中指定的聚合类型确定
     */
    public OpIterator iterator() {
        HashMap<Field, Integer> aggResult = aggHandler.getAggResult();

        Type[] fieldTypes;  //字段类型
        String[] fieldNames; //字段名称
        TupleDesc tupleDesc;    //当前元组的各种信息
        List<Tuple> tuples = new ArrayList<>();
        //如果没有分组要求，构造新的元组、元信息
        if(gbFieldIndex == NO_GROUPING){
            //获取类型和名称
            fieldTypes = new Type[]{Type.STRING_TYPE};
            fieldNames = new String[]{"aggValue"};
            tupleDesc = new TupleDesc(fieldTypes, fieldNames);
            Tuple tuple = new Tuple(tupleDesc);
            //获取聚合元组
            IntField resultField = new IntField(aggResult.get(gbField));
            tuple.setField(0, resultField);
            //加入到迭代的元组集中
            tuples.add(tuple);
        }else{
            //如果有分组要求就会除了聚合字段还有元组字段
            //这里注意：对于结果集来说肯定是统计的次数，即是INT型不要瞎改
            fieldTypes = new Type[]{gbFieldType, Type.INT_TYPE};
            fieldNames = new String[]{"groupValue", "aggValue"};
            tupleDesc = new TupleDesc(fieldTypes, fieldNames);
            for(Field f : aggResult.keySet()){
                Tuple tuple = new Tuple(tupleDesc);
                if(gbFieldType == Type.INT_TYPE){
                    IntField intField = (IntField) f;
                    tuple.setField(0, intField);
                }else{
                    StringField stringField = (StringField) f;
                    tuple.setField(0,stringField);
                }
                IntField resField = new IntField(aggResult.get(f));
                tuple.setField(1, resField);
                tuples.add(tuple);
            }

        }
        return new TupleIterator(tupleDesc,tuples);
    }
}
```

### 3.3 实现Aggregate

- 概述

> 该类就是作为整型或字符型的迭代聚合操作类，本质上就是一个迭代器（迭代器通过各自的聚合类获得），去执行我们所说的聚合元组；就与之前的 Join 一样，都是 Operator 的具体实现。
> 
- 代码

```java
/**
 * 计算聚合的聚合运算符（例如 sum、avg、max、min）。请注意，我们仅支持单个列上的聚合，按单个列分组。
 */
public class Aggregate extends Operator {

    private static final long serialVersionUID = 1L;

    //需要聚合的tuples
    private OpIterator child;
    //待聚合字段的序号
    private int aggField;
    //待分组的字段序号
    private int gbField;
    //运算符
    private Aggregator.Op op;
    //进行聚合操作的类
    private Aggregator aggregator;
    //聚合结果的迭代器
    private OpIterator aggIterator;
    //聚合结果的元信息
    private TupleDesc aggTupleDesc;
    /**
     * Constructor.
     * <p>
     * 实现提示：根据字段的类型，您将需要构造一个 {@link IntegerAggregator}
     * 或 {@link StringAggregator} 来帮助您实现 readNext()。
     *
     * @param child  为我们提供元组的 Operator。
     * @param afield 我们正在计算聚合的列
     * @param gfield 我们对结果进行分组的列，如果没有分组，则为 -1
     * @param aop    要使用的聚合运算符
     */
    public Aggregate(OpIterator child, int afield, int gfield, Aggregator.Op aop) {
        this.child = child;
        this.aggField = afield;
        this.gbField = gfield;
        this.op = aop;
        Type gbFieldType = gfield == Aggregator.NO_GROUPING ? null : child.getTupleDesc().getFieldType(gfield);
        Type aggFieldType = child.getTupleDesc().getFieldType(afield);

        Type[] fieldTypes;
        String[] fieldNames;
        //获取聚合字段的名称
        String aggFieldName = String.format("%s(%s)", aop.toString(), child.getTupleDesc().getFieldName(afield));
        //没有要求分组
        if(gbFieldType == null){
            fieldTypes = new Type[]{aggFieldType};
            fieldNames = new String[]{aggFieldName};
        }else{  //要求分组结果集的字段就有两个
            fieldTypes = new Type[]{gbFieldType, aggFieldType};
            String gbFieldName = child.getTupleDesc().getFieldName(gfield);
            fieldNames = new String[]{gbFieldName, aggFieldName};
        }
        aggTupleDesc = new TupleDesc(fieldTypes, fieldNames);
    }

    /**
     * @return 如果此聚合伴随一个 groupby，则返回 <b>INPUT<b> 元组中的 groupby 字段索引。
     *              如果没有，返回
     * {@link Aggregator#NO_GROUPING}
     */
    public int groupField() {
        return gbField == Aggregator.NO_GROUPING ? -1 : gbField;
    }

    /**
     * @return 如果此聚合伴随着 group by，则返回 <b>OUTPUT<b> 元组中 groupby 字段的名称。
     *         如果不是，则返回null；
     */
    public String groupFieldName() {
        if(groupField() == -1)
            return null;
        return aggTupleDesc.getFieldName(gbField);
    }

    /**
     * @return 聚合字段
     */
    public int aggregateField() {
        return aggField;
    }

    /**
     * @return 返回 <b>OUTPUT<b> 元组中聚合字段的名称
     */
    public String aggregateFieldName() {
        return aggTupleDesc.getFieldName(aggField);
    }

    /**
     * @return 返回聚合运算符
     */
    public Aggregator.Op aggregateOp() {
        return op;
    }

    public static String nameOfAggregatorOp(Aggregator.Op aop) {
        return aop.toString();
    }

    /**
     * 此时就要根据你传入的分组来选择返回的Int还是String类型的迭代器规则
     * @throws NoSuchElementException
     * @throws DbException
     * @throws TransactionAbortedException
     */
    public void open() throws NoSuchElementException, DbException,
            TransactionAbortedException {
        super.open();
        child.open();
        //获取分组和聚合字段的类型
        Type gbFieldType = gbField == -1 ? null : child.getTupleDesc().getFieldType(gbField);
        Type aggFieldType = child.getTupleDesc().getFieldType(aggField);
        //根据不同的类型，赋值聚合所需的迭代器
        if(aggFieldType == Type.INT_TYPE)
            aggregator = new IntegerAggregator(gbField, gbFieldType, aggField, op);
        else
            aggregator = new StringAggregator(gbField, gbFieldType, aggField, op);
        //逐个合并每个元组
        while (child.hasNext())
            aggregator.mergeTupleIntoGroup(child.next());

        aggIterator = aggregator.iterator();
        aggIterator.open();
    }

    /**
     * 返回下一个元组。如果有分组依据字段，那么第一个字段是我们分组的字段，第二个字段是计算聚合的结果。
     * 如果没有按字段分组，则结果元组应包含一个表示聚合结果的字段。如果没有更多元组，则应返回 null。
     */
    protected Tuple fetchNext() throws TransactionAbortedException, DbException {
        if(aggIterator.hasNext())
            return aggIterator.next();
        else
            return null;
    }

    public void rewind() throws DbException, TransactionAbortedException {
        child.rewind();
        aggIterator.rewind();
    }

    /**
     * 返回此聚合的 TupleDesc。如果没有按字段分组，这将有一个字段 - 聚合列。
     * 如果有分组字段，则第一个字段将是分组字段，第二个字段将是聚合值列。
     * <p>
     * 聚合列的名称应该提供信息。例如： "aggName(aop) (child_td.getFieldName(afield))"
     * 其中aop和afield在构造函数中给出，child_td是子迭代器的TupleDesc
     */
    public TupleDesc getTupleDesc() {
        return aggTupleDesc;
    }

    public void close() {
        super.close();
        child.close();
        aggIterator.close();
    }

    @Override
    public OpIterator[] getChildren() {
        return new OpIterator[]{child};
    }

    @Override
    public void setChildren(OpIterator[] children) {
        child = children[0];
    }
}
```

## 4.实现修改表的方法

- 概述

> 我们只用实现两种修改表的方法：
> 
> 1. **Removing tuples:** 要删除一个元组，你需要实现 `deleteTuple`。元组包含 `RecordIDs`，这允许你找到它们所在的页面，所以这应该像定位元组所属的页面并适当修改页面的头一样简单。
> 2. **Adding tuples:** `HeapFile.java` 中的 `insertTuple` 方法负责向堆文件添加元组。要向 HeapFile 添加一个新的元组，你必须找到一个有空槽的页面。如果 HeapFile 中不存在这样的页面，则需要创建一个新页面，并将其追加到磁盘上的物理文件中。你将需要确保元组中的 RecordID 被正确更新。
- 分析增加元组过程

> 这个过程其实跟四个关键的地方有关分别是：
> 
> - HeapPage：代表页本身要去检查自己有没有空的slot
> - HeapFile：代表页面的集合，会操作一些对页面集合的检索之类的工作
> - Buffer Pool：代表页面的缓存区域，当HeapFile想要操作某个HeapPage就会先去池中寻找，找到返回没找到则去持久化的磁盘寻找
> - 磁盘：作为池中不存在Page的置换场所
- 整个添加记录的过程就如下图

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab2%EF%BC%88CRUD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%8C%E7%BC%93%E5%86%B2%E6%B1%A0%E9%A1%B5%E9%9D%A2%E7%BD%AE%E6%8D%A2%EF%BC%89/image%203.png)

### 4.1 实现HeapPage

- 代码

```java
/**
 * HeapPage 的每个实例都存储一页 HeapFiles 的数据，并实现 BufferPool 使用的 Page 接口。
 *
 * @see HeapFile
 * @see BufferPool
 *
 */
public class HeapPage implements Page {

    final HeapPageId pid;
    final TupleDesc td;
    final byte[] header;
    final Tuple[] tuples;
    final int numSlots;

    byte[] oldData;
    private final Byte oldDataLock= (byte) 0;

    // 将页面更改为脏页的事务 id
    private TransactionId dirtyId;
    //如果页面脏了
    private boolean dirty;

    /**
     * 从磁盘读取的一组字节数据创建一个 HeapPage。 HeapPage 的格式是一组标头字节，
     * 指示正在使用的页面的槽，一些元组槽。具体来说，元组的数量等于:
     *          向下取整((BufferPool.getPageSize()*8) / (tuple size * 8 + 1))
     * 其中元组大小是该数据库表中元组的大小，可以通过 {@link Catalog#getTupleDesc}确定。
     * 8 位标题字的数量等于：向上取整(no. tuple slots / 8)
     *
     *
     * <p>
     * @see Database#getCatalog
     * @see Catalog#getTupleDesc
     * @see BufferPool#getPageSize()
     */
    public HeapPage(HeapPageId id, byte[] data) throws IOException {
        this.pid = id;
        this.td = Database.getCatalog().getTupleDesc(id.getTableId());
        this.numSlots = getNumTuples();
        DataInputStream dis = new DataInputStream(new ByteArrayInputStream(data));

        // 分配和读取本页的页眉槽
        header = new byte[getHeaderSize()];
        for (int i=0; i<header.length; i++)
            header[i] = dis.readByte();

        tuples = new Tuple[numSlots];
        try{
            // 分配和读取本页的实际记录
            for (int i=0; i<tuples.length; i++)
                tuples[i] = readNextTuple(dis,i);
        }catch(NoSuchElementException e){
            e.printStackTrace();
        }
        dis.close();

        setBeforeImage();
    }

    /** 检索此页面上的元组数。
        @return 此页面上的元组数
    */
    private int getNumTuples() {
        //int的四则运算就是向下取整的
        return (BufferPool.getPageSize() * 8) / (td.getSize() * 8 + 1);
    }

    /**
     * 计算 HeapFile 中页面标题中的字节数，每个元组占用 tupleSize 个字节
     * @return HeapFile 中页面标题中的字节数，每个元组占用 tupleSize 个字节
     *
     * 注意这里切记要*1.0先转化为double不然后续会被int转为别的值
     */
    private int getHeaderSize() {
        return (int) Math.ceil(getNumTuples() * 1.0 / 8);
    }

    /** 返回此页面在修改之前的视图 - 由恢复使用 */
    public HeapPage getBeforeImage(){
        try {
            byte[] oldDataRef = null;
            synchronized(oldDataLock)
            {
                oldDataRef = oldData;
            }
            return new HeapPage(pid,oldDataRef);
        } catch (IOException e) {
            e.printStackTrace();
            //永远不应该发生——我们之前已经解析好了！
            System.exit(1);
        }
        return null;
    }

    public void setBeforeImage() {
        synchronized(oldDataLock) {
            oldData = getPageData().clone();
        }
    }

    /**
     * @return 与此页面关联的 PageId。
     */
    public HeapPageId getId() {
        return pid;
    }

    /**
     * 从源文件中吸取元组。
     */
    private Tuple readNextTuple(DataInputStream dis, int slotId) throws NoSuchElementException {
        // 如果关联位未设置，则向前读取到下一个元组，并返回 null。
        if (!isSlotUsed(slotId)) {
            for (int i=0; i<td.getSize(); i++) {
                try {
                    dis.readByte();
                } catch (IOException e) {
                    throw new NoSuchElementException("error reading empty tuple");
                }
            }
            return null;
        }

        // 读取元组中的字段
        Tuple t = new Tuple(td);
        RecordId rid = new RecordId(pid, slotId);
        t.setRecordId(rid);
        try {
            for (int j=0; j<td.numFields(); j++) {
                Field f = td.getFieldType(j).parse(dis);
                t.setField(j, f);
            }
        } catch (java.text.ParseException e) {
            e.printStackTrace();
            throw new NoSuchElementException("parsing error!");
        }

        return t;
    }

    /**
     * 生成一个表示此页面内容的字节数组。用于将此页面序列化到磁盘。
     * <p>
     * 这里的不变量是应该可以将 getPageData 生成的字节数组传递给 HeapPage 构造函数，
     * 并让它生成一个相同的 HeapPage 对象。
     *
     * @see #HeapPage
     * @return 一个字节数组对应这个页面的字节。
     */
    public byte[] getPageData() {
        int len = BufferPool.getPageSize();
        ByteArrayOutputStream baos = new ByteArrayOutputStream(len);
        DataOutputStream dos = new DataOutputStream(baos);

        // 创建页面的头部
        for (byte b : header) {
            try {
                dos.writeByte(b);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        // 创建元组
        for (int i=0; i<tuples.length; i++) {
            // 空槽
            if (!isSlotUsed(i)) {
                for (int j=0; j<td.getSize(); j++) {
                    try {
                        dos.writeByte(0);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }

                }
                continue;
            }

            // 非空槽
            for (int j=0; j<td.numFields(); j++) {
                Field f = tuples[i].getField(j);
                try {
                    f.serialize(dos);

                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        // 填充
        int zerolen = BufferPool.getPageSize() - (header.length + td.getSize() * tuples.length); //- numSlots * td.getSize();
        byte[] zeroes = new byte[zerolen];
        try {
            dos.write(zeroes, 0, zerolen);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            dos.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return baos.toByteArray();
    }

    /**
     * 生成对应于空 HeapPage 的字节数组的静态方法。用于向文件添加新的空白页面。
     * 将此方法的结果传递给 HeapPage 构造函数将创建一个其中没有有效元组的 HeapPage。
     *
     * @return 返回的字节数组。
     */
    public static byte[] createEmptyPageData() {
        int len = BufferPool.getPageSize();
        return new byte[len]; //all 0
    }

    /**
     *从页面中删除指定的元组；应更新相应的标头位以反映它不再存储在任何页面上。
     * @throws DbException 如果这个元组不在这个页面上，或者元组槽已经是空的。
     * @param t 要删除的元组
     */
    public void deleteTuple(Tuple t) throws DbException {
        int tupleNumber = t.getRecordId().getTupleNumber();
        //这里有可能slot位不为空但是两者不相等的情况一定要记得判断
        //切记要去自己实现元组类的equals方法，注意不需要对比recordId，因为其中的页是在Buffer中的，
        //而另一个相同的页是在磁盘中获取的
        if(tuples[tupleNumber] == null || !t.equals(tuples[tupleNumber]))
            throw new DbException("没有你要删除的元组");

        if(!isSlotUsed(tupleNumber))
            throw new DbException("该元组对应的槽为空！");

        markSlotUsed(tupleNumber, false);
        tuples[tupleNumber] = null;
    }

    /**
     * 将指定的元组添加到页面；应该更新元组以反映它现在存储在此页面上。
     * @throws DbException 如果页面已满（没有空槽）或 tupledesc 不匹配。
     * @param t 要添加的元组。
     */
    public void insertTuple(Tuple t) throws DbException {
        int numEmptySlots = getNumEmptySlots();
        if(numEmptySlots == 0)
            throw new DbException("此页已经满了！");
        if(!t.getTupleDesc().equals(td))
            throw new DbException("加错表了！");
        for (int i = 0; i < numSlots; i++) {
            //如果此slot没有用
            if(!isSlotUsed(i)){
                markSlotUsed(i, true);
                t.setRecordId(new RecordId(pid, i));    //标记这条记录在这个页的哪里
                tuples[i] = t;
                return;
            }
        }
    }

    /**
     * 将此页面标记为脏不脏并记录进行脏的事务
     */
    public void markDirty(boolean dirty, TransactionId tid) {
        this.dirty = dirty;
        this.dirtyId = tid;
    }

    /**
     * 返回上次弄脏此页面的事务的 tid，如果页面不脏，则返回 null
     */
    public TransactionId isDirty() {
        if (dirty)
            return dirtyId;
        else
            return null;
    }

    /**
     * 返回此页面上的空槽数。
     */
    public int getNumEmptySlots() {
        int res = 0;
        for(int i = 0; i < numSlots; i++){
            if(!isSlotUsed(i))
                res++;
        }
        return res;
    }

    /**
     * 如果此页面上的关联插槽已填满，则返回 true。
     * header中的每一个slot是一个8位的byte
     * 在JVM中使用的是大端序：
     * 例如有18个slots，而且全是used的，那么header的二进制数据为[11111111, 11111111, 00000011]
     * 则表明0~17号slot正在使用，18号及以上未被使用。(byte的右侧为低位)
     * 因为大端序中高位字节是存储在低位地址中，刚好就是[11111111,11111111,00000011]这种格式。
     */
    public boolean isSlotUsed(int i) {
        int index = i / 8;  //看是第几个slot
        int offset = i % 8; //然后偏移值是多少，从0开始
        //head保存着每个slot的状态，移动到offset处就是i位置的slot，然后进行与运算查看是不是1
        //1就是无效返回true
        int bit = (header[index]>>offset) & 1;
        return bit == 1;

        /**
         * 这种方式也是可以的，例如该byte是11111011,offset(也就是0那个bit的位置)
         * 那么只需先左移7-2=5位即可通过符号位来判断，注意要强转
         */
        //return (byte)(header[index] << (7 - offset)) < 0;
    }

    /**
     * 用于填充或清除此页面上的插槽的抽象。
     */
    private void markSlotUsed(int i, boolean value) {
        //算填充起始点，然后增加或删除的偏移值
        if(i < numSlots){
            int index = i / 8;  //第几个slot
            int offset = i % 8; //偏移多少
            //计算需要占位几个byte，将偏移值转换成byte
            byte mask = (byte) (0x1 << offset);
            if(value)   //如果是增加则或运算跟mask，将字节量加上去
                header[index] |= mask;
            else    //如果是删除，则是mask的非运算【(~x) = -(x + 1)】与当前位的字节进行与运算
                    //正好就可以反向的将mask偏移量的header记录全部退成未占用
                header[index] &= ~mask;
        }
    }

    /**
     * @return 此页面上所有元组的迭代器（在此迭代器上调用 remove 会引发 UnsupportedOperationException）
     * （请注意，此迭代器不应返回空槽中的元组！）
     */
    public Iterator<Tuple> iterator() {
        ArrayList<Tuple> filledTuples = new ArrayList<>();
        for(int i = 0; i < numSlots; i++){
            if(isSlotUsed(i)){
                filledTuples.add(tuples[i]);
            }
        }
        return filledTuples.iterator();
    }

}
```

- 总结

> 一定要注意里面的位运算的细节还有判断之间的细节
> 

### 4.2 实现HeapFile

- 代码

```java
/**
 * HeapFile 是一个 DbFile 的实现，它以无特定顺序存储一组元组。
 * 元组存储在页面上，每个页面都是固定大小的，文件只是这些页面的集合。
 * HeapFile 与 HeapPage 密切合作。 HeapPages 的格式在 HeapPage 构造函数中描述。
 *
 * @see HeapPage#HeapPage
 * @author Sam Madden
 */
public class HeapFile implements DbFile {
    private final File file;
    private final TupleDesc td;
    private final int id;

    /**
     * 构造由指定文件支持的堆文件。
     *
     * @param f 存储此堆文件的磁盘后备存储的文件。
     */
    public HeapFile(File f, TupleDesc td) {
        this.file = f;
        this.td = td;
        id = f.getAbsoluteFile().hashCode();
    }

    /**
     * 返回磁盘上支持此 HeapFile 的文件
     *
     * @return 磁盘上支持此 HeapFile 的文件。
     */
    public File getFile() {
        return file;
    }

    /**
     * 返回唯一标识此 HeapFile 的 ID。
     * 实施说明：您需要在某处生成此 tableid 以确保每个 HeapFile 都有一个“唯一 id”，
     * 并且您始终为特定 HeapFile 返回相同的值。我们建议散列 heapfile 底层文件的绝对文件名，
     * 即 f.getAbsoluteFile().hashCode()。
     *
     * @return 唯一标识此 HeapFile 的 ID。
     */
    public int getId() {
        return id;
    }

    /**
     * 返回存储在此 DbFile 中的表的 TupleDesc。
     *
     * @return 此 DbFile 的 TupleDesc
     */
    public TupleDesc getTupleDesc() {
        return td;
    }

    // 有关 javadocs，请参阅 DbFile.java
    public Page readPage(PageId pid) {
        //这两个值用于获取heapPageId
        int tableId = pid.getTableId();
        int pageNo = pid.getPageNumber();

        int pageSize = Database.getBufferPool().getPageSize();
        //该页面在缓冲池的偏移量
        long offset = pageNo * pageSize;
        byte[] data = new byte[pageSize];
        RandomAccessFile raf = null;
        /**
         * mode参数指定打开文件的访问模式。允许的值及其含义是：
         * 价值：意义
         * “r”：仅供阅读。调用结果对象的任何写入方法都将导致抛出IOException 。
         * “rw”：开放阅读和写作。如果该文件尚不存在，则将尝试创建它。
         * “rws”：打开以进行读写，与"rw"一样，并且还要求对文件内容或元数据的每次更新都同步写入底层存储设备。
         * “rwd”：打开以进行读写，与"rw"一样，并且还要求对文件内容的每次更新都同步写入底层存储设备
         */
        try {
            raf = new RandomAccessFile(file, "r");
            //寻找到对应位置的数据
            raf.seek(offset);
            //然后开始读
            raf.read(data);
            HeapPageId heapPageId = new HeapPageId(tableId, pageNo);
            //根据heapPageId构造当前页
            HeapPage heapPage = new HeapPage(heapPageId, data);
            return heapPage;
        } catch (FileNotFoundException e) {
            throw new IllegalArgumentException("HeapFile: readPage:没有相关页数据");
        } catch (IOException e) {
            throw new IllegalArgumentException(String.format("HeapFile: readPage: 该偏移值 %d 未找到",offset));
        } finally {
            try {
                raf.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public void writePage(Page page) throws IOException {
        PageId id = page.getId();
        int pageNumber = id.getPageNumber();
        int tableId = id.getTableId();
        byte[] pageData = page.getPageData();

        int pageSize = Database.getBufferPool().getPageSize();

        RandomAccessFile asf = new RandomAccessFile(file, "rws");
        //从脏页开始写到磁盘中
        asf.skipBytes(pageNumber * pageSize);
        asf.write(pageData);
    }

    /**
     * 返回此 HeapFile 中的页数。
     */
    public int numPages() {
        int num = (int)Math.floor(file.length()*1.0/BufferPool.getPageSize());
        return num;
    }

    /**
     * 将tuple插入到HeapFile中的page中，如果HeapFile中的page都已经满了，
     * 则在HeapFile中创建一个新的page
     * @param tid 执行更新的事务
     * @param t 要添加的元组。应该更新这个元组以反映它现在存储在这个文件中。
     *
     */
    public List<Page> insertTuple(TransactionId tid, Tuple t)
            throws DbException, IOException, TransactionAbortedException {
        List<Page> pages = new ArrayList<>();
        for (int pageNo = 0; pageNo < numPages(); pageNo++) {
            PageId pageId = new HeapPageId(getId(), pageNo);
            HeapPage page = (HeapPage) Database.getBufferPool().getPage(tid, pageId, Permissions.READ_WRITE);
            if(page.getNumEmptySlots() != 0){
                page.insertTuple(t);
                pages.add(page);
                return pages;
            }
        }

        //如果每一页都没有空槽那么就新建一页，使用缓冲流能加快IO速度
        BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(file, true));
        byte[] emptyPageData = HeapPage.createEmptyPageData();
        bos.write(emptyPageData);
        bos.close();

        //从新的一页开始写
        PageId pageId = new HeapPageId(getId(), numPages() - 1);
        HeapPage newPage = (HeapPage) Database.getBufferPool().getPage(tid, pageId, Permissions.READ_WRITE);
        newPage.insertTuple(t);
        pages.add(newPage);
        return pages;
    }

    /**
     *
     * @param tid 执行更新的事务
     * @param t 要删除的元组。应该更新这个元组以反映它不再存储在任何页面上
     * @return
     * @throws DbException
     * @throws TransactionAbortedException
     */
    public ArrayList<Page> deleteTuple(TransactionId tid, Tuple t) throws DbException,
            TransactionAbortedException {
        ArrayList<Page> pages = new ArrayList<>();
        PageId pageId = t.getRecordId().getPageId();
        HeapPage page = (HeapPage) Database.getBufferPool().getPage(tid, pageId, Permissions.READ_WRITE);
        page.deleteTuple(t);
        pages.add(page);
        return pages;
    }

    // see DbFile.java for javadocs
    public DbFileIterator iterator(TransactionId tid) {
        return new HeapFileIterator(tid);
    }

    private class HeapFileIterator implements DbFileIterator{
        private int curPageNo;
        private Iterator<Tuple> it;
        private final TransactionId tid;
        public HeapFileIterator(TransactionId tid){
            this.tid = tid;
        }

        @Override
        public void open() throws DbException, TransactionAbortedException {
            curPageNo = 0;
            it = getTuplesIterator(curPageNo);
        }

        private Iterator<Tuple> getTuplesIterator(int pageNo) throws TransactionAbortedException, DbException {
            //如果页号在范围内
            if(pageNo >=0 && pageNo < numPages()){
                //当前页的id与表的id绑定
                HeapPageId heapPageId = new HeapPageId(getId(), pageNo);
                HeapPage heapPage = (HeapPage) Database.getBufferPool().getPage(tid, heapPageId, Permissions.READ_ONLY);
                return heapPage.iterator();
            }else
                throw new DbException("该heapFIle："+getId()+"不存在该页："+pageNo);
        }

        @Override
        public boolean hasNext() throws DbException, TransactionAbortedException {
            if(it == null)
                return false;
            //当前页的元组迭代器没有元组了，那么就换下一页的迭代器
            if(!it.hasNext()){
                //这里切记一直循环判断
                while(curPageNo < (numPages() - 1)){
                    curPageNo++;
                    it = getTuplesIterator(curPageNo);
                    if(it.hasNext()){
                        return true;
                    }
                }
                return false;
            }else
                return true;
        }

        @Override
        public Tuple next() throws DbException, TransactionAbortedException, NoSuchElementException {
            if(it == null || !it.hasNext()){
                throw new NoSuchElementException("没有多余的元素了");
            }
            return it.next();
        }

        @Override
        public void rewind() throws DbException, TransactionAbortedException {
            close();
            open();
        }

        @Override
        public void close() {
            it = null;
        }
    }
}
```

- 总结

> 同理要注意边界情况，以及三个类之间添加或者删除的细节步骤
> 

### 4.3 实现BufferPool

- 代码

```java
/**
 * BufferPool 管理页面从磁盘到内存的读取和写入。访问方法调用它来检索页面，并从适当的位置获取页面。
 * BufferPool 也负责锁定；当事务获取页面时，BufferPool 会检查事务是否具有适当的锁来读写页面。
 *
 * @Threadsafe, 所有字段都是最终的
 */
public class BufferPool {
    /** 每页字节数，包括标题 */
    private static final int DEFAULT_PAGE_SIZE = 4096;

    private static int pageSize = DEFAULT_PAGE_SIZE;

    /** 传递给构造函数的默认页数。这被其他类使用。 BufferPool应该使用构造函数的numPages参数. */
    public static final int DEFAULT_PAGES = 50;

    private final int numPages;

    //pageId到page的映射
    private final ConcurrentHashMap<PageId, Page> bufferPool;

    /**
     * 创建一个缓存最多 numPages 页的 BufferPool。
     *
     * @param numPages 此缓冲池中的最大页数。
     */
    public BufferPool(int numPages) {
        this.numPages = numPages;
        bufferPool = new ConcurrentHashMap<>();
    }

    public static int getPageSize() {
      return pageSize;
    }

    // 此功能应仅用于测试！
    public static void setPageSize(int pageSize) {
    	BufferPool.pageSize = pageSize;
    }

    // 此功能应仅用于测试！
    public static void resetPageSize() {
    	BufferPool.pageSize = DEFAULT_PAGE_SIZE;
    }

    /**
     * 检索具有关联权限的指定页面。将获得一个锁，如果该锁被另一个事务持有，则可能会阻塞
     * <p>
     * 检索到的页面应在缓冲池中查找。如果存在，则应将其退回。如果不存在，则应将其添加到缓冲池并返回。
     * 如果缓冲池中空间不足，则应逐出一个页面并在其位置添加新页面。
     *
     * @param tid 请求页面的事务的 ID
     * @param pid 请求页面的 ID
     * @param perm 页面上请求的权限
     */
    public  Page getPage(TransactionId tid, PageId pid, Permissions perm)
        throws TransactionAbortedException, DbException {
        //缓冲池不存在该页
        if(!bufferPool.containsKey(pid)){
            if(pageSize > bufferPool.size()){
                //去硬盘中寻找该页的Catalog获取存放的DBFile
                DbFile databaseFile = Database.getCatalog().getDatabaseFile(pid.getTableId());
                //获取对应页
                Page page = databaseFile.readPage(pid);
                //如果不存在则要放到缓冲池中
                bufferPool.put(pid, page);
                return page;
            }else
                throw new DbException("缓冲池满了");
        }
        return bufferPool.get(pid);
    }

    /**
     * Releases the lock on a page.
     * Calling this is very risky, and may result in wrong behavior. Think hard
     * about who needs to call this and why, and why they can run the risk of
     * calling it.
     *
     * @param tid the ID of the transaction requesting the unlock
     * @param pid the ID of the page to unlock
     */
    public  void unsafeReleasePage(TransactionId tid, PageId pid) {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /**
     * Release all locks associated with a given transaction.
     *
     * @param tid the ID of the transaction requesting the unlock
     */
    public void transactionComplete(TransactionId tid) {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /** Return true if the specified transaction has a lock on the specified page */
    public boolean holdsLock(TransactionId tid, PageId p) {
        // some code goes here
        // not necessary for lab1|lab2
        return false;
    }

    /**
     * Commit or abort a given transaction; release all locks associated to
     * the transaction.
     *
     * @param tid the ID of the transaction requesting the unlock
     * @param commit a flag indicating whether we should commit or abort
     */
    public void transactionComplete(TransactionId tid, boolean commit) {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /**
     * 代表事务 tid 向指定表添加一个元组。将在添加元组的页面和任何其他更新的页面上获取写锁
     * （lab2 不需要获取锁）。如果无法获取锁，可能会阻塞。
     *
     * 通过调用它们的 markDirty 位将被操作弄脏的任何页面标记为脏，
     * 并将任何已被弄脏的页面的版本添加到缓存中（替换这些页面的任何现有版本），
     * 以便将来的请求看到最新的页面.
     *
     * 这里我们以后会进行重构，采用不同的置换算法
     * @param tid the transaction adding the tuple
     * @param tableId the table to add the tuple to
     * @param t the tuple to add
     */
    public void insertTuple(TransactionId tid, int tableId, Tuple t)
        throws DbException, IOException, TransactionAbortedException {
        DbFile heapFile = Database.getCatalog().getDatabaseFile(tableId);
        List<Page> pages = heapFile.insertTuple(tid, t);
        for (Page page : pages) {
            PageId pageId = page.getId();
            page.markDirty(true, tid);

            if(bufferPool.size() > numPages)
                evictPage();
            bufferPool.put(pageId, page);
        }
    }

    /**
     * 从缓冲池中删除指定的元组。将在删除元组的页面和任何其他更新的页面上获取写锁。
     * 如果无法获取锁，可能会阻塞。
     *
     * 通过调用它们的 markDirty 位将被操作弄脏的任何页面标记为脏，
     * 并将任何已被弄脏的页面的版本添加到缓存中（替换这些页面的任何现有版本），
     * 以便将来的请求看到最新的页面.
     *
     * @param tid the transaction deleting the tuple.
     * @param t the tuple to delete
     */
    public  void deleteTuple(TransactionId tid, Tuple t)
        throws DbException, IOException, TransactionAbortedException {
        DbFile heapFile = Database.getCatalog().getDatabaseFile(t.getRecordId().getPageId().getTableId());

        List<Page> pages = heapFile.deleteTuple(tid, t);
        for (Page page : pages) {
            page.markDirty(true, tid);

            if(bufferPool.size() > numPages)
                evictPage();
            bufferPool.put(page.getId(), page);
        }
    }

    /**
     * 将所有脏页刷新到磁盘。
     * NB: 使用这个例程要小心——它会将脏数据写入磁盘，因此如果在 NO STEAL 模式下运行会破坏 simpledb。
     */
    public synchronized void flushAllPages() throws IOException {

    }

    /** 从缓冲池中删除特定的页面 id。恢复管理器需要它来确保缓冲池不会在其缓存中保留回滚页面。

     B+ 树文件也使用它来确保从缓存中删除已删除的页面，以便可以安全地重用它们
    */
    public synchronized void discardPage(PageId pid) {
        // some code goes here
        // not necessary for lab1
    }

    /**
     * 将某个页面刷新到磁盘
     * @param pid 要刷新的页面的 ID
     */
    private synchronized  void flushPage(PageId pid) throws IOException {
        // some code goes here
        // not necessary for lab1
    }

    /** Write all pages of the specified transaction to disk.
     */
    public synchronized  void flushPages(TransactionId tid) throws IOException {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /**
     * 从缓冲池中丢弃一个页面。将页面刷新到磁盘以确保在磁盘上更新脏页。
     * 这里丢弃其实也要根据不同的置换策略去挑选页丢弃
     */
    private synchronized  void evictPage() throws DbException {
        // some code goes here
        // not necessary for lab1
    }
}
```

- 总结

> 本次实验的末尾还会将Buffer中的方法进行补齐
> 

## 5.实现Insert和Delete操作符

- 概述

在第四节中我们已经完成对于单个元组的删除或添加的底层逻辑，现在就是将业务逻辑抽象成具体的函数操作符：insert和delete

- Insert：该操作符将从子操作符读取的元组添加到其构造函数中指定的 `tableid` 中。它应该使用 `BufferPool.insertTuple()` 方法来完成此操作。
- Delete：该操作符删除它从其子操作符中读取的元组，该子操作符在其构造函数中指定 `tableid`。它应该使用 `BufferPool.deleteTuple()` 方法来完成此操作。

### 5.1 实现insert

- 代码

```java
/**
 * 将从子运算符读取的元组插入到构造函数中指定的 tableId
 */
public class Insert extends Operator {

    private static final long serialVersionUID = 1L;

    private TransactionId tid;
    private OpIterator child;
    private int tableId;

    //标志位，避免fetchNext操作可以无限制的向下取
    boolean isInserted;
    /**
     * fetchNext()会返回一个表示插入了多少tuple的一个tuple，
     * tupleDesc是该tuple的属性行fieldTypes == {Type.INT_TYPE}、
     *                          fieldNames == {“numbers of instered tuples”}
     */
    TupleDesc tupleDesc;

    /**
     * Constructor.
     *
     * @param t 运行插入的事务。
     * @param child 从中读取要插入的元组的子运算符。
     * @param tableId 插入元组的表。
     * @throws DbException 如果 child 的 TupleDesc 与我们要插入的表不同。
     */
    public Insert(TransactionId t, OpIterator child, int tableId)
            throws DbException {
        if(!Database.getCatalog().getTupleDesc(tableId).equals(child.getTupleDesc())){
            throw new DbException("元信息不匹配！");
        }

        this.tid = t;
        this.child = child;
        this.tableId = tableId;
        this.isInserted = false;

        Type[] types = new Type[]{Type.INT_TYPE};
        String[] fieldNames = new String[]{"插入元组的数量"};
        this.tupleDesc = new TupleDesc(types, fieldNames);
    }

    public TupleDesc getTupleDesc() {
        return tupleDesc;
    }

    public void open() throws DbException, TransactionAbortedException {
        child.open();
        super.open();
    }

    public void close() {
        super.close();
        child.close();
    }

    public void rewind() throws DbException, TransactionAbortedException {
        child.rewind();
    }

    /**
     * 将从 child 读取的元组插入到构造函数指定的 tableId 中。它返回一个包含插入记录数的单字段元组。
     * 插入应该通过 BufferPool 传递。 BufferPool 的实例可通过 Database.getBufferPool() 获得。
     * 请注意，插入不需要在插入之前检查特定元组是否重复。
     *
     * @return 包含插入记录数的元组，如果多次调用，则为 null。
     * @see Database#getBufferPool
     * @see BufferPool#insertTuple
     */
    protected Tuple fetchNext() throws TransactionAbortedException, DbException {
        BufferPool bufferPool = Database.getBufferPool();
        //如果第一次调用插入
        if(!isInserted){
            isInserted = true;
            int count = 0;
            while (child.hasNext()){
                Tuple next = child.next();
                try {
                    bufferPool.insertTuple(tid, tableId, next);
                    count++;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            //返回包含插入了多少tuple的一个tuple
            Tuple tuple = new Tuple(tupleDesc);
            tuple.setField(0, new IntField(count));
            return tuple;
        }else
            return null;
    }

    @Override
    public OpIterator[] getChildren() {
        return new OpIterator[]{child};
    }

    @Override
    public void setChildren(OpIterator[] children) {
        child = children[0];
    }
}
```

- 总结

> 注意最后返回的是新的数量元组就好了
> 

### 5.2 实现delete

- 代码

```java
/**
 * 删除运算符。 Delete 从其子运算符中读取元组，并将它们从它们所属的表中删除。
 */
public class Delete extends Operator {

    private static final long serialVersionUID = 1L;

    private TransactionId tid;
    private OpIterator child;

    private TupleDesc tupleDesc;

    //标志位，避免fetchNext操作可以无限制的向下取
    boolean isDeleted;
    /**
     * 指定此删除所属的事务以及要读取的子事务的构造函数。
     *
     * @param t 此删除运行的事务
     * @param child 从中读取元组以进行删除的子运算符
     */
    public Delete(TransactionId t, OpIterator child) {
        this.tid = t;
        this.child = child;

        tupleDesc = new TupleDesc(new Type[]{Type.INT_TYPE}, new String[]{"删除的元组数"});
        isDeleted = false;
    }

    public TupleDesc getTupleDesc() {
        return tupleDesc;
    }

    public void open() throws DbException, TransactionAbortedException {
        child.open();
        super.open();
    }

    public void close() {
        super.close();
        child.close();
    }

    public void rewind() throws DbException, TransactionAbortedException {
        child.rewind();
    }

    /**
     * 在从子运算符读取元组时删除它们。删除是通过缓冲池处理的
     * （可以通过 Database.getBufferPool() 方法访问。
     *
     * @return 包含已删除记录数的字段元组。
     * @see Database#getBufferPool
     * @see BufferPool#deleteTuple
     */
    protected Tuple fetchNext() throws TransactionAbortedException, DbException {
        BufferPool bufferPool = Database.getBufferPool();
        if(!isDeleted){
            isDeleted = true;
            int count = 0;
            while(child.hasNext()){
                Tuple next = child.next();
                try {
                    bufferPool.deleteTuple(tid, next);
                    count++;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            //返回包含删除了多少tuple的一个tuple
            Tuple tuple = new Tuple(tupleDesc);
            tuple.setField(0, new IntField(count));
            return tuple;
        }else
            return null;
    }

    @Override
    public OpIterator[] getChildren() {
        return new OpIterator[]{child};
    }

    @Override
    public void setChildren(OpIterator[] children) {
        child = children[0];
    }

}
```

## 6.实现BufferPool中的页面置换算法。

- 概述

> 在Lab1中我们使用`HashMap<PageId, Page>`将页面与页号映射起来，让出现页面满的时候我们会直接报错（缓冲池满了），而现在我们使用LRU的置换算法将原本的映射关系改为`HashMap<PageId, PageLinkedList>`，将每个页面通过一个链表进行连接
> 

> 在MySQL中Buffer的页面就是用链表连起来的，详情可看[Buffer pool](https://blog.csdn.net/weixin_49258262/article/details/123512105)
> 
- PageLinkedList

> `PageLinkedList`是自定义的双端链表，Node节点内保存了pageID和page，以及前后两个节点`pre、next`。用`PageLinkedList`构建一个链表，**每当BufferPool中的page被访问时，将该pageId对应的PageLinkedList移动到链表的头部，当有page需要放置到BufferPool中，且BufferPool的容量已经满时，则将最近最少使用的page淘汰，即链表的最后一个节点，然后将该page放置到BufferPool中。**
> 

```java
class PageNode{
        PageId pageId;
        Page page;
        PageNode pre;
        PageNode next;
        public PageNode() {}
        public PageNode(PageId pageId, Page page) {
            this.pageId = pageId;
            this.page = page;
        }
    }

    //我们采用头插法，正好符合LRU的意思，刚使用的在头节点
    private void addToHead(PageNode node){
        node.pre = head;
        node.next = head.next;
        head.next = node;
        node.next.pre = node;
    }

    private void delNode(PageNode node){
        node.pre.next = node.next;
        node.next.pre = node.pre;
    }

    /**
     * 移动到链表头部
     * @param node
     */
    private void moveToHead(PageNode node){
        delNode(node);
        addToHead(node);
    }

    private PageNode delTail(){
        PageNode res = tail.pre;
        delNode(res);
        return res;
    }
```

### 6.1 重构getPage、insertTuple、deleteTuple

- getPage

```java
/**
     * 检索具有关联权限的指定页面。将获得一个锁，如果该锁被另一个事务持有，则可能会阻塞
     * <p>
     * 检索到的页面应在缓冲池中查找。如果存在，则应将其退回。如果不存在，则应将其添加到缓冲池并返回。
     * 如果缓冲池中空间不足，则应逐出一个页面并在其位置添加新页面。
     *
     * @param tid 请求页面的事务的 ID
     * @param pid 请求页面的 ID
     * @param perm 页面上请求的权限
     */
    public Page getPage(TransactionId tid, PageId pid, Permissions perm)
        throws TransactionAbortedException, DbException {
        //缓冲池不存在该页
        if(!bufferPool.containsKey(pid)){
            //去硬盘中寻找该页的Catalog获取存放的DBFile
            DbFile databaseFile = Database.getCatalog().getDatabaseFile(pid.getTableId());
            //获取对应页
            Page page = databaseFile.readPage(pid);
            PageNode node = new PageNode(pid, page);
            //如果缓冲池没满
            if(numPages > bufferPool.size()){
                addToHead(node);
                bufferPool.put(pid, node);
                return node.page;
            }else{  //缓冲池满了触发LRU
                evictPage();
                addToHead(node);
                bufferPool.put(page.getId(), node);
                return page;
            }
        }else{  //如果存在则触发使用过的节点移动到表头
            PageNode node = bufferPool.get(pid);
            moveToHead(node);
            return node.page;
        }
    }
```

- insertTuple

```java
/**
     * 代表事务 tid 向指定表添加一个元组。将在添加元组的页面和任何其他更新的页面上获取写锁
     * （lab2 不需要获取锁）。如果无法获取锁，可能会阻塞。
     *
     * 通过调用它们的 markDirty 位将被操作弄脏的任何页面标记为脏，
     * 并将任何已被弄脏的页面的版本添加到缓存中（替换这些页面的任何现有版本），
     * 以便将来的请求看到最新的页面.
     *
     * @param tid the transaction adding the tuple
     * @param tableId the table to add the tuple to
     * @param t the tuple to add
     */
    public void insertTuple(TransactionId tid, int tableId, Tuple t)
        throws DbException, IOException, TransactionAbortedException {
        DbFile heapFile = Database.getCatalog().getDatabaseFile(tableId);
        //得到这个表的所有页（如果没有空位就会新建一页加入集合中）
        List<Page> pages = heapFile.insertTuple(tid, t);
        for (Page page : pages) {
            PageId pageId = page.getId();
            page.markDirty(true, tid);
            //如果该页不存在缓冲池那就加载进来
            if(!bufferPool.containsKey(pageId)){
                PageNode pageNode = new PageNode(pageId, page);
                if(getPageSize() < numPages){
                    addToHead(pageNode);
                    bufferPool.put(pageId, pageNode);
                }else { //由于可能当前页没有槽位，所以新建了一页，同时buffer的容量也到了极限
                    //那么肯定要进行LRU
                    evictPage();
                    addToHead(pageNode);
                    bufferPool.put(pageId, pageNode);
                }
            }else{  //如果已经存在就移动到对头中
                PageNode pageNode = bufferPool.get(pageId);
                moveToHead(pageNode);
                pageNode.page = page;
                bufferPool.put(pageId, pageNode);
            }
        }
    }
```

- deleteTuple

```java
/**
     * 从缓冲池中删除指定的元组。将在删除元组的页面和任何其他更新的页面上获取写锁。
     * 如果无法获取锁，可能会阻塞。
     *
     * 通过调用它们的 markDirty 位将被操作弄脏的任何页面标记为脏，
     * 并将任何已被弄脏的页面的版本添加到缓存中（替换这些页面的任何现有版本），
     * 以便将来的请求看到最新的页面.
     *
     * @param tid the transaction deleting the tuple.
     * @param t the tuple to delete
     */
    public void deleteTuple(TransactionId tid, Tuple t)
        throws DbException, IOException, TransactionAbortedException {
        DbFile heapFile = Database.getCatalog().getDatabaseFile(t.getRecordId().getPageId().getTableId());

        List<Page> pages = heapFile.deleteTuple(tid, t);
        for (Page page : pages) {
            page.markDirty(true, tid);

            PageNode pageNode = bufferPool.get(page.getId());
            if(pageNode == null){   //如果该页不存在
                if(getPageSize() < numPages){   //如果满了就触发置换
                    PageNode temp = new PageNode(page.getId(), page);
                    addToHead(temp);
                    bufferPool.put(page.getId(), pageNode);
                }else{
                    evictPage();
                    PageNode temp = new PageNode(page.getId(), page);
                    addToHead(temp);
                    bufferPool.put(page.getId(), pageNode);
                }
            }else{  //如果存在那么就移动到对头
                PageNode temp = bufferPool.get(page.getId());
                moveToHead(temp);
                bufferPool.put(page.getId(),temp);
            }
        }
    }
```

### 6.2 Buffer Pool的完善

```java
/**
 * BufferPool 管理页面从磁盘到内存的读取和写入。访问方法调用它来检索页面，并从适当的位置获取页面。
 * BufferPool 也负责锁定；当事务获取页面时，BufferPool 会检查事务是否具有适当的锁来读写页面。
 *
 * @Threadsafe, 所有字段都是最终的
 */
public class BufferPool {
    /** 每页字节数，包括标题 */
    private static final int DEFAULT_PAGE_SIZE = 4096;

    private static int pageSize = DEFAULT_PAGE_SIZE;

    /** 传递给构造函数的默认页数。这被其他类使用。 BufferPool应该使用构造函数的numPages参数. */
    public static final int DEFAULT_PAGES = 50;

    private final int numPages;

    //pageId到page的映射
    private final ConcurrentHashMap<PageId, PageNode> bufferPool;

    //头尾结点
    private PageNode head;
    private PageNode tail;

    /**
     * 创建一个缓存最多 numPages 页的 BufferPool。
     *
     * @param numPages 此缓冲池中的最大页数。
     */
    public BufferPool(int numPages) {
        this.numPages = numPages;
        bufferPool = new ConcurrentHashMap<>();
        head = new PageNode();
        tail = new PageNode();
        head.next = tail;
        tail.pre = head;

    }

    public static int getPageSize() {
      return pageSize;
    }

    // 此功能应仅用于测试！
    public static void setPageSize(int pageSize) {
    	BufferPool.pageSize = pageSize;
    }

    // 此功能应仅用于测试！
    public static void resetPageSize() {
    	BufferPool.pageSize = DEFAULT_PAGE_SIZE;
    }

    /**
     * Releases the lock on a page.
     * Calling this is very risky, and may result in wrong behavior. Think hard
     * about who needs to call this and why, and why they can run the risk of
     * calling it.
     *
     * @param tid the ID of the transaction requesting the unlock
     * @param pid the ID of the page to unlock
     */
    public  void unsafeReleasePage(TransactionId tid, PageId pid) {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /**
     * Release all locks associated with a given transaction.
     *
     * @param tid the ID of the transaction requesting the unlock
     */
    public void transactionComplete(TransactionId tid) {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /** Return true if the specified transaction has a lock on the specified page */
    public boolean holdsLock(TransactionId tid, PageId p) {
        // some code goes here
        // not necessary for lab1|lab2
        return false;
    }

    /**
     * Commit or abort a given transaction; release all locks associated to
     * the transaction.
     *
     * @param tid the ID of the transaction requesting the unlock
     * @param commit a flag indicating whether we should commit or abort
     */
    public void transactionComplete(TransactionId tid, boolean commit) {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /**
     * 将所有脏页刷新到磁盘。
     * NB: 使用这个例程要小心——它会将脏数据写入磁盘，因此如果在 NO STEAL 模式下运行会破坏 simpledb。
     */
    public synchronized void flushAllPages() throws IOException {
        for (PageId pageId : bufferPool.keySet()) {
            flushPage(pageId);
        }
    }

    /** 从缓冲池中删除特定的页面 id。恢复管理器需要它来确保缓冲池不会在其缓存中保留回滚页面。

     B+ 树文件也使用它来确保从缓存中删除已删除的页面，以便可以安全地重用它们
    */
    public synchronized void discardPage(PageId pid) {
        bufferPool.remove(pid);
    }

    /**
     * 将某个页面刷新到磁盘
     * @param pid 要刷新的页面的 ID
     */
    private synchronized  void flushPage(PageId pid) throws IOException {
        Page page = bufferPool.get(pid).page;
        //如果不为脏则事务id返回null
        if(page.isDirty() != null){
            Database.getCatalog().getDatabaseFile(pid.getTableId()).writePage(page);
            //不为脏则设置事务id为null
            page.markDirty(false, null);
        }
    }

    /** 将指定事务的所有页面写入磁盘。
     */
    public synchronized  void flushPages(TransactionId tid) throws IOException {
        // some code goes here
        // not necessary for lab1|lab2
    }

    /**
     * 从缓冲池中丢弃一个页面。将页面刷新到磁盘以确保在磁盘上更新脏页。
     * 这里丢弃其实也要根据不同的置换策略去挑选页丢弃
     */
    private synchronized void evictPage() throws DbException {
        PageNode tail = delTail();
        PageId evictPageId = tail.pageId;
        try {
            flushPage(evictPageId);
        } catch (IOException e){
            e.printStackTrace();
        }
        discardPage(evictPageId);
    }

}
```