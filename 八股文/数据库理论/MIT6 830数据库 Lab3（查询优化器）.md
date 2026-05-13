# MIT6.830数据库 | Lab3（查询优化器）

type: Post
status: Published
date: 2022/09/02
summary: 查询优化器
tags: 实践
category: 数据库

# Lab3

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

> 
> 
> - Tuple和TupleDesc是数据库表的最基本元素了。Tuple就是一个若干个Field的数组，TupleDesc则是一个表的meta-data，包括每列的field name和type。
> - HeapPage和HeapFile都分别是Page和DbFile interface的实现，毕竟HeapPage和HeapFile组织还是太简单了，后面lab会用B+树来替代之。
> - BufferPool是用来做缓存的，getPage会优先从这里拿，如果没有，才会调用File的readPage去从文件中读取对应page，disk中读入的page会缓存在其中。
> - SeqScan用来遍历一个table的所有tuple，包装了HeapFile的iterator。

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab3%EF%BC%88%E6%9F%A5%E8%AF%A2%E4%BC%98%E5%8C%96%E5%99%A8%EF%BC%89/image.png)

## 1.Lab3的任务总概

- 概述

> 在本次实验中会实现一个查询优化器，主要任务包括实现选择性评估框架和基于成本的优化器，大致就是先得到统计数据然后在连接方案中寻找最佳的
> 
> - 实现对某一字段直方图的构建
> - 实现对某一表的所有字段的直方图的构建
> - 实现对连接代价以及连接操作后基数的估计
> - 实现查询优化，给定连接查询，选择出连接代价最小的查询

## 2.查询优化器

- 宏观过程

> • `词法解析`：将sql语句解析成符合数据库内部的一些数据结构，会涉及到词法解析、语法分析、语义分析等
• `查询优化`：这个就是本次我们实验完成，的优化程序会对我们的语句
做一些优化，如外连接转换为内连接、表达式简化、子查询转为连接等。优化的结果就是生成一个执行计划，这个执行计划表明了应该使用哪些索引进行查询，表之间的连接顺序是啥样的。
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab3%EF%BC%88%E6%9F%A5%E8%AF%A2%E4%BC%98%E5%8C%96%E5%99%A8%EF%BC%89/image%201.png)

### 2.1 什么是优化器

- 概述

> 在MySQL中查询优化器在真正执行该语句之前会进行很多的分析，**根据表的统计信息分析每个执行方案的代价，还有根据一些固定的规则改写你的sql（条件化简、外连接消除、子查询优化等）**，这就分别代表两种不同的优化器：基于成本的优化和基于规则的优化，在MySQL中每个sql都会这两种优化的**洗礼**
> 
- 实现的主要思想

> • 使用关于表的统计信息来估计不同查询计划的`“成本”`。通常，计划的成本与中间连接和选择的基数 (由中间连接和选择产生的元组的数量) 以及筛选器和连接谓词的选择性有关。
• 使用这些统计信息可以以最优的方式对连接和选择进行排序，并从几个备选方案中选择连接算法的最佳实现。
> 
- 在项目中的起点——`parser`解析器

> 在项目中会首先调用parser这个类，作为优化器的起点，**这个类就是负责分析计算当前这个表的统计信息并且把查询转换为逻辑计划表示，然后调用查询优化器来生成最佳计划。你可以理解为生成了每个方案成本计算的那些必要的数值**
> 

==基于成本的优化器==

> `CBO: Cost-Based Optimization`也即`“基于成本的优化器”`，会根据优化规则对sql进行转换生成多个执行计划，然后计算每个执行计划的成本，然后挑选出成本最低执行
> 

==基于规则的优化器==

> `RBO: Rule-Based Optimization`也即`“基于规则的优化器”`，在使用数据库的人中每个的水平都层次不急，难免会写出性能很差的，那么优化器就会竭尽全力根据一些在编码层的规则去优化这个sql的执行效率，**但是数据是变化的规则是死的，所以有时候就会好心办坏事**
> 

### 2.2 整体优化器结构

- 结构如下

> 说明解析器中使用的类、方法和对象的图表
> 
> - `TableStats`类：对指定表中的数据进行统计，对表中的每一字段构建直方图（**IntHistogram、StringHistogram就是exercise1中要完成的，它能根据给定的字段和选择谓词，计算出选择率，即estimateSelectivity。exercise2要根据给定的tableId完成对TableStats的初始化**）
> - `Parser`类：查询解析器，当有查询输入时，调用parseQuery方法对查询进行解析。
> - `LogicalPlan`类：实例代表解析后的查询，调用physicalPlan方法返回给Parser类一个最优的查询计划
> - `JoinOptimizer`类：选择出最优的查询计划，orderJoin方法根据不同的连接顺序所产生的代价，选择出连接代价最小的查询计划。

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab3%EF%BC%88%E6%9F%A5%E8%AF%A2%E4%BC%98%E5%8C%96%E5%99%A8%EF%BC%89/image%202.png)

- 大致过程

> 
> 
> 1. `Parser.java`在初始化时构造一组表统计信息(存储在`statsMap`容器中)。然后等待输入查询，并对该查询调用方法parseQuery。
> 2. `parseQuery`首先构造一个`LogicalPlan`表示解析后的查询。`parseQuery`然后调用构造的`physicalPlan`方法`LogicalPlan`实例。`physicalPlan`方法返回一个`DBIterator`对象，该对象可用于实际运行查询。

### 2.3 统计估计

- 概述

> 准确估计计划成本是十分困难的，在我上面的文章链接中也可以看到成本的计算都是不精准需要进行估计或者`猜`的，所以在本次实验我们只关心连接序列（内连接驱动表与被驱动表的选择）和全表访问的成本这两种。
> 

> **我们不用担心索引带来的影响或额外操作符的成本 (如聚合)。因为前两个Lab中只实现了SeqScan这一种表扫描方式**
> 

==总体计划成本（里面包含连接成本）==

> 加入我们编写了一个形式为 `p=t1 join t2 join... tn` 的连接计划，这表示一个左深连接（其中每个连接的左输入是前一个连接的结果），其中 t1 是最左边的连接 (树中最深的)。那么成本就可以表示为：
> 

> **其中 `scancost(t1)`为扫描表t1的IO开销，`joincost(t1,t2)`为t1连接t2的CPU开销，两者相加就是总成本**。**为了使I/O和CPU成本具有可比性**，通常使用一个恒定的成本常数，在MySQL中IO成本常数为1.0，CPU常数为0.2；然后用扫描到的记录数或页数去乘IO常数或者CPU常数
> 

```sql
# scancost(xx)就是扫描的页数
scancost(t1) + scancost(t2) + joincost(t1 join t2) +
scancost(t3) + joincost((t1 join t2) join t3) +
```

==总体成本中的连接成本==

> 当使用嵌套循环连接时，回想一下两个表 t1 和 t2(其中 t1 是外部的) 之间连接的开销是：其中ntups是元组数量（基数）
> 

```sql
joincost(t1 join t2) = scancost(t1) + ntups(t1) x scancost(t2) //IO cost
                       + ntups(t1) x ntups(t2)  //CPU cost
```

==统计元组（记录）数量—— filter selectivities==

> **在MySQL中无论是主键索引，还是非主键索引都需要统计元组数量，对于前者获取元组数量比较简单沿着最左边的根节点向右查询，因为不存在重复值，而对于其他二级索引来说，我们需要找到二级索引中的记录并进行回表，但是二级索引中的记录时重复的，统计的方式是找到最左边最后一个符合条件的记录和最右边最后一个符合条件的记录，中间隔得页少直接迭代统计，隔得多就取一个平均值算出一个大约的记录数**
> 

> 在这个实验中是根据一种直方图的形式计算出记录数量
选择率的计算公式如下：这个值为value的记录数叫做基数（即总共有多少条值为value的记录），代表每一列不重复记录的个数
> 
> - 对于等值运算value = const，首先需要找到包含该const值的桶，然后进行计算：选择率 = （value的记录数）/ 记录总数，**假设数值在桶中是均匀分布的**，value的记录数为 桶高 / 桶宽，**故选择率可以表示为 （桶高 / 桶宽）/ 记录总数。**
> - 对于非等值运算，我们采用的也是同样的思想，value > const的选择率 = （value > const的记录数）/ 记录总数，value > const的记录数的记录数在直方图中由两部分构成。`（const，b.right]`部分的记录数 和 `[b.right，max]`部分的记录数。`（const，b.right]`部分的记录数 = `（桶高 / 桶宽）* （b_right - const）`， `[b.right，max]`部分的记录数 = 后面桶高的加和。对于value < const就是照葫芦画瓢
> 
> ![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab3%EF%BC%88%E6%9F%A5%E8%AF%A2%E4%BC%98%E5%8C%96%E5%99%A8%EF%BC%89/image%203.png)
> 

## 3.实现IntHistogram

- 概述

> 我们上面说到过通过直方图的形式得到元组的数量，那么这个类就负责构建这样的直方图，一个直方图代表着一个字段的统计信息，
> 
> 
> **直方图将字段的值分为多个相同的区间，并统计落于每个区间的记录数。每个区间的记录数是一个bucket，bucket的宽度是区间的大小，bucket的高度是落于该区间的记录的数量。**
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab3%EF%BC%88%E6%9F%A5%E8%AF%A2%E4%BC%98%E5%8C%96%E5%99%A8%EF%BC%89/image%204.png)

- 代码

```java
/** 表示单个基于整数的字段上的固定宽度直方图的类。
 */
public class IntHistogram {
    private int[] buckets;  //直方图中的每个条形

    private int min;

    private int max;

    private double width;   //每个桶的宽度

    private int tuplesCount;    //整个直方图统计的元组数

    /**
     * 创建一个新的 IntHistogram。
     *
     * 他的 IntHistogram 应该维护它接收的整数值的直方图。它应该将直方图拆分为“桶”桶。
     *
     * 直方图中的值将通过“addValue()”函数一次提供一个。
     *
     * 您的实现应该使用空间并具有相对于直方图值的数量恒定的执行时间。
     * 只需将您看到的每个值都存储在排序列表中。
     *
     * @param buckets 要将输入值拆分成的桶数
     * @param min 将传递给此类以进行直方图的最小整数值
     * @param max 将传递给此类进行直方图的最大整数值
     */
    public IntHistogram(int buckets, int min, int max) {
    	this.buckets = new int[buckets];
    	this.min = min;
    	this.max = max;
    	this.width = (max - min + 1.0) / buckets;
        this.tuplesCount = 0;
    }

    /**
     * 将一个值添加到您要保留其直方图的值集。
     * @param v 添加到直方图中的值
     */
    public void addValue(int v) {
        if(v >= min && v <= max){
            int index = getIndex(v);
            buckets[index]++;
            tuplesCount++;
        }
    }

    /**
     * 根据value获得桶的序号
     * @param v
     * @return
     */
    private int getIndex(int v){
        return (int) ((v - min) / width);
    }

    /**
     * 估计此表上特定谓词和操作数的选择性。
     *
     * 例如，如果“op”为“GREATER_THAN”且“v”为 5，则返回对大于 5 的元素比例的估计。
     *
     * @param op Operator
     * @param v Value
     * @return Predicted selectivity of this particular operator and value
     */
    public double estimateSelectivity(Predicate.Op op, int v) {
        switch (op){
            case EQUALS:    //== 等于 <= 减去 <
                return estimateSelectivity(Predicate.Op.LESS_THAN_OR_EQ, v) -
                        estimateSelectivity(Predicate.Op.LESS_THAN, v);
            case GREATER_THAN:  // > 等于 1 减去 <=
                return 1 - estimateSelectivity(Predicate.Op.LESS_THAN_OR_EQ, v);
            case LESS_THAN: //我们通过<去辐射全部的运算符规则，属于非等值运算哦
                if(v <= min)
                    return 0.0;
                else if(v >= max)
                    return 1.0;
                else{
                    int index = getIndex(v);    //得到第几个桶
                    double tuples = 0;
                    for (int i = 0; i < index; i++) {
                        //部分记录数[min, left]：计算小于这个v值的全部元组数
                        tuples += buckets[i];
                    }
                    //部分记录数(left , v]：（桶高 / 桶宽） * v - left
                    //left就是这个index对应的桶的起始位置
                    tuples += (1.0 * buckets[index] / width) * (v - (min + index * width));
                    //返回选择性即这个元组的重复率（选择率）
                    return tuples / tuplesCount;
                }
            case LESS_THAN_OR_EQ:   // <= 等于 <，让其值+1变得不相等
                return estimateSelectivity(Predicate.Op.LESS_THAN, v + 1);
            case GREATER_THAN_OR_EQ: // >= 等于 >
                return estimateSelectivity(Predicate.Op.GREATER_THAN, v - 1);
            case NOT_EQUALS: //!= 等于 1 减去 =
                return 1 - estimateSelectivity(Predicate.Op.EQUALS, v);
            default:
                throw new UnsupportedOperationException("运算符不支持");
        }
    }

    /**
     * @return
     *     此直方图的平均选择性。
     *     这不是实现基本连接优化的必不可少的方法。如果您想实现更有效的优化，可能需要它
     * */
    public double avgSelectivity() {
       return tuplesCount / tuplesCount;
    }

    /**
     * @return 描述此直方图的字符串，用于调试目的
     */
    public String toString() {
        return String.format("IntHistgram(buckets=%d, min=%d, max=%d",
                buckets.length, min, max);
    }
}
```

## 4.实现TableStats类

- 概述

> 根据给定的tableid，扫描出所有记录，并对每一个字段建立一个直方图。
> 
- 代码

> 默认的属性很多注意看，还有构造方法
> 

```java
/**
 * TableStats 表示有关查询中基表的统计信息（例如直方图）。
 *
 */
public class TableStats {

    private static final ConcurrentMap<String, TableStats> statsMap = new ConcurrentHashMap<>();

    static final int IOCOSTPERPAGE = 1000;

    public static TableStats getTableStats(String tablename) {
        return statsMap.get(tablename);
    }

    public static void setTableStats(String tablename, TableStats stats) {
        statsMap.put(tablename, stats);
    }

    public static void setStatsMap(Map<String,TableStats> s)
    {
        try {
            java.lang.reflect.Field statsMapF = TableStats.class.getDeclaredField("statsMap");
            statsMapF.setAccessible(true);
            statsMapF.set(null, s);
        } catch (NoSuchFieldException | IllegalAccessException | IllegalArgumentException | SecurityException e) {
            e.printStackTrace();
        }

    }

    public static Map<String, TableStats> getStatsMap() {
        return statsMap;
    }

    public static void computeStatistics() {
        Iterator<Integer> tableIt = Database.getCatalog().tableIdIterator();

        System.out.println("Computing table stats.");
        while (tableIt.hasNext()) {
            int tableid = tableIt.next();
            TableStats s = new TableStats(tableid, IOCOSTPERPAGE);
            setTableStats(Database.getCatalog().getTableName(tableid), s);
        }
        System.out.println("Done.");
    }

    /**
     * 直方图的桶数量。随意将此值增加到 100 以上，尽管我们的测试假设您的直方图中至少有 100 个桶。
     */
    static final int NUM_HIST_BINS = 100;
    //当前表
    private HeapFile table;
    //每页 IO 的成本
    private int ioCostPerPage;
    //元组的数量
    private int tuplesNum;
    //页的数量
    private int pagesNum;
    //整型字段与其直方图的映射
    private HashMap<Integer, IntHistogram> intHistogramMap;
    //字符串字段与其直方图的映射
    private HashMap<Integer, StringHistogram> stringHistogramMap;
    //表中所有的元组
    private ArrayList<Tuple> tuples;
    //表的属性行
    private TupleDesc tupleDesc;

    /**
     * 创建一个新的 TableStats 对象，用于跟踪表的每一列的统计信息
     * 对于此函数，您必须获取相关表的 DbFile，然后扫描其元组并计算所需的值。
     * 您应该尝试合理有效地执行此操作，但您不一定必须（例如）在一次扫描表中完成所有操作。
     *
     * @param tableId 计算统计信息的表
     * @param ioCostPerPage 每页 IO 的成本。这并没有区分顺序扫描 IO 和磁盘寻道。
     */
    public TableStats(int tableId, int ioCostPerPage) {
        table = (HeapFile) Database.getCatalog().getDatabaseFile(tableId);
        tupleDesc = table.getTupleDesc();
        this.ioCostPerPage = ioCostPerPage;
        this.pagesNum = table.numPages();
        DbFileIterator iterator = table.iterator(new TransactionId());
        int numFields = tupleDesc.numFields();

        tuples = new ArrayList<>();
        tuplesNum = 0;
        intHistogramMap = new HashMap<>();
        stringHistogramMap = new HashMap<>();

        //字段与该字段中最小值的映射
        HashMap<Integer, Integer> minField = new HashMap<>();
        //字段与该字段中最大值的映射
        HashMap<Integer, Integer> maxField = new HashMap<>();

        try {
            iterator.open();
            while (iterator.hasNext()){
                //遍历当前元组的字段，统计当前字段下最大值与最小值
                Tuple next = iterator.next();
                tuples.add(next);
                tuplesNum++;
                for (int i = 0; i < numFields; i++) {
                    if(tupleDesc.getFieldType(i).equals(Type.INT_TYPE)){
                        int value = ((IntField) next.getField(i)).getValue();
                        if(maxField.get(i) == null || value > maxField.get(i))
                            maxField.put(i, value);
                        if(minField.get(i) == null || value < minField.get(i))
                            minField.put(i, value);
                    }
                }
            }
            iterator.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

        //现在构造当前字段的直方图，根据当前字段的最大最小值
        for (int i = 0; i < numFields; i++) {
            Iterator<Tuple> tupleIterator = tuples.iterator();
            Type fieldType = tupleDesc.getFieldType(i);
            if(fieldType.equals(Type.INT_TYPE)){
                int min = minField.get(i);
                int max = maxField.get(i);
                /**
                 * 在NUM_HIST_BINS >> max - min + 1时，数据集的离散程度不够，
                 * 会出现buckets中数据局部聚簇，导致estimate the selectivity时有较大误差
                 * (estimateSelectivity函数)，示例就是TableStatsTest中最大最小值位31和0，
                 * 但是NUM_HIST_BINS足足有1000，过不了测试用例
                 */
                IntHistogram intHistogram = new IntHistogram
                        (Math.min(NUM_HIST_BINS, max - min + 1), min, max);
                try {
                    //将每个桶属于的当前字段进行统计
                    while (tupleIterator.hasNext()){
                        Tuple next = tupleIterator.next();
                        int fieldValue = ((IntField) next.getField(i)).getValue();
                        intHistogram.addValue(fieldValue);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
                intHistogramMap.put(i, intHistogram);
            }else{  //同理
                StringHistogram stringHistogram = new StringHistogram(NUM_HIST_BINS);
                while (tupleIterator.hasNext()){
                    Tuple tuple = tupleIterator.next();
                    String fieldValue = ((StringField)tuple.getField(i)).getValue();
                    stringHistogram.addValue(fieldValue);
                }
                stringHistogramMap.put(i, stringHistogram);
            }
        }
    }

    /**
     * 估计顺序扫描文件的成本，假设读取页面的成本是 costPerPageIO。
     * 您可以假设没有搜索并且缓冲池中没有页面。
     *
     * 此外，假设您的硬盘驱动器一次只能读取整个页面，因此如果表的最后一页只有一个元组，
     * 则读取整个页面的成本一样高。 （大多数真正的硬盘驱动器一次无法有效地寻址小于一页的区域。）
     *
     * @return 扫描表的估计成本。
     */
    public double estimateScanCost() {
        return 1.0 * pagesNum * ioCostPerPage;
    }

    /**
     * 假定应用了具有选择性 selectivityFactor 的谓词，返回给定选择率下的基数（同一列不同值的个数）
     * 选择性 = 基数 / 记录数
     *
     * @param selectivityFactor 表上任何谓词的选择性
     * @return 使用指定的 selectivityFactor 估计的扫描基数
     */
    public int estimateTableCardinality(double selectivityFactor) {
        return (int) (tuplesNum * selectivityFactor);
    }

    /**
     * op下场的平均选择性。
     * @param field 字段索引
     * @param op 谓词中的运算符 该方法的语义是，给定表，然后给定一个元组，其中我们不知道该字段的值，
     *           返回预期的选择性。您可以从直方图中估计此值。
     * */
    public double avgSelectivity(int field, Predicate.Op op) {
        double res = 0;
        Type fieldType = tupleDesc.getFieldType(field);
        //根据不同的类型完成不同的任务
        if(fieldType.equals(Type.INT_TYPE)) {
            IntHistogram intHistogram = intHistogramMap.get(field);
            res = intHistogram.avgSelectivity();
        }else{
            StringHistogram stringHistogram = stringHistogramMap.get(field);
            res = stringHistogram.avgSelectivity();
        }
        return res;
    }

    /**
     * 估计表上谓词字段操作常数的选择性。
     *
     * @param field 谓词范围的字段
     * @param op 谓词中的逻辑运算
     * @param constant 与字段进行比较的值
     * @return 估计的选择性（满足的元组的分数）谓词
     */
    public double estimateSelectivity(int field, Predicate.Op op, Field constant) {
        Type fieldType = tupleDesc.getFieldType(field);
        if(fieldType.equals(Type.INT_TYPE)) {
            IntHistogram intHistogram = intHistogramMap.get(field);
            return intHistogram.estimateSelectivity(op, ((IntField) constant).getValue());
        }else{
            StringHistogram stringHistogram = stringHistogramMap.get(field);
            return stringHistogram.estimateSelectivity(op, ((StringField) constant).getValue());
        }
    }

    /**
     * 返回此表中的元组总数
     * */
    public int totalTuples() {
        return tuplesNum;
    }

}
```

## 5.实现JoinOptimizer类——两表连接的估算

- 概述

> 在这个实验，我们要实现对连接代价以及连接操作后基数的估计（**这里一定要明确基数，这个基数其实是通过扫描驱动表扫描而来符合条件的元组数，在MySQL中称为扇出，注意mysql的基数跟这个基数不是一个意思**），为此我们需要实现这个类中分别代表这两个功能的两个方法
> 

### 5.1 实现JoinOptimizer#estimateJoinCost

- 概述

> 这个方法就是实现连接代价的方法，这个方法的五个参数，左表的基数为card1，成本为cost1；右边的基数为card2，成本为cost2，（左表和右表的数值都是作为驱动表时的数值）
> 

> 那么在左表作为驱动表，并且我们在Lab2使用的连接算法是嵌套循环算法：**前两个为IO成本，后一个为CPU成本**
> 
> - 那么驱动表的扫描成本为`cost1`
> - 而被驱动表右表的扫描代价是`card1*cost2`（驱动表查出的记录都要在被驱动表进行逐一的查询）
> - 然后连接成本为`card1*card2`

```java
/**
     * 估计加入的成本。
     *
     * 连接成本应根据您为实验 2 实现的连接算法（或多个算法）计算。
     * 它应该是在查询过程中必须读取的数据量以及数量的函数您的加入执行的 CPU 操作数。
     * 假设单个谓词应用程序的成本大约为 1。
     *
     *
     * @param j 表示正在执行的连接操作的 LogicalJoinNode。
     * @param card1 查询左侧的估计基数
     * @param card2 查询右侧的估计基数
     * @param cost1 对查询左侧的表进行一次完整扫描的估计成本
     * @param cost2 对查询右侧的表进行一次完整扫描的估计成本
     * @return 此查询的成本估算，以 cost1 和 cost2 表示
     */
    public double estimateJoinCost(LogicalJoinNode j, int card1, int card2,
            double cost1, double cost2) {
        if (j instanceof LogicalSubplanJoinNode) {
            // You do not need to implement proper support for these for Lab 3.
            return card1 + cost1 + cost2;
        } else {
            //在此处插入您的代码。提示：如果您实现的连接算法比基本的嵌套循环连接更复杂，
            // 您可能需要使用变量“j”。
            double cost = cost1 + cost2 * card1 + card1 * card2;
            return -1.0;
        }
    }
```

### 5.2 实现JoinOptimizer#estimateJoinCardinality

- 概述

> 这个基数的计算（需要我们明确很多情况下这个基数都是估计值），在我上面连接MySQL的查询优化器中有详细的讲解，但是对于两个表通过连接条件筛选出来的基数（非重复元组数量）如何决定？在本次实验中，我们试着统计下
> 

> 举具体的例子就是：**左表的基数为card1，成本为cost1；右边的基数为card2，成本为cost2，（左表和右表的数值都是作为驱动表时的数值），这个基数的选取就是该选card1，还是该选card2，因为因为这个的选取直接决定着公式`ntups(t1) x scancost(t2)`的大小，而这一项恰巧有时决定性因素**
> 

```sql
joincost(t1 join t2) = scancost(t1) + ntups(t1) x scancost(t2) //IO cost
                       + ntups(t1) x ntups(t2)  //CPU cost
```

- 对于等值连接

> • 如果连接的属性中有一个是主键列，我们通常采用非主键的基数作为该主键列的基数，因为在连接后主键列不为空，其他列为空的情况很常见，那么就有可能造成主键列的有数据的元组大于其他列的，那么就会造成基数的巨大误差
• 如果两个连接属性都是主键列，那么就选那个元组数较少的
• 如果两个连接属性都不是主键列，那就比较难估计了，因为都不是唯一的，本Lab中采用连接后的结果的基数是两表中较大的基数
> 
- 对于范围连接

> 统计起来也很难，本Lab采用`两表基数乘积 * 0.3` （MySQL中的CPU成本常数也为0.2）作为范围扫描的基数估计。
> 
- 代码

```java
/**
     * 估计两个表的连接基数。
     * */
    public static int estimateTableJoinCardinality(Predicate.Op joinOp,
                                                   String table1Alias,
                                                   String table2Alias,
                                                   String field1PureName,
                                                   String field2PureName,
                                                   int card1, int card2,
                                                   boolean t1pkey,
                                                   boolean t2pkey,
                                                   Map<String, TableStats> stats,
                                                   Map<String, Integer> tableAliasToId){
        int card = 1;
        if(joinOp == Predicate.Op.EQUALS){  //等值连接
            //主键和非主键的情况，采取非主键的基数
            if(t1pkey && !t2pkey){
                card = card2;
            }else if(t1pkey && t2pkey){ //两者都是主键
                card = Math.min(card1, card2);
            }else if(!t1pkey && t2pkey){    //也是主键和非主键的情况
                card = card1;
            }else{  //两者都是非主键的情况
                card = Math.max(card1, card2);
            }
        }else{  //不是等值连接
            card = (int) (card1 * card2 * 0.3);
        }
        return card <= 0 ? 1 : card;
    }
```

## 6.实现JoinOptimizer类——优化多表连接

- 概述

> 在多表连接下，选择出两个表（这里表与表之间可能是集合的关系）最小的执行成本；当有三个表时，就有12中不同的连接顺序，那么我们就需要在不同的连接顺序中迅速找出成本最低的；**宏观上这样就构造了一颗最左深树**
> 

> 当有很多表时如果按次序一个一个试显然是不可能的，所以我们可以采取类似于MySQL中的优化测试：**通过一个变量记录当前连接顺序的最小成本，如果后续的换不同节点统计代价时已经比这个最小值大了，那么直接抛弃，进行下一个**
> 
- 动态规划

> 通过上面的描述可见是一种动态规划的思路，用已知推出未知并得到最优解，实现最小代价的连接次序
> 
- 代码

> 我们需要额外关注三个方法和两个辅助类，分别是：
> 
> - enumerateSubsets：进行不同连接连接方式构造，会对结构进行重置，所以下面代码会贴出来
> - computeCostAndCardOfSubplan：进行当前子查询的最优代价计算
> - printJoins：将执行计划进行显示
> 
> ![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab3%EF%BC%88%E6%9F%A5%E8%AF%A2%E4%BC%98%E5%8C%96%E5%99%A8%EF%BC%89/image%205.png)
> 
> - CostCard：这个类就是代价+基数的一个封装类
> - planCache类：每次子查询结果的存放类，实际上就是当前执行机会的快照

```java
/**
     * 对集合进行拆分，得到具有size个logicalJoinNode节点的所有集合。
     *
     * 就是动态规划的枚举方法，可以看见时间复杂度十分高，我们可以优化成dfs+回溯的方式去优化时间复杂度
     *
     * @param v 需要其子集的向量
     * @param size 感兴趣的子集的大小
     * @return 一组指定大小的所有子集
     */
    public <T> Set<Set<T>> enumerateSubsets(List<T> v, int size) {
        /*Set<Set<T>> els = new HashSet<>();
        els.add(new HashSet<>());
        // Iterator<Set> it;
        // long start = System.currentTimeMillis();

        for (int i = 0; i < size; i++) {
            Set<Set<T>> newels = new HashSet<>();
            for (Set<T> s : els) {
                for (T t : v) {
                    Set<T> news = new HashSet<>(s);
                    if (news.add(t))
                        newels.add(news);
                }
            }
            els = newels;
        }

        return els;*/
        Set<Set<T>> els = new HashSet<>();
        Deque<T> subset = new ArrayDeque<>();
        dfs(v, 0, size, els, subset);
        return els;
    }

    /**
     *
     * @param list 需要拆分的子集
     * @param cur   到达那个结点
     * @param size  当前结点集合joins中前size个节点需要被拆分
     * @param subsets   每个连接顺序
     * @param subset    某个连接顺序
     * @param <T>
     */
    private <T> void dfs(List<T> list, int cur, int size,
                         Set<Set<T>> subsets, Deque<T> subset){
        if(subset.size() == size){
            subsets.add(new HashSet<>(subset));
        }

        for (int i = cur; i < list.size(); i++) {
            subset.addLast(list.get(i));
            dfs(list, i + 1, size, subsets, subset);
            subset.removeLast();
        }
    }
    /**
     * 在指定的表上计算一个合理有效的逻辑连接。
     * 给定各个表的统计数据，与各个表的选择率，返回joins的最优连接顺序
     *
     * @param stats 连接中涉及的每个表的统计信息，由基表名称引用，而不是别名
     * @param filterSelectivities 连接中每个表的过滤谓词的选择性，由表别名引用
     *                            （如果没有别名，则为基表名称）
     * @param explain 指示您的代码是应该解释其查询计划还是简单地执行它
     * @return 一个 List<LogicalJoinNode> 以执行它们的左深顺序存储连接。
     * @throws ParsingException
     *             when stats or filter selectivities is missing a table in the
     *             join, or or when another internal error occurs
     */
    public List<LogicalJoinNode> orderJoins(
            Map<String, TableStats> stats,
            Map<String, Double> filterSelectivities, boolean explain)
            throws ParsingException {
        //这个就是存储动态规划中最优解的容器
        PlanCache planCache = new PlanCache();
        //指定由 plan 表示的最优计划的成本和基数。
        CostCard bestCostCard = new CostCard();
        //得到需要连接的表节点数量
        int size = joins.size();
        for (int i = 1; i <= size; i++) {
            //这个enumerateSubsets方法就是动态规划的实际执行者，这个集合里面存放着不同的连接顺序
            Set<Set<LogicalJoinNode>> sets = enumerateSubsets(joins, i);
            //某一个连接顺序
            for (Set<LogicalJoinNode> subSet : sets) {
                double curBestValue = Double.MAX_VALUE; //记录当前的最小成本
                bestCostCard = new CostCard();
                //连接顺序的重排
                for (LogicalJoinNode removeNode : subSet) {   //遍历当前结点集合，删除不是最优的节点
                    //返回了子查询最优的代价
                    CostCard costCard = computeCostAndCardOfSubplan(stats, filterSelectivities, removeNode, subSet, curBestValue, planCache);
                    if(costCard != null){
                        curBestValue = costCard.cost;
                        bestCostCard = costCard;
                    }
                }
                if(curBestValue != Double.MAX_VALUE){   //说明这最小值更新了
                    //那么记录下来
                    planCache.addPlan(subSet, bestCostCard.cost, bestCostCard.card, bestCostCard.plan);
                }
            }
        }
        //如果有需要查询执行计划
        if(explain){
            printJoins(bestCostCard.plan, planCache, stats, filterSelectivities);
        }

        return bestCostCard.plan;
    }
```