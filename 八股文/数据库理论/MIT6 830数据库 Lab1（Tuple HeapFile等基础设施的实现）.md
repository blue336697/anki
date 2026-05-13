# MIT6.830数据库 | Lab1（Tuple/HeapFile等基础设施的实现）

type: Post
status: Published
date: 2022/08/31
summary: Tuple/HeapFile等基础设施的实现
tags: 实践
category: 数据库

# Lab1

## 前言

- 环境

> 需要配置Ant集成化测试环境，当然你使用自带的Junit也可以
> 

## 结构总概

- SimpleDB所包括的结构

> • 表示字段、元组和元组模式的类；
• 将谓词和条件应用于元组的类；
• 一种或多种访问方法（例如，堆文件），将关系存储在磁盘上，并提供一种遍历这些关系的元组的方法；
• 处理元组的运算符类（例如，选择、连接、插入、删除等）的集合；
• 一个缓冲池，在内存中缓存活动的元组和页面，并处理并发控制和事务；并且，存储有关可用表及其模式的信息的目录。
> 
- 图示

> 
> 
> - Tuple和TupleDesc是数据库表的最基本元素了。Tuple就是一个若干个Field的数组，TupleDesc则是一个表的meta-data，包括每列的field name和type。
> - HeapPage和HeapFile都分别是Page和DbFile interface的实现，毕竟HeapPage和HeapFile组织还是太简单了，后面lab会用B+树来替代之。
> - BufferPool是用来做缓存的，getPage会优先从这里拿，如果没有，才会调用File的readPage去从文件中读取对应page，disk中读入的page会缓存在其中。
> - SeqScan用来遍历一个table的所有tuple，包装了HeapFile的iterator。

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab1%EF%BC%88Tuple%20HeapFile%E7%AD%89%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%89/image.png)

- DataBase类

> **Database 类提供对作为数据库全局状态的静态对象集合的访问。具体来说，这包括访问编目 (数据库中所有表的列表)、缓冲池 (当前驻留在内存中的数据库文件页的集合) 和日志文件的方法。**
> 

## 1.Lab1的任务总概

- 概述

> 总体目标是实现对Lab剩下的操作函数以及置换页面算法的实现；大致有以下五个任务：
> 
> 1. 实现了元组以及元组的属性行
> 2. 实现一个数据库的实例，包含了数据库现有的表信息。需要实现添加新表的功能，以及从特定的表中提取信息。
> 3. 实现了BufferPool，负责将内存最近读过的物理页缓存下来
> 4. 实现了pageId、记录Id以及page的封装
> 5. 实现磁盘文件的接口，通过该接口可以从磁盘中读取信息、向磁盘中写入信息
> 6. 实现了扫描功能，即`SELECT * FROM table`

## 2.实现元组以及元组的属性行（Tuple&TupleDesc）

- 元组、字段、元组元信息之间的关系

> • `TupleDesc`：是这个表各个字段的类型、名称的集合，该表所有的字段信息都在这里面
• `Tuple`：元组就是所谓的这一行记录，一张表有无数条记录组成
• `Field`：属性、字段，是表中最小的数据单位，很多的Field组成了Tuple
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab1%EF%BC%88Tuple%20HeapFile%E7%AD%89%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%89/image%201.png)

### 2.1 实现TupleDesc

- 概述

> 这个类内部很简单，就是很多字段类（类型、名称）的一个集合（数组），这个集合的构成是一个内部类TDItem
> 
- 代码

```java
/**
 * TupleDesc 描述元组的模式。
 */
public class TupleDesc implements Serializable {
    //表示当前元组的各个字段信息
    private final TDItem[] tdItems;

    /**
     * 一个帮助类，方便组织各个字段的信息，表示filed
     * */
    public static class TDItem implements Serializable {

        private static final long serialVersionUID = 1L;

        /**
         * 字段类型
         * */
        public final Type fieldType;

        /**
         * 字段名
         * */
        public final String fieldName;

        public TDItem(Type t, String n) {
            this.fieldName = n;
            this.fieldType = t;
        }

        public String toString() {
            return fieldName + "(" + fieldType + ")";
        }
    }

    /**
     * @return
     *        迭代此 TupleDesc 中包含的所有字段 TDItems 的迭代器
     * */
    public Iterator<TDItem> iterator() {
        //当然你也可以自己创建迭代器
        return (Iterator<TDItem>) Arrays.asList(tdItems).iterator();
    }

    /*private class TDItemIterator implements Iterator<TDItem>{
        private int pos = 0;
        @Override
        public boolean hasNext() {
            return tdAr.length > pos;
        }

        @Override
        public TDItem next() {
            if(!hasNext()){
                throw new NoSuchElementException();
            }
            return tdAr[pos++];
        }
    }*/

    private static final long serialVersionUID = 1L;

    /**
     * 创建一个新的 TupleDesc，其中 typeAr.length 字段具有指定类型的字段以及关联的命名字段。
     *
     * @param typeAr    指定此 TupleDesc 中字段的数量和类型的数组。它必须至少包含一个条目
     * @param fieldAr   指定字段名称的数组。请注意，名称可能为空。
     */
    public TupleDesc(Type[] typeAr, String[] fieldAr) {
        // some code goes here
        tdItems = new TDItem[typeAr.length];
        for (int i = 0; i < tdItems.length; i++){
            tdItems[i] = new TDItem(typeAr[i], fieldAr[i]);
        }
    }

    /**
     * 构造函数。创建一个新的元组 desc，其中 typeAr.length 字段具有指定类型的字段，
     * 以及匿名（未命名）字段。
     *
     * @param typeAr    指定此 TupleDesc 中字段的数量和类型的数组。它必须至少包含一个条目
     */
    public TupleDesc(Type[] typeAr) {
        // some code goes here
        tdItems = new TDItem[typeAr.length];
        for (int i = 0; i < tdItems.length; i++){
            tdItems[i] = new TDItem(typeAr[i], "");
        }
    }

    /**
     * @return 此 TupleDesc 中的字段数
     */
    public int numFields() {
        return tdItems.length;
    }

    /**
     * 获取此 TupleDesc 的第 i 个字段的（可能为 null）字段名称。
     *
     * @param i 要返回的字段名称的索引。它必须是有效的索引。
     * @return 第 i 个字段的名称
     * @throws NoSuchElementException   如果 i 不是有效的字段参考。
     */
    public String getFieldName(int i) throws NoSuchElementException {
        if(i < 0 || i >= tdItems.length){
            throw new NoSuchElementException("索引 " + i + " 不合法");
        }
        return tdItems[i].fieldName;
    }

    /**
     * 获取此 TupleDesc 的第 i 个字段的类型。
     *
     * @param i 要获取其类型的字段的索引。它必须是有效的索引。
     * @return 第 i 个字段的类型
     * @throws NoSuchElementException   如果 i 不是有效的字段参考
     */
    public Type getFieldType(int i) throws NoSuchElementException {
        if(i < 0 || i >= tdItems.length){
            throw new NoSuchElementException("索引 " + i + " 不合法");
        }
        return tdItems[i].fieldType;
    }

    /**
     * 查找具有给定名称的字段的索引。
     *
     * @param name  字段的名字
     * @return 第一个具有给定名称的字段的索引。
     * @throws NoSuchElementException   如果没有找到具有匹配名称的字段。
     */
    public int fieldNameToIndex(String name) throws NoSuchElementException {
        for(int i = 0; i < tdItems.length; i++){
            if(tdItems[i].fieldName.equals(name))
                return i;
        }
        throw new NoSuchElementException("没有找到匹配的名称：" + name);
    }

    /**
     * @return 与此 TupleDesc 对应的元组的大小（以字节为单位）。
     *          请注意，来自给定 TupleDesc 的元组具有固定大小。
     */
    public int getSize() {
        int totalSize = 0;
        for(TDItem t : tdItems){
            totalSize += t.fieldType.getLen();
        }
        return totalSize;
    }

    /**
     * 将两个 TupleDescs 合并为一个，带有 td1.numFields + td2.numFields 字段，
     * 其中第一个 td1.numFields 来自 td1，其余来自 td2。
     *
     * @param td1   带有新 TupleDesc 的第一个字段的 TupleDesc
     * @param td2   TupleDesc 与 TupleDesc 的最后一个字段
     * @return 新的 TupleDesc
     */
    public static TupleDesc merge(TupleDesc td1, TupleDesc td2) {
        int totalLen = td1.numFields() + td2.numFields();
        int cur = 0;
        Type[] types = new Type[totalLen];
        String[] names = new String[totalLen];
        for(int i = 0; i < td1.numFields(); i++){
            types[i] = td1.getFieldType(i);
            names[i] = td1.getFieldName(i);
        }
        for (int i = 0, j = td1.numFields(); i <td2.numFields(); i++,j++) {
            types[j] = td2.getFieldType(i);
            names[j] = td2.getFieldName(i);
        }
        return new TupleDesc(types, names);
    }

    /**
     * 比较指定对象与此 TupleDesc 是否相等。如果两个 TupleDescs 具有相同数量的项，
     * 并且此 TupleDesc 中的第 i 个类型等于每个 i 的 o 中的第 i 个类型，则认为它们相等。
     *
     * @param o 要与此 TupleDesc 比较是否相等的对象。
     *
     * @return 如果对象等于此 TupleDesc，则为 true。
     */

    public boolean equals(Object o) {
        if(this.getClass().isInstance(o)) {
            TupleDesc another = (TupleDesc) o;
            if (numFields() == another.numFields()) {
                for (int i = 0; i < numFields(); ++i) {
                    if (!tdItems[i].fieldType.equals(another.tdItems[i].fieldType)) {
                        return false;
                    }
                }
                return true;
            }
        }
        return false;
    }

    public int hashCode() {
        //如果您想使用 TupleDesc 作为 HashMap 的键，请实现此功能，
        // 以便相等的对象具有相等的 hashCode() 结果
        throw new UnsupportedOperationException("unimplemented");
    }

    /**
     * 返回描述此描述符的字符串。它应该是
     * “fieldType[0](fieldName[0]), ..., fieldType[M](fieldName[M])”的形式，
     * 尽管确切的格式并不重要。
     *
     * @return 描述此描述符的字符串。
     */
    public String toString() {
        StringBuilder sb =  new StringBuilder();
        for(int i = 0; i < tdItems.length; i++){
            sb.append(tdItems[i].toString()+",");
        }
        sb.append(tdItems[tdItems.length - 1].toString() + "\\n");
        return sb.toString();
    }
}
```

- 注意——`instanceof 和 isinstance`

> 我们在以后会经常自定义equals方法，所以了解一下这两个作用差不多的关键字
==obj.instanceof(class)==
也就是说这个对象是不是这种类型，
> 
> - 一个对象是本身类的一个对象
> - 一个对象是本身类父类（父类的父类）和接口（接口的接口）的一个对象
> - 所有对象都是`Object obj.instance(Object)` true
> - 凡是null有关的都是`false null.instanceof(class)`

==class.isInstance(obj)==

> 这个对象能不能被转化为这个类
> 
> - 一个对象是本身类的一个对象
> - 一个对象能被转化为本身类所继承类（父类的父类等）和实现的接口（接口的父接口）强转
> - 所有对象都能被Object的强转
> - 凡是null有关的都是false class.isInstance(null)

==总结==

> 可见与instanceof用法相同，关键在于动态等价
> 
> - 对`obj.instanceof(class)`，在编译时编译器需要知道类的具体类型
> - 对`class.isInstance(obj)`，编译器在运行时才进行类型检查，故可用于反射，泛型中

### 2.2 实现Tuple

- 概述

> Tuple在Lab1中没什么好说的直接上代码，需要注意的一点就是一定要重写equals方法，因为在Lab2中会用到，不重写会导致判断错误
> 

```java
/**
 * 元组维护有关元组内容的信息。元组具有由 TupleDesc
 * 对象指定的指定模式，并包含具有每个字段数据的 Field 对象。
 */
public class Tuple implements Serializable {

    private static final long serialVersionUID = 1L;

    //字段集合
//    private List<Field> fields;   这种是简便写法
    private final Field[] fields;
    //当前元组的元信息
    private TupleDesc tupleDesc;
    //当前元组在磁盘中的位置信息
    private RecordId recordId;

    /**
     * 使用指定的模式（类型）创建一个新元组
     *
     * @param td
     *    这个元组的模式。它必须是具有至少一个字段的有效 TupleDesc 实例。
     */
    public Tuple(TupleDesc td) {
        fields = new Field[td.numFields()];
        tupleDesc = td;
    }

    /**
     * @return 表示得到此元组的元信息。
     */
    public TupleDesc getTupleDesc() {
        return tupleDesc;
    }

    /**
     * @return RecordId 表示此元组在磁盘上的位置。可能为空。
     */
    public RecordId getRecordId() {
        return recordId;
    }

    /**
     * 设置此元组的 RecordId 信息。
     *
     * @param rid   此元组的新 RecordId。
     */
    public void setRecordId(RecordId rid) {
        recordId = rid;
    }

    /**
     * 更改此元组的第 i 个字段的值。
     *
     * @param i 要更改的字段的索引。它必须是有效的索引。
     * @param f 字段的新值。
     */
    public void setField(int i, Field f) {
        fields[i] = f;
    }

    /**
     * @return 第 i 个字段的值，如果尚未设置，则为 null。
     *
     * @param i 要返回的字段索引。必须是有效索引。
     */
    public Field getField(int i) {
        return fields[i];
    }

    /**
     * 将此元组的内容作为字符串返回。请注意，要通过系统测试，格式需要如下：
     *  column1\\tcolumn2\\tcolumn3\\t...\\tcolumnN
     *
     * 其中 \\t 是任何空格（换行符除外）
     */
    public String toString() {
        StringBuilder sb =  new StringBuilder();
        for(int i = 0; i < tupleDesc.numFields() - 1; i++){
            sb.append(fields[i].toString()+" ");
        }
        sb.append(fields[tupleDesc.numFields() - 1].toString() + "\\n");
        return sb.toString();
    }

    /**
     * @return  迭代此元组的所有字段的迭代器
     * */
    public Iterator<Field> fields() {
        //这里有复杂的就是自己继承iterator接口实现方法
        return new FiledIterator();
        //简便写法
        //return (Iterator<Field>) Arrays.asList(fields).iterator();
    }

    private class FiledIterator implements Iterator<Field>{
        private int pos = 0;
        @Override
        public boolean hasNext() {
            return fields.length > pos;
        }

        @Override
        public Field next() {
            if(!hasNext()){
                throw new NoSuchElementException();
            }
            return fields[pos++];
        }
    }

    /**
     * 重置此元组的 TupleDesc（仅影响 TupleDesc）
     * */
    public void resetTupleDesc(TupleDesc td) {
        tupleDesc = td;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Tuple)) return false;
        Tuple tuple = (Tuple) o;
        return Arrays.equals(fields, tuple.fields) && Objects.equals(getTupleDesc(), tuple.getTupleDesc());
    }

    @Override
    public int hashCode() {
        int result = Objects.hash(getTupleDesc());
        result = 31 * result + Arrays.hashCode(fields);
        return result;
    }
}
```

## 3.实现CataLog类

- 概述

> 这个CataLog实际上就是整个数据库的代理对象，整个的逻辑关系如下图
> 
> - `CataLog`：目录。数据库包含很多张表，每张表有一个TupleDesc，以及这个TupleDesc规范下的很多个Tuple。Catalog管理着数据库中的所有表。调用数据库的Catalog需要调用Database.getCatalog()方法。
> - `DbFile`：为数据库磁盘文件的接口。数据库中每张表对应着一个DbFile，DbFile储存着表中的所有信息。
>     
>     ![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/cc01710c2e02252f65191067592aafce.png)
>     
- 代码

```java
/**
 * 目录跟踪数据库中所有可用的表及其关联的模式。目前，这是一个存根目录，用户程序必须先用表填充它，
 * 然后才能使用它——最终，它应该转换为从磁盘读取目录表的目录。
 *
 * @Threadsafe
 */
public class Catalog {

    //Catelog是Table的集合，然后每个Table有DbFile, PrimaryKeyField, Name
    //所以我们封装一下
    public class Table{
        private DbFile file;
        private String name;
        private String pkField;

        public Table(DbFile file, String name, String pkField){
            this.file = file;
            this.name = name;
            this.pkField = pkField;
        }

        public String toString(){
            return name + "(" + file.getId() + ":" + pkField +")";
        }
    }

    //我们要存取tableId和table的索引关联
    private ConcurrentHashMap<Integer, Table> tables;

    public Catalog() {
        // some code goes here
        tables = new ConcurrentHashMap<>();
    }

    /**
     * 将新表添加到目录中。此表的内容存储在指定的 DbFile中。
     * @param file 要添加的表格内容； file.getId() 是此 filetupledesc 参数的标识符，
     *             用于调用 getTupleDesc 和 getFile
     * @param name 表的名称——可能是一个空字符串。不能为空。
     *             如果存在名称冲突，请使用要添加的最后一个表作为给定名称的表。
     * @param pkeyField 主键字段的名称
     */
    public void addTable(DbFile file, String name, String pkeyField) {
        tables.put(file.getId(), new Table(file, name, pkeyField));
    }

    public void addTable(DbFile file, String name) {
        addTable(file, name, "");
    }

    /**
     * 将新表添加到目录中。此表具有使用指定的 TupleDesc 格式化的元组，其内容存储在指定的 DbFile中。
     * @param file 要添加的表格内容； file.getId() 是此 filetupledesc 参数的标识符，
     *             用于调用 getTupleDesc 和 getFile
     */
    public void addTable(DbFile file) {
        addTable(file, (UUID.randomUUID()).toString());
    }

    /**
     * 返回具有指定名称的表的id，
     * @throws NoSuchElementException 如果表不存在
     */
    public int getTableId(String name) throws NoSuchElementException {
        Integer id = tables.searchValues(1, value -> {
            if (value.name.equals(name))
                return value.file.getId();
            return null;
        });
        if(id != null)
            return id.intValue();
        else
            throw new NoSuchElementException("没有找到这个名字的表："+name);
    }

    /**
     * 返回指定表的元组描述符（模式）
     * @param tableid 表的 id，由传递给 addTable 的 DbFile.getId() 函数指定
     * @throws NoSuchElementException 如果表不存在
     */
    public TupleDesc getTupleDesc(int tableid) throws NoSuchElementException {
        Table table = tables.get(tableid);
        if(table != null)
            return table.file.getTupleDesc();
        else
            throw new NoSuchElementException("没有此表："+tableid);
    }

    /**
     * 返回可用于读取指定表内容的 DbFile。
     * @param tableid 表的 id，由传递给 addTable 的 DbFile.getId() 函数指定
     */
    public DbFile getDatabaseFile(int tableid) throws NoSuchElementException {
        Table table = tables.get(tableid);
        if(table != null)
            return table.file;
        else
            throw new NoSuchElementException("没有此表："+tableid);
    }

    public String getPrimaryKey(int tableid) {
        Table table = tables.get(tableid);
        if(table != null)
            return table.pkField;
        else
            throw new NoSuchElementException("没有此表："+tableid);
    }

    public Iterator<Integer> tableIdIterator() {
        ConcurrentHashMap.KeySetView<Integer, Table> ids = tables.keySet();
        return ids.stream().iterator();
    }

    public String getTableName(int id) {
        Table table = tables.get(id);
        if(table != null)
            return table.name;
        else
            throw new NoSuchElementException("没有此表："+id);
    }

    /** 从目录中删除所有表 */
    public void clear() {
        tables.clear();
    }

    /**
     * 从文件中读取模式并在数据库中创建适当的表
     * @param catalogFile
     */
    public void loadSchema(String catalogFile) {
        String line = "";
        String baseFolder=new File(new File(catalogFile).getAbsolutePath()).getParent();
        try {
            BufferedReader br = new BufferedReader(new FileReader(catalogFile));

            while ((line = br.readLine()) != null) {
                //assume line is of the format name (field type, field type, ...)
                String name = line.substring(0, line.indexOf("(")).trim();
                //System.out.println("TABLE NAME: " + name);
                String fields = line.substring(line.indexOf("(") + 1, line.indexOf(")")).trim();
                String[] els = fields.split(",");
                ArrayList<String> names = new ArrayList<>();
                ArrayList<Type> types = new ArrayList<>();
                String primaryKey = "";
                for (String e : els) {
                    String[] els2 = e.trim().split(" ");
                    names.add(els2[0].trim());
                    if (els2[1].trim().equalsIgnoreCase("int"))
                        types.add(Type.INT_TYPE);
                    else if (els2[1].trim().equalsIgnoreCase("string"))
                        types.add(Type.STRING_TYPE);
                    else {
                        System.out.println("Unknown type " + els2[1]);
                        System.exit(0);
                    }
                    if (els2.length == 3) {
                        if (els2[2].trim().equals("pk"))
                            primaryKey = els2[0].trim();
                        else {
                            System.out.println("Unknown annotation " + els2[2]);
                            System.exit(0);
                        }
                    }
                }
                Type[] typeAr = types.toArray(new Type[0]);
                String[] namesAr = names.toArray(new String[0]);
                TupleDesc t = new TupleDesc(typeAr, namesAr);
                HeapFile tabHf = new HeapFile(new File(baseFolder+"/"+name + ".dat"), t);
                addTable(tabHf,name,primaryKey);
                System.out.println("Added table : " + name + " with schema " + t);
            }
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(0);
        } catch (IndexOutOfBoundsException e) {
            System.out.println ("Invalid catalog entry : " + line);
            System.exit(0);
        }
    }
}
```

## 4.实现BufferPool

- 概述

> 对于缓冲池就是减少在磁盘所带来的速度差异，在内存中实现一个一定大小的缓冲池，使用局部性原理防止一些页面在内存中，对于MySQL的Buffer Pool，详解请看
> 
> 
> [Buffer Pool](https://blog.csdn.net/weixin_49258262/article/details/123512105)
> 

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab1%EF%BC%88Tuple%20HeapFile%E7%AD%89%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%89/image%202.png)

在Lab2中我们会实现淘汰策略，而现在的淘汰策略就是简单的抛异常

- 代码

```java
package simpledb.storage;

import simpledb.common.Database;
import simpledb.common.Permissions;
import simpledb.common.DbException;
import simpledb.common.DeadlockException;
import simpledb.transaction.TransactionAbortedException;
import simpledb.transaction.TransactionId;

import java.io.*;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

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
    public Page getPage(TransactionId tid, PageId pid, Permissions perm)
        throws TransactionAbortedException, DbException {
        if(!buffferPool.containsKey(pid)){
        if(numPages > buffferPool.size()){
            //bufferpool 中没有指定页，到disk中去找到对应的page  并将它保存到bufferpool中
            //1、在disk中找到page 所在的Dbfile/Table
            DbFile dbFile = Database.getCatalog().getDatabaseFile(pid.getTableId());
            //2、在Dbfile中找到 pid所对应的page
            Page page = dbFile.readPage(pid);
            buffferPool.put(pid,page);
        }
        else{
            throw new DbException("bufferPool is full");
        }
    }
    return buffferPool.get(pid);
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
     * @param tid the transaction adding the tuple
     * @param tableId the table to add the tuple to
     * @param t the tuple to add
     */
    public void insertTuple(TransactionId tid, int tableId, Tuple t)
        throws DbException, IOException, TransactionAbortedException {
        // not necessary for lab1
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
    public void deleteTuple(TransactionId tid, Tuple t)
        throws DbException, IOException, TransactionAbortedException {
        // not necessary for lab1
    }

    /**
     * 将所有脏页刷新到磁盘。
     * NB: 使用这个例程要小心——它会将脏数据写入磁盘，因此如果在 NO STEAL 模式下运行会破坏 simpledb。
     */
    public synchronized void flushAllPages() throws IOException {
        // not necessary for lab1
    }

    /** 从缓冲池中删除特定的页面 id。恢复管理器需要它来确保缓冲池不会在其缓存中保留回滚页面。

     B+ 树文件也使用它来确保从缓存中删除已删除的页面，以便可以安全地重用它们
    */
    public synchronized void discardPage(PageId pid) {
       // not necessary for lab1
    }

    /**
     * 将某个页面刷新到磁盘
     * @param pid 要刷新的页面的 ID
     */
    private synchronized  void flushPage(PageId pid) throws IOException {
        // not necessary for lab1
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
        // not necessary for lab1
    }
}
```

## 5.实现了pageId类、RecordId类、HeapPage类

- 概述

> 这三者就构成组成页的基本信息
> 

### 5.1 实现HeapPageId类

- 概述

> HeapPage 对象的唯一标识符，包含表id和页id
> 
- 代码

```java
/** HeapPage 对象的唯一标识符. */
public class HeapPageId implements PageId {
    private final int tableId;
    private final int pgNo;

    /**
     * 构造函数。为特定表的特定页面创建页面 id 结构。
     *
     * @param tableId 被引用的表
     * @param pgNo 该表中的页码。
     */
    public HeapPageId(int tableId, int pgNo) {
        this.tableId = tableId;
        this.pgNo = pgNo;
    }

    /** @return 与此 PageId 关联的表 */
    public int getTableId() {
        return tableId;
    }

    /**
     * @return 与此 PageId 关联的表 getTableId() 中的页码
     */
    public int getPageNumber() {
        return pgNo;
    }

    /**
     * @return 此页面的哈希码，由表号和页号的组合表示
     * （例如，如果 PageId 用作 BufferPool 中的哈希表中的键，则需要。）
     * @see BufferPool
     */
    public int hashCode() {
        String hash = "" + tableId + pgNo;
        return hash.hashCode();
        //throw new UnsupportedOperationException("implement this");
    }

    /**
     * 将一个 PageId 与另一个进行比较
     *
     * @param o 要比较的对象（必须是 PageId）
     * @return 如果对象相等（例如，页码和表 ID 相同），则为 true
     */
    public boolean equals(Object o) {
        if(this.getClass().isInstance(o)){
            PageId another = (PageId) o;
            if(getTableId() == another.getTableId() && getPageNumber() == another.getPageNumber())
                return true;
        }
        return false;
    }

    /**
     *  将此对象的表示形式返回为整数数组，用于写入磁盘。
     *  返回数组的大小必须包含与构造函数之一的参数数量相对应的整数数量。
     */
    public int[] serialize() {
        int[] data = new int[2];

        data[0] = getTableId();
        data[1] = getPageNumber();

        return data;
    }
}
```

### 5.2 实现RecordId类

- 概述

> RecordId 是对特定表的特定页面上特定元组的引用。人话就是某个元组在某个页的记录
> 
- 代码

```java
/**
 * RecordId 是对特定表的特定页面上特定元组的引用。
 */
public class RecordId implements Serializable {

    private static final long serialVersionUID = 1L;

    private final PageId pid;

    private final int tupleNo;

    /**
     * 引用指定的 PageId 和元组编号创建一个新的 RecordId。
     *
     * @param pid 元组所在页面的 pageid
     * @param tupleNo 页面内的元组编号。
     */
    public RecordId(PageId pid, int tupleNo) {
        this.pid = pid;
        this.tupleNo = tupleNo;
    }

    /**
     * @return 此 RecordId 引用的元组编号。
     */
    public int getTupleNumber() {
        return tupleNo;
    }

    /**
     * @return 此 RecordId 引用的页面 id。
     */
    public PageId getPageId() {
        return pid;
    }

    /**
     * 如果两个 RecordId 对象表示相同的元组，则它们被视为相等。
     *
     * @return 如果 this 和 o 表示相同的元组，则为真
     */
    @Override
    public boolean equals(Object o) {
        if(this.getClass().isInstance(o)){
            RecordId another = (RecordId) o;
            if(getPageId().equals(another) && getTupleNumber() == another.getTupleNumber())
                return true;
        }
        return false;
    }

    /**
     * 您应该实现 hashCode()，以便两个相等的 RecordId 实例
     * （相对于 equals()）具有相同的 hashCode()。
     *
     * @return 对于相等的 RecordId 对象，它是相同的 int。
     */
    @Override
    public int hashCode() {
        String hash = "" + pid.getTableId() + pid.getPageNumber() + tupleNo;
        return hash.hashCode();
    }
}
```

### 5.3 实现HeapPage类

- 概述

> 这个就是数据库中页的具体实现了，当然最后还有B+树结构的页面
> 
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
                // not necessary for lab1
    }

    /**
     * 将指定的元组添加到页面；应该更新元组以反映它现在存储在此页面上。
     * @throws DbException 如果页面已满（没有空槽）或 tupledesc 不匹配。
     * @param t 要添加的元组。
     */
    public void insertTuple(Tuple t) throws DbException {
                // not necessary for lab1
    }

    /**
     * 将此页面标记为脏不脏并记录进行脏的事务
     */
    public void markDirty(boolean dirty, TransactionId tid) {
                // not necessary for lab1
    }

    /**
     * 返回上次弄脏此页面的事务的 tid，如果页面不脏，则返回 null
     */
    public TransactionId isDirty() {
                // not necessary for lab1
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
                // not necessary for lab1
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

- 我们重点说一下`getNumTuples和getHeaderSize`这两个方法

==header数组==

> 我们可以看到header这个数组储存方式为byte数组，每个byte包含8个bit，这个数组的作用就是标记slot的使用情况，每一bit位代表几号slot在被使用，简单来说就是元组占用slot槽的关系就是HeapPage这个类的作用
> 

> 在JVM中采用的存储顺序是大端存储，所以例如当header数组为下面这个时，则表明0~17号slot正在使用，18号及以上未被使用。
> 

```java
{[11111111],[11111111],[00000011]}
```

> • `大端模式`是指数据的低位保存在内存的高地址中，而数据的高位保存在内存的低地址中.
• `小端模式`是指数据的低位保存在内存的低地址中，而数据的高位保存在内存的高地址中。
> 

==getNumTuples==

> 这个方法是返回每个page中最多包含的元组数，就是用`（整个缓冲池的大小*8 ）/ （这个页面属于的表中的所有字段的大小 * 8 + 1 ）`的向下取整
> 

> 所谓表中的所有字段的大小就是某一条记录的大小
> 

==getHeaderSize==

> 返回page中的header的大小，每个元组占用 tupleSize 个字节，就是用当前页面的元组数除8结果的向上取整就是header数组的大小，字节数组每个索引位置的大小就是一个字节，所以除8
> 

## 6.实现磁盘文件的接口：HeapFile

- 概述

> HeapFile对象包含一组`“物理页”`，每一个页大小固定，页内存储行数据。在SimpleDB中，数据库中每一个表对应一个HeapFile对象，HeapFile对象中的物理页的类型是HeapPage，物理页是存储在Buffer Pool中，通过HeapFile类读写。
> 
- 整个逻辑关系如下

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab1%EF%BC%88Tuple%20HeapFile%E7%AD%89%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%89/image%203.png)

- 从磁盘中读取页

> 首先需要计算文件中的正确偏移量。**需要随机访问该文件（这时候就会用到一个类RandomAccessFile，在代码中会解释其中的访问模式）**，以便以任意偏移量读取和写入页面。从磁盘读取页面时，不应调用缓冲池方法。
> 
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
                // not necessary for lab1
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
               // not necessary for lab1
        return null;
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
                // not necessary for lab1
        return null;
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

## 7.实现了扫描功能：SeqScan类

- 概述

> SeqScan 是一种顺序扫描访问方法的实现，它以无特定顺序读取表的每个元组，就是最基本的select功能，属于是基础函数运算符。本质上就是一个迭代器
> 
- 由下及上——迭代器的遍历思想

> 整个个过程就是通过将低级操作符传递到高级操作符的构造函数中，**即“将它们链接在一起”**，操作符被连接到一个任务中。位于任务叶子处的特殊访问方法操作符负责从磁盘读取数据 (因此在它们下面没有任何操作符)。
> 

> 在任务的顶部，与 SimpleDB 交互的程序简单地在根操作符上调用`getNext`；然后，该操作符在其子节点上调用 `getNext`，依此类推，直到调用这些叶操作符。它们从磁盘中获取元组并传递给树 (作为返回参数 `getNext`)；
> 

> 元组以这种方式在任务中向上传播，直到它们在根输出，或者被任务中的另一个操作符组合或拒绝。
> 

```java
/**
 * SeqScan 是一种顺序扫描访问方法的实现，它以无特定顺序读取表的每个元组（例如，因为它们被布置在磁盘上）。
 */
public class SeqScan implements OpIterator {

    private static final long serialVersionUID = 1L;

    private final TransactionId tid;
    private int tableId;
    private String tableAlias;
    private DbFileIterator dFIterator;

    /**
     * 作为指定事务的一部分，创建对指定表的顺序扫描。
     *
     * @param tid
     *            此扫描作为其中一部分运行的事务。
     * @param tableid
     *            要扫描的表。
     * @param tableAlias
     * 此表的别名（解析器需要）；返回的 tupleDesc 应该有名称为 tableAlias.fieldName 的字段
     * （注意：这个类不负责处理 tableAlias 或 fieldName 为空的情况。如果它们不应该崩溃，
     * 但结果名称可以是 null.fieldName，tableAlias .null 或 null.null）。
     */
    public  SeqScan(TransactionId tid, int tableid, String tableAlias) {
        this.tid = tid;
        this.tableId = tableid;
        this.tableAlias = tableAlias;
    }

    /**
     * @return
     *       返回操作员扫描的表的表名。这应该是数据库目录中表的实际名称
     * */
    public String getTableName() {
        return Database.getCatalog().getTableName(tableId);
    }

    /**
     * @return 返回此运算符扫描的表的别名。
     * */
    public String getAlias() {
        return tableAlias;
    }

    /**
     * 重置此运算符的 tableid 和 tableAlias。
     * @param tableid
     *            要扫描的表。
     * @param tableAlias
     *    此表的别名（解析器需要）；返回的 tupleDesc 应该有名称为 tableAlias.fieldName 的字段
     *    （注意：这个类不负责处理 tableAlias 或 fieldName 为空的情况。如果它们不应该崩溃，
     *    但结果名称可以是 null.fieldName，tableAlias .null 或 null.null）。
     */
    public void reset(int tableid, String tableAlias) {
        this.tableId = tableid;
        this.tableAlias = tableAlias;
    }

    public SeqScan(TransactionId tid, int tableId) {
        this(tid, tableId, Database.getCatalog().getTableName(tableId));
    }

    /**
     * 初始化迭代器，根据表id获取表的堆文件，然后获取迭代器
     * @throws DbException
     * @throws TransactionAbortedException
     */
    public void open() throws DbException, TransactionAbortedException {
        dFIterator = Database.getCatalog().getDatabaseFile(tableId).iterator(tid);
        dFIterator.open();
    }

    /**
     * 返回 TupleDesc，其字段名称来自基础 HeapFile，前缀为来自构造函数的 tableAlias 字符串。
     * 当连接包含同名字段的表时，此前缀非常有用。别名和名称应以“.”分隔。字符
     * （例如，“alias.fieldName”）。
     *
     * @return TupleDesc 具有来自基础 HeapFile 的字段名称，
     *                  前缀为来自构造函数的 tableAlias 字符串。
     */
    public TupleDesc getTupleDesc() {
        TupleDesc tupleDesc = Database.getCatalog().getTupleDesc(tableId);
        String prefix = "null";
        //就是循环设置每个字段的前缀
        if(tableAlias != null){
            prefix = tableAlias;
        }
        int len = tupleDesc.numFields();
        Type[] types = new Type[len];
        String[] fields = new String[len];
        for(int i = 0; i < len; i++){
            types[i] = tupleDesc.getFieldType(i);
            String fieldName = "null";
            if(tupleDesc.getFieldName(i) != null)
                fieldName = tupleDesc.getFieldName(i);
            fields[i] = prefix + "." + fieldName;
        }
        tupleDesc = new TupleDesc(types,fields);
        return tupleDesc;
    }

    public boolean hasNext() throws TransactionAbortedException, DbException {
        if(dFIterator == null)
            throw new TransactionAbortedException();
        return dFIterator.hasNext();
    }

    public Tuple next() throws NoSuchElementException,
            TransactionAbortedException, DbException {
        if(dFIterator == null)
            throw new NoSuchElementException("没有多余的元组了");
        Tuple next = dFIterator.next();
        if(next == null)
            throw new NoSuchElementException("没有多余的元组了");
        return next;
    }

    public void close() {
        dFIterator.close();
    }

    public void rewind() throws DbException, NoSuchElementException,
            TransactionAbortedException {
        dFIterator.rewind();
    }
}
```

## 8.集成测试Lab1——循环扫描

步骤如下

1. 自定义一个.txt文件，内容就是几行几列的表

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab1%EF%BC%88Tuple%20HeapFile%E7%AD%89%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%89/image%204.png)

1. 生成测试Jar包，博主使用Idea自带的Ant集成环境直接编译打包的

![image.png](MIT6%20830%E6%95%B0%E6%8D%AE%E5%BA%93%20Lab1%EF%BC%88Tuple%20HeapFile%E7%AD%89%E5%9F%BA%E7%A1%80%E8%AE%BE%E6%96%BD%E7%9A%84%E5%AE%9E%E7%8E%B0%EF%BC%89/image%205.png)

1. 输入下面的命令生成二进制文件，其中的N代表有几列

```java
java -jar dist/simpledb.jar convert xxx/file.txt N
```

1. 编写测试类

```java
/**
 * @author lhj
 * @create 2022/8/28 11:56
 */
public class Lab1Test {
    public static void main(String[] argv) {
        // 构造一个 3 列表模式
        Type types[] = new Type[]{ Type.INT_TYPE, Type.INT_TYPE, Type.INT_TYPE };
        String names[] = new String[]{ "field0", "field1", "field2" };
        TupleDesc descriptor = new TupleDesc(types, names);

        // 创建表，将其与 some_data_file.dat 关联，并告诉目录该表的模式
        HeapFile table1 = new HeapFile(new File("dist/some_data_file.dat"), descriptor);
        Database.getCatalog().addTable(table1, "testTable");

        // 构造查询：我们使用一个简单的 SeqScan，它通过它的迭代器勺子馈送元组。
        TransactionId tid = new TransactionId();
        SeqScan f = new SeqScan(tid, table1.getId());

        try {
            f.open();
            while (f.hasNext()) {
                Tuple tup = f.next();
                System.out.println(tup);
            }
            Database.getBufferPool().transactionComplete(tid);
        } catch (Exception e) {
            System.out.println ("Exception : " + e);
        }finally {
            f.close();
        }
    }
}
```